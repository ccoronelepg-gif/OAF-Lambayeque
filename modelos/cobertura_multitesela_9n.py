#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9N: cobertura multi-tesela Copernicus GLO90, pendiente y orientación.
La ausencia de una tesela se registra como falta de datos, NUNCA como terreno plano.
Los valores por píxel son del DSM y no certifican microclimas ni aptitud agrícola.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.features import rasterize, shapes
from rasterio.windows import from_bounds, transform as window_transform
from shapely import make_valid
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT / "datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
PREV_STATUS = ROOT / "datos/sensibilidad_9m/estado_relieve_9m.json"
BASE = ROOT / "datos/cobertura_multitesela_9n"
TILES = BASE / "fuentes"
ORIGINAL = ROOT / "datos/relieve_9l/fuentes/copernicus_glo90_s07_w080.tif"
ORIGINAL_STATUS = ROOT / "datos/relieve_9l/estado_relieve_9l.json"
STATE = BASE / "estado_cobertura_9n.json"
GEO = BASE / "mascaras_multitesela_9n.geojson"
MANIFEST = BASE / "fuentes_dem_9n.json"
MISSING = BASE / "teselas_no_disponibles_9n.json"
BASE_URL = "https://copernicus-dem-90m.s3.amazonaws.com"
FLOORS = {
    "llanura_costa": (0,100), "valle_bajo": (100,300),
    "piedemonte": (300,800), "montana_baja": (800,1600),
    "montana_media": (1600,2500), "montana_alta": (2500,6500),
    "cota_negativa_revisar": (-100,0),
}
LEVELS = (20,30,40)
SCALES = (3,5)
TILE_LIMIT = 18_000_000
WESTERN_BOUND = (-81,-79)
SOUTHERN_BOUND = (-8,-5)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load_json(path):
    return json.loads(path.read_text(encoding="utf8"))

def tile_id(lat,lon):
    return ("S" if lat<0 else "N") + f"{abs(lat):02d}" + ("W" if lon<0 else "E") + f"{abs(lon):03d}"

def url_for(lat,lon):
    part=f"Copernicus_DSM_COG_30_{'S' if lat<0 else 'N'}{abs(lat):02d}_00_{'W' if lon<0 else 'E'}{abs(lon):03d}_00_DEM"
    return f"{BASE_URL}/{part}/{part}.tif"

def tile_inventory(features):
    found={}
    for f in features:
        b=shape(f["geometry"]).bounds
        for lat in range(math.floor(b[1]),math.floor(b[3])+1):
            for lon in range(math.floor(b[0]),math.floor(b[2])+1):
                if (SOUTHERN_BOUND[0]<=lat<=SOUTHERN_BOUND[1] and
                        WESTERN_BOUND[0]<=lon<=WESTERN_BOUND[1]):
                    token=tile_id(lat,lon)
                    if token not in found:
                        found[token]={"id":token,"lat":lat,"lon":lon,"url":url_for(lat,lon)}
    return dict(sorted(found.items()))

def inspect_tiff(raw,lat,lon):
    if len(raw)<20_000 or len(raw)>TILE_LIMIT:
        raise ValueError("Tamaño GeoTIFF inválido")
    with rasterio.MemoryFile(raw) as m, m.open() as ds:
        if ds.count!=1 or ds.crs.to_epsg()!=4326 or ds.width<500 or ds.height<500:
            raise ValueError("Tesela Copernicus no cumple CRS/bandas/dimensiones")
        b=ds.bounds
        if not (abs(b.left-lon)<.005 and abs(b.right-(lon+1))<.005
                and abs(b.bottom-lat)<.005 and abs(b.top-(lat+1))<.005):
            raise ValueError("La tesela no coincide con su cuadrante solicitado")
        return {"ancho":ds.width,"alto":ds.height,
                "crs":"EPSG:4326","bounds":[b.left,b.bottom,b.right,b.top]}

