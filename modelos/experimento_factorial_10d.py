#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10D: matched factorial lag 1 vs lag 2+, same train/tune/cal/test windows.

RESEARCH ONLY: CHIRPS v3 FINAL is retrospectively revised and no as-issued data
or independent gauges validate these hindcasts. Do not issue operational alerts.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
import generalizacion_espacial_9x as lag1
import reentrenamiento_lag2_10c as core

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/experimentos_10d"
REPORT=BASE/"evaluacion_controlada_10d.json"
PRED=BASE/"predicciones_factorial_10d.csv"
INDEX=BASE/"roni_noaa_2021_2025.json"
REF10C=ROOT/"datos/reentrenamiento_10c/evaluacion_lag2_10c.json"
ARMS=("lag1","lag2")
MODELS=("climatologia_piso","random_forest","gcn")
FIELDS=("brazo","mes","sector","piso","bloque","modelo","observado_mm","estimado_mm")
CUTS=(50,100,150)
SEED=20261017

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text("utf8"))
def rows(p):
 with p.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def write_csv(p,values):
 with p.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(values)
def stats(rr):
 n=len(rr)
 if not n:return {"n":0,"mae_mm":None,"rmse_mm":None,"sesgo_mm":None}
 e=[float(r["estimado_mm"])-float(r["observado_mm"]) for r in rr]
 return {"n":n,"mae_mm":round(statistics.mean(abs(x) for x in e),4),
   "rmse_mm":round(math.sqrt(statistics.mean(x*x for x in e)),4),
   "sesgo_mm":round(statistics.mean(e),4)}
def by(rr,cols):
 g=defaultdict(list)
 for r in rr:g[tuple(r[c] for c in cols)].append(r)
 return [{**dict(zip(cols,k)),**stats(v)} for k,v in sorted(g.items())]
def rates(obs,pred,cut,threshold):
 tp=fp=tn=fn=0
 for y,p in zip(obs,pred):
  hit=y>=threshold;flag=p>=cut
  if hit and flag:tp+=1
  elif hit:fn+=1
  elif flag:fp+=1
  else:tn+=1
 precision=tp/(tp+fp) if tp+fp else 0.
 recall=tp/(tp+fn) if tp+fn else None
 fpr=fp/(fp+tn) if fp+tn else None
 beta2=4.
 f2=(1+beta2)*precision*recall/(beta2*precision+recall) if recall is not None and beta2*precision+recall else 0.
 csi=tp/(tp+fp+fn) if tp+fp+fn else None
 return {"n":len(obs),"eventos":tp+fn,"tp":tp,"fn":fn,"fp":fp,"tn":tn,
   "precision_pct":round(100*precision,2),
   "sensibilidad_pct":round(100*recall,2) if recall is not None else None,
   "fpr_pct":round(100*fpr,2) if fpr is not None else None,
   "f2":round(f2,5),"csi":round(csi,5) if csi is not None else None}
def tune(cal,threshold):
 obs=[float(r["observado_mm"]) for r in cal]
 pred=[float(r["estimado_mm"]) for r in cal]
 if sum(x>=threshold for x in obs)<10:
  return {"estado":"INSUFICIENTES_EVENTOS_CALIBRACION","umbral_predicho_mm":None,
    "n_eventos_calibracion":sum(x>=threshold for x in obs)}
 cands=[]
 # Conservative cap on FPR, defined a priori, and calibration only.
 for t in range(0,201,5):
  m=rates(obs,pred,t,threshold)
  if m["fpr_pct"] is not None and m["fpr_pct"]<=25:
   cands.append((m["f2"],-m["fpr_pct"],t))
 if not cands:return {"estado":"SIN_REGLA_ADMISIBLE","umbral_predicho_mm":None,
    "n_eventos_calibracion":sum(x>=threshold for x in obs)}
 score,minus_fpr,cut=max(cands)
 return {"estado":"CALIBRADA_EXPLORATORIA","umbral_predicho_mm":cut,
   "n_eventos_calibracion":sum(x>=threshold for x in obs),
   "f2_calibracion":score,"fpr_calibracion_pct":-minus_fpr}
def regimes():
 src=load(INDEX)
 values=src["datos"]
 expected={f"{y}-{m:02d}" for y in range(2021,2026) for m in range(1,13)}
 if set(values)!=expected:raise ValueError("RONI incompleto 2021-25")
 return {date:("RONI_calido_geq_0.5" if x>=0.5 else
               "RONI_frio_leq_-0.5" if x<=-0.5 else "RONI_neutro")
   for date,x in values.items()}
