"""QA publicable de Fase 3Z. Se ejecuta sobre artefactos reales archivados.

No consulta APIs ni inventa lluvia. Un mes sin GeoTIFF debe permanecer
ausente del CSV. Distingue ENFEN verificado frente a fallo institucional.
"""
import csv
import datetime as dt
import json
import math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
STATIONS={"Jayanca (La Viña)","Cayaltí","Reque","Lambayeque","Cueva Blanca"}

def verify():
    chirps=json.loads((DATA/"estado_monitoreo_3z.json").read_text(encoding="utf-8"))
    audit=json.loads((DATA/"auditoria_rasters_chirps_3z.json").read_text(encoding="utf-8"))
    enfen=json.loads((DATA/"estado_enfen_3z.json").read_text(encoding="utf-8"))
    with (DATA/"chirps_v3_reciente_3z.csv").open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(audit)!=12:
        raise ValueError("Se requieren 12 meses cerrados auditados; calendario mensual, no días")
    month_status={x["mes"]:x["estado"] for x in audit}
    if len(month_status)!=12:
        raise ValueError("Meses duplicados en auditoría")
    successes={month for month,st in month_status.items() if st=="descargado_y_extraido"}
    failures={month for month,st in month_status.items() if st=="no_disponible"}
    if successes|failures!=set(month_status):
        raise ValueError("Estado no reconocido de raster mensual")
    if chirps["meses_con_raster_verificado"]!=len(successes):
        raise ValueError("Número de meses verificados inconsistente")
    if chirps["meses_no_disponibles"]!=len(failures):
        raise ValueError("Meses no disponibles inconsistente")
    if len(rows)!=len(successes)*5:
        raise ValueError("No se verificaron los cinco puntos para cada mes")
    bymonth=Counter()
    seen=set()
    for row in rows:
        month=row["mes"]
        name=row["estacion_referencial"]
        if month not in successes:
            raise ValueError("Se publicó un valor de un mes sin raster verificado")
        if name not in STATIONS or (month,name) in seen:
            raise ValueError("Estación no reconocida o duplicada")
        seen.add((month,name))
        bymonth[month]+=1
        value=float(row["lluvia_estimada_mm"])
        if not math.isfinite(value) or value<0 or value>10000:
            raise ValueError("Precipitación estimada inválida")
        if row["tipo_dato"]!="ESTIMADO_SATELITAL_GAUGE_BLEND":
            raise ValueError("Se está confundiendo lluvia estimada con observada")
        if row["resolucion_grados"]!="0.05":
            raise ValueError("Resolución CHIRPS alterada")
        if not row["url_raster"].startswith("https://data.chc.ucsb.edu/products/CHIRPS/v3.0/"):
            raise ValueError("Url de raster no oficial")
    if any(n!=5 for n in bymonth.values()):
        raise ValueError("Píxeles incompletos para un mes")
    if chirps.get("ultimo_mes_disponible")!=max(successes,default=None):
        raise ValueError("Fecha de último mes errónea")
    if chirps.get("prediccion_propia") is not False or chirps.get("alerta_oaf") is not False:
        raise ValueError("No se pueden anunciar alertas OAF sin validación")
    if chirps.get("validacion_externa_independiente") is not False:
        raise ValueError("No se demostró independencia de los pluviómetros")
    if chirps.get("anios_observados_senamhi_nuevos_certificados")!=0:
        raise ValueError("La extracción CHIRPS no certifica datos de estación")
    if enfen.get("alerta_emitida_por_oaf") is not False or enfen.get("prediccion_oaf") is not False:
        raise ValueError("El OAF no emite aviso ENSO propio")
    if enfen["verificacion"]!="identificado_en_comunicado" and enfen.get("estado_institucional") is not None:
        raise ValueError("ENFEN declaró un estado sin haberlo confirmado en comunicado")
    if enfen["verificacion"]=="identificado_en_comunicado":
        if not all((enfen.get("fecha_emision"),enfen.get("numero"),enfen.get("url_comunicado"),
                    enfen.get("estado_institucional"))):
            raise ValueError("Falta fecha o fuente en ENFEN verificado")
    html=(ROOT/"index.html").read_text(encoding="utf-8")
    for x in ('id="monitoreo3z"','datos/chirps_v3_reciente_3z.csv',
              'datos/estado_enfen_3z.json',"VERSIÓN PÚBLICA · 2.1",
              "CARLOS ENRIQUE CORONEL GARCÍA","tel:+51929304528"):
        if x not in html:
            raise ValueError("Panel OAF/autor no encontrado: "+x)
    print(json.dumps({
        "resultado":"correcto",
        "meses_con_raster":len(successes),
        "meses_sin_raster":len(failures),
        "valores_grillados":len(rows),
        "ultimo_mes_verificado":max(successes,default=None),
        "enfen_verificacion":enfen["verificacion"],
        "alertas_oaf_activas":False,
    },ensure_ascii=False))
if __name__=="__main__":
    verify()
