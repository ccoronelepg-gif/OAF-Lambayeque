#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10I: SOLO RANDOM FOREST PARA PRECIPITACIÓN (mm y evento P90).

Four paired feature ablations:
  local CHIRPS (t-2+) | + NOAA Pacific/winds | + NASA atmosphere | + both.
RF Regressor predicts monthly CHIRPS precipitation, RF Classifier predicts
P(monthly rain >= site TRAIN period P90). NO disease/leaf-wetness output.

Research hindcasts with retrospectively revised sources; NOT operational
weather warnings. Grouped coarse NASA bins do not form independent stations.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error,average_precision_score,brier_score_loss
import probabilidad_39_sectores_10f as base
import comparacion_rf_gcn_nasa_10h as nasa
import probabilidad_multivariable_10e as probability

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"datos/rf_precipitacion_10i"
CSV=OUT/"evaluacion_emparejada_10i.csv"
REPORT=OUT/"informe_rf_lluvia_10i.json"
FIELDNAMES=("mes","sector","piso","bloque","familia_variables",
  "lluvia_chirps_observada_mm","lluvia_rf_predicha_mm",
  "lluvia_climatologia_mm","umbral_local_p90_mm","evento_observado_p90",
  "probabilidad_rf_p90","probabilidad_climatologia_p90")
GROUPS=("lluvia","lluvia_oceano","lluvia_atmosfera","lluvia_oceano_atmosfera")
SEED=20261017
MONTHS=np.arange(12,360)
HIST=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text("utf8"))
def records(p):
 with p.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def weather_with_derived(nodes,X,dates):
 out,audit=nasa.join_features(nodes,X,dates)
 if len(out)!=len(dates):raise ValueError("NASA window changed")
 # Physical derived predictors, computed from t-2 air and dewpoint (NOT leaf wetness).
 t=out[:,:,-6].astype(np.float64)
 dew=out[:,:,-1].astype(np.float64)
 def sat(x):return .6108*np.exp(17.27*x/(x+237.3))
 depression=np.maximum(0.,t-dew)
 vpd=np.maximum(0.,sat(t)-sat(np.minimum(t,dew)))
 if not np.isfinite(vpd).all() or np.max(vpd)>35:raise ValueError("Derived humidity physics invalid")
 extra=np.stack((depression,vpd),axis=-1).astype(np.float32)
 return np.concatenate([out,extra],axis=-1),audit

def arm_inputs(nodes,base0,base1,dates):
 atm_only,audit=weather_with_derived(nodes,base0,dates)
 full,other=weather_with_derived(nodes,base1,dates)
 if atm_only.shape[-1]!=base0.shape[-1]+8 or full.shape[-1]!=base1.shape[-1]+8:
  raise ValueError("Atmospheric arms dimensions unexpected")
 return {"lluvia":base0,"lluvia_oceano":base1,
         "lluvia_atmosfera":atm_only,"lluvia_oceano_atmosfera":full},audit

def fit_classifier(xtr,ytr,xhold,train,val,fold,group):
 settings=[]
 for leaf in (4,12):
  clf=RandomForestClassifier(n_estimators=130,min_samples_leaf=leaf,
    max_depth=13,max_features=.8,class_weight="balanced_subsample",
    n_jobs=2,random_state=SEED+fold)
  clf.fit(xtr[train].reshape(-1,xtr.shape[-1]),ytr[train].reshape(-1))
  pv=clf.predict_proba(xtr[val].reshape(-1,xtr.shape[-1]))[:,1]
  brier=float(brier_score_loss(ytr[val].reshape(-1),pv))
  settings.append((brier,leaf,clf))
 b,leaf,best=min(settings,key=lambda v:(v[0],v[1]))
 preds=best.predict_proba(xhold.reshape(-1,xhold.shape[-1]))[:,1].reshape(xhold.shape[:2])
 return preds,{"hoja":leaf,"brier_seleccion_2016_18":round(b,6),"arboles":130}