def block_ci(rr,model="gcn"):
 # Equal weighted five block averages of paired absolute-error differences.
 errs=defaultdict(list)
 vals=defaultdict(dict)
 for r in rr:
  if r["modelo"]!=model:continue
  key=(r["mes"],r["sector"])
  vals[key][r["brazo"]]=r
 for k,arm in vals.items():
  if set(arm)!=set(ARMS):raise ValueError("Falta comparación pareada")
  a=arm["lag1"];b=arm["lag2"]
  if abs(float(a["observado_mm"])-float(b["observado_mm"]))>0.01:
   raise ValueError("Observaciones no comparables")
  errs[int(a["bloque"])].append(abs(float(b["estimado_mm"])-float(b["observado_mm"]))-
     abs(float(a["estimado_mm"])-float(a["observado_mm"])))
 if set(errs)!=set(range(5)):raise ValueError("Faltan bloques espaciales")
 avg={k:statistics.mean(v) for k,v in errs.items()}
 boot=sorted(statistics.mean(avg[k] for k in sample)
   for sample in itertools.product(sorted(avg),repeat=5))
 def percentile(q):
  pos=q*(len(boot)-1);lo=math.floor(pos);hi=math.ceil(pos)
  return round(boot[lo]+(boot[hi]-boot[lo])*(pos-lo),4)
 return {"delta_mae_lag2_menos_lag1_mm":round(statistics.mean(avg.values()),4),
   "intervalo_95_exploratorio_mm":[percentile(.025),percentile(.975)],
   "bloques":5,"remuestreos":len(boot),
   "nota":"IC exploratorio con solo 5 bloques; no prueba independencia climática."}
def assess(allrows,meta):
 identity=set();pair=defaultdict(dict)
 for r in allrows:
  k=(r["brazo"],r["mes"],r["sector"],r["modelo"])
  if k in identity:raise ValueError("Duplicado")
  identity.add(k)
  pair[(r["mes"],r["sector"],r["modelo"])][r["brazo"]]=r
 if len(allrows)!=39*84*len(MODELS)*2 or len(pair)!=39*84*len(MODELS):
  raise ValueError("Faltan observaciones factoriales")
 for k,v in pair.items():
  if set(v)!=set(ARMS):raise ValueError("Falta brazo")
  if abs(float(v["lag1"]["observado_mm"])-float(v["lag2"]["observado_mm"]))>0.01:
   raise ValueError("Objetivo divergente entre brazos")
 cal=[r for r in allrows if "2019-01"<=r["mes"]<="2020-12"]
 te=[r for r in allrows if "2021-01"<=r["mes"]<="2025-12"]
 if len(cal)!=39*24*len(MODELS)*2 or len(te)!=39*60*len(MODELS)*2:
  raise ValueError("Calendario de calibración o prueba incorrecto")
 roni=regimes()
 enriched=[{**r,"anio":r["mes"][:4],"regimen_roni":roni[r["mes"]]} for r in te]
 metrics=by(enriched,("brazo","modelo"))
 annual=by(enriched,("brazo","modelo","anio"))
 floor=by(enriched,("brazo","modelo","piso"))
 regimes_metrics=by(enriched,("brazo","modelo","regimen_roni"))
 threshold_results=[]
 for arm in ARMS:
  for model in MODELS:
   train=[r for r in cal if r["brazo"]==arm and r["modelo"]==model]
   test=[r for r in enriched if r["brazo"]==arm and r["modelo"]==model]
   obs=[float(x["observado_mm"]) for x in test]
   pred=[float(x["estimado_mm"]) for x in test]
   for threshold in CUTS:
    base=rates(obs,pred,threshold,threshold)
    rule=tune(train,threshold)
    tuned=(rates(obs,pred,rule["umbral_predicho_mm"],threshold)
           if rule["umbral_predicho_mm"] is not None else None)
    threshold_results.append({"brazo":arm,"modelo":model,"umbral_evento_mm":threshold,
      "regla_original":base,"regla_calibrada":rule,"prueba_regla_calibrada":tuned})
 boot={m:block_ci(enriched,m) for m in ("random_forest","gcn")}
 # Aggregate objective count not number of independent storms.
 return {"fase":"10D","fecha_corte":"2026-10-17",
  "tipo":"FACTORIAL_RETROSPECTIVO_CONTRA_CHIRPS3_FINAL",
  "fuente_matriz_sha256":digest(core.SOURCE),
  "fuente_roni_sha256":digest(INDEX),
  "periodos":{"entrenamiento":"1997-01/2015-12","ajuste":"2016-01/2018-12",
    "calibracion_umbral":"2019-01/2020-12","prueba":"2021-01/2025-12"},
  "rezagos":{"lag1":[1,2,3,6,12],"lag2":[2,3,4,6,12]},
  "media_movil":{"lag1":[3,2,1],"lag2":[4,3,2]},
  "diseno":"Misma partición, arquitectura, hiperparámetros candidatos, semillas y ventanas en ambos brazos. Las decisiones de selección por brazo pueden diferir.",
  "modelos":list(MODELS),"n_sectores":39,"n_bloques":5,
  "n_predicciones_calibracion":len(cal),"n_predicciones_prueba":len(te),
  "mae_global":metrics,"mae_por_anio":annual,"mae_por_piso":floor,
  "mae_por_regimen_roni":regimes_metrics,
  "bootstrap_pareado_cinco_bloques":boot,
  "eventos":threshold_results,
  "nota_regimen":"RONI NOAA es indicador tropical relativo centrado y retrospectivo; no equivale a Niño costero ENFEN ni fue predictor.",
  "advertencias":["Entradas CHIRPS v3 FINAL compiladas posteriormente, NO vintages as-issued.",
   "Umbrales 50/100/150 mm mensuales exploratorios, NO niveles oficiales de alerta.",
   "Pisos agroclimáticos y bloques son exploratorios; falta validación instrumental independiente.",
   "Se optimizan reglas sobre 2019-2020 de sectores holdout: no equivale a calibración en zona sin historia local.",
   "Solo cinco bloques espaciales, con dependencia temporal y espacial; 2023 puede cambiar distribución.",
   "GCN es convolución en grafos, no CNN raster bidimensional."],
  "as_issued_certificado":False,"validacion_campo_independiente":False,
  "modelo_operativo_ganador":None,"alertas_habilitadas":False,
  "sha256_predicciones_factorial":digest(PRED)}
