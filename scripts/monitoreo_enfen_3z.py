"""OAF 2.0 / Fase 3Z: consultar último comunicado institucional ENFEN.

Extrae título, fecha y enlace oficial del archivo de comunicados, y confirma
la declaración de estado únicamente si aparece en la noticia ORIGINAL.
No calcula ICEN, no pronostica El Niño y nunca publica una alerta del OAF.
Si la fuente falla, conserva un estado 'no_verificado', nunca inventa novedades.
"""
from __future__ import annotations
import datetime as dt
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin,urlparse

import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
INDEX="https://enfen.imarpe.gob.pe/comunicados/"
CURRENT="https://enfen.imarpe.gob.pe/comunicados/"
HEADERS={"User-Agent":"OAF-Lambayeque/2.0 academic ENSO institutional provenance"}
MONTHS={
 "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
 "jul":7,"ago":8,"set":9,"sep":9,"oct":10,"nov":11,"dic":12
}
KINDS=[
 ("alerta_de_el_nino_costero","Alerta de El Niño Costero"),
 ("vigilancia_de_el_nino_costero","Vigilancia de El Niño Costero"),
 ("alerta_de_la_nina_costera","Alerta de La Niña Costera"),
 ("vigilancia_de_la_nina_costera","Vigilancia de La Niña Costera"),
 ("no_activo","No Activo"),
]

def normal(s):
    return "".join(x for x in unicodedata.normalize("NFKD",str(s)).lower()
        if x.isascii() and x.isalnum())

def fetch(url):
    r=requests.get(url,timeout=(20,55),headers=HEADERS)
    r.raise_for_status()
    if len(r.content)<2000:
        raise ValueError("La página es demasiado pequeña")
    final=urlparse(r.url)
    if final.hostname not in ("enfen.imarpe.gob.pe","www.enfen.imarpe.gob.pe"):
        raise ValueError("La respuesta redirigió a un dominio no oficial")
    return r.text

def latest_index():
    """Index actual ENFEN; usar solamente enlaces reconocidos en el portal oficial."""
    from actualizar_fuentes_oaf_2026 import latest_enfen
    entry=latest_enfen(fetch(INDEX))
    entry["fecha_emision"]=None
    return entry

def classify_status(text):
    # El rótulo institucional es el único punto de extracción de estado;
    # mencionar un evento en el resto del comunicado NO lo convierte en alerta.
    flat=re.sub(r"\s+"," ",text.replace("\xa0"," "))
    matched=re.search(r"Estado\s+(?:del\s+)?sistema\s+de\s+alerta\s*[:：]\s*(.{0,90})",flat,re.I)
    if not matched:
        return "estado_no_verificado",None
    segment=normal(matched.group(1)[:65])
    for key,name in KINDS:
        if normal(name) in segment:
            return "identificado_en_comunicado",name
    return "estado_no_verificado",None

def main():
    at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    status={
        "fase":"3Z","fuente":"ENFEN - Comisión Multisectorial Perú",
        "tipo_dato":"ESTADO_OFICIAL_ENSO","fuente_archivo":INDEX,
        "pagina_comunicados":CURRENT,"fecha_consulta_utc":at,
        "numero":None,"anio":None,"fecha_emision":None,
        "titulo":None,"url_comunicado":None,"estado_institucional":None,
        "verificacion":"no_verificado","edad_comunicado_dias":None,
        "fuente_publica":True,"prediccion_oaf":False,
        "alerta_emitida_por_oaf":False,"errores":[],
        "nota":"El estado oficial es responsabilidad de ENFEN, nunca una alerta propia del OAF. Se requiere leer fecha y fuente original."
    }
    try:
        entry=latest_index()
        status.update({k:entry[k] for k in ("numero","anio","titulo","fecha_emision")})
        status["url_comunicado"]=entry["url"]
        txt=BeautifulSoup(fetch(entry["url"]),"html.parser").get_text(" ",strip=True)
        verification,statement=classify_status(txt)
        status["verificacion"]=verification
        status["estado_institucional"]=statement
        if entry["fecha_emision"]:
            issue=dt.date.fromisoformat(entry["fecha_emision"])
            if issue>dt.datetime.now(dt.timezone.utc).date():
                raise ValueError("La fecha del comunicado está en el futuro")
            status["edad_comunicado_dias"]=(dt.datetime.now(dt.timezone.utc).date()-issue).days
        if not statement:
            status["errores"].append("El texto consultado no permitió confirmar el rótulo oficial del estado de alerta")
    except (requests.RequestException,ValueError,TypeError,KeyError) as exc:
        status["verificacion"]="consulta_fallida"
        status["estado_institucional"]=None
        status["errores"].append(f"{type(exc).__name__}: {str(exc)[:300]}")
    DATA.mkdir(exist_ok=True)
    (DATA/"estado_enfen_3z.json").write_text(
       json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=[
        "# OAF-Lambayeque | Fase 3Z: último comunicado oficial ENFEN","",
        "**Esta fuente informa del ESTADO INSTITUCIONAL de El Niño Costero. No es un pronóstico propio, ni una alerta del observatorio.**","",
        "- Fecha de consulta UTC: "+at,
        "- Número: "+str(status["numero"]),
        "- Fecha de emisión: "+str(status["fecha_emision"]),
        "- Estado institucional confirmado textualmente: "+str(status["estado_institucional"] or "no_verificado"),
        "- Control de calidad: "+status["verificacion"],
        "- Documento oficial: "+str(status["url_comunicado"] or INDEX),
        "- Última edad comprobada (días): "+str(status["edad_comunicado_dias"]),
        "- Archivo de comunicados: "+INDEX,"",
        "## Interpretación","",
        "La publicación tiene fecha; el OAF no puede afirmar que el estado siga vigente si la institución actualizó después su comunicado.",
        "Los pronósticos de lluvia locales requieren fuentes meteorológicas propias y evaluación; un comunicado ENFEN no cuantifica lluvia futura en los cinco píxeles.",
        "No se calculó un índice Niño 1+2 ni se inventaron probabilidades.",
        "La fuente debe volver a consultarse en caso de incidencias, actualización pendiente o estado no verificado.","",
        "## Errores de consulta",""]
    if status["errores"]:
        report.extend("- "+x for x in status["errores"])
    else:report.append("No se registraron errores de consulta.")
    report+=["","Archivo de estado: datos/estado_enfen_3z.json.",
             "Código: scripts/monitoreo_enfen_3z.py.",""]
    (ROOT/"MONITOREO_ENFEN_3Z.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(status,ensure_ascii=False,indent=2),flush=True)
    if status["verificacion"]!="identificado_en_comunicado":
        raise SystemExit("No se pudo verificar el estado institucional ENFEN; publicar con estado no verificado")

if __name__=="__main__":
    main()