def fit_regressor(xtr,ytr,xhold,train,val,fold):
 settings=[]
 for leaf in (4,12):
  for transf in ("mm","log1p_mm"):
   reg=RandomForestRegressor(n_estimators=130,min_samples_leaf=leaf,
      max_depth=14,max_features=.8,n_jobs=2,random_state=SEED+fold)
   target=np.log1p(ytr[train]) if transf=="log1p_mm" else ytr[train]
   reg.fit(xtr[train].reshape(-1,xtr.shape[-1]),target.reshape(-1))
   va_p=reg.predict(xtr[val].reshape(-1,xtr.shape[-1]))
   if transf=="log1p_mm":va_p=np.expm1(va_p)
   mae=float(mean_absolute_error(ytr[val].reshape(-1),np.maximum(0,va_p)))
   settings.append((mae,leaf,transf,reg))
 valmae,leaf,transf,best=min(settings,key=lambda v:(v[0],v[1],v[2]))
 out=best.predict(xhold.reshape(-1,xhold.shape[-1]))
 if transf=="log1p_mm":out=np.expm1(out)
 return np.maximum(0,out).reshape(xhold.shape[:2]),{
  "hoja":leaf,"transformacion":transf,"mae_seleccion_2016_18_mm":round(valmae,4),"arboles":130}

def baseline(raw,Y,tr,dates,held):
 """Site-specific TRAIN 1997-2015 reference; no 2019-25 leakage."""
 pred=np.zeros((len(dates),len(held)),dtype=np.float32)
 probs=np.zeros_like(pred)
 month=np.array([int(m[5:7]) for m in dates])
 for j,idx in enumerate(held):
  for m in range(1,13):
   sample=tr&(month==m)
   if sample.sum()<10:raise ValueError("Missing climatological baseline")
   pred[month==m,j]=raw[sample,idx].mean()
   probs[month==m,j]=(Y[sample,idx].sum()+1)/(sample.sum()+10)
 return pred,probs

def group_scores(rows):
 def scored(group):
  y=np.array([float(v["lluvia_chirps_observada_mm"]) for v in group])
  yh=np.array([float(v["lluvia_rf_predicha_mm"]) for v in group])
  yclim=np.array([float(v["lluvia_climatologia_mm"]) for v in group])
  ev=np.array([int(v["evento_observado_p90"]) for v in group])
  p=np.array([float(v["probabilidad_rf_p90"]) for v in group])
  p0=np.array([float(v["probabilidad_climatologia_p90"]) for v in group])
  return {"n":len(group),"positivos":int(ev.sum()),
    "mae_rf_mm":round(float(mean_absolute_error(y,yh)),4),
    "mae_climatologia_mm":round(float(mean_absolute_error(y,yclim)),4),
    "rmse_rf_mm":round(float(np.sqrt(mean_squared_error(y,yh))),4),
    "sesgo_rf_mm":round(float(np.mean(yh-y)),4),
    "brier_rf":round(float(brier_score_loss(ev,p)),6),
    "brier_climatologia":round(float(brier_score_loss(ev,p0)),6),
    "pr_auc_rf":round(float(average_precision_score(ev,p)),5) if ev.sum()>0 else None,
    "pr_auc_climatologia":round(float(average_precision_score(ev,p0)),5) if ev.sum()>0 else None}
 out={}
 for g in GROUPS:
  rr=[r for r in rows if r["familia_variables"]==g]
  out[g]={"global":scored(rr),
    "anual":{str(y):scored([r for r in rr if r["mes"][:4]==str(y)]) for y in range(2021,2026)},
    "por_piso":{k:scored([r for r in rr if r["piso"]==k]) for k in sorted({v["piso"] for v in rr})},
    "por_bloque":{k:scored([r for r in rr if r["bloque"]==k]) for k in sorted({v["bloque"] for v in rr})}}
 return out

