#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10J: rigorous rain-only Random Forest and future-safe research gates.

Targets (NOT diseases): monthly CHIRPS mm, event >= local historical P90,
and relatively exceptional event >= local P95. The 4 feature-family arms,
RF residual corrections and probability shrinkage are selected using
2016-18 VALIDATION on train sectors only. 2019-20 holdout-sector labels
are used exclusively to estimate descriptive prediction intervals.
The frozen 2021-25 interval is evaluated retrospectively, never tuned.

All sources are retrospective final/reanalysis; as-issued not demonstrated.
Any alarm or official forecast requires independent prospective validation.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.metrics import average_precision_score
import probabilidad_39_sectores_10f as base
import random_forest_lluvia_multivariable_10i as previous

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"datos/rf_robusto_10j"
PRED=DEST/"predicciones_rf_tres_objetivos_10j.csv"
SUMMARY=DEST/"auditoria_y_seleccion_10j.json"
MONITOR=DEST/"estado_publicacion_10j.json"
ARMS=("lluvia","lluvia_oceano","lluvia_atmosfera","lluvia_oceano_atmosfera")
OUT_FIELDS=("mes","sector","piso","bloque","familia_rf","lluvia_observada_mm",
    "lluvia_predicha_rf_mm","lluvia_climatologia_mm","limite_inferior_90_mm",
    "limite_superior_90_mm","umbral_p90_sector_mm","umbral_p95_sector_mm",
    "evento_p90_observado","probabilidad_rf_p90","probabilidad_base_p90",
    "evento_p95_observado","probabilidad_rf_p95","probabilidad_base_p95")
SEED=20261017
WEIGHTS=(0.0,.2,.4,.6,.8,1.0)
LEAF=(5,12)
TRIAL_YEARS=("2021","2022","2023","2024","2025")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def report_load(path):return json.loads(path.read_text("utf-8"))
def read(p):
 with p.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def normal(raw,train,dates):
 """All sectors have pre-2016 CHIRPS climatology; permit history in holdout."""
 month=np.array([int(x[-2:]) for x in dates])
 n,sites=raw.shape; mu=np.empty_like(raw,dtype=np.float32)
 for m in range(1,13):
  hist=train&(month==m)
  if hist.sum()<12:raise ValueError("Missing climatic normal "+str(m))
  mu[month==m,:]=raw[hist,:].mean(axis=0)
 return mu
def frequencies(y,train,dates):
 month=np.array([int(x[-2:]) for x in dates])
 out=np.empty_like(y,dtype=np.float32)
 for m in range(1,13):
  hist=train&(month==m)
  n=hist.sum()
  out[month==m,:]=(y[hist,:].sum(axis=0)+1)/(n+10)
 return out
def choose_weight(reference,proposal,y,mask,kind):
 """Use only 2016-18 validation; 0 is a climatological abstention."""
 n=reference[mask];p=proposal[mask];target=y[mask]
 stats=[]
 for w in WEIGHTS:
  pred=(1-w)*n+w*p
  pred=np.maximum(0,pred) if kind=="mm" else np.clip(pred,0,1)
  error=float(np.mean(np.abs(pred-target))) if kind=="mm" else float(np.mean((pred-target)**2))
  stats.append((error,w))
 # deterministic tie-break favors simpler baseline
 loss,weight=min(stats,key=lambda item:(item[0],item[1]))
 return weight,{"metric":"MAE_mm" if kind=="mm" else "Brier",
   "validation_score":round(loss,7),
   "candidates":{str(w):round(error,7) for error,w in stats}}
