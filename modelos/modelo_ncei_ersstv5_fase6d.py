#!/usr/bin/env python3
"""OAF-Lambayeque Fase 6D: NOAA NCEI ERSSTv5 Niño1+2 rebased to 1991-2020.

NCEI convenience anomaly series: 1971-2000, columns YEAR MONTH NINO3 NINO4 NINO34 NINO12.
Rebase month by month by subtracting monthly 1991-2020 anomaly means.
This transformation is OAF-derived and NOT the official ICEN or NOAA CPC series.
Calculates month-ahead AR(1) model + 1-3 month walk-forward using Fase6C engine.
"""
import argparse
import csv
import json
import math
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from modelo_ersstv5_nino12_fase6c import evaluate, advance_month

SOURCE="https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat"
DIR=Path("datos")
ARCHIVE=DIR/"noaa_ersstv5_nino12_mensual.csv"
OUT=DIR/"modelo_ersstv5_ncei_6d.json"
MIN_OVERLAP=60


def parse_ncei(text):
    """Data description: https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/Readme"""
    raw,keys=[],set()
    for line in text.splitlines():
        p=line.split()
        if len(p)!=6 or not p[0].isdigit() or not p[1].isdigit():
            continue
        yr,mo=int(p[0]),int(p[1])
        if not (1854<=yr<=2100 and 1<=mo<=12):
            raise ValueError("Invalid year-month")
        date=f"{yr:04d}-{mo:02d}"
        if date in keys:raise ValueError("Duplicate month "+date)
        n12=float(p[5]) # COL 6: Niño 1+2; others are Niño3, Niño4 and Niño3.4.
        if not math.isfinite(n12) or abs(n12)>12:
            raise ValueError("Out-of-range Niño 1+2 "+date)
        keys.add(date)
        raw.append({"mes":date,"anomalia_1971_2000_c":n12})
    raw.sort(key=lambda x:x["mes"])
    if len(raw)<1900 or raw[0]["mes"]!="1854-01":
        raise ValueError("Unexpected NCEI NOAA time series")
    for prev,cur in zip(raw,raw[1:]):
        if advance_month(prev["mes"])!=cur["mes"]:
            raise ValueError("Discontinuous NCEI months "+prev["mes"]+" → "+cur["mes"])
    return raw


def rebase(raw):
    basis={mon:[] for mon in range(1,13)}
    for row in raw:
        yr,mon=map(int,row["mes"].split("-"))
        if 1991<=yr<=2020:
            basis[mon].append(row["anomalia_1971_2000_c"])
    if any(len(vals)!=30 for vals in basis.values()):
        raise ValueError("Cannot calculate verified 1991-2020 normals")
    offsets={m:statistics.mean(vals) for m,vals in basis.items()}
    series=[{
        "mes":r["mes"],
        "tsm_c":None, # source offers ANOMALIES only; do not invent absolute SST
        "anomalia_ersstv5_c":round(r["anomalia_1971_2000_c"]-offsets[int(r["mes"][5:])],5)
    } for r in raw if r["mes"]>="1950-01"]
    return series,offsets


def compare_cpc(series):
    if not ARCHIVE.exists():return {"estado":"sin_serie_anteriores","calidad_suficiente":False}
    with ARCHIVE.open(encoding="utf-8",newline="") as inp:
        original={r["mes"]:float(r["anomalia_ersstv5_c"]) for r in csv.DictReader(inp)}
    aligned=[(r["mes"],r["anomalia_ersstv5_c"]-original[r["mes"]])
             for r in series if r["mes"] in original]
    if len(aligned)<MIN_OVERLAP:
        return {"estado":"comparacion_insuficiente","calidad_suficiente":False,"meses":len(aligned)}
    recent=aligned[-24:]
    mae=statistics.mean(abs(x[1]) for x in aligned)
    recent_mae=statistics.mean(abs(x[1]) for x in recent)
    maxrecent=max(abs(x[1]) for x in recent)
    # This is a plausibility gate, not a proof of unbiased data.
    acceptable=recent_mae<=0.4 and maxrecent<=0.75
    return {
        "estado":"contraste_rebases_1991_2020",
        "meses_comunes":len(aligned),
        "ultima_fecha_comun":aligned[-1][0],
        "media_abs_diferencias_todos_c":round(mae,4),
        "media_abs_diferencias_ultimos24_c":round(recent_mae,4),
        "max_abs_diferencia_ultimos24_c":round(maxrecent,4),
        "dif_ultimo_c":round(aligned[-1][1],4),
        "umbral_operativo_comparacion":"MAE últimos 24 <=0.4 °C y diferencia absoluta máxima <=0.75 °C",
        "calidad_suficiente":acceptable,
        "no_es_validacion_independiente":True
    }


