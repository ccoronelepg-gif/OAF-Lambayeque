#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10F: 39-sector CHIRPS probability RF vs GCN with delayed regional ocean indices.
ALL results are retrospective research, not 'as-issued' forecasts or official alerts.
ERA5 local temperature/radiation/humidity/wind from just 4 cities MUST NOT be
copied to 39 polygons; this module only uses temporally delayed regional signals.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,random,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch
from torch import nn
import reentrenamiento_lag2_10c as previous
import probabilidad_multivariable_10e as clf
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/extension_10f"
REPORT=BASE/"evaluacion_39_sectores_10f.json"
PRED=BASE/"probabilidades_39_sectores_10f.csv"
LAND=ROOT/"datos/integracion_8v/matriz_terrestre_8v.csv"
SOI=ROOT/"datos/noaa_cpc_predictores_atmosfericos_8b.csv"
MAR=ROOT/"datos/integracion_8v/matriz_marina_8v.csv"
RONI=ROOT/"datos/experimentos_10d/roni_noaa_2021_2025.json"
FOLDS=ROOT/"datos/reentrenamiento_10c/bloques_geograficos_10c.json"
SEED=20261017
NAMES=("climatologia_sector_estacional","RF_lluvia","GCN_lluvia","RF_lluvia_oceano","GCN_lluvia_oceano")
FIELDNAMES=("mes","sector","piso","bloque","modelo","evento_p90","observado_mm","umbral_p90_mm","probabilidad")
COV_NAMES=("nino12_anom_t2","nino34_anom_t2","soi_t2","alisios_central_t2",
           "alisios_oriental_t2","viento_marino_pimentel_t2","viento_marino_norte_t2")
TRAIN=("1997-01","2015-12");VAL=("2016-01","2018-12")
CAL=("2019-01","2020-12");TEST=("2021-01","2025-12")
torch.set_num_threads(2)
def read(p):
 with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text("utf8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(v,name):
 x=float(v)
 if not math.isfinite(x):raise ValueError("Non-finite "+name)
 return x
def auxiliary(months):
 """Global regional ocean/atmosphere from shared NOAA and two distinct SEA cells.
 None of these series are a coastal station / local sector observation."""
 land=[r for r in read(LAND) if r["localidad"]=="Chiclayo"]
 ocean={r["mes"]:r for r in land}
 soi={r["mes"]:r for r in read(SOI)}
 marine=defaultdict(dict)
 for r in read(MAR):marine[r["mes"]][r["punto_viento"]]=r
 if len(ocean)!=360 or any(len(marine[m])!=2 for m in months):
  raise ValueError("Regional ocean archive incomplete")
 out=[]
 for month in months:
  if month not in soi or month not in ocean:raise ValueError("Missing regional data "+month)
  l=ocean[month];s=soi[month];m=marine[month]
  if set(m)!={"Mar_frente_Pimentel","Mar_norte_Lambayeque"}:raise ValueError("Marine source locations changed")
  out.append([finite(l["anomalia_nino12_c"],"SST 1+2"),
    finite(l["anomalia_nino34_c"],"SST 3.4"),
    finite(s["soi_estandarizado"],"SOI"),
    finite(s["alisios_pacifico_central"],"central trade winds"),
    finite(s["alisios_pacifico_oriental"],"east trade winds"),
    finite(m["Mar_frente_Pimentel"]["viento_10m_m_s"],"marine wind Pimentel"),
    finite(m["Mar_norte_Lambayeque"]["viento_10m_m_s"],"marine wind north")])
 return np.asarray(out,dtype=np.float32)
def matrix(nodes,fixed,data):
 X,ylog,dates,tr,va,ca,te=previous.features_matrix(nodes,fixed,data)
 months=[f"{year}-{mon:02d}" for year in range(1996,2026) for mon in range(1,13)]
 regional=auxiliary(months)
 delayed=regional[np.arange(12,360)-2]
 extra=np.repeat(delayed[:,None,:],len(nodes),axis=1)
 mixed=np.concatenate((X,extra),axis=-1)
 if X.shape!=(348,39,11) or mixed.shape!=(348,39,18):
  raise ValueError("Unexpected sector feature matrix")
 raw=np.expm1(ylog)
 thresholds=np.quantile(raw[tr],.90,axis=0) # historical 1997–2015 ONLY
 if np.any(thresholds<=0):raise ValueError("Degenerate sector P90")
 Y=(raw>=thresholds[None,:]).astype(np.float32)
 return X,mixed,Y,raw,thresholds,dates,tr,va,ca,te
def enrich(X,raw):
 a=(raw>0).astype(np.float32)
 np.fill_diagonal(a,0.)
 counts=a.sum(axis=1)
 weights=a/np.maximum(1,counts[:,None])
 # same neighbor signal family for RF and GCN, rain lags only
 neighbor=np.stack([np.einsum("ij,tj->ti",weights,X[:,:,k]) for k in (0,2,4)],axis=-1)
 for idx in range(len(counts)):
  if counts[idx]==0:neighbor[:,idx,:]=X[:,idx,:][:,[0,2,4]]
 degree=np.broadcast_to((counts/8).reshape(1,len(counts),1),(len(X),len(counts),1))
 return np.concatenate((X,neighbor,degree),axis=-1).astype(np.float32)
def gcn(Xtrain,Ytrain,Xhold,Atrain,Ahold,tr,va,seed):
 torch.manual_seed(seed);np.random.seed(seed);random.seed(seed)
 mu=Xtrain[tr].mean(axis=(0,1))
 sd=Xtrain[tr].std(axis=(0,1));sd=np.where(sd<1e-5,1.,sd)
 xt=torch.tensor((Xtrain-mu)/sd,dtype=torch.float32)
 xh=torch.tensor((Xhold-mu)/sd,dtype=torch.float32)
 yy=torch.tensor(Ytrain,dtype=torch.float32)
 at=torch.tensor(Atrain,dtype=torch.float32)
 ah=torch.tensor(Ahold,dtype=torch.float32)
 model=clf.GCN(Xtrain.shape[-1])
 positives=float(Ytrain[tr].mean())
 positive_weight=torch.tensor(min(6.,max(1.,math.sqrt((1-positives)/max(.0001,positives)))))
 optimizer=torch.optim.AdamW(model.parameters(),lr=.007,weight_decay=.008)
 train_ids=np.flatnonzero(tr);val_ids=np.flatnonzero(va)
 best_loss=float("inf");best_epoch=0;weights=None
 for epoch in range(1,151):
  model.train()
  for pack in torch.randperm(len(train_ids)).split(32):
   indexes=torch.tensor(train_ids[pack],dtype=torch.long)
   logits=model(xt[indexes],at)
   loss=nn.functional.binary_cross_entropy_with_logits(logits,yy[indexes],pos_weight=positive_weight)
   optimizer.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),4.);optimizer.step()
  model.eval()
  with torch.no_grad():
   prob=torch.sigmoid(model(xt[val_ids],at)).numpy()
  value=float(np.mean((prob-Ytrain[va])**2))
  if value<best_loss-1e-5:
   best_loss=value;best_epoch=epoch
   weights={key:v.detach().clone() for key,v in model.state_dict().items()}
  if epoch-best_epoch>=18:break
 if weights is None:raise ValueError("No checkpoint GCN")
 model.load_state_dict(weights);model.eval()
 with torch.no_grad():
  p=torch.sigmoid(model(xh,ah)).numpy()
 return p,{"brier_validacion":round(best_loss,6),"mejor_epoca":best_epoch,"epoca_parada":epoch}
