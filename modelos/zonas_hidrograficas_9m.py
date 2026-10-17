#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9M: verificar unidades hidrográficas ANA desde capa publicada en IDEP.
Separa geometrías *referenciales* del acto de validar cuencas oficialmente.
Tolerar falta de acceso sin convertir el error en ausencia de cuencas.
No inferir que una 'subcuenca' sea apta para un cultivo.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from shapely.geometry import shape,mapping,box
from shapely import make_valid
from shapely.ops import unary_union,transform
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/sensibilidad_9m"
STATE=BASE/"estado_cuencas_ana_9m.json"
OVERLAY=BASE/"cruces_hidrograficos_9m.geojson"
RAW=BASE/"fuentes/idep_ana_unidades_hidrograficas_9m.geojson.gz"
SECTORS=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
ENDPOINT=("https://www.idep.gob.pe/geoportal/rest/services/"
          "INSTITUCIONALES/ANA_WMS/FeatureServer/7/query")
BOX=[-80.70,-7.25,-79.00,-5.40]
ARG={"where":"1=1","geometry":",".join(map(str,BOX)),
     "geometryType":"esriGeometryEnvelope","inSR":"4326",
     "spatialRel":"esriSpatialRelIntersects",
     "outFields":"OBJECTID_1,CODIGO,NOMBRE,NIVEL5,NIVEL6,NIVEL7,NOMB_UH_N6,NOMB_UH_N7",
     "outSR":"4326","returnGeometry":"true","f":"geojson",
     "resultRecordCount":"1000"}
URL=ENDPOINT+"?"+urlencode(ARG)
PROJ=Transformer.from_crs("EPSG:4326","EPSG:32717",always_xy=True).transform
UNPROJ=Transformer.from_crs("EPSG:32717","EPSG:4326",always_xy=True).transform

def sha(data):return hashlib.sha256(data).hexdigest()
def polygon(x):
 if not x.is_valid:x=make_valid(x)
 if x.geom_type in ("Polygon","MultiPolygon"):return x
 parts=[g for g in getattr(x,"geoms",[]) if g.geom_type in ("Polygon","MultiPolygon")]
 return unary_union(parts) if parts else None
def fetch():
 if RAW.exists():
  raw=gzip.decompress(RAW.read_bytes())
  if len(raw)>10_000_000:raise ValueError("Fuente cacheada demasiado grande")
  return raw
 req=Request(URL,headers={"User-Agent":"OAF-9M-regional-zoning/1.0"})
 with urlopen(req,timeout=65) as r:
  raw=r.read(10_000_001)
 if not 100<len(raw)<=10_000_000:raise ValueError("Respuesta institucional fuera de tamaño")
 j=json.loads(raw)
 if j.get("type")!="FeatureCollection" or not isinstance(j.get("features"),list):
  raise ValueError("Servicio no entregó GeoJSON: "+str(j.get("error",""))[:200])
 if len(j["features"])>=1000:raise ValueError("Posible paginación >1000, no declarar cobertura")
 if len(j["features"])<1:raise ValueError("GeoJSON ANA sin unidades retornadas")
 if not any(k in f.get("properties",{}) for f in j["features"] for k in ("CODIGO","NOMBRE","NIVEL6")):
  raise ValueError("El origen carece de identificadores hidrográficos")
 RAW.parent.mkdir(parents=True,exist_ok=True)
 RAW.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
 return raw
