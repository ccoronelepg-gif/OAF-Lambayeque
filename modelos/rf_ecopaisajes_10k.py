#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10K — RF precipitation by operational eco-climatic landscapes.

A map of ecological LANDSCAPES is NOT the official MINAM ecoregion polygons.
Three 9K sectors without complete CHIRPS are excluded; polygons exploratory.
Five spatial blocks, train 1997-15, tune weights 2016-18, calibrate 2019-20,
evaluate 2021-25, strictly retrospective (not as-issued / live forecasts).
Includes controlled RF with 5-group landform one-hot + region, only rainfall
or verified rainfall+ocean+NASA inputs. Against frozen 10J and climatology.

No pathogen/disease model is fitted or inferred by this program.
"""
from __future__ import annotations
import csv,json,hashlib,math,collections
from pathlib import Path
import numpy as np
import probabilidad_39_sectores_10f as base
import random_forest_lluvia_multivariable_10i as previous
import rf_lluvia_extremos_10j as rf
from shapely.geometry import shape

ROOT=Path(__file__).resolve().parents[1]
SOURCE_GEO=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
AUDIT=ROOT/"datos/validacion_9w/auditoria_puente_9w.json"
SOURCE_10J=rf.PRED
OUT=ROOT/"datos/ecopaisajes_10k"
ECO=OUT/"paisajes_ecoclimaticos_10k.geojson"
SUMMARY=OUT/"evaluacion_ecoclimatica_10k.json"
SERIES=OUT/"series_sector_mes_10k.json"
PRED=OUT/"predicciones_ecopaisajes_10k.csv"
CATEGORIES={
 "costa_valle":{"nombre":"Costa árida y valles bajos","pisos":["cota_negativa_revisar","llanura_costa","valle_bajo"],"color":"#d8a94a","orden":1,"referencia":"Transición litoral y valles costeros; NO polígono oficial de desierto del Pacífico"},
 "piedemonte":{"nombre":"Piedemonte y transición de bosque seco","pisos":["piedemonte"],"color":"#8da852","orden":2,"referencia":"Afinidad ecológica aproximada con bosque seco ecuatorial, pendiente de intersección oficial"},
 "ladera_baja":{"nombre":"Vertientes andinas bajas","pisos":["montana_baja"],"color":"#4a9b7c","orden":3,"referencia":"Estrato altitudinal 9K; NO mapa certificado de serranía esteparia"},
 "ladera_media":{"nombre":"Vertientes andinas medias","pisos":["montana_media"],"color":"#5383af","orden":4,"referencia":"Estrato altitudinal exploratorio 9K, no ecorregión oficial"},
 "cumbres":{"nombre":"Alturas y cumbres andinas","pisos":["montana_alta"],"color":"#8d83b0","orden":5,"referencia":"Alta montaña exploratoria; no afirmar páramo/puna sin cartografía MINAM"}
}
ARM_NAMES=("lluvia_ecopaisaje","lluvia_oceano_atmosfera_ecopaisaje")
FIELD_NAMES=("mes","sector","estrato","paisaje","bloque","brazo_rf",
  "observado_mm","estimado_rf_mm","climatologia_mm","prob_rf_p90","prob_ref_p90",
  "prob_rf_p95","prob_ref_p95","evento_p90","evento_p95",
  "umbral_p90_mm","umbral_p95_mm","limite_inf_90_mm","limite_sup_90_mm")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gread(path):return json.loads(path.read_text(encoding="utf8"))
def readcsv(path):
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def catalog():
 eco=gread(SOURCE_GEO);a=gread(AUDIT)
 if eco["metadata"].get("limite_regional_oficial") is not False:raise ValueError("Source must be exploratory")
 valid=set(a["sectores_evaluables"])
 by_floor={floor:key for key,val in CATEGORIES.items() for floor in val["pisos"]}
 features=[];lookup={};floor_data={}
 for f in eco["features"]:
  prop=f["properties"];sector=prop["id_sector"];floor=prop["estrato"]
  if floor not in by_floor:raise ValueError("Unknown altitude floor "+str(floor))
  if sector not in valid:continue
  if sector in lookup or not shape(f["geometry"]).is_valid:raise ValueError("Duplicate/invalid geography")
  group=by_floor[floor]
  feat={"type":"Feature","geometry":f["geometry"],"properties":{
    "sector":sector,"paisaje_id":group,"paisaje_nombre":CATEGORIES[group]["nombre"],
    "estrato":floor,"alt_min_m":prop.get("alt_min_nodos_m"),"alt_max_m":prop.get("alt_max_nodos_m"),
    "cota_negativa_pendiente":bool(prop.get("alt_min_nodos_m",0)<0),
    "cobertura_CHIRPS_1996_2025":True,
    "categoria_ecologica_oficial":False,
    "limite_sectorial_oficial":False}}
  features.append(feat);lookup[sector]=group;floor_data[sector]=floor
 features.sort(key=lambda x:x["properties"]["sector"])
 if len(features)!=39 or set(lookup)!=valid:raise ValueError("39 evaluated eco polygons required")
 for cat in CATEGORIES:
  if cat not in lookup.values():raise ValueError("Empty ecological landscape "+cat)
 return {"type":"FeatureCollection","name":"OAF 10K paisajes ecoclimaticos PROVISIONALES",
    "metadata":{"fase":"10K","proyeccion":"EPSG:4326","fuente_geometria":"9K exploratoria",
      "es_mapa_oficial_MINAM":False,"n_sectores_con_CHIRPS":39,"n_poligonos_originales":42,
      "poligonos_descartados_sin_CHIRPS":a["sectores_sin_celda_CHIRPS"],
      "referencia_conceptual_MINAM":"https://www.gob.pe/institucion/minam/informes-publicaciones/277146-mapa-nacional-de-ecosistemas-del-peru",
      "advertencia":"NO ecorregiones oficiales ni limites de ecosistemas MINAM; agrupa pisos experimentales por paisaje."},
    "features":features},lookup,floor_data
def ones(nodes,lookup):
 names=list(CATEGORIES)
 return np.asarray([[1.0 if lookup[sid]==key else 0.0 for key in names] for sid in nodes],dtype=np.float32)
def append_eco(x,nodes,lookup):
 extra=ones(nodes,lookup)
 if len(x.shape)!=3 or x.shape[1]!=len(nodes):raise ValueError("Bad eco feature matrix")
 n=len(x)
 return np.concatenate((x,np.broadcast_to(extra[None,:,:],(n,len(nodes),len(CATEGORIES)))),axis=2)
def stats(rows):
 if not rows:return None
 obs=np.array([float(r["observado_mm"]) for r in rows])
 pred=np.array([float(r["estimado_rf_mm"]) for r in rows])
 clim=np.array([float(r["climatologia_mm"]) for r in rows])
 p90=np.array([float(r["prob_rf_p90"]) for r in rows]);c90=np.array([float(r["prob_ref_p90"]) for r in rows])
 p95=np.array([float(r["prob_rf_p95"]) for r in rows]);c95=np.array([float(r["prob_ref_p95"]) for r in rows])
 y90=np.array([int(r["evento_p90"]) for r in rows]);y95=np.array([int(r["evento_p95"]) for r in rows])
 lo=np.array([float(r["limite_inf_90_mm"]) for r in rows]);hi=np.array([float(r["limite_sup_90_mm"]) for r in rows])
 return {"n":len(rows),"n_sectores":len({r["sector"] for r in rows}),
  "lluvia_observada_media_mm":round(float(np.mean(obs)),3),
  "lluvia_rf_media_mm":round(float(np.mean(pred)),3),
  "lluvia_climatologia_media_mm":round(float(np.mean(clim)),3),
  "mae_rf_mm":round(float(np.mean(np.abs(obs-pred))),4),
  "mae_climatologia_mm":round(float(np.mean(np.abs(obs-clim))),4),
  "sesgo_rf_mm":round(float(np.mean(pred-obs)),4),
  "brier_rf_p90":round(float(np.mean((p90-y90)**2)),6),
  "brier_climatologia_p90":round(float(np.mean((c90-y90)**2)),6),
  "brier_rf_p95":round(float(np.mean((p95-y95)**2)),6),
  "brier_climatologia_p95":round(float(np.mean((c95-y95)**2)),6),
  "n_eventos_p90":int(y90.sum()),"n_eventos_p95":int(y95.sum()),
  "cobertura_intervalo_90_pct":round(float(np.mean((obs>=lo)&(obs<=hi))*100),2),
  "limite_incertidumbre":"Intervalo empírico NO garantizado, 2019-20, sensible a 2023"}
def aggregate(rows,fn):
 sets=collections.defaultdict(list)
 for r in rows:sets[fn(r)].append(r)
 return {str(k):stats(v) for k,v in sorted(sets.items(),key=lambda x:str(x[0]))}
def train():
 polygons,lookup,floors=catalog()
 nodes,A,edges,fixed,old_floors,poly,data,_=base.previous.inputs()
 if set(nodes)!=set(lookup):raise ValueError("Sector inventory mismatch")
 cells=base.previous.raster_cells(nodes,poly)
 folds=base.previous.folds(nodes,poly,cells)
 X0,X1,Y90,raw,t90,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 arms,atm=previous.arm_inputs(nodes,X0,X1,dates)
 feature={"lluvia_ecopaisaje":append_eco(arms["lluvia"],nodes,lookup),
          "lluvia_oceano_atmosfera_ecopaisaje":append_eco(arms["lluvia_oceano_atmosfera"],nodes,lookup)}
 t95=np.quantile(raw[tr],.95,axis=0)
 y95=(raw>=t95[None,:]).astype(np.float32)
 ref_mm=rf.normal(raw,tr,dates)
 ref90=rf.frequencies(Y90,tr,dates)
 ref95=rf.frequencies(y95,tr,dates)
 rows=[];meta=[];valid={}
 for fold,held_names in sorted(folds.items()):
  i_train=[i for i,s in enumerate(nodes) if s not in held_names]
  i_hold=[i for i,s in enumerate(nodes) if s in held_names]
  _,atr=base.previous.subgraph(A,i_train)
  _,aho=base.previous.subgraph(A,i_hold)
  valid[str(fold)]={}
  for arm,values in feature.items():
   xtr=base.enrich(values[:,i_train,:],atr)
   xho=base.enrich(values[:,i_hold,:],aho)
   residual,mm_info=rf.rf_mm(xtr,raw[:,i_train],tr,va,fold,ref_mm[:,i_train],xho)
   pp90,p90_info=rf.rf_event(xtr,Y90[:,i_train],tr,va,fold,ref90[:,i_train],xho)
   pp95,p95_info=rf.rf_event(xtr,y95[:,i_train],tr,va,fold,ref95[:,i_train],xho)
   mu=ref_mm[:,i_hold]
   estimate=rf.bias_correct_clipped(mu,residual,mm_info["blend_weight"])
   p90=rf.blend_probability(ref90[:,i_hold],pp90,p90_info["blend_weight"])
   p95=rf.blend_probability(ref95[:,i_hold],pp95,p95_info["blend_weight"])
   radius=rf.finite_interval(raw[ca][:,i_hold]-estimate[ca])
   low=np.maximum(0,estimate-radius);high=estimate+radius
   valid[str(fold)][arm]={"mm":mm_info["validacion"]["validation_score"],
                          "p90":p90_info["validacion"]["validation_score"],
                          "p95":p95_info["validacion"]["validation_score"]}
   meta.append({"fold":fold,"arm":arm,"n_held":len(i_hold),
      "mm":{"leaf":mm_info["min_samples_leaf"],"weight":mm_info["blend_weight"]},
      "p90":{"leaf":p90_info["min_samples_leaf"],"weight":p90_info["blend_weight"]},
      "p95":{"leaf":p95_info["min_samples_leaf"],"weight":p95_info["blend_weight"]},
      "calibration_90_radius_mm":round(radius,4)})
   for ti,month in enumerate(dates):
    if not te[ti]:continue
    for j,idx in enumerate(i_hold):
     sid=nodes[idx]
     row={"mes":str(month),"sector":sid,"estrato":floors[sid],"paisaje":lookup[sid],
       "bloque":str(fold),"brazo_rf":arm,
       "observado_mm":round(float(raw[ti,idx]),5),
       "estimado_rf_mm":round(float(estimate[ti,j]),5),
       "climatologia_mm":round(float(mu[ti,j]),5),
       "prob_rf_p90":round(float(p90[ti,j]),7),"prob_ref_p90":round(float(ref90[ti,idx]),7),
       "prob_rf_p95":round(float(p95[ti,j]),7),"prob_ref_p95":round(float(ref95[ti,idx]),7),
       "evento_p90":int(Y90[ti,idx]),"evento_p95":int(y95[ti,idx]),
       "umbral_p90_mm":round(float(t90[idx]),5),"umbral_p95_mm":round(float(t95[idx]),5),
       "limite_inf_90_mm":round(float(low[ti,j]),5),"limite_sup_90_mm":round(float(high[ti,j]),5)}
     if any(not math.isfinite(float(row[k])) for k in ("estimado_rf_mm","prob_rf_p90","prob_rf_p95")):raise ValueError("NaN in rain predictions")
     rows.append(row)
   print("10K_RF",fold,arm,"hold",len(i_hold),"weight_mm",mm_info["blend_weight"],"radius",round(radius,2),flush=True)
 if len(rows)!=4680:raise ValueError("Expected 39 sectors * 60 months * 2 eco models")
 rows.sort(key=lambda r:(r["mes"],r["sector"],r["brazo_rf"]))
 chosen={}
 for metric in ("mm","p90","p95"):
  chosen[metric]={fold:min(ARM_NAMES,key=lambda a:(valid[fold][a][metric],list(ARM_NAMES).index(a))) for fold in valid}
 by_arm={arm:[r for r in rows if r["brazo_rf"]==arm] for arm in ARM_NAMES}
 selected={metric:[r for r in rows if r["brazo_rf"]==chosen[metric][r["bloque"]]] for metric in chosen}
 if any(len(value)!=2340 for value in selected.values()):raise ValueError("Selection did not preserve 39*60")
 OUT.mkdir(parents=True,exist_ok=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=FIELD_NAMES);w.writeheader();w.writerows(rows)
 ECO.write_text(json.dumps(polygons,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 # Baseline 10J cross-check on a distinct model; only exact same observation keys.
 old=readcsv(SOURCE_10J);old_by={(r["sector"],r["mes"],r["familia_rf"]):r for r in old}
 if len(old_by)!=9360:raise ValueError("Missing 10J baseline complete")
 for row in selected["mm"]:
  ref=old_by[(row["sector"],row["mes"],"lluvia")]
  if abs(float(ref["lluvia_observada_mm"])-float(row["observado_mm"]))>.001:
   raise ValueError("10J/10K test rain mismatch")
 # chosen at mm objective for map; do NOT use P90/P95 rows from another arm when graphing
 historical=selected["mm"]
 slim=[{"mes":r["mes"],"sector":r["sector"],"paisaje":r["paisaje"],"estrato":r["estrato"],
    "observado_mm":r["observado_mm"],"rf_mm":r["estimado_rf_mm"],
    "climatologia_mm":r["climatologia_mm"],"p90":r["prob_rf_p90"],"p95":r["prob_rf_p95"],
    "ref_p90":r["prob_ref_p90"],"ref_p95":r["prob_ref_p95"],
    "umbral_p90_mm":r["umbral_p90_mm"],"umbral_p95_mm":r["umbral_p95_mm"],
    "lo_mm":r["limite_inf_90_mm"],"hi_mm":r["limite_sup_90_mm"],
    "e90":r["evento_p90"],"e95":r["evento_p95"],"brazo":r["brazo_rf"]}
    for r in historical]
 SERIES.write_text(json.dumps({"fase":"10K","objetivo":"Reconstrucciones retrospectivas NO pronosticos actuales",
    "fecha_evaluacion":"2021-2025","seleccion_solo_validacion_2016_2018":True,
    "datos":slim},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 summary={
  "fase":"10K","nombre":"Paisajes ecoclimáticos OAF — modelos experimentales de precipitación",
  "objetivos":["lluvia_mensual_mm","probabilidad_lluvia_alta_P90","probabilidad_lluvia_excepcional_P95"],
  "ecorregiones_oficiales_intersectadas":False,
  "metodologia_paisajes":"Agrupación proxy de estratos altitudinales 9K; NO ecorregiones/minam oficiales",
  "fuentes_ecorregiones_referencia":["https://www.gob.pe/institucion/minam/informes-publicaciones/277146-mapa-nacional-de-ecosistemas-del-peru",
    "https://sinia.minam.gob.pe/mapas/mapa-nacional-ecosistemas-peru"],
  "paisajes":{k:{**v,"n_sectores":sum(lookup[s]==k for s in nodes),
    "sectores":[s for s in nodes if lookup[s]==k]} for k,v in CATEGORIES.items()},
  "n_sector_mes":2340,"n_predicciones":len(rows),"n_sectores":len(nodes),"n_paisajes":5,
  "ventanas":{"train":"1997-2015","validacion_seleccion":"2016-2018","intervalo":"2019-2020","test":"2021-2025"},
  "validacion_por_bloque":valid,"seleccion_por_validacion":chosen,
  "resultados_familias":{arm:{"global":stats(by_arm[arm]),
    "por_paisaje":aggregate(by_arm[arm],lambda r:r["paisaje"]),
    "por_estrato":aggregate(by_arm[arm],lambda r:r["estrato"])} for arm in ARM_NAMES},
  "resultado_selector_mm":{"global":stats(historical),
    "por_paisaje":aggregate(historical,lambda r:r["paisaje"]),
    "por_paisaje_2023":aggregate([r for r in historical if r["mes"].startswith("2023")],lambda r:r["paisaje"]),
    "por_estrato":aggregate(historical,lambda r:r["estrato"]),
    "por_anio":aggregate(historical,lambda r:r["mes"][:4]),
    "por_sector":aggregate(historical,lambda r:r["sector"]),
    "por_sector_2023":aggregate([r for r in historical if r["mes"].startswith("2023")],lambda r:r["sector"])},
  "resultados_selectores_p90_p95":{
    k:{"global":stats(selected[k]),"por_paisaje":aggregate(selected[k],lambda r:r["paisaje"])}
    for k in ("p90","p95")},
  "referencia_10j_familia_lluvia":{"global":rf.scoring([{
    "lluvia_observada_mm":r["lluvia_observada_mm"],
    "lluvia_predicha_rf_mm":r["lluvia_predicha_rf_mm"],
    "lluvia_climatologia_mm":r["lluvia_climatologia_mm"],
    "probabilidad_rf_p90":r["probabilidad_rf_p90"],
    "probabilidad_base_p90":r["probabilidad_base_p90"],
    "probabilidad_rf_p95":r["probabilidad_rf_p95"],
    "probabilidad_base_p95":r["probabilidad_base_p95"],
    "evento_p90_observado":r["evento_p90_observado"],
    "evento_p95_observado":r["evento_p95_observado"],
    "limite_inferior_90_mm":r["limite_inferior_90_mm"],
    "limite_superior_90_mm":r["limite_superior_90_mm"]}
    for r in old if r["familia_rf"]=="lluvia"])},
  "hiperparametros":meta,
  "sha256":{"predicciones_10k":sha(PRED),"mapa_10k":sha(ECO),"serie_visores_10k":sha(SERIES),
    "geom_9k":sha(SOURCE_GEO),"modelo_previo_10j_predicciones":sha(SOURCE_10J)},
  "unidad_promedios":"Promedios simples por sector-mes, NO ponderados por hectárea ni estación instrumental",
  "controles_operativos":{"evaluacion_as_issued":False,"modelos_validados_estaciones_independientes":False,
    "pronostico_en_tiempo_real_habilitado":False,"prediccion_de_enfermedades":False,
    "ecorregiones_MINAM_homologadas":False},
  "limitaciones":["Geometría de sectores 9K experimental y 3 sectores sin datos CHIRPS descartados.",
    "Clases de paisajes basadas en pisos no equivalen a ecorregiones cartográficas oficiales.",
    "Pocos sectores de montaña alta; muestras de sector-mes están correlacionadas.",
    "Los cinco folds CHIRPS aún comparten algunas celdas NASA de covariables.",
    "Seleccionar la mejor familia usando 2021–2025 sesga prueba; solo 2016–2018 para selección.",
    "CHIRPS FINAL, NOAA y NASA se obtuvieron ex post, no existe verificación as-issued.",
    "Pronóstico de precipitación mensual no equivale a lluvia intensa horaria ni evento ENSO.",
    "Entrenamiento de enfermedades quedará para etapa futura con datos de campo."]}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10K_FIN",json.dumps({"n_paisajes":5,"n_territorial":len(nodes),
   "seleccion":chosen,"global":summary["resultado_selector_mm"]["global"],
   "10J_ref":summary["referencia_10j_familia_lluvia"]["global"]},ensure_ascii=False),flush=True)
def verify():
 obj=gread(SUMMARY);geo=gread(ECO);series=gread(SERIES)
 with PRED.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
 if obj["fase"]!="10K" or len(rows)!=4680 or len(series["datos"])!=2340:raise ValueError("Not fully calculated")
 if obj["sha256"]["predicciones_10k"]!=sha(PRED) or obj["sha256"]["mapa_10k"]!=sha(ECO):raise ValueError("Hashes differ")
 if len(geo["features"])!=39 or obj["controles_operativos"]["pronostico_en_tiempo_real_habilitado"]:raise ValueError("Invalid map or status")
 print("10K_VERIFICADO",obj["resultado_selector_mm"]["global"])
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");arg=p.parse_args()
 verify() if arg.check else train()
