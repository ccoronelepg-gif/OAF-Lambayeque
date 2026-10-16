#!/usr/bin/env python3
"""OAF 8K: recuperar SOLO los metadatos espaciales informados por Open-Meteo.

No pretende demostrar identidad con la celda originalmente utilizada en 8D:
es una consulta NUEVA al proveedor con el mismo modelo y selección por defecto.
Utiliza un día antiguo (2020-07-01) y registra URL, hora UTC y SHA-256 del JSON.
La propiedad 'elevation' es el dato de elevación *reportado por la API*,
no la orografía ERA5-Land verificada.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import io
import json
import math
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE/"modelos/benchmark_impacto_regional_8d.py"
DEST="datos/metadatos_celdas_openmeteo_8k.csv"
FIELDS=(
  "localidad_oaf","latitud_solicitada","longitud_solicitada",
  "latitud_respuesta","longitud_respuesta","elevacion_respuesta_m",
  "tipo_elevacion","modelo_solicitado","seleccion_celda","fecha_muestra",
  "fecha_consulta_utc","url_consulta","fuente_documentacion","sha256_respuesta",
  "metadatos_celda_8d_originales_verificados"
)
API="https://archive-api.open-meteo.com/v1/archive"

def sites(root):
    t=ast.parse((root/"modelos/benchmark_impacto_regional_8d.py").read_text(encoding="utf-8"))
    values=[ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign)
            and any(isinstance(x,ast.Name) and x.id=="SITES" for x in n.targets)]
    if len(values)!=1 or list(values[0])!=["Chiclayo","Jayanca","Motupe","Olmos"]:
        raise ValueError("No se reconoce el conjunto original de sitios 8D")
    return values[0]

def request_meta(name,lat,lon):
    params={"latitude":str(lat),"longitude":str(lon),"start_date":"2020-07-01",
            "end_date":"2020-07-01","timezone":"America/Lima",
            "daily":"temperature_2m_mean","models":"era5_land","cell_selection":"land"}
    url=API+"?"+urlencode(params)
    last=None
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-8K-metadata-research/1.0"}),
                         timeout=30) as response:
                data=response.read()
            if len(data)>250000:raise ValueError("Respuesta excesiva para un día")
            payload=json.loads(data)
            if not isinstance(payload,dict) or payload.get("error"):
                raise ValueError("Proveedor rechazó consulta: "+str(payload.get("reason")))
            if payload.get("timezone")!="America/Lima":
                raise ValueError("Zona horaria del proveedor incompatible")
            vals=payload.get("daily",{})
            if vals.get("time")!=["2020-07-01"] or not isinstance(vals.get("temperature_2m_mean"),list) or len(vals["temperature_2m_mean"])!=1:
                raise ValueError("Respuesta sin serie diaria completa de comprobación")
            t=vals["temperature_2m_mean"][0]
            if t is None or not isinstance(t,(float,int)) or not -40<t<55:
                raise ValueError("Temperatura de serie 2020 no disponible o fuera de rango")
            plat,plon,elevation=(payload.get(x) for x in ("latitude","longitude","elevation"))
            if any(not isinstance(z,(int,float)) or not math.isfinite(z) for z in (plat,plon,elevation)):
                raise ValueError("Proveedor no devolvió ubicación y elevación numéricas")
            if abs(plat)>90 or abs(plon)>180 or not -500<elevation<7000:
                raise ValueError("Metadatos geográficos inverosímiles")
            # CSV enlaza la huella del JSON íntegro, no un valor redactado.
            return {
             "localidad_oaf":name,"latitud_solicitada":str(lat),"longitud_solicitada":str(lon),
             "latitud_respuesta":str(plat),"longitud_respuesta":str(plon),
             "elevacion_respuesta_m":str(elevation),
             "tipo_elevacion":"altura_reportada_api_no_orografia_era5_verificada",
             "modelo_solicitado":"era5_land","seleccion_celda":"land",
             "fecha_muestra":"2020-07-01",
             "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "url_consulta":url,
             "fuente_documentacion":"https://open-meteo.com/en/docs/historical-weather-api",
             "sha256_respuesta":hashlib.sha256(data).hexdigest(),
             "metadatos_celda_8d_originales_verificados":"false"
            }
        except (URLError,HTTPError,TimeoutError,ValueError,KeyError,json.JSONDecodeError) as exc:
            last=exc
            if attempt<2:time.sleep(2*(attempt+1))
    raise RuntimeError("Consulta metadata Open-Meteo fallida "+name+": "+str(last))

def collect(root,refresh=False):
    path=root/DEST
    if not path.exists():raise FileNotFoundError("Falta esquema de metadatos 8K")
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=list(FIELDS):raise ValueError("Manifiesto de celdas alterado")
        existing=list(reader)
    if existing and not refresh:
        if len(existing)!=4:raise ValueError("Catálogo parcial: no reemplazarlo silenciosamente; usar --refresh auditado")
        print("Metadatos existentes conservados (no se modifica fecha/huella).")
        return
    rows=[]
    for city,(lat,lon) in sites(root).items():
        rows.append(request_meta(city,lat,lon))
        print("Consulta geográfica de proveedor completada para "+city,flush=True)
    # Escritura atómica sólo después de las cuatro respuestas válidas.
    text=io.StringIO(newline="")
    writer=csv.DictWriter(text,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(mode="w",encoding="utf-8",delete=False,dir=path.parent) as temp:
        temp.write(text.getvalue());temp_path=Path(temp.name)
    temp_path.replace(path)
    print("Cuatro respuestas del proveedor guardadas con trazabilidad. NO son celdas 8D originales.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=BASE)
    p.add_argument("--refresh",action="store_true",help="Regenerar huellas y fecha ante solicitud explícita")
    args=p.parse_args()
    collect(args.root,args.refresh)
