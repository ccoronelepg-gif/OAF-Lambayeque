"""OAF-Lambayeque 2.0, fase 3Z: monitoreo mensual CHIRPS v3 verificable.

Consulta GeoTIFF oficiales CHIRPS v3 LATAM para los últimos 12 meses
CALENDARIO FINALIZADOS; no considera el mes en curso. Extrae píxeles
en 5 puntos del OAF de ubicación instrumental histórica provisional.

CHIRPS es un PRODUCTO GRILLADO ESTIMADO (satélite, climatología y
pluviómetros); NO representa medición instrumental de estaciones SENAMHI,
NO pronostica días futuros y NO es alerta meteorológica.

Cada fichero perdido queda marcado NO DISPONIBLE, nunca se imputa 0.
Las unidades y CRS se comprueban. Sin CAPTCHA ni claves privadas.
"""
from __future__ import annotations
import calendar
import csv
import datetime as dt
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import requests
from rasterio.io import MemoryFile
from rasterio.warp import transform as reproject

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
BASE="https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
VERSION="CHIRPS v3.0"
POINTS=[
 ("Jayanca (La Viña)",-6.322,-79.779),
 ("Cayaltí",-6.88079444,-79.54701389),
 ("Reque",-6.88613,-79.8355),
 ("Lambayeque",-6.73152778,-79.90983611),
 ("Cueva Blanca",-6.1313,-79.4045)
]
MONTHS=12
MAX_RASTER_BYTES=40_000_000
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"OAF-Lambayeque/2.0 public scientific climate monitor"})

def previous_month(year,month):
    if month==1:return year-1,12
    return year,month-1

def target_months(now):
    y,m=previous_month(now.year,now.month)
    result=[]
    for _ in range(MONTHS):
        result.append((y,m))
        y,m=previous_month(y,m)
    return list(reversed(result))

def extract_month(year,month,at):
    period=f"{year:04d}-{month:02d}"
    url=BASE+f"chirps-v3.0.{year:04d}.{month:02d}.tif"
    resp=None
    error=None
    for n in range(2):
        try:
            resp=SESSION.get(url,timeout=(20,100))
            if resp.status_code in (404,410):
                raise FileNotFoundError(f"Archivo no publicado HTTP {resp.status_code}")
            resp.raise_for_status()
            if len(resp.content)<100000 or len(resp.content)>MAX_RASTER_BYTES:
                raise ValueError("GeoTIFF de tamaño inesperado")
            if not (resp.content[:4] in (b"II*\x00",b"MM\x00*",
                                          b"II+\x00",b"MM\x00+")):
                raise ValueError("La respuesta no es TIFF")
            with MemoryFile(resp.content) as mem:
                with mem.open() as ds:
                    if ds.count!=1 or ds.crs is None:
                        raise ValueError("El producto no tiene CRS o contiene bandas inesperadas")
                    if not all(abs(abs(res)-.05)<.0001 for res in ds.res):
                        raise ValueError("Resolución del producto distinta de 0,05 grados")
                    units=str(ds.units[0] or "").strip().lower() if ds.units else ""
                    # El proveedor documenta precipitación mensual en mm.
                    # Si raster declara una unidad distinta, detener la ingesta.
                    if units and units not in ("mm","millimeter","millimeters"):
                        raise ValueError("Unidad distinta de mm: "+units[:60])
                    output=[]
                    for name,lat,lon in POINTS:
                        xx,yy=reproject("EPSG:4326",ds.crs,[lon],[lat])
                        x,y=xx[0],yy[0]
                        if not(ds.bounds.left<x<ds.bounds.right and
                               ds.bounds.bottom<y<ds.bounds.top):
                            raise ValueError(f"Punto {name} fuera de cobertura")
                        val=next(ds.sample([(x,y)],indexes=1,masked=True))[0]
                        if np.ma.is_masked(val):
                            raise ValueError(f"Raster sin dato en {name}")
                        amount=float(val)
                        if not math.isfinite(amount) or amount<0 or amount>10000:
                            raise ValueError(f"Precipitación inválida en {name}: {amount}")
                        row,col=ds.index(x,y)
                        centerx,centery=ds.xy(row,col,offset="center")
                        plon,plat=reproject(ds.crs,"EPSG:4326",[centerx],[centery])
                        output.append({
                            "mes":period,"estacion_referencial":name,
                            "lluvia_estimada_mm":f"{amount:.3f}",
                            "latitud_consultada":f"{lat:.8f}",
                            "longitud_consultada":f"{lon:.8f}",
                            "latitud_centro_pixel":f"{plat[0]:.7f}",
                            "longitud_centro_pixel":f"{plon[0]:.7f}",
                            "resolucion_grados":"0.05",
                            "producto":VERSION,
                            "tipo_dato":"ESTIMADO_SATELITAL_GAUGE_BLEND",
                            "url_raster":url,
                            "fecha_consulta_utc":at
                        })
            return output,{
              "mes":period,"estado":"descargado_y_extraido",
              "fuente":url,"bytes":len(resp.content),
              "sha256":hashlib.sha256(resp.content).hexdigest(),
              "last_modified_http":resp.headers.get("Last-Modified"),
              "etag_http":resp.headers.get("ETag"),
              "estaciones_extraidas":len(output),
              "unidad":"mm/mes","tipo_dato":"ESTIMADO_SATELITAL_GAUGE_BLEND"
            }
        except (requests.RequestException,FileNotFoundError,ValueError,RuntimeError,OSError) as exc:
            error=exc
            if isinstance(exc,FileNotFoundError):
                break
            if n==0:
                time.sleep(2)
    return [],{
      "mes":period,"estado":"no_disponible",
      "fuente":url,"estaciones_extraidas":0,
      "error":f"{type(error).__name__}: {str(error)[:180]}" if error else "desconocido"
    }