def run(raw):
    series,offsets=rebase(raw)
    comparison=compare_cpc(series)
    # Fase6C engine uses revised historical NOAA index, NOT real-time forecasts.
    report,quarters,folds=evaluate(series)
    report.update({
        "fase":"6D",
        "fuente":"NOAA NCEI",
        "url_fuente":SOURCE,
        "producto":"ERSSTv5 Niño 1+2 NOAA NCEI: rebajado 1971-2000 -> 1991-2020 por OAF",
        "serie_noaa_orig_anom_base":"1971-2000",
        "serie_oaf_ajustada_base":"1991-2020",
        "transformacion":"Para cada mes calendario restar media de anomalía NCEI 1971-2000 durante 1991-2020",
        "offset_mensual_1971a2000_a_1991a2020_c":{str(m):round(v,5) for m,v in offsets.items()},
        "valores_rebasados_no_indice_oficial":True,
        "es_icen_oficial":False,
        "no_es_clasificacion_enfen":True,
        "es_alerta":False,
        "contraste_cpc_ersstv5":comparison,
    })
    source_recent=report["prediccion_actual_disponible"]
    allowed=bool(source_recent and comparison["calidad_suficiente"])
    report["prediccion_actual_disponible"]=allowed
    report["estado"]="experimental_rebase_verificado_no_operativo" if allowed else "historico_experimental_o_validacion_pendiente"
    if not allowed:
        for horizon in report["modelos_horizontes"].values():
            horizon["pronostico_ar1_c"]=None
            horizon["pronostico_persistencia_c"]=None
            horizon["mes_objetivo"]=None
    # Regardless of retrospective skill, independent prospective verification is absent.
    for horizon in report["modelos_horizontes"].values():
        horizon["mejora_consistente_demostrada"]=False
        horizon["validacion_prospectiva"]=False
    report["advertencias"].extend([
        "El índice NCEI tiene climatología original 1971–2000, ajustada estadísticamente por OAF a 1991–2020; no es el ICEN oficial.",
        "El ajuste de media mensual y la comparación con CPC no prueban identidad de fuentes ni validez operativa.",
        "Aunque la fuente esté vigente, no existe predicción probabilística calibrada ni habilidad prospectiva demostrada.",
    ])
    return series,report,quarters,folds


def download():
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"OAF-Lambayeque/0.3 (scientific reproducibility)"})
    error=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=40) as stream:
                raw=stream.read()
            if not 15000<len(raw)<200000:raise ValueError("Unexpected text size")
            return raw.decode("ascii")
        except (OSError,UnicodeError,ValueError) as e:
            error=e
            if attempt<2:time.sleep(3)
    raise RuntimeError("NCEI NOAA source could not be verified: "+str(error))


def write(series,report,quarters,folds):
    DIR.mkdir(exist_ok=True)
    def table(name,headers,rows):
        with (DIR/name).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
    table("noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv",
          ["mes","tsm_c","anomalia_ersstv5_c"],series)
    table("ncei_ersstv5_backtest_1a3m.csv",
          ["origen","objetivo","horizonte_meses","observado","ar1","persistencia","cero"],folds)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def self_test():
    source=[]
    for year in range(1854,2027):
        maxmonth=9 if year==2026 else 12
        for month in range(1,maxmonth+1):
            v=.2*math.sin(len(source)/18)+.1*math.cos(len(source)/7)+.012*(year-1980)
            source.append(f"{year} {month} 0.0 0.0 0.0 {v:.4f}")
    parsed=parse_ncei("\n".join(source))
    assert len(parsed)>2000 and parsed[-1]["mes"]=="2026-09"
    base,offsets=rebase(parsed)
    assert base[-1]["mes"]=="2026-09"
    assert all(abs(statistics.mean(r["anomalia_ersstv5_c"] for r in base
                                  if 1991<=int(r["mes"][:4])<=2020 and int(r["mes"][5:])==m))<1e-4
               for m in range(1,13))
    try:parse_ncei("\n".join(source).replace("1854 2 ","1854 4 ",1))
    except ValueError:pass
    else:raise AssertionError("Missing record not detected")
    assert advance_month("2026-12",1)=="2027-01"
    print("NCEI rebasing and continuous time-series tests PASS (synthetic).")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:self_test();return
    raw=parse_ncei(download())
    series,report,quarters,folds=run(raw)
    write(series,report,quarters,folds)
    print(json.dumps({"last_month":report["mes_ultimo_observado"],
                      "comparison":report["contraste_cpc_ersstv5"],
                      "forecast_available":report["prediccion_actual_disponible"],
                      "latest_anomaly":report["ultima_anomalia_ersstv5_c"]},ensure_ascii=False))


if __name__=="__main__":
    try:main()
    except Exception as e:
        print("OAF NCEI 6D error: "+str(e),file=sys.stderr)
        raise SystemExit(1)