def rf_mm(xtr,raw,train,val,fold,normal_train,xhold):
 options=[]
 for leaf in LEAF:
  model=RandomForestRegressor(n_estimators=150,max_depth=13,
    min_samples_leaf=leaf,max_features=.8,n_jobs=2,random_state=SEED+fold)
  residual=raw[train]-normal_train[train]
  model.fit(xtr[train].reshape(-1,xtr.shape[-1]),residual.reshape(-1))
  pp=model.predict(xtr.reshape(-1,xtr.shape[-1])).reshape(raw.shape)
  w,detail=choose_weight(normal_train,normal_train+pp,raw,val,"mm")
  options.append((detail["validation_score"],leaf,w,detail,model))
 score,leaf,weight,detail,model=min(options,key=lambda t:(t[0],t[1]))
 pp=model.predict(xhold.reshape(-1,xhold.shape[-1])).reshape(xhold.shape[:2])
 return pp,{"min_samples_leaf":leaf,"blend_weight":weight,
               "validacion":detail,"feature_importances":model.feature_importances_.round(7).tolist()}
def rf_event(xtr,event,train,val,fold,normal_train,xhold):
 choices=[]
 for leaf in LEAF:
  model=RandomForestClassifier(n_estimators=150,max_depth=13,
    min_samples_leaf=leaf,max_features=.8,class_weight="balanced_subsample",
    n_jobs=2,random_state=SEED+fold)
  labels=event[train].reshape(-1).astype(int)
  if labels.min()==labels.max():raise ValueError("Training has only one class")
  model.fit(xtr[train].reshape(-1,xtr.shape[-1]),labels)
  pp=model.predict_proba(xtr.reshape(-1,xtr.shape[-1]))[:,1].reshape(event.shape)
  weight,detail=choose_weight(normal_train,pp,event,val,"event")
  choices.append((detail["validation_score"],leaf,weight,detail,model))
 loss,leaf,w,detail,model=min(choices,key=lambda t:(t[0],t[1]))
 pred=model.predict_proba(xhold.reshape(-1,xhold.shape[-1]))[:,1].reshape(xhold.shape[:2])
 return pred,{"min_samples_leaf":leaf,"blend_weight":w,
               "validacion":detail,"feature_importances":model.feature_importances_.round(7).tolist()}
def bias_correct_clipped(clim,raw_residual,w):return np.maximum(0,np.asarray(clim)+w*np.asarray(raw_residual))
def blend_probability(clim,prob,w):return np.clip((1-w)*clim+w*prob,0,1)
def finite_interval(errors,level=.9):
 """Empirical split holdout calibration radius; NO exchangeability guarantee."""
 arr=np.sort(np.abs(np.asarray(errors,dtype=float).reshape(-1)))
 if not len(arr) or not np.isfinite(arr).all():raise ValueError("Missing calibration residuals")
 k=min(len(arr)-1,max(0,math.ceil((len(arr)+1)*level)-1))
 return float(arr[k])
def scoring(rows):
 if not rows:return None
 y=np.array([float(r["lluvia_observada_mm"]) for r in rows])
 mm=np.array([float(r["lluvia_predicha_rf_mm"]) for r in rows])
 b=np.array([float(r["lluvia_climatologia_mm"]) for r in rows])
 p90=np.array([float(r["probabilidad_rf_p90"]) for r in rows])
 c90=np.array([float(r["probabilidad_base_p90"]) for r in rows])
 p95=np.array([float(r["probabilidad_rf_p95"]) for r in rows])
 c95=np.array([float(r["probabilidad_base_p95"]) for r in rows])
 e90=np.array([int(r["evento_p90_observado"]) for r in rows])
 e95=np.array([int(r["evento_p95_observado"]) for r in rows])
 low=np.array([float(r["limite_inferior_90_mm"]) for r in rows])
 upper=np.array([float(r["limite_superior_90_mm"]) for r in rows])
 return {"n":len(rows),"n_p90":int(e90.sum()),"n_p95":int(e95.sum()),
   "mae_rf_mm":round(float(np.mean(np.abs(mm-y))),5),
   "mae_climatologia_mm":round(float(np.mean(np.abs(b-y))),5),
   "rmse_rf_mm":round(float(np.sqrt(np.mean((mm-y)**2))),5),
   "sesgo_rf_mm":round(float(np.mean(mm-y)),5),
   "brier_rf_p90":round(float(np.mean((p90-e90)**2)),7),
   "brier_ref_p90":round(float(np.mean((c90-e90)**2)),7),
   "pr_auc_rf_p90":round(float(average_precision_score(e90,p90)),5) if e90.sum()>0 else None,
   "pr_auc_ref_p90":round(float(average_precision_score(e90,c90)),5) if e90.sum()>0 else None,
   "brier_rf_p95":round(float(np.mean((p95-e95)**2)),7),
   "brier_ref_p95":round(float(np.mean((c95-e95)**2)),7),
   "pr_auc_rf_p95":round(float(average_precision_score(e95,p95)),5) if e95.sum()>0 else None,
   "cobertura_intervalo_90_pct":round(float(100*np.mean((y>=low)&(y<=upper))),2),
   "ancho_intervalo_90_mm":round(float(np.mean(upper-low)),4)}
