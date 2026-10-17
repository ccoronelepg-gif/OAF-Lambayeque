#!/usr/bin/env python3
"""8Y: asociaciones exploratorias entre CAMS PM2.5/PM10 y clima ERA5 2023-2025.
SIN correlacion causal, p-valores, ni prediccion de aire/agricultura.
Se reportan Pearson bruto, desestacionalizado y sensibilidad por año excluido.
Puntos CAMS con series PM identicas NO representan 2 muestras independientes.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path("datos")
SRC_PM = BASE / "aire_8x" / "particulas_mensuales_8x.csv"
META_PM = BASE / "aire_8x" / "estado_aire_8x.json"
SRC_CLIMA = BASE / "integracion_8v" / "matriz_terrestre_8v.csv"
DEST = BASE / "diagnostico_pm_8y"
YEARS = (2023, 2024, 2025)
SITES = ("Chiclayo", "Jayanca", "Motupe", "Olmos")
PM = ("pm25_media_ug_m3", "pm10_media_ug_m3")
WEATHER = ("viento_10m_m_s", "precipitacion_mes_mm",
           "temperatura_aire_c", "radiacion_mes_mj_m2", "anomalia_nino12_c")
MIN_MONTHS = 24

def parse_csv(path):
    original = path.read_bytes()
    return list(csv.DictReader(io.StringIO(original.decode("utf-8-sig")))), hashlib.sha256(original).hexdigest()

def numeric(row, field):
    try: val = float(row[field])
    except (ValueError, KeyError, TypeError): raise ValueError("Missing numeric: " + field) from None
    if not math.isfinite(val): raise ValueError("Nonfinite: " + field)
    return val

def pearson(xs, ys):
    if len(xs) != len(ys) or len(xs) < 3: return None
    a = sum(xs)/len(xs); b = sum(ys)/len(ys)
    u = sum((x-a)**2 for x in xs)
    v = sum((y-b)**2 for y in ys)
    if u<=1e-14 or v<=1e-14:return None
    r=sum((x-a)*(y-b) for x,y in zip(xs,ys))/math.sqrt(u*v)
    return min(1.0,max(-1.0,r))

def seasonally_centered(records):
    # Demean per calendar month over AVAILABLE years (descriptive only).
    grouped=defaultdict(list)
    for dt, x, y in records:
        grouped[dt[5:]].append((x,y))
    norm={key:(sum(a for a,b in vals)/len(vals),
               sum(b for a,b in vals)/len(vals))
          for key, vals in grouped.items()}
    return [(x-norm[dt[5:]][0], y-norm[dt[5:]][1]) for dt,x,y in records]

def statistics(records):
    if len(records)<MIN_MONTHS:return {"pearson_bruto":None,
        "pearson_sin_ciclo_mensual":None,"coincidencias":len(records),
        "cortes_exclusion_anual_disponibles":0,"signo_sin_ciclo_estable":None}
    x=[r[1] for r in records];y=[r[2] for r in records]
    d=seasonally_centered(records)
    raw=pearson(x,y); adjusted=pearson([r[0] for r in d],[r[1] for r in d])
    cuts=[]
    for year in YEARS:
        s=[r for r in records if not r[0].startswith(str(year))]
        if len(s)>=MIN_MONTHS:
            sub=seasonally_centered(s)
            val=pearson([r[0] for r in sub],[r[1] for r in sub])
            if val is not None:cuts.append(val)
    stable=(bool(adjusted is not None and cuts and
                 all((v>0)==(adjusted>0) for v in cuts))
            if adjusted is not None else None)
    return {"pearson_bruto":round(raw,6) if raw is not None else None,
        "pearson_sin_ciclo_mensual":round(adjusted,6) if adjusted is not None else None,
        "coincidencias":len(records), "cortes_exclusion_anual_disponibles":len(cuts),
        "r_desestacionalizada_excluyendo_anio":[round(v,6) for v in cuts],
        "signo_sin_ciclo_estable":stable}

def analyze(root="."):
    root=Path(root)
    pm,sha_pm=parse_csv(root/SRC_PM)
    weather,sha_weather=parse_csv(root/SRC_CLIMA)
    meta=json.loads((root/META_PM).read_text(encoding="utf-8"))
    if (meta.get("tipo")!="modelo_atmosferico_no_medicion_instrumental" or
        meta.get("comparacion_legal_ECA_habilitada") is not False):
        raise ValueError("Origen CAMS o salvaguarda reglamentaria incorrecta")
    byclim={}
    for row in weather:
        key=(row["localidad"],row["mes"])
        if key in byclim:raise ValueError("Duplicate weather")
        byclim[key]=row
    bysite=defaultdict(list)
    unique=set()
    for row in pm:
        key=(row["localidad"],row["mes"])
        if key in unique:raise ValueError("Duplicate PM")
        unique.add(key)
        if row["localidad"] not in SITES:raise ValueError("Site outside inventory")
        if int(row["mes"][:4]) not in YEARS:continue
        if row.get("mes_pm_completo_80pct")=="True":
            for var in PM:
                if numeric(row,var)<0:raise ValueError("Negative PM")
            bysite[row["localidad"]].append(row)
    # Reject false reporting of 36 consecutive months if all months absent.
    if sum(len(v) for v in bysite.values())!=int(meta["meses_pm_80pct_aptos"]):
        raise ValueError("CAMS coverage state and real monthly rows disagree")
    dup_pairs=meta.get("series_pm_identicas",[])
    rows=[]
    for site in SITES:
        for variable in PM:
            for feature in WEATHER:
                p=[]
                for r in sorted(bysite[site],key=lambda v:v["mes"]):
                    c=byclim.get((site,r["mes"]))
                    if c is not None:
                        p.append((r["mes"],numeric(r,variable),numeric(c,feature)))
                st=statistics(p)
                rows.append({"localidad":site,"particula":variable,
                             "meteorologia":feature,"meses_comunes":len(p),
                             **st,"evaluacion_descriptiva_permitida":len(p)>=MIN_MONTHS,
                             "duplicacion_espacial_pm":any(site in pair["sitios"]
                                                         for pair in dup_pairs)})
    # Independence: list unique PM fingerprints, never sum sites as independent.
    fingerprints={}
    for site in SITES:
        series=tuple((r["mes"],r["pm25_media_ug_m3"],r["pm10_media_ug_m3"])
            for r in sorted(bysite[site],key=lambda a:a["mes"]))
        if series:
            digest=hashlib.sha256(repr(series).encode()).hexdigest()
            fingerprints[site]=digest
    unique_pm=len(set(fingerprints.values()))
    report={
        "fase":"8Y","estado":"evaluacion_asociaciones_no_causal",
        "periodo":"2023-2025","datos_pm_fuente":"CAMS Global modelado, no sensor",
        "clima_fuente":"ERA5 ERA5-Land y NOAA CPC revisados, reanalisis",
        "n_meses_pm_con_cobertura":sum(len(v) for v in bysite.values()),
        "anios_pm_archivados_con_cobertura":sorted({int(r["mes"][:4]) for rs in bysite.values() for r in rs}),
        "n_series_localidad_disponibles":sum(bool(bysite[x]) for x in SITES),
        "n_series_pm_unicas_en_periodo":unique_pm,
        "parejas_series_identicas":dup_pairs,
        "n_comparaciones":len(rows),
        "n_comparaciones_evaluables":sum(z["evaluacion_descriptiva_permitida"] for z in rows),
        "n_comparaciones_36_meses":sum(z["meses_comunes"]==36 for z in rows),
        "series_historicas_pm_1996_2025_no_obtenidas":True,
        "numero_estaciones_aire_locales_validadas":0,
        "humedad_relativa_pm_historica_integrada":False,
        "uso_pm_como_predictor_climatico_aprobado":False,
        "alertas_por_pm_o_fitosanidad_aprobadas":False,
        "inferencia_causal_permitida":False,
        "ajuste_estacional":"restar medias de mes calendario de 2023-2025; sólo descriptivo",
        "incertidumbre":"solo 3 años y autocorrelacion; sin p-valores ni intervalos calibrados",
        "entrada_sha256":{"PM":sha_pm,"clima":sha_weather},
        "comparaciones":rows
    }
    return report

def execute(root=".",check=False):
    root=Path(root)
    report=analyze(root)
    target=root/DEST
    payload=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    if check:
        if (target/"estado_diagnostico_pm_8y.json").read_bytes()!=payload:
            raise AssertionError("El análisis de 8Y no coincide con las fuentes actuales")
    else:
        target.mkdir(parents=True,exist_ok=True)
        (target/"estado_diagnostico_pm_8y.json").write_bytes(payload)
    return {k:v for k,v in report.items() if k!="comparaciones"}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",default=".")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    print(json.dumps(execute(args.root,args.check),ensure_ascii=False,indent=2))
