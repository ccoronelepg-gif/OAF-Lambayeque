#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF automatic research candidate retraining once NEW verified monthly CHIRPS
sector data are committed. Never auto-promote to public operational prediction.

Public CHIRPS v3 final is not instantly available after month-end and historical
'revisions' are not as-issued. No 2026 labels are fabricated. New staged CSVs
MUST provide 39 sector records and auditable original URL, SHA and timestamp.

When future NOAA/NASA archives are absent, degrade EXPLICITLY to rainfall-only
RF rather than recycling 2025 ocean/meteorological signals as current data.
Models saved as internal trusted joblib CI artifacts, not public forecasts.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math,re,itertools
from collections import defaultdict
from pathlib import Path
import numpy as np
from joblib import dump
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
import probabilidad_39_sectores_10f as base

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"datos/nuevos_meses_chirps_10j"
OUTPUT=ROOT/"datos/rf_robusto_10j/actualizacion_automatica_10j.json"
ARTIFACT=ROOT/"modelos/candidatos_temporales_10j/rf_lluvia_candidato.joblib"
PATH_RE=re.compile(r"lluvia_CHIRPS3_FINAL_(20\d\d)_(0[1-9]|1[0-2])\.csv$")
FIELDS=("mes","sector","lluvia_mm","producto","url_fuente","fecha_publicacion_utc","sha256_fuente_original")
SOURCE="CHIRPS3_FINAL"
SHA_RE=re.compile(r"^[0-9a-fA-F]{64}$")
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def months_between(y,m):
 while True:
  yield f"{y:04d}-{m:02d}"
  y,m=(y+1,1) if m==12 else (y,m+1)
def next_month(year,month):return (year+1,1) if month==12 else (year,month+1)
def parse_staged(folder,sectors,now=None):
 now=now or dt.datetime.now(dt.timezone.utc)
 files=sorted(folder.glob("*.csv"))
 if not files:return {},[],{"estado":"SIN_MESES_NUEVOS","n_meses":0}
 required=set(FIELDS);months={};details=[]
 for path in files:
  m=PATH_RE.fullmatch(path.name)
  if not m:raise ValueError("Archivo CHIRPS no cumple nombre: "+path.name)
  year,mo=int(m.group(1)),int(m.group(2))
  if year<2026:raise ValueError("Solo 2026+ en zona de ingresados")
  expected=f"{year}-{mo:02d}"
  with path.open(newline="",encoding="utf-8-sig") as f:
   reader=csv.DictReader(f)
   if not reader.fieldnames or set(reader.fieldnames)!=required:
    raise ValueError("Esquema del archivo nuevo no trazable "+path.name)
   rows=list(reader)
  if len(rows)!=len(sectors):raise ValueError("Exigir exactamente 39 sectores por mes "+expected)
  recorded={}
  for row in rows:
   sid=row["sector"]
   if sid not in sectors or sid in recorded or row["mes"]!=expected or row["producto"]!=SOURCE:
    raise ValueError("Sector duplicado, mes/proveedor inesperados "+expected)
   num=float(row["lluvia_mm"])
   if not math.isfinite(num) or not 0<=num<=4000:raise ValueError("Lluvia fuera de dominio "+sid)
   src=row["url_fuente"]
   if not (src.startswith("https://data.chc.ucsb.edu/") or src.startswith("https://www.chc.ucsb.edu/")):
    raise ValueError("CHIRPS fuente URL no reconocida")
   if not SHA_RE.fullmatch(row["sha256_fuente_original"]):raise ValueError("SHA fuente no válido")
   try:published=dt.datetime.fromisoformat(row["fecha_publicacion_utc"].replace("Z","+00:00"))
   except ValueError as e:raise ValueError("Fecha de publicación inválida") from e
   if published.tzinfo is None or published>now:raise ValueError("Publicación sin zona UTC o futura")
   # Final published after the target month. Reject next-day 'Final' to reduce
   # accidental use of preliminary vintages; does NOT independently verify URL.
   ny,nm=next_month(year,mo)
   following=dt.datetime(ny,nm,1,tzinfo=dt.timezone.utc)
   if published < following+dt.timedelta(days=8):
    raise ValueError("Final declarado demasiado pronto; auditar vintage "+expected)
   recorded[sid]=num
  if expected in months:raise ValueError("Mes repetido "+expected)
  months[expected]=recorded
  details.append({"mes":expected,"sha256_archivo_subido":digest(path),
    "n_sectores":len(recorded),
    "originales_sha256_declarados":sorted(set(row["sha256_fuente_original"] for row in rows)),
    "nota":"Los SHA originales provienen del manifiesto aportado; verificación independiente del URL NO demostrada."})
 requested=sorted(months)
 allmonths=list(itertools.islice(months_between(2026,1),len(requested)))
 if requested != allmonths[:len(requested)]:
  raise ValueError("Faltan meses contiguos desde 2026-01; no interpolar")
 return months,details,{"estado":"MES_COMPLETO_CON_PROCEDENCIA_APORTADA",
  "n_meses":len(months),"n_sectores":len(sectors),"mes_ultimo":requested[-1]}
