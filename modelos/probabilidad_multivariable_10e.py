#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10E - independent author's multivariable PROBABILISTIC benchmark.
4 reanalysis localities ONLY (not 39 CHIRPS sectors). Data are ex-post
reprocessed. Not an issued forecast nor official warning. Zero alerts.
"""
from __future__ import annotations
import csv,json,hashlib,math,random,statistics,argparse
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss,average_precision_score,roc_auc_score,
                             log_loss,precision_score,recall_score)
import torch
from torch import nn

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/probabilidades_10e"
LAND=ROOT/"datos/integracion_8v/matriz_terrestre_8v.csv"
HUM=ROOT/"datos/humedad_8z/humedad_vpd_mensual_8z.csv"
MAR=ROOT/"datos/integracion_8v/matriz_marina_8v.csv"
SOI=ROOT/"datos/noaa_cpc_predictores_atmosfericos_8b.csv"
CURRENT=ROOT/"datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv"
REPORT=BASE/"evaluacion_probabilistica_10e.json"
PRED=BASE/"predicciones_probabilisticas_10e.csv"
LOCALITIES=("Chiclayo","Jayanca","Motupe","Olmos")
SEED=20261017
TRAIN=("1997-01","2015-12")
TUNE=("2016-01","2018-12")
CAL=("2019-01","2020-12")
TEST=("2021-01","2025-12")
MODEL_NAMES=("RF_multivariable","GCN_multivariable","RF_solo_lluvia","GCN_solo_lluvia","climatologia_local_estacional")
FIELDS=("mes","localidad","modelo","evento_p90","probabilidad","lluvia_observada_mm","umbral_p90_local_mm","lluvia_ge1000_revisar")
torch.set_num_threads(2)

def read(path):
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def obj(path):return json.loads(path.read_text("utf8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def required_float(v,col):
 x=float(v)
 if not math.isfinite(x):raise ValueError("Dato no finito "+col)
 return x
def get_data():
 ld=read(LAND);hu=read(HUM);ma=read(MAR);so=read(SOI)
 lm={(r["mes"],r["localidad"]):r for r in ld}
 hm={(r["mes"],r["localidad"]):r for r in hu}
 sm={r["mes"]:r for r in so}
 marine=defaultdict(list)
 for r in ma:marine[r["mes"]].append(r)
 months=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 if len(lm)!=1440 or len(hm)!=1440 or len(ma)!=720 or len(sm)<360:
  raise ValueError("Matrices climáticas incompletas o duplicadas")
 series={}; flagged=[]
 for i,loc in enumerate(LOCALITIES):
  entries=[]
  for month in months:
   k=(month,loc)
   if k not in lm or k not in hm or len(marine[month])!=2 or month not in sm:
    raise ValueError("Inconsistencia temporal "+str(k))
   l,h,o=lm[k],hm[k],sm[month]
   def lf(c):return required_float(l[c],"land:"+c)
   def hf(c):return required_float(h[c],"humidity:"+c)
   def sf(c):return required_float(o[c],"soi:"+c)
   mr=marine[month]
   vals={
    "rain":lf("precipitacion_mes_mm"),"t":lf("temperatura_aire_c"),
    "rad":lf("radiacion_mes_mj_m2"),"wind":lf("viento_10m_m_s"),
    "u":lf("viento_u_aprox_m_s"),"v":lf("viento_v_aprox_m_s"),
    "rh":hf("rh_2m_media_pct"),"vpd":hf("vpd_max_diario_media_mes_kpa"),
    "sst12":lf("anomalia_nino12_c"),"sst34":lf("anomalia_nino34_c"),
    "soi":sf("soi_estandarizado"),"trades_east":sf("alisios_pacifico_oriental"),
    "mar_wind":statistics.mean(float(r["viento_10m_m_s"]) for r in mr),
    "lat":lf("celda_viento_lat"),"lon":lf("celda_viento_lon"),
    "flag":str(l["lluvia_modelada_ge_1000_mm_revisar"]).strip().lower()=="true"
   }
   if vals["rain"]<0 or vals["rad"]<0 or vals["wind"]<0 or not (0<=vals["rh"]<=100):
    raise ValueError("Valores físicos fuera de dominio "+str(k))
   if vals["flag"] or vals["rain"]>=1000:flagged.append({"mes":month,"localidad":loc,"lluvia_mm":vals["rain"]})
   entries.append(vals)
  series[loc]=entries
 return months,series,flagged
def design(months,series):
 # Array t=12..359 includes lagged inputs of at least TWO completed months.
 dates=months[12:];n=len(dates)
 columns=("lluvia_t2","lluvia_t3","lluvia_t6","lluvia_t12","lluvia_media_t2t4",
  "temperatura_t2","radiacion_t2","viento_t2","viento_u_t2","viento_v_t2",
  "humedad_t2","vpd_t2","anomalia_nino12_t2","anomalia_nino34_t2",
  "soi_t2","alisios_orientales_t2","viento_marino_t2",
  "latitud","longitud","mes_seno","mes_coseno","id_Chiclayo","id_Jayanca","id_Motupe","id_Olmos")
 X=np.zeros((n,4,len(columns)),dtype=np.float32)
 rain=np.zeros((n,4),dtype=np.float32)
 bad=np.zeros((n,4),dtype=bool)
 for j,loc in enumerate(LOCALITIES):
  r=series[loc]
  for z,idx in enumerate(range(12,360)):
   a=r[idx-2]; m=int(months[idx][5:7])
   X[z,j]=[
    *[math.log1p(r[idx-lag]["rain"]) for lag in (2,3,6,12)],
    math.log1p(sum(r[idx-lag]["rain"] for lag in (2,3,4))/3),
    a["t"],a["rad"],a["wind"],a["u"],a["v"],a["rh"],a["vpd"],
    a["sst12"],a["sst34"],a["soi"],a["trades_east"],a["mar_wind"],
    a["lat"],a["lon"],math.sin(2*math.pi*m/12),math.cos(2*math.pi*m/12),
    *[float(j==i) for i in range(4)]]
   rain[z,j]=r[idx]["rain"]
   bad[z,j]=r[idx]["flag"] or r[idx]["rain"]>=1000
 if not np.isfinite(X).all() or not np.isfinite(rain).all():raise ValueError("Matriz no finita")
 masks={name:np.array([lo<=d<=hi for d in dates]) for name,(lo,hi) in [
   ("entrenamiento",TRAIN),("ajuste",TUNE),("calibracion",CAL),("prueba",TEST)]}
 if [int(m.sum()) for m in masks.values()]!=[228,36,24,60]:raise ValueError("Split temporal alterado")
 # Per-locality 90th percentile of TRAIN ONLY. These thresholds are not official.
 thr=np.quantile(rain[masks["entrenamiento"]],0.9,axis=0)
 Y=(rain>=thr[None,:]).astype(np.float32)
 return dates,X,Y,rain,bad,thr,masks,columns

def adjacency():
 # 4 ERA5 locality grids sorted north to south; static, no rain correlations.
 A=np.eye(4,dtype=np.float32)
 for i in range(3):A[i,i+1]=A[i+1,i]=1.
 degree=A.sum(axis=1)
 return A/np.sqrt(degree[:,None]*degree[None,:])
class GCN(nn.Module):
 def __init__(self,n_features):
  super().__init__()
  self.in_proj=nn.Linear(n_features,24)
  self.res=nn.Linear(n_features,24)
  self.hidden=nn.Linear(24,16)
  self.head=nn.Linear(16,1)
 def forward(self,x,A):
  h=torch.relu(self.in_proj(torch.einsum("ij,tjf->tif",A,x))+self.res(x))
  h=torch.relu(self.hidden(torch.einsum("ij,tjf->tif",A,h)))
  return self.head(h).squeeze(-1)
def enrich(X,adj):
 # RF and GCN receive identical feature channels, including neighbors' lags.
 raw=(adj>0).astype(np.float32);np.fill_diagonal(raw,0.)
 raw/=np.maximum(1,raw.sum(axis=1,keepdims=True))
 neigh=np.einsum("ij,tjf->tif",raw,X[:,:,:5])
 return np.concatenate([X,neigh],axis=-1)
def gcn_fit(X,Y,masks,arm):
 torch.manual_seed(SEED+arm);np.random.seed(SEED+arm);random.seed(SEED+arm)
 a=torch.tensor(adjacency(),dtype=torch.float32)
 mu=X[masks["entrenamiento"]].mean(axis=(0,1))
 sd=X[masks["entrenamiento"]].std(axis=(0,1))
 sd=np.where(sd<1e-6,1.,sd)
 xx=(X-mu[None,None,:])/sd[None,None,:]
 tx=torch.tensor(xx,dtype=torch.float32)
 yy=torch.tensor(Y,dtype=torch.float32)
 tr=np.flatnonzero(masks["entrenamiento"])
 va=np.flatnonzero(masks["ajuste"])
 model=GCN(X.shape[-1]);opt=torch.optim.AdamW(model.parameters(),lr=.007,weight_decay=.008)
 freq=Y[masks["entrenamiento"]].mean()
 weight=torch.tensor(float(min(5.,max(1.,math.sqrt((1-freq)/max(.0001,freq))))),dtype=torch.float32)
 best=float("inf");best_weights=None;best_epoch=0
 for epoch in range(1,161):
  model.train()
  perm=torch.randperm(len(tr))
  for indices in perm.split(32):
   ix=torch.tensor(tr[indices],dtype=torch.long)
   logit=model(tx[ix],a)
   loss=nn.functional.binary_cross_entropy_with_logits(logit,yy[ix],pos_weight=weight)
   opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),4.);opt.step()
  model.eval()
  with torch.no_grad():
   p=torch.sigmoid(model(tx[va],a)).numpy().reshape(-1)
  score=float(brier_score_loss(Y[masks["ajuste"]].reshape(-1),p))
  if score<best-1e-5:
   best=score;best_epoch=epoch
   best_weights={k:v.detach().clone() for k,v in model.state_dict().items()}
  if epoch-best_epoch>=20:break
 model.load_state_dict(best_weights);model.eval()
 with torch.no_grad():
  out=torch.sigmoid(model(tx,a)).numpy()
 return out,{"brier_ajuste":round(best,5),"epoch":best_epoch,"parada":epoch}
def rf_fit(X,Y,masks):
 tr=masks["entrenamiento"];va=masks["ajuste"]
 best=None
 for leaf in (4,9,18):
  model=RandomForestClassifier(n_estimators=180,min_samples_leaf=leaf,
   max_depth=12,max_features=.85,random_state=SEED,n_jobs=2,
   class_weight="balanced_subsample")
  model.fit(X[tr].reshape(-1,X.shape[-1]),Y[tr].reshape(-1))
  p=model.predict_proba(X[va].reshape(-1,X.shape[-1]))[:,1]
  b=float(brier_score_loss(Y[va].reshape(-1),p))
  if best is None or b<best[0]:best=(b,leaf,model)
 p=best[2].predict_proba(X.reshape(-1,X.shape[-1]))[:,1].reshape(Y.shape)
 return p,{"brier_ajuste":round(best[0],5),"hoja":best[1]}
def platt(pred,Y,masks):
 ca=masks["calibracion"];pc=np.clip(pred[ca].reshape(-1),.001,.999)
 yy=Y[ca].reshape(-1)
 if len(np.unique(yy))<2:return pred,{"estado":"sin_dos_clases","n_eventos_cal":int(yy.sum())}
 logit=np.log(pc/(1-pc)).reshape(-1,1)
 cal=LogisticRegression(C=1.,solver="lbfgs",max_iter=500,random_state=SEED)
 cal.fit(logit,yy)
 all_p=np.clip(pred.reshape(-1),.001,.999)
 probs=cal.predict_proba(np.log(all_p/(1-all_p)).reshape(-1,1))[:,1].reshape(pred.shape)
 return probs,{"estado":"ajuste_platt_calibracion_independiente","n_eventos_cal":int(yy.sum()),
  "coeficiente":round(float(cal.coef_[0,0]),5),
  "intercepto":round(float(cal.intercept_[0]),5)}
def baseline(Y,dates,masks):
 # Laplace shrinkage seasonal, each site independently, TRAIN ONLY.
 out=np.zeros_like(Y)
 m=np.array([int(d[-2:]) for d in dates])
 train=masks["entrenamiento"]
 for month in range(1,13):
  mask=train & (m==month)
  priors=(Y[mask].sum(axis=0)+1.)/(mask.sum()+10.)
  out[m==month]=priors
 return out
def score(y,p):
 y=np.asarray(y).astype(int).ravel()
 p=np.asarray(p,dtype=float).ravel()
 n=len(y);pos=int(y.sum())
 return {"n":n,"eventos":pos,"prevalencia_pct":round(100*pos/n,2),
  "brier":round(float(brier_score_loss(y,p)),6),
  "logloss":round(float(log_loss(y,p,labels=[0,1])),6),
  "pr_auc":round(float(average_precision_score(y,p)),5) if pos else None,
  "roc_auc":round(float(roc_auc_score(y,p)),5) if 0<pos<n else None}
def decision_threshold(p,y,mask):
 a=p[mask].reshape(-1);b=y[mask].reshape(-1).astype(int)
 choices=[]
 for t in np.linspace(.05,.95,19):
  yp=a>=t
  tp=int(((yp==1)&(b==1)).sum())
  fp=int(((yp==1)&(b==0)).sum())
  fn=int(((yp==0)&(b==1)).sum())
  tn=int(((yp==0)&(b==0)).sum())
  fpr=fp/(fp+tn) if fp+tn else 0.
  prec=tp/(tp+fp) if tp+fp else 0.
  rec=tp/(tp+fn) if tp+fn else 0.
  f2=5*prec*rec/(4*prec+rec) if 4*prec+rec else 0.
  if fpr<=.25:choices.append((f2,-fpr,float(t)))
 if not choices:return None
 return max(choices)[2]
def confusion(y,p,t):
 x=np.asarray(y).astype(bool).ravel();f=np.asarray(p).ravel()>=t
 tp=int(np.sum(x&f));fn=int(np.sum(x&~f));fp=int(np.sum(~x&f));tn=int(np.sum(~x&~f))
 return {"tp":tp,"fn":fn,"fp":fp,"tn":tn,
  "sensibilidad_pct":round(100*tp/(tp+fn),2) if tp+fn else None,
  "precision_pct":round(100*tp/(tp+fp),2) if tp+fp else None,
  "fpr_pct":round(100*fp/(fp+tn),2) if fp+tn else None}
def main(check=False):
 if check:
  r=obj(REPORT);p=read(PRED)
  if len(p)!=1200 or r["alertas_habilitadas"] is not False or r["modelo_operativo_certificado"] is not None:
   raise ValueError("Invariante 10E rota")
  if digest(PRED)!=r["sha256_predicciones"]:raise ValueError("Hash de salida inválido")
  return r
 months,data,flags=get_data()
 dates,X,Y,rain,bad,thr,masks,columns=design(months,data)
 for c in (LAND,HUM,MAR,SOI):
  if not c.is_file():raise ValueError("Fuente faltante")
 A=adjacency()
 full=enrich(X,A)
 # rainfall-only uses rainfall and seasonal location features plus neighbor rainfall
 subset=[0,1,2,3,4,19,20,21,22,23,24]
 rain_only=enrich(X[:,:,subset],A)
 probs={}
 metadata={}
 for arm,Z in (("multivariable",full),("solo_lluvia",rain_only)):
  pf,mrf=rf_fit(Z,Y,masks)
  pg,mg=gcn_fit(Z,Y,masks,0 if arm=="multivariable" else 1)
  for prefix,pp,info in (("RF",pf,mrf),("GCN",pg,mg)):
   name=prefix+"_"+arm
   cal,diag=platt(pp,Y,masks)
   probs[name]=cal;metadata[name]={"entrenamiento":info,"calibracion":diag}
  print("10E entrenado",arm,metadata["RF_"+arm],metadata["GCN_"+arm],flush=True)
 probs["climatologia_local_estacional"]=baseline(Y,dates,masks)
 test=masks["prueba"];ca=masks["calibracion"]
 results={}
 for name,p in probs.items():
  t=decision_threshold(p,Y,ca)
  test_rows=Y[test];test_prob=p[test]
  results[name]={"global":score(test_rows,test_prob),
   "por_localidad":{loc:score(Y[test,j],p[test,j]) for j,loc in enumerate(LOCALITIES)},
   "por_anio":{str(year):score(Y[np.array([d[:4]==str(year) for d in dates]),:]
                  ,p[np.array([d[:4]==str(year) for d in dates]),:])
     for year in range(2021,2026)},
   "corte_probabilistico_calibrado":round(t,3) if t is not None else None,
   "deteccion_2021_2025":confusion(test_rows,test_prob,t) if t is not None else None,
   "ajuste":metadata.get(name,{"metodo":"climatologia_entrenada_solo_hasta_2015"})}
 # honest decision protocol: exploratory only, no operational model.
 ordered=sorted((name for name in MODEL_NAMES if name!="climatologia_local_estacional"),
  key=lambda m:results[m]["global"]["brier"])
 base=results["climatologia_local_estacional"]["global"]
 best=ordered[0];bm=results[best]["global"]
 better=(bm["brier"]<base["brier"] and bm["pr_auc"]>base["pr_auc"] and bm["eventos"]>=15)
 # Never certify; provisional presentation choice requires superiority of baseline.
 choice=best if better else None
 output=[]
 for z,date in enumerate(dates):
  if not test[z]:continue
  for j,loc in enumerate(LOCALITIES):
   for name in MODEL_NAMES:
    output.append({"mes":date,"localidad":loc,"modelo":name,
      "evento_p90":int(Y[z,j]),"probabilidad":round(float(probs[name][z,j]),6),
      "lluvia_observada_mm":round(float(rain[z,j]),5),
      "umbral_p90_local_mm":round(float(thr[j]),4),
      "lluvia_ge1000_revisar":str(bool(bad[z,j])).lower()})
 if len(output)!=60*4*5:raise ValueError("Faltan probabilidades de prueba")
 BASE.mkdir(parents=True,exist_ok=True)
 with PRED.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(output)
 report={"fase":"10E","fecha_corte":"2026-10-17",
  "objeto":"probabilidad experimental de lluvia mensual >= percentil 90 LOCAL calculado SOLO en train",
  "unidad_evaluacion":"4 localidades ERA5; NO 39 sectores CHIRPS",
  "localidades":list(LOCALITIES),"historico":"1996–2025",
  "periodos":{"train":TRAIN,"tuning":TUNE,"calibracion":CAL,"test":TEST},
  "sectores_o_zonas_certificadas":0,
  "variables_predictores_t_rezagados_dos_meses":list(columns),
  "fuentes_sha256":{str(p.relative_to(ROOT)):digest(p) for p in (LAND,HUM,MAR,SOI,CURRENT)},
  "corrientes_marinas":{"estado":"NO_INCLUIDAS_EN_ENTRENAMIENTO","motivo":"serie parcial 2017-2025 y puntos geostróficos sin colocalización con costa/modelos terrestres","serie":str(CURRENT.relative_to(ROOT))},
  "presion_msl_nubosidad_humedad_dosel":{"estado":"NO DISPONIBLE EN ESTA MATRIZ HOMOLOGADA","accion":"preparar ingesta y fuentes con timestamp"},
  "objetivo_umbral_p90_local_mm":{loc:round(float(thr[j]),4) for j,loc in enumerate(LOCALITIES)},
  "n_muestras_por_modelo":{"entrenamiento":int(masks["entrenamiento"].sum()*4),
   "ajuste":int(masks["ajuste"].sum()*4),"calibracion":int(ca.sum()*4),"prueba":int(test.sum()*4)},
  "n_episodios_lluvia_ge1000_marcados_en_archivo":len(flags),
  "n_banderas_ge1000_en_test":int(bad[test].sum()),
  "resultados":results,"ranking_descriptivo_por_brier":ordered,
  "modelo_destacado_experimental_si_supera_climatologia":choice,
  "regla_de_eleccion":"Brier inferior y PR-AUC superior a climatología local estacional, al menos 15 positivos en test; no certificación ni despliegue de alertas.",
  "as_issued_disponible":False,"verificacion_instrumental_independiente":False,
  "transferencia_espacial_validada":False,"modelo_operativo_certificado":None,
  "alertas_habilitadas":False,
  "limitaciones":[
   "ERA5/ERA5-Land y otros insumos son retrospectivos; no emisiones originales.",
   "NOAA Niño1+2/3.4 son índices oceánicos regionales, NO SST costera local.",
   "Cuatro localidades con datos de modelo/reanálisis, no pluviómetros ni 39 sectores con covariables completas.",
   "Los datos de corrientes geostróficas comienzan 2017, se omiten para evitar rellenar 1996–2016.",
   "P90 local de entrenamiento no es umbral oficial SENAMHI ni evento ENSO, las salidas son riesgo mensual de lluvia alta.",
   "GCN sobre grafo simple de cuatro localidades, NO CNN bidimensional ni extrapolación a pisos ecológicos.",
   "La etiqueta objetivo usa reanálisis ERA5, no CHIRPS: no comparar directamente habilidad con fase 10D.",
   "No confundir probabilidades de lluvia intensa con pronósticos de enfermedades agrícolas o del Niño Costero.",
   "Modelos calibrados sobre 2019-20, resultado no garantiza cobertura ante 2023.",
   "Las variables de radiación, mar, viento etc se observan con lag de 2 meses y nunca incluyen valores del objetivo.",
   "Valores de lluvia >=1000 mm del reanálisis existen y se señalizan para revisión, sin borrarlos silenciosamente."
  ]}
 report["sha256_predicciones"]=digest(PRED)
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10E_RESULTADOS",json.dumps({"umbral_p90_mm":report["objetivo_umbral_p90_local_mm"],
  "prueba":report["n_muestras_por_modelo"]["prueba"],
  "modelos":{n:results[n]["global"] for n in MODEL_NAMES},
  "destacado_experimental":choice,"alertas":False},ensure_ascii=False),flush=True)
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 main(check=a.check)
