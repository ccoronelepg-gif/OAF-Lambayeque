#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9O: extracción histórica CHIRPS v3 LATAM por píxel, sector y testigo.

1996–2025 fijado antes de consultar la fuente: 360 GeoTIFF mensuales.
No archiva los TIFF (~1,5 GB), pero registra origen + SHA256 + conteos de
celdas y versiones descargadas. Una celda repetida NO cuenta como réplica.
Sin descargas inventadas: una incidencia produce mes ausente, no interpolación.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, os, statistics, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.windows import from_bounds,transform as window_transform
from shapely.geometry import shape,box

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/homogeneidad_9o"
GEOMS=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
POINTS=ROOT/"datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv"
DAYS=BASE/"fuentes_chirps_9o.json"
SERIES=BASE/"serie_sectores_chirps_9o.csv"
WITNESS=BASE/"serie_testigos_chirps_9o.csv"
URL="https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
YEARS=list(range(1996,2026))
MONTHS=[f"{y}-{m:02d}" for y in YEARS for m in range(1,13)]
BBOX=(-80.72,-7.23,-79.11,-5.48)
MAX_TIFF=9_000_000
F_SEC=("mes","sector","precipitacion_promedio_pixel_mm","dispersion_espacial_mm",
       "n_pixeles_terrestres","n_pixeles_geometricos","n_pixeles_invalidos",
       "producto_fuente","sha256_tiff")
F_WIT=("mes","testigo","latitud_celda","longitud_celda","precipitacion_pixel_mm",
       "producto_fuente","sha256_tiff")
def sha(raw):return hashlib.sha256(raw).hexdigest()

def read_csv(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def inputs():
 geo=json.loads(GEOMS.read_text("utf8"))
 witness=read_csv(POINTS)
 if len(geo["features"])!=42 or len(witness)!=81:raise ValueError("Base SIG/8P modificada")
 seen=set()
 for f in geo["features"]:
  p=f["properties"]
  if p["id_sector"] in seen:raise ValueError("ID sector duplicado")
  seen.add(p["id_sector"])
  if p["zona_homogenea_validada"] is not False:raise ValueError("Zona no certificada")
 for p in witness:
  if p["perfil_completo_1996_2025"]!="true" or p["apto_para_zona_operativa"]!="false":
   raise ValueError("Testigo ERA5 incorrectamente certificado")
 return sorted(geo["features"],key=lambda f:f["properties"]["id_sector"]),witness

def source_url(month):
 yr,mo=month.split("-")
 return URL+f"chirps-v3.0.{yr}.{mo}.tif"

def download(month):
 url=source_url(month)
 last=None
 for attempt in range(2):
  try:
   with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-9O-historical-research/1.0"}),
                timeout=65) as response:
    raw=response.read(MAX_TIFF+1)
   if not 400_000<len(raw)<MAX_TIFF:raise ValueError("GeoTIFF fuera de tamaño esperado")
   if raw[:4] not in (b"II*\x00",b"MM\x00*"):raise ValueError("El proveedor no devolvió GeoTIFF")
   return month,raw,None
  except (HTTPError,URLError,TimeoutError,ValueError,OSError) as e:
   last=f"{type(e).__name__}: {e}"[:280]
   if attempt==0:time.sleep(.5)
 return month,None,last

def get_grid(raw):
 with MemoryFile(raw) as mem,mem.open() as ds:
  if ds.crs is None or ds.crs.to_epsg()!=4326 or ds.count!=1 or not ds.transform.is_rectilinear:
   raise ValueError("CHIRPS v3 raster sin EPSG4326, banda única o ejes rectilíneos")
  if ds.res[0]>.051 or ds.res[1]>.051 or ds.res[0]<.049 or ds.res[1]<.049:
   raise ValueError("La resolución no es CHIRPS 0,05°")
  if not box(*ds.bounds).contains(box(*BBOX)):
   raise ValueError("Bounding Box de CHIRPS no incluye Lambayeque")
  win=from_bounds(*BBOX,transform=ds.transform).round_offsets().round_lengths()
  data=ds.read(1,window=win).astype("float64")
  transform=window_transform(win,ds.transform)
  if data.shape[0]<25 or data.shape[1]<25 or data.size>2500:
   raise ValueError("Ventana CHIRPS distinta de ~0,05° alrededor de Lambayeque")
  if not np.all(np.isfinite(data)|np.isnan(data)):raise ValueError("CHIRPS con inf")
  valid=np.isfinite(data)&(data>=0)&(data<50000) # excluye -9999 sin nodata declarado
  return data,valid,transform,ds.crs.to_epsg(),tuple(round(v,8) for v in (transform.a,transform.e,transform.c,transform.f))

