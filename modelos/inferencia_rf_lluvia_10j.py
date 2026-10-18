#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protected inference for the trained 10J RF research candidate (not alerts).

Given a target month YYYY-MM, require authentic CHIRPS sectors for t-2, t-3,
t-4, t-6, and t-12. No use of t-1 or target y. A target-month forecast with
missing history fails closed. Historical replays are NOT original as-issued.
"""
from __future__ import annotations
import argparse,datetime as dt,json,math
from pathlib import Path
import joblib
import numpy as np
import probabilidad_39_sectores_10f as base
import actualizacion_automatica_rf_10j as updates
import rf_lluvia_extremos_10j as research
from exportar_candidato_rf_10j import MODEL,META,sha

ROOT=Path(__file__).resolve().parents[1]
def shift(ym,k):
 year,mo=map(int,ym.split("-"))
 offset=12*year+mo-1-k
 return f"{offset//12:04d}-{offset%12+1:02d}"
def build_features(payload,history,target):
 nodes=payload["sector_ids"]
 month=int(target[-2:])
 vals=[]
 for lag in (2,3,4,6,12):
  source=shift(target,lag)
  if source not in history:raise ValueError("CHIRPS no disponible para "+source+"; bloquear inferencia")
  vals.append(np.log1p([history[source][s] for s in nodes]))
 rolling=np.stack([np.array([history[shift(target,k)][s] for s in nodes]) for k in (4,3,2)])
 row=np.column_stack([*vals,np.log1p(rolling.mean(axis=0)),
   np.full(len(nodes),math.sin(2*math.pi*month/12)),
   np.full(len(nodes),math.cos(2*math.pi*month/12)),
   *[payload["static_9k"][:,i] for i in range(3)]]).astype("float32")
 if row.shape!=(39,11):raise ValueError("Wrong RF input matrix")
 X=base.enrich(row[None,:,:],payload["adjacency_raw"])[0]
 if X.shape!=(39,15) or not np.isfinite(X).all():raise ValueError("Wrong RF enriched features")
 return X
def research_inference(payload,history,target):
 X=build_features(payload,history,target)
 mi=int(target[-2:])-1
 baseline=payload["baseline_1997_2015"]
 w=payload["pesos_fijados_validacion_2016_18"]
 pmm=np.maximum(0,baseline["mm"][mi]+w["mm"]*payload["regressor_residual"].predict(X))
 scores={}
 for k in ("p90","p95"):
  raw=payload["clasificadores"][k].predict_proba(X)[:,1]
  scores[k]=np.clip((1-w[k])*baseline[k][mi]+w[k]*raw,0,1)
 records=[]
 for i,sector in enumerate(payload["sector_ids"]):
  records.append({"sector":sector,"mes_objetivo":target,
    "lluvia_rf_mm":round(float(pmm[i]),4),
    "p_rain_ge_p90":round(float(scores["p90"][i]),6),
    "p_rain_ge_p95":round(float(scores["p95"][i]),6),
    "umbral_p90_sector_mm":round(float(payload["p90_umbral"][i]),4),
    "umbral_p95_sector_mm":round(float(payload["p95_umbral"][i]),4),
    "prediccion_enfermedad":None,"es_alerta_meteorologica":False})
 return records
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--mes",required=True)
 ap.add_argument("--salida",type=Path,required=True)
 args=ap.parse_args()
 if not args.mes.endswith(tuple(f"-{x:02d}" for x in range(1,13))):
  raise ValueError("Mes objetivo inválido")
 metadata=json.loads(META.read_text("utf-8"))
 if sha(MODEL)!=metadata["sha256_joblib_candidato"] or not metadata["no_alertas"]:
  raise ValueError("Model provenance does not pass")
 model=joblib.load(MODEL) # ONLY own verified CI model.
 nodes,_,_,_,_,_,data,_=base.previous.inputs()
 history={month:{sid:data[sid][month] for sid in nodes}
   for month in (list(updates.months_between(1996,1))[:360])}
 # New source data must be validated monthly, not invented.
 later,_,_=updates.parse_staged(updates.INPUT,set(nodes))
 history.update(later)
 result=research_inference(model,history,args.mes)
 args.salida.parent.mkdir(parents=True,exist_ok=True)
 args.salida.write_text(json.dumps({"modo":"EXPERIMENTO_RETROSPECTIVO_Y_CANDIDATO",
   "mes_objetivo":args.mes,"historico_as_issued_demostrado":False,
   "no_alertas":True,"no_enfermedades":True,"datos":result},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10J_INFERENCIA_EXPERIMENTAL",args.mes,len(result),flush=True)
if __name__=="__main__":main()
