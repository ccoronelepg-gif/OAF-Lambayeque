#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10N — SOLO RF experimental de corrección pluviométrica en estación.
Importa los 40 meses SENAMHI 10M, sin control de calidad formal; cruza la
normal CHIRPS 1997-2015 de los sectores S007-S008 en el dataset de 10L.
Train <=2024 (17 meses), valida 2025 (15), prueba retrospectiva 2026 (8).
NO reemplaza RF regional 10L, NO alerta oficial, NO enfermedad.
"""
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
from joblib import dump
from sklearn.ensemble import RandomForestRegressor

ROOT=Path(__file__).resolve().parents[1]
STATION=ROOT/"datos/senamhi_10n/meses_pluviometricos_completos_10n.csv"
REFERENCE=ROOT/"datos/montanas_10l/predicciones_lluvia_montanas_10l.csv"
REPORT=ROOT/"datos/senamhi_10n/evaluacion_rf_estacion_10n.json"
PRED=ROOT/"datos/senamhi_10n/evaluacion_mensual_rf_estacion_10n.csv"
MODEL=ROOT/"modelos/candidatos_10n/rf_estaciones_cumbre_10n.joblib"
LEAVES=[2,3,5];DEPTH={2:3,3:4,5:4};WEIGHTS=[0,.25,.5,.75,1.]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(p):
 with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def records():
 rows=read(STATION);grid=read(REFERENCE)
 assert len(rows)==40 and all(x["observacion_sin_qc"]=="true" for x in rows)
 normals={}
 for x in grid:
  if x["sector"] not in ("S007","S008"):continue
  key=(x["sector"],int(x["mes"][-2:]))
  value=float(x["climatologia_mm"])
  if key in normals and abs(normals[key]-value)>0.0002:raise ValueError("Climatologia cambia por año, posible fuga")
  normals[key]=value
 assert len(normals)==24
 out=[]
 for x in rows:
  code=x["codigo_estacion"];sector=x["sector_9k"];month=x["mes"];year=int(month[:4])
  if (code,sector) not in (("153102","S008"),("000307","S007")):raise ValueError("Station polygon incorrect")
  target=float(x["precipitacion_mm"])
  if not np.isfinite(target) or target<0:raise ValueError("Bad rain")
  label="train" if year<=2024 else "validation" if year==2025 else "test" if year==2026 else "invalid"
  if label=="invalid":raise ValueError("Year not allowed")
  out.append(dict(code=code,name=x["estacion"],sector=sector,year=year,month=month,
    mon=int(month[-2:]),rain=target,clim=normals[(sector,int(month[-2:]))],
    alt=float(x["altitud_m"]),split=label))
 if len({(r["code"],r["month"]) for r in out})!=40:raise ValueError("Station month duplicates")
 return out
def design(data):
 return np.array([[math.sin((x["mon"]-1)*math.pi/6),math.cos((x["mon"]-1)*math.pi/6),
   math.log1p(x["clim"]),x["alt"]/4000,float(x["sector"]=="S007"),float(x["sector"]=="S008")] for x in data])
def fit(data,leaf):
 m=RandomForestRegressor(n_estimators=250,min_samples_leaf=leaf,max_depth=DEPTH[leaf],
  max_features=1.,bootstrap=True,n_jobs=1,random_state=20261018)
 m.fit(design(data),np.array([x["rain"]-x["clim"] for x in data]))
 return m
def metric(data,p):
 return dict(n=len(data),mae_rf_mm=round(float(np.mean([abs(a["rain"]-v) for a,v in zip(data,p)])),4),
  mae_climatologia_mm=round(float(np.mean([abs(a["rain"]-a["clim"]) for a in data])),4),
  sesgo_rf_mm=round(float(np.mean([v-a["rain"] for a,v in zip(data,p)])),4))
def run():
 data=records()
 train=[r for r in data if r["split"]=="train"]
 val=[r for r in data if r["split"]=="validation"]
 test=[r for r in data if r["split"]=="test"]
 assert (len(train),len(val),len(test))==(17,15,8)
 attempts=[]
 for leaf in LEAVES:
  model=fit(train,leaf)
  corrections=model.predict(design(val))
  for weight in WEIGHTS:
   pred=np.maximum(0,np.array([r["clim"] for r in val])+weight*corrections)
   mae=float(np.mean([abs(r["rain"]-v) for r,v in zip(val,pred)]))
   attempts.append((mae,weight,leaf))
 mae,w,leaf=min(attempts)
 # Frozen choice from 2025; model fitted through 2025 evaluates 2026, not used to select.
 mv=fit(train,leaf);m2026=fit(train+val,leaf)
 pv=np.maximum(0,np.array([r["clim"] for r in val])+w*mv.predict(design(val)))
 pt=np.maximum(0,np.array([r["clim"] for r in test])+w*m2026.predict(design(test)))
 MODEL.parent.mkdir(parents=True,exist_ok=True)
 dump({"rf_residual":m2026,"calibration_weight":w,"trained_through":"2025-12",
   "station_codes":["153102","000307"],"operational":False,"predicts_infections":False},MODEL,compress=3)
 sample=[]
 for group,pred in ((val,pv),(test,pt)):
  for row,y in zip(group,pred):
   sample.append(dict(estacion_codigo=row["code"],estacion=row["name"],sector=row["sector"],
    mes=row["month"],etapa=row["split"],lluvia_estacion_mm=row["rain"],
    lluvia_normal_sector_chirps_mm=row["clim"],lluvia_rf_ajustada_mm=round(float(y),5),
    datos_calidad_formal=False,alerta_operativa=False))
 with PRED.open("w",newline="",encoding="utf8") as f:
  flds=list(sample[0]);wr=csv.DictWriter(f,fieldnames=flds);wr.writeheader();wr.writerows(sorted(sample,key=lambda x:(x["mes"],x["estacion_codigo"])))
 report={"fase":"10N","fuente":"SENAMHI/DRD aportado sin QC instrumental",
  "estaciones":2,"estaciones_codigos":["153102","000307"],"sectores":["S008","S007"],
  "meses_completos":len(data),"entrenamiento_2021_2024":len(train),
  "ajuste_2025":len(val),"prueba_2026":len(test),
  "resultado_validation":metric(val,pv),"resultado_2026":metric(test,pt),
  "resultado_2026_por_estacion":{code:metric([r for r in test if r["code"]==code],[float(p) for r,p in zip(test,pt) if r["code"]==code]) for code in ("153102","000307")},
  "seleccion_validacion":{"peso_rf":w,"hoja_minima":leaf,"profundidad":DEPTH[leaf],"arboles":250,"mae_validacion_mm":round(mae,5)},
  "sha256":{"csv_senamhi":sha(STATION),"referencia_10l":sha(REFERENCE),"modelo_binario_interno":sha(MODEL),"predicciones_mensuales":sha(PRED)},
  "lectura_correcta":"RF entrenado como corrector puntual, con peso 0 si no mejora la climatología. No es el RF territorial reentrenado.",
  "fecha_de_emision_historica_verificada":False,"independencia_de_CHIRPS_verificada":False,
  "QC_instrumental_formal_aprobado":False,"reentrenamiento_regional":False,
  "pronosticos_actuales_habilitados":False,"alertas_habilitadas":False,"prediccion_enfermedades":False,
  "limitaciones":["17 meses iniciales y 15 de validacion de solo dos estaciones, periodos discontinuos",
   "8 pares de 2026 para test, insuficientes para habilidad robusta",
   "climatologia CHIRPS sectorial ≠ precipitacion puntual de la estacion",
   "las entradas y observaciones se recopilaron retrospectivamente y no son as-issued",
   "necesario control instrumental SENAMHI y estaciones ajenas a CHIRPS antes de activar uso publico"]}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10N_CANDIDATO",json.dumps({"validacion":report["resultado_validation"],"prueba":report["resultado_2026"],"parametros":report["seleccion_validacion"]},ensure_ascii=False))
def check():
 r=json.loads(REPORT.read_text("utf8"))
 assert r["fase"]=="10N" and r["meses_completos"]==40 and r["prueba_2026"]==8
 assert r["sha256"]["predicciones_mensuales"]==sha(PRED)
 assert r["sha256"]["csv_senamhi"]==sha(STATION)
 assert r["alertas_habilitadas"] is False and r["prediccion_enfermedades"] is False
 print("10N_VERIFICADO")
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 check() if a.check else run()
