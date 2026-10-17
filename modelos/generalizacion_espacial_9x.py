#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9X: inductive spatial-block validation on archived OAF CHIRPS data.

Five spatial folds are based ONLY on geographic centroids (not rainfall).
Time: fit 1997–2015; tune/stopping 2016–2020; predict 2021–2025.
No held-out sector target from any year can enter model fitting or validation.
Lagged history of a held-out sector IS permitted at prediction time: this is
transfer of a fitted forecasting relationship, not zero-data extrapolation.
All rainfall uses CHIRPS v3 FINAL compiled retrospectively (not as-issued).
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,random,statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from shapely.geometry import shape,Point
import torch
from torch import nn

import comparacion_gcn_rf_9r as nine_r

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/generalizacion_9x"
SOURCE=ROOT/"datos/validacion_9w/matriz_sectores_chirps_9w.csv"
AUDIT=ROOT/"datos/validacion_9w/auditoria_puente_9w.json"
REPORT=BASE/"evaluacion_bloques_espaciales_9x.json"
PRED=BASE/"predicciones_sector_bloque_9x.csv"
FOLDS=BASE/"bloques_geograficos_9x.json"
SEED=20261017
FEAT=15
N_FOLDS=5
TRAIN=("1997-01","2015-12")
VAL=("2016-01","2020-12")
TEST=("2021-01","2025-12")
MODELS=("climatologia_global","climatologia_piso","persistencia_anual","random_forest","gcn")
CSV_COLUMNS=("mes","anio","sector","piso","bloque","modelo","observado_CHIRPS_mm","predicho_mm")
torch.set_num_threads(2)

