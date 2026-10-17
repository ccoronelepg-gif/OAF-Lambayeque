#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9L — Máscara de relieve continuo para núcleos 9K.
Fuente real Copernicus GLO-90 COG, recorte conservador.
No genera cuencas, límites oficiales, zonas homogéneas ni downscaling validado.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize, shapes
from rasterio.io import MemoryFile
from rasterio.windows import from_bounds, transform as window_transform
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import make_valid
from affine import Affine

ROOT=Path(__file__).resolve().parents[1]
PREVIOUS=ROOT/"datos/sectores_agroclimaticos_9k"
DEST=ROOT/"datos/relieve_9l"
F_SOURCE=DEST/"fuentes/copernicus_glo90_s07_w080.tif"
F_GEO=DEST/"nucleos_restringidos_relieve_9l.geojson"
F_STATE=DEST/"estado_relieve_9l.json"
F_BASE=PREVIOUS/"sectores_muestreo_9k.geojson"
F_META=PREVIOUS/"estado_sectores_9k.json"
F_FORECAST=PREVIOUS/"inventario_nmme_9k.json"
URL=("https://copernicus-dem-90m.s3.amazonaws.com/"
     "Copernicus_DSM_COG_30_S07_00_W080_00_DEM/"
     "Copernicus_DSM_COG_30_S07_00_W080_00_DEM.tif")
FLOORS={
 "llanura_costa":(0,100),"valle_bajo":(100,300),"piedemonte":(300,800),
 "montana_baja":(800,1600),"montana_media":(1600,2500),
 "montana_alta":(2500,6000),"cota_negativa_revisar":(-100,0)}
DOWNSAMPLE=3
MAX_SLOPE=30.0  # umbral EXPLORATORIO a ~270 m, no criterio normativo agroecológico

def sha(b):return hashlib.sha256(b).hexdigest()
def download():
    if F_SOURCE.exists():
        raw=F_SOURCE.read_bytes()
        if raw[:4] not in (b'II*\x00',b'MM\x00*'):raise ValueError("Original TIFF dañando")
        return raw
    req=Request(URL,headers={"User-Agent":"OAF-Lambayeque-9L-terrain/1.0"})
    with urlopen(req,timeout=100) as res:
        raw=res.read(50_000_001)
    if len(raw)>50_000_000 or len(raw)<100000 or raw[:4] not in (b'II*\x00',b'MM\x00*'):
        raise ValueError("Copernicus GeoTIFF no verificable o supera 50 MB")
    F_SOURCE.parent.mkdir(parents=True,exist_ok=True)
    F_SOURCE.write_bytes(raw)
    return raw

def clean(poly):
    if not poly.is_valid:poly=make_valid(poly)
    pieces=[]
    if poly.geom_type=="Polygon":pieces=[poly]
    elif hasattr(poly,"geoms"):
        for g in poly.geoms:
            if g.geom_type=="Polygon":pieces.append(g)
            elif g.geom_type=="MultiPolygon":pieces.extend(g.geoms)
    return unary_union([p for p in pieces if p.area>0]) if pieces else Polygon()

