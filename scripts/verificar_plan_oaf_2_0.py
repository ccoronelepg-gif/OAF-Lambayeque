"""Comprobaciones de consistencia de la nueva hoja de ruta OAF-Lambayeque 2.0.

No descarga datos, no genera pronósticos y nunca activa alertas.
Protege el estado científico del proyecto y la distinción entre datos
observados, estimados y pronosticados.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT/"datos/plan_operativo_oaf_2_0.json"
CATALOG = ROOT/"datos/catalogo_fuentes_operativas_3z.csv"
PAGE = ROOT/"index.html"
README = ROOT/"README.md"
PROTOCOL = ROOT/"PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md"
MASTER = ROOT/"PLAN_MAESTRO_OAF_2_0.md"
COVERAGE = ROOT/"datos/estado_cobertura_oficial.json"
PHASES = ("3Z","4A","4B","4C")
MODULES = {f"M{i}" for i in range(6)}
REQUIRED_TYPES = {"ESTADO_OFICIAL_ENSO", "OBSERVADO_INSTRUMENTAL",
                  "ESTIMADO_SATELITAL", "PRONOSTICO_METEOROLOGICO",
                  "AVISO_OFICIAL"}

def run():
    plan = json.loads(ROUTE.read_text(encoding="utf-8"))
    if tuple(x["id"] for x in plan["entregables"]) != PHASES:
        raise ValueError("Fases reordenadas o incompletas")
    if set(x["id"] for x in plan["modulos"]) != MODULES:
        raise ValueError("Se requieren M0 a M5")
    if any(x["estado"] not in ("siguiente","pendiente","en_progreso") for x in plan["entregables"]):
        raise ValueError("El plan no puede proclamar fases implementadas sin informe de validación")
    rules = plan["reglas"]
    for key in ("imputacion_observaciones_prohibida", "no_confundir_estimacion_con_observacion",
                "no_confundir_reanalisis_con_pronostico",
                "observacion_actual_sin_exigir_anio_terminado"):
        if rules[key] is not True:
            raise ValueError("Se alteró la regla obligatoria: "+key)
    for key in ("alertas_propias_operativas_habilitadas","indice_fitosanitario_validado"):
        if rules[key] is not False:
            raise ValueError("Estado de alerta/riesgo validado sin soporte documental")
    with CATALOG.open(encoding="utf-8-sig",newline="") as stream:
        rows=list(csv.DictReader(stream))
    if len(rows)<5:
        raise ValueError("Faltan fuentes operativas candidatas")
    if len({x["codigo"] for x in rows})!=len(rows):
        raise ValueError("Fuentes duplicadas")
    if not REQUIRED_TYPES.issubset({x["tipo_de_dato"] for x in rows}):
        raise ValueError("No se distingue observación, estimación, pronóstico y comunicados")
    if any(not x["documentacion_oficial"].startswith("https://") for x in rows):
        raise ValueError("No todos los enlaces de fuentes son seguros")
    if any(not x["estado_en_pipeline_3z"] or not x["limitacion"] for x in rows):
        raise ValueError("Estado y limitación deben estar presentes en cada fuente")
    page=PAGE.read_text(encoding="utf-8")
    readme=README.read_text(encoding="utf-8")
    master=MASTER.read_text(encoding="utf-8")
    protocol=PROTOCOL.read_text(encoding="utf-8")
    for key in ('id="plan20"','VERSIÓN PÚBLICA · 2.1',"CARLOS ENRIQUE CORONEL GARCÍA","tel:+51929304528",
                "PLAN_MAESTRO_OAF_2_0.md","PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md"):
        if key not in page:
            raise ValueError("Falta bloque esencial en portal: "+key)
    for key in ("3Z","4A","4B","4C","2026","No se imputan"):
        if key not in readme:
            raise ValueError("El README no documenta: "+key)
    if "sin alertas propias" not in master.lower() and "no existen todavía alertas" not in protocol.lower():
        raise ValueError("Los documentos no advierten de ausencia de alertas")
    observed=json.loads(COVERAGE.read_text(encoding="utf-8"))
    expected=int(plan["fases_historicas"]["ultimo_anio_instrumental_compartido_completo"])
    actual=int(observed["ultimo_anio_temporalmente_completo_compartido_cinco_estaciones"])
    if actual!=expected:
        raise ValueError("Actualizar el snapshot 2.0 desde control oficial de cobertura")
    if observed.get("imputacion_de_faltantes_permitida") is not False:
        raise ValueError("No se permiten rellenos de estaciones")
    print(json.dumps({
        "status":"ok","version":"2.0","fases":list(PHASES),
        "modulos":len(MODULES),"fuentes_catalogadas":len(rows),
        "ultimo_anio_instrumental_comun":actual,"alertas_operativas":False
    },ensure_ascii=False))

if __name__=="__main__":
    run()
