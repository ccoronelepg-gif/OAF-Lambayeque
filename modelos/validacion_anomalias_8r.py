#!/usr/bin/env python3
"""8R: evaluación cronológica fuera de entrenamiento de anomalía T2m, 1 mes adelante.

Solo ERA5-Land vía 8Q. No son pronósticos futuros ni observaciones SENAMHI.
1996-2010: normals por sitio y ajuste de coeficientes (1997-2010);
2011-2015: selección de UNA estrategia usando centros distintos de rejilla;
2016-2025: test congelado, sin información futura del mes que se pronostica.
Predictores: anomalía del mes ANTERIOR, local y señal regional excluyendo celda
del objetivo, agregada por centros de ERA5-Land únicos.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import transectos_continuidad_8q as reference
import perfiles_climaticos_8o as history

ROOT=Path(__file__).resolve().parents[1]
DIR="datos/validacion_predictiva_8r"
CAL=(1996,2010)
TRAIN=(1997,2010)
VAL=(2011,2015)
TEST=(2016,2025)
FIELDS=("mes_objetivo","testigo_id","transecto","centro_celda_t",
        "observacion_anomalia_c","climatologia_pred_c","persistencia_pred_c",
        "regional_rezago_pred_c","modelo_jerarquico_pred_c","seleccionado_pred_c",
        "metodo_seleccionado","ultimo_mes_observado")
MODELS=("climatologia","persistencia","regional_rezago","jerarquico")
DESC={
 "climatologia":"anomalía cero con normal fija 1996–2010",
 "persistencia":"anomalía propia del mes previo, observada/reanálisis",
 "regional_rezago":"media del mes anterior en otros píxeles T2m de ERA5-Land (sin el píxel objetivo)",
 "jerarquico":"regresión ridge global con retrasos local + otros píxeles, calibrada hasta 2010"
}

def normal_monthly(values):
    """Calculate site-specific normals without val/test leakage."""
    keys=sorted(values)
    if len(keys)!=360 or keys[0]!="1996-01" or keys[-1]!="2025-12":
        raise ValueError("Se requieren exactamente los 360 meses 1996–2025")
    means={}
    for month in range(1,13):
        selected=[values[f"{y}-{month:02d}"] for y in range(CAL[0],CAL[1]+1)]
        if len(selected)!=15 or any(not math.isfinite(x) for x in selected):
            raise ValueError("Climatología inadecuada")
        means[month]=statistics.mean(selected)
    return means

def cell_groups(centers):
    """1 vote per reanalysis cell, never per duplicative API request."""
    bycell=defaultdict(list)
    for name,center in centers.items():
        bycell[tuple(center)].append(name)
    return {k:sorted(ids) for k,ids in sorted(bycell.items())}

def features(monthly,centers):
    ids=sorted(monthly)
    if len(ids)<3 or set(ids)!=set(centers):
        raise ValueError("Testigos/centros no concuerdan")
    allkeys=sorted(next(iter(monthly.values())))
    if allkeys!=[f"{year}-{mon:02d}" for year in range(1996,2026) for mon in range(1,13)]:
        raise ValueError("Calendario mensual 30 años incompleto")
    if any(sorted(monthly[pid])!=allkeys for pid in ids):
        raise ValueError("Cobertura temporal desigual")
    groups=cell_groups(centers)
    if len(groups)<3:raise ValueError("Se requieren al menos 3 píxeles distintos")
    normals={i:normal_monthly(monthly[i]) for i in ids}
    anomalies={i:{day:monthly[i][day]-normals[i][int(day[-2:])] for day in allkeys}
               for i in ids}
    # Coherencia frente a duplicados: use a single representative per pixel.
    for _,names in groups.items():
        a=names[0]
        for b in names[1:]:
            # Open-Meteo can downscale temperature by elevation on same pixel.
            # Anomalies may differ slightly; count the pixel once via its
            # representative and publish the limitation.
            if len(anomalies[b])!=len(anomalies[a]):raise ValueError("Pseudo-réplica incompleta")
    byid={pid:tuple(centers[pid]) for pid in ids}
    representative={pixel:names[0] for pixel,names in groups.items()}
    rows=[]
    for t in range(1,len(allkeys)):
        month=allkeys[t];previous=allkeys[t-1];year=int(month[:4])
        for pid in ids:
            pixel=byid[pid]
            peer=[anomalies[pick][previous] for cell,pick in representative.items()
                  if cell!=pixel]
            rows.append({
             "pid":pid,"date":month,"prev":previous,"year":year,"cell":pixel,
             "y":anomalies[pid][month],
             "local":anomalies[pid][previous],
             "regional":statistics.mean(peer),
             "normal":normals[pid][int(month[-2:])],
             "temp":monthly[pid][month]})
    return rows,groups,normals

def representative_rows(rows,groups):
    ids={a[0] for a in groups.values()}
    return [r for r in rows if r["pid"] in ids]

def solve3(matrix,vector):
    # Gauss-Jordan elimination with intercept unregularized.
    n=3;A=[list(matrix[i])+[vector[i]] for i in range(n)]
    for c in range(n):
        pivot=max(range(c,n),key=lambda i:abs(A[i][c]))
        if abs(A[pivot][c])<1e-9:raise ValueError("Matriz regresión no invertible")
        A[c],A[pivot]=A[pivot],A[c]
        f=A[c][c];A[c]=[v/f for v in A[c]]
        for j in range(n):
            if j==c:continue
            k=A[j][c];A[j]=[p-k*q for p,q in zip(A[j],A[c])]
    return [A[i][-1] for i in range(n)]

def fit_ridge(train,penalty=1.0):
    if len(train)<150:raise ValueError("Calibración insuficiente")
    mat=[[0.]*3 for _ in range(3)];rhs=[0.]*3
    for r in train:
        xx=[1.,r["local"],r["regional"]]
        for a in range(3):
            rhs[a]+=xx[a]*r["y"]
            for b in range(3):mat[a][b]+=xx[a]*xx[b]
    for i in (1,2):mat[i][i]+=penalty
    return solve3(mat,rhs)

def predictions(row,coef):
    return {"climatologia":0.,"persistencia":row["local"],
            "regional_rezago":row["regional"],
            "jerarquico":coef[0]+coef[1]*row["local"]+coef[2]*row["regional"]}

def score(rows,pred):
    if not rows:raise ValueError("No hay meses para evaluar")
    errors=[pred(r)-r["y"] for r in rows]
    return {"n":len(errors),"mae_c":round(statistics.mean(abs(e) for e in errors),6),
            "rmse_c":round(math.sqrt(statistics.mean(e*e for e in errors)),6),
            "sesgo_c":round(statistics.mean(errors),6)}

def exercise(monthly,centers,transects):
    rows,groups,normals=features(monthly,centers)
    reps=representative_rows(rows,groups)
    train=[r for r in reps if TRAIN[0]<=r["year"]<=TRAIN[1]]
    val=[r for r in reps if VAL[0]<=r["year"]<=VAL[1]]
    test=[r for r in reps if TEST[0]<=r["year"]<=TEST[1]]
    assert len(train)==len(groups)*168 and len(val)==len(groups)*60 and len(test)==len(groups)*120
    coef=fit_ridge(train)
    validation={model:score(val,lambda r,m=model:predictions(r,coef)[m]) for model in MODELS}
    chosen=min(MODELS,key=lambda m:(validation[m]["rmse_c"],MODELS.index(m)))
    testing={model:score(test,lambda r,m=model:predictions(r,coef)[m]) for model in MODELS}
    baseline=testing["climatologia"]["rmse_c"]
    persist=testing["persistencia"]["rmse_c"]
    preferred=testing[chosen]["rmse_c"]
    comparison={
        "rmse_seleccionado_c":preferred,
        "skill_rmse_frente_climatologia":round(1-preferred/baseline,6) if baseline>1e-9 else None,
        "skill_rmse_frente_persistencia":round(1-preferred/persist,6) if persist>1e-9 else None,
        "mejora_frente_climatologia":preferred<baseline,
        "mejora_frente_persistencia":preferred<persist
    }
    perSite=[]
    for pid in sorted(monthly):
        subset=[r for r in rows if r["pid"]==pid and TEST[0]<=r["year"]<=TEST[1]]
        perf={model:score(subset,lambda r,m=model:predictions(r,coef)[m]) for model in MODELS}
        perSite.append({
          "id":pid,"transecto":transects[pid],"centro_celda_era5land":list(centers[pid]),
          "n_meses_2016_2025":len(subset),"rmse_seleccionado_c":perf[chosen]["rmse_c"],
          "mae_seleccionado_c":perf[chosen]["mae_c"],
          "rmse_climatologia_c":perf["climatologia"]["rmse_c"],
          "rmse_persistencia_c":perf["persistencia"]["rmse_c"],
          "rmse_jerarquico_c":perf["jerarquico"]["rmse_c"],
          "replica_de_celda_compartida":len(groups[tuple(centers[pid])])>1
        })
    csvrows=[]
    for r in rows:
        if TEST[0]<=r["year"]<=TEST[1]:
            p=predictions(r,coef)
            csvrows.append({
              "mes_objetivo":r["date"],"testigo_id":r["pid"],
              "transecto":transects[r["pid"]],
              "centro_celda_t":f"{centers[r['pid']][0]:.5f};{centers[r['pid']][1]:.5f}",
              "observacion_anomalia_c":round(r["y"],5),
              "climatologia_pred_c":round(p["climatologia"],5),
              "persistencia_pred_c":round(p["persistencia"],5),
              "regional_rezago_pred_c":round(p["regional_rezago"],5),
              "modelo_jerarquico_pred_c":round(p["jerarquico"],5),
              "seleccionado_pred_c":round(p[chosen],5),
              "metodo_seleccionado":chosen,
              "ultimo_mes_observado":r["prev"]})
    summary={
      "fase":"8R","tipo":"backtest_cronologico_pseudoprospectivo_un_mes",
      "modelo_fuente":"ERA5-Land via Open-Meteo, mismo proveedor histórico",
      "periodo_normales_exclusivo_calibracion":"1996–2010",
      "periodo_ajuste_coeficientes":"1997–2010",
      "periodo_seleccion_estrategia":"2011–2015",
      "periodo_prueba_estrictamente_reservado":"2016–2025",
      "fecha_corte_train":"2010-12",
      "fecha_corte_validacion":"2015-12",
      "horizonte":"un_mes_calendario_adelante",
      "n_meses_prueba_por_sitio":120,
      "n_sitios":len(monthly),"n_centros_celda_era5land_distintos":len(groups),
      "n_sitios_pseudoreplicados":sum(len(names)-1 for names in groups.values()),
      "conteo_valoracion_seleccion_por_celda_no_por_consulta":True,
      "periodo_de_entrenamiento_val_test_no_solapado":True,
      "variables_explicativas_disponibles_t_menos_1":True,
      "modelo_regional_excluye_el_pixel_del_objetivo":True,
      "senal_regional_promedio_pixels_distintos":True,
      "normal_de_validacion_test_no_utilizada_en_entrenamiento":True,
      "estrategias":DESC,"coeficientes_ridge_congelados":dict(zip(("intercepto","rezago_local","rezago_regional"),[round(x,8) for x in coef])),
      "penalizacion_ridge":1.,
      "evaluacion_validacion_rmse_por_celda":validation,
      "estrategia_seleccionada_por_validacion":chosen,
      "evaluacion_prueba_por_celda":testing,
      "comparacion_prueba":comparison,
      "evaluacion_prueba_por_testigo":perSite,
      "n_registros_prueba_por_sitio":len(csvrows),
      "pronostico_operativo_validado_senamhi":False,
      "evaluacion_prospectiva_real":False,
      "validacion_instrumental_independiente":False,
      "zonas_agroclimaticas_homogeneas_certificadas":0,
      "capacidad_predictiva_ENFEN_demostrada":False,
      "riesgo_fitosanitario_validado":False,
      "cautelas":[
        "Calibración y validación usan reanálisis ERA5-Land; resultados no son habilidad instrumental ni independencia espacial.",
        "Las series del test retrospectivo permiten conocer las observaciones de meses ya transcurridos para predecir t+1; no hay predicciones realmente emitidas en 2015.",
        "Escoger el mejor modelo en validación no garantiza superar climatología o persistencia en 2016-2025.",
        "Los centros de rejilla pueden repetirse o ser autocorrelacionados. El promedio regional excluye el píxel objetivo y pondera píxeles distintos una sola vez.",
        "Los parámetros 1996–2010 no representan la normal climática final OAF 1996–2025; es una ventana de calibración necesaria para no contaminar el test.",
        "No se ha usado una fuente independiente SENAMHI y los transectos no son regiones cartográficas certificadas."
      ]
    }
    return summary,csvrows

def load_archive(root):
    audit,selected,climate_metrics,cell_rows,covariation=reference.evaluate(root)
    if audit["fase"]!="8Q" or audit["fuentes_climaticas_verificadas"]!=6 or len(selected)!=10:
        raise ValueError("8Q aún no tiene datos completos auditados")
    pts=reference.points(selected)
    parsed={}
    cells=defaultdict(set)
    for start,end in history.BLOCKS:
        original=reference.inspect(root,"era5_land",start,end,pts)
        if original is None:raise ValueError("Falta archivo de ERA5-Land")
        for site,obj in zip(pts,original):
            pid=site["id"]
            daily=obj["daily"]
            center=(round(float(obj["latitude"]),5),round(float(obj["longitude"]),5))
            cells[pid].add(center)
            monthly=parsed.setdefault(pid,{})
            buckets=defaultdict(list)
            for day,temp in zip(daily["time"],daily["temperature_2m_mean"]):
                buckets[day[:7]].append(float(temp))
            for mon,temps in buckets.items():
                if mon in monthly:raise ValueError("Mes duplicado")
                monthly[mon]=statistics.mean(temps)
    if any(len(v)!=1 for v in cells.values()):
        raise ValueError("Centro de celda variable entre décadas: no deduplicar")
    centers={pid:next(iter(v)) for pid,v in cells.items()}
    transects={p["testigo_id"]:p["transecto"] for p in selected}
    return parsed,centers,transects,{"archivos_fuente_sha256":[{
         "modelo":"era5_land","inicio":start,"fin":end,
         "sha256_archivo_original_comprimido":hashlib.sha256(reference.source_paths(
             root,"era5_land",start,end)[0].read_bytes()).hexdigest()}
         for start,end in history.BLOCKS],
         "fase_fuente":"8Q","inspeccion_validada":True}

def csv_text(rows):
    buf=io.StringIO(newline="")
    writer=csv.DictWriter(buf,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    return buf.getvalue()

def publish(root,check=False):
    monthly,centers,transects,trace=load_archive(root)
    report,rows=exercise(monthly,centers,transects)
    report["trazabilidad"]=trace
    base=root/DIR
    out={
      base/"estado_validacion_8r.json":json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
      base/"predicciones_retrospectivas_8r.csv":csv_text(rows)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,value in out.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=value:
                raise ValueError("Estado 8R no reproducible a partir de fuentes 8Q")
        elif not path.exists() or path.read_text(encoding="utf-8")!=value:
            path.write_text(value,encoding="utf-8")
    print(json.dumps({"fase":"8R","metodo":report["estrategia_seleccionada_por_validacion"],
       "rmse_test":report["evaluacion_prueba_por_celda"][report["estrategia_seleccionada_por_validacion"]]["rmse_c"],
       "skill_climatologia":report["comparacion_prueba"]["skill_rmse_frente_climatologia"],
       "pixels":report["n_centros_celda_era5land_distintos"],
       "check":check},ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    publish(args.root,args.check)
