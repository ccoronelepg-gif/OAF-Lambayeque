#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9W: puente auditado 9O+9P+9Q a benchmarks 9R,9T,9U.

Los meses CHIRPS v3 finales y los polígonos fueron compilados a posteriori.
La evaluación de 2021-25 es retrospectiva, NO emitida ex-ante.
No comparar GCN 9R y RF 9T como un torneo de protocolo idéntico;
se registran deliberadamente por separado.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/validacion_9w"
BRIDGE=BASE/"matriz_sectores_chirps_9w.csv"
MANIFEST=BASE/"auditoria_puente_9w.json"
EVIDENCE=BASE/"evaluacion_bloques_9w.json"
FLOOR=BASE/"errores_pisos_9w.csv"
YEAR=BASE/"errores_anios_9w.csv"
SOURCES=[
 ("9O","datos/homogeneidad_9o/fuentes_chirps_9o.json","fuentes","datos/homogeneidad_9o/serie_sectores_chirps_9o.csv"),
 ("9P","datos/continuidad_9p/fuentes_adicionales_chirps_9p.json","nuevos","datos/continuidad_9p/meses_adicionales_sectores_9p.csv"),
 ("9Q","datos/recuperacion_9q/fuentes_chirps_9q.json","nuevos","datos/recuperacion_9q/sectores_mensuales_9q.csv")]
