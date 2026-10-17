#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9I: diagnóstico descriptivo en meses realmente comunes CHIRPS/ERA5/estación.
No extrapola estaciones, no selecciona el mejor escenario ni evalúa pronósticos.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/validacion_estaciones_9i"
FILE=BASE/"diagnostico_multianual_9i.json"
CHIRPS_9H=ROOT/"datos/validacion_estaciones_9h/pares_mensuales_9h.csv"
ERA5_9H=ROOT/"datos/validacion_estaciones_9h/pares_era5_complementarios_9h.csv"
CHIRPS_EXTRA=BASE/"pares_chirps_ampliacion_9i.csv"
EXTRA_MANIFEST=BASE/"fuentes_chirps_ampliacion_9i.json"
YEARS=(1996,1998,2002,2007,2011,2013)
PRODUCTS=("CHIRPS v3","ERA5 atmosférico")

def read_csv(file):
    if not file.exists():return []
    with file.open(newline="",encoding="utf8") as f:
        return list(csv.DictReader(f))

def metrics(pairs):
    if not pairs:return None
    diffs=[r["producto"]-r["estacion"] for r in pairs]
    return {"n_meses":len(pairs),
       "mae_mm_mes":round(sum(abs(x) for x in diffs)/len(diffs),3),
       "rmse_mm_mes":round(math.sqrt(sum(x*x for x in diffs)/len(diffs)),3),
       "sesgo_producto_menos_estacion_mm_mes":round(sum(diffs)/len(diffs),3),
       "lluvia_estacion_mm":round(sum(r["estacion"] for r in pairs),3),
       "lluvia_producto_mm":round(sum(r["producto"] for r in pairs),3)}

def read_pairs():
    chirps=read_csv(CHIRPS_9H)+read_csv(CHIRPS_EXTRA)
    era=read_csv(ERA5_9H)
    data={}
    provenance=set()
    for r in chirps:
        if r["producto"]!="CHIRPS-v3 mensual LATAM":continue
        if int(r["mes"][:4]) not in YEARS:raise ValueError("Año CHIRPS no preinscrito")
        key=("CHIRPS v3",r["codigo_archivo"],r["escenario"],r["mes"])
        if key in data:raise ValueError("Par CHIRPS duplicado")
        entry={"producto":float(r["precipitacion_producto_mm"]),
               "estacion":float(r["precipitacion_estacion_mm"]),
               "nombre":r["nombre"],"sha256":r["sha256_respuesta"]}
        data[key]=entry
        provenance.add(("CHIRPS v3",r["mes"],r["sha256_respuesta"]))
    for r in era:
        if r["variable"]!="precipitation_sum" or r["producto"]!="ERA5_atmosferico":
            continue
        if int(r["mes"][:4]) not in YEARS:continue
        key=("ERA5 atmosférico",r["codigo_archivo"],r["escenario"],r["mes"])
        if key in data:raise ValueError("Par ERA5 duplicado")
        data[key]={"producto":float(r["reanálisis"]),
                   "estacion":float(r["observado"]),
                   "nombre":r["nombre"],"sha256":r["sha256_respuesta"]}
        provenance.add(("ERA5 atmosférico",r["mes"][:4],r["sha256_respuesta"]))
    for k,r in data.items():
        if not all(math.isfinite(r[f]) and r[f]>=0 for f in ("producto","estacion")):
            raise ValueError("Valor de lluvia inválido: "+str(k))
        if len(r["sha256"])!=64:raise ValueError("Huella ausente: "+str(k))
    return data,provenance