def export_csv(path,rows,columns):
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def main():
    stamp=dt.datetime.now(dt.timezone.utc)
    now=stamp.date()
    at=stamp.isoformat(timespec="seconds")
    selection=target_months(now)
    observations=[]
    audit=[]
    for year,month in selection:
        monthly,meta=extract_month(year,month,at)
        observations.extend(monthly)
        audit.append(meta)
        print(f"{meta['mes']}: {meta['estado']} ({len(monthly)} puntos)",flush=True)
    available={m["mes"] for m in audit if m["estado"]=="descargado_y_extraido"}
    if len(observations)!=5*len(available):
        raise ValueError("Cobertura espacial incompleta en mes marcado válido")
    if len(set((r["mes"],r["estacion_referencial"]) for r in observations))!=len(observations):
        raise ValueError("Duplicados estación-mes")
    all_months=[f"{y:04d}-{m:02d}" for y,m in selection]
    if any(m not in all_months for m in available):
        raise ValueError("Mes extra fuera de ventana")
    validvals=[float(r["lluvia_estimada_mm"]) for r in observations]
    if any(not math.isfinite(v) or v<0 for v in validvals):
        raise ValueError("Datos inexistentes o negativos")
    months_index={key:i for i,key in enumerate(all_months)}
    latest=max(available) if available else None
    lag=(len(all_months)-1-months_index[latest]) if latest else None
    state={
        "fase":"3Z",
        "producto":VERSION,
        "tipo_dato":"ESTIMADO_SATELITAL_GAUGE_BLEND",
        "periodicidad":"mensual",
        "proveedor":"UCSB Climate Hazards Center",
        "periodo_analizado_inicio":all_months[0],
        "periodo_analizado_fin_ultimo_mes_calendario_terminado":all_months[-1],
        "fecha_ejecucion_utc":at,
        "meses_con_raster_verificado":len(available),
        "meses_no_disponibles":len(all_months)-len(available),
        "ultimo_mes_disponible":latest,
        "desfase_en_meses_respecto_al_ultimo_mes_cerrado":lag,
        "registros_punto_mes":len(observations),
        "puntos_oaf_provisionales":5,
        "resultado":(
          "sin_datos" if not available else
          "con_rezago" if lag is not None and lag>=2 else
          "disponible_para_ventana_consultada"),
        "actualizacion_automatico_semanal_programado":True,
        "edicion_final_o_preliminar_no_confirmada_por_archivo":True,
        "anios_observados_senamhi_nuevos_certificados":0,
        "validacion_externa_independiente":False,
        "prediccion_propia":False,
        "alerta_oaf":False,
        "medicion_estacion_senamhi":False,
        "coordenadas_historicas_senamhi_confirmadas":False,
        "advertencia":"CHIRPS es precipitación estimada satélite/pluviómetro a escala de pixel; no es pluviómetro ni pronóstico ni alerta; los meses faltantes NO se imputan."
    }
    fields=["mes","estacion_referencial","lluvia_estimada_mm",
            "latitud_consultada","longitud_consultada",
            "latitud_centro_pixel","longitud_centro_pixel",
            "resolucion_grados","producto","tipo_dato",
            "url_raster","fecha_consulta_utc"]
    export_csv(DATA/"chirps_v3_reciente_3z.csv",observations,fields)
    (DATA/"auditoria_rasters_chirps_3z.json").write_text(
       json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (DATA/"estado_monitoreo_3z.json").write_text(
       json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=[
       "# OAF-Lambayeque | Fase 3Z: primera extracción de CHIRPS v3 reciente","",
       "**No es un pronóstico meteorológico ni alerta.** CHIRPS combina información satelital y datos pluviométricos.",
       "Cada valor corresponde a **precipitación mensual estimada de una celda de 0,05°**, consultada en las coordenadas OAF históricas provisionales, NO a medición de estación.","",
       "## Periodo y disponibilidad verificada","",
       "- Fecha de consulta UTC: "+at,
       "- Ventana de 12 meses calendarios CERRADOS: "+all_months[0]+" a "+all_months[-1]+".",
       "- Meses con raster descargado y cinco valores revisados: **"+str(len(available))+"**.",
       "- Meses con raster no disponible/fallido: **"+str(len(all_months)-len(available))+"**.",
       "- Último mes CHIRPS realmente accesible: **"+str(latest or "ninguno")+"**.",
       "- Estado de actualización: "+state["resultado"]+".",
       "- La clasificación final/preliminar exacta del archivo no se afirma hasta consultar su metadato oficial; puede revisarse posteriormente.","",
       "## Muestras de cinco puntos por mes","",
       "| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca |",
       "|---|---:|---:|---:|---:|---:|"]
    for month in sorted(available):
        m={r["estacion_referencial"]:r["lluvia_estimada_mm"] for r in observations if r["mes"]==month}
        md.append("| "+month+" | "+" | ".join(m.get(k,"—") for k,_,_ in POINTS)+" |")
    md+=["","## Meses no disponibles",""]
    unavailable=[x for x in audit if x["estado"]!="descargado_y_extraido"]
    if not unavailable:md.append("No se encontraron faltantes en los doce meses cerrados consultados.")
    else:
        for x in unavailable:md.append("- **"+x["mes"]+"**: "+str(x.get("error","No disponible"))+" ("+x["fuente"]+")")
    md+=["","## Condiciones científicas","",
         "- No se sustituyeron archivos no disponibles por cero ni por productos alternativos.",
         "- Los cinco puntos son referenciales y pueden no coincidir con el emplazamiento instrumental histórico.",
         "- La disponibilidad de un GeoTIFF no implica independencia respecto a pluviómetros SENAMHI.",
         "- Estos valores no certifican años 2016–2025 de lluvia instrumental ni permiten por sí solos pronosticar El Niño Costero.",
         "- El intervalo termina en el último mes calendario cerrado. No aparece un valor de mes en curso incompleto.",
         "- Verificar la condición preliminar/final mediante metadatos de publicación; no inferirla del nombre del fichero.",
         "- Un fichero puede sufrir revisiones; se registra SHA256, fecha y HTTP Last-Modified cuando exista.",
         "- La agenda semanal automática actualiza datos, pero no garantiza puntualidad de publicación de la fuente.",
         "- El estado oficial de El Niño Costero se obtiene de ENFEN, no se infiere de estos cinco píxeles.","",
         "## Fuentes y artefactos","",
         "- Proveedor: https://www.chc.ucsb.edu/data/chirps3",
         "- Servidor oficial de GeoTIFF: "+BASE,
         "- Serie CSV: datos/chirps_v3_reciente_3z.csv",
         "- Auditoría de ficheros: datos/auditoria_rasters_chirps_3z.json",
         "- Estado público: datos/estado_monitoreo_3z.json",
         "- Script: scripts/monitoreo_chirps_reciente_3z.py",""]
    (ROOT/"MONITOREO_CHIRPS_RECIENTE_3Z.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2),flush=True)
    if not available:
        raise SystemExit("Sin meses disponibles; estado y metadatos guardados, pipeline falla para notificar")

if __name__=="__main__":
    main()
