"""Fase 3W: comprobar acceso al CSV GBON/RBON, SOLO metadatos y cabecera."""
import json
import time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
URLS=[
 "https://www.datosabiertos.gob.pe/sites/default/files/Variables%20Meteorologicas%20de%20las%20Estaciones%20autom%C3%A1ticas%20de%20intercambio%20internacional%20-%20%5BServicio%20Nacional%20de%20Meteorolog%C3%ADa%20e%20Hidrolog%C3%ADa%20del%20Per%C3%BA%20-%20SENAMHI%5D.csv",
 "https://www.datosabiertos.gob.pe/sites/default/files/Variables%20Meteorologicas%20de%20las%20Estaciones%20autom%C3%A1ticas%20de%20intercambio%20internacional%20-%20%5BServicio%20Nacional%20de%20Meteorolog%C3%ADa%20e%20Hidrolog%C3%ADa%20del%20Per%C3%BA%20-%20SENAMHI%5D_0.csv",
 "https://repositorio.senamhi.gob.pe/bitstream/20.500.12542/3635/3/Variables-meteorologicas-estaciones-autom%C3%A1ticas-intercambio-internacional_2024.csv"
]
status={"fase":"3W","archivo_descargado":False,"esquema_verificado":False,
        "resultados":[],"nuevos_meses_certificados":0,
        "observaciones_2016_2025_incorporadas":0}
for url in URLS:
    item={"url":url}
    try:
        with requests.get(url,timeout=(20,45),stream=True,headers={"User-Agent":"Mozilla/5.0 (OAF-Lambayeque academic provenance audit)"}) as r:
            item["http_status"]=r.status_code
            item["tipo"]=r.headers.get("Content-Type")
            item["longitud"]=r.headers.get("Content-Length")
            item["url_final"]=r.url
            if r.status_code==200:
                sample=next(r.iter_content(2400),b"")
                if b"<html" in sample.lower() or b"<!doctype" in sample.lower():
                    item["problema"]="Respuesta HTML, no CSV"
                else:
                    firstline=sample.splitlines()[0].decode("utf-8-sig",errors="replace")
                    item["cabecera_csv"]=firstline[:1500]
                    item["delimitador_sugerido"]=";" if firstline.count(";")>firstline.count(",") else ","
                    if firstline.count(";")+firstline.count(",")>=3:
                        status["archivo_descargado"]=True
                        status["url_csv_accesible"]=url
                        status["esquema_verificado"]=True
            else:item["problema"]="El archivo no es accesible mediante este servidor"
    except Exception as e:
        item["problema"]=f"{type(e).__name__}: {str(e)[:200]}"
    status["resultados"].append(item)
    print(json.dumps(item,ensure_ascii=False),flush=True)
    if status["archivo_descargado"]:break
DATA.mkdir(exist_ok=True)
(DATA/"estado_3w_acceso.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("RESUMEN",json.dumps({k:status[k] for k in ("archivo_descargado","esquema_verificado")}),flush=True)
