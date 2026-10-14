"""OAF-Lambayeque | Fase 3Q: piloto 1998 CHIRPS v3 mensual LATAM.
Observaciones: SENAMHI 1998; otras fuentes: PISCOp y ERA5 de fase 3N.
No es validacion independiente: CHIRPS incluye pluviómetros en su produccion.
Los metadatos historicos de ubicacion de las estaciones son provisionales.
"""
from __future__ import annotations
import io
import json
import math
import time
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import transform as project

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
MONTHS=range(1,13)
URL="https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
STATIONS={
 "Jayanca (La Viña)":(-6.322,-79.779),
 "Cayaltí":(-6.88079444,-79.54701389),
 "Reque":(-6.88613,-79.8355),
 "Lambayeque":(-6.73152778,-79.90983611),
 "Cueva Blanca":(-6.13130,-79.40450)
}

def distance_km(lat1,lon1,lat2,lon2):
 a,b=map(math.radians,(lat1,lat2))
 da=math.radians(lat2-lat1)
 db=math.radians(lon2-lon1)
 v=math.sin(da/2)**2+math.cos(a)*math.cos(b)*math.sin(db/2)**2
 return 12742.0176*math.asin(min(1,math.sqrt(v)))

def fetch_bytes(url):
 import requests
 error=None
 with requests.Session() as sess:
  sess.headers.update({"User-Agent":"OAF-Lambayeque-academic-CHIRPS-audit/0.7"})
  for attempt in range(3):
   try:
    res=sess.get(url,timeout=(20,90))
    res.raise_for_status()
    if len(res.content)<100000:
     raise ValueError("GeoTIFF unusually small")
    return res.content
   except (requests.RequestException,ValueError) as exc:
    error=exc
    if attempt<2:
     print("RETRY",url,type(exc).__name__,flush=True)
     time.sleep((attempt+1)*5)
 raise RuntimeError(str(error)[:180])

def extract_month(month):
 ym=f"1998-{month:02d}"
 src=URL+f"chirps-v3.0.1998.{month:02d}.tif"
 blob=fetch_bytes(src)
 result=[]
 with MemoryFile(blob) as mem:
  with mem.open() as ds:
   if not ds.crs or ds.count!=1:
    raise ValueError("GeoTIFF without CRS or with unexpected band count")
   if ds.res[0]<=0 or ds.res[1]<=0:
    raise ValueError("Invalid raster resolution")
   for station,(lat,lon) in STATIONS.items():
    xs,ys=project("EPSG:4326",ds.crs,[lon],[lat])
    x,y=xs[0],ys[0]
    if not (ds.bounds.left<=x<=ds.bounds.right and ds.bounds.bottom<=y<=ds.bounds.top):
     raise ValueError("Coordinate outside CHIRPS LATAM raster: "+station)
    value=next(ds.sample([(x,y)],indexes=1,masked=True))[0]
    if np.ma.is_masked(value) or not np.isfinite(float(value)) or float(value)<0:
     raise ValueError("Missing/invalid CHIRPS pixel: "+station+" "+ym)
    row,col=ds.index(x,y)
    cx,cy=ds.xy(row,col,offset="center")
    gx,gy=project(ds.crs,"EPSG:4326",[cx],[cy])
    result.append({
     "estacion":station,"mes":ym,"chirps_mm":round(float(value),4),
     "latitud_punto":lat,"longitud_punto":lon,
     "latitud_pixel":round(float(gy[0]),7),
     "longitud_pixel":round(float(gx[0]),7),
     "distancia_pixel_km":round(distance_km(lat,lon,gy[0],gx[0]),3),
     "resolucion_x":round(float(ds.res[0]),6),
     "resolucion_y":round(float(ds.res[1]),6),
     "sistema_referencia":str(ds.crs),"url_raster":src
    })
 return result

