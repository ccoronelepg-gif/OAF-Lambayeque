#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9L: consulta institucional exploratoria de unidades hidrográficas ANA.
Servicio de cartografía publicado por Ministerio de Vivienda como mapa EXTERNAS/ANA.
Una capa referencial no reemplaza certificación ANA ni cuenca observada en campo.
Si el servicio no responde, preserva estado 0 y nunca inventa unidades.
"""
import argparse, json, hashlib
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely import make_valid

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/relieve_9l"
GEO=BASE/"nucleos_restringidos_relieve_9l.geojson"
OUT=BASE/"consulta_unidades_hidrograficas_9l.json"
OVERLAY=BASE/"intersecciones_cuencas_9l.geojson"
PROVIDER=("https://dportalgis.vivienda.gob.pe/dfdserver/rest/services/"
          "EXTERNAS/Hidrografia/MapServer/6/query")
BB=(-79.67,-6.62,-79.24,-6.05)
PARAMS={"where":"1=1","geometry":",".join(str(x) for x in BB),
        "geometryType":"esriGeometryEnvelope","inSR":"4326",
        "spatialRel":"esriSpatialRelIntersects","outFields":"*",
        "outSR":"4326","returnGeometry":"true","f":"geojson",
        "resultRecordCount":"1000"}
URL=PROVIDER+"?"+urlencode(PARAMS)

def run():
    a=json.loads(GEO.read_text("utf8"))
    zones=[f for f in a["features"] if f["geometry"]]
    findings=[];features=[];err=None;count=0;digest=None
    try:
        with urlopen(Request(URL,headers={"User-Agent":"OAF-Lambayeque/9L science research"}),timeout=45) as response:
            raw=response.read(8_000_001)
        if len(raw)>8_000_000 or len(raw)<100:
            raise ValueError("Respuesta institucional demasiado grande o vacía")
        digest=hashlib.sha256(raw).hexdigest()
        response=json.loads(raw)
        if response.get("type")!="FeatureCollection" or not isinstance(response.get("features"),list):
            raise ValueError("Proveedor no devolvió GeoJSON FeatureCollection")
        rows=response["features"]
        if len(rows)>999:raise ValueError("Posible paginación sin controlar, no publicar cobertura completa")
        for z in zones:
            region=shape(z["geometry"])
            for b in rows:
                if not b.get("geometry"):continue
                poly=shape(b["geometry"])
                if not poly.is_valid:poly=make_valid(poly)
                cut=region.intersection(poly)
                if cut.is_empty or cut.area<=1e-10:continue
                ident=str(b.get("properties",{}).get("OBJECTID") or
                          b.get("properties",{}).get("FID") or
                          b.get("id") or "sin_codigo")
                findings.append({"sector_9k":z["properties"]["sector_9k"],
                    "familia":z["properties"]["familia"],"identificador_mapa":ident})
                features.append({"type":"Feature","geometry":mapping(cut),
                    "properties":{"sector_9k":z["properties"]["sector_9k"],
                    "familia":z["properties"]["familia"],"referencia_unidad_mapa":ident,
                    "cuenca_certificada":False,"prediccion_hidrologica_validada":False}})
        count=len(rows)
        if not rows:err="Consulta institucional devolvió 0 elementos"
    except Exception as ex:
        err=f"{type(ex).__name__}: {ex}"[:380]
        findings=[];features=[]
    state={"fase":"9L","fecha_corte":"2026-10-17",
      "fuente":"Servicio institucional ANÁLISIS EXTERNAS/Hidrografia MapServer/6 - Unidades Hidrográficas ANA (vía Vivienda)",
      "url_consulta":URL,"sha256_respuesta":digest,
      "n_unidades_proveedor_devueltas":count,
      "n_intersecciones_sector_unidad_referencial":len(features),
      "n_unidades_institucionales_certificadas_para_zonificacion":0,
      "separacion_por_cuenca_operativa_validada":False,
      "mensaje_error":err,
      "observaciones":[
        "Una capa publicada mediante servicio externo no acredita por sí sola actualidad, escala o certificación ANA.",
        "Cruzar polígonos de influencia 9K con unidades de cuenca no convierte los polígonos en regiones climáticas homogéneas.",
        "Si la consulta es parcial o no está disponible, no se infiere que las zonas pertenezcan a una sola cuenca."
      ]}
    BASE.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n","utf8")
    OVERLAY.write_text(json.dumps({"type":"FeatureCollection",
        "metadata":{"fase":"9L","cuencas_certificadas":False,"fuente_consulta":URL},
        "features":features},ensure_ascii=False,separators=(",",":"))+"\n","utf8")
    print("9L cuencas:",count,"geometrías de proveedor,",len(features),
          "cruces; incidencias:",err or "sin incidencias")
    return state

if __name__=="__main__":
    p=argparse.ArgumentParser();p.parse_args()
    run()
