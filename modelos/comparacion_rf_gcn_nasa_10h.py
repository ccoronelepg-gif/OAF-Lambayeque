#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10H: paired 39-sector RF/GCN probability benchmark with NASA POWER coarse meteorology.
Requires verified NASA POWER 1996-2025 archive; no pretending it resolves a parcel.
MERRA-2 variables are coarse, ~0.5x0.625deg; solar archive mixes SRB and CERES.
10F RF/GCN comparison is retrospective too; never issue automated warnings.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
import probabilidad_39_sectores_10f as base
import probabilidad_multivariable_10e as metrics
ROOT=Path(__file__).resolve().parents[1]
ATM=ROOT/"datos/nasa_power_10h/atmosfera_power_mensual_39_sectores_10h.csv"
AUDIT=ROOT/"datos/nasa_power_10h/auditoria_fuentes_10h.json"
ORIG=ROOT/"datos/extension_10f/probabilidades_39_sectores_10f.csv"
OUT=ROOT/"datos/modelos_multivariables_10h"
REPORT=OUT/"evaluacion_rf_gcn_nasa_10h.json"
PRED=OUT/"probabilidades_rf_gcn_nasa_10h.csv"
FEATURES=("temperatura_c","humedad_pct","viento_10m_m_s",
          "radiacion_nasa_kwh_m2_dia","presion_superficie_kpa","temperatura_rocio_c")
FIELDS=("mes","sector","piso","bloque","modelo","evento_p90","observado_mm","umbral_p90_mm","probabilidad")
NAMES=("RF_lluvia_oceano_nasa","GCN_lluvia_oceano_nasa")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text("utf8"))
def join_features(nodes,X,dates):
 audit=load(AUDIT)
 if audit.get("fase")!="10H" or audit.get("n_filas")!=14040 or audit.get("ninguna_alerta_automatica") is not True:
  raise ValueError("Histórico NASA 10H completo no auditado")
 if audit["sha256_csv"]!=sha(ATM):
  raise ValueError("Archivo NASA cambió SHA")
 rows=read(ATM)
 if len(rows)!=39*360:raise ValueError("NASA no contiene 360 meses por sector")
 by={};cells=defaultdict(set)
 expected={f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)}
 for row in rows:
  sid,date=row["sector"],row["mes"]
  if sid not in nodes or date not in expected or (sid,date) in by:
   raise ValueError("Sector o mes NASA duplicado/inesperado")
  if row["fuente"]!="NASA_POWER_MERRA2_Meteorologia_SRB_CERES_Radiacion" or row["es_estacion"]!="false":
   raise ValueError("Fuente NASA impropia o etiqueta instrumental errónea")
  values=[float(row[k]) for k in FEATURES]
  if not np.isfinite(values).all():raise ValueError("No finitos NASA")
  by[(sid,date)]=values
  cells[sid].add(row["celda_aprox"])
 if len(by)!=39*360 or any(len(v)!=1 for v in cells.values()):
  raise ValueError("NASA sector mensual incompleto")
 observed_bins=len(set.union(*cells.values()))
 if observed_bins!=audit["n_bins_aproximados"]:
  raise ValueError("La grilla aproximada difiere del informe")
 all_months=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 # forecast month t: only NASA month t-2, never target or t-1.
 extra=np.array([[by[(sid,all_months[k-2])] for sid in nodes] for k in range(12,360)],dtype=np.float32)
 if extra.shape!=(348,39,len(FEATURES)):
  raise ValueError("Matriz NASA incorrecta")
 return np.concatenate((X,extra),axis=2),audit

def summaries(pairs):
 out={}
 for model in NAMES:
  rr=[r for r in pairs if r["modelo"]==model]
  out[model]={"global":metrics.score([r["evento_p90"] for r in rr],[r["probabilidad"] for r in rr]),
    "por_anio":{str(year):metrics.score([r["evento_p90"] for r in rr if r["mes"].startswith(str(year))],
       [r["probabilidad"] for r in rr if r["mes"].startswith(str(year))]) for year in range(2021,2026)}}
 return out
def compare(pairs):
 previous=read(ORIG)
 prev={(r["sector"],r["mes"],r["modelo"]):r for r in previous}
 if len(prev)!=11700:raise ValueError("No existe la prueba pareada completa de 10F")
 names={"RF_lluvia_oceano_nasa":"RF_lluvia_oceano","GCN_lluvia_oceano_nasa":"GCN_lluvia_oceano"}
 bymodel=defaultdict(list)
 for r in pairs:
  key=(r["sector"],r["mes"],names[r["modelo"]])
  old=prev.get(key)
  if old is None:raise ValueError("Pareja 10F ausente")
  if int(old["evento_p90"])!=int(r["evento_p90"]) or abs(float(old["observado_mm"])-float(r["observado_mm"]))>.01:
   raise ValueError("La etiqueta de comparación 10F es distinta")
  newp=float(r["probabilidad"]);oldp=float(old["probabilidad"]);y=int(r["evento_p90"])
  bymodel[r["modelo"]].append((r["mes"][:4],r["sector"],(newp-y)**2-(oldp-y)**2))
 report={}
 for model,vals in bymodel.items():
  year={str(y):round(statistics.mean(v[2] for v in vals if v[0]==str(y)),6) for y in range(2021,2026)}
  delta=round(statistics.mean(v[2] for v in vals),6)
  report[model]={"n":len(vals),"delta_brier_nasa_menos_10f":delta,
    "deltas_anuales":year,
    "interpretacion":"Negativo favorece incluir NASA. Cinco años con dependencia espacial: descriptivo, NO causalidad ni certificacion."}
 return report