def run(check=False):
 if check:
  d=load(REPORT);rr=records(CSV)
  if d["fase"]!="10I" or len(rr)!=4*39*60 or digest(CSV)!=d["sha256_predicciones"]:
   raise ValueError("Missing verified 10I output")
  if d["alertas_operativas_habilitadas"] or d["modelo_validado_operativamente"] is not None:
   raise ValueError("Forbidden model certification")
  print("10I_VERIFICADO",d["seleccion"]["mejor_rf_por_mae_historico"],flush=True)
  return d
 nodes,A,edges,fixed,floors,polygons,data,audit=base.previous.inputs()
 per=base.previous.raster_cells(nodes,polygons)
 folds=base.previous.folds(nodes,polygons,per)
 X0,X1,Y,actual,thresholds,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 arms,source=arm_inputs(nodes,X0,X1,dates)
 if source["n_bins_aproximados"]>=39:raise ValueError("Missing known coarse NASA grid overlap")
 rows=[];settings=[]
 for fold,hold_sectors in sorted(folds.items()):
  train=[j for j,sid in enumerate(nodes) if sid not in hold_sectors]
  hold=[j for j,sid in enumerate(nodes) if sid in hold_sectors]
  _,atr=base.previous.subgraph(A,train)
  _,aho=base.previous.subgraph(A,hold)
  climate,clim_p=baseline(actual,Y,tr,dates,hold)
  for group,X in arms.items():
   xtr=base.enrich(X[:,train,:],atr)
   xh=base.enrich(X[:,hold,:],aho)
   classifier,meta_c=fit_classifier(xtr,Y[:,train],xh,tr,va,fold,group)
   calibrated,meta_cal=probability.platt(classifier,Y[:,hold],{"calibracion":ca})
   reg,meta_r=fit_regressor(xtr,actual[:,train],xh,tr,va,fold)
   settings.append({"bloque":fold,"familia":group,"clasificador":meta_c,
     "calibracion":meta_cal,"regresor":meta_r})
   for ti,mes in enumerate(dates):
    if not te[ti]:continue
    for j,idx in enumerate(hold):
     vals=[reg[ti,j],calibrated[ti,j],actual[ti,idx],climate[ti,j],clim_p[ti,j]]
     if not np.isfinite(vals).all() or reg[ti,j]<0 or not 0<=calibrated[ti,j]<=1:
      raise ValueError("Prediction invalid")
     rows.append({"mes":str(mes),"sector":nodes[idx],
       "piso":floors[nodes[idx]],"bloque":fold,"familia_variables":group,
       "lluvia_chirps_observada_mm":round(float(actual[ti,idx]),5),
       "lluvia_rf_predicha_mm":round(float(reg[ti,j]),5),
       "lluvia_climatologia_mm":round(float(climate[ti,j]),5),
       "umbral_local_p90_mm":round(float(thresholds[idx]),5),
       "evento_observado_p90":int(Y[ti,idx]),
       "probabilidad_rf_p90":round(float(calibrated[ti,j]),6),
       "probabilidad_climatologia_p90":round(float(clim_p[ti,j]),6)})
   print("10I_RF_ENTRENADO",fold,group,"mae_val",meta_r["mae_seleccion_2016_18_mm"],
     "brier_val",meta_c["brier_seleccion_2016_18"],flush=True)
 rows.sort(key=lambda r:(r["mes"],r["sector"],r["familia_variables"]))
 if len(rows)!=9360 or len(set((x["mes"],x["sector"],x["familia_variables"]) for x in rows))!=9360:
  raise ValueError("Test matrix incomplete")
 OUT.mkdir(parents=True,exist_ok=True)
 with CSV.open("w",newline="",encoding="utf8") as f:
  writer=csv.DictWriter(f,fieldnames=FIELDNAMES)
  writer.writeheader();writer.writerows(rows)
 result=group_scores(rows)
 # Choice on held-out 2021-25 only describes this historic experiment.
 # NEVER optimize/retrain with held-out data and call it prospective.
 rankmae=sorted(GROUPS,key=lambda x:result[x]["global"]["mae_rf_mm"])
 rankbrier=sorted(GROUPS,key=lambda x:result[x]["global"]["brier_rf"])
 bestmae=rankmae[0];bestbrier=rankbrier[0]
 report={"fase":"10I","fecha":"2026-10-17",
  "alcance":"Random Forest para lluvia mensual CHIRPS (mm) y evento lluvia elevada ≥P90, NO enfermedades",
  "n_sectores":39,"n_sector_mes_test":2340,"n_predicciones_4_familias":len(rows),
  "particiones":{"entrenamiento":list(base.TRAIN),"seleccion":list(base.VAL),
    "calibracion_probabilidades":list(base.CAL),"prueba":list(base.TEST)},
  "conjunto_variables":{
    "lluvia":"5 rezagos CHIRPS t-2/3/4/6/12, media t-2:4, estacionalidad, ubicación y vecindad",
    "oceano":"SST Niño1+2, Niño3.4, SOI, alisios centro/este, viento marino Pimentel/norte, todos t-2",
    "atmosfera":"NASA POWER temperatura, RH, WS10m, radiación, presión superficie y punto de rocío t-2; derivados VPD y depresión T-rocío t-2"},
  "factores_no_disponibles_homologados":["corrientes oceánicas completas antes 2017",
   "radiación y nubosidad horaria de parcelas","horas de hoja húmeda","humedad del suelo homogénea por sector"],
  "destino_fitosanitario":"No se pronostica enfermedad. La estimación de horas HR elevada necesita meteorología HORARIA; humectación foliar requiere sensor o método validado a nivel de cubierta vegetal. No se deduce de mm mensuales.",
  "grupos_atmosfericos_aproximados":source["n_bins_aproximados"],
  "fuentes_sha256":{"nasa_power_mensual":digest(nasa.ATM),
    "lluvia_chirps_sectorial":digest(base.previous.SOURCE),
    "oceanografia_noaa_regional":digest(base.LAND),
    "soi_alisios_regional":digest(base.SOI),
    "viento_marino_regional":digest(base.MAR)},
  "resultados":result,
  "seleccion":{"orden_mae":rankmae,"orden_brier":rankbrier,
    "mejor_rf_por_mae_historico":bestmae,
    "mejor_rf_por_brier_historico":bestbrier,
    "supera_climatologia_mae":result[bestmae]["global"]["mae_rf_mm"]<result[bestmae]["global"]["mae_climatologia_mm"],
    "supera_climatologia_brier":result[bestbrier]["global"]["brier_rf"]<result[bestbrier]["global"]["brier_climatologia"],
    "nota":"El ranking entre familias evaluado sobre 2021-25 es una comparación descriptiva, no puede usarse para optimizar el modelo y volver a calificar 2021-25 como prueba ciega."},
  "configuraciones_y_metadatos":settings,"sha256_predicciones":digest(CSV),
  "validacion_as_issued":False,"validacion_externa_instrumental":False,
  "modelo_validado_operativamente":None,"alertas_operativas_habilitadas":False,
  "restricciones":["Solo predice precipitación CHIRPS mensual, no horas ni episodios ENFEN.",
    "Reanálisis NASA POWER y CHIRPS Final descargados ex post, sin vintages as-issued.",
    "Un número pequeño de celdas MERRA2 se comparte entre sectores de pliegues distintos.",
    "Las temperaturas y RH mensuales no producen horas de hoja húmeda directamente.",
    "La climatología sectorial debe permanecer como línea base en el portal.",
    "No eliminar indebidamente la cota negativa preliminar S001.",
    "No seleccionar un modelo operativo con este mismo test histórico: probar en años futuros y con instrumentos independientes."]}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10I_FINAL",json.dumps({"resultado_global":{k:v["global"] for k,v in result.items()},
  "seleccion":report["seleccion"],"alertas":False},ensure_ascii=False),flush=True)
 return report

if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true")
 args=a.parse_args();run(check=args.check)
