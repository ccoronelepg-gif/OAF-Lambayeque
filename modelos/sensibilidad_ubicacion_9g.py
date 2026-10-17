#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9G. Cuantificar incertidumbre geométrica de fichas históricas.

Compara coordenadas publicadas alternativas y las bandas altitudinales OAF.
No usa grillas ERA5 o CHIRPS, no calcula error de predicción ni corrige fichas.
La fuente primaria por estación es el registro documental de fase 9F.
"""
import argparse
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"datos/validacion_estaciones_9f/identificacion_territorial_9f.json"
OUTPUT=ROOT/"datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json"
# Coordenadas alternativas *de los textos explícitamente citados en 9F*.
# No inferidas del clima, datos satelitales o altitud.
ALTERNATES={
    "00000340":{
      "nombre":"El Espinal",
      "coordenadas":[-(6+49/60+32/3600),-(79+12/60+59/3600)],
      "string_origen":"6°49'32 S, 79°12'59 O",
      "descripcion":"ubicación alternativa en documento MINAG"
    },
    "00153114":{
      "nombre":"Puchaca",
      "coordenadas":[-(6+21/60),-(79+28/60)],
      "string_origen":"6°21 S, 79°28 O",
      "descripcion":"ubicación alternativa aproximada en catálogo histórico SENAMHI"
    },
    "00152107":{
      "nombre":"Virrey",
      "coordenadas":[-(5+34/60+33/3600),-(79+58/60+58/3600)],
      "string_origen":"5°34'33 S, 79°58'58 O",
      "descripcion":"ubicación alternativa SENAMHI de estudio 2015"
    }
}
BANDS=((0,99),(100,299),(300,799),(800,1599),(1600,2499),(2500,float("inf")))
def band(alt):
    for a,b in BANDS:
        if a<=alt<=b:
            return f"{a}–{int(b) if math.isfinite(b) else 'más'} m"
    return "fuera de las seis franjas DEM del OAF"
def haversine(a,b):
    lat1,lon1=map(math.radians,a)
    lat2,lon2=map(math.radians,b)
    dlat,dlong=lat2-lat1,lon2-lon1
    q=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlong/2)**2
    return 2*6371.0088*math.asin(min(1,math.sqrt(q)))
def build():
    src=json.loads(SOURCE.read_text(encoding="utf8"))
    assert src["fase"]=="9F" and src["identidad_verificada_por_3_coincidencias_diarias"]
    stations=[]
    for station in src["estaciones"]:
        code=station["codigo_archivo"]
        alt=ALTERNATES[code]
        assert station["nombre"]==alt["nombre"]
        hint=station["otra_ubicacion_publicada"]
        assert len(hint)>=2 and alt["string_origen"] in hint[0]
        ref=[float(v) for v in station["coordenadas_dereferencia"]]
        alternative=alt["coordenadas"]
        assert all(-83<x<-68 for x in (ref[1],alternative[1]))
        assert all(-19<x<-3 for x in (ref[0],alternative[0]))
        heights=[float(station["altitud_de_referencia_m"])] + [float(x) for x in station["altitudes_alternativas_publicadas_m"]]
        groups=sorted(set(band(h) for h in heights))
        shift=haversine(ref,alternative)
        stations.append({
            "nombre":station["nombre"],"codigo_archivo":code,
            "coordenada_documental_1":{"lat":ref[0],"lon":ref[1],
                "url":station["fuente_cartografica"],
                "caracter":"referencia cartográfica publicada; fecha histórica de emplazamiento sin certificar"},
            "coordenada_documental_2":{"lat":round(alternative[0],9),"lon":round(alternative[1],9),
                "url":hint[1],"caracter":alt["descripcion"]},
            "desplazamiento_entre_referencias_km":round(shift,3),
            "altitudes_publicadas_m":heights,
            "altitud_min_m":min(heights),
            "altitud_max_m":max(heights),
            "rango_publicado_altitud_m":round(max(heights)-min(heights),2),
            "franjas_altitudinales_posibles":groups,
            "franja_unica_acreditada":False,
            "tramo_1998_mm":station["resumen_1998"]["lluvia_1998_mm"],
            "mensaje":"Los cambios de emplazamiento y de altura pueden alterar las comparaciones con píxeles; datos de 9F no acreditan qué referencia corresponde al sensor en cada año.",
            "parejas_observacion_vs_CHIRPS":0,
            "parejas_observacion_vs_ERA5_Land":0,
            "riesgo_desfase_geografico":"elevado" if shift>=2 or len(groups)>1 else "requiere_revision"
        })
    assert len(stations)==3 and all(s["desplazamiento_entre_referencias_km"]>0 for s in stations)
    return {
        "fase":"9G","fecha_revision":"2026-10-17",
        "dictamen":"evaluacion_de_incertidumbre_de_fichas; productos_grillados_no_extraidos",
        "identidad_nombres_corroborada":True,
        "ubicacion_sensor_1963_2014_certificada":False,
        "comparacion_era5_chirps_ejecutada":False,
        "metricas_mae_rmse_sesgo_calculadas":False,
        "origen":"metadatos públicos documentados en 9F, no coordenadas derivadas de ERA5/CHIRPS",
        "interpretacion_espacial":"Las resoluciones nominales 0,05° y 0,1° no acreditan por sí solas un píxel comparable; se necesita confirmar centros reales de celda y cobertura temporal de cada producto.",
        "estaciones":stations,
        "criterios_para_9H":[
          "Obtener evidencia de emplazamiento e historia de traslados por fecha",
          "Revisar discrepancias de altitud con SENAMHI, especialmente Puchaca",
          "Extraer valores de CHIRPS y ERA5-Land por cada coordenada alternativa sin seleccionar solo la que mejor ajusta",
          "Homologar hora, día, periodo, variable, resolución y producto final/preliminar",
          "Cuantificar dependencia de CHIRPS por posible asimilación del mismo pluviómetro",
          "Calcular sesgo, MAE/RMSE por punto y sensibilidad entre ubicaciones con meses completos, separando observación y predicción"
        ]
    }
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check",action="store_true")
    args=a.parse_args()
    payload=json.dumps(build(),indent=2,ensure_ascii=False)+"\n"
    if args.check:
        assert OUTPUT.read_text(encoding="utf8")==payload,"Datos 9G no reproducibles"
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(payload,encoding="utf8")
    print("9G: 3 pares de coordenadas documentales cuantificados. ERROR grilla: no calculado sin valores extraídos.")
if __name__=="__main__":
    main()