def group_summary(rows):
 out={}
 for group in ARMS:
  rr=[r for r in rows if r["familia_rf"]==group]
  out[group]={"global":scoring(rr),
    "por_anio":{y:scoring([r for r in rr if r["mes"][:4]==y]) for y in TRIAL_YEARS},
    "por_piso":{p:scoring([r for r in rr if r["piso"]==p]) for p in sorted({r["piso"] for r in rr})},
    "por_bloque":{str(b):scoring([r for r in rr if r["bloque"]==str(b)]) for b in range(5)}}
 return out
def validation_only_selector(summary_models,observations,selected):
 """Selected arms are frozen on 2016-18, independently of 2021-25 test."""
 out={}
 for objective in ("mm","p90","p95"):
  group=selected[objective]
  rr=[r for r in observations if r["familia_rf"]==group[r["bloque"]]]
  out[objective]={"familia_por_bloque":group,"test":scoring(rr),
                  "eleccion_fuente":"solo validacion 2016-2018, NO test"}
 return out
def run(check=False):
 if check:
  x=report_load(SUMMARY);rr=read(PRED)
  if x["fase"]!="10J" or len(rr)!=9360 or x["sha256_predicciones"]!=sha(PRED):
   raise ValueError("10J file integrity failed")
  if x["despliegue_operativo_autorizado"] or x["predice_enfermedades"]:
   raise ValueError("Forbidden claims")
  print("10J_CHECK_OK",x["decision"],flush=True);return
 nodes,A,edges,fixed,floors,polygons,data,original=base.previous.inputs()
 cells=base.previous.raster_cells(nodes,polygons)
 folds=base.previous.folds(nodes,polygons,cells)
 X0,X1,Y90,raw,threshold90,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 arms,atmo=previous.arm_inputs(nodes,X0,X1,dates)
 if tuple(arms)!=ARMS or len(nodes)!=39:raise ValueError("Unexpected climate arms")
 thresholds95=np.quantile(raw[tr],.95,axis=0)
 Y95=(raw>=thresholds95[None,:]).astype(np.float32)
 base_mm=normal(raw,tr,dates)
 base90=frequencies(Y90,tr,dates)
 base95=frequencies(Y95,tr,dates)
 n_records=0;rows=[];fold_detail=[];val_arm={}
 for fold,hold_names in sorted(folds.items()):
  trix=[i for i,s in enumerate(nodes) if s not in hold_names]
  hoix=[i for i,s in enumerate(nodes) if s in hold_names]
  _,atr=base.previous.subgraph(A,trix)
  _,aho=base.previous.subgraph(A,hoix)
  val_arm[str(fold)]={}
  for arm in ARMS:
   xin=base.enrich(arms[arm][:,trix,:],atr)
   xout=base.enrich(arms[arm][:,hoix,:],aho)
   mm_res,mm_info=rf_mm(xin,raw[:,trix],tr,va,fold,base_mm[:,trix],xout)
   p90_raw,p90_info=rf_event(xin,Y90[:,trix],tr,va,fold,base90[:,trix],xout)
   p95_raw,p95_info=rf_event(xin,Y95[:,trix],tr,va,fold,base95[:,trix],xout)
   mu=base_mm[:,hoix]
   phat=bias_correct_clipped(mu,mm_res,mm_info["blend_weight"])
   p90=blend_probability(base90[:,hoix],p90_raw,p90_info["blend_weight"])
   p95=blend_probability(base95[:,hoix],p95_raw,p95_info["blend_weight"])
   # Frozen 2019-20 holdout-sector calibration is NOT used for tuning or weight choice.
   radius=finite_interval(raw[ca][:,hoix]-phat[ca])
   low=np.maximum(0,phat-radius);high=phat+radius
   val_arm[str(fold)][arm]={"mm":mm_info["validacion"]["validation_score"],
       "p90":p90_info["validacion"]["validation_score"],
       "p95":p95_info["validacion"]["validation_score"]}
   fold_detail.append({"bloque":fold,"n_sectores_holdout":len(hoix),
       "familia":arm,"mm":mm_info,"p90":p90_info,"p95":p95_info,
       "calibracion_2019_2020":{"radio_intervalo_90_mm":round(radius,5),
         "n_registros":int(ca.sum()*len(hoix)),
         "cobertura_nominal_no_garantizada":True}})
   for time,month in enumerate(dates):
    if not te[time]:continue
    for j,idx in enumerate(hoix):
     y=float(raw[time,idx])
     item={"mes":str(month),"sector":nodes[idx],"piso":floors[nodes[idx]],
       "bloque":str(fold),"familia_rf":arm,
       "lluvia_observada_mm":round(y,5),
       "lluvia_predicha_rf_mm":round(float(phat[time,j]),5),
       "lluvia_climatologia_mm":round(float(mu[time,j]),5),
       "limite_inferior_90_mm":round(float(low[time,j]),5),
       "limite_superior_90_mm":round(float(high[time,j]),5),
       "umbral_p90_sector_mm":round(float(threshold90[idx]),5),
       "umbral_p95_sector_mm":round(float(thresholds95[idx]),5),
       "evento_p90_observado":int(Y90[time,idx]),
       "probabilidad_rf_p90":round(float(p90[time,j]),7),
       "probabilidad_base_p90":round(float(base90[time,idx]),7),
       "evento_p95_observado":int(Y95[time,idx]),
       "probabilidad_rf_p95":round(float(p95[time,j]),7),
       "probabilidad_base_p95":round(float(base95[time,idx]),7)}
     if not all(np.isfinite(float(item[k])) for k in ("lluvia_predicha_rf_mm","probabilidad_rf_p90","probabilidad_rf_p95")):
      raise ValueError("Nonfinite rain prediction")
     rows.append(item)
   print("10J_RF_TRAINED",fold,arm,"val_mm",mm_info["validacion"]["validation_score"],
     "val_p90",p90_info["validacion"]["validation_score"],
     "val_p95",p95_info["validacion"]["validation_score"],flush=True)
 if len(rows)!=39*60*len(ARMS):raise ValueError("Some held out rows missing")
 rows.sort(key=lambda r:(r["mes"],r["sector"],r["familia_rf"]))
 DEST.mkdir(exist_ok=True,parents=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=OUT_FIELDS);w.writeheader();w.writerows(rows)
 selections={}
 for objective in ("mm","p90","p95"):
  selections[objective]={fold:min(ARMS,key=lambda arm:(val_arm[fold][arm][objective],ARMS.index(arm))) for fold in val_arm}
 summary=group_summary(rows)
 selection=validation_only_selector(summary,rows,selections)
 mm=selection["mm"]["test"]
 p90=selection["p90"]["test"]
 p95=selection["p95"]["test"]
 decision={
  "modelo_familia":"Random Forest exclusivamente para lluvia",
  "prediccion_mm_supera_climatologia":mm["mae_rf_mm"]<mm["mae_climatologia_mm"],
  "probabilidad_p90_supera_climatologia":p90["brier_rf_p90"]<p90["brier_ref_p90"],
  "probabilidad_p95_supera_climatologia":p95["brier_rf_p95"]<p95["brier_ref_p95"],
  "seleccion_solo_validacion":True,
  "modelo_operativo_publicable":False,
  "razon":"No hay validacion as-issued ni estaciones independientes y el periodo 2021-25 se ha consultado en estudios previos."}
 report={"fase":"10J","objetivo":"precipitacion mensual CHIRPS en mm + P90 + P95 local; NO enfermedades",
  "n_sectores":39,"n_sector_mes":2340,"n_predicciones":len(rows),
  "entrenamiento":"1997-2015","seleccion":"2016-2018 sobre sectores de entrenamiento",
  "calibracion_intervalo":"2019-2020 en sectores holdout; dependencia espacial, sin cobertura garantizada",
  "evaluacion":"2021-2025 retrospectivo","banda_intervalo":"intervalo simetrico por residuos |error|, nivel 90% exploratorio",
  "interpretacion_extremos":"P90 alto y P95 excepcional relativos al sector, NO umbrales de alertas oficiales ni lluvia horaria intensa.",
  "lags_de_variables_temporales":"al menos 2 meses",
  "fuentes_sha256":{"CHIRPS":sha(base.previous.SOURCE),"NASA_POWER":sha(previous.nasa.ATM),
    "NOAA_SST":sha(base.LAND),"SOI_alisios":sha(base.SOI),"viento_marino":sha(base.MAR)},
  "grupos_nasa_aproximados":atmo["n_bins_aproximados"],
  "familias_rf":list(ARMS),"resultados":summary,
  "validacion_elecciones":val_arm,"seleccion_por_bloque":selection,
  "hiperparametros_y_importancias_impureza":fold_detail,
  "decision":decision,"sha256_predicciones":sha(PRED),
  "as_issued_demostrado":False,"estaciones_independientes_verificadas":False,
  "predice_enfermedades":False,"despliegue_operativo_autorizado":False,
  "limitaciones":["No datos diarios u horarios para predecir tormenta puntual ni hora de lluvia.",
    "No equivale a ocurrencia oficial El Nino; objetivos P90 y P95 estadisticos locales.",
    "NASA MERRA2 contiene 7 bins aproximados, NO 39 estaciones.",
    "Radiacion NASA SRB/CERES tiene posible discontinuidad de producto en 2001.",
    "Series historicas descargadas posteriormente, NO reproduccion de datos disponibles al momento.",
    "P95 poco frecuente: estadistica de los extremos no garantiza habilidad en episodios raros.",
    "Intervalos empiricos carecen de garantia nominal por dependencia temporal/espacial.",
    "No se autoriza promocion automatica sin mejoras fuera de muestra e instrumentos independientes.",
    "Los futuros algoritmos de enfermedades requieren etiquetas de campo independientes."]}
 SUMMARY.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 state={"fase":"10J","modo":"INVESTIGACION_RF_LLUVIA",
   "puede_mostrar_metricas_retrospectivas":True,
   "puede_emitir_predicciones_operativas":False,
   "permite_reentrenamiento_automatico_candidato":True,
   "promocion_a_produccion_automatica":False,
   "requiere_observaciones_nuevas_2026_o_posteriores":True,
   "requiere_verificacion_as_issued_y_estaciones":True,
   "modelo_reemplazado_automaticamente":False,
   "prohibida_prediccion_enfermedades":True,
   "sha256_informe":sha(SUMMARY),"sha256_predicciones":sha(PRED)}
 MONITOR.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("10J_FINAL",json.dumps({"seleccion":selection,"decision":decision,"global":{k:v["global"] for k,v in summary.items()}},ensure_ascii=False),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");arg=p.parse_args()
 run(check=arg.check)
