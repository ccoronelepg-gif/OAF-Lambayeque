#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9M: sensibilidad de relieve, pendiente y aspecto para sectores de 9K.
Usa EXCLUSIVAMENTE el Copernicus GLO-90 original, ya preservado en 9L.
La cobertura es la intersección con la tesela S07 W080, no toda Lambayeque.
No genera cuencas, pronósticos locales ni áreas agrícolas certificadas.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.features import rasterize, shapes
from rasterio.windows import from_bounds, transform as wtransform
from shapely.geometry import shape,mapping,box,Polygon
from shapely.ops import unary_union
from shapely import make_valid

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"datos/relieve_9l/fuentes/copernicus_glo90_s07_w080.tif"
SECTORS=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
STATE9L=ROOT/"datos/relieve_9l/estado_relieve_9l.json"
BASE=ROOT/"datos/sensibilidad_9m"
STATE=BASE/"estado_relieve_9m.json"
GEO=BASE/"sectores_filtrados_tesela_9m.geojson"
CSV=BASE/"sensibilidad_42_sectores_9m.csv"
FLOORS={
  "llanura_costa":(0,100),"valle_bajo":(100,300),
  "piedemonte":(300,800),"montana_baja":(800,1600),
  "montana_media":(1600,2500),"montana_alta":(2500,6500),
  "cota_negativa_revisar":(-100,0)}
SCALES=(3,5)
LIMITS=(20,30,40)
MIN_PIXELS=10
COLUMNS=("id_sector","piso","familia","tipo_cobertura",
 "fraccion_poligono_9k_dentro_tesela",
 "pixeles_validos_270m","altitud_mediana_m_270m","pendiente_p90_270m",
 "aspecto_dominante_270m","fraccion_aspecto_dominante_270m",
 "compatible_270m_20","compatible_270m_30","compatible_270m_40",
 "compatible_450m_20","compatible_450m_30","compatible_450m_40",
 "sensibilidad_30grados_abs_270_vs_450","n_piezas_270m_30",
 "zona_homogenea_validada","riesgo_fitosanitario_validado")
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(x):
 if not x.is_valid:x=make_valid(x)
 parts=[]
 if x.geom_type=="Polygon":parts=[x]
 elif x.geom_type=="MultiPolygon":parts=list(x.geoms)
 elif hasattr(x,"geoms"):
  for v in x.geoms:
   if v.geom_type=="Polygon":parts.append(v)
   elif v.geom_type=="MultiPolygon":parts.extend(v.geoms)
 return unary_union([v for v in parts if v.area>0]) if parts else Polygon()
def parts(x):
 if x.is_empty:return []
 if x.geom_type=="Polygon":return [x]
 if x.geom_type=="MultiPolygon":return list(x.geoms)
 return []
def calculate(ds,poly,scale,mode=False):
 """Raster average 3x/5x, pendientes con protección de nodata y bordes."""
 L,B,R,T=poly.bounds
 # Expandir ventana raster 2 celdas de salida en cada extremo para derivadas.
 eps=abs(ds.transform.a)*scale*2
 ext=box(L-eps,B-eps,R+eps,T+eps).intersection(box(*ds.bounds))
 l,b,r,t=ext.bounds
 win=from_bounds(l,b,r,t,ds.transform).round_offsets().round_lengths()
 h0,w0=round(win.height),round(win.width)
 if h0<5 or w0<5:return None
 hh=max(3,math.ceil(h0/scale));ww=max(3,math.ceil(w0/scale))
 mat=ds.read(1,window=win,out_shape=(hh,ww),
             resampling=Resampling.average,masked=True)
 z=np.ma.filled(mat,np.nan).astype("float64")
 tx=wtransform(win,ds.transform)*Affine.scale(w0/ww,h0/hh)
 dem=np.isfinite(z)&(z>-200)&(z<6500)
 coverage=rasterize([(mapping(poly),1)],out_shape=(hh,ww),
                     transform=tx,all_touched=False,fill=0).astype(bool)
 usable=dem&coverage
 # Evitar gradient wrap-around en bordes; vecinos deben ser válidos.
 full=dem.copy()
 full[0,:]=False;full[-1,:]=False;full[:,0]=False;full[:,-1]=False
 full[1:,:]&=dem[:-1,:];full[:-1,:]&=dem[1:,:]
 full[:,1:]&=dem[:,:-1];full[:,:-1]&=dem[:,1:]
 valid=usable&full
 if usable.sum()<MIN_PIXELS or valid.sum()<MIN_PIXELS:return None
 zz=np.where(dem,z,0.0)
 lat=poly.centroid.y
 dy=abs(tx.e)*111132.9;dx=abs(tx.a)*111319.5*math.cos(math.radians(lat))
 z_south,z_east=np.gradient(zz,dy,dx)
 slope=np.degrees(np.arctan(np.hypot(z_south,z_east)))
 # Aspecto de descenso: 0=N,90=E,180=S,270=O.
 aspect=(np.degrees(np.arctan2(-z_east,z_south))+360)%360
 eligible_slope=valid&(slope>=2)
 labels=np.array(["N","E","S","O"],dtype=object)
 quart=np.floor((aspect+45)%360/90).astype("int8")
 qcount=Counter(labels[int(x)] for x in quart[eligible_slope])
 totalq=sum(qcount.values())
 aspect_main=sorted(qcount,key=lambda k:(-qcount[k],k))[0] if qcount else None
 dom_frac=round(qcount[aspect_main]/totalq,5) if totalq else None
 lo,hi=FLOORS[mode] if isinstance(mode,str) else (None,None)
 if lo is None:raise ValueError("Estrato de elevación no especificado")
 outputs={}
 for threshold in LIMITS:
  keep=valid&(z>=lo)&(z<hi)&(slope<=threshold)
  outputs[str(threshold)]={
    "pixeles":int(keep.sum()),
    "fraccion":round(float(keep.sum()/usable.sum()),5),
    "mask":keep}
 return {"alt_mediana":round(float(np.median(z[usable])),2),
  "slope_p90":round(float(np.quantile(slope[valid],.9)),2),
  "pixeles":int(usable.sum()),
  "dominante":aspect_main,"f_aspecto":dom_frac,
  "orientacion_con_direccion_definida_n_pixeles":totalq,
  "orientaciones":dict(sorted(qcount.items())),
  "limites":outputs,"transform":tx}