def define_grid(geoms,points,sh,transform):
 masks={}
 for f in geoms:
  p=f["properties"]
  masked=geometry_mask([f["geometry"]],out_shape=sh,transform=transform,
                       all_touched=False,invert=True)
  if not masked.any():
   # Si el polígono es menor al píxel CHIRPS se declara ausencia y no se
   # fuerza un píxel vecino como observación del sector.
   masked=np.zeros(sh,dtype=bool)
  masks[p["id_sector"]]=masked
 locations={}
 seen={}
 for p in points:
  lon=float(p["longitud"]);lat=float(p["latitud"])
  col=int(math.floor((lon-transform.c)/transform.a))
  row=int(math.floor((lat-transform.f)/transform.e))
  if not (0<=row<sh[0] and 0<=col<sh[1]):raise ValueError("Testigo fuera de ventana")
  coord=(round(transform.c+(col+.5)*transform.a,8),
         round(transform.f+(row+.5)*transform.e,8))
  locations[p["id"]]=(row,col,coord[1],coord[0])
  seen.setdefault((row,col),[]).append(p["id"])
 return masks,locations,seen

def build(max_months=360,workers=6,years=None):
 geoms,points=inputs()
 selected=[m for m in MONTHS if years is None or int(m[:4]) in years][:max_months]
 BASE.mkdir(parents=True,exist_ok=True)
 sources=[];s_rows=[];p_rows=[];errors=[]
 signature=None;mask=None;location=None;duplicated=None
 n=0
 # El executor.map devuelve en orden y mantiene como mucho max_workers futuros
 # residentes si la ejecución se controla en lotes de <=12 meses.
 with ThreadPoolExecutor(max_workers=workers) as pool:
  for begin in range(0,len(selected),12):
   pending=selected[begin:begin+12]
   for mon,raw,error in pool.map(download,pending):
    if error:
     errors.append({"mes":mon,"url":source_url(mon),"error":error})
     continue
    try:
     array,valid,transform,crs,sig=get_grid(raw)
     if signature is None:
      signature=sig
      mask,location,duplicated=define_grid(geoms,points,array.shape,transform)
     if sig!=signature:raise ValueError("CHIRPS transform mensual cambió")
     rawsha=sha(raw)
     month_sec=[];month_pt=[]
     for sector,m in mask.items():
      observed=array[m&valid]
      geom_n=int(m.sum())
      total=int(observed.size)
      mean=round(float(observed.mean()),5) if total>0 else ""
      std=round(float(observed.std(ddof=0)),5) if total>1 else "" if total==0 else 0.0
      month_sec.append({"mes":mon,"sector":sector,"precipitacion_promedio_pixel_mm":mean,
        "dispersion_espacial_mm":std,"n_pixeles_terrestres":total,
        "n_pixeles_geometricos":geom_n,"n_pixeles_invalidos":geom_n-total,
        "producto_fuente":"CHIRPS-v3.0-final-LATAM","sha256_tiff":rawsha})
     for pt,(row,col,lat,lon) in location.items():
      observed=round(float(array[row,col]),5) if valid[row,col] else ""
      month_pt.append({"mes":mon,"testigo":pt,"latitud_celda":lat,"longitud_celda":lon,
       "precipitacion_pixel_mm":observed,"producto_fuente":"CHIRPS-v3.0-final-LATAM",
       "sha256_tiff":rawsha})
     s_rows+=month_sec;p_rows+=month_pt
     sources.append({"mes":mon,"url":source_url(mon),"sha256":rawsha,"bytes":len(raw),
       "pixeles_nativos_reutilizados":len(duplicated),
       "n_pixeles_lambayeque_validos":int(valid.sum()),
       "n_sectores_sin_pixel_terrestre":sum(x["n_pixeles_terrestres"]==0 for x in month_sec),
       "raster_transform":list(sig),"epsg":crs})
     n+=1
     if n%12==0:print("CHIRPS 9O:",n,"/360 meses comprobados",flush=True)
    except (ValueError,IndexError,AssertionError) as e:
     errors.append({"mes":mon,"url":source_url(mon),
       "error":f"{type(e).__name__}: {e}"[:280]})
   # No persistir ninguno de los TIFF íntegros; cada uno lleva SHA y URL fuente.
 fields={"sec":F_SEC,"wit":F_WIT}
 for path,rows,cols in ((SERIES,s_rows,F_SEC),(WITNESS,p_rows,F_WIT)):
  with path.open("w",encoding="utf8",newline="") as file:
   w=csv.DictWriter(file,fieldnames=cols);w.writeheader();w.writerows(rows)
 report={"fase":"9O","producto":"CHIRPS v3 final mensual LATAM a 0.05°",
     "periodo_solicitado":"1996-01 a 2025-12",
     "anios_preseleccionados":[int(y) for y in years] if years is not None else YEARS,
     "meses_objetivo_total_30anios":360,
     "n_meses_solicitados":len(selected),"n_meses_reales":len(sources),
     "n_meses_faltantes":len(errors),"n_sectores":42,"n_testigos_reanalisis":81,
     "periodo_climatologico_30anios_completo":len(sources)==360,
     "n_registros_sector_mes":len(s_rows),"n_registros_testigo_mes":len(p_rows),
     "n_pixeles_chirps_distintos_en_testigos":len(duplicated or {}),
     "n_testigos_duplican_pixel_chirps":sum(len(v)>1 for v in (duplicated or {}).values()),
     "errores":errors,"fuentes":sources,
     "raw_geotiff_archivado_en_github":False,
     "reproduccion_fuente":"Descargar URL mensual original; comparar SHA256 conservado antes de re-extraer.",
     "primera_descarga_con_fecha_UTC":datetime.now(timezone.utc).isoformat(timespec="seconds"),
     "mascara_terrestre_chirps_no_terreno_dem":True,
     "superficie_pixel_media_no_ponderada_por_area":True,
     "calibracion_de_pronosticos_zonales":False,
     "estaciones_meteorologicas_independientes":False,
     "advertencia":"La lluvia gridded CHIRPS incorpora estaciones: ni sectores contiguos ni píxeles contiguos son réplicas independientes. Los polígonos SIG 9K no son terrenos homogéneos certificados."}
 DAYS.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return report

