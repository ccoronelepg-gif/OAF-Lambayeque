#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produce a versioned, NON-OPERATIONAL trusted joblib RF candidate for rainfall.

10J retrospective performance belongs to 5-fold backtesting, not the final
refit on 1997-2025. The joblib artifact is a model package for future research,
never loaded from untrusted files and never pushed as an official forecast.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
import probabilidad_39_sectores_10f as base
import rf_lluvia_extremos_10j as research

ROOT=Path(__file__).resolve().parents[1]
META=ROOT/"datos/rf_robusto_10j/manifest_modelo_candidato_10j.json"
MODEL=ROOT/"modelos/candidatos_10j/rf_precipitacion_candidato_10j.joblib"
SUMMARY=research.SUMMARY
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def prepare():
 report=json.loads(SUMMARY.read_text("utf-8"))
 if report["fase"]!="10J" or report["despliegue_operativo_autorizado"] is not False or sha(research.PRED)!=report["sha256_predicciones"]:
  raise ValueError("No valid 10J benchmark for configuration freeze")
 folds=report["hiperparametros_y_importancias_impureza"]
 chosen=[v for v in folds if v["familia"]=="lluvia"]
 if len(chosen)!=5 or any(report["seleccion_por_bloque"][v]["familia_por_bloque"]!=dict((str(i),"lluvia") for i in range(5)) for v in ("mm","p90","p95")):
  raise ValueError("Selected family changed; no silent fallback")
 nodes,A,edges,fixed,floors,polygons,data,audit=base.previous.inputs()
 X0,X1,Y90,raw,p90,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 # Frozen normals/quantiles from 1997-2015, not updated by the eventual 2026 observations.
 frozen_mm=research.normal(raw,tr,dates)
 frozen_p90=research.frequencies(Y90,tr,dates)
 p95=np.quantile(raw[tr],.95,axis=0)
 Y95=(raw>=p95[None,:]).astype(np.int32)
 frozen_p95=research.frequencies(Y95,tr,dates)
 _,graph=base.previous.subgraph(A,list(range(len(nodes))))
 full=base.enrich(X0,graph)
 train=dates<="2025-12"
 features=full[train].reshape(-1,full.shape[-1])
 if features.shape[1]!=15:raise ValueError("Unexpected rainfall RF feature vector")
 import statistics
 weights={g:float(statistics.median([x[g]["blend_weight"] for x in chosen])) for g in ("mm","p90","p95")}
 leaves={g:int(statistics.median([x[g]["min_samples_leaf"] for x in chosen])) for g in ("mm","p90","p95")}
 reg=RandomForestRegressor(n_estimators=150,max_depth=13,min_samples_leaf=leaves["mm"],
     max_features=.8,random_state=research.SEED,n_jobs=2)
 reg.fit(features,(raw[train]-frozen_mm[train]).reshape(-1))
 clfs={}
 for label,target in (("p90",Y90),("p95",Y95)):
  m=RandomForestClassifier(n_estimators=150,max_depth=13,min_samples_leaf=leaves[label],
     max_features=.8,class_weight="balanced_subsample",random_state=research.SEED,n_jobs=2)
  m.fit(features,target[train].reshape(-1))
  clfs[label]=m
 # Monthly baseline arrays [month-1, node] known before any 2026 target.
 months=np.array([int(s[-2:]) for s in dates])
 baseline={}
 for name,array in (("mm",frozen_mm),("p90",frozen_p90),("p95",frozen_p95)):
  result=np.zeros((12,len(nodes)),dtype=np.float32)
  for m in range(1,13):
   idx=tr&(months==m)
   result[m-1]=array[idx].mean(axis=0)
  baseline[name]=result
 payload={"regressor_residual":reg,"clasificadores":clfs,
   "sector_ids":nodes,"adjacency_raw":graph,"static_9k":fixed,
   "baseline_1997_2015":baseline,"p90_umbral":p90,"p95_umbral":p95,
   "lag_temporal_min_meses":2,"pesos_fijados_validacion_2016_18":weights,
   "codigo_fuente":"modelos/rf_lluvia_extremos_10j.py",
   "origen_proyecto":"OAF-Lambayeque","modelo_experimental":True,
   "prediccion_enfermedad":False,"permite_alertas_operativas":False}
 MODEL.parent.mkdir(parents=True,exist_ok=True)
 META.parent.mkdir(parents=True,exist_ok=True)
 joblib.dump(payload,MODEL,compress=3)
 manifest={"fase":"10J","estado":"CANDIDATO_MODELO_RF_RECENTRENADO_1997_2025_NO_VALIDADO_OPERATIVAMENTE",
   "candidatura":"Lluvia histórica t−2 con modelos RF para mm, P90, P95",
   "periodo_ajuste_final":"1997-01 a 2025-12",
   "periodo_referencia_normales":"1997-01 a 2015-12",
   "pesos_en_validacion_2016_2018":weights,"min_samples_leaf_por_objetivo":leaves,
   "n_sectores":len(nodes),"n_features_rf":features.shape[1],"n_filas_entrenamiento":features.shape[0],
   "sha256_joblib_candidato":sha(MODEL),
   "sha256_benchmark":sha(SUMMARY),"sha256_lluvia_CHIRPS":sha(base.previous.SOURCE),
   "advertencia":"Este refit NO tiene MAE/Brier propios en prueba independiente. No reciclar resultados del modelo fold CV 10J como si fueran de este refit final.",
   "no_as_issued":True,"sin_estaciones_independientes":True,
   "no_infecciones":True,"no_alertas":True,
   "restriccion_inferencia":"Requiere CHIRPS hasta al menos t−2 con disponibilidad verificable; no se pueden generar estimaciones actuales con vacios 2026."}
 META.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("10J_MODELO_CANDIDATO_EXPORTADO",json.dumps({k:manifest[k] for k in ("n_features_rf","n_filas_entrenamiento","pesos_en_validacion_2016_2018","sha256_joblib_candidato")}),flush=True)
def verify():
 d=json.loads(META.read_text("utf-8"))
 if d["fase"]!="10J" or d["no_alertas"] is not True or sha(MODEL)!=d["sha256_joblib_candidato"]:
  raise ValueError("Candidate model corrupted")
 # joblib is safe to load ONLY when generated by trusted local CI; no untrusted user files.
 m=joblib.load(MODEL)
 if m["permite_alertas_operativas"] or m["prediccion_enfermedad"]:
  raise ValueError("Forbidden model behavior")
 if len(m["sector_ids"])!=39 or m["lag_temporal_min_meses"]!=2:
  raise ValueError("Wrong sector coverage or temporal horizon")
 print("10J_MODELO_CANDIDATO_VERIFICADO",d["sha256_joblib_candidato"],flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 verify() if p.parse_args().check else prepare()