def measure(raw):
    source=json.loads(F_BASE.read_text("utf8"))
    state=json.loads(F_META.read_text("utf8"))
    if state["n_poligonos_graficos_exploratorios"]!=42 or len(source["features"])!=42:
        raise ValueError("9K alterado; no es reproducible")
    cores=[f for f in source["features"] if f["properties"]["familia_similitud"]]
    if len(cores)!=5 or sorted({p["properties"]["familia_similitud"] for p in cores})!=["C01","C02","C03"]:
        raise ValueError("Núcleos 9K no reconocidos")
    feats=[]
    with MemoryFile(raw) as handle, handle.open() as ds:
        if ds.crs.to_epsg()!=4326 or ds.count!=1:
            raise ValueError("COG sin WGS84 o múltiples bandas inesperadas")
        bounds=ds.bounds
        if not (bounds.left<=-79.60 and bounds.right>=-79.33
                and bounds.bottom<=-6.55 and bounds.top>=-6.08):
            raise ValueError("La tesela descargada no cubre los núcleos 9K")
        for f in sorted(cores,key=lambda v:v["properties"]["id_sector"]):
            p=f["properties"];polygon=shape(f["geometry"])
            if not polygon.is_valid:raise ValueError("Entrada de polígono 9K inválida")
            # El COG se lee a resolución nativa y se agrega a 3x (~270m)
            # para controlar fragmentación y coste. No es DEM de 30m.
            left,bottom,right,top=polygon.bounds
            win=from_bounds(left,bottom,right,top,ds.transform)
            win=win.round_offsets().round_lengths()
            iw,ih=round(win.width),round(win.height)
            if iw<3 or ih<3 or iw>2000 or ih>2000:
                raise ValueError("Ventana DEM fuera de escala prevista")
            H=max(3,math.ceil(ih/DOWNSAMPLE));W=max(3,math.ceil(iw/DOWNSAMPLE))
            data=ds.read(1,window=win,out_shape=(H,W),resampling=Resampling.average,
                         boundless=False,masked=True)
            z=np.ma.filled(data,np.nan).astype("float64")
            trans=window_transform(win,ds.transform)*Affine.scale(iw/W,ih/H)
            dem_ok=np.isfinite(z)&(z>-200)&(z<6500)
            mask=rasterize([(mapping(polygon),1)],out_shape=(H,W),
                           transform=trans,fill=0,all_touched=False).astype(bool)
            valid=mask&dem_ok
            if valid.sum()<10:raise ValueError("Menos de 10 píxeles del COG en "+p["id_sector"])
            # Resolver pendiente local aproximando distancias en lat/lon desde el centro:
            lat=polygon.centroid.y
            dy=abs(trans.e)*111132.9
            dx=abs(trans.a)*111319.5*math.cos(math.radians(lat))
            zz=z.copy()
            if not np.all(dem_ok):
                # Se elimina la máscara de cobertura de los gradientes y, si
                # hubiera nodata en la ventana, se excluyen sus vecindades.
                zz[~dem_ok]=0
            dzdy,dzdx=np.gradient(zz,dy,dx)
            slope=np.degrees(np.arctan(np.hypot(dzdx,dzdy)))
            # No usar gradientes que tocan celdas nodata.
            keep=valid.copy()
            for ax in (0,1):
                keep&=np.roll(dem_ok,1,axis=ax)&np.roll(dem_ok,-1,axis=ax)
            alt_lo,alt_hi=FLOORS[p["estrato"]]
            in_floor=(z>=alt_lo)&(z<alt_hi)
            permissible=keep&in_floor&(slope<=MAX_SLOPE)
            if permissible.sum()<4:
                # NO borrar el núcleo por falta de relieve elegible:
                # reportar el no cumplimiento y geometría vacía.
                final=Polygon()
            else:
                frag=[clean(shape(g)) for g,v in shapes(
                       permissible.astype("uint8"),mask=permissible,transform=trans)
                       if int(v)==1]
                final=clean(unary_union([g for g in frag if not g.is_empty]))
                # Recorte original + simplificación topológica sin ampliar geometrías.
                final=clean(final.intersection(polygon).simplify(0.00015,preserve_topology=True))
                final=clean(final.intersection(polygon))
            values=z[valid]
            good_slopes=slope[keep]
            eligible=int(permissible.sum())
            prop={
                "sector_9k":p["id_sector"],"familia":p["familia_similitud"],
                "piso_nominal_9k":p["estrato"],"altura_min_piso_m":alt_lo,
                "altura_max_piso_m":alt_hi,
                "n_pixeles_cog_en_poligono":int(valid.sum()),
                "n_pixeles_relieve_piso_y_pendiente_compatible":eligible,
                "fraccion_compatible_en_muestra_raster":round(eligible/int(valid.sum()),5),
                "altitud_cog_min_m":round(float(np.min(values)),2),
                "altitud_cog_max_m":round(float(np.max(values)),2),
                "altitud_cog_p50_m":round(float(np.median(values)),2),
                "pendiente_cog_mediana_grados":round(float(np.median(good_slopes)),2) if good_slopes.size else None,
                "pendiente_cog_p90_grados":round(float(np.quantile(good_slopes,.9)),2) if good_slopes.size else None,
                "n_piezas_contiguas_filtradas":(len(final.geoms) if final.geom_type=="MultiPolygon" else
                                               1 if not final.is_empty else 0),
                "modelo_dsm_es_superficie_no_terreno_desnudo":True,
                "limite_9k_referencial":True,
                "continuidad_climatica_validada":False,
                "prediccion_zonal_validada":False}
            feats.append({"type":"Feature","properties":prop,
                          "geometry":mapping(final) if not final.is_empty else None})
    groups=defaultdict(list)
    for f in feats:groups[f["properties"]["familia"]].append(f["properties"])
    families=[{
        "familia":key,
        "n_sectores_9k":len(items),
        "pixeles_total":sum(q["n_pixeles_cog_en_poligono"] for q in items),
        "pixeles_compatibles":sum(q["n_pixeles_relieve_piso_y_pendiente_compatible"] for q in items),
        "fraccion_compatible":round(sum(q["n_pixeles_relieve_piso_y_pendiente_compatible"] for q in items)/
                             sum(q["n_pixeles_cog_en_poligono"] for q in items),5),
        "recomendacion":"verificar_cuenca_exposicion_y_estaciones"} for key,items in sorted(groups.items())]
    forecast=json.loads(F_FORECAST.read_text("utf8"))
    if forecast["fuentes_netcdf_comprobadas"]!=2 or forecast["downscaling_zonal_aplicado"]:
        raise ValueError("NMME 9K insuficiente")
    unique_noaa=sorted({(s["celda_latitud"],s["celda_longitud_archivo"])
        for x in forecast["fuentes"] for s in x["sitios_celda"]})
    state={
      "fase":"9L","fecha_corte":"2026-10-17","estado":"relieve_continuo_local_tres_familias_exploratorio",
      "fuente":"Copernicus GLO-90 DSM 2021, Cloud Optimized GeoTIFF (AWS Open Data)",
      "doi":"10.5270/ESA-c5d3d65","origen_url":URL,
      "sha256_tiff_original":sha(raw),"bytes_tiff_original":len(raw),
      "resolucion_modelo_m_aprox":90,
      "resolucion_analisis_m_aprox":270,
      "muestra_restringida_a_nucleos_9k":True,
      "n_sectores_9k_auditados":len(feats),"n_familias":len(families),
      "familias":families,
      "comparacion_nmme":{"n_celdas_noaa_para_4_localidades":len(unique_noaa),
         "celdas":[{"lat":v[0],"lon_east":v[1]} for v in unique_noaa],
         "periodo_base_local":"1996-2025 ERA5/ERA5-Land",
         "anomalias_noaa_normal_modelo_diferente":True,
         "ajuste_altitudinal_entrenado":False,"prediccion_por_sector_generada":False,
         "habilidad_prospectiva_demostrada":False},
      "zonas_homogeneas_instrumentales_certificadas":0,
      "cuencas_hidrograficas_confirmadas":0,
      "limite_region_ine_i_ign_validado":False,
      "umbrales_de_filtro_experimentales":{"max_pendiente_grados":MAX_SLOPE,
         "altitud_exige_banda_de_9k":True,"agregacion_dem_3x":True},
      "sha256_geojson_9k":hashlib.sha256(F_BASE.read_bytes()).hexdigest(),
      "observaciones":["Es un DSM de superficie: vegetación y construcciones pueden afectar pendientes.",
         "Cada píxel filtrado corresponde a la banda altitudinal nominal y pendiente, no a continuidad climática observada.",
         "El límite y las categorías 9K son referenciales; la máscara es una hipótesis para focalizar campo.",
         "Sin cuencas oficiales independientes verificadas, no se afirma que las piezas compartan drenaje.",
         "NMME 1° no permite un pronóstico diferente por cada ladera sin método de transferencia validado."]}
    geo={"type":"FeatureCollection","name":"OAF 9L filtro de relieve en núcleos 9K",
         "metadata":{"fase":"9L","uso":"planificacion_muestreo","homogeneidad_validada":False,
         "sistema":"EPSG:4326","n_familias":3,"zonas_9k_referenciales":True},
         "features":feats}
    return geo,state

def save():
    raw=download();geo,status=measure(raw)
    DEST.mkdir(parents=True,exist_ok=True)
    F_GEO.write_text(json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n","utf8")
    F_STATE.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n","utf8")
    return status

def check():
    raw=download();geo,status=measure(raw)
    if json.loads(F_GEO.read_text("utf8"))!=json.loads(json.dumps(geo)):
        raise ValueError("La máscara de relieve 9L no se reproduce")
    if json.loads(F_STATE.read_text("utf8"))!=status:
        raise ValueError("El informe 9L no se reproduce")
    return status

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
    r=check() if a.check else save()
    print("9L:",r["n_sectores_9k_auditados"],"núcleos,",
          r["n_familias"],"familias, SHA DEM",r["sha256_tiff_original"][:16])
