#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9R — Random Forest vs Graph Convolutional Network (GCN).

Target: one-month-ahead CHIRPS-v3 FINAL *retrospective* monthly rain, 1996–2025.
Train: 1997–2015, tune: 2016–2020, held-out: 2021–2025.
NO climate future leakage in features, preprocessing, training climatology or model choice.
At t use only monthly rainfall t-1,t-2,t-3,t-6,t-12 plus month and fixed terrain.
Graph edges: elevation band + static ANA hydro unit + geometric proximity; no rainfall correlations.
The sectors and final-revised CHIRPS dataset, however, were compiled after test era:
this is historical simulation, NOT demonstrated as-issued operational skill.
"""
from __future__ import annotations
import csv,json,hashlib,math,random
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from shapely.geometry import shape
import torch
from torch import nn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/validacion_predictiva_9r"
FROM=[("9O","datos/homogeneidad_9o/fuentes_chirps_9o.json","fuentes","datos/homogeneidad_9o/serie_sectores_chirps_9o.csv"),
      ("9P","datos/continuidad_9p/fuentes_adicionales_chirps_9p.json","nuevos","datos/continuidad_9p/meses_adicionales_sectores_9p.csv"),
      ("9Q","datos/recuperacion_9q/fuentes_chirps_9q.json","nuevos","datos/recuperacion_9q/sectores_mensuales_9q.csv")]
GEO=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
HYDRO=ROOT/"datos/sensibilidad_9m/cruces_hidrograficos_9m.geojson"
GROUPS=ROOT/"datos/recuperacion_9q/agrupaciones_exploratorias_9q.geojson"
SOURCE=ROOT/"datos/recuperacion_9q/fuentes_chirps_9q.json"
RESULT=BASE/"comparacion_modelos_9r.json"
PRED=BASE/"predicciones_prueba_2021_2025_9r.csv"
MODELS=("Climatología","Random Forest","GCN")
SEED=20261017
N_FEATURES=11
TRAIN_RANGE=("1997-01","2015-12")
VAL_RANGE=("2016-01","2020-12")
TEST_RANGE=("2021-01","2025-12")
def read(path):
 return json.loads(path.read_text("utf8"))
def csvs(path):
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def hashfile(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def sources():
 months={}; data=defaultdict(dict)
 manifests={}
 for phase,manifest,ref,rawcsv in FROM:
  doc=read(ROOT/manifest)
  stage={i["mes"]:i["sha256"] for i in doc[ref]}
  if len(stage)!=len(doc[ref]) or set(stage)&set(months):
   raise ValueError("Mes CHIRPS duplicado o manifiesto inconsistente "+phase)
  months.update(stage)
  raw=csvs(ROOT/rawcsv)
  if len(raw)!=42*len(stage):raise ValueError("42 filas por mes necesarias "+phase)
  seen=set()
  for p in raw:
   m,s=p["mes"],p["sector"]
   if (m,s) in seen or m not in stage or p["sha256_tiff"]!=stage[m]:
    raise ValueError("Origen temporal SHA o duplicado "+phase)
   seen.add((m,s))
   if p["precipitacion_promedio_pixel_mm"]!="":
    v=float(p["precipitacion_promedio_pixel_mm"])
    if not np.isfinite(v) or v<0 or v>10000:raise ValueError("CHIRPS lluvia fuera de límites")
    data[s][m]=v
  manifests[phase]=len(stage)
 expected=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 if sorted(months)!=expected or len(months)!=360:
  raise ValueError("No se encuentran los 360 meses CHIRPS verdaderos")
 j=read(SOURCE)
 if j["n_meses_chirps_verificados"]!=360 or j["n_meses_no_comprobados"]!=0:
  raise ValueError("Validación 9Q de CHIRPS incompleta")
 return data,manifests
def static(data):
 sectors=read(GEO)["features"];hydro=read(HYDRO)["features"]
 by={i["properties"]["id_sector"]:i for i in sectors}
 nodes=[sid for sid in sorted(by) if len(data.get(sid,{}))==360]
 if len(sectors)!=42 or len(nodes)<30:
  raise ValueError("Menos de 30 sectores con 360 meses de lluvia CHIRPS")
 units=defaultdict(set)
 for feature in hydro:
  p=feature["properties"]
  units[p["sector_9k"]].add(p["codigo_referencial"])
 coords={sid:shape(by[sid]["geometry"]).centroid for sid in nodes}
 floor={sid:by[sid]["properties"]["estrato"] for sid in nodes}
 n=len(nodes);edges=[];adj=np.eye(n,dtype=np.float32)
 for a in range(n):
  for b in range(a+1,n):
   x,y=nodes[a],nodes[b]
   if floor[x]!=floor[y] or floor[x]=="cota_negativa_revisar":continue
   if not(units[x]&units[y]):continue
   # Static spatial topology only — no 9Q rainfall group labels or similarity results.
   if shape(by[x]["geometry"]).distance(shape(by[y]["geometry"]))>0.14:continue
   adj[a,b]=adj[b,a]=1.;edges.append([x,y])
 degree=adj.sum(axis=1)
 norm=adj/np.sqrt(degree[:,None]*degree[None,:])
 fixed=[]
 for sid in nodes:
  p=by[sid]["properties"]
  pt=coords[sid]
  elev=p.get("alt_min_nodos_m",None)
  lo=p.get("alt_max_nodos_m",None)
  elevation=0.5*(float(elev)+float(lo)) if elev is not None and lo is not None else 0.
  fixed.append([elevation/3000,(pt.x+79.8)/2,(pt.y+6.5)/2])
 return nodes,norm,edges,np.array(fixed,dtype="float32"),floor,by
def matrix(data,nodes,fixed):
 months=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 R=np.array([[data[sid][month] for sid in nodes] for month in months],dtype=np.float32)
 if R.shape!=(360,len(nodes)) or not np.isfinite(R).all():
  raise ValueError("Matriz CHIRPS 360 meses x N no válida")
 # Logs and lagged CHIRPS available by the END of preceding month:
 # Features at target t contain nothing from target or future.
 t=np.arange(12,360,dtype=np.int32)
 X=[];target=[]
 for k in t:
  month=(k%12)+1
  period=[np.log1p(R[k-lag]) for lag in (1,2,3,6,12)]
  rolling=[np.log1p(np.mean(R[k-3:k],axis=0))]
  static=np.broadcast_to(fixed,(len(nodes),3))
  seasonal=np.broadcast_to(np.array([math.sin(2*math.pi*month/12),
             math.cos(2*math.pi*month/12)],dtype=np.float32),(len(nodes),2))
  x=np.column_stack([*period,*rolling,seasonal[:,0],seasonal[:,1],static])
  if x.shape!=(len(nodes),N_FEATURES):raise ValueError("Características distintas de 11")
  X.append(x)
  target.append(np.log1p(R[k]))
 XX=np.stack(X).astype("float32");yy=np.stack(target).astype("float32")
 dates=np.array(months)[t]
 train=(dates>=TRAIN_RANGE[0])&(dates<=TRAIN_RANGE[1])
 val=(dates>=VAL_RANGE[0])&(dates<=VAL_RANGE[1])
 test=(dates>=TEST_RANGE[0])&(dates<=TEST_RANGE[1])
 if (train.sum(),val.sum(),test.sum())!=(228,60,60):
  raise ValueError("Split cronológico incorrecto")
 # baselines month/sector from targets on TRAIN only
 baseline=np.zeros((12,len(nodes)),dtype=np.float32)
 for m in range(12):
  idx=train&(t%12==m)
  baseline[m]=np.expm1(yy[idx]).mean(axis=0)
 if not np.all(np.isfinite(baseline)):raise ValueError("Baseline sin valores")
 # normalize features and log-target with only TRAIN observations
 mu=XX[train].reshape(-1,N_FEATURES).mean(axis=0)
 std=XX[train].reshape(-1,N_FEATURES).std(axis=0)
 std=np.where(std<1e-6,1.,std)
 xx=((XX-mu)/std).astype(np.float32)
 ym=float(yy[train].mean());ys=float(yy[train].std())
 return dates,xx,yy,train,val,test,baseline,ym,ys,{"mu":mu.tolist(),"std":std.tolist()}
def forest(X,y,tr,va,te,ym,ys):
 n=X.shape[1]
 xtr=X[tr].reshape(-1,N_FEATURES);ytr=y[tr].reshape(-1)
 xv=X[va].reshape(-1,N_FEATURES);yv=y[va].reshape(-1)
 choices=[]
 for leaf in (3,8):
  m=RandomForestRegressor(n_estimators=240,max_depth=15,min_samples_leaf=leaf,
     max_features=.85,n_jobs=2,random_state=SEED)
  m.fit(xtr,ytr)
  v=m.predict(xv).reshape(-1,n)
  mae=mean_absolute_error(np.expm1(yv),np.maximum(0,np.expm1(v.reshape(-1))))
  choices.append((mae,leaf,m))
 choices.sort(key=lambda x:(x[0],x[1]))
 best=choices[0]
 return best[2],best[2].predict(X[te].reshape(-1,N_FEATURES)).reshape(-1,n),{
   "candidate_min_samples_leaf":[3,8],"chosen_min_samples_leaf":best[1],
   "val_mae_mm":round(float(best[0]),4),
   "validation_candidates_mae_mm":{str(leaf):round(float(mae),4) for mae,leaf,_ in choices}}
class GCN(nn.Module):
 def __init__(self,features=11,hidden=40):
  super().__init__()
  self.layer1=nn.Linear(features,hidden)
  self.layer2=nn.Linear(hidden,hidden)
  self.residual=nn.Linear(features,hidden)
  self.head=nn.Sequential(nn.ReLU(),nn.Linear(hidden,1))
  self.dropout=nn.Dropout(.13)
 def forward(self,x,A):
  v=torch.einsum("ij,tjf->tif",A,x)
  h=torch.relu(self.layer1(v)+self.residual(x))
  h=self.dropout(h)
  h=torch.relu(self.layer2(torch.einsum("ij,tjf->tif",A,h)))
  h=self.dropout(h)
  return self.head(h).squeeze(-1)
def graph_net(X,y,tr,va,te,A,ym,ys):
 torch.set_num_threads(2)
 torch.manual_seed(SEED);np.random.seed(SEED);random.seed(SEED)
 model=GCN()
 adjacency=torch.tensor(A,dtype=torch.float32)
 tx=torch.tensor(X,dtype=torch.float32)
 ty=torch.tensor(y,dtype=torch.float32)
 opt=torch.optim.AdamW(model.parameters(),lr=.009,weight_decay=.004)
 best=None;best_mae=float("inf");epoch_best=0;patience=25
 for epoch in range(1,181):
  model.train()
  perm=torch.randperm(int(tr.sum()))
  ind=torch.tensor(np.where(tr)[0])
  for part in perm.split(32):
   rows=ind[part]
   out=model(tx[rows],adjacency)
   loss=nn.functional.smooth_l1_loss(out,ty[rows],beta=.8)
   opt.zero_grad();loss.backward()
   torch.nn.utils.clip_grad_norm_(model.parameters(),5.)
   opt.step()
  model.eval()
  with torch.no_grad():
   v=model(tx[torch.tensor(np.where(va)[0])],adjacency).numpy()
  mae=float(np.mean(np.abs(np.maximum(0,np.expm1(np.clip(v,-12,12)))-
                             np.expm1(y[va]))))
  if mae<best_mae-0.001:
   best_mae=mae;epoch_best=epoch
   best={k:t.detach().clone() for k,t in model.state_dict().items()}
  if epoch-epoch_best>=patience:break
 if best is None:raise ValueError("GCN no convergió")
 model.load_state_dict(best);model.eval()
 with torch.no_grad():
  out=model(tx[torch.tensor(np.where(te)[0])],adjacency).numpy()
 return out,{"best_epoch":epoch_best,"stop_epoch":epoch,"val_mae_mm":round(best_mae,4),
    "hidden_features":40,"graph_layers":2,"early_stopping_patience":patience,
    "library":"PyTorch GCN normalización D^-1/2 (A+I) D^-1/2, sin torch_geometric",
    "loss":"Huber log1p precipitación"}
def scores(y,p):
 y=np.array(y,dtype=float).flatten();p=np.array(p,dtype=float).flatten()
 if len(y)==0:return {"n":0,"mae_mm":None,"rmse_mm":None,"bias_mm":None}
 return {"n":len(y),"mae_mm":round(float(np.mean(np.abs(y-p))),4),
         "rmse_mm":round(float(np.sqrt(np.mean((y-p)**2))),4),
         "bias_mm":round(float(np.mean(p-y)),4)}
def compare():
 data,manifests=sources()
 nodes,A,edges,fixed,floors,geom=static(data)
 dates,X,y,tr,va,te,baseline,ym,ys,scaler=matrix(data,nodes,fixed)
 rf,rf_log,rfmeta=forest(X,y,tr,va,te,ym,ys)
 gc_log,gmeta=graph_net(X,y,tr,va,te,A,ym,ys)
 # Same log1p transformed response for both models; forecasts nonnegative mm
 truth=np.expm1(y[te]).astype("float64")
 rf_mm=np.maximum(0,np.expm1(np.clip(rf_log,-12,12)))
 gcn_mm=np.maximum(0,np.expm1(np.clip(gc_log,-12,12)))
 idxmonth=np.array([int(x[-2:])-1 for x in dates[te]])
 base=baseline[idxmonth]
 predictions={"Climatología":base,"Random Forest":rf_mm,"GCN":gcn_mm}
 overall={k:scores(truth,v) for k,v in predictions.items()}
 benchmark=overall["Climatología"]["mae_mm"]
 for value in overall.values():
  value["skill_mae_vs_climatologia_pct"]=round(100*(1-value["mae_mm"]/benchmark),3) if benchmark else None
 years=np.array([int(m[:4]) for m in dates[te]])
 # Estimate dependence: leave-one-test-year-out rather than fake independent p-values.
 yearly=[]
 for year in range(2021,2026):
  sub=years==year
  yearly.append({"year":year,"metrics":{k:scores(truth[sub],v[sub]) for k,v in predictions.items()}})
 loyo=[]
 for year in range(2021,2026):
  sub=years!=year
  rfmae=np.mean(np.abs(truth[sub]-predictions["Random Forest"][sub]))
  gcmae=np.mean(np.abs(truth[sub]-predictions["GCN"][sub]))
  loyo.append({"excluded_year":year,"rf_minus_gcn_mae_mm":round(float(rfmae-gcmae),4)})
 floorlist=sorted(set(floors.values()))
 byfloor={}
 for f in floorlist:
  indices=[i for i,node in enumerate(nodes) if floors[node]==f]
  byfloor[f]={"nodes":[nodes[i] for i in indices],
              "n_sector":len(indices),
              "metrics":{k:scores(truth[:,indices],v[:,indices]) for k,v in predictions.items()}}
 groups=read(GROUPS)["features"]
 bygroup={}
 for f in groups:
  members=f["properties"]["sectores"]
  valid=[nodes.index(s) for s in members if s in nodes]
  bygroup[f["properties"]["id"]]={"sectors":members,"n_evaluable":len(valid),
     "metrics":{k:scores(truth[:,valid],v[:,valid]) for k,v in predictions.items()} if valid else None}
 # Verification on wet anomalies, threshold derived strictly from TRAIN only.
 monthwise=np.zeros((12,len(nodes)))
 for m in range(12):
  sub=tr&(np.array([int(x[-2:])-1 for x in dates])==m)
  monthwise[m]=np.quantile(np.expm1(y[sub]),.8,axis=0)
 actual=truth>monthwise[idxmonth]
 anomaly={}
 for name,pred in predictions.items():
  detected=pred>monthwise[idxmonth]
  tp=int((actual&detected).sum());fp=int((~actual&detected).sum())
  fn=int((actual&~detected).sum())
  anomaly[name]={"train_monthly_p80_threshold":True,"n_true_anomaly":int(actual.sum()),
    "tp":tp,"fp":fp,"fn":fn,
    "precision":round(tp/(tp+fp),4) if tp+fp else None,
    "recall":round(tp/(tp+fn),4) if tp+fn else None,
    "f1":round(2*tp/(2*tp+fp+fn),4) if 2*tp+fp+fn else None}
 rows=[]
 for m,yy0,b0,rf0,g0 in zip(dates[te],truth,base,rf_mm,gcn_mm):
  for i,sid in enumerate(nodes):
   rows.append({"mes_objetivo":str(m),"sector":sid,"piso":floors[sid],
    "lluvia_observada_CHIRPS_mm":round(float(yy0[i]),4),
    "climatologia_entrenamiento_mm":round(float(b0[i]),4),
    "random_forest_mm":round(float(rf0[i]),4),"gcn_mm":round(float(g0[i]),4)})
 winner=min(overall,key=lambda m:overall[m]["mae_mm"])
 winner_ml=min(("Random Forest","GCN"),key=lambda m:overall[m]["mae_mm"])
 out={"fase":"9R","fecha_corte":"2026-10-17",
      "objetivo":"Lluvia mensual del mes siguiente por sector, CHIRPS v3 final, hindcast pseudo-prospectivo",
      "variables_disponibles_al_mes_previo":["CHIRPS lluvia meses -1,-2,-3,-6,-12",
           "promedio de meses -1 a -3","seno/coseno del mes objetivo",
           "altitud del nodo, latitud y longitud estáticas 9K"],
      "variables_EXCLUIDAS_por_fuga_temporal":["normales ERA5 1996-2025",
          "familias 9Q basadas en precipitación 2021-2025","lluvia CHIRPS del mes objetivo",
          "series de sensores no archivadas ex-ante","temperatura,HR,radiación contemporáneas del mes objetivo"],
      "conjuntos":{"train":"1997-01 a 2015-12",
          "validacion":"2016-01 a 2020-12",
          "prueba_fuera_muestra":"2021-01 a 2025-12",
          "n_meses_entrenamiento":int(tr.sum()),"n_meses_validacion":int(va.sum()),
          "n_meses_prueba":int(te.sum()),"horizonte_meses":1,
          "mes_objetivo_desconocido_para_predictor":True,
          "serie_final_CHIRPS_revisada_a_posteriori":True},
      "origen_CHIRPS":{
          "meses_verificados":360,"periodo":"1996-2025","fase_origen":manifests,
          "fuente_manifest_sha256":hashfile(SOURCE),
          "sin_pluviometros_independientes":True},
      "grafo":{"n_nodos_con_lluvia_valida":len(nodes),
          "sectores_descartados":[i for i in sorted(geom) if i not in nodes],
          "n_aristas_no_dirigidas":len(edges),"aristas_estaticas":edges,
          "adyacencia":"misma banda altitudinal + código hidrográfico ANA/IDEP + distancia <=0.14°",
          "construccion_sin_series_CHIRPS_de_entrenamiento_o_prueba":True,
          "sin_cuartos_pisos_ecologicos_oficiales":True},
      "modelo_RF":rfmeta,"modelo_GCN":gmeta,
      "metricas_prueba":overall,
      "mejor_modelo_ml_por_mae":winner_ml,
      "mejor_modelo_incluyendo_baseline_por_mae":winner,
      "comparacion_por_piso_altitudinal":byfloor,
      "comparacion_por_grupo_exploratorio_9q":bygroup,
      "metricas_por_anio_test":yearly,
      "sensibilidad_cinco_anios_test_leave_one_year_out":loyo,
      "anomalia_lluvia_muy_alta_umbral_percentil80_train":anomaly,
      "n_predicciones_sector_mes_prueba":len(rows),
      "n_zonas_homogeneas_certificadas":0,
      "n_modelos_operativamente_validados":0,
      "alertas_fitosanitarias_emitidas":False,
      "pronostico_2026_comprobado":False,
      "limitaciones":[
         "Se predice lluvia CHIRPS FINAL reanalizada, no cantidades medidas en pluviómetros independientes.",
         "La serie CHIRPS FINAL para t-1 fue revisada a posteriori y pudo no estar disponible exactamente en la fecha original; simulación histórica no vintage emitido.",
         "La propia geometría sectorial exploratoria y el grafo se construyeron después del periodo de prueba: el ensayo no es backtest operacional puramente ex-ante.",
         "Un único bloque de prueba 2021-2025 contiene pocos años de El Niño intenso y extremos; no extrapolar habilidad a nuevos eventos.",
         "Sectores próximos pueden compartir orígenes satelitales y de estaciones: 39 nodos no son 39 réplicas independientes.",
         "Se pronostica un solo mes por paso con lluvia pasada efectivamente observada; no se valida pronóstico a tres/seis meses.",
         "No incorporar los sectores sin píxel CHIRPS ni reclamar capacidad en todos los pisos o agrupaciones.",
         "Una victoria en MAE no garantiza mayor acierto de lluvia extrema; contrastar RMSE, recall y baseline.",
         "No hay umbrales de fitopatología/arándano/vid ni validación SENAMHI para este modelo."
      ]}
 return out,rows

def main(check=False):
 if check:
  result=read(RESULT)
  if result["fase"]!="9R" or result["n_modelos_operativamente_validados"]!=0:
   raise ValueError("9R status/no-certificación erróneo")
  if result["n_predicciones_sector_mes_prueba"]!=len(csvs(PRED)):
   raise ValueError("N de predicciones prueba distinto de registros")
  if result["conjuntos"]["n_meses_prueba"]!=60 or result["conjuntos"]["n_meses_entrenamiento"]!=228:
   raise ValueError("Fechas de prueba modificadas")
  print("9R check:",result["metricas_prueba"])
  return result
 torch.use_deterministic_algorithms(True)
 np.random.seed(SEED);random.seed(SEED);torch.manual_seed(SEED)
 output,rows=compare()
 BASE.mkdir(parents=True,exist_ok=True)
 RESULT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n","utf8")
 with PRED.open("w",newline="",encoding="utf8") as f:
  fields=list(rows[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print("9R result:",json.dumps(output["metricas_prueba"],ensure_ascii=False),
       "winner ML:",output["mejor_modelo_ml_por_mae"],flush=True)
 return output

if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 main(check=p.parse_args().check)
