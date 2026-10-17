#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF Lambayeque: identificación instrumental 9F y contraste de 1998.

Revalida hashes de los ficheros originales, compara fecha y magnitud EXACTAS
de extremos con referencias publicadas por SENAMHI. Las coordenadas/altitudes
se citan como REFERENCIAS CARTOGRÁFICAS con discrepancias históricas, NO como
levantamientos topográficos de la posición exacta de cada sensor.
No se usa este programa para certificar ERA5, CHIRPS ni pronósticos.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import estaciones_instrumentales_9d as d9

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"datos/validacion_estaciones_9f/identificacion_territorial_9f.json"
INVENTORY=ROOT/"datos/validacion_estaciones_9e/metadatos_identidad_9e.json"
MONTHLY=ROOT/"datos/estaciones_9d/series_mensuales_9d.csv"

SEN_EXTREMES="https://www.senamhi.gob.pe/load/file/02245SENA-4.pdf"
SEN_2015="https://sigrid.cenepred.gob.pe/docs/PARA%20PUBLICAR/SENAMHI/Validacion%20de%20datos%20CHIRPS%20de%20Precipitacion%20para%20Monitoreo%20de%20Periodos%20Secos%20y%20Humedos%20en%20el%20Peru.pdf"
SEN_CLIM="https://www.senamhi.gob.pe/load/file/01401SENA-77.pdf"
SEN_ATLAS="https://www.senamhi.gob.pe/pdf/anexos-atlas-climatico.pdf"
MINAG="https://www.ana.gob.pe/sites/default/files/normatividad/files/condiciones_agroclimaticas_arroz_0_2.pdf"

# Referencia 2024 SENAMHI: 02245SENA-4.pdf, Tabla 3. La ubicación oficial
# está tomada de la fuente citada, NO del contenido de los 3 archivos.
STATIONS=(
    {
        "codigo_archivo":"00000340","codigo_fuente":"000340",
        "nombre":"El Espinal","nombre_indicado_usuario":"Espinal",
        "sector":"Oyotún · Chiclayo",
        "coordenadas_publicadas":[-6.817527778,-79.201611111],
        "altitud_publicada_m":409,
        "alternativas_altitud_m":[371,408.6],
        "fuentes_alternativas_altitud":[SEN_ATLAS,"https://www.senamhi.gob.pe/load/file/02245SENA-5.pdf"],
        "ubicacion_alternativa":["6°49'32 S, 79°12'59 O (documento MINAG)",MINAG],
        "extremo":{"fecha":"1998-02-20","lluvia_mm":107.0},
        "fuente_codigo":MINAG
    },
    {
        "codigo_archivo":"00153114","codigo_fuente":"153114",
        "nombre":"Puchaca","nombre_indicado_usuario":"Pucha",
        "sector":"Incahuasi · Ferreñafe",
        "coordenadas_publicadas":[-6.373638889,-79.4695],
        "altitud_publicada_m":355,
        "alternativas_altitud_m":[500,800],
        "fuentes_alternativas_altitud":[
            "https://www.senamhi.gob.pe/pdf/estudios/hidro_varPluvio_anualCuatri.pdf",SEN_CLIM],
        "ubicacion_alternativa":["6°21 S, 79°28 O (catálogo histórico)",SEN_CLIM],
        "extremo":{"fecha":"1998-01-06","lluvia_mm":150.2},
        "fuente_codigo":SEN_CLIM
    },
    {
        "codigo_archivo":"00152107","codigo_fuente":"152107",
        "nombre":"Virrey","nombre_indicado_usuario":"Virrey",
        "sector":"Olmos · Lambayeque",
        "coordenadas_publicadas":[-5.580833333,-79.969888889],
        "altitud_publicada_m":264,
        "alternativas_altitud_m":[275,214],
        "fuentes_alternativas_altitud":[SEN_2015,
            "https://repositorio.ana.gob.pe/bitstream/handle/20.500.12543/2031/ANA0000882_1.pdf"],
        "ubicacion_alternativa":["5°34'33 S, 79°58'58 O (SENAMHI 2015)",SEN_2015],
        "extremo":{"fecha":"2012-02-10","lluvia_mm":330.0},
        "fuente_codigo":SEN_2015
    }
)
assert len(STATIONS)==3
def haversine(a,b):
    r=6371.
    lat1,lon1=(math.radians(v) for v in a)
    lat2,lon2=(math.radians(v) for v in b)
    q=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2*r*math.asin(min(1,math.sqrt(q)))