def main():
 obs=pd.read_csv(DATA/"senamhi_mensual_1998.csv")
 assert len(obs)==60 and (obs.dias_validos==obs.dias_mes).all()
 other=pd.read_csv(DATA/"comparacion_3n_1998.csv")
 rows=[];errors=[]
 for m in MONTHS:
  try:
   new=extract_month(m)
   rows.extend(new)
   print("OK",m,"pixels",len(new),flush=True)
  except Exception as exc:
   error={"mes":f"1998-{m:02d}","error":f"{type(exc).__name__}: {str(exc)[:230]}"}
   errors.append(error)
   print("ERROR",error,flush=True)
  time.sleep(.4)
 frame=pd.DataFrame(rows)
 if len(frame):
  frame.to_csv(DATA/"chirps_3q_pixeles_1998.csv",index=False)
  cmp=frame.merge(obs[["estacion","mes","observado_mm"]],on=["estacion","mes"],validate="one_to_one")
  others=other[["estacion","mes","producto","estimado_mm"]]
  pivot=others.pivot(index=["estacion","mes"],columns="producto",values="estimado_mm").reset_index()
  cmp=cmp.merge(pivot,on=["estacion","mes"],how="left",validate="one_to_one")
  cmp["error_chirps_mm"]=(cmp.chirps_mm-cmp.observado_mm).round(4)
  cmp.to_csv(DATA/"comparacion_3q_chirps_1998.csv",index=False)
 else:
  (DATA/"chirps_3q_pixeles_1998.csv").write_text("estacion,mes,chirps_mm\n")
  (DATA/"comparacion_3q_chirps_1998.csv").write_text("estacion,mes,chirps_mm,observado_mm,error_chirps_mm\n")
 metrics=[]
 for sta in STATIONS:
  if len(frame)==0:continue
  part=cmp[cmp.estacion==sta]
  if len(part)==0:continue
  obs_values=part.observado_mm.to_numpy()
  pred=part.chirps_mm.to_numpy()
  err=pred-obs_values
  record={"estacion":sta,"meses":len(part),
   "mae_mensual_mm":round(float(np.mean(np.abs(err))),3),
   "rmse_mensual_mm":round(float(np.sqrt(np.mean(err**2))),3),
   "sesgo_mensual_mm":round(float(np.mean(err)),3),
   "pearson_mensual":round(float(np.corrcoef(obs_values,pred)[0,1]),4)
         if len(part)>=3 and np.std(pred)>0 and np.std(obs_values)>0 else None}
  if len(part)==12:
   total_obs=float(part.observado_mm.sum())
   total_chirps=float(part.chirps_mm.sum())
   record["obs_anual_mm"]=round(total_obs,3)
   record["chirps_anual_mm"]=round(total_chirps,3)
   record["sesgo_anual_pct"]=round(100*(total_chirps-total_obs)/total_obs,2) if total_obs>0 else None
  else:
   record["obs_anual_mm"]=None
   record["chirps_anual_mm"]=None
   record["sesgo_anual_pct"]=None
  metrics.append(record)
 pd.DataFrame(metrics).to_csv(DATA/"metricas_3q_chirps_1998.csv",index=False)
 state={"version":"3Q-piloto-1998","meses_previstos":12,
        "meses_descargados":len(set(r["mes"] for r in rows)),
        "pares_estacion_mes":len(rows),"esperados":60,
        "incidencias":errors,"validacion_independiente":False,
        "coordenadas_estaciones_preliminares":True,
        "observacion":"Solo calcular totales anuales con 12 meses validos"}
 (DATA/"estado_3q_chirps.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
 report=["# Fase 3Q — CHIRPS v3 mensual: piloto 1998","",
  "> ESTUDIO EXPLORATORIO. Las estaciones pueden contribuir a CHIRPS; la coincidencia no equivale a validacion independiente.",
  "> Coordenadas instrumentales historicas aun preliminares.","",
  f"**Rasters mensuales validos: {state['meses_descargados']}/12. Pares estacion-mes: {len(rows)}/60.**","",
  "Fuente oficial: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/",
  "Metodo: pixel que contiene la coordenada preliminar SENAMHI, sin interpolar. Se conserva georreferenciacion de pixel, resolucion y URL fuente.",
  "No se completan artificialmente meses o pixeles faltantes.",
  "PISCOp y ERA5 de 1998 provienen de la fase 3N.","",
  "## Indicadores por estacion","",
  "| Estacion | Meses | SENAMHI anual mm | CHIRPS anual mm | Sesgo anual % | MAE mensual mm | RMSE mensual mm |",
  "|---|---:|---:|---:|---:|---:|---:|"]
 for r in metrics:
  def show(x):
   return "No calculable" if x is None or pd.isna(x) else str(x)
  report.append(f"| {r['estacion']} | {r['meses']} | {show(r['obs_anual_mm'])} | {show(r['chirps_anual_mm'])} | {show(r['sesgo_anual_pct'])} | {r['mae_mensual_mm']} | {r['rmse_mensual_mm']} |")
 if errors:
  report.extend(["","## Incidencias",""])
  report.extend("- "+json.dumps(e,ensure_ascii=False) for e in errors)
 report.extend(["","## Reglas de interpretacion","",
   "- Es un piloto limitado a 1998, no una evaluacion multianual del periodo 1996–2025.",
   "- Para contrastes multianuales usar exactamente los mismos meses de observacion valida.",
   "- CHIRPS v3 incorpora estaciones de lluvia; evaluar dependencia y generalizacion fuera de muestra.",
   "- No inferir alertas sanitarias sin registros locales de enfermedades de arandano.",""])
 (ROOT/"CHIRPS_3Q_1998.md").write_text("\n".join(report),encoding="utf-8")
 print("FINAL",len(rows),"pares",len(errors),"incidencias",flush=True)
 return len(rows)
if __name__=="__main__":
 if main()==0:
  raise SystemExit(1)