def check():
 report=json.loads(DAYS.read_text("utf8"))
 with SERIES.open(encoding="utf8",newline="") as f:secs=list(csv.DictReader(f))
 with WITNESS.open(encoding="utf8",newline="") as f:pts=list(csv.DictReader(f))
 assert report["fase"]=="9O" and report["producto"]=="CHIRPS v3 final mensual LATAM a 0.05°"
 assert report["n_meses_reales"]+report["n_meses_faltantes"]==report["n_meses_solicitados"]
 assert len(secs)==report["n_registros_sector_mes"]==42*report["n_meses_reales"]
 assert len(pts)==report["n_registros_testigo_mes"]==81*report["n_meses_reales"]
 assert report["periodo_climatologico_30anios_completo"]==(report["n_meses_reales"]==360)
 assert report["calibracion_de_pronosticos_zonales"] is False
 shas={s["mes"]:s["sha256"] for s in report["fuentes"]}
 assert len(shas)==report["n_meses_reales"]
 for r in secs:
  assert r["mes"] in shas and r["sha256_tiff"]==shas[r["mes"]]
  assert 0<=int(r["n_pixeles_terrestres"])<=int(r["n_pixeles_geometricos"])
 for r in pts:
  assert r["mes"] in shas and r["sha256_tiff"]==shas[r["mes"]]
 return report
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--check",action="store_true")
 ap.add_argument("--max-months",type=int,default=360)
 ap.add_argument("--workers",type=int,default=6)
 ap.add_argument("--years",default=None,help="años íntegros preespecificados separados por comas")
 args=ap.parse_args()
 years=[int(v) for v in args.years.split(",")] if args.years else None
 if years and (len(set(years))!=len(years) or any(v not in YEARS for v in years)):
  raise SystemExit("Años fuera de 1996–2025 o repetidos")
 if not 1<=args.max_months<=360 or not 1<=args.workers<=8:
  raise SystemExit("Fuera de cuotas")
 report=check() if args.check else build(max_months=args.max_months,workers=args.workers,years=years)
 print("9O CHIRPS: meses reales",report["n_meses_reales"],"/",report["n_meses_solicitados"],
       "píxeles distintos",report["n_pixeles_chirps_distintos_en_testigos"])