def read_monthly():
    by=defaultdict(dict)
    with MONTHLY.open(encoding="utf8",newline="") as f:
        for r in csv.DictReader(f):
            key=(r["codigo"],r["mes"])
            if key in by[r["codigo"]]:raise ValueError("Mes duplicado "+str(key))
            by[r["codigo"]][r["mes"]]={
                "dias_validos":int(r["precip_dias_validos"]),
                "dias_calendario":int(r["dias_calendario"]),
                "lluvia_mm":float(r["precip_total_mm"]) if r["precip_total_mm"]!="" else None
            }
    return by

def rain_complete(record):
    return bool(record and record["dias_validos"]==record["dias_calendario"] and record["lluvia_mm"] is not None)

def strict_annual(by,year):
    a=[by.get(f"{year:04d}-{m:02d}") for m in range(1,13)]
    return round(sum(r["lluvia_mm"] for r in a),2) if all(rain_complete(r) for r in a) else None

def median(values):
    a=sorted(values)
    if not a:return None
    return (a[(len(a)-1)//2]+a[len(a)//2])/2

def validation(code,by,identity):
    if identity["nombre"]!=next(x["nombre"] for x in STATIONS if x["codigo_archivo"]==code):
        raise ValueError("Nombre en 9E difiere del corroborado")
    years={}
    for y in range(1996,2014):
        years[y]=strict_annual(by,y)
    base={y:v for y,v in years.items() if y not in (1997,1998) and v is not None}
    target=years[1998]
    if len(base)<12 or target is None:
        raise ValueError("No existen referencias anuales/objetivo suficientes")
    avg=sum(base.values())/len(base)
    seasonal=[]
    for month in (1,2,3,4):
        vals=[
            by[f"{y:04d}-{month:02d}"]["lluvia_mm"]
            for y in range(1996,2014) if y not in (1997,1998)
            and rain_complete(by.get(f"{y:04d}-{month:02d}"))
        ]
        x=by.get(f"1998-{month:02d}")
        seasonal.append({
            "mes":month,
            "referencia":f"1996–2013 sin 1997 y 1998 ({len(vals)} años)",
            "lluvia_observada_1998_mm":x["lluvia_mm"] if rain_complete(x) else None,
            "mediana_mes_mm":round(median(vals),3) if vals else None,
            "n_base":len(vals)
        })
    return {
        "anio_extremo":1998,
        "lluvia_1998_mm":target,
        "anos_base_validos":len(base),
        "anos_excluidos_de_base":[1997,1998],
        "media_anual_base_exploratoria_mm":round(avg,3),
        "mediana_anual_base_exploratoria_mm":round(median(list(base.values())),3),
        "factor_sobre_media_base":round(target/avg,2) if avg>0 else None,
        "descripcion":"Contraste descriptivo entre 1998 y 1996–2013 excluyendo 1997/1998. No es una normal de 30 años ni verificación fuera de muestra de pronósticos.",
        "meses_enero_abril":seasonal
    }

def build():
    registry=json.loads(INVENTORY.read_text(encoding="utf8"))
    identity={x["codigo_archivo"]:x for x in registry["estaciones"]}
    months=read_monthly()
    stations=[]
    for station in STATIONS:
        code=station["codigo_archivo"]
        info=d9.INPUTS[code]
        raw,_=d9.load_source(code,info) # valida SHA y calendario de 1963/64 a 2013/14
        event=station["extremo"]
        yr,mo,dy=event["fecha"].split("-")
        sought=f"{int(yr)} {int(mo)} {int(dy)} "
        matched=[r.split() for r in (d9.RAW/info["filename"]).read_text("utf8").splitlines() if r.startswith(sought)]
        if len(matched)!=1 or float(matched[0][3])!=event["lluvia_mm"]:
            raise AssertionError("Falló extremo SENAMHI "+station["nombre"]+" "+str(matched))
        if identity[code]["codigo_oficial"]!=station["codigo_fuente"]:
            raise ValueError("Código oficial 9E no armonizado: "+code)
        entry={
            "codigo_archivo":code,"codigo_catalogo":station["codigo_fuente"],
            "nombre":station["nombre"],"nombre_indicado_usuario":station["nombre_indicado_usuario"],
            "sector_referencia":station["sector"],
            "correspondencia_archivo_ficha":"documental_fuertemente_corroborada_por_codigo_y_maximo_diario",
            "dia_maximo_coincidente":event,"hash_original_sha256":raw["raw_sha256"],
            "fuentes_codigo_y_valor":[station["fuente_codigo"],SEN_EXTREMES],
            "coordenadas_dereferencia":[round(x,9) for x in station["coordenadas_publicadas"]],
            "fuente_cartografica":SEN_EXTREMES,
            "altitud_de_referencia_m":station["altitud_publicada_m"],
            "altitudes_alternativas_publicadas_m":station["alternativas_altitud_m"],
            "fuentes_alternativas_altitud":station["fuentes_alternativas_altitud"],
            "otra_ubicacion_publicada":station["ubicacion_alternativa"],
            "estado_cartografico":"referencia_documental_oficial; divergencias de coordenadas/altura no conciliadas; no garantía de posición histórica exacta",
            "medicion_termina_en":raw["fin"],
            "uso_en_mapas":"solo referencia puntual aproximada con incertidumbre explícita",
            "uso_para_validar_modelo_espacial":"pendiente_analisis_sensibilidad_celdas_y_fecha_instrumental",
            "resumen_1998":validation(code,months[code],identity[code]),
        }
        stations.append(entry)
    distances=[]
    for i in range(len(STATIONS)):
        for j in range(i+1,len(STATIONS)):
            a,b=STATIONS[i],STATIONS[j]
            distances.append({
                "estacion_a":a["nombre"],"estacion_b":b["nombre"],
                "distancia_entre_referencias_km":round(haversine(a["coordenadas_publicadas"],b["coordenadas_publicadas"]),1),
                "advertencia":"distancia entre posiciones publicadas, no proximidad instrumental exacta"
            })
    return {
        "fase":"9F","fecha_auditoria":"2026-10-17",
        "nombres_y_codigos_encontrados":True,
        "fuente_reporte_extremos_SENAMHI":SEN_EXTREMES,
        "fuente_codigo_virrey_SENAMHI_2015":SEN_2015,
        "normal_1996_2025_completa":False,
        "identidad_verificada_por_3_coincidencias_diarias":True,
        "coordenadas_historicas_sin_incertidumbre":False,
        "geolocalizacion_parcelaria":False,
        "estimaciones_reanalisis_verificadas":False,
        "estaciones":stations,"distancias_documentales":distances,
        "restricciones":[
            "Los tres archivos tienen máximo histórico exacto con día y magnitud publicados en SENAMHI; no implica certificación de calidad de toda la serie.",
            "Distintas publicaciones asignan alturas o emplazamientos diferentes a algunas estaciones; no atribuir exactitud parcelaria al mapa.",
            "Las altitudes no prueban por sí mismas pertenencia a una zona homogénea ni caracterizan todos los pisos altitudinales de Lambayeque.",
            "Las referencias 1996–2013 excluyendo 1997 y 1998 son exploratorias y NO son normal climatológica 1996–2025.",
            "No se valida habilidad predictiva OAF con series históricas 1963–2014 porque no existe retrospectiva con vintage de emisión."
        ]
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    output=json.dumps(build(),ensure_ascii=False,indent=2)+"\n"
    if a.check:
        if OUT.read_text("utf8")!=output:raise SystemExit("Archivo de auditoría 9F no reproducible")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(output,encoding="utf8")
    print("9F OK: 3 códigos y extremos diarios confirmados; referencias cartográficas con incertidumbre; análisis exploratorio 1998.")

if __name__=="__main__":
    main()
