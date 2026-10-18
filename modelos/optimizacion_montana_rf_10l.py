#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10L mountain-specific Random Forest for monthly CHIRPS rain ONLY.

Highland strata are *exploratory*, not official MINAM ecoregions. A fair
comparison uses same 39-sector/60-month test as 10K; NO 2021-25 selection.
Train 1997-2015, tune only 2016-2018 among training-sector samples,
calibrate 2019-2020 on holdout, evaluate 2021-2025 retrospectively.
If a regional RF correction does not improve validation MAE, set weight 0
(fall back to site climatology). No diseases, hourly storm warnings, ENSO
event classifier, or deployment to public now.
"""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import probabilidad_39_sectores_10f as base
import random_forest_lluvia_multivariable_10i as multi
import rf_lluvia_extremos_10j as rain
import rf_ecopaisajes_10k as eco

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"datos/montanas_10l"
PRED=OUT/"predicciones_lluvia_montanas_10l.csv"
REPORT=OUT/"evaluacion_montanas_10l.json"
MAP=OUT/"sectores_mejora_montana_10l.geojson"
SERIES=OUT/"series_montana_10l.json"
TARGET=("ladera_media","cumbres")
OPTIONS=("global_rain_normalized","global_rain_log",
 "especialista_normalized","especialista_log",
 "global_full_normalized","global_full_log")
BLEND=(0.,.2,.4,.6,.8,1.)
FIELD=("mes","sector","paisaje","estrato","bloque","observado_mm",
 "nuevo_rf_mm","rf_10k_mm","climatologia_mm","intervalo_inf_90_mm",
 "intervalo_sup_90_mm","rf_p90_10k","rf_p95_10k",
 "evento_p90","evento_p95","opcion_validacion","peso_rf_validacion")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):
 with path.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def load(path):return json.loads(path.read_text("utf8"))
def alt_features(nodes,geometry,reference,rain,train,dates):
 """Only static 9K altitude/topology and 1997-2015 precipitation normals."""
 props={f["properties"]["sector"]:f["properties"] for f in geometry["features"]}
 n=len(nodes)
 alt=np.array([(props[s]["alt_min_m"]+props[s]["alt_max_m"])/2 for s in nodes],np.float32)
 gradient=np.array([max(0,props[s]["alt_max_m"]-props[s]["alt_min_m"]) for s in nodes],np.float32)
 # Month/site climatological SD and calendar-specific normal, both train only.
 months=np.array([int(k[-2:]) for k in dates])
 dispersion=np.empty_like(reference)
 for month in range(1,13):
  historical=train&(months==month)
  dispersion[months==month,:]=rain[historical].std(axis=0)
 longterm=rain[train].mean(axis=0)
 return np.stack((reference/100,dispersion/100,
   np.broadcast_to(alt[None,:]/4000,reference.shape),
   np.broadcast_to(gradient[None,:]/2500,reference.shape),
   np.broadcast_to(longterm[None,:]/100,reference.shape)),axis=-1).astype("float32")
def build_arms(xrain,xfull,clim,nodes,geo,raw,train,dates,lookup):
 static=alt_features(nodes,geo,clim,raw,train,dates)
 baseEco=eco.append_eco(xrain,nodes,lookup)
 fullEco=eco.append_eco(xfull,nodes,lookup)
 return {"rain":np.concatenate((baseEco,static),axis=-1),
         "full":np.concatenate((fullEco,static),axis=-1)}
def predict(clim,model_output,variant,weight):
 if variant=="log":
  # Guard log-ratio corrections against runaway extrapolation in severe rain.
  return np.maximum(0,np.expm1(np.clip(np.log1p(clim)+weight*np.clip(model_output,-3,3),0,np.log1p(3000))))
 return np.maximum(0,clim+weight*np.clip(model_output,-2,7)*(20+clim))
def target_values(raw,clim,variant):
 if variant=="log":return np.clip(np.log1p(raw)-np.log1p(clim),-3,3)
 return np.clip((raw-clim)/(20+clim),-2,7)
def sel_mae(observed,clim,raw_output,variant,mask):
 if int(mask.sum())<6:raise ValueError("Not enough highland validation")
 errors=[]
 for weight in BLEND:
  p=predict(clim[mask],raw_output[mask],variant,weight)
  errors.append((float(np.mean(np.abs(observed[mask]-p))),weight))
 score,weight=min(errors,key=lambda t:(t[0],t[1]))
 return score,weight
def train_one(X,raw,clim,selected_sites,tr,va,fold,option,clim_hold,Xhold,high_flags,wet):
 """Train-site mask and train-date mask do not include any test/holdout labels."""
 specialist=option.startswith("especialista")
 variant="log" if option.endswith("_log") else "normalized"
 if specialist:
  sites=[i for i,yes in enumerate(high_flags) if yes]
 else:sites=list(range(X.shape[1]))
 if not sites:raise ValueError("No mountain training sites")
 xtrain=X[:,sites,:]
 target=target_values(raw[:,sites],clim[:,sites],variant)
 weights=np.ones_like(target)
 if not specialist:
  weights[:,np.asarray(high_flags,dtype=bool)] *= 4
 # Rainy-month adjustment from known month, not from future observations.
 weights[tr & wet,:]*=1.5
 weights=np.broadcast_to(weights[tr],target[tr].shape)
 mdl=RandomForestRegressor(n_estimators=120,min_samples_leaf=10,
  max_depth=12,max_features=.85,bootstrap=True,random_state=20261017+fold,n_jobs=2)
 mdl.fit(xtrain[tr].reshape(-1,xtrain.shape[-1]),
  target[tr].reshape(-1),sample_weight=weights.reshape(-1))
 all_val=mdl.predict(X.reshape(-1,X.shape[-1])).reshape(X.shape[:2])
 hold=mdl.predict(Xhold.reshape(-1,Xhold.shape[-1])).reshape(Xhold.shape[:2])
 return variant,all_val,hold,{"n_train_sites":len(sites),"specialist":specialist,"n_train_records":int(tr.sum()*len(sites))}
def targeted_evaluation():
 geo,lookup,floors=eco.catalog()
 nodes,A,edges,fixed,oldfloors,polygon,data,source=base.previous.inputs()
 if set(nodes)!=set(lookup):raise ValueError("Geographic inventory incompatible with 10K")
 masks=base.previous.folds(nodes,polygon,base.previous.raster_cells(nodes,polygon))
 X0,X1,Y,raw,thr,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 arms,atm=multi.arm_inputs(nodes,X0,X1,dates)
 ref=rain.normal(raw,tr,dates)
 full=build_arms(arms["lluvia"],arms["lluvia_oceano_atmosfera"],ref,nodes,geo,raw,tr,dates,lookup)
 old=read(eco.PRED)
 oldrows={(r["mes"],r["sector"]):r for r in old if r["brazo_rf"]=="lluvia_ecopaisaje"}
 if len(oldrows)!=2340:raise ValueError("Missing frozen 10K comparator")
 result=[];decisions=[]
 for fold,held_names in sorted(masks.items()):
  ix=[j for j,s in enumerate(nodes) if s not in held_names]
  ho=[j for j,s in enumerate(nodes) if s in held_names]
  _,Atrain=base.previous.subgraph(A,ix)
  _,Ahold=base.previous.subgraph(A,ho)
  high_train=np.array([lookup[nodes[j]] in TARGET for j in ix],bool)
  wet=np.array([int(k[-2:]) in (11,12,1,2,3,4) for k in dates],bool)
  alternatives={}
  for arm in ("rain","full"):
   xtr=base.enrich(full[arm][:,ix,:],Atrain)
   xho=base.enrich(full[arm][:,ho,:],Ahold)
   for spec in ("global","especialista"):
    for var in ("normalized","log"):
     # Only rainfall highland experts; avoid fitting tiny specialists with full coast signals.
     if spec=="especialista" and arm=="full":continue
     name=(spec+"_rain_" if spec=="global" and arm=="rain" else
           "global_full_" if spec=="global" else "especialista_")+var
     if name not in OPTIONS:raise ValueError("Unexpected candidate "+name)
     variant,model_val,model_hold,meta=train_one(xtr,raw[:,ix],ref[:,ix],None,tr,va,fold,
       name,ref[:,ho],xho,high_train,wet)
     alternatives[name]=(variant,model_val,model_hold,meta)
  for landscape in TARGET:
   training_sites=[i for i,j in enumerate(ix) if lookup[nodes[j]]==landscape]
   held_sites=[i for i,j in enumerate(ho) if lookup[nodes[j]]==landscape]
   # All three high-mountain sectors can fall into the same spatial fold.
   # Without ANY independent high-mountain training sites, default to
   # historical climatology; no terrain transfer is claimed to be validated.
   high_alt_without_training=bool(not training_sites and held_sites)
   if high_alt_without_training:
    training_sites=[i for i,j in enumerate(ix) if lookup[nodes[j]]=="ladera_media"]
    if not training_sites:raise ValueError("No middle-altitude analogues to audit")
   if not training_sites:continue
   pairs=[]
   for name,(variant,train_pred,hold_pred,meta) in alternatives.items():
    mask=np.zeros_like(raw[:,ix],bool)
    mask[np.ix_(va,training_sites)]=True
    value,w=sel_mae(raw[:,ix],ref[:,ix],train_pred,variant,mask)
    # Prefer a no-correction competitor over RF if tuning has no evidence.
    pairs.append((value,name,w))
   baseline_mae=float(np.mean(np.abs(raw[va][:,ix][:,training_sites]-ref[va][:,ix][:,training_sites])))
   options=[(baseline_mae,"climatologia",0.)]+([] if high_alt_without_training else pairs)
   validation,name,weight=min(options,key=lambda v:(v[0],v[2],v[1]))
   if name=="climatologia" or weight==0:
    chosen_pred=ref[:,ho]
    mode="climatologia"
    weight=0.
   else:
    variant,_,pr,metadata=alternatives[name]
    chosen_pred=predict(ref[:,ho],pr,variant,weight)
    mode=name
   # Calibration only on 2019-20, held-out sectors of the same terrain band.
   radius=rain.finite_interval(raw[ca][:,ho][:,held_sites]-chosen_pred[ca][:,held_sites]) if held_sites else None
   decisions.append({"fold":fold,"paisaje":landscape,"n_train_sites":len(training_sites),
     "n_hold_sites":len(held_sites),"sin_sector_alto_independiente":high_alt_without_training,
     "validacion_grupo":("ladera_media_solo_diagnostico_no_transferible" if high_alt_without_training else landscape),
     "validation_mae_mm":round(validation,5),
     "baseline_validation_mae_mm":round(baseline_mae,5),"chosen_arm":mode,
     "chosen_weight":weight,"interval_90_cal_radius_mm":round(radius,3) if radius is not None else None,
     "candidates":{k:round(v,5) for v,k,w in options}})
   for ti,month in enumerate(dates):
    if not te[ti]:continue
    for j in held_sites:
     sector=nodes[ho[j]]
     prev=oldrows[(str(month),sector)]
     obs=float(raw[ti,ho[j]])
     if abs(float(prev["observado_mm"])-obs)>.002:raise ValueError("Comparator not paired")
     y=float(chosen_pred[ti,j])
     result.append({"mes":str(month),"sector":sector,"paisaje":landscape,
       "estrato":floors[sector],"bloque":str(fold),
       "observado_mm":round(obs,5),"nuevo_rf_mm":round(y,5),
       "rf_10k_mm":float(prev["estimado_rf_mm"]),"climatologia_mm":round(float(ref[ti,ho[j]]),5),
       "intervalo_inf_90_mm":round(max(0,y-(radius or 0)),5),
       "intervalo_sup_90_mm":round(y+(radius or 0),5),
       "rf_p90_10k":float(prev["prob_rf_p90"]),"rf_p95_10k":float(prev["prob_rf_p95"]),
       "evento_p90":int(prev["evento_p90"]),"evento_p95":int(prev["evento_p95"]),
       "opcion_validacion":mode,"peso_rf_validacion":weight})
  print("10L_FIN_BLOQUE",fold,"geos",len(ho),"altos",sum(lookup[nodes[j]] in TARGET for j in ho),flush=True)
 result.sort(key=lambda x:(x["mes"],x["sector"]))
 if len(result)!=11*60 or len(set((r["mes"],r["sector"]) for r in result))!=660:
  raise ValueError("11 high mountain sectors * 60 months required")
 OUT.mkdir(parents=True,exist_ok=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=FIELD);w.writeheader();w.writerows(result)
 def grp(rows):
  if not rows:return None
  n=len(rows);m=lambda fn:float(sum(fn(x) for x in rows)/n)
  return {"n_sector_mes":n,"n_sectores":len(set(x["sector"] for x in rows)),
    "lluvia_media_observada_mm":round(m(lambda x:x["observado_mm"]),3),
    "lluvia_media_nueva_mm":round(m(lambda x:x["nuevo_rf_mm"]),3),
    "mae_optimizado_mm":round(m(lambda x:abs(x["nuevo_rf_mm"]-x["observado_mm"])),4),
    "mae_rf_10k_mm":round(m(lambda x:abs(x["rf_10k_mm"]-x["observado_mm"])),4),
    "mae_climatologia_mm":round(m(lambda x:abs(x["climatologia_mm"]-x["observado_mm"])),4),
    "sesgo_optimizado_mm":round(m(lambda x:x["nuevo_rf_mm"]-x["observado_mm"]),4),
    "intervalo_90_cobertura_pct":round(100*m(lambda x:x["intervalo_inf_90_mm"]<=x["observado_mm"]<=x["intervalo_sup_90_mm"]),2),
    "eventos_p90":sum(x["evento_p90"] for x in rows),
    "eventos_p95":sum(x["evento_p95"] for x in rows)}
 subsets={cat:[r for r in result if r["paisaje"]==cat] for cat in TARGET}
 output={"fase":"10L","tipo":"Random Forest especifico de lluvia mensual en vertientes medias/altas",
   "n_sectores_objetivo":11,"n_meses_prueba":60,"n_sector_mes":len(result),
   "concepto_economico":"Ecorregiones NO oficiales, 9K paisajes experimentales",
   "train":"1997-2015","tuning":"2016-2018 sin sectores held",
   "calibracion":"2019-2020 por banda altitudinal held",
   "test":"2021-2025 test retrospectivo, no as-issued",
   "nuevos_candidatos":list(OPTIONS),"nuevas_variables":["climatologia_mensual_sectores_1997_2015",
     "desviacion_estacional_pre2016","promedio_pre2016_por_sector",
     "altura_dem_preliminar","relieve_local_dem_preliminar",
     "paisaje_ecoclimatico_9K","rezagos CHIRPS t-2+",
     "oceano NOAA y NASA POWER t-2+ solo cuando la variante se selecciona"],
   "resultados":{"total_montana":grp(result),
     "vertiente_media":grp(subsets["ladera_media"]),
     "alta_montana":grp(subsets["cumbres"]),
     "en_2023":grp([r for r in result if r["mes"][:4]=="2023"]),
     "por_region_2023":{k:grp([r for r in v if r["mes"][:4]=="2023"]) for k,v in subsets.items()},
     "por_anio":{str(y):grp([r for r in result if r["mes"][:4]==str(y)]) for y in range(2021,2026)},
     "por_sector":{sid:grp([r for r in result if r["sector"]==sid]) for sid in sorted({r["sector"] for r in result})}},
   "seleccion_solo_2016_2018":decisions,
   "estadisticas": {"criterio":"MAE en mm; alternativas normalizadas/log, ponderadas y expertos; climatología competidor con peso cero.",
    "evaluacion_mensual":"No predice lluvia extrema horaria",
    "predictivos_P90_P95":"Se conservan sin reentrenar las probabilidades 10K, no adjudicar mejoras de clasificación a 10L.",
    "superioridad_estadistica_certificada":False},
   "restricciones":{"alertas_habilitadas":False,"datos_as_issued":False,
    "estaciones_senamhi_independientes":False,"ecorregiones_minam_verificadas":False,
    "modelo_enfermedades":False,"pronostico_2026":False},
   "hashes":{"RF_10K_csv":sha(eco.PRED),"CHIRPS":sha(base.previous.SOURCE)},
   "notas":["Se usan las 11 vertientes 9K de montaña media y alta, no una malla de estaciones.",
     "La climatología histórica por sector proviene de 1997-2015, incluso en el área withheld.",
     "Elegir por validación temporal no implica un pronóstico nuevo as-issued.",
     "Los 3 sectores de alta montaña pueden quedar juntos en un bloque: fallback obligatorio climatológico si no existe entrenamiento independiente.",
     "Se prohíbe forzar mejoras si falla el criterio MAE de validación.",
     "Dependencia espacial entre sectores y celdas NASA, prueba prospectiva pendiente."]}
 # Keep each polygon with scores, not invented geophysical boundaries.
 shapeGeo,lookup,floor=eco.catalog()
 for ft in shapeGeo["features"]:
  p=ft["properties"];key=p["sector"]
  p["metodo_10l"]="modelo_montana" if key in output["resultados"]["por_sector"] else "fase_10k"
  p["mae_10l_mm"]=output["resultados"]["por_sector"].get(key,{}).get("mae_optimizado_mm")
  p["mae_10k_mm"]=output["resultados"]["por_sector"].get(key,{}).get("mae_rf_10k_mm")
  p["no_pronostico_actual"]=True
 MAP.write_text(json.dumps(shapeGeo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 SERIES.write_text(json.dumps({"fase":"10L","descripcion":"Comparación retrospectiva 2021-2025",
  "datos":result},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 output["hashes"].update({"resultados_csv":sha(PRED),"mapa_geojson":sha(MAP),"series_json":sha(SERIES)})
 REPORT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10L_RESUMEN",json.dumps(output["resultados"],ensure_ascii=False),flush=True)
def check():
 d=load(REPORT);g=load(MAP);s=load(SERIES)["datos"];rows=read(PRED)
 if d["fase"]!="10L" or len(rows)!=660 or len(s)!=660 or len(g["features"])!=39:
  raise ValueError("Invalid 10L outputs")
 if d["restricciones"]["alertas_habilitadas"] or d["restricciones"]["modelo_enfermedades"]:
  raise ValueError("Forbidden forecast claims")
 for name,path in (("resultados_csv",PRED),("mapa_geojson",MAP),("series_json",SERIES)):
  if sha(path)!=d["hashes"][name]:raise ValueError("Integrity fail "+name)
 print("10L_QA_OK",d["resultados"]["total_montana"])
if __name__=="__main__":
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true")
 check() if parser.parse_args().check else targeted_evaluation()
