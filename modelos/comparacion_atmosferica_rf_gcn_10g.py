#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10G: paired 39-sector RF/GCN probabilistic ablation using ERA5 local-grid samples.
Requires verified 10G 39*360 ERA5 archive; fails closed if unavailable.
All ERA5 fields are from 0.25deg reanalysis points, not independent farm stations.
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
ATM=ROOT/"datos/atmosfera_sectorial_10g/muestra_era5_mensual_10g.csv"
AUDIT=ROOT/"datos/atmosfera_sectorial_10g/auditoria_atmosfera_10g.json"
ORIG=ROOT/"datos/extension_10f/probabilidades_39_sectores_10f.csv"
OUT=ROOT/"datos/experimento_multivariable_10g"
REPORT=OUT/"evaluacion_rf_gcn_era5_10g.json"
PRED=OUT/"probabilidades_rf_gcn_era5_10g.csv"
FEATURES=("temperatura_aire_c","humedad_relativa_pct","viento_10m_m_s",
          "radiacion_corta_mj_m2","presion_nivel_mar_hpa","nubosidad_pct",
          "vpd_max_diario_media_mes_kpa")
FIELDS=("mes","sector","piso","bloque","modelo","evento_p90","observado_mm","umbral_p90_mm","probabilidad")
NAMES=("RF_lluvia_oceano_era5","GCN_lluvia_oceano_era5")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text("utf8"))
def join_features(nodes,X,dates):
 audit=load(AUDIT)
 if audit.get("fase")!="10G" or audit.get("modo")!="extraccion_1996_2025" or audit.get("alertas_activadas") is not False:
  raise ValueError("Atmosfera 10G completa no auditada")
 if audit["sha256_matriz"]!=sha(ATM) or audit["resumen"]["filas"]!=14040:
  raise ValueError("Archivo atmosferico alterado")
 rows=read(ATM)
 if len(rows)!=39*360:raise ValueError("No existen 360 meses por sector")
 by={}
 ids=set(nodes)
 expected={f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)}
 cells=defaultdict(set)
 for row in rows:
  sid,date=row["sector"],row["mes"]
  if sid not in ids or date not in expected or (sid,date) in by:raise ValueError("Sector, mes o duplicado ERA5 no valido")
  if row.get("producto")!="ERA5-0.25deg-OpenMeteo-historical-reanalysis":raise ValueError("Fuente atmosferica ajena")
  if row.get("medicion_instrumental")!="false" or row.get("punto_representativo_no_promedio_areal")!="true":
   raise ValueError("No se puede presentar como medicion instrumental")
  values=[float(row[k]) for k in FEATURES]
  if not np.isfinite(values).all() or int(row["dias_validos"])<28:
   raise ValueError("Variable nula o faltan dias en "+sid+"/"+date)
  by[(sid,date)]=values
  cells[sid].add((row["era5_celda_lat"],row["era5_celda_lon"]))
 if len(by)!=39*360 or any(len(v)!=1 for v in cells.values()):
  raise ValueError("Matriz ERA5 no homogénea 1996-2025")
 if audit["resumen"]["n_celdas_era5_distintas"]!=len(set.union(*cells.values())):
  raise ValueError("La multiplicidad de celdas no coincide con auditoria")
 all_months=[f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)]
 extra=np.array([[[*by[(sid,all_months[k-2])]] for sid in nodes]
                 for k in range(12,360)],dtype=np.float32)
 if extra.shape!=(348,39,7):raise ValueError("Dimensionalidad extra inválida")
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
 names={"RF_lluvia_oceano_era5":"RF_lluvia_oceano","GCN_lluvia_oceano_era5":"GCN_lluvia_oceano"}
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
  report[model]={"n":len(vals),"delta_brier_era5_menos_10f":delta,
    "deltas_anuales":year,
    "interpretacion":"Negativo favorece incluir ERA5. Cinco años con dependencia espacial: descriptivo, NO causalidad ni certificacion."}
 return report
def main(check=False):
 if check:
  r=load(REPORT)
  if r["fase"]!="10G" or sha(PRED)!=r["sha256_predicciones"] or r["alertas_habilitadas"] is not False:
   raise ValueError("Comparacion 10G no verificada")
  if len(read(PRED))!=4680:raise ValueError("Prueba incompleta")
  print("10G_MODELOS_VERIFICADOS",r["contraste_pareado_10f"],flush=True);return
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
  for model,p in (("RF_lluvia_oceano_era5",rf),("GCN_lluvia_oceano_era5",gcn)):
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
  print("10G_BLOQUE_MODELO",k,"sectores",len(hold),flush=True)
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
 result={"fase":"10G","tipo":"EXPERIMENTO_PAREADO_DE_ABLACION_MULTIVARIABLE_RETROSPECTIVA",
  "n_sector_mes_prueba":2340,"n_predicciones":4680,"n_sectores":39,
  "periodos":{"train":base.TRAIN,"tuning":base.VAL,"calibracion":base.CAL,"prueba":base.TEST},
  "variables_era5_t_minus_2":list(FEATURES),
  "resolucion_era5":"0.25 grados, una celda nearest por poligono 9K; algunas compartidas",
  "numero_celdas_era5_distintas":audit_atm["resumen"]["n_celdas_era5_distintas"],
  "sectores_en_celdas_compartidas":audit_atm["resumen"]["sectores_en_celdas_era5_compartidas"],
  "fuentes_sha256":{"atmosfera_10g":sha(ATM),"probabilidades_10f":sha(ORIG)},
  "resultados_modelos_nuevos":res,
  "referencia_10f_brier":brierref,
  "contraste_pareado_10f":dif,
  "bloques":fold_reports,"sha256_predicciones":sha(PRED),
  "mejora_predictiva_operativa_certificada":False,"as_issued_preservado":False,
  "sector_datos_instrumentales":False,
  "modelo_operativo_ganador":None,"alertas_habilitadas":False,
  "limitaciones":[
   "La selección de ERA5 0.25° produce celdas compartidas, no 39 estaciones independientes.",
   "El punto interior del poligono experimental no es promedio areal ni cultivo individual.",
   "Los datos de ERA5 y CHIRPS FINAL pueden haber sido revisados tras la fecha pronosticada.",
   "Los rezagos t−2 reducen riesgo de fuga temporal, pero no certifican snapshots originales.",
   "La comparación usa mismas 2340 etiquetas de prueba de 10F y cinco bloques geograficos.",
   "La calibracion en sectores de prueba 2019-2020 presupone registro histórico local previo.",
   "El mejor Brier observado no demuestra habilidad operativa o enfermedades agrícolas reales."
  ]}
 REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10G_MODELOS",json.dumps({"brier":{m:d["global"]["brier"] for m,d in res.items()},
  "delta":dif,"referencia":brierref,
  "n_celdas":result["numero_celdas_era5_distintas"]},ensure_ascii=False),flush=True)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args()
 main(check=args.check)
