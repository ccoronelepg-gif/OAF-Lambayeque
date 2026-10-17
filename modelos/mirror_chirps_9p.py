#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9P: comprobar mirror oficial USGS de CHIRPS v3 final global vs LATAM 9O.

Antes de añadir siquiera un mes se exige concordancia por píxel con al menos
dos meses históricos pre-archivados, controles SHA, georreferencia y producto FINAL.
Un producto PRELIMINAR o CHIRPS v2 NUNCA sustituye silenciosamente a CHIRPS v3.
La fuente alternativa USGS entrega TIFF GLOBAL (~22MB), no LATAM (~4MB).
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

import numpy as np
from rasterio.io import MemoryFile
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds,transform as window_transform

import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import chirps_homogeneidad_9o as parent

BASE=ROOT/"datos/continuidad_9p"
META=BASE/"fuentes_adicionales_chirps_9p.json"
SEC=BASE/"meses_adicionales_sectores_9p.csv"
WIT=BASE/"meses_adicionales_testigos_9p.csv"
GLOBAL=("https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/"
        "fews/web/global/monthly/chirps/final/downloads/monthly/")
PROBES=("1996-01","2025-12")
MAX_BYTES=36_000_000
MAX_TOTAL_DOWNLOADS=8
MONTHS=parent.MONTHS
def urlof(month):return GLOBAL+"chirps-v3.0."+month.replace("-",".")+".tif"
def read(path):
 return json.loads(path.read_text("utf8"))
def fetch(month):
 url=urlof(month)
 with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-climatology-9P/1.0"}),timeout=70) as r:
  raw=r.read(MAX_BYTES+1)
 if not 4_000_000<len(raw)<MAX_BYTES or raw[:4] not in (b"II*\0",b"MM\0*"):
  raise ValueError("Mirror no entregó GeoTIFF GLOBAL v3 del tamaño esperado")
 return raw
def compare(probe,oldsec,oldwit,original):
 raw=fetch(probe)
 data,valid,t,epsg,sig=parent.get_grid(raw)
 geometries,witness=parent.inputs()
 masks,sites,_=parent.define_grid(geometries,witness,data.shape,t)
 comparisons=[]
 for f in geometries:
  sid=f["properties"]["id_sector"]
  reference=oldsec[(probe,sid)]
  r=reference["precipitacion_promedio_pixel_mm"]
  accepted=data[masks[sid]&valid]
  got=float(accepted.mean()) if len(accepted) else None
  if r=="":
   if got is not None:raise ValueError("Una celda ausente 9O aparece ahora como observada para "+sid)
  else:
   if got is None or abs(float(r)-got)>0.04:
    raise ValueError("Diferencia del producto GLOBAL vs LATAM en sector "+sid+
       " para "+probe+": "+str((r,got)))
   comparisons.append(abs(float(r)-got))
 for p,(row,col,lat,lon) in sites.items():
  r=oldwit[(probe,p)]["precipitacion_pixel_mm"]
  got=float(data[row,col]) if valid[row,col] else None
  if r=="":
   if got is not None:raise ValueError("Píxel testigo faltante 9O cambió de máscara "+p)
  elif got is None or abs(float(r)-got)>0.04:
   raise ValueError("Píxel testigo distinto entre final GLOBAL y LATAM "+p+
                    " para "+probe+" (mm "+str((r,got))+")")
 return {"mes":probe,"url_mirror":urlof(probe),"sha256_mirror":parent.sha(raw),
   "sha256_latam_original":original[probe]["sha256"],
   "n_sectores_con_datos_comparados":len(comparisons),
   "max_diferencia_promedios_sector_mm":round(max(comparisons),6) if comparisons else None,
   "tolerancia_mm":0.04,"producto_equivalente_en_celdas_lambayeque":True},sig

def one_month(month,signature,geometries,witness):
 raw=fetch(month)
 data,valid,t,epsg,sig=parent.get_grid(raw)
 if any(abs(a-b)>1e-6 for a,b in zip(sig,signature)):
  raise ValueError("Origen GLOBAL perdió el alineamiento geográfico de LATAM")
 masks,sites,_=parent.define_grid(geometries,witness,data.shape,t)
 hash_=parent.sha(raw)
 sec=[]
 for f in geometries:
  sid=f["properties"]["id_sector"];mask=masks[sid]
  v=data[mask&valid]
  geom=int(mask.sum());n=int(v.size)
  mean=round(float(v.mean()),5) if n else ""
  std=round(float(v.std(ddof=0)),5) if n>1 else 0.0 if n else ""
  sec.append({"mes":month,"sector":sid,"precipitacion_promedio_pixel_mm":mean,
   "dispersion_espacial_mm":std,"n_pixeles_terrestres":n,
   "n_pixeles_geometricos":geom,"n_pixeles_invalidos":geom-n,
   "producto_fuente":"CHIRPS-v3.0-final-GLOBAL-USGS-verificada-vs-LATAM",
   "sha256_tiff":hash_})
 pt=[]
 for site,(row,col,lat,lon) in sites.items():
  pt.append({"mes":month,"testigo":site,"latitud_celda":lat,"longitud_celda":lon,
    "precipitacion_pixel_mm":round(float(data[row,col]),5) if valid[row,col] else "",
    "producto_fuente":"CHIRPS-v3.0-final-GLOBAL-USGS-verificada-vs-LATAM",
    "sha256_tiff":hash_})
 source={"mes":month,"url":urlof(month),"sha256":hash_,"bytes":len(raw),
         "formato":"GeoTIFF global v3 final, validado contra LATAM 9O",
         "n_sectores":len(sec),"n_testigos":len(pt),"crs":epsg,"transform":list(sig)}
 return source,sec,pt

