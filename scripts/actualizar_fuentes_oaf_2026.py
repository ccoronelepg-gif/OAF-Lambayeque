"""Actualización documental prudente de fuentes climáticas OAF.

NO interpreta avisos de SENAMHI como pronósticos ni promueve RF candidatos.
Solo comprueba accesibilidad, identifica número de comunicado ENFEN y publica
metadatos con marcas temporales; no equivale a monitoreo en tiempo real.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datos" / "estado_fuentes_oficiales_auto.json"
ENFEN = "https://enfen.imarpe.gob.pe/comunicados/"
SOURCES = {
    "enfen": ("ENFEN", ENFEN, "Comunicados institucionales"),
    "noaa": ("NOAA CPC", "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc_Sp.shtml", "Discusión oficial ENOS"),
    "senamhi": ("SENAMHI", "https://www.senamhi.gob.pe/main.php?dp=lambayeque&p=aviso-meteorologico-vigente", "Portal de avisos regionales; vigencia de cada aviso no inferida"),
    "cenepred": ("CENEPRED", "https://sigrid.cenepred.gob.pe/sigridv3/", "Escenarios de riesgo; su edición se consulta en el documento"),
}
HEADERS = {"User-Agent": "OAF-Lambayeque/2.0 (+https://ccoronelepg-gif.github.io/OAF-Lambayeque/; auditoria fuentes cientificas)"}
ISSUE = re.compile(r"Comunicado\s+Oficial\s+Enfen\s+N\s*[°ºo.]?\s*(\d{1,2})\s*[-–]\s*(20\d{2})", re.I)

def latest_enfen(html):
    """Solo lee números presentes en enlaces del dominio institucional."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        match = ISSUE.search(text)
        if not match:
            parent = a.find_parent(["article", "li", "div"])
            nearby = parent.get_text(" ", strip=True)[:320] if parent else ""
            match = ISSUE.search(nearby)
        if not match:
            continue
        url = urljoin(ENFEN, a.get("href",""))
        if urlparse(url).hostname not in ("enfen.imarpe.gob.pe","www.enfen.imarpe.gob.pe"):
            continue
        num,year = map(int,match.groups())
        if num>30 or year>datetime.now(timezone.utc).year+1:
            continue
        items.append({"numero":num,"anio":year,"titulo":f"Comunicado Oficial ENFEN N.º {num:02d}-{year}","url":url})
    if not items:
        # No interpretar como verificado si la página cambió su HTML o no hay enlace.
        raise ValueError("No se pudo identificar un enlace a un comunicado oficial de ENFEN")
    return sorted(items,key=lambda x:(x["anio"],x["numero"]),reverse=True)[0]

def load_previous():
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}

def run():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    previous=load_previous()
    output={
        "esquema":"OAF-fuentes-operativas-2026-v1",
        "fecha_comprobacion_utc":now,
        "metodo":"Solicitudes HTTPS a páginas oficiales; respuesta HTTP no implica actualización editorial ni disponibilidad de avisos para cada distrito.",
        "fuentes":{},
        "catalogo_modelos":[
            {"id":"open_meteo","nombre":"Pronóstico diario Open-Meteo","frecuencia":"Consulta de API cuando se abre la pestaña","tipo":"pronostico_externo","estado":"dinamico_del_proveedor","operativo_oaf":False},
            {"id":"chirps_3z","nombre":"CHIRPS v3 mensual","frecuencia":"Trabajo semanal programado (ver estado 3Z)","tipo":"estimacion_satelital","estado":"depende_de_job_y_publicacion","operativo_oaf":False},
            {"id":"ncei_6d","nombre":"NOAA NCEI ERSSTv5 Niño 1+2","frecuencia":"Días 12 y 19 cada mes","tipo":"serie_historica_actualizable","estado":"depende_de_job_y_publicacion","operativo_oaf":False},
            {"id":"rf_10j","nombre":"Random Forest 10J","frecuencia":"Día 26; requiere nuevos meses CHIRPS validados","tipo":"modelo_candidato","estado":"no_publicacion_automatica","operativo_oaf":False},
            {"id":"rf_10n","nombre":"Random Forest corrector estaciones 10N","frecuencia":"Sin reentrenamiento automático operativo","tipo":"modelo_experimental","estado":"historico_sin_habilidad_aceptada","operativo_oaf":False},
            {"id":"otros_experimentos","nombre":"Otros visores y comparaciones RF, GCN, CNN","frecuencia":"Reproducibles bajo cambios y auditoría, NO pronósticos nuevos por defecto","tipo":"evaluacion_historica","estado":"sin_actualizacion_operativa_automatica","operativo_oaf":False}
        ]
    }
    session=requests.Session()
    for id,(name,url,description) in SOURCES.items():
        rec={"organismo":name,"url":url,"tipo":description,"estado_consulta":"no_verificado","ultima_consulta_utc":now,
             "fecha_ultimo_documento":None,"ultimo_documento":None,"error":None,"respuesta_http":None,
             "no_equivale_a_pronostico_local":True}
        try:
            res=session.get(url,headers=HEADERS,timeout=(10,25))
            rec["respuesta_http"]=res.status_code
            res.raise_for_status()
            final=urlparse(res.url)
            if final.scheme!="https" or not final.hostname or not final.hostname.endswith(urlparse(url).hostname.split(".",1)[-1]):
                raise ValueError("Redirección a dominio no autorizado")
            if id=="enfen":
                latest=latest_enfen(res.text)
                rec["ultimo_documento"]=latest
                prev_doc=previous.get("fuentes",{}).get(id,{}).get("ultimo_documento") or {}
                rec["estado_consulta"]="nuevo_documento_por_interpretar" if (
                    (latest["anio"],latest["numero"])>(prev_doc.get("anio",0),prev_doc.get("numero",0))
                    and prev_doc.get("numero") is not None
                ) else "indice_oficial_verificado"
                rec["url"]=latest["url"]
            else:
                # Se verificó disponibilidad del sitio, NO emisión ni fecha de un aviso.
                rec["estado_consulta"]="sitio_accesible_fecha_aviso_no_verificada"
        except (requests.RequestException,ValueError,TypeError) as ex:
            rec["error"]=f"{type(ex).__name__}: {str(ex)[:160]}"
            rec["estado_consulta"]="consulta_fallida"
            if id=="enfen":
                older=previous.get("fuentes",{}).get("enfen",{}).get("ultimo_documento")
                if older:rec["ultimo_documento"]=older
        output["fuentes"][id]=rec
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v["estado_consulta"] for k,v in output["fuentes"].items()},ensure_ascii=False))
    return output

if __name__=="__main__":
    run()