def derive(raw):
 src=json.loads(raw)
 if src.get("type")!="FeatureCollection":raise ValueError("Datos ANA no son GeoJSON")
 sectors=json.loads(SECTORS.read_text("utf8"))["features"]
 if len(sectors)!=42:raise ValueError("9K modificado")
 units=[];bad=0
 for f in src["features"]:
  g=f.get("geometry");pr=f.get("properties") or {}
  if not g:bad+=1;continue
  try:poly=polygon(shape(g))
  except (TypeError,ValueError):bad+=1;continue
  if poly is None or poly.is_empty:bad+=1;continue
  ident=next((str(pr[k]).strip() for k in ("CODIGO","NIVEL7","NIVEL6","OBJECTID_1")
              if pr.get(k) not in (None,"")),None)
  if not ident:bad+=1;continue
  units.append((ident,str(pr.get("NOMBRE") or pr.get("NOMB_UH_N7") or "Unidad sin nombre"),
                transform(PROJ,poly),pr))
 records=[]
 connections={}
 covered=0
 for sf in sectors:
  sid=sf["properties"]["id_sector"];base=transform(PROJ,shape(sf["geometry"]))
  intersections=[]
  for unit,nombre,poly,pr in units:
   if not base.intersects(poly):continue
   part=base.intersection(poly)
   if part.is_empty or part.area<10000:continue # < 0.01 km², bajo escala SIG
   intersections.append((unit,nombre,part,pr))
  if not intersections:continue
  # Union geométrica para evitar sumas dobles entre jerarquías superpuestas.
  coverage=unary_union([z[2] for z in intersections])
  cover_ratio=min(1.0,coverage.area/base.area)
  # Nunca confundir la unidad con 'cuenca operativa certificada'
  report=sorted(intersections,key=lambda x:(-x[2].area,x[0]))
  connections[sid]={
   "n_referencias_hidrograficas":len(report),
   "fraccion_geometrica_cubierta":round(cover_ratio,5),
   "codigo_principal_por_interseccion":report[0][0],
   "coincidencia_no_es_validacion_de_cuenca":True
  }
  for unit,nombre,part,pr in report:
   brief=polygon(transform(UNPROJ,part).simplify(.00025,preserve_topology=True))
   if brief is None or brief.is_empty:continue
   if len(records)>=800:
    raise ValueError("Demasiados cruces, limitar o segmentar consulta antes de publicar")
   records.append({"type":"Feature","geometry":mapping(brief),
       "properties":{"sector_9k":sid,"codigo_referencial":unit,
         "nombre_en_capa":nombre[:100],
         "area_interseccion_aproximada_km2":round(part.area/1e6,3),
         "nivel_6_capa":str(pr.get("NIVEL6") or ""),
         "nivel_7_capa":str(pr.get("NIVEL7") or ""),
         "fuente":"IDEP INSTITUCIONALES/ANA_WMS/FeatureServer/7",
         "unidad_territorial_certificada_para_oaf":False,
         "homogeneidad_agroclimatica_validada":False}})
  covered+=1
 meta={"fase":"9M","fecha_corte":"2026-10-17",
   "servidor":"www.idep.gob.pe / INSTITUCIONALES/ANA_WMS/FeatureServer/7",
   "capa":"Unidades Hidrográficas","consulta":URL,
   "sha256_original":sha(raw),"n_unidades_devueltas":len(src["features"]),
   "n_unidades_geometricas_elegibles":len(units),
   "n_registros_sin_geometria_valida":bad,
   "n_sectores_9k_con_interseccion":covered,
   "n_intersecciones_referenciales":len(records),
   "n_sectores_9k_no_cruzados":42-covered,
   "cobertura_institucional_capa_descargada":True,
   "verificacion_de_vigencia_limites_ANA":False,
   "n_cuencas_certificadas_por_oaf":0,
   "n_zonas_homogeneas_declaradas":0,
   "sin_duplicacion_de_area_entre_niveles":True,
   "asignacion_sectores":connections,
   "alertas_fitosanitarias_habilitadas":False,
   "cautelas":["La procedencia institucional de la capa no acredita actualización, escala oficial a parcela ni delimitación de cultivo.",
       "Algunos códigos pueden referirse a distintos niveles de jerarquía: cruzar geometrías no implica una unidad exclusiva.",
       "El mapa conserva únicamente las intersecciones de más de 0,01 km², simplificadas para pantalla.",
       "Se requiere ratificar vigencia y versión con ANA/IDEP antes de segmentación operativa."]}
 return {"type":"FeatureCollection",
         "metadata":{"fase":"9M","capas_hidrograficas_certificadas":False,
                     "fuente_url":URL,"conteo":len(records)},"features":records},meta

def main(check=False,allow_network=True):
 error=None;overlay=None
 try:
  if not RAW.exists() and not allow_network:raise ValueError("Sin archivo crudo de capa institucional")
  raw=fetch()
  overlay,meta=derive(raw)
 except Exception as e:
  error=f"{type(e).__name__}: {e}"[:300]
  overlay={"type":"FeatureCollection",
       "metadata":{"fase":"9M","capas_hidrograficas_certificadas":False,
                   "fuente_url":URL,"conteo":0},"features":[]}
  meta={"fase":"9M","fecha_corte":"2026-10-17",
    "servidor":"www.idep.gob.pe / INSTITUCIONALES/ANA_WMS/FeatureServer/7",
    "capa":"Unidades Hidrográficas","consulta":URL,
    "n_unidades_devueltas":0,"n_sectores_9k_con_interseccion":0,
    "n_intersecciones_referenciales":0,
    "cobertura_institucional_capa_descargada":False,
    "verificacion_de_vigencia_limites_ANA":False,
    "n_cuencas_certificadas_por_oaf":0,
    "n_zonas_homogeneas_declaradas":0,
    "alertas_fitosanitarias_habilitadas":False,
    "problema_acceso":error,
    "nota":"Falló el servicio; esto no significa que no existan cuencas."}
 if check:
  if json.loads(STATE.read_text("utf8"))!=meta:raise ValueError("Estado ANA no reproducible")
  if json.loads(OVERLAY.read_text("utf8"))!=json.loads(json.dumps(overlay)):
   raise ValueError("Geometrías ANA no reproducibles")
 else:
  BASE.mkdir(parents=True,exist_ok=True)
  STATE.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  OVERLAY.write_text(json.dumps(overlay,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 print("9M IDEP-ANA:",meta["n_unidades_devueltas"],"geometrías;",
       meta["n_sectores_9k_con_interseccion"],"sectores;",error or "sin error")
 return meta
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true")
 opts=ap.parse_args()
 main(check=opts.check,allow_network=not opts.check)