def run(batch=4,allow_network=True):
 BASE.mkdir(parents=True,exist_ok=True)
 prior=read(parent.DAYS)
 oldsources={f["mes"]:f for f in prior["fuentes"]}
 oldsec={(r["mes"],r["sector"]):r for r in parent.read_csv(parent.SERIES)}
 oldwit={(r["mes"],r["testigo"]):r for r in parent.read_csv(parent.WITNESS)}
 cached=read(META) if META.exists() else {"fase":"9P","nuevos":[],"errores":[]}
 if cached.get("fase")!="9P":raise ValueError("Estado 9P no comprobable")
 good={f["mes"]:f for f in cached["nuevos"]}
 if set(good)&set(oldsources):raise ValueError("Mes duplicado entre 9O y 9P")
 probes=cached.get("comparaciones_equivalencia",[])
 error=None
 signature=None
 if allow_network:
  try:
   probes=[]
   for probe in PROBES:
    if probe not in oldsources:raise ValueError("Falta prueba control histórica 9O "+probe)
    comparison,sign=compare(probe,oldsec,oldwit,oldsources)
    if signature is None:signature=sign
    elif sign!=signature:raise ValueError("Rejilla espejo no estable entre controles")
    probes.append(comparison)
  except (HTTPError,URLError,OSError,TimeoutError,ValueError) as exc:
   error=f"{type(exc).__name__}: {exc}"[:450]
 verified=(len(probes)==len(PROBES) and
           all(x["producto_equivalente_en_celdas_lambayeque"] for x in probes) and
           error is None and allow_network)
 geometries,witness=parent.inputs()
 sec=parent.read_csv(SEC) if SEC.exists() else []
 pts=parent.read_csv(WIT) if WIT.exists() else []
 if len(sec)!=42*len(good) or len(pts)!=81*len(good):
  raise ValueError("Series previas 9P no respaldan manifiesto")
 missing=[m for m in MONTHS if m not in good and m not in oldsources]
 # Priorizar completar años parcialmente cercanos 2001 y años del periodo central.
 missing.sort(key=lambda m:(abs(int(m[:4])-2001),m))
 errors={x["mes"]:x for x in cached.get("errores",[]) if x.get("mes") in MONTHS}
 attempted=[]
 if verified:
  for month in missing[:batch]:
   try:
    source,newsec,newpt=one_month(month,signature,geometries,witness)
    good[month]=source
    sec.extend(newsec);pts.extend(newpt)
    attempted.append(month)
    errors.pop(month,None)
   except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
    errors[month]={"mes":month,"url":urlof(month),
                   "error":f"{type(exc).__name__}: {exc}"[:300]}
    attempted.append(month)
    if isinstance(exc,(HTTPError,URLError)):
     break # respetar prohibición de acceso; no insistir
 sec.sort(key=lambda r:(r["mes"],r["sector"]))
 pts.sort(key=lambda r:(r["mes"],r["testigo"]))
 if len({(r["mes"],r["sector"]) for r in sec})!=len(sec) or len({(r["mes"],r["testigo"]) for r in pts})!=len(pts):
  raise ValueError("Duplicado por extracción incremental")
 for path,data,columns in ((SEC,sec,parent.F_SEC),(WIT,pts,parent.F_WIT)):
  with path.open("w",encoding="utf8",newline="") as f:
   writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(data)
 state={"fase":"9P","fecha_corte":"2026-10-17",
  "fuente_alternativa":"USGS FEWS NET CHIRPS v3 FINAL GLOBAL GeoTIFF",
  "url_raiz":GLOBAL,"sonda_repositorio":allow_network,
  "mirroring_verificado":verified,
  "comparaciones_equivalencia":probes,
  "n_meses_referencia_9o":len(oldsources),
  "n_meses_9p_nuevos":len(good),
  "n_meses_objetivo":360,
  "n_meses_pendientes":360-len(oldsources)-len(good),
  "meses_intentados_lote":attempted,
  "problema_sonda":error,
  "nuevos":sorted(good.values(),key=lambda f:f["mes"]),
  "errores":sorted(errors.values(),key=lambda f:f["mes"]),
  "ninguna_equivalencia_asumida_sin_prueba":True,
  "no_mezcla_productos_CHIRPS_v2_prelim":True,
  "calibracion_zonal_validada":False,
  "zonas_climaticas_certificadas":0,
  "nota":"La comprobación del espejo compara físicamente lluvia en 42 polígonos y 81 puntos en 2 meses superpuestos. Si no coincide, 0 meses nuevos."}
 META.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n","utf8")
 print("9P espejo:",len(probes),"controles,",len(good),"meses nuevos,",
       state["n_meses_pendientes"],"pendientes.",error or "")
 return state

def check():
 s=read(META)
 if s["fase"]!="9P" or s["n_meses_referencia_9o"]!=108:
  raise ValueError("Archivo 9P incompatible")
 if s["n_meses_9p_nuevos"]!=len(s["nuevos"]) or (
    s["n_meses_referencia_9o"]+s["n_meses_9p_nuevos"]+
    s["n_meses_pendientes"])!=360:raise ValueError("Conteos CHIRPS 9P inválidos")
 if s["n_meses_9p_nuevos"]>0 and not s["mirroring_verificado"]:
  raise ValueError("Se mezclaron productos sin prueba de equivalencia")
 if len(parent.read_csv(SEC))!=42*s["n_meses_9p_nuevos"] or len(parent.read_csv(WIT))!=81*s["n_meses_9p_nuevos"]:
  raise ValueError("Filas espejo no coinciden con nuevos meses")
 return s
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true")
 ap.add_argument("--batch",type=int,default=4)
 args=ap.parse_args()
 if not 0<=args.batch<=6:raise SystemExit("Batch máximo 6 meses")
 if args.check:check()
 else:run(batch=args.batch)