def prepare_static(nodes,fixed,from1996):
 dates=sorted(from1996)
 expected=list(months_between(1996,1))[:len(dates)]
 if dates!=expected:raise ValueError("Serie 1996+ no contigua")
 rain=np.array([[from1996[month][sid] for sid in nodes] for month in dates],dtype=np.float32)
 X=[];Y=[];dts=[]
 for index in range(12,len(dates)):
  month=int(dates[index][-2:])
  lag=[np.log1p(rain[index-l]) for l in (2,3,4,6,12)]
  rolling=np.log1p(rain[index-4:index-1].mean(axis=0))
  sin=np.full(len(nodes),math.sin(2*math.pi*month/12),dtype=np.float32)
  cos=np.full(len(nodes),math.cos(2*math.pi*month/12),dtype=np.float32)
  feat=np.column_stack([*lag,rolling,sin,cos,*[fixed[:,j] for j in range(3)]])
  X.append(feat);Y.append(rain[index]);dts.append(dates[index])
 return np.array(dts),np.array(X,dtype=np.float32),np.array(Y,dtype=np.float32)
def baselines(Y,dates):
 """P90/P95 and seasonal climatology FROZEN to 1997-2015."""
 tr=(dates>="1997-01")&(dates<="2015-12")
 thresholds={90:np.quantile(Y[tr],.90,axis=0),
             95:np.quantile(Y[tr],.95,axis=0)}
 season=np.zeros(Y.shape,dtype=np.float32)
 binary={}
 month=np.array([int(x[-2:]) for x in dates])
 for level,cutoff in thresholds.items():
  y=(Y>=cutoff[None,:]).astype(int)
  prob=np.zeros(Y.shape,dtype=np.float32)
  for mo in range(1,13):
   mask=tr&(month==mo)
   prob[month==mo]=(y[mask].sum(axis=0)+1)/(mask.sum()+10)
  binary[level]=(y,prob)
 for mo in range(1,13):
  mask=tr&(month==mo)
  season[month==mo]=Y[mask].mean(axis=0)
 return season,binary,thresholds
def rf_fit(X,y,season,binary,train_mask):
 model=RandomForestRegressor(n_estimators=180,min_samples_leaf=12,max_depth=13,
   max_features=.8,random_state=20261017,n_jobs=2)
 # Training on known date labels only, never shadow target months.
 model.fit(X[train_mask],(y-season)[train_mask])
 classifiers={}
 for level,(event,prior) in binary.items():
  clf=RandomForestClassifier(n_estimators=180,min_samples_leaf=12,
     max_depth=13,max_features=.8,random_state=20261017,n_jobs=2,
     class_weight="balanced_subsample")
  if len(np.unique(event[train_mask]))<2:raise ValueError("Solo una clase en entrenamiento")
  clf.fit(X[train_mask],event[train_mask])
  classifiers[level]=clf
 return model,classifiers
def metrics(Y,dates,X,season,labels,reg,cls,mask):
 predict=np.maximum(0,season[mask]+reg.predict(X[mask]))
 truth=Y[mask]
 if not len(truth):return None
 out={"n_sector_mes":len(truth),
   "mae_rf_mm":round(float(np.mean(np.abs(predict-truth))),5),
   "mae_climatologia_mm":round(float(np.mean(np.abs(season[mask]-truth))),5)}
 for level,(ev,prior) in labels.items():
  p=cls[level].predict_proba(X[mask])[:,1]
  out[f"n_eventos_p{level}"]=int(ev[mask].sum())
  out[f"brier_rf_p{level}"]=round(float(np.mean((p-ev[mask])**2)),7)
  out[f"brier_climatologia_p{level}"]=round(float(np.mean((prior[mask]-ev[mask])**2)),7)
 return out
