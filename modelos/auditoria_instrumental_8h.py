#!/usr/bin/env python3
"""OAF 8H: auditoría instrumental/geográfica y preparación de incertidumbre.

Usa únicamente documentos archivados. No obtiene temperaturas de pluviómetros,
no declara independencia ni calcula intervalos 90% para emisiones 8E.
La calibración conformal es una función futura con barreras de fecha; sus
pruebas sintéticas no son datos de OAF. Biblioteca estándar de Python 3.11.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PERU = ZoneInfo("America/Lima")
SITES = {
    "Chiclayo": (-6.77140, -79.84090),
    "Jayanca": (-6.39278, -79.82280),
    "Motupe": (-6.15083, -79.71420),
    "Olmos": (-5.98825, -79.74723),
}
STATIONS = ("Jayanca (La Viña)", "Cayaltí", "Reque", "Lambayeque", "Cueva Blanca")
FILE_STATIONS = "datos/catalogo_instrumental_candidato_8h.csv"
FILE_RAIN = "datos/senamhi_mensual_completo_1996_2015.csv"
FILE_COVER = "datos/estado_cobertura_oficial.json"
FILE_8G = "datos/evaluacion_prospectiva_8g/metricas_8g.json"
OUTPUT_DIR = "datos/auditoria_instrumental_8h"
OUT_JSON = "estado_8h.json"
OUT_CSV = "estaciones_8h.csv"
FIELDS = (
    "estacion","meses_completos_precipitacion","primer_mes","ultimo_mes",
    "anios_completos","ultimo_anio_completo",
    "latitud_referencia_no_certificada","longitud_referencia_no_certificada",
    "alternativa_publicada_disponible","diferencia_posiciones_km",
    "punto_oaf_provisional_mas_cercano","distancia_referencial_km",
    "altitud_publicada_m","serie_temperatura_t2m_instrumental_verificada",
    "codigo_instrumental_verificado","historial_emplazamiento_verificado",
    "identidad_serie_txt_verificada","apto_contraste_8e_temperatura","fuente_metadatos"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def haversine(lat1, lon1, lat2, lon2):
    coords = [lat1,lon1,lat2,lon2]
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in coords):
        raise ValueError("Coordenadas no finitas")
    if any(abs(v)>90 for v in (lat1,lat2)) or any(abs(v)>180 for v in (lon1,lon2)):
        raise ValueError("Coordenadas fuera de rango")
    r = math.pi / 180
    a = math.sin((lat2-lat1)*r/2)**2 + math.cos(lat1*r)*math.cos(lat2*r)*math.sin((lon2-lon1)*r/2)**2
    return 6371.0088*2*math.asin(min(1.,math.sqrt(a)))


def iso_month(value: str) -> str:
    if len(value)!=7 or value[4]!='-' or not value[:4].isdigit() or not value[5:].isdigit():
        raise ValueError("Mes inválido "+repr(value))
    y,m=int(value[:4]),int(value[5:])
    date(y,m,1)
    return value


def maybe_float(value: str):
    if value is None or not value.strip():
        return None
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("Valor no finito")
    return x


def parse_flag(value: str) -> bool:
    if value not in ("true","false"):
        raise ValueError("Indicador de metadatos no reconocido")
    return value=="true"


def stations_registry(root: Path):
    with (root/FILE_STATIONS).open(encoding="utf-8-sig",newline="") as handle:
        rows=list(csv.DictReader(handle))
    if len(rows)!=len(STATIONS) or {r["estacion"] for r in rows}!=set(STATIONS):
        raise ValueError("Catálogo instrumental incompleto o estaciones duplicadas")
    registry={}
    for row in rows:
        site=row["estacion"]
        lat,lon=float(row["latitud_consultada"]),float(row["longitud_consultada"])
        haversine(lat,lon,lat,lon)
        altlat,altlon=maybe_float(row["latitud_candidata_publicada"]),maybe_float(row["longitud_candidata_publicada"])
        if (altlat is None)!=(altlon is None):
            raise ValueError("Par de coordenadas publicado incompleto "+site)
        if altlat is not None:
            haversine(altlat,altlon,lat,lon)
        alt=maybe_float(row["altitud_publicada_m"])
        if alt is not None and not -450<=alt<=7000:
            raise ValueError("Altitud documental imposible")
        code=parse_flag(row["codigo_instrumental_verificado"])
        history=parse_flag(row["continuidad_emplazamiento_verificada"])
        identity=parse_flag(row["identidad_con_serie_txt_verificada"])
        if row["variable_archivo_historico"]!="precipitacion_mm":
            raise ValueError("El archivo instrumental existente solo certifica precipitación")
        if not row["referencia_documental"].startswith("https://"):
            raise ValueError("Fuente documental sin enlace seguro")
        registry[site]={"lat":lat,"lon":lon,"altlat":altlat,"altlon":altlon,"alt":alt,
                        "code":code,"history":history,"identity":identity,
                        "source":row["referencia_documental"]}
    return registry


def rain_inventory(root: Path):
    src=root/FILE_RAIN
    with src.open(encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        expected={"estacion","mes","observado_mm","dias_validos","dias_mes"}
        if not reader.fieldnames or set(reader.fieldnames)!=expected:
            raise ValueError("Esquema de precipitación inesperado; no es una serie de temperatura")
        months={station:{} for station in STATIONS}
        seen=set()
        for row in reader:
            station=row["estacion"]
            if station not in STATIONS:
                raise ValueError("Estación desconocida")
            month=iso_month(row["mes"])
            if not "1996-01"<=month<="2015-12":
                raise ValueError("Mes fuera del alcance instrumental")
            key=(station,month)
            if key in seen:
                raise ValueError("Mes instrumental duplicado")
            seen.add(key)
            mm=maybe_float(row["observado_mm"])
            if mm is None or mm<0 or mm>10000:
                raise ValueError("Lluvia faltante/incorrecta")
            try:
                valid,total=int(row["dias_validos"]),int(row["dias_mes"])
            except (ValueError,TypeError):
                raise ValueError("Metadatos de días incorrectos") from None
            expected_days=calendar.monthrange(int(month[:4]),int(month[5:]))[1]
            if total!=expected_days or valid!=total:
                raise ValueError("El acumulado no incluye todos los días")
            months[station][month]=mm
    return months


def load_8g(root: Path):
    raw=json.loads((root/FILE_8G).read_text(encoding="utf-8"))
    if raw["fase"]!="8G" or raw["validacion_instrumental"] is not False or raw["habilidad_prospectiva_demostrada"] is not False:
        raise ValueError("El archivo 8G no respeta estado experimental")
    return raw


def conformal_radius(calibration: list, emission_utc: str, alpha=.10, min_samples=36):
    """Radio conformal retrospectivo SOLO con errores publicados previamente.

    Entrada esperada: fecha_objetivo YYYY-MM, observado_disponible_utc,
    prediccion_emitida_utc, error_c. Cada registro histórico debe haberse
    emitido antes del inicio del mes objetivo. Se rechaza cualquier ejemplo
    cuya observación fuese conocida después del origen candidato.
    Para series seriales, este cuantíl NO demuestra cobertura nominal futura;
    se requiere una prueba independiente y evaluación temporal específica.
    """
    if not 0<alpha<1 or min_samples<30:
        raise ValueError("Parámetros de calibración no admisibles")
    issuance=datetime.fromisoformat(emission_utc.replace("Z","+00:00"))
    if issuance.tzinfo is None:
        raise ValueError("Origen sin zona")
    issuance=issuance.astimezone(timezone.utc)
    if len(calibration)<min_samples:
        return None
    errors=[]
    months=set()
    for row in calibration:
        target=iso_month(row["fecha_objetivo"])
        if target in months:
            raise ValueError("Mismo mes duplicado en calibración; requiere muestras temporales únicas")
        months.add(target)
        issue=datetime.fromisoformat(row["prediccion_emitida_utc"].replace("Z","+00:00"))
        released=datetime.fromisoformat(row["observado_disponible_utc"].replace("Z","+00:00"))
        if issue.tzinfo is None or released.tzinfo is None:
            raise ValueError("Registros sin zona")
        issue=issue.astimezone(timezone.utc)
        released=released.astimezone(timezone.utc)
        if issue.astimezone(PERU).date()>=date(int(target[:4]),int(target[5:]),1):
            raise ValueError("Estimación intramensual en calibración premes")
        # Un valor del mes objetivo no puede publicarse antes de terminar el mes.
        # 8E exige al menos el día 10 del mes siguiente para reanálisis.
        y,m=int(target[:4]),int(target[5:])
        next_year,next_month=(y+1,1) if m==12 else (y,m+1)
        if released.astimezone(PERU).date()<date(next_year,next_month,10):
            raise ValueError("Verificación fechada antes del cierre y madurez del mes objetivo")
        if not issue<released<issuance:
            raise ValueError("Fuga temporal en disponibilidad instrumental/reanálisis")
        score=maybe_float(str(row["error_c"]))
        if score is None:
            raise ValueError("Error faltante")
        errors.append(abs(score))
    n=len(errors)
    rank=math.ceil((n+1)*(1-alpha))
    if rank>n:
        return None
    return round(sorted(errors)[rank-1],5)


def assess(root: Path):
    registry=stations_registry(root)
    monthly=rain_inventory(root)
    metadata=json.loads((root/FILE_COVER).read_text(encoding="utf-8"))
    evaluation=load_8g(root)
    if metadata.get("imputacion_de_faltantes_permitida") is not False:
        raise ValueError("La política instrumental no puede permitir imputación")
    if int(metadata["meses_estacion_completos"])!=sum(map(len,monthly.values())):
        raise ValueError("La cobertura oficial histórica y el archivo mensual difieren")
    if int(metadata["estaciones"])!=len(registry):
        raise ValueError("Número de estaciones inválido")
    if metadata["serie_continua_2016_2025_certificada"] is not False:
        raise ValueError("2016–2025 no está certificado")
    records=[]
    for site in STATIONS:
        ms=monthly[site]
        years=Counter(int(month[:4]) for month in ms)
        complete_years=sorted(y for y,n in years.items() if n==12)
        expected_last=metadata["ultimo_anio_completo_por_estacion"][site]
        if max(complete_years,default=None)!=expected_last:
            raise ValueError("Año completo final no coincide con auditoría histórica: "+site)
        geo=registry[site]
        candidate=sorted((round(haversine(geo["lat"],geo["lon"],a,b),2),city) for city,(a,b) in SITES.items())
        geo_diff=round(haversine(geo["lat"],geo["lon"],geo["altlat"],geo["altlon"]),2) if geo["altlat"] is not None else None
        # Archivo de lluvia NO tiene Tmax/Tmin/Tmedia: un total pluviométrico no
        # permite inferir la temperatura observada ni validar 8E.
        t2m=False
        ready=t2m and geo["code"] and geo["history"] and geo["identity"]
        records.append({
            "estacion":site,
            "meses_completos_precipitacion":len(ms),
            "primer_mes":min(ms) if ms else None,"ultimo_mes":max(ms) if ms else None,
            "anios_completos":len(complete_years),"ultimo_anio_completo":max(complete_years,default=None),
            "latitud_referencia_no_certificada":geo["lat"],"longitud_referencia_no_certificada":geo["lon"],
            "alternativa_publicada_disponible":geo["altlat"] is not None,
            "diferencia_posiciones_km":geo_diff,
            "punto_oaf_provisional_mas_cercano":candidate[0][1],
            "distancia_referencial_km":candidate[0][0],"altitud_publicada_m":geo["alt"],
            "serie_temperatura_t2m_instrumental_verificada":t2m,
            "codigo_instrumental_verificado":geo["code"],
            "historial_emplazamiento_verificado":geo["history"],
            "identidad_serie_txt_verificada":geo["identity"],
            "apto_contraste_8e_temperatura":bool(ready),
            "fuente_metadatos":geo["source"]
        })
    years_by_station={r["estacion"]:{int(m[:4]) for m in monthly[r["estacion"]]} for r in records}
    common_complete={int(y) for y in range(1996,2016) if all(
        sum(1 for m in monthly[s] if m.startswith(str(y)+"-"))==12 for s in STATIONS)}
    if max(common_complete,default=None)!=int(metadata["ultimo_anio_temporalmente_completo_compartido_cinco_estaciones"]):
        raise ValueError("Último año completo común no corresponde a la fuente")
    if sum(r["anios_completos"] for r in records)!=int(metadata["combinaciones_estacion_anio_completas"]):
        raise ValueError("Cantidad de estaciones-año completas no corresponde")
    n_temp=sum(r["apto_contraste_8e_temperatura"] for r in records)
    result={
        "fase":"8H","tipo":"auditoria_instrumental_de_preparacion",
        "variable_instrumental_existente":"precipitacion mensual (mm)",
        "variable_modelo_8e":"temperatura media mensual a 2 m (°C)",
        "comparabilidad_directa_variables":False,
        "meses_estacion_precipitacion":sum(len(v) for v in monthly.values()),
        "estaciones_historicas_precipitacion":len(records),
        "estacion_anio_completos":sum(r["anios_completos"] for r in records),
        "ultimo_anio_comun_completo":max(common_complete,default=None),
        "serie_temperatura_senamhi_disponible_en_repositorio":False,
        "estaciones_aptas_validacion_temperatura_8e":n_temp,
        "comparaciones_temperatura_instrumental_efectuadas":0,
        "estado_validacion_independiente_temperatura":"pendiente_de_serie_t2m_y_metadatos",
        "numero_emisiones_premes_8g":evaluation["n_premes_archivados"],
        "numero_emisiones_premes_verificadas_era5_8g":evaluation["n_verificados_premes"],
        "intervalos_prediccion_90_publicables":False,
        "radio_90_por_localidad_horizonte":None,
        "cobertura_intervalos_90":None,
        "calibracion_temporal_realizada":False,
        "aptitud_operativa":False,
        "adquisicion_prioritaria":[
            "Tmax/Tmin y, preferiblemente, Tmedia diaria observada a 2 m de estación con códigos de ausencia documentados, para los mismos meses de pronóstico.",
            "Código instrumental oficial de cada serie, WSI si corresponde, latitud/longitud/altitud y tipo de estación.",
            "Historia de traslados y cambios de instrumentos, fechas y método de cálculo de la temperatura media.",
            "Verificación de series diarias completas; coincidencia temporal y geográfica con píxel ERA5-Land.",
            "Documentar posible participación de las estaciones en la generación de productos de reanálisis y corrección de sesgos.",
            "Establecer conjunto futuro de calibración y evaluación sin fuga temporal; archivar intervalos ANTES de observar el objetivo."
        ],
        "separacion_de_fuentes":{
            "senamhi":"archivo histórico de precipitación de estaciones (1996–2015)",
            "era5_land":"reanálisis de temperatura de celda, nunca estación SENAMHI",
            "oaf_8e":"predicciones experimentales de temperatura modelada, sin validación instrumental"
        },
        "advertencias":[
            "La estación meteorológica con nombre de localidad no es necesariamente el mismo punto usado por los modelos regionales.",
            "Las distancias calculadas son geográficas exploratorias entre coordenadas candidatas, NO certifican identidad de estación ni permiten comparar temperaturas.",
            "Cueva Blanca tiene documentación reciente de altitud elevada y no es sustituto automático de estaciones de valles agrícolas.",
            "Ni la precipitación de estaciones ni un historial ERA5-Land equivalen a Tmedia instrumental de SENAMHI.",
            "La técnica conformal es un mecanismo preparatorio: sin predicciones previas, errores documentados antes de la emisión y validación, NO se anuncian intervalos 90%."
        ],
        "trazabilidad":{
            "catalogo_estaciones_sha256":digest(root/FILE_STATIONS),
            "lluvia_historica_sha256":digest(root/FILE_RAIN),
            "metadatos_cobertura_sha256":digest(root/FILE_COVER),
            "informe_8g_sha256":digest(root/FILE_8G)
        },
        "fuentes_oficiales":{
            "senamhi":"https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos",
            "wmo_oscar":"https://wmo.int/activities/global-observing-system-gos/global-observing-system-gos",
            "copernicus_era5_land":"https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land"
        }
    }
    return result,records


def file_json(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+"\n"


def file_csv(rows):
    buf=io.StringIO(newline="")
    writer=csv.DictWriter(buf,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name:"" if row.get(name) is None else str(row[name]).lower()
                         if isinstance(row.get(name),bool) else row.get(name) for name in FIELDS})
    return buf.getvalue()


def run(root: Path, check=False):
    summary,stations=assess(root)
    out=root/OUTPUT_DIR
    files={out/OUT_JSON:file_json(summary),out/OUT_CSV:file_csv(stations)}
    for path,content in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("Informe 8H desactualizado: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8H","meses_instrumentales_de_lluvia":summary["meses_estacion_precipitacion"],
                      "temperaturas_instrumentales_compatibles":summary["estaciones_aptas_validacion_temperatura_8e"],
                      "intervalos_90_publicables":False,"revision":check},ensure_ascii=False))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    run(args.root,args.check)