def main(check=False):
 if check:
  r=load(REPORT)
  if r["fase"]!="10H" or sha(PRED)!=r["sha256_predicciones"] or r["alertas_habilitadas"] is not False:
   raise ValueError("Comparacion 10H no verificada")
  if len(read(PRED))!=4680:raise ValueError("Prueba incompleta")
  print("10H_MODELOS_VERIFICADOS",r["contraste_pareado_10f"],flush=True);return
 nodes,A,edges,fixed,floors,polygons,data,audit=base.previous.inputs()
 per=base.previous.raster_cells(nodes,polygons)
 partitions=base.previous.folds(nodes,polygons,per)
 X0,X1,Y,rain,thresholds,dates,tr,va,ca,te=base.matrix(nodes,fixed,data)
 X,audit_atm=join_features(nodes,X1,dates)
 output=[];fold_reports=[]
 for k,holdnames in sorted(partitions.items()):
  hold=[i for i,sid in enumerate(nodes) if sid in holdnames]
  train=[i for i,sid in enumerate(nodes) if sid not in holdnames]
  Atr,rtrain=base.previous.subgraph(A,train)
  Aho,rhold=base.previous.subgraph(A,hold)
  xt=base.enrich(X[:,train,:],rtrain)
  xh=base.enrich(X[:,hold,:],rhold)
  rf,meta_rf=base.forest(xt,Y[:,train],xh,tr,va,base.SEED+k)
  gcn,meta_gcn=base.gcn(xt,Y[:,train],xh,Atr,Aho,tr,va,base.SEED+k)
  settings={}
  for model,p in (("RF_lluvia_oceano_nasa",rf),("GCN_lluvia_oceano_nasa",gcn)):
   calibrated,meta=base.clf.platt(p,Y[:,hold],{"calibracion":ca})
   settings[model]={"fit":meta_rf if model.startswith("RF") else meta_gcn,"calibracion":meta}
   for time_index,month in enumerate(dates):
    if not te[time_index]:continue
    for j,index in enumerate(hold):
     probability=float(calibrated[time_index,j])
     if not 0<=probability<=1 or not math.isfinite(probability):
      raise ValueError("Probabilidad inválida")
     output.append({"mes":str(month),"sector":nodes[index],"piso":floors[nodes[index]],
       "bloque":k,"modelo":model,"evento_p90":int(Y[time_index,index]),
       "observado_mm":round(float(rain[time_index,index]),5),
       "umbral_p90_mm":round(float(thresholds[index]),5),
       "probabilidad":round(probability,6)})
  fold_reports.append({"bloque":k,"holdout":list(holdnames),"modelo":settings})
  print("10H_BLOQUE_MODELO",k,"sectores",len(hold),flush=True)
 if len(output)!=4680 or len({(r["mes"],r["sector"],r["modelo"]) for r in output})!=4680:
  raise ValueError("Faltan casos o duplicados")
 output.sort(key=lambda x:(x["mes"],x["sector"],x["modelo"]))
 OUT.mkdir(parents=True,exist_ok=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(output)
 res=summaries(output)
 dif=compare(output)
 ref=load(base.REPORT)
 brierref={v["modelo"]:v["brier"] for v in ref["evaluacion"]["global"]}
 result={"fase":"10H","tipo":"EXPERIMENTO_PAREADO_DE_ABLACION_MULTIVARIABLE_RETROSPECTIVA",
  "n_sector_mes_prueba":2340,"n_predicciones":4680,"n_sectores":39,
  "periodos":{"train":base.TRAIN,"tuning":base.VAL,"calibracion":base.CAL,"prueba":base.TEST},
  "variables_nasa_t_minus_2":list(FEATURES),
  "resolucion_nasa":"NASA POWER MERRA2 0.5x0.625 grados; radiacion SRB/CERES aprox 1 grado. Una muestra por grupo.",
  "numero_bins_nasa_aproximados":audit_atm["n_bins_aproximados"],
  "sectores_en_celdas_compartidas":audit_atm["resumen"]["sectores_en_celdas_nasa_compartidas"],
  "fuentes_sha256":{"atmosfera_10h":sha(ATM),"probabilidades_10f":sha(ORIG)},
  "resultados_modelos_nuevos":res,
  "referencia_10f_brier":brierref,
  "contraste_pareado_10f":dif,
  "bloques":fold_reports,"sha256_predicciones":sha(PRED),
  "mejora_predictiva_operativa_certificada":False,"as_issued_preservado":False,
  "sector_datos_instrumentales":False,
  "modelo_operativo_ganador":None,"alertas_habilitadas":False,
  "limitaciones":[
   "La selección de NASA 0.25° produce celdas compartidas, no 39 estaciones independientes.",
   "El punto interior del poligono experimental no es promedio areal ni cultivo individual.",
   "Los datos de NASA y CHIRPS FINAL pueden haber sido revisados tras la fecha pronosticada.",
   "Los rezagos t−2 reducen riesgo de fuga temporal, pero no certifican snapshots originales.",
   "La comparación usa mismas 2340 etiquetas de prueba de 10F y cinco bloques geograficos.",
   "La calibracion en sectores de prueba 2019-2020 presupone registro histórico local previo.",
   "El mejor Brier observado no demuestra habilidad operativa o enfermedades agrícolas reales."
  ]}
 REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10H_MODELOS",json.dumps({"brier":{m:d["global"]["brier"] for m,d in res.items()},
  "delta":dif,"referencia":brierref,
  "n_celdas":result["numero_celdas_nasa_distintas"]},ensure_ascii=False),flush=True)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args()
 main(check=args.check)
