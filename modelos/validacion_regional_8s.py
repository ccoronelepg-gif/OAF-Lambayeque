#!/usr/bin/env python3
"""OAF Fase 8S: validación regional de anomalías térmicas, temporal y por bloques.

Fuentes ERA5-Land de OAF 8O/8P archivadas, verificadas por hash, 1996–2025.
Cada normal local utiliza SOLO años de entrenamiento, y cada predictor t-1.
No mezclar celdas duplicadas como replicaciones independientes; no usar
test para ajustar parámetros o elegir estrategia. El control espacial
retiene franjas geográficas completas, pero permite al sitio reservado su
climatología histórica preexistente y rezago local: transferencia PARCIAL.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import perfiles_climaticos_8o as src8o
import clima_vecindades_8p as src8p
import validacion_anomalias_8r as core

ROOT=Path(__file__).resolve().parents[1]
OUT="datos/validacion_regional_8s"
YEARS=((2008,2009,2011,2012,2014),
       (2011,2012,2014,2015,2017),
       (2014,2015,2017,2018,2020),
       (2017,2018,2020,2021,2022),
       (2020,2021,2022,2023,2025))
MODELS=core.MODELS
ALT=("llanura_costa","valle_bajo","piedemonte",
     "montana_baja","montana_media","montana_alta")
COLUMNS=("evaluacion","corte","bloque_retenido","modelo_seleccionado",
         "centro_celda_era5land","estrato_altitudinal","mes_objetivo",
         "anomalía_observada_c","prediccion_c","persistencia_c",
         "climatologia_c","mes_dato_mas_reciente")
PERIODS=("1996–2025","1996-2025")

def load_catalog(root):
    """Read original 8O and completed 8P with the provider audits in place."""
    state=json.loads((root/src8p.OUT/"estado_clima_8p.json").read_text(encoding="utf-8"))
    if (state.get("fase")!="8P" or state.get("testigos_climaticos_reutilizados_8o")!=19
        or state.get("zonas_homogeneas_geograficas_certificadas")!=0):
        raise ValueError("8P regional no posee trazabilidad climática válida")
    original=src8o.read_testigos(root)
    if len(original)!=19:raise ValueError("19 testigos 8O no comprobados")
    selected=src8p.nodes(root)
    completed=state.get("grupos_de_descarga_completos",[])
    if any(type(i)!=int or i not in range(1,len(src8p.chunked(selected))+1) for i in completed):
        raise ValueError("8P declara lote histórico no válido")
    info={}
    for p in original:
        info[p["id"]]={"id":p["id"],"latitud":p["latitud"],
           "longitud":p["longitud"],"altitud_dem_m":p["altitud_dem_m"],
           "estrato_fisico_preliminar":p["estrato_fisico_preliminar"],
           "fase_fuente":"8O"}
    batches=src8p.chunked(selected)
    for batch in completed:
        for p in batches[batch-1]:
            info[p["id"]]={"id":p["id"],"latitud":p["latitud"],
              "longitud":p["longitud"],"altitud_dem_m":p["altitud_dem_m"],
              "estrato_fisico_preliminar":p["estrato_fisico_preliminar"],
              "fase_fuente":"8P"}
    monthly={};cells=defaultdict(set);provenance=[]
    def ingest(points,series,origin,start,end,archive):
        # Never silently use a partial, corrupted or shifted period.
        for site,block in zip(points,series):
            pid=site["id"]
            if pid not in info:raise ValueError("Site without source inventory")
            cells[pid].add((round(float(block["latitude"]),5),
                            round(float(block["longitude"]),5)))
            vals=monthly.setdefault(pid,{})
            buckets=defaultdict(list)
            for day,temp in zip(block["daily"]["time"],block["daily"]["temperature_2m_mean"]):
                buckets[day[:7]].append(float(temp))
            for month,ts in buckets.items():
                if month in vals:raise ValueError("Mes reanalizado dos veces")
                vals[month]=statistics.mean(ts)
        provenance.append({"fuente":origin,"inicio":start,"fin":end,
            "sha256_archivo_comprimido":hashlib.sha256(archive.read_bytes()).hexdigest(),
            "centros_en_solicitud":len(points)})
    for start,end in src8o.BLOCKS:
        data=src8o.read_source(root,"era5_land",start,end,original)
        if data is None:raise ValueError("Fuente ERA5-Land 8O incompleta")
        raw,_=data
        archive=src8o.raw_paths(root,"era5_land",start,end)[0]
        ingest(original,raw,"8O",start,end,archive)
    for groupidx in completed:
        points=batches[groupidx-1]
        for start,end in src8o.BLOCKS:
            raw=src8p.inspect(root,groupidx,"era5_land",start,end,points)
            if raw is None:raise ValueError("8P indica lote completo sin ERA5-Land")
            archive=src8p.paths(root,groupidx,"era5_land",start,end)[0]
            ingest(points,raw,"8P_grupo_"+str(groupidx),start,end,archive)
    if len(monthly)!=len(info) or len(monthly)!=state["testigos_total_con_30_anios"]:
        raise ValueError("Inventario de puntos climáticos 8P no coincide")
    if any(len(centers)!=1 for centers in cells.values()):
        raise ValueError("Centro ERA5-Land cambió dentro del periodo")
    # DEM<=5m can include coast, water and near-sea cells. This is a
    # deliberately cautious filter, not a verified shore/land mask.
    dropped=[pid for pid in monthly if info[pid]["altitud_dem_m"]<=5]
    for pid in dropped:
        monthly.pop(pid);cells.pop(pid)
    centers={pid:next(iter(x)) for pid,x in cells.items()}
    meta={pid:info[pid] for pid in monthly}
    if len(monthly)<30 or len(set(centers.values()))<12:
        raise ValueError("La expansión 8S regional es aún muy pequeña")
    return monthly,centers,meta,{"fuentes_temperatura_reanalisis":provenance,
       "testigos_8p_8o_disponibles":len(info),"testigos_descartados_dem_le_5_m":len(dropped),
       "estado_original_8p_sha256":hashlib.sha256((root/src8p.OUT/"estado_clima_8p.json").read_bytes()).hexdigest()}

def geographic_groups(centers,count=4):
    """Latitude bands of ERA5-Land centres, balanced by distinct cells."""
    unique=sorted(set(centers.values()))
    if len(unique)<count*3:raise ValueError("Insuficientes centros para prueba regional espacial")
    grouping={}
    for j,coordinate in enumerate(unique):
        label="LAT"+str(min(count-1,j*count//len(unique))+1)
        grouping[coordinate]=label
    byname=defaultdict(list)
    for cell,band in grouping.items():byname[band].append(cell)
    if len(byname)!=count or any(len(values)<2 for values in byname.values()):
        raise ValueError("Bloque geográfico carece de suficientes centros")
    return grouping

def monthly_folds(monthly,centers,train_end,band_held=None,groups=None):
    """No future data in site normals; no held band in regional predictors."""
    years=range(1996,train_end+1)
    ids=sorted(monthly)
    complete=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
    if any(sorted(monthly[pid])!=complete or
           any(type(value) not in (int,float) or not math.isfinite(value)
               for value in monthly[pid].values()) for pid in ids):
        raise ValueError("Histórico mensual incompleto o no numérico entre 1996 y 2025")
    norm={pid:{m:statistics.mean(monthly[pid][f"{year}-{m:02d}"] for year in years)
              for m in range(1,13)} for pid in ids}
    unique=core.cell_groups(centers)
    representatives={cell:names[0] for cell,names in unique.items()}
    included={cell:pid for cell,pid in representatives.items()
              if band_held is None or groups[cell]!=band_held}
    if len(included)<3:raise ValueError("Muy pocas celdas en grupo de entrenamiento")
    deviations={pid:{month:monthly[pid][month]-norm[pid][int(month[-2:])] for month in complete}
                for pid in ids}
    rows=[]
    for t in range(1,len(complete)):
        month=complete[t];last=complete[t-1]
        for cell,pid in representatives.items():
            peers=[deviations[p][last] for c,p in included.items() if c!=cell]
            if not peers:raise ValueError("No hay predictor regional excluyendo la propia celda")
            rows.append({"pid":pid,"cell":cell,"date":month,"prev":last,
              "year":int(month[:4]),"y":deviations[pid][month],
              "local":deviations[pid][last],"regional":statistics.mean(peers)})
    return rows,unique,norm

def metrics(rows,model,coef):
    return core.score(rows,lambda r:core.predictions(r,coef)[model])

def evaluate_region(monthly,centers,meta):
    cells=core.cell_groups(centers)
    groups=geographic_groups(centers)
    outcomes=[];regional_rows=[];spatial_rows=[];warnings=[]
    for i,(train_end,v0,v1,t0,t1) in enumerate(YEARS,1):
        if not (1996<train_end<v0<=v1<t0<=t1<=2025):
            raise ValueError("Separación cronológica 8S no válida")
        base,unique,_=monthly_folds(monthly,centers,train_end)
        train=[r for r in base if 1997<=r["year"]<=train_end]
        val=[r for r in base if v0<=r["year"]<=v1]
        test=[r for r in base if t0<=r["year"]<=t1]
        coef=core.fit_ridge(train)
        vscore={x:metrics(val,x,coef) for x in MODELS}
        choice=min(MODELS,key=lambda x:(vscore[x]["rmse_c"],MODELS.index(x)))
        tscore={x:metrics(test,x,coef) for x in MODELS}
        report={"corte":i,"train":"1997–"+str(train_end),"normal_local":"1996–"+str(train_end),
          "validacion":str(v0)+"–"+str(v1),"prueba":str(t0)+"–"+str(t1),
          "n_centros":len(unique),"modelo_elegido":choice,
          "rmse_validacion_por_modelo":{k:v["rmse_c"] for k,v in vscore.items()},
          "rmse_prueba_por_modelo":{k:v["rmse_c"] for k,v in tscore.items()},
          "n_observaciones_test":len(test),"coeficientes_ajustados":[round(x,7) for x in coef]}
        outcomes.append(report)
        for r in test:
            pred=core.predictions(r,coef)
            regional_rows.append({
              "evaluacion":"temporal","corte":i,"bloque_retenido":"todos",
              "modelo_seleccionado":choice,
              "centro_celda_era5land":f"{r['cell'][0]:.5f};{r['cell'][1]:.5f}",
              "estrato_altitudinal":meta[r["pid"]]["estrato_fisico_preliminar"],
              "mes_objetivo":r["date"],"anomalía_observada_c":round(r["y"],6),
              "prediccion_c":round(pred[choice],6),
              "persistencia_c":round(pred["persistencia"],6),
              "climatologia_c":0.,"mes_dato_mas_reciente":r["prev"]})
        # Hold an entire latitude band from coefficient fitting/selection
        # AND from every regional predictor in the fit and val.
        for band in sorted(set(groups.values())):
            rows,_,_=monthly_folds(monthly,centers,train_end,band,groups)
            tr=[r for r in rows if groups[r["cell"]]!=band and 1997<=r["year"]<=train_end]
            va=[r for r in rows if groups[r["cell"]]!=band and v0<=r["year"]<=v1]
            te=[r for r in rows if groups[r["cell"]]==band and t0<=r["year"]<=t1]
            coefS=core.fit_ridge(tr)
            selectScore={x:metrics(va,x,coefS)["rmse_c"] for x in MODELS}
            selected=min(MODELS,key=lambda x:(selectScore[x],MODELS.index(x)))
            scored={x:metrics(te,x,coefS) for x in MODELS}
            for r in te:
                p=core.predictions(r,coefS)
                spatial_rows.append({
                  "evaluacion":"espacial","corte":i,"bloque_retenido":band,
                  "modelo_seleccionado":selected,
                  "centro_celda_era5land":f"{r['cell'][0]:.5f};{r['cell'][1]:.5f}",
                  "estrato_altitudinal":meta[r["pid"]]["estrato_fisico_preliminar"],
                  "mes_objetivo":r["date"],"anomalía_observada_c":round(r["y"],6),
                  "prediccion_c":round(p[selected],6),
                  "persistencia_c":round(p["persistencia"],6),
                  "climatologia_c":0.,"mes_dato_mas_reciente":r["prev"]})
            warnings.append({"corte":i,"bloque":band,"centros_retenidos":len({r["cell"] for r in te}),
              "metodo_elegido_otros_bloques":selected,
              "rmse_prueba_retenido":scored[selected]["rmse_c"],
              "rmse_persistencia_retenido":scored["persistencia"]["rmse_c"],
              "rmse_climatologia_retenido":scored["climatologia"]["rmse_c"]})
    return outcomes,regional_rows,spatial_rows,warnings,groups

def series_report(items):
    if not items:return None
    errors=[float(v["prediccion_c"])-float(v["anomalía_observada_c"]) for v in items]
    pers=[float(v["persistencia_c"])-float(v["anomalía_observada_c"]) for v in items]
    clim=[float(v["anomalía_observada_c"]) for v in items]
    def calc(a):
        return {"rmse_c":round(math.sqrt(statistics.mean(v*v for v in a)),6),
                "mae_c":round(statistics.mean(abs(v) for v in a),6)}
    a,b,c=map(calc,(errors,pers,clim))
    def skill(x,y):return round(1-x/y,6) if y>0 else None
    return {"n":len(items),"seleccionado":a,"persistencia":b,"climatologia":c,
       "skill_rmse_vs_persistencia":skill(a["rmse_c"],b["rmse_c"]),
       "skill_rmse_vs_climatologia":skill(a["rmse_c"],c["rmse_c"]),
       "mejora_persistencia":a["rmse_c"]<b["rmse_c"]}

def report_bands(rows):
    bands=sorted({r["estrato_altitudinal"] for r in rows})
    return [{"estrato":band,**series_report([r for r in rows if r["estrato_altitudinal"]==band])}
            for band in bands]

def textcsv(rows):
    buffer=io.StringIO(newline="")
    writer=csv.DictWriter(buffer,fieldnames=COLUMNS,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    return buffer.getvalue()

def compile(root):
    monthly,centers,meta,trace=load_catalog(root)
    runs,timepred,spacepred,splits,groups=evaluate_region(monthly,centers,meta)
    unique=core.cell_groups(centers)
    stat={
      "fase":"8S","estado":"ensayo_regional_reanalisis_completo_no_operativo",
      "periodo_fuente":"1996–2025","horizonte":"anomalia_termica_un_mes",
      "fuente":"temperatura diaria ERA5-Land via Open-Meteo, archivos 8O/8P",
      "testigos_climaticos_regionales_disponibles":trace["testigos_8p_8o_disponibles"],
      "testigos_excluidos_dem_le_5m":trace["testigos_descartados_dem_le_5_m"],
      "testigos_empleados":len(monthly),
      "centros_celda_era5land_unicos":len(unique),
      "consultas_redundantes_descartadas":len(monthly)-len(unique),
      "n_cortes_rolling_origin":len(YEARS),
      "cortes_temporales":runs,
      "n_bloques_espaciales_latitudinales":len(set(groups.values())),
      "bloques_latitudinales_no_cuencas_ni_zonas_agricolas":True,
      "n_pruebas_bloque_espacial":len(splits),
      "pliegues_espaciales":splits,
      "evaluacion_temporal":series_report(timepred),
      "evaluacion_con_bloque_retenido":series_report(spacepred),
      "evaluacion_por_estrato_altitudinal":report_bands(spacepred),
      "n_predicciones_temporales":len(timepred),
      "n_predicciones_espaciales":len(spacepred),
      "red_espacial_de_solo_reanalisis_sin_sensores":True,
      "climatologia_sitio_del_bloque_retenido_historicamente_disponible":True,
      "variables_predictores_disponibles_hasta_t_menos_1":True,
      "ningun_test_utilizado_en_ajuste_o_seleccion":True,
      "señal_regional_entrenamiento_excluye_bloque_espacial_retenido":True,
      "normal_local_recalculada_solo_con_periodo_de_entrenamiento":True,
      "prediccion_operativa_o_prospectiva_demostrada":False,
      "habilidad_confirmada_con_estaciones_SENAMHI":False,
      "zonas_agroclimaticas_homogeneas_certificadas":0,
      "modelo_ENFEN_Nino_costero_verificado":False,
      "riesgos_fitosanitarios_arandano_vid_validados":False,
      "advertencias":[
        "Validación retrospectiva de un mes; no hay pronósticos realmente emitidos ni verificación prospectiva.",
        "Todas las temperaturas proceden de ERA5-Land: el mismo sistema genera predictores y observaciones objetivo.",
        "Las bandas norte-sur son particiones experimentales, no unidades agroclimáticas de producción, cuencas ni polígonos homogéneos.",
        "Al retener una franja, sí se permite su normal de entrenamiento y anomalía local del mes anterior: no se demuestra extrapolación sin registros locales.",
        "Celdas distintas de un mismo reanálisis pueden conservar autocorrelación espacial y errores compartidos.",
        "No hay fuente independiente de estaciones SENAMHI ni cartografía IGN/INEI homologada para delimitar zonas agrícolas.",
        "Algunos cortes podrían empeorar frente a persistencia. Revisar tablas completas, no solo agregados.",
        "No se utiliza teleconexión ENFEN/ENSO ni medición agrícola o enfermedades en este backtest."
      ],
      "trazabilidad":trace
    }
    return stat,timepred,spacepred

def publish(root,check=False):
    stat,a,b=compile(root)
    out={
      root/OUT/"estado_validacion_8s.json":json.dumps(stat,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
      root/OUT/"predicciones_temporales_8s.csv":textcsv(a),
      root/OUT/"predicciones_bloques_8s.csv":textcsv(b)}
    if not check:(root/OUT).mkdir(parents=True,exist_ok=True)
    for path,contents in out.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=contents:
                raise ValueError("8S salida no reproduce sus fuentes originales")
        elif not path.exists() or path.read_text(encoding="utf-8")!=contents:
            path.write_text(contents,encoding="utf-8")
    print(json.dumps({"fase":"8S","testigos":stat["testigos_empleados"],
       "celulas_unicas":stat["centros_celda_era5land_unicos"],
       "rmse_temporal":stat["evaluacion_temporal"]["seleccionado"]["rmse_c"],
       "rmse_espacial":stat["evaluacion_con_bloque_retenido"]["seleccionado"]["rmse_c"],
       "check":check},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    publish(a.root,a.check)