def run(mode):
 nodes,A,edges,fixed,floors,polygons,historical,source=base.previous.inputs()
 new,logs,state=parse_staged(INPUT,set(nodes))
 if mode=="inspect" or not new:
  print("10J_AUTO_INSPECCION",json.dumps(state,ensure_ascii=False),flush=True)
  return
 allrain={m:{sid:historical[sid][m] for sid in nodes}
          for m in (list(itertools.islice(months_between(1996,1),360)))}
 allrain.update(new)
 dates,X,Y=prepare_static(nodes,fixed,allrain)
 baseline,labels,threshold=baselines(Y,dates)
 # Rain-only arm if 2026+ ocean/NASA coverage missing. No pretending to use
 # full multivariable predictors from 2025 in the current target year.
 _,raw=base.previous.subgraph(A,list(range(len(nodes))))
 X=base.enrich(X,raw).reshape(-1,15)
 Y1=Y.reshape(-1);S=baseline.reshape(-1)
 D=np.repeat(np.array(dates),len(nodes))
 L={level:(ev.reshape(-1),prior.reshape(-1)) for level,(ev,prior) in labels.items()}
 n_future=len(new);split=sorted(new)[-12] if n_future>=12 else None
 # First assess shadow on 12 NEW labeled months withheld from training.
 shadow=None
 if split:
  fit=(D<split)
  hold=(D>=split)
  shadow_reg,shadow_cls=rf_fit(X,Y1,S,L,fit)
  shadow=metrics(Y1,D,X,S,L,shadow_reg,shadow_cls,hold)
  shadow["periodo_evaluado"]=split+" a "+max(new)
  shadow["evaluacion_as_issued"]=False
  shadow["etiquetas_2026_que_se_usaron_para_tuning"]=False
 # New candidate refit after previously reported shadow block has been evaluated.
 fit=(D>= "1997-01")
 model,cls=rf_fit(X,Y1,S,L,fit)
 state.update({"fase":"10J","tipo":"REENTRENAMIENTO_CANDIDATO_RF_LLUVIA_UNICAMENTE",
  "familia_factores":"solo_lluvia_CHIRPS_historica",
  "justificacion":"Océano y NASA POWER actualizados 2026+ no demostrados; no reciclar 2025 como si fuera predictores actuales.",
  "n_sector_mes_candidato":int(fit.sum()),"shadow_ultimos_12_meses":shadow,
  "archivos_cargados":logs,
  "fuente_CHIRPS_historica_sha256":digest(base.previous.SOURCE),
  "vintages_auditados_independientemente":False,
  "ejecuciones_de_emision_as_issued_archivadas":False,
  "modelos_no_confiables_se_reemplazan_solos":False,
  "modelo_desplegado_automaticamente":False,
  "prediccion_de_infecciones":False,
  "estado_promocion":"CANDIDATO_INTERNAMENTE_REENTRENADO_NO_OPERATIVO",
  "criterios_minimos_de_publicacion":"12+ meses de previsiones emitidas antes del objetivo, mediciones independientes y mejora robusta de MAE/Brier frente a climatología; revisión científica antes de despliegue.",
  "no_alertas_automaticas":True})
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 ARTIFACT.parent.mkdir(parents=True,exist_ok=True)
 dump({"regressor":model,"classifiers":cls,
   "frozen_climatology_training_period":"1997-2015",
   "dates_through":max(new),"source":"CHIRPS3_Final declarado en uploads",
   "forecast_operational_allowed":False,
   "thresholds_p90_p95":threshold},ARTIFACT)
 state["sha256_modelo_joblib_interno"]=digest(ARTIFACT)
 OUTPUT.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("10J_AUTO_CANDIDATO",json.dumps({"latest":max(new),
   "model_sha":state["sha256_modelo_joblib_interno"],"shadow":shadow,
   "promocion":"PROHIBIDA"},ensure_ascii=False),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=("inspect","candidate"),default="inspect")
 run(p.parse_args().mode)