def generate():
    data,provenance=read_pairs()
    locations=sorted({(key[1],key[2],v["nombre"]) for key,v in data.items()})
    years=[]
    stations=[]
    comparisons=[]
    for code,scenario,name in locations:
        for year in YEARS:
            months=[f"{year}-{m:02d}" for m in range(1,13)]
            ch=[(m,data.get(("CHIRPS v3",code,scenario,m))) for m in months]
            er=[(m,data.get(("ERA5 atmosférico",code,scenario,m))) for m in months]
            common=[m for m in months
                    if data.get(("CHIRPS v3",code,scenario,m)) is not None
                    and data.get(("ERA5 atmosférico",code,scenario,m)) is not None]
            # Comprobar consistencia exacta de la observación comparada por ambos productos.
            for month in common:
                a=data[("CHIRPS v3",code,scenario,month)]["estacion"]
                b=data[("ERA5 atmosférico",code,scenario,month)]["estacion"]
                if abs(a-b)>0.0001:raise ValueError("Estación incongruente: "+str((code,month)))
            ch_rows=[{"producto":v["producto"],"estacion":v["estacion"]}
                     for m,v in ch if m in common]
            era_rows=[{"producto":v["producto"],"estacion":v["estacion"]}
                     for m,v in er if m in common]
            # No declarar año completo salvo que ambos productos emparejen los 12 meses.
            comparisons.append({
              "codigo_archivo":code,"nombre":name,"escenario":scenario,"anio":year,
              "n_chirps":sum(v is not None for m,v in ch),
              "n_era5":sum(v is not None for m,v in er),
              "n_meses_comunes":len(common),
              "meses_comunes":common,
              "anio_completo_12_meses":len(common)==12,
              "chirps":metrics(ch_rows),"era5":metrics(era_rows),
              "resultado":"descriptivo_no_independiente_sin_ranking_operativo"})
            for product,rows in (("CHIRPS v3",ch_rows),("ERA5 atmosférico",era_rows)):
                stations.append({"codigo_archivo":code,"nombre":name,"escenario":scenario,
                                 "anio":year,"producto":product,"metricas_sobre_meses_comunes":metrics(rows)})
    for year in YEARS:
        items=[q for q in comparisons if q["anio"]==year]
        n_unique=len(set((s["codigo_archivo"],m)
                    for s in items for m in s["meses_comunes"]))
        years.append({"anio":year,
          "meses_estacion_distintos_emparejados":n_unique,
          "pares_duplicados_por_escenario":sum(s["n_meses_comunes"] for s in items),
          "meses_todas_las_estaciones_completas":sum(1 for m in range(1,13)
             if len({s["codigo_archivo"] for s in items
             if f"{year}-{m:02d}" in s["meses_comunes"]})==3),
          "estado":"con_pares" if n_unique else "aun_sin_CHIRPS_extraido"})
    all_chirps=sum(1 for k in data if k[0]=="CHIRPS v3")
    all_era=sum(1 for k in data if k[0]=="ERA5 atmosférico")
    matched=sum(s["n_meses_comunes"] for s in comparisons)
    distinct=len({(s["codigo_archivo"],m) for s in comparisons for m in s["meses_comunes"]})
    manifest=json.loads(EXTRA_MANIFEST.read_text("utf8")) if EXTRA_MANIFEST.exists() else None
    if manifest is not None and manifest["pares_adicionales"]!=len(read_csv(CHIRPS_EXTRA)):
        raise ValueError("Manifiesto CHIRPS inconsistente")
    result={
      "fase":"9I","alcance":"diagnostico retrospectivo comparacion de meses estrictamente coincidentes",
      "anios_prespecificados":list(YEARS),
      "productos":["CHIRPS v3 mensual LATAM","ERA5 atmosférico"],
      "precipitacion_unidad":"mm por mes",
      "estaciones_n":len(set(s["codigo_archivo"] for s in comparisons)),
      "escenarios_documentales_por_estacion":2,
      "total_chirps_pares":all_chirps,
      "total_era5_pares_en_los_anios":all_era,
      "pares_chirps_era5_mes_escenario":matched,
      "meses_estacion_unicos_emparejados":distinct,
      "meses_fuente_chirps_registrados":sorted({k[3] for k in data if k[0]=="CHIRPS v3"}),
      "anios_resumen":years,
      "resultados_estacion_escenario_anio":comparisons,
      "metrica_regla":"MAE, RMSE, sesgo sobre exactamente los mismos meses completos de estación",
      "fuentes_sha256_distintas_n":len(provenance),
      "archivo_fuente_extra_procesado":manifest is not None,
      "problemas_descarga":manifest["problemas"] if manifest else [],
      "exposicion_historica_no_seleccionada_por_ajuste":True,
      "independencia_CHIRPS_validada":False,
      "horario_pluviometrico_validado":False,
      "emplazamiento_historico_certificado":False,
      "pronosticos_archivados_con_vintage":False,
      "modelo_predictivo_calibrado_en_esta_fase":False,
      "cobertura_1996_2025_de_estaciones":False,
      "advertencia":"Los 2 escenarios comparten la observación; no duplicar muestras, no declarar habilidad predictiva."
    }
    return result

def save():
    result=generate()
    BASE.mkdir(parents=True,exist_ok=True)
    FILE.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return result

def check():
    result=generate()
    archived=json.loads(FILE.read_text("utf8"))
    if result!=archived:raise ValueError("Reporte 9I no reproducible a partir de CSV")
    assert result["meses_estacion_unicos_emparejados"]*2==result["pares_chirps_era5_mes_escenario"]
    assert result["anios_prespecificados"]==list(YEARS)
    assert result["estaciones_n"]==3
    assert not result["independencia_CHIRPS_validada"]
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    x=check() if a.check else save()
    print("9I meses estación únicos:",x["meses_estacion_unicos_emparejados"],
          "pares escenario:",x["pares_chirps_era5_mes_escenario"],
          "meses CHIRPS:",len(x["meses_fuente_chirps_registrados"]))