def obtain_sources(tiles,allow_download=True):
    previous=load_json(ORIGINAL_STATUS)
    if digest(ORIGINAL.read_bytes())!=previous["sha256_tiff_original"]:
        raise ValueError("Copernicus 9L original no coincide con su SHA-256")
    sources={}
    details=[]
    failures=[]
    for key,t in tiles.items():
        path=(ORIGINAL if key=="S07W080" else TILES/f"{key}.tif")
        url=t["url"]
        if path.exists():
            raw=path.read_bytes()
            mode="congelado_9L" if key=="S07W080" else "congelado_9N"
        elif allow_download:
            try:
                request=Request(url,headers={"User-Agent":"OAF-Lambayeque-9N-science/1.0"})
                with urlopen(request,timeout=75) as req:
                    raw=req.read(TILE_LIMIT+1)
                meta=inspect_tiff(raw,t["lat"],t["lon"])
                TILES.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
                mode="descarga_archivada_9N"
            except (HTTPError,URLError,TimeoutError,ValueError) as err:
                failures.append({"id":key,"url":url,
                                 "razon":f"{type(err).__name__}: {err}"[:250],
                                 "no_inferir_elevacion_cero":True})
                continue
        else:
            failures.append({"id":key,"url":url,
                             "razon":"Sin copia cruda local conservada",
                             "no_inferir_elevacion_cero":True})
            continue
        meta=inspect_tiff(raw,t["lat"],t["lon"])
        item={**t,**meta,"bytes":len(raw),"sha256":digest(raw),
              "procedencia":mode,"path":str(path.relative_to(ROOT))}
        sources[key]=item
        details.append(item)
    return sources,details,failures

def parts(poly):
    if not poly.is_valid:
        poly=make_valid(poly)
    if poly.geom_type=="Polygon":
        return [poly] if poly.area>0 else []
    if hasattr(poly,"geoms"):
        out=[]
        for sub in poly.geoms:
            out.extend(parts(sub))
        return out
    return []

def read_tile(ds,poly,scale,floor):
    """Leer dentro de una tesela, con margen suficiente para pendiente válida."""
    outer=box(*ds.bounds)
    clip=poly.intersection(outer)
    if clip.is_empty or clip.area<1e-12:
        return None
    margin=abs(ds.transform.a)*scale*2
    envelope=box(clip.bounds[0]-margin,clip.bounds[1]-margin,
                 clip.bounds[2]+margin,clip.bounds[3]+margin).intersection(outer)
    if envelope.is_empty:return None
    win=from_bounds(*envelope.bounds,transform=ds.transform).round_offsets().round_lengths()
    iw,ih=round(win.width),round(win.height)
    if iw<4 or ih<4 or iw>1700 or ih>1700:
        return None
    W=max(3,math.ceil(iw/scale))
    H=max(3,math.ceil(ih/scale))
    sample=ds.read(1,window=win,out_shape=(H,W),masked=True,
                   resampling=Resampling.average)
    values=np.ma.filled(sample,np.nan).astype("float64")
    trans=window_transform(win,ds.transform)*Affine.scale(iw/W,ih/H)
    terrain=np.isfinite(values)&(values>-200)&(values<6500)
    inside=rasterize([(mapping(clip),1)],out_shape=(H,W),
                     transform=trans,all_touched=False).astype(bool)
    measurement=terrain&inside
    if measurement.sum()<5:
        return None
    valid=terrain.copy()
    valid[0,:]=False;valid[-1,:]=False
    valid[:,0]=False;valid[:,-1]=False
    valid[1:,:]&=terrain[:-1,:]
    valid[:-1,:]&=terrain[1:,:]
    valid[:,1:]&=terrain[:,:-1]
    valid[:,:-1]&=terrain[:,1:]
    valid&=inside
    z=np.where(terrain,values,0)
    lat=clip.centroid.y
    dy=abs(trans.e)*111132.9
    dx=abs(trans.a)*111319.5*math.cos(math.radians(lat))
    ns,ew=np.gradient(z,dy,dx)
    slope=np.degrees(np.arctan(np.hypot(ns,ew)))
    aspect=(np.degrees(np.arctan2(-ew,ns))+360)%360
    direction=np.floor((aspect+45)%360/90).astype("uint8")
    lo,hi=FLOORS[floor]
    matches={}
    for threshold in LEVELS:
        matches[threshold]=valid&(values>=lo)&(values<hi)&(slope<=threshold)
    out={"count":int(measurement.sum()),"usable":int(valid.sum()),
         "sum_elev":float(np.sum(values[measurement])),
         "sum_slope":float(np.sum(slope[valid])),
         "n_elev":int(measurement.sum()),"count_dir":Counter(
              int(v) for v in direction[valid&(slope>=2)]),
         "counts":{t:int(matches[t].sum()) for t in LEVELS},
         "coverage_polygon":clip,
         "mask":matches[30] if scale==3 else None,
         "transform":trans}
    return out

