#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10H: NASA POWER monthly MERRA-2/SRB/CERES regional grid factor archive.
Alternative public provider after Open-Meteo 429. One request per unique
coarse meteorological 0.5x0.625 degree bin, NOT one per sector.
No use in real-time forecasts or infection diagnoses. Strict fail-closed QA.
"""
import argparse,csv,datetime as dt,hashlib,json,math,time,urllib.error,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path
import ingesta_era5_39_sectores_10g as ten_g

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"datos/nasa_power_10h"
CSV=OUT/"atmosfera_power_mensual_39_sectores_10h.csv"
META=OUT/"auditoria_fuentes_10h.json"
BASE_URL="https://power.larc.nasa.gov/api/temporal/monthly/point"
PARAM=("T2M","RH2M","WS10M","ALLSKY_SFC_SW_DWN","PS","T2MDEW")
SECTORS=ten_g.manifest()["puntos"]
COLS=("mes","sector","celda_aprox","consulta_lat","consulta_lon",
      "fuente_grid_lat","fuente_grid_lon","temperatura_c","humedad_pct",
      "viento_10m_m_s","radiacion_mj_m2_dia","presion_superficie_kpa",
      "temperatura_rocio_c","es_estacion","fuente","descargado_utc")
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def indices(p):
 # Dedup conservative grid bins. Explicit approximate, NOT official NASA grid mapping.
 return (math.floor((p["lat"]+90)/.5),math.floor((p["lon"]+180)/.625))
def groups():
 g=defaultdict(list)
 for p in SECTORS:g[indices(p)].append(p)
 return dict(sorted(g.items()))
def fetch(p,attempts=4):
 args={"parameters":",".join(PARAM),"community":"AG",
       "longitude":str(p["lon"]),"latitude":str(p["lat"]),
       "start":"1996","end":"2025","format":"JSON"}
 url=BASE_URL+"?"+urllib.parse.urlencode(args)
 last=""
 for attempt in range(attempts):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"OAF-Lambayeque/10H-Academic-Research"})
   with urllib.request.urlopen(req,timeout=165) as res:
    raw=res.read()
    if res.status!=200:raise ValueError("HTTP "+str(res.status))
   obj=json.loads(raw)
   if obj.get("messages"):raise ValueError("NASA POWER: "+str(obj["messages"]))
   return obj,{"url":url,"response_sha256":hashlib.sha256(raw).hexdigest(),
     "bytes":len(raw),"descargado_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   last=str(e)
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):
    detail=e.read(1000).decode("utf8","replace")
    raise ValueError("NASA POWER petición "+last+": "+detail) from e
   time.sleep(4*(attempt+1))
 raise RuntimeError("NASA POWER no responde tras intentos prudentes: "+last)
def parse_response(blob,p,rec,ids):
 props=blob.get("properties",{}).get("parameter",{})
 if not all(k in props for k in PARAM):
  raise ValueError("NASA no entrega todos los campos: "+str(sorted(props)))
 values={k:props[k] for k in PARAM}
 months=[f"{y}{m:02d}" for y in range(1996,2026) for m in range(1,13)]
 geo=blob.get("geometry",{}).get("coordinates",[])
 if len(geo)<2:raise ValueError("NASA no devuelve coordenadas")
 records=[]
 for ym in months:
  vals=[]
  for k in PARAM:
   val=values[k].get(ym)
   if val is None or not math.isfinite(float(val)) or float(val)<=-990:
    raise ValueError("NASA mes ausente "+str(ids)+" "+ym+" "+k)
   vals.append(float(val))
  t,rh,wind,rad,ps,dew=vals
  if not(-30<=t<=55 and -50<=dew<=55 and 0<=rh<=100 and 0<=wind<80
         and 0<=rad<50 and 40<=ps<=120):
   raise ValueError("Variable fuera de dominio "+str(ids)+" "+ym+" "+str(vals))
  month=ym[:4]+"-"+ym[4:]
  for sector in ids:
   records.append({"mes":month,"sector":sector,"celda_aprox":str(indices(p)),
    "consulta_lat":p["lat"],"consulta_lon":p["lon"],"fuente_grid_lat":geo[1],
    "fuente_grid_lon":geo[0],"temperatura_c":t,"humedad_pct":rh,
    "viento_10m_m_s":wind,"radiacion_mj_m2_dia":rad,
    "presion_superficie_kpa":ps,"temperatura_rocio_c":dew,
    "es_estacion":"false",
    "fuente":"NASA_POWER_MERRA2_Meteorologia_SRB_CERES_Radiacion",
    "descargado_utc":rec["descargado_utc"]})
 return records
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 group=groups()
 if len(group)<3 or len(group)>39:raise ValueError("Agrupación NASA inesperada")
 rows=[];ledger=[]
 for ix,(k,sects) in enumerate(group.items()):
  # One real API request per coarse grid bin, no 39 duplicate downloads.
  p=sects[0];o,meta=fetch(p)
  batch=parse_response(o,p,meta,[s["sector"] for s in sects])
  rows.extend(batch)
  ledger.append({"bin":list(k),"sector_sample":p["sector"],
    "sectores_comparten_muestra":[s["sector"] for s in sects],
    **meta})
  print("10H_NASA_BLOQUE",ix+1,"de",len(group),"sectores",len(sects),
        "registros",len(rows),flush=True)
  time.sleep(2)
 rows.sort(key=lambda x:(x["sector"],x["mes"]))
 if len(rows)!=39*360 or len(set((x["sector"],x["mes"]) for x in rows))!=14040:
  raise ValueError("Serie completa 39x360 ausente o duplicada")
 with CSV.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=COLS);w.writeheader();w.writerows(rows)
 info={"fase":"10H","periodo":"1996-01/2025-12",
  "estado":"INGESTA_MENSUAL_REANALISIS_COMPLETA_NO_VALIDACION_CAMPO",
  "fuente":"https://power.larc.nasa.gov/docs/services/api/temporal/monthly/",
  "meteorologia":"NASA POWER MERRA-2 (0.5 x 0.625 aprox)",
  "radiacion":"NASA SRB historico y CERES; quiebre de origen alrededor de 2001",
  "n_sectores":39,"n_meses_por_sector":360,"n_filas":len(rows),
  "n_bins_aproximados":len(group),"n_peticion_fuente":len(ledger),
  "resolucion":"Varios sectores reciben las mismas series de celda aproximada; NO 39 estaciones independientes.",
  "variables":list(PARAM),"peticiones":ledger,"sha256_csv":hashfile(CSV),
  "sha256_geometria_9k":hashfile(ten_g.GEO),
  "no_pretender_era5":True,"datos_as_issued":False,
  "validado_con_estaciones_independientes":False,
  "ninguna_alerta_automatica":True}
 META.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10H_FUENTE_VERIFICADA",json.dumps({"n":len(rows),"bins":len(group),"sha":info["sha256_csv"]}),flush=True)
def check():
 obj=json.loads(META.read_text("utf8"))
 with CSV.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
 assert obj["sha256_csv"]==hashfile(CSV) and len(rows)==14040
 assert obj["datos_as_issued"] is False and obj["ninguna_alerta_automatica"]
 print("10H_FUENTE_VERIFICADA",obj["n_bins_aproximados"],len(rows))
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args()
 check() if args.check else run()
