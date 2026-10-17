#!/usr/bin/env python3
"""OAF 8T: NOAA CPC SST Niño1+2 (snapshot) + 8S rolling spatial evaluation.

The NOAA CPC index is a revised historical vintage. Uses t-2 exclusively,
never target month's SST. No retrospective release-vintage access: results
are NOT genuine historical forecasts, operational ENSO skill, or SENAMHI QA.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
sys.path.insert(0,str(Path(__file__).resolve().parent))
import validacion_regional_8s as regional
import validacion_anomalias_8r as predictor

ROOT=Path(__file__).resolve().parents[1]
URL="https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
RAW="datos/oceano_8t/noaa_cpc_sstoi_indices.txt.gz"
META="datos/oceano_8t/noaa_cpc_sstoi_indices.meta.json"
OUT="datos/validacion_oceanica_8t"
COLUMN=("prueba","corte","bloque_retenido","modelo_preseleccionado",
        "celda_termica","estrato","mes_objetivo",
        "mes_indice_noaa","anomalia_nino12_rezagada_c",
        "anomalia_tmedia_objetivo_c","prediccion_noaa_c",
        "prediccion_jerarquica_c","prediccion_seleccionada_c",
        "prediccion_persistencia_c","indice_es_revisado")
MODEL=("jerarquico_8s","jerarquico_nino12")
ALPHA=1.

def checksum(raw):return hashlib.sha256(raw).hexdigest()

def parse_noaa(raw):
    """NOAA CPC format: YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM."""
    text=raw.decode("utf-8-sig")
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    if not lines or not lines[0].startswith("YR MON") or "NINO1+2" not in lines[0]:
        raise ValueError("Cabecera NOAA CPC Niño 1+2 no identificada")
    all_index={}
    for record in lines[1:]:
        fields=record.split()
        if len(fields)!=10:raise ValueError("Línea NOAA con columnas no reconocidas")
        try:
            year=int(fields[0]);month=int(fields[1]);v=list(map(float,fields[2:]))
        except (TypeError,ValueError) as e:
            raise ValueError("Registro NOAA con valores no numéricos") from e
        if not 1<=month<=12 or not all(math.isfinite(x) for x in v):
            raise ValueError("Fecha o valor NOAA fuera del dominio")
        # 1+2 SST (index 0), 1+2 anomaly (index 1), 3.4 SST (index 6), 3.4 anomaly (index 7)
        if not(10<=v[0]<=35 and -10<v[1]<10 and 10<=v[6]<=35 and -10<v[7]<10):
            raise ValueError("Temperaturas/anomalías NOAA inverosímiles")
        key=f"{year:04d}-{month:02d}"
        if key in all_index:raise ValueError("Serie NOAA con mes duplicado")
        all_index[key]={"nino12_anom_c":v[1],"nino34_anom_c":v[7]}
    required=[f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)]
    missing=[x for x in required if x not in all_index]
    if missing:raise ValueError("Niño 1+2 NOAA 1996–2025 no reúne 360 meses")
    return {date:all_index[date] for date in required}

def paths(root):
    return root/RAW,root/META

def archive(root):
    file,meta=paths(root)
    if not file.exists() or not meta.exists():
        raise ValueError("No existe archivo de observación NOAA con huella verificable")
    raw=gzip.decompress(file.read_bytes())
    x=json.loads(meta.read_text(encoding="utf-8"))
    if (x.get("fuente")!="NOAA CPC SST Niño indices" or x.get("url")!=URL or
        x.get("sha256_original")!=checksum(raw) or
        x.get("nino12_mes_referencia")!="1996–2025" or
        x.get("indices_revisables_retroactivamente") is not True):
        raise ValueError("Archivo NOAA sin identidad y huella SHA comprobable")
    values=parse_noaa(raw)
    if len(values)!=x.get("n_meses_estudio"):raise ValueError("SST NOAA periodo/metadata inconsistente")
    return values,x

def acquire(root):
    path,meta=paths(root)
    if path.exists() or meta.exists():
        archive(root)
        print("Fuente NOAA ya fijada por SHA; no se sobreescribe automáticamente.")
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    with urlopen(Request(URL,headers={"User-Agent":"OAF-Lambayeque-8T-research/1.0"}),
                 timeout=75) as response:
        if response.status!=200:raise ValueError("HTTP NOAA no exitoso")
        blob=response.read(170_001)
        if len(blob)>170_000:raise ValueError("Archivo NOAA excede límite esperado")
    rows=parse_noaa(blob)
    info={"fuente":"NOAA CPC SST Niño indices",
          "url":URL,"consultado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
          "sha256_original":checksum(blob),
          "nino12_mes_referencia":"1996–2025","n_meses_estudio":len(rows),
          "indices_revisables_retroactivamente":True,
          "tipo":"OISST índice mensual NOAA CPC (serie actual revisable)",
          "observacion_en_archivo_no_equivale_a_vintage_realtime":True,
          "variable_usada":"NINO1+2 ANOM",
          "rezago_meses_prueba":2,
          "prohibido_inferir_aviso_ENFEN":True}
    path.write_bytes(gzip.compress(blob,mtime=0))
    meta.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Serie NOAA recuperada y congelada con SHA-256:",info["sha256_original"])

def gauss(a,b):
    n=len(b); matrix=[list(a[i])+[b[i]] for i in range(n)]
    for i in range(n):
        j=max(range(i,n),key=lambda k:abs(matrix[k][i]))
        if abs(matrix[j][i])<1e-10:raise ValueError("Regresión oceánica no invertible")
        matrix[i],matrix[j]=matrix[j],matrix[i]
        scale=matrix[i][i]
        matrix[i]=[v/scale for v in matrix[i]]
        for row in range(n):
            if row==i:continue
            w=matrix[row][i]
            matrix[row]=[v-w*t for v,t in zip(matrix[row],matrix[i])]
    return [matrix[i][-1] for i in range(n)]

def fit_enriched(rows):
    if len(rows)<100:raise ValueError("Muy pocas observaciones para regresión NOAA")
    n=4;a=[[0.0]*n for _ in range(n)];b=[0.0]*n
    for row in rows:
        f=[1.,row["local"],row["regional"],row["ocean12"]]
        for i in range(n):
            b[i]+=f[i]*row["y"]
            for j in range(n):a[i][j]+=f[i]*f[j]
    for i in range(1,n):a[i][i]+=ALPHA
    return gauss(a,b)

def add_ocean(rows,index):
    """Conservative t-2 ocean lag, independent of target/previous monthly SST."""
    result=[]
    for row in rows:
        year,month=map(int,row["date"].split("-"))
        t=(year*12+month-1)-2
        key=f"{t//12:04d}-{t%12+1:02d}"
        if key not in index:continue  # only early train months before 1996-01
        a={**row,"ocean12":index[key]["nino12_anom_c"],
           "ocean34":index[key]["nino34_anom_c"],"ocean_month":key}
        if not(a["ocean_month"]<row["prev"]<row["date"]):
            raise ValueError("Fuga de información oceánica temporal")
        result.append(a)
    return result

def predict(row,coeff_base,coeff_new):
    p_base=coeff_base[0]+coeff_base[1]*row["local"]+coeff_base[2]*row["regional"]
    p_new=(coeff_new[0]+coeff_new[1]*row["local"]+coeff_new[2]*row["regional"]+
           coeff_new[3]*row["ocean12"])
    return {"jerarquico_8s":p_base,"jerarquico_nino12":p_new,
            "persistencia":row["local"],"climatologia":0.}

def rmse(rows,func):
    return predictor.score(rows,func)["rmse_c"]

def stats(records):
    if not records:return None
    def error(field):
        delta=[float(r[field])-float(r["anomalia_tmedia_objetivo_c"]) for r in records]
        return {"rmse_c":round(math.sqrt(statistics.mean(v*v for v in delta)),6),
                "mae_c":round(statistics.mean(abs(v) for v in delta),6)}
    e=error("prediccion_seleccionada_c")
    base=error("prediccion_jerarquica_c")
    persist=error("prediccion_persistencia_c")
    gain=round(1-e["rmse_c"]/base["rmse_c"],6) if base["rmse_c"]>1e-10 else None
    return {"n":len(records),"modelo_seleccionado":e,"modelo_8s_sin_oceano":base,
            "persistencia":persist,
            "mejora_RMSE_vs_8S":gain,
            "mejora_RMSE_vs_persistencia":round(1-e["rmse_c"]/persist["rmse_c"],6)
                 if persist["rmse_c"]>1e-10 else None}

def evaluate(monthly,centers,meta,index):
    bands=regional.geographic_groups(centers)
    temporal=[];spatial=[];windows=[];spacefolds=[]
    for number,(endtrain,startval,endval,starttest,endtest) in enumerate(regional.YEARS,1):
        def fit_fold(hold=None):
            allrows,grp,normals=regional.monthly_folds(monthly,centers,endtrain,hold,bands)
            dat=add_ocean(allrows,index)
            tr=[r for r in dat if 1997<=r["year"]<=endtrain and (hold is None or bands[r["cell"]]!=hold)]
            va=[r for r in dat if startval<=r["year"]<=endval and (hold is None or bands[r["cell"]]!=hold)]
            te=[r for r in dat if starttest<=r["year"]<=endtest and (hold is None or bands[r["cell"]]==hold)]
            base=predictor.fit_ridge(tr)
            new=fit_enriched(tr)
            val={m:rmse(va,lambda r,model=m:predict(r,base,new)[model]) for m in MODEL}
            selected=min(MODEL,key=lambda m:(val[m],MODEL.index(m)))
            return tr,va,te,base,new,val,selected
        tr,va,te,coeff,aug,v,choice=fit_fold()
        windows.append({"corte":number,"train_end":endtrain,"validacion":f"{startval}–{endval}",
           "prueba":f"{starttest}–{endtest}","n_train":len(tr),"n_test":len(te),
           "rmse_validacion_8s":v["jerarquico_8s"],"rmse_validacion_nino12":v["jerarquico_nino12"],
           "modelo_preseleccionado":choice,
           "coeficiente_nino12":round(aug[3],8),
           "rmse_prueba_8s":rmse(te,lambda r:predict(r,coeff,aug)["jerarquico_8s"]),
           "rmse_prueba_oceanico":rmse(te,lambda r:predict(r,coeff,aug)["jerarquico_nino12"]),
           "rmse_prueba_seleccionado":rmse(te,lambda r:predict(r,coeff,aug)[choice])})
        for r in te:
            p=predict(r,coeff,aug)
            temporal.append(make_row("temporal",number,"todos",choice,r,p,meta))
        for held in sorted(set(bands.values())):
            tr,va,te,coeff,aug,v,choice=fit_fold(held)
            spacefolds.append({"corte":number,"franja":held,"celdas_retenidas":len({r["cell"] for r in te}),
                "modelo_preseleccionado":choice,
                "coeficiente_nino12":round(aug[3],8),
                "rmse_8s":rmse(te,lambda r:predict(r,coeff,aug)["jerarquico_8s"]),
                "rmse_oceano":rmse(te,lambda r:predict(r,coeff,aug)["jerarquico_nino12"]),
                "rmse_seleccionado":rmse(te,lambda r:predict(r,coeff,aug)[choice])})
            for r in te:
                spatial.append(make_row("espacial",number,held,choice,r,predict(r,coeff,aug),meta))
    return temporal,spatial,windows,spacefolds

def make_row(kind,cut,held,choice,r,p,meta):
    return {"prueba":kind,"corte":cut,"bloque_retenido":held,
      "modelo_preseleccionado":choice,
      "celda_termica":f"{r['cell'][0]:.5f};{r['cell'][1]:.5f}",
      "estrato":meta[r["pid"]]["estrato_fisico_preliminar"],
      "mes_objetivo":r["date"],"mes_indice_noaa":r["ocean_month"],
      "anomalia_nino12_rezagada_c":round(r["ocean12"],4),
      "anomalia_tmedia_objetivo_c":round(r["y"],6),
      "prediccion_noaa_c":round(p["jerarquico_nino12"],6),
      "prediccion_jerarquica_c":round(p["jerarquico_8s"],6),
      "prediccion_seleccionada_c":round(p[choice],6),
      "prediccion_persistencia_c":round(p["persistencia"],6),
      "indice_es_revisado":"true"}

def textcsv(rows):
    buf=io.StringIO(newline="")
    writer=csv.DictWriter(buf,fieldnames=COLUMN,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    return buf.getvalue()

def build(root):
    ocean,meta=archive(root)
    monthly,centers,sites,sources=regional.load_catalog(root)
    ts,ss,windows,folds=evaluate(monthly,centers,sites,ocean)
    dates=[r["mes_objetivo"] for r in ts]
    if len(ts)!=len(ss) or len(set((r["celda_termica"],r["mes_objetivo"]) for r in ss))!=len(ss):
        raise ValueError("Evaluación oceánica duplicó celdas-meses")
    if min(dates)!="2012-01" or max(dates)!="2025-12":
        raise ValueError("NOAA t-2 no cubre todos los meses de prueba")
    grouped={key:stats([r for r in ss if r["estrato"]==key]) for key in regional.ALT}
    t=stats(ts);s=stats(ss)
    report={
      "fase":"8T","estado":"contraste_oceanico_retroactivo_auditable_no_operativo",
      "periodo_clima":"1996–2025","horizonte_objetivo":"1 mes",
      "indices_fuente":"NOAA CPC sstoi.indices, Niño1+2 ANOM, serie mensual revisable",
      "corte_fuente_noaa_utc":meta["consultado_utc"],
      "fuente_noaa_url":URL,"sha256_indice_original":meta["sha256_original"],
      "n_meses_noaa_historicos":len(ocean),
      "rezago_oceanico_meses":2,
      "indice_1996_2025_se_puede_revisar_expost":True,
      "no_representa_vintage_NOAA_publicado_en_cada_fecha_historica":True,
      "no_equivale_a_ICEN_ENFEN_ni_a_alerta_oficial":True,
      "entrenamiento_y_normales_solo_anteriores_al_test":True,
      "seleccion_de_modelo_solo_validacion_pasada":True,
      "predictores_local_y_regional_rezagados_un_mes":True,
      "bloque_latitudinal_retenido_fuera_del_ajuste_y_predictores_regionales":True,
      "n_testigos_empleados":len(monthly),
      "n_centros_temperatura_era5land_unicos":len(set(centers.values())),
      "n_cortes_temporales":len(windows),
      "n_bloques_geo":4,
      "n_evaluaciones_temporales":len(ts),"n_evaluaciones_espaciales":len(ss),
      "comparacion_temporal":t,
      "comparacion_bloques_espaciales":s,
      "comparacion_por_estrato":grouped,
      "ventanas_temporales":windows,
      "controles_espaciales":folds,
      "seleccion_oceanica_por_ventanas":dict(Counter(w["modelo_preseleccionado"] for w in windows)),
      "n_pliegues_oceanicos_seleccionados":sum(w["modelo_preseleccionado"]=="jerarquico_nino12" for w in folds),
      "factores_probados":["anomalia_termica_local_t-1","anomalia_termica_otros_pixeles_t-1",
                           "Niño1+2_NOAA_anomalia_t-2"],
      "fuentes_de_datos_senamhi_instrumentales_integradas":0,
      "prediccion_prospectiva_demostrada":False,
      "habilidad_nino_costero_predecir_ENFEN_demostrada":False,
      "zonas_homogeneas_certificadas":0,
      "evaluacion_riesgo_fitopatologico_validada":False,
      "nota":"Análisis incremental exploratorio: si el índice oceánico no ayuda en validación se conserva modelo 8S. Existen revisiones NOAA retrospectivas y el objetivo proviene de ERA5-Land.",
      "limitaciones":[
          "Índices NOAA actuales están revisados retrospectivamente: no son vintages históricos disponibles en las fechas del backtest.",
          "Lag t−2 disminuye filtración inmediata, pero no establece fecha real de publicación mensual ni acceso operativo.",
          "Las franjas espaciales retienen coeficientes y señal regional, pero permiten temperatura y climatología anterior propia de la franja.",
          "No existe contraste independiente con estaciones SENAMHI ni estaciones agrícolas.",
          "El Niño 1+2 histórico NOAA no es el ICEN clasificado por ENFEN ni probabilidad de un evento oficial.",
          "El método exige evaluar ventanas sin elegir el mejor resultado tras leer el test.",
          "Series de NOAA y ERA5-Land no son muestras estadísticamente independientes entre centros y meses."
      ],
      "trazabilidad_climatica":sources
    }
    return report,ts,ss

def publish(root,check=False):
    report,ts,ss=build(root)
    output={root/OUT/"estado_oceanico_8t.json":json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
            root/OUT/"predicciones_oceanicas_temporales_8t.csv":textcsv(ts),
            root/OUT/"predicciones_oceanicas_espaciales_8t.csv":textcsv(ss)}
    if not check:(root/OUT).mkdir(parents=True,exist_ok=True)
    for path,value in output.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=value:
                raise ValueError("Reporte 8T no reproduce índices NOAA y datos 8O/8P")
        elif not path.exists() or path.read_text(encoding="utf-8")!=value:
            path.write_text(value,encoding="utf-8")
    print(json.dumps({"fase":"8T","testigos":report["n_testigos_empleados"],
       "centros":report["n_centros_temperatura_era5land_unicos"],
       "rmse_noaa_seleccionado":report["comparacion_bloques_espaciales"]["modelo_seleccionado"]["rmse_c"],
       "skill_vs_8S":report["comparacion_bloques_espaciales"]["mejora_RMSE_vs_8S"],
       "check":check},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--fetch",action="store_true")
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    if a.fetch:acquire(a.root)
    publish(a.root,a.check)