def forest(Xtr,Ytr,Xho,tr,va,seed):
 from sklearn.ensemble import RandomForestClassifier
 variants=[]
 for leaf in (4,9):
  m=RandomForestClassifier(n_estimators=150,min_samples_leaf=leaf,
     max_depth=14,max_features=.85,random_state=seed,
     class_weight="balanced_subsample",n_jobs=2)
  m.fit(Xtr[tr].reshape(-1,Xtr.shape[-1]),Ytr[tr].reshape(-1))
  prob=m.predict_proba(Xtr[va].reshape(-1,Xtr.shape[-1]))[:,1]
  b=float(np.mean((prob-Ytr[va].reshape(-1))**2))
  variants.append((b,leaf,m))
 best=min(variants,key=lambda x:x[0])
 p=best[2].predict_proba(Xho.reshape(-1,Xho.shape[-1]))[:,1].reshape(Xho.shape[:2])
 return p,{"brier_validacion":round(best[0],6),"min_samples_leaf":best[1]}
def baseline(Y,tr,dates,held):
 result=np.zeros((len(dates),len(held)),dtype=np.float32)
 months=np.array([int(v[-2:]) for v in dates])
 for j,sector_idx in enumerate(held):
  # Existing local 1997–2015 records may define local event normal/reference
  # even in holdout; NO label from this sector is used to tune RF/GCN.
  for month in range(1,13):
   mask=tr&(months==month)
   rate=(float(Y[mask,sector_idx].sum())+1)/(mask.sum()+10)
   result[months==month,j]=rate
 return result
def regime(date,roni):
 value=float(roni[date])
 return "calido_RONI" if value>=.5 else "frio_RONI" if value<=-.5 else "neutro_RONI"
