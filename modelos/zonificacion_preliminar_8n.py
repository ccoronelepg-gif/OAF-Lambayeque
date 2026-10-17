#!/usr/bin/env python3
"""OAF 8N: DEM de muestreo regional y PRE-estratificación altitudinal.

Los estratos NO constituyen zonas agroclimáticas homogéneas validadas.
La cartografía referencial simplificada proviene de un repositorio público
secundario; requiere contrastación con límites oficiales IGN/INEI.
Las elevaciones consultadas a Open-Meteo son DEM (no termómetros).
No genera predicciones, riesgo fitosanitario o altitud de parcelas.
Python estándar 3.11; sin dependencias GIS externas.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
BOUNDARY="datos/zonificacion_8n/limite_lambayeque_referencial.geojson"
RAW="datos/zonificacion_8n/elevacion_fuentes"
OUT="datos/zonificacion_8n"
DEG=0.125
BATCH=50
ELEV_API="https://api.open-meteo.com/v1/elevation"
BANDS=((0,100,"planicie_muy_baja"),(100,300,"planicie_valle_interior"),
       (300,800,"piedemonte"),(800,1600,"ladera_baja"),
       (1600,2500,"ladera_media"),(2500,9000,"zona_alta_andina"))
POINT_FIELDS=("id","latitud","longitud","altitud_dem_m",
   "estrato_altitudinal_preliminar","clima_homogeneo_validado",
   "clase_geografica_no_equivale_a_prediccion")
REGION_PROPERTIES={"nombre":"LAMBAYEQUE","codigo_ubigeo":"14"}

def sha(blob):return hashlib.sha256(blob).hexdigest()

def coord_num(x):return float(round(x,5))

def geom(root):
    path=root/BOUNDARY
    blob=path.read_bytes()
    obj=json.loads(blob)
    if obj.get("type")!="FeatureCollection" or len(obj.get("features",[]))!=1:
        raise ValueError("Cartografía no corresponde a un polígono documental único")
    f=obj["features"][0]
    if f.get("properties",{}).get("codigo_ubigeo")!="14" or f.get("properties",{}).get("nombre")!="LAMBAYEQUE":
        raise ValueError("Límite no identifica Lambayeque de manera inequívoca")
    g=f["geometry"]
    if g["type"]=="Polygon":parts=[g["coordinates"]]
    elif g["type"]=="MultiPolygon":parts=g["coordinates"]
    else:raise ValueError("Se requiere superficie regional con anillos geográficos")
    for p in parts:
        for ring in p:
            if len(ring)<4 or ring[0]!=ring[-1]:
                raise ValueError("Anillo regional no cerrado")
            for x,y in ring:
                if not -82<=x<=-77 or not -9<=y<=-4:
                    raise ValueError("Coordenadas cartográficas fuera de Lambayeque")
    return parts,sha(blob)

def inside_ring(x,y,ring):
    ok=False
    for (a,b),(c,d) in zip(ring,ring[1:]):
        if ((b>y)!=(d>y)) and (x<(c-a)*(y-b)/(d-b)+a):
            ok=not ok
    return ok

def inside(x,y,multi):
    return any(inside_ring(x,y,part[0]) and not any(inside_ring(x,y,h) for h in part[1:])
               for part in multi)

def grid(root):
    multi,_=geom(root)
    pts=[(x,y) for shape in multi for ring in shape for x,y in ring]
    lon0,lat0=min(x for x,y in pts),min(y for x,y in pts)
    lon1,lat1=max(x for x,y in pts),max(y for x,y in pts)
    # Anchored, deterministic grid centers. No claim of full pixel coverage.
    lons=[-81+i*DEG for i in range(32)]
    lats=[-8+i*DEG for i in range(32)]
    out=[]
    for lat in lats:
        for lon in lons:
            if lon0<=lon<=lon1 and lat0<=lat<=lat1 and inside(lon,lat,multi):
                out.append({"id":f"P{len(out)+1:03d}","latitud":coord_num(lat),
                            "longitud":coord_num(lon)})
    if len(out)<30 or len(out)>320:
        raise ValueError("Malla territorial anómala: revisar límite y grado de muestreo")
    return out

def batches(root):
    pts=grid(root)
    return [pts[i:i+BATCH] for i in range(0,len(pts),BATCH)]

def request_url(points):
    coords={"latitude":",".join(str(p["latitud"]) for p in points),
            "longitude":",".join(str(p["longitud"]) for p in points)}
    return ELEV_API+"?"+urlencode(coords)

def raw_path(root,i):return root/RAW/f"lote_{i:02d}.json.gz"
def meta_path(root,i):return root/RAW/f"lote_{i:02d}.meta.json"

def payload_check(raw,points):
    payload=json.loads(raw)
    elev=payload.get("elevation") if isinstance(payload,dict) else None
    if not isinstance(elev,list) or len(elev)!=len(points):
        raise ValueError("DEM API: cantidad de elevaciones incompatible")
    for a in elev:
        if type(a) not in (int,float) or not math.isfinite(a) or not -100<=a<=6500:
            raise ValueError("DEM API: altitud fuera de rango o faltante")
    return [float(z) for z in elev]

def inspect(root,i,group):
    f=raw_path(root,i);m=meta_path(root,i)
    if not f.exists() and not m.exists():return None
    if not f.exists() or not m.exists():raise ValueError("Lote DEM incompleto")
    raw=gzip.decompress(f.read_bytes())
    meta=json.loads(m.read_text(encoding="utf-8"))
    if (meta.get("fase")!="8N" or meta.get("api")!=ELEV_API or
        meta.get("url")!=request_url(group) or
        meta.get("puntos")!=[p["id"] for p in group] or
        meta.get("sha256_json_original")!=sha(raw) or
        meta.get("fuente_de_elevacion")!="Open-Meteo Elevation API; DEM, no instrumento"):
        raise ValueError("Integridad o parámetros geográficos del DEM incorrectos")
    return payload_check(raw,group)

def get(url):
    for attempt in range(2):
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-8N-regional-elevation-research/1.0"}),
                         timeout=50) as f:
                if f.status!=200:raise ValueError("HTTP "+str(f.status))
                data=f.read(200001)
            if len(data)>200000:raise ValueError("DEM demasiado grande")
            json.loads(data)
            return data
        except HTTPError as e:
            if e.code==429:raise RuntimeError("HTTP 429 DEM: esperar próximo ciclo, sin forzar consultas") from e
            if attempt==1:raise
        except (URLError,ValueError,TimeoutError,OSError,json.JSONDecodeError):
            if attempt==1:raise
        time.sleep(3)
    raise RuntimeError("DEM no disponible")

def fetch(root,max_new_batches=2):
    groups=batches(root)
    folder=root/RAW
    folder.mkdir(parents=True,exist_ok=True)
    count=0
    for index,points in enumerate(groups,1):
        if inspect(root,index,points) is not None:continue
        if count>=max_new_batches:break
        url=request_url(points)
        raw=get(url)
        payload_check(raw,points)
        meta={
          "fase":"8N","api":ELEV_API,"url":url,
          "fuente_de_elevacion":"Open-Meteo Elevation API; DEM, no instrumento",
          "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
          "puntos":[p["id"] for p in points],
          "sha256_json_original":sha(raw),"cartografia_es_referencial":True
        }
        raw_path(root,index).write_bytes(gzip.compress(raw,mtime=0))
        meta_path(root,index).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        count+=1
        print("DEM lote verificado",index,"de",len(groups),flush=True)
    print("Lotes DEM nuevos:",count)

def band(z):
    if z<0:return "cota_negativa_dem_verificar"
    for lo,hi,label in BANDS:
        if lo<=z<hi:return label
    raise ValueError("DEM fuera del intervalo de clasificación")

def csv_text(rows,fields):
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    for item in rows:writer.writerow(item)
    return stream.getvalue()

def calculate(root):
    points=grid(root)
    groups=batches(root)
    _,bh=geom(root)
    data=[]
    present=0
    for i,g in enumerate(groups,1):
        values=inspect(root,i,g)
        if values is None:continue
        present+=1
        for p,z in zip(g,values):
            data.append({**p,"altitud_dem_m":z,
                         "estrato_altitudinal_preliminar":band(z),
                         "clima_homogeneo_validado":"false",
                         "clase_geografica_no_equivale_a_prediccion":"true"})
    inventory={}
    for l in [b[2] for b in BANDS]+["cota_negativa_dem_verificar"]:
        entries=[x for x in data if x["estrato_altitudinal_preliminar"]==l]
        inventory[l]={"n_puntos_dem":len(entries),
                      "alt_min_m":min((x["altitud_dem_m"] for x in entries),default=None),
                      "alt_max_m":max((x["altitud_dem_m"] for x in entries),default=None),
                      "zona_climatica_homogenea_demostrada":False,
                      "apto_para_pronostico_por_zona":False}
    summary={
      "fase":"8N","estado":("malla_dem_completa_solo_estratificacion_fisica" if len(data)==len(points)
                      else "malla_dem_parcial_no_permite_cobertura_regional" if data
                      else "pendiente_elevaciones_dem"),
      "region":"Lambayeque","nodos_en_malla_regional_referencial":len(points),
      "nodos_con_elevacion_dem_verificada":len(data),
      "n_lotes_dem_esperados":len(groups),
      "n_lotes_dem_archivados":present,
      "cobertura_puntual_completa":len(data)==len(points),
      "puntos_son_centros_de_muestreo_no_poligonos":True,
      "cobertura_espacial_polinomio_porcentual_certificada":False,
      "clasificacion":"estratos_altitudinales_candidatos_NO_zonas_agroclimaticas_homogeneas",
      "homogeneidad_climatica_estadistica_demostrada":False,
      "pronosticos_8e_recalibrados":False,
      "validacion_instrumental_SENAMHI":False,
      "zonas_operativas_aprobadas":0,
      "umbrales_altitudinales_preliminares_m":[[a,b,lab] for a,b,lab in BANDS],
      "estratos":inventory,
      "condiciones_pendientes_para_zonas_homogeneas":[
        "Confirmar límite regional vigente con INEI/IGN y ajustar celdas limítrofes.",
        "Cruzar topografía con exposición, distancia real al mar, cuencas y laderas.",
        "Obtener climatologías 1996–2025 por nodo de T2m, Tmax/Tmin, precipitación, humedad, radiación y ET0 con misma procedencia temporal.",
        "Agrupar similitud climática con escalamiento documentado, validación espacial por bloques y continuidad geográfica.",
        "Verificar cambio de régimen costa/valle/piedemonte/Andes y umbrales en estaciones SENAMHI cuando existan registros.",
        "Para pronosticar, entrenar modelos por zona con evaluación retrospectiva y prospectiva sin fuga temporal."
      ],
      "limite_regional_fuente":"juaneladio/peru-geojson, límite simplificado histórico NO oficial validado 2026; capa de cribado",
      "elevacion_fuente":"Open-Meteo Elevation API, DEM de referencia, no sensor real",
      "toda_lambayeque_no_cubierta_por_8m":True,
      "trazabilidad":{"limite_sha256":bh,
        "lotes":[{"lote":i,"hash":sha(raw_path(root,i).read_bytes())}
                 for i,g in enumerate(groups,1) if raw_path(root,i).exists()] }
    }
    return summary,data,points

def publish(root,check=False):
    state,rows,centers=calculate(root)
    folder=root/OUT
    output={
     folder/"estado_8n.json":json.dumps(state,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
     folder/"nodos_altitudinales_8n.csv":csv_text(rows,POINT_FIELDS),
     folder/"malla_geografica_8n.csv":csv_text(centers,("id","latitud","longitud")),
    }
    if not check:folder.mkdir(parents=True,exist_ok=True)
    for p,s in output.items():
        if check:
            if not p.exists() or p.read_text(encoding="utf-8")!=s:
                raise ValueError("Estado 8N desincronizado con DEM y límite regional")
        elif not p.exists() or p.read_text(encoding="utf-8")!=s:
            p.write_text(s,encoding="utf-8")
    print(json.dumps({"fase":"8N","nodos":len(centers),
      "cargados":len(rows),"estado":state["estado"],"check":check},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--fetch-elevations",action="store_true")
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--max-new-batches",type=int,default=2)
    x=parser.parse_args()
    if x.fetch_elevations:fetch(x.root,x.max_new_batches)
    publish(x.root,x.check)