def calculate(sources,features):
    geometries=[];rows=[]
    coverage_totals=Counter()
    tile_coverage=Counter()
    for f in sorted(features,key=lambda x:x["properties"]["id_sector"]):
        p=f["properties"]
        sid=p["id_sector"]
        floor=p["estrato"]
        if floor not in FLOORS:
            raise ValueError("Piso no registrado")
        original=shape(f["geometry"])
        results_by_scale={s:[] for s in SCALES}
        physically_covered=[]
        for t in sources.values():
            tf=box(t["lon"],t["lat"],t["lon"]+1,t["lat"]+1)
            segment=original.intersection(tf)
            if segment.is_empty or segment.area<1e-11:continue
            with rasterio.open(ROOT/t["path"]) as ds:
                r3=read_tile(ds,segment,3,floor)
                r5=read_tile(ds,segment,5,floor)
            if r3 is not None and r5 is not None:
                results_by_scale[3].append((t["id"],r3))
                results_by_scale[5].append((t["id"],r5))
                physically_covered.append(segment)
                tile_coverage[t["id"]]+=1
        covered_union=unary_union(physically_covered) if physically_covered else Polygon()
        covered_ratio=min(1,covered_union.area/original.area) if original.area else 0
        coverage=("completa" if covered_ratio>=.995 else
                  "parcial" if covered_ratio>=.001 else "sin_dem")
        row={"id_sector":sid,"piso_nominal":floor,
             "familia_preliminar":p["familia_similitud"],
             "cobertura":coverage,
             "fraccion_geometrica_teselas_leidas":round(covered_ratio,5),
             "n_teselas_con_datos":len(results_by_scale[3]),
             "n_pixeles_270m":None,"n_pixeles_450m":None,
             "compatible_270m_20":None,"compatible_270m_30":None,"compatible_270m_40":None,
             "compatible_450m_20":None,"compatible_450m_30":None,"compatible_450m_40":None,
             "diferencia_abs_30_270_vs_450":None,
             "altitud_media_dem_270":None,"pendiente_media_270":None,
             "orientacion_frecuente_270":None,"fragmentos_fisicos_270_30":None,
             "zona_homogenea_instrumental_validada":False,
             "cuenca_operativa_certificada":False}
        coverage_totals[coverage]+=1
        if not results_by_scale[3]:
            rows.append(row);continue
        for scale in SCALES:
            samples=[q for _,q in results_by_scale[scale]]
            denom=sum(q["count"] for q in samples)
            if denom==0:raise ValueError("Pixeles DEM contados nulos")
            row[f"n_pixeles_{scale*90}m"]=denom
            for threshold in LEVELS:
                row[f"compatible_{scale*90}m_{threshold}"]=round(
                    sum(q["counts"][threshold] for q in samples)/denom,5)
            if scale==3:
                row["altitud_media_dem_270"]=round(
                   sum(q["sum_elev"] for q in samples)/denom,2)
                sl_n=sum(q["usable"] for q in samples)
                row["pendiente_media_270"]=round(
                   sum(q["sum_slope"] for q in samples)/sl_n,2) if sl_n else None
                c=Counter()
                for q in samples:c.update(q["count_dir"])
                row["orientacion_frecuente_270"]=(
                    "NESO"[sorted(c,key=lambda d:(-c[d],d))[0]] if c else None)
        row["diferencia_abs_30_270_vs_450"]=round(
            abs(row["compatible_270m_30"]-row["compatible_450m_30"]),5)
        pixgeom=[]
        for _tile,q in results_by_scale[3]:
            mask=q["mask"]
            if mask is None or int(mask.sum())<4:continue
            for gg,val in shapes(mask.astype("uint8"),mask=mask,transform=q["transform"]):
                if int(val)!=1:continue
                clip=shape(gg).intersection(q["coverage_polygon"])
                pixgeom.extend(parts(clip))
        if pixgeom:
            union=unary_union(pixgeom)
            row["fragmentos_fisicos_270_30"]=len(parts(union))
            if len(pixgeom)>3000:
                raise ValueError("Más de 3000 piezas para un solo sector, revisar resolución")
            if not union.is_valid:union=make_valid(union)
            # Almacenamiento de geometrías piloto, simplificadas para web sin ampliar fronteras.
            union=union.simplify(.00013,preserve_topology=True).intersection(original)
            if not union.is_valid:union=make_valid(union)
            polys=parts(union)
            if polys:
                geometries.append({"type":"Feature","geometry":mapping(unary_union(polys)),
                    "properties":{"sector_9k":sid,"piso":floor,
                     "familia":p["familia_similitud"],
                     "cobertura_dem":coverage,"fraccion_territorial_examinada":row["fraccion_geometrica_teselas_leidas"],
                     "fraccion_pixeles_filtrados":row["compatible_270m_30"],
                     "orientacion_mayoritaria":row["orientacion_frecuente_270"],
                     "n_piezas":row["fragmentos_fisicos_270_30"],
                     "limitacion":"NO representa aptitud agrícola ni homogeneidad climática",
                     "zona_homogenea_validada":False,"riesgo_fitosanitario_validado":False}})
        rows.append(row)
    if len(rows)!=42:raise ValueError("Inventario de sectores DEM incompleto")
    return rows,geometries,dict(sorted(coverage_totals.items())),dict(sorted(tile_coverage.items()))