def evaluate(pred):
 def metrics(rows):
  y=[int(r["evento_p90"]) for r in rows]
  p=[float(r["probabilidad"]) for r in rows]
  return clf.score(y,p)
 def group(fields,eligible=pred):
  d=defaultdict(list)
  for r in eligible:d[tuple(r[k] for k in fields)].append(r)
  return [{**dict(zip(fields,key)),**metrics(v)} for key,v in sorted(d.items())]
 roni=load(RONI)["datos"]
 for r in pred:
  r["anio"]=r["mes"][:4];r["regimen_roni"]=regime(r["mes"],roni)
 # Spatial dependency => exploratory block bootstrap (only 5 blocks).
 data=defaultdict(dict)
 for r in pred:data[(r["mes"],r["sector"])][r["modelo"]]=r
 byyear=defaultdict(list)
 for key,items in data.items():
  if set(items)!=set(NAMES):raise ValueError("Not paired by sector/month")
  byyear[key[0][:4]].append(items)
 bs={}
 for a,b in (("RF_lluvia_oceano","GCN_lluvia_oceano"),
             ("RF_lluvia_oceano","climatologia_sector_estacional"),
             ("RF_lluvia_oceano","RF_lluvia"),
             ("GCN_lluvia_oceano","GCN_lluvia")):
  deltas={}
  for year,rs in byyear.items():
   deltas[year]=statistics.mean((float(r[a]["probabilidad"])-int(r[a]["evento_p90"]))**2-
      (float(r[b]["probabilidad"])-int(r[b]["evento_p90"]))**2 for r in rs)
  bs[a+"_menos_"+b]={"delta_brier":round(statistics.mean(deltas.values()),6),
    "por_anio":{y:round(v,6) for y,v in sorted(deltas.items())},
    "advertencia":"Cinco años, correlación por sector; descriptivo y NO intervalo confirmatorio"}
 global_metrics=group(("modelo",))
 rank=sorted((r for r in global_metrics if r["modelo"]!="climatologia_sector_estacional"),
  key=lambda x:x["brier"])
 ref=next(r for r in global_metrics if r["modelo"]=="climatologia_sector_estacional")
 best=rank[0] if rank else None
 recommend=(best["modelo"] if best and best["brier"]<ref["brier"] and
            best["pr_auc"] is not None and best["pr_auc"]>ref["pr_auc"] and best["eventos"]>=15 else None)
 return {"global":global_metrics,"por_ano":group(("modelo","anio")),
  "por_piso":group(("modelo","piso")),"por_bloque":group(("modelo","bloque")),
  "por_regimen_roni":group(("modelo","regimen_roni")),
  "por_piso_2023":group(("modelo","piso"),[r for r in pred if r["anio"]=="2023"]),
  "comparaciones_temporales":bs,"ranking_ia_por_brier":rank,
  "modelo_ia_destacado_si_supera_climatologia":recommend}