def measure():
 ref=json.loads(STATE9L.read_text("utf8"))
 if ref["fase"]!="9L" or filehash(SOURCE)!=ref["sha256_tiff_original"]:
  raise ValueError("Relieve 9L fue alterado o carece de SHA-256")
 geo=json.loads(SECTORS.read_text("utf8"))
 if len(geo["features"])!=42:raise ValueError("No son 42 piezas 9K")
 results=[];features=[]
 with rasterio.open(SOURCE) as ds:
  if ds.crs.to_epsg()!=4326 or ds.count!=1:raise ValueError("COG no WGS84")
  footprint=box(*ds.bounds)
  for f in geo["features"]:
   p=f["properties"];id=p["id_sector"];floor=p["estrato"]
   poly=shape(f["geometry"])
   intersect=poly.intersection(footprint)
   denom=poly.area
   area=round(float(intersect.area/denom),5) if denom>0 else 0.0
   desc={"id_sector":id,"piso":floor,"familia":p["familia_similitud"],
         "tipo_cobertura":"fuera_de_tesela",
         "fraccion_poligono_9k_dentro_tesela":area,
         "pixeles_validos_270m":None,"altitud_mediana_m_270m":None,
         "pendiente_p90_270m":None,"aspecto_dominante_270m":None,
         "fraccion_aspecto_dominante_270m":None,
         "zona_homogenea_validada":False,"riesgo_fitosanitario_validado":False}
   for scale in SCALES:
    for t in LIMITS:desc[f"compatible_{scale*90}m_{t}"]=None
   desc.update({"sensibilidad_30grados_abs_270_vs_450":None,"n_piezas_270m_30":None})
   if intersect.is_empty or area<0.001:
    results.append(desc);continue
   r3=calculate(ds,intersect,3,mode=floor)
   r5=calculate(ds,intersect,5,mode=floor)
   if not r3 or not r5:
    desc["tipo_cobertura"]="insuficiente_pixeles"
    results.append(desc);continue
   desc["tipo_cobertura"]="completa" if area>=0.995 else "parcial"
   desc.update({"pixeles_validos_270m":r3["pixeles"],
    "altitud_mediana_m_270m":r3["alt_mediana"],
    "pendiente_p90_270m":r3["slope_p90"],
    "aspecto_dominante_270m":r3["dominante"],
    "fraccion_aspecto_dominante_270m":r3["f_aspecto"]})
   for scale,r in ((270,r3),(450,r5)):
    for t in LIMITS:desc[f"compatible_{scale}m_{t}"]=r["limites"][str(t)]["fraccion"]
   desc["sensibilidad_30grados_abs_270_vs_450"]=round(abs(
       r3["limites"]["30"]["fraccion"]-r5["limites"]["30"]["fraccion"]),5)
   compatible=r3["limites"]["30"]["mask"]
   polys=[]
   if compatible.sum()>=4:
    for g,v in shapes(compatible.astype("uint8"),mask=compatible,transform=r3["transform"]):
     if int(v)==1:
      part=clean(shape(g).intersection(intersect))
      if not part.is_empty:
       # no simplificar hacia afuera del polígono referencial
       part=clean(part.simplify(.00016,preserve_topology=True).intersection(intersect))
       polys.extend(parts(part))
   kept=clean(unary_union(polys)) if polys else None
   count=len(parts(kept)) if kept is not None else 0
   desc["n_piezas_270m_30"]=count
   if kept is not None and not kept.is_empty:
    features.append({"type":"Feature","geometry":mapping(kept),
       "properties":{"id_sector_9k":id,"piso":floor,"familia":p["familia_similitud"],
        "tipo_cobertura_tesela":desc["tipo_cobertura"],
        "fraccion_fisica_filtrada_270m_30":desc["compatible_270m_30"],
        "n_piezas":count,"orientacion_dominante":desc["aspecto_dominante_270m"],
        "zona_homogenea_validada":False,"cuenca_certificada":False,
        "prediccion_zonal_validada":False}})
   results.append(desc)
 total=Counter(r["tipo_cobertura"] for r in results)
 processed=[r for r in results if r["tipo_cobertura"] in ("completa","parcial")]
 sensitivity=[r["sensibilidad_30grados_abs_270_vs_450"] for r in processed]
 fcount=Counter(r["piso"] for r in processed)
 state={"fase":"9M","corte":"2026-10-17",
  "metodo":"Auditoria de franja altitudinal, pendiente, aspecto e incertidumbre a 270/450 m usando una tesela GLO-90 original; NO mapa regional completo.",
  "n_sectores_9k":42,"n_sector_evaluados_con_dos_escalas":len(processed),
  "estado_cobertura":dict(sorted(total.items())),
  "por_piso_evaluados":dict(sorted(fcount.items())),
  "n_geometrias_refinadas":len(features),
  "n_fuentes_cog_territoriales":1,
  "limite_territorial_de_prueba":"tesela S07 W080, lat -7..-6 lon -80..-79",
  "comparacion_resoluciones_m": [270,450],
  "umbrales_pendiente_grados":[20,30,40],
  "desnivel_max_zona_operativa":None,
  "resumen_cambio_fraccion_30grados_270_450":{
   "min":round(min(sensitivity),5) if sensitivity else None,
   "mediana":round(float(np.median(sensitivity)),5) if sensitivity else None,
   "max":round(max(sensitivity),5) if sensitivity else None},
  "filtro_altitud_por_celda_raster_no_por_altitud_unica_del_nodo":True,
  "aspecto_orientacion_terreno_no_viento_ni_radiacion":True,
  "indicador_area_agricola":False,
  "n_cuencas_ANA_certificadas":0,
  "n_zonas_homogeneas_certificadas":0,
  "downscaling_nmme_entrenado":False,
  "alerta_fitosanitaria_generada":False,
  "capa_9k_sha256":filehash(SECTORS),
  "dem_original_9l_sha256":filehash(SOURCE),
  "nota":"La sensibilidad es diferencia de FRACCIONES de píxeles muestreados entre resoluciones, sin observación meteorológica independiente; valores de sectores parciales no caracterizan el polígono completo.",
  "limitaciones":["No se extrapola fuera de la tesela Copernicus archivada.",
    "La orientación es dirección de máxima pendiente hacia abajo derivada del DSM, sin validar exposición solar o drenaje.",
    "Las pendientes son aproximadas sobre grados de lat/lon con distancias geográficas locales.",
    "No se deducen áreas agrícolas, límites administrativos oficiales ni riesgo de arándano/vid.",
    "La clasificación de píxeles depende de celdas promediadas, vecinos y resolución; no es aptitud agronómica."]}
 return {"type":"FeatureCollection","name":"OAF 9M: sectores filtrados de la tesela S07 W080, no oficiales",
   "metadata":{"fase":"9M","fuente":"Copernicus GLO90 9L","validacion_instrumental":False,
     "limite_oficial":False,"cuencas_certificadas":0},
   "features":features},state,results

def run(check=False):
 geo,state,rows=measure()
 if check:
  if json.loads(GEO.read_text("utf8"))!=json.loads(json.dumps(geo)):
   raise ValueError("GeoJSON 9M no se reproduce")
  if json.loads(STATE.read_text("utf8"))!=state:
   raise ValueError("Estado 9M no se reproduce")
  with CSV.open(newline="",encoding="utf-8") as f: saved=list(csv.DictReader(f))
  if len(saved)!=len(rows):raise ValueError("Tabla 9M incompleta")
 else:
  BASE.mkdir(parents=True,exist_ok=True)
  GEO.write_text(json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
  STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  with CSV.open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader();w.writerows(rows)
 print("9M relieve:",state["n_sector_evaluados_con_dos_escalas"],
       "de 42 sectores; COG original conservado;",
       state["n_geometrias_refinadas"],"máscaras.")
 return state

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 run(check=p.parse_args().check)