def run(check=False):
 if check:
  rep=load(REPORT);pred=rows(PRED)
  if rep["fase"]!="10D" or rep["alertas_habilitadas"] is not False or rep["modelo_operativo_ganador"] is not None:
   raise ValueError("Declaración operativa indebida")
  if rep["sha256_predicciones_factorial"]!=digest(PRED) or len(pred)!=rep["n_predicciones_calibracion"]+rep["n_predicciones_prueba"]:
   raise ValueError("Predicciones no coinciden con informe")
  if rep["n_predicciones_prueba"]!=14040 or rep["n_predicciones_calibracion"]!=5616:
   raise ValueError("Cobertura incompleta")
  return rep
 nodes,A,edges,fixed,floors,polygons,data,audit=core.inputs()
 pixels=core.raster_cells(nodes,polygons)
 folds=core.folds(nodes,polygons,pixels)
 archived=load(core.FOLDS)
 for k,held in folds.items():
  if sorted(held)!=sorted(archived["folds"][k]["sectores_holdout"]):
   raise ValueError("Los bloques difieren de 10C")
 X2,y,dates,tr,va,ca,te=core.features_matrix(nodes,fixed,data)
 X1,y1,dates1,_,_,_=lag1.features_matrix(nodes,fixed,data)
 if not np.array_equal(dates,dates1) or not np.array_equal(y,y1):
  raise ValueError("Las variables objetivo no coinciden")
 out=[]
 for fold,held in sorted(folds.items()):
  train=[i for i,s in enumerate(nodes) if s not in held]
  hold=[i for i,s in enumerate(nodes) if s in held]
  for arm,X in (("lag1",X1),("lag2",X2)):
   pred,info=core.fit_fold(X,y,dates,tr,va,ca|te,A,train,hold,floors,nodes,fold)
   truth=np.expm1(y[ca|te][:,hold])
   for ti,date in enumerate(dates[ca|te]):
    for j,idx in enumerate(hold):
     for model in MODELS:
      observed=round(float(truth[ti,j]),5)
      estimate=round(float(pred[model][ti,j]),5)
      if not math.isfinite(estimate) or estimate<0:
       raise ValueError("Pronóstico fuera del dominio")
      out.append({"brazo":arm,"mes":str(date),"sector":nodes[idx],
       "piso":floors[nodes[idx]],"bloque":fold,"modelo":model,
       "observado_mm":observed,"estimado_mm":estimate})
   print("10D",fold,arm,"rf_leaf",info["rf_leaf_selected"],"gcn_epoch",info["gcn_best_epoch"],flush=True)
 out.sort(key=lambda r:(r["mes"],r["sector"],r["modelo"],r["brazo"]))
 BASE.mkdir(parents=True,exist_ok=True)
 write_csv(PRED,out)
 rep=assess(out,{})
 REPORT.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("10D",json.dumps({"mae":rep["mae_global"],"eventos100":[v for v in rep["eventos"] if v["umbral_evento_mm"]==100],"alertas":False},ensure_ascii=False),flush=True)
 return rep
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true")
 run(check=parser.parse_args().check)