def obj(path):return json.loads(path.read_text("utf8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csvread(path):
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def writecsv(path,data,fields):
 with path.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)

def inputs():
 m=obj(AUDIT)
 if m.get("fase")!="9W" or sha(SOURCE)!=m.get("sha256_matriz_nueva"):
  raise ValueError("La fuente de 9W perdió trazabilidad SHA256")
 raw=csvread(SOURCE)
 if len(raw)!=39*360:raise ValueError("9W no contiene 39 x 360 meses")
 data=defaultdict(dict)
 for row in raw:
  v=float(row["lluvia_mm"])
  if not math.isfinite(v) or v<0:raise ValueError("Lluvia nula, negativa o no finita")
  if row["mes"] in data[row["sector_id"]]:raise ValueError("Mes duplicado")
  data[row["sector_id"]][row["mes"]]=v
 nodes,A,edges,fixed,floors,features=nine_r.static(data)
 if len(nodes)!=39 or any(len(data[n])!=360 for n in nodes):
  raise ValueError("No hay 39 series completas de CHIRPS")
 return nodes,np.array(A,dtype=np.float32),edges,np.array(fixed,dtype=np.float32),floors,features,data,m

def raster_cells(nodes,polygons):
 # Index of native CHIRPS 0.05° cell centres; source transform frozen in 9O.
 t=obj(ROOT/"datos/homogeneidad_9o/fuentes_chirps_9o.json")["fuentes"][0]["raster_transform"]
 xres,yres,x0,y0=map(float,t)
 per={}
 for sid in nodes:
  region=shape(polygons[sid]["geometry"])
  mi,ma,bo,to=region.bounds
  xmin=max(0,math.floor((mi-x0)/xres)-2)
  xmax=min(300,math.ceil((ma-x0)/xres)+2)
  ymin=max(0,math.floor((to-y0)/yres)-2)
  ymax=min(300,math.ceil((bo-y0)/yres)+2)
  cells=set()
  for col in range(xmin,xmax+1):
   for row in range(ymin,ymax+1):
    c=(x0+(col+.5)*xres,y0+(row+.5)*yres)
    if region.contains(Point(*c)):cells.add((row,col))
  if not cells:raise ValueError("Sector sin píxel CHIRPS propio: "+sid)
  per[sid]=cells
 return per

def folds(nodes,polygons,per):
 # The entire fold is a spatial block; KMeans sees lat/long only.
 pts=np.array([[shape(polygons[s]["geometry"]).centroid.x,
                shape(polygons[s]["geometry"]).centroid.y] for s in nodes])
 labels=KMeans(n_clusters=N_FOLDS,n_init=20,random_state=SEED).fit_predict(pts)
 partitions={i:sorted(nodes[k] for k,l in enumerate(labels) if l==i) for i in range(N_FOLDS)}
 if not all(3<=len(p)<=15 for p in partitions.values()):
  raise ValueError("Bloques geográficos desbalanceados")
 overlap=[]
 for i in range(N_FOLDS):
  for j in range(i+1,N_FOLDS):
   cells_i=set().union(*(per[s] for s in partitions[i]))
   cells_j=set().union(*(per[s] for s in partitions[j]))
   shared=cells_i&cells_j
   if shared:overlap.append({"i":i,"j":j,"n":len(shared)})
 if overlap:
  # No ocultar fugas de pixeles; bloqueo estricto.
  raise ValueError("Píxeles CHIRPS compartidos entre pliegues: "+str(overlap))
 return partitions

def features_matrix(nodes,fixed,data):
 months=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 rainfall=np.array([[data[s][m] for s in nodes] for m in months],dtype=np.float32)
 if rainfall.shape!=(360,39) or not np.isfinite(rainfall).all():raise ValueError("Grilla fuente CHIRPS irregular")
 time_indices=np.arange(12,360)
 feats=[]
 for idx in time_indices:
  mm=idx%12+1
  lag=[np.log1p(rainfall[idx-k]) for k in (1,2,3,6,12)]
  rolling=np.log1p(rainfall[idx-3:idx].mean(axis=0))
  sin=np.full(len(nodes),math.sin(2*math.pi*mm/12),dtype=np.float32)
  cos=np.full(len(nodes),math.cos(2*math.pi*mm/12),dtype=np.float32)
  static=fixed
  feats.append(np.column_stack([*lag,rolling,sin,cos,static.T]).astype(np.float32))
 X=np.stack(feats)
 y=np.log1p(rainfall[time_indices])
 dates=np.array(months)[time_indices]
 tr=(dates>=TRAIN[0])&(dates<=TRAIN[1])
 va=(dates>=VAL[0])&(dates<=VAL[1])
 te=(dates>=TEST[0])&(dates<=TEST[1])
 if (int(tr.sum()),int(va.sum()),int(te.sum()))!=(228,60,60):
  raise ValueError("Cortes temporales inesperados")
 return X,y,dates,tr,va,te

def subgraph(A,idx):
 raw=(A[np.ix_(idx,idx)]>0).astype(np.float32)
 np.fill_diagonal(raw,1.)
 degree=raw.sum(axis=1)
 norm=raw/np.sqrt(degree[:,None]*degree[None,:])
 return norm,raw

def enrich(X,raw):
 # RF and GCN get the SAME 15 predictors: 11 local and 3 means of
 # neighbours' lagged rainfall + static degree. ONLY nodes in this fold's
 # subgraph can be neighbours. No targets of the predicted month are used.
 n=X.shape[1]
 if n!=raw.shape[0]:raise ValueError("Adyacencia de otra partición")
 a=raw.copy()
 np.fill_diagonal(a,0.)
 degree=a.sum(axis=1)
 mean=a/np.where(degree[:,None]>0,degree[:,None],1.)
 neigh=np.stack([np.einsum("ij,tj->ti",mean,X[:,:,k]) for k in (0,2,4)],axis=-1)
 for i in range(n):
  if degree[i]==0:neigh[:,i,:]=X[:,i,[0,2,4]].T
 de=np.broadcast_to((degree/8).reshape(1,n,1),(len(X),n,1))
 enriched=np.concatenate((X,neigh,de),axis=2).astype(np.float32)
 if enriched.shape[-1]!=FEAT:raise ValueError("Dimensión features inesperada")
 return enriched

def scale(trainX,allX):
 vals=trainX.reshape(-1,trainX.shape[-1])
 mu=vals.mean(axis=0);std=vals.std(axis=0)
 std=np.where(std<1e-6,1.,std)
 return ((allX-mu)/std).astype(np.float32),mu,std

def baseline(y,tr,months,trainidx,testidx,floors,nodes):
 # Baselines are derived entirely from labels in TRAIN sectors, TRAIN dates.
 actual=np.expm1(y[tr][:,trainidx])
 mon=np.array([int(m[-2:])-1 for m in months[tr]])
 byglobal={m:float(actual[mon==m].mean()) for m in range(12)}
 byfloor={}
 fallback=set()
 for fl in set(floors.values()):
  matched=[k for k,i in enumerate(trainidx) if floors[nodes[i]]==fl]
  if matched:
   for m in range(12):
    byfloor[(fl,m)]=float(actual[mon==m][:,matched].mean())
  else:fallback.add(fl)
 months_target=np.array([int(m[-2:])-1 for m in months])
 global_pred=np.array([[byglobal[m] for _ in testidx] for m in months_target])
 floor_pred=np.array([[byfloor.get((floors[nodes[i]],m),byglobal[m]) for i in testidx]
                       for m in months_target])
 return global_pred,floor_pred,sorted(fallback)

def fit_fold(X,y,dates,tr,va,te,A,trainidx,holdidx,floors,nodes,fold):
 Atrain,rawtrain=subgraph(A,trainidx)
 Ahold,rawhold=subgraph(A,holdidx)
 exTrain=enrich(X[:,trainidx,:],rawtrain)
 exTest=enrich(X[:,holdidx,:],rawhold)
 mu=exTrain[tr].reshape(-1,FEAT).mean(axis=0)
 std=exTrain[tr].reshape(-1,FEAT).std(axis=0)
 std=np.where(std<1e-6,1.,std)
 exTrain=((exTrain-mu)/std).astype(np.float32)
 exTest=((exTest-mu)/std).astype(np.float32)
 y_train=y[:,trainidx]
 rfmeta=[]
 rfbest=None
 for leaf in (3,8):
  rf=RandomForestRegressor(n_estimators=160,min_samples_leaf=leaf,
     max_features=.85,max_depth=15,random_state=SEED+fold,n_jobs=2)
  rf.fit(exTrain[tr].reshape(-1,FEAT),y_train[tr].reshape(-1))
  pred=rf.predict(exTrain[va].reshape(-1,FEAT)).reshape(va.sum(),len(trainidx))
  val_mae=float(np.abs(np.maximum(0,np.expm1(np.clip(pred,-12,12)))-
                          np.expm1(y_train[va])).mean())
  rfmeta.append({"leaf":leaf,"validation_mae_mm":round(val_mae,4)})
  if rfbest is None or val_mae<rfbest[0]:rfbest=(val_mae,leaf,rf)
 rf_pred=rfbest[2].predict(exTest[te].reshape(-1,FEAT)).reshape(te.sum(),len(holdidx))
 rf_mm=np.maximum(0,np.expm1(np.clip(rf_pred,-12,12)))
 # Train GCN in an induced graph with ZERO held-out nodes/targets.
 torch.manual_seed(SEED+fold);np.random.seed(SEED+fold);random.seed(SEED+fold)
 model=nine_r.GCN(features=FEAT,hidden=32)
 aTrain=torch.tensor(Atrain,dtype=torch.float32)
 aHold=torch.tensor(Ahold,dtype=torch.float32)
 tX=torch.tensor(exTrain,dtype=torch.float32)
 tY=torch.tensor(y_train,dtype=torch.float32)
 opt=torch.optim.AdamW(model.parameters(),lr=.009,weight_decay=.004)
 train_ids=torch.tensor(np.flatnonzero(tr),dtype=torch.long)
 val_ids=torch.tensor(np.flatnonzero(va),dtype=torch.long)
 best_epoch=0;best_mae=float("inf");weights=None
 for epoch in range(1,121):
  model.train()
  order=torch.randperm(len(train_ids))
  for p in order.split(32):
   ids=train_ids[p];output=model(tX[ids],aTrain)
   loss=nn.functional.smooth_l1_loss(output,tY[ids],beta=.8)
   opt.zero_grad();loss.backward()
   torch.nn.utils.clip_grad_norm_(model.parameters(),5.)
   opt.step()
  model.eval()
  with torch.no_grad():
   yp=model(tX[val_ids],aTrain).numpy()
  val_mm=np.maximum(0,np.expm1(np.clip(yp,-12,12)))
  err=float(np.mean(np.abs(val_mm-np.expm1(y_train[va]))))
  if err<best_mae-.001:
   best_mae=err;best_epoch=epoch
   weights={k:v.detach().clone() for k,v in model.state_dict().items()}
  if epoch-best_epoch>=18:break
 if weights is None:raise ValueError("GCN no optimizó validación dentro del bloque")
 model.load_state_dict(weights);model.eval()
 with torch.no_grad():
  gcn_raw=model(torch.tensor(exTest[te],dtype=torch.float32),aHold).numpy()
 gcn_mm=np.maximum(0,np.expm1(np.clip(gcn_raw,-12,12)))
 globals_,floors_,missing=baseline(y,tr,dates,trainidx,holdidx,floors,nodes)
 persist=np.expm1(X[te][:,holdidx,4])
 predictions={
   "climatologia_global":globals_[te],
   "climatologia_piso":floors_[te],
   "persistencia_anual":persist,
   "random_forest":rf_mm,
   "gcn":gcn_mm}
 if any(np.shape(v)!=(te.sum(),len(holdidx)) for v in predictions.values()):
  raise ValueError("Predicciones cambian dimensionalidad")
 return predictions,{"rf_validation_candidates":rfmeta,
   "rf_leaf_selected":rfbest[1],
   "gcn_best_epoch":best_epoch,"gcn_stopped_epoch":epoch,
   "gcn_validation_mae_mm":round(best_mae,4),
   "n_aristas_intra_entrenamiento":int((rawtrain.sum()-len(trainidx))/2),
   "n_aristas_intra_test":int((rawhold.sum()-len(holdidx))/2),
   "pisos_sin_testigo_en_entrenamiento":missing,
   "holdout_excluded_from_train_and_validation_targets":True,
   "sector_holdout_lags_used_only_at_inference":True}

def stats(vals):
 if not vals:return None
 errs=[p-o for o,p in vals]
 return {"n":len(errs),"mae_mm":round(float(statistics.mean(abs(v) for v in errs)),4),
    "rmse_mm":round(float(math.sqrt(statistics.mean(v*v for v in errs))),4),
    "sesgo_mm":round(float(statistics.mean(errs)),4)}

def bootstrap_folds(rows,ma,mb):
 # Spatial block bootstrap over ONLY 5 heldout geographic blocks.
 # Does not confer independence to spatially correlated CHIRPS pixels.
 blocks=sorted({int(r["bloque"]) for r in rows})
 loss=defaultdict(list)
 for r in rows:
  loss[(int(r["bloque"]),r["modelo"])].append(abs(float(r["predicho_mm"])-float(r["observado_CHIRPS_mm"])))
 avg={k:statistics.mean(v) for k,v in loss.items()}
 differences=[]
 for selection in __import__("itertools").product(blocks,repeat=len(blocks)):
  differences.append(statistics.mean(avg[(k,ma)]-avg[(k,mb)] for k in selection))
 differences.sort()
 def percentile(q):
  pos=q*(len(differences)-1);low=math.floor(pos);up=math.ceil(pos)
  return round(differences[low]+(differences[up]-differences[low])*(pos-low),4)
 return {"delta_mae_mm_positivo_es_peor":round(statistics.mean(avg[(k,ma)]-avg[(k,mb)] for k in blocks),4),
   "rango_bootstrap_espacial_exploratorio_95_pct_mm":[percentile(.025),percentile(.975)],
   "n_bloques_geograficos":len(blocks),"remuestras_exactas":len(differences),
   "basado_en_medias_igualmente_ponderadas_por_bloque":True}

def run(check=False):
 if check:
  d=obj(REPORT);f=obj(FOLDS);r=csvread(PRED)
  if d["fase"]!="9X" or f["fase"]!="9X":raise ValueError("Datos 9X inválidos")
  if d["n_predicciones_sector_mes_por_modelo"]!=39*60:raise ValueError("Cobertura prueba parcial")
  if len(r)!=39*60*len(MODELS):raise ValueError("Resultados incompletos")
  if d["sha256_serie_9w"]!=sha(SOURCE):raise ValueError("La serie 9W cambió")
  if d["n_modelos_operativos_autorizados"]!=0 or d["validacion_SENAMHI_externa"]:
   raise ValueError("Afirmación indebida de validación")
  return d
 nodes,A,edges,fixed,floors,polygons,data,prior=inputs()
 pix=raster_cells(nodes,polygons)
 partitions=folds(nodes,polygons,pix)
 X,y,dates,tr,va,te=features_matrix(nodes,fixed,data)
 out=[]
 meta=[]
 for k in sorted(partitions):
  held=partitions[k]
  train=[i for i,s in enumerate(nodes) if s not in held]
  test=[i for i,s in enumerate(nodes) if s in held]
  predictions,details=fit_fold(X,y,dates,tr,va,te,A,train,test,floors,nodes,k)
  truth=np.expm1(y[te][:,test])
  for date_idx,month in enumerate(dates[te]):
   for j,i in enumerate(test):
    sid=nodes[i];obs=float(truth[date_idx,j])
    for model,v in predictions.items():
     pred=float(v[date_idx,j])
     if not math.isfinite(pred) or pred<0:raise ValueError("Predicción fuera de rango")
     out.append({"mes":month,"anio":int(month[:4]),"sector":sid,"piso":floors[sid],
       "bloque":k,"modelo":model,"observado_CHIRPS_mm":round(obs,5),
       "predicho_mm":round(pred,5)})
  meta.append({"id":k,"sectores_holdout":held,"n_sectores_holdout":len(held),
    "sectores_train":[nodes[i] for i in train],
    "n_sectores_train":len(train),"n_celdas_CHIRPS_holdout":len(set().union(*(pix[s] for s in held))),
    **details})
  print("9X bloque",k,"holdout",len(held),"RF leaf",details["rf_leaf_selected"],
    "GCN epoch",details["gcn_best_epoch"],flush=True)
 # 5-fold coverage only heldout months; each sector in test exactly once.
 keys={(r["mes"],r["sector"],r["modelo"]) for r in out}
 if len(keys)!=len(out) or len(out)!=39*60*len(MODELS):
  raise ValueError("Hay duplicados o faltan casos en los cinco bloques")
 overall={m:stats([(float(r["observado_CHIRPS_mm"]),float(r["predicho_mm"]))
   for r in out if r["modelo"]==m]) for m in MODELS}
 baseline=overall["climatologia_piso"]["mae_mm"]
 skill={m:round(100*(1-overall[m]["mae_mm"]/baseline),3) for m in MODELS}
 byfloor=[]
 for fl in sorted(set(floors.values())):
  for m in MODELS:
   entries=[r for r in out if r["piso"]==fl and r["modelo"]==m]
   byfloor.append({"piso":fl,"modelo":m,**stats([(float(x["observado_CHIRPS_mm"]),float(x["predicho_mm"])) for x in entries])})
 byyear=[]
 for year in range(2021,2026):
  for m in MODELS:
   entries=[r for r in out if int(r["anio"])==year and r["modelo"]==m]
   byyear.append({"anio":year,"modelo":m,**stats([(float(x["observado_CHIRPS_mm"]),float(x["predicho_mm"])) for x in entries])})
 boots={}
 for a,b in (("random_forest","climatologia_piso"),("gcn","climatologia_piso"),("gcn","random_forest")):
  boots[a+"_menos_"+b]=bootstrap_folds(out,a,b)
 out.sort(key=lambda r:(r["mes"],r["sector"],r["modelo"]))
 BASE.mkdir(parents=True,exist_ok=True)
 writecsv(PRED,out,CSV_COLUMNS)
 foldreport={"fase":"9X","semilla":SEED,
  "tipo_bloque":"k-means estático de centroides SIG, 5 bloques, CHIRPS píxel sin intersección entre bloques",
  "n_folds":N_FOLDS,"folds":meta,"n_pixeles_compartidos_entre_bloques":0,
  "n_datos_de_lluvia_de_sectores_holdout_usados_para_fit":0,
  "fecha_prueba":"2021-01/2025-12","fecha_entrenamiento":"1997-01/2015-12",
  "fecha_validacion":"2016-01/2020-12",
  "uso_rezagos_holdout":"solo como predictores del mes posterior, no para entrenamiento",
  "zonas_homogeneas_certificadas":0}
 FOLDS.write_text(json.dumps(foldreport,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 report={"fase":"9X","fecha_corte":"2026-10-17",
  "objetivo":"Transferencia espacial de modelo entrenado en sectores ajenos, lluvia mensual CHIRPS final",
  "periodo_referencia":"1996-2025","n_sectores":39,"n_bloques":N_FOLDS,
  "n_predicciones_sector_mes_por_modelo":39*60,
  "n_predicciones_totales":len(out),
  "periodo_train":"1997-01/2015-12","periodo_validacion":"2016-01/2020-12",
  "periodo_test":"2021-01/2025-12",
  "modelos":list(MODELS),
  "metricas_globales":overall,"skill_MAE_vs_climatologia_piso_pct":skill,
  "ganador_por_mae_descriptivo":min(MODELS,key=lambda m:overall[m]["mae_mm"]),
  "metricas_por_piso":byfloor,"metricas_por_anio":byyear,
  "bootstrap_espacial_bloques":boots,
  "sha256_serie_9w":sha(SOURCE),
  "sha256_geometrias":sha(nine_r.GEO),
  "sha256_predicciones_9x":sha(PRED),
  "climatologia_entrenada_solo_en_otros_sectores":True,
  "normalizadores_entrenados_solo_en_otros_sectores_y_anios_train":True,
  "seleccion_hiperparametros_solo_en_otros_sectores_y_anios_validacion":True,
  "grafo_gcn_inductivo_entrenado_solo_con_nodos_train":True,
  "features_vecinales_RF_GCN_iguales_y_solo_rezagos":True,
  "sectores_holdout_con_lags_anteriores_disponibles_a_inferencia":True,
  "GCN_grafos_no_CNN_2D":True,
  "comparable_directamente_con_9R_por_metricas":False,
  "tampoco_habilidad_2026_prospectiva":True,
  "version_original_as_issued_CHIRPS_no_conservada":True,
  "n_modelos_operativos_autorizados":0,
  "validacion_SENAMHI_externa":False,
  "n_zonas_homogeneas_certificadas":0,
  "alertas_fitosanitarias_activadas":False,
  "limitaciones":[
   "Las fuentes CHIRPS v3 finales compiladas en 2026 incluyen estimaciones y pluviómetros; no archivos disponibles en la fecha de emisión histórica.",
   "Los sectores del mapa de 9K son geometrías exploratorias realizadas después del período de prueba.",
   "La evaluación espacial usa lag de lluvia histórica del sector reservado, aunque jamás usa su lluvia objetivo para entrenar; no equivale a pronóstico sin ninguna historia local.",
   "K-means sobre centroides forma bloques reproducibles pero no reemplaza cuencas oficiales ni elimina autocorrelación atmosférica regional.",
   "Se evita celda CHIRPS compartida en bloques, pero eso no garantiza independencia instrumental o ausencia de influencia espacial.",
   "Cinco bloques espaciales y cinco años de prueba dan incertidumbre sustancial, particularmente en montaña.",
   "El MAE 9X NO puede compararse directamente con el 9R: este último entrenó en las mismas ubicaciones que probó.",
   "La GCN usa convolución de grafo; no se ha entrenado CNN regular 2D sobre imágenes CHIRPS.",
   "No hay pluviómetros independientes con serie 1996–2025 para certificar habilidad en Lambayeque.",
   "No se ha hecho verificación prospectiva ni se emiten alertas de arándano, vid o El Niño." ]}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("9X",json.dumps({"mae":{m:overall[m]["mae_mm"] for m in MODELS},
   "winner":report["ganador_por_mae_descriptivo"],"n":len(out)},ensure_ascii=False),flush=True)
 return report

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 run(check=p.parse_args().check)