def main(check=False):
 if check:
  d=load(REPORT);rows=read(PRED)
  if d["fase"]!="10F" or len(rows)!=11700 or d["sha256_predicciones"]!=sha(PRED):
   raise ValueError("10F corrupted or incomplete")
  if d["modelo_operativo_ganador"] is not None or d["alertas_habilitadas"] is not False:
   raise ValueError("Not permitted for operations")
  return d
 nodes,A,edges,fixed,floors,polygons,data,audit=previous.inputs()
 pixel=previous.raster_cells(nodes,polygons)
 partitions=previous.folds(nodes,polygons,pixel)
 old=load(FOLDS)
 for k in range(5):
  if sorted(partitions[k])!=sorted(old["folds"][k]["sectores_holdout"]):
   raise ValueError("Spatial blocks changed")
 X0,X1,Y,rain,thresholds,dates,tr,va,ca,te=matrix(nodes,fixed,data)
 records=[];meta=[]
 for k,held_sectors in sorted(partitions.items()):
  hold=[i for i,s in enumerate(nodes) if s in held_sectors]
  train=[i for i,s in enumerate(nodes) if s not in held_sectors]
  Atr,raw_tr=previous.subgraph(A,train)
  Aho,raw_ho=previous.subgraph(A,hold)
  predictions={"climatologia_sector_estacional":baseline(Y,tr,dates,hold)}
  settings={}
  for variant,xx in (("lluvia",X0),("lluvia_oceano",X1)):
   xt=enrich(xx[:,train,:],raw_tr)
   xh=enrich(xx[:,hold,:],raw_ho)
   rf,rfinfo=forest(xt,Y[:,train],xh,tr,va,SEED+k)
   gc,gcinfo=gcn(xt,Y[:,train],xh,Atr,Aho,tr,va,SEED+k)
   for model,prediction in (("RF_"+variant,rf),("GCN_"+variant,gc)):
    calibrated,cal_info=clf.platt(prediction,Y[:,hold],{"calibracion":ca})
    # clf.platt expects prediction for ALL dates, Y with same node axis.
    predictions[model]=calibrated
    settings[model]={"rf":rfinfo if model.startswith("RF") else None,
       "gcn":gcinfo if model.startswith("GCN") else None,"calibration":cal_info}
  for ti,month in enumerate(dates):
   if not te[ti]:continue
   for j,idx in enumerate(hold):
    for model in NAMES:
     p=float(predictions[model][ti,j])
     if not math.isfinite(p) or not 0<=p<=1:raise ValueError("Probability out of bounds")
     records.append({"mes":str(month),"sector":nodes[idx],"piso":floors[nodes[idx]],
       "bloque":k,"modelo":model,"evento_p90":int(Y[ti,idx]),
       "observado_mm":round(float(rain[ti,idx]),5),
       "umbral_p90_mm":round(float(thresholds[idx]),5),"probabilidad":round(p,6)})
  meta.append({"bloque":k,"sectores_holdout":held_sectors,
    "train_nodes":len(train),"holdout_nodes":len(hold),
    "hiperparametros_y_calibracion":settings})
  print("10F bloque",k,"holdout",len(hold),flush=True)
 if len(records)!=39*60*len(NAMES):raise ValueError("Missing test rows")
 records.sort(key=lambda r:(r["mes"],r["sector"],r["modelo"]))
 BASE.mkdir(parents=True,exist_ok=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  writer=csv.DictWriter(f,fieldnames=FIELDNAMES);writer.writeheader();writer.writerows(records)
 metrics=evaluate(records)
 report={"fase":"10F","fecha_corte":"2026-10-17",
  "objetivo":"Probabilidad de exceder P90 lluvia mensual CHIRPS histórico POR SECTOR, referencia 1997–2015",
  "n_sectores":39,"n_bloques_geograficos":5,"n_predicciones_prueba":len(records),
  "n_sector_mes_objetivo":39*60,
  "n_modelos":len(NAMES),"p90_referencia":"1997-01/2015-12 solo CHIRPS del sector",
  "uso_historia_holdout":"Normal P90 y climatologia usan observaciones históricas anteriores a 2016 del sector reservado; NO en ajuste RF/GCN",
  "periodos":{"entrenamiento":TRAIN,"ajuste":VAL,"calibracion_platt":CAL,"prueba":TEST},
  "predictoras_rainfall_t2mas":["precipitacion_t2","precipitacion_t3","precipitacion_t4",
    "precipitacion_t6","precipitacion_t12","media_lluvia_t2t4","estacionalidad","atributos_geograficos"],
  "predictoras_regionales_t2":list(COV_NAMES),
  "regionales_mismas_en_los_39_sectores":True,
  "covariables_locales_39_sectores_ausentes":["temperatura_aire","radiacion_solar",
    "humedad_vpd","viento_local_homologado"],
  "corrientes_marinas_incluidas":False,
  "razon":"Corrientes geostroficas solo 2017–2025 y sin co-localización con puntos terrestres; no imputar",
  "fuentes_sha256":{str(p.relative_to(ROOT)):sha(p) for p in (previous.SOURCE,LAND,SOI,MAR,RONI)},
  "evaluacion":metrics,"folds":meta,
  "verificacion_instrumental_independiente":False,
  "instantaneas_as_issued":False,
  "modelo_operativo_ganador":None,"alertas_habilitadas":False,
  "limitaciones":[
    "NO reconstruye temperaturas, humedad, radiacion ni viento local para los 39 sectores.",
    "NO usa corrientes marinas sin datos historicos completos e iguales unidades de soporte.",
    "CHIRPS v3 FINAL fue reprocesado historicamente: no constituye as-issued.",
    "NOAA regional Niño1+2/3.4 y viento marino NO equivalen a SST y viento de cada poligono.",
    "SOI y SST regional históricas revisadas, con t−2 para evitar mes objetivo.",
    "P90 por sector calculado de historia CHIRPS incluso para sector holdout; se permite climatologia local histórica, no etiquetas objetivo del periodo de prueba.",
    "La calibracion Platt del holdout usa 2019–2020: no es extrapolacion a un lugar SIN registros previos.",
    "Ensayo binario de precipitacion elevada NO estima evento ENFEN ni infecciones fitosanitarias.",
    "Estratos altitudinales preliminares, cota_negativa_revisar pendiente.",
    "Con cinco pliegues y sesenta meses, no hay garantía de habilidad prospectiva ni intervalos confirmatorios.",
    "Uso investigativo; publicar todas las métricas y comparación con climatología, cero alertas."
  ]}
 report["sha256_predicciones"]=sha(PRED)
 REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("10F_RESULTADOS",json.dumps({"global":metrics["global"],
  "ranking":metrics["ranking_ia_por_brier"],
  "destacado":metrics["modelo_ia_destacado_si_supera_climatologia"],
  "casos":report["n_sector_mes_objetivo"],"alertas":False},ensure_ascii=False),flush=True)
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 main(check=a.check)