def compute(allow_download=True):
    geo=load_json(PREV)
    if len(geo["features"])!=42:raise ValueError("Se perdió la base de 42 sectores 9K")
    manifest=tile_inventory(geo["features"])
    sources,details,failures=obtain_sources(manifest,allow_download)
    rows,shapes_out,counts,tcounts=calculate(sources,geo["features"])
    prev=load_json(PREV_STATUS)
    candidate=[r for r in rows if r["cobertura"]!="sin_dem"]
    differences=[r["diferencia_abs_30_270_vs_450"] for r in candidate]
    report={"fase":"9N","corte_peru":"2026-10-17",
        "proposito":"Completar cobertura GLO90 por teselas sin imputación falsa",
        "n_sectores_9k":42,"n_sectores_cobertura_completa":counts.get("completa",0),
        "n_sectores_cobertura_parcial":counts.get("parcial",0),
        "n_sectores_sin_dem":counts.get("sin_dem",0),
        "n_sectores_evaluables":len(candidate),
        "n_geometrias_filtro":len(shapes_out),
        "cobertura_por_estado":counts,
        "teselas_necesarias":len(manifest),"teselas_archivadas_validas":len(details),
        "teselas_no_disponibles":len(failures),
        "n_teselas_nuevas_validas":sum(t["id"]!="S07W080" for t in details),
        "n_teselas_reutilizadas_9L":int("S07W080" in sources),
        "resoluciones_de_evaluacion_aprox_m":[270,450],
        "umbrales_pendiente_grados":[20,30,40],
        "mediana_diferencia_30grados_resoluciones":round(float(np.median(differences)),5) if differences else None,
        "max_diferencia_30grados_resoluciones":round(max(differences),5) if differences else None,
        "comparacion_9M":{"n_sectores_evaluables_previamente":prev["n_sector_evaluados_con_dos_escalas"],
             "n_sectores_cobertura_completa_previamente":prev["estado_cobertura"]["completa"]},
        "cuencas_ana_oficialmente_ratificadas":0,
        "n_zonas_agroclimaticas_homogeneas_validadas":0,
        "ajuste_altitudinal_nmme_validado":False,
        "alertas_fitosanitarias_derivadas":False,
        "estado_fuentedem":"parcial_si_hay_teselas_ausentes" if failures else "todas_teselas_requeridas_almacenadas",
        "fragmentos_sensibles":sorted([
            {"sector":r["id_sector"],"diferencia":r["diferencia_abs_30_270_vs_450"],
             "piso":r["piso_nominal"],"cobertura":r["cobertura"]}
            for r in candidate],key=lambda v:-v["diferencia"])[:12],
        "advertencias":[
          "Teselas faltantes o zonas oceánicas sin teselas DEM son valores desconocidos, no cota cero.",
          "El DEM GLO90 es un DSM; la pendiente estimada no es de terreno desnudo ni determina cultivos.",
          "La agregación 270/450m y los límites 20/30/40° son pruebas metodológicas, no umbrales agronómicos.",
          "Una cobertura geométrica completa no equivale a cobertura de estaciones ni microclima validado.",
          "La comparación con 9M varía ligeramente al leer ventanas con márgenes de pendiente diferentes.",
          "No se extrapola una señal NOAA NMME 1° a sectores de montaña."] }
    dataset={"type":"FeatureCollection","name":"OAF 9N DEM multitesela en sectores 9K",
      "metadata":{"fase":"9N","origen":"Copernicus GLO90 2021",
        "homogeneidad_agroclimatica_validada":False,
        "cobertura_completa_no_es_aptitud_agronomica":True,
        "n_teselas":len(details)},"features":shapes_out}
    inventory={"fase":"9N","organizacion":"AWS Open Data Copernicus DEM GLO-90",
        "fuente":"https://registry.opendata.aws/copernicus-dem/",
        "teselas_requeridas":list(manifest.values()),
        "teselas_que_pudieron_abrirse":details,
        "teselas_que_no_pudieron_comprobarse":failures,
        "nota":"Los GeoTIFF originales se conservan íntegros con SHA-256, sin reemplazar los originales 9L."}
    return dataset,report,inventory,rows

def run(check=False):
    geo,report,inventory,rows=compute(allow_download=not check)
    if check:
        if load_json(GEO)!=json.loads(json.dumps(geo)):
            raise ValueError("Geometrías 9N no se reproducen")
        if load_json(STATE)!=report or load_json(MANIFEST)!=inventory:
            raise ValueError("Metadatos o manifiesto 9N no se reproducen")
        if len(load_json(MISSING))!=len(inventory["teselas_que_no_pudieron_comprobarse"]):
            raise ValueError("Faltantes de DEM sin inventario")
    else:
        BASE.mkdir(parents=True,exist_ok=True)
        GEO.write_text(json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
        STATE.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        MANIFEST.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        MISSING.write_text(json.dumps(inventory["teselas_que_no_pudieron_comprobarse"],ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("9N:",report["n_sectores_cobertura_completa"],"sectores completos;",
          report["n_sectores_cobertura_parcial"],"parciales;",
          report["n_sectores_sin_dem"],"sin DEM;",
          report["teselas_archivadas_validas"],"teselas abiertas")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    opts=ap.parse_args()
    run(check=opts.check)