GEOMS=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
PRED9R=ROOT/"datos/validacion_predictiva_9r/predicciones_prueba_2021_2025_9r.csv"
STAT9R=ROOT/"datos/validacion_predictiva_9r/comparacion_modelos_9r.json"
GROUPS=ROOT/"datos/recuperacion_9q/agrupaciones_exploratorias_9q.geojson"
T_PRED=ROOT/"resultados/9t/predicciones_fuera_muestra.csv"
T_STATUS=ROOT/"resultados/9t/manifiesto.json"
U_STATUS=ROOT/"resultados/9u/decision.json"
NAMES=("climatologia","random_forest","gcn")
DAYS=[f"{y:04d}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
EPS=.001  # tolerancia máxima 0,001 mm por cast float32 en 9R y redondeo CSV

def hashfile(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def obj(path):return json.loads(path.read_text("utf8"))
def rows(path):
 with path.open("r",newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def writecsv(path, data, cols):
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(data)
def numeric(v,context):
 try:n=float(v)
 except (ValueError,TypeError):raise ValueError("Número inválido "+str(context))
 if not math.isfinite(n) or n<0:raise ValueError("Valor no finito o negativo "+str(context))
 return n
def ingest():
 geo=obj(GEOMS)
 floors={x["properties"]["id_sector"]:x["properties"]["estrato"] for x in geo["features"]}
 if len(floors)!=42:raise ValueError("9K no representa 42 sectores únicos")
 source={};values=defaultdict(dict);stages={};rawhash={}
 for phase,meta,field,path in SOURCES:
  man=obj(ROOT/meta);items={x["mes"]:x["sha256"] for x in man[field]}
  if len(items)!=len(man[field]) or set(items)&set(source):raise ValueError("Manifiesto meses duplicados "+phase)
  source.update(items);stages[phase]=len(items)
  src=ROOT/path;rawhash[phase]=hashfile(src)
  seen=set()
  with src.open("r",newline="",encoding="utf-8-sig") as f:
   for row in csv.DictReader(f):
    m,s=row["mes"],row["sector"]
    if m not in items or s not in floors or (m,s) in seen:
     raise ValueError("Mes/sector desconocido o repetido: "+str((m,s)))
    seen.add((m,s))
    if row["sha256_tiff"]!=items[m]:raise ValueError("Sector mes sin trazabilidad SHA "+str((m,s)))
    if row["precipitacion_promedio_pixel_mm"]!="":
     values[s][m]=numeric(row["precipitacion_promedio_pixel_mm"],(m,s))
  if len(seen)!=42*len(items):raise ValueError("Filas incompletas CHIRPS "+phase)
 if list(sorted(source))!=DAYS or stages!={"9O":108,"9P":12,"9Q":240}:
  raise ValueError("No se ha auditado la matriz mensual 360 años / fases esperadas")
 good=sorted(k for k in floors if set(values[k])==set(DAYS))
 dropped=sorted(set(floors)-set(good))
 if len(good)!=39 or dropped!=["S028","S032","S034"]:
  raise ValueError("Número o identidad de sectores CHIRPS evaluables cambió")
 document=obj(STAT9R)
 if document["grafo"]["n_nodos_con_lluvia_valida"]!=len(good):
  raise ValueError("9R reporta otro censo de nodos")
 pred=rows(PRED9R)
 max_abs_target_diff=0.0
 if len(pred)!=2340 or len({(v["mes_objetivo"],v["sector"]) for v in pred})!=2340:
  raise ValueError("Archivo 9R no tiene 60 x 39 casos únicos")
 for row in pred:
  m,s=row["mes_objetivo"],row["sector"]
  if s not in good or m not in DAYS[-60:]:
   raise ValueError("9R muestra fuera de corte")
  y=numeric(row["lluvia_observada_CHIRPS_mm"],(m,s))
  diff=abs(y-values[s][m]);max_abs_target_diff=max(max_abs_target_diff,diff)
  if diff>EPS:
   raise ValueError("Objetivo observado 9R no es CHIRPS 9Q en "+m+" "+s+" diferencia="+str(diff))
 if document["origen_CHIRPS"]["meses_verificados"]!=360:
  raise ValueError("9R no tiene procedencia 360")
 return floors,good,dropped,values,stages,rawhash,document,pred,max_abs_target_diff

def bridge():
 floors,good,dropped,values,stages,rawhash,doc,pred,max_diff=ingest()
 BASE.mkdir(parents=True,exist_ok=True)
 data=[{"sector_id":s,"mes":m,"lluvia_mm":format(values[s][m],".5f")}
       for s in good for m in DAYS]
 writecsv(BRIDGE,data,["sector_id","mes","lluvia_mm"])
 result={"fase":"9W","fecha_corte":"2026-10-17",
  "insumos_identificados":{"9O":SOURCES[0][3],"9P":SOURCES[1][3],"9Q":SOURCES[2][3]},
  "meses_CHIRPS_final_verificados":360,"anios_completos":30,
  "n_poligonos_9k":42,"n_sectores_aptos_historia_CHIRPS":len(good),
  "sectores_sin_celda_CHIRPS":dropped,"sectores_evaluables":good,
  "filas_matriz_auditada":len(data),"sha256_matriz_nueva":hashfile(BRIDGE),
  "sha256_poligonos":hashfile(GEOMS),"sha256_9R_predicciones":hashfile(PRED9R),
  "sha256_fuentes_csv":rawhash,"conteo_por_fase":stages,
  "auditoria_de_objetivos_9R":{"n_comparaciones":len(pred),
    "tolerancia_redondeo_mm":EPS,"diferencia_maxima_observada_mm":round(max_diff,7),"incongruencias":0},
  "fuente_productos":"CHIRPS v3 final retrospectivo, no mediciones SENAMHI independientes",
  "meses_bloque_train_9R":"1997-01/2015-12",
  "meses_bloque_validacion_9R":"2016-01/2020-12",
  "meses_bloque_prueba_9R":"2021-01/2025-12",
  "modelo_9R_ya_ejecutado":True,
  "notas_9S_9V_anteriores_desactualizadas":True,
  "vintage_CHIRPS_as_issued_historico_no_auditado":True,
  "no_publicar_aciertos_operacionales":True,
  "zona_homogenea_certificada":False,"alertas_activadas":False}
 MANIFEST.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("9W: matriz CHIRPS",len(data),"observaciones de",len(good),"sectores; "
       "se verificaron",len(pred),"objetivos originales 9R.")
 return result

def percentile(vals,q):
 if not vals:return None
 arr=sorted(vals);pos=q*(len(arr)-1)
 low=math.floor(pos);up=math.ceil(pos)
 return round(arr[low]+(arr[up]-arr[low])*(pos-low),5)

def metrics(items):
 if not items:return None
 errs=[x["pred"]-x["obs"] for x in items]
 return {"n":len(items),"mae_mm":round(statistics.mean(abs(x) for x in errs),5),
  "rmse_mm":round(math.sqrt(statistics.mean(x*x for x in errs)),5),
  "sesgo_mm":round(statistics.mean(errs),5)}
def boot_year(records,left,right,years):
 # Bootstrap EXACTO: 5^5 o 4^4 con años completos como clúster.
 # Cada año tiene 39 * 12 meses y todos los modelos usan las mismas observaciones.
 by=defaultdict(list)
 for r in records:
  if r["year"] in years:by[(r["model"],r["year"])].append(abs(r["pred"]-r["obs"]))
 sums={k:(sum(v),len(v)) for k,v in by.items()}
 for model in (left,right):
  if any((model,y) not in sums for y in years):raise ValueError("Faltó bloque año "+model)
 deltas=[]
 for sample in itertools.product(years,repeat=len(years)):
  loss={}
  for model in (left,right):
   total=sum(sums[(model,y)][0] for y in sample)
   count=sum(sums[(model,y)][1] for y in sample)
   loss[model]=total/count
  deltas.append(loss[left]-loss[right])
 observed=statistics.mean([sums[(left,y)][0]/sums[(left,y)][1]
                     -sums[(right,y)][0]/sums[(right,y)][1] for y in years])
 return {"comparacion":left+"_menos_"+right,
   "delta_mae_mm_positivo_es_peor":round(observed,5),
   "intervalo_bootstrap_anual_95_pct_mm":[percentile(deltas,.025),percentile(deltas,.975)],
   "fraccion_remuestras_delta_positivo":round(sum(d>0 for d in deltas)/len(deltas),5),
   "n_bloques_anio":len(years),"n_remuestras_exactas":len(deltas),
   "interpretacion":"variabilidad por AÑOS de prueba; no independencia espacial ni prueba prospectiva"}

def unpack9R(pred):
 all_=[]
 mapping={"climatologia_entrenamiento_mm":"climatologia",
          "random_forest_mm":"random_forest",
          "gcn_mm":"gcn"}
 for r in pred:
  obs=numeric(r["lluvia_observada_CHIRPS_mm"],r["sector"])
  for field,name in mapping.items():
   pred_=numeric(r[field],(field,r["mes_objetivo"]))
   all_.append({"protocol":"9R","month":r["mes_objetivo"],"year":int(r["mes_objetivo"][:4]),
    "sector":r["sector"],"floor":r["piso"],"model":name,"obs":obs,"pred":pred_})
 return all_
def unpack9T(good,values,floors):
 if not T_PRED.exists() or not T_STATUS.exists() or not U_STATUS.exists():
  raise ValueError("9T/9U aún no ejecutados sobre la matriz 9W")
 doc=obj(T_STATUS)
 if doc.get("sha256_entrada")!=hashfile(BRIDGE) or doc.get("n_sectores")!=len(good):
  raise ValueError("9T usó una matriz diferente de 9W")
 decision=obj(U_STATUS)
 if decision.get("fase")!="9U":raise ValueError("Falta criterio de decisión 9U")
 raw=rows(T_PRED)
 models={"climatologia","persistencia","random_forest"}
 seq=[]
 seen=set()
 for row in raw:
  sector,month,model=row["sector_id"],row["mes"],row["modelo"]
  if row["periodo"] not in ("validacion","prueba") or sector not in good or model not in models:
   raise ValueError("9T predictor, sector o split inesperado")
  expected="prueba" if month>="2022-01" else "validacion"
  if row["periodo"]!=expected:raise ValueError("9T etiquetas temporales incorrectas")
  key=(row["periodo"],sector,month,model)
  if key in seen:raise ValueError("9T contiene duplicados")
  seen.add(key)
  obs=numeric(row["observado_mm"],key)
  if abs(obs-values[sector][month])>EPS:raise ValueError("9T usa CHIRPS distinto del original")
  seq.append({"protocol":"9T","month":month,"year":int(month[:4]),
    "sector":sector,"floor":floors[sector],"model":model,"obs":obs,
    "pred":numeric(row["predicho_mm"],key)})
 test=[r for r in seq if r["year"]>=2022]
 if len(test)!=len(good)*48*3:
  raise ValueError("Conjunto de prueba 9T no cubre 48 x 39 x 3")
 for model in models:
  keys={(x["month"],x["sector"]) for x in test if x["model"]==model}
  if len(keys)!=len(good)*48:raise ValueError("Sectores/meses 9T distintos")
 return test,decision,doc

def report():
 floors,good,dropped,values,stages,rawhash,doc,pred=ingest()
 if not MANIFEST.exists() or obj(MANIFEST)["sha256_matriz_nueva"]!=hashfile(BRIDGE):
  raise ValueError("9W debe construir y archivar matriz antes de evaluar")
 a=unpack9R(pred)
 b,decision,man9T=unpack9T(good,values,floors)
 panels=[]
 byfloor=[]
 byyear=[]
 for protocol,records,years in (("9R",a,[2021,2022,2023,2024,2025]),
                                 ("9R_2022_2025",[x for x in a if x["year"]>=2022],[2022,2023,2024,2025]),
                                 ("9T",b,[2022,2023,2024,2025])):
  model_names=sorted({x["model"] for x in records})
  mm={m:metrics([r for r in records if r["model"]==m]) for m in model_names}
  baseline=mm["climatologia"]["mae_mm"]
  deltas={}
  for left,right in (("random_forest","climatologia"),("gcn","climatologia"),
                     ("gcn","random_forest"),("persistencia","climatologia")):
   if left in mm and right in mm:deltas[left+"_menos_"+right]=boot_year(records,left,right,years)
  skill={m:round(100*(1-mm[m]["mae_mm"]/baseline),4) for m in model_names}
  for floor in sorted(set(floors[x] for x in good)):
   members=[r for r in records if r["floor"]==floor]
   ref=metrics([r for r in members if r["model"]=="climatologia"])["mae_mm"]
   for model in model_names:
    subset=[r for r in members if r["model"]==model]
    cur=metrics(subset)
    byfloor.append({"protocolo":protocol,"piso":floor,"modelo":model,
      "n":cur["n"],"mae_mm":cur["mae_mm"],"rmse_mm":cur["rmse_mm"],
      "skill_vs_climatologia_pct":round(100*(1-cur["mae_mm"]/ref),4) if ref else ""})
  for year in years:
   for model in model_names:
    subset=[r for r in records if r["year"]==year and r["model"]==model]
    cur=metrics(subset)
    byyear.append({"protocolo":protocol,"anio":year,"modelo":model,
       "n":cur["n"],"mae_mm":cur["mae_mm"],"rmse_mm":cur["rmse_mm"],
       "sesgo_mm":cur["sesgo_mm"]})
  panels.append({"protocolo":protocol,"anios_prueba":years,
    "n_sectores":len(good),
    "casos_sector_mes_por_modelo":len([r for r in records if r["model"]=="climatologia"]),
    "metrica_modelos":mm,"skill_MAE_vs_climatologia_pct":skill,
    "comparacion_errores_emparejados":deltas,
    "ganador_por_mae_incluyendo_baselines":min(mm,key=lambda m:mm[m]["mae_mm"])})
 result={"fase":"9W","fecha_corte":"2026-10-17",
  "mensaje":"9R YA TENÍA entrenamiento real GCN/RF; 9S-9V son documentos metodológicos obsoletos respecto a ello",
  "auditoria_matriz_9q_sectorial":obj(MANIFEST),
  "modelos_y_pruebas":panels,
  "decision_9U_reproducida_en_protocolo_9T":decision,
  "comparar_mae_9R_vs_9T_para_elegir_modelo":False,
  "razon_no_intercambiabilidad":"Particiones de entrenamiento y validación DIFERENTES, hiperparámetros y entrenamiento distintos, aunque se repitan 2022–2025; no comparar como torneo pareado 9R vs 9T",
  "n_estaciones_independientes_SENAMHI_validadas":0,
  "validacion_espacial_con_sectores_ausentes_en_entrenamiento":False,
  "GCN_de_9R_arquitectura_de_grafos_no_CNN_convolucion_2D":True,
  "producto_CHIRPS_version_final_historica_revisada":True,
  "verificacion_as_issued_de_variables_rezagadas":False,
  "modelo_operativo_habilitado":False,
  "n_zonas_climaticamente_homogeneas_certificadas":0,
  "alertas_fitosanitarias_emitidas":False,
  "limitaciones":[
    "Los sectores test estuvieron presentes en el entrenamiento 9R y 9T: hay prueba temporal, NO prueba de transferencia espacial a sectores nuevos.",
    "Los 5 años de prueba 9R o 4 de 9T son clústeres temporales; 39x60 no son 2340 observaciones independientes.",
    "La reestimación con otro corte 9T es control de robustez, no un nuevo ensayo independiente por compartir años 2022–2025.",
    "Climatología 9R y 9T cambia porque se estima sobre tramos temporales diferentes: no comparar MAE directo entre protocolos para declarar ganador.",
    "CHIRPS v3 final y geometrías 9K fueron compiladas en 2026 a posteriori: rezagos no certificados como disponibles en la fecha histórica de emisión.",
    "No se evaluó ninguna CNN 2D convencional: 9R utilizó GCN convolucional sobre grafo.",
    "Los modelos no se validaron sobre estaciones pluviométricas SENAMHI independientes ni eventos fitosanitarios reales." ]}
 BASE.mkdir(parents=True,exist_ok=True)
 EVIDENCE.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 writecsv(FLOOR,byfloor,["protocolo","piso","modelo","n","mae_mm","rmse_mm","skill_vs_climatologia_pct"])
 writecsv(YEAR,byyear,["protocolo","anio","modelo","n","mae_mm","rmse_mm","sesgo_mm"])
 print("9W: 9R 2021-25,",len(good),"sectores, 9T 2022-25; "+
       "límites del bootstrap anual y pisos auditados.")
 return result

def check():
 floors,good,dropped,values,stages,sha,doc,pred,max_diff=ingest()
 st=obj(MANIFEST)
 if hashfile(BRIDGE)!=st["sha256_matriz_nueva"]:raise ValueError("SHA matriz 9W cambiado")
 if len(rows(BRIDGE))!=39*360:raise ValueError("Matriz incompleta")
 if obj(EVIDENCE)!=report():raise ValueError("Estado 9W no reproducible")
 return True

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--bridge",action="store_true")
 p.add_argument("--evaluate",action="store_true")
 p.add_argument("--check",action="store_true")
 a=p.parse_args()
 if a.bridge:bridge()
 elif a.evaluate:report()
 elif a.check:check()
 else:raise SystemExit("Especificar --bridge o --evaluate o --check")
