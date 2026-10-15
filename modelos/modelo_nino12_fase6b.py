#!/usr/bin/env python3
"""OAF-Lambayeque / Fase 6B: Niño 1+2 SST NOAA CPC (no ICEN).

Reproducible baseline / AR(1) monthly anomaly forecast, strictly expanding
training windows. No diagnosis of El Niño Costero; only experimental anomaly
of a DIFFERENT SST product (NOAA CPC OISST v2.1, not ICEN ERSSTv5).

Source https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
Usage: python modelos/modelo_nino12_fase6b.py
       python modelos/modelo_nino12_fase6b.py --self-test
Stdlib only. No values invented if source retrieval fails.
"""
import argparse
import csv
import json
import math
import random
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
OUTPUT = Path("datos")
TRAIN_MIN = 120
BACKTEST_FROM = "2010-01"
MIN_SAMPLES = 100


def month_after(month):
    y, m = map(int, month.split("-"))
    return f"{y+1 if m==12 else y:04d}-{1 if m==12 else m+1:02d}"


def parse_text(source):
    """Parse fixed whitespace NOAA CPC sstoi.indices; do NOT interpolate gaps."""
    seen, rows = set(), []
    for line in source.splitlines():
        parts = line.split()
        if len(parts) < 10 or not (parts[0].isdigit() and parts[1].isdigit()):
            continue
        year, mon = int(parts[0]), int(parts[1])
        if not 1982 <= year <= 2100 or not 1 <= mon <= 12:
            continue
        key = f"{year:04d}-{mon:02d}"
        if key in seen:
            raise ValueError("Duplicate month: " + key)
        sst, anom = float(parts[2]), float(parts[3])
        if not (math.isfinite(sst) and math.isfinite(anom)
                and 10 <= sst <= 35 and -8 <= anom <= 12):
            raise ValueError("Out-of-range NOAA Niño 1+2 values for " + key)
        seen.add(key)
        rows.append({"mes": key, "nino12_tsm_c": sst, "nino12_anom_c": anom})
    rows.sort(key=lambda r: r["mes"])
    if len(rows) < 420 or rows[0]["mes"] != "1982-01":
        raise ValueError("Historical NOAA source too short or unsupported")
    for a, b in zip(rows, rows[1:]):
        if month_after(a["mes"]) != b["mes"]:
            raise ValueError("Gap in monthly index between "+a["mes"]+" and "+b["mes"])
    return rows


def download_text():
    req = urllib.request.Request(URL, headers={"User-Agent": "OAF-Lambayeque-research/0.1 (public climate indices)"})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                raw = response.read()
            if len(raw) > 300000:
                raise ValueError("Unexpectedly large NOAA file")
            return raw.decode("ascii")
        except (OSError, UnicodeError, ValueError) as error:
            last = error
            if attempt < 2:
                time.sleep(3)
    raise RuntimeError("NOAA source unavailable: "+str(last))


def ar1(history):
    """OLS with intercept, using ONLY months known as of issue."""
    if len(history) < TRAIN_MIN:
        raise ValueError("Not enough training months")
    x, y = history[:-1], history[1:]
    mx, my = statistics.mean(x), statistics.mean(y)
    var = sum((v-mx)**2 for v in x)
    if var < 1e-12:
        return my, 0.0
    slope = sum((a-mx)*(b-my) for a, b in zip(x, y)) / var
    intercept = my - slope*mx
    return intercept, slope


def quantile(data, p):
    v = sorted(data)
    if not v:
        raise ValueError("No valid residuals")
    u = (len(v)-1)*p
    i = int(u)
    return v[i]*(1-(u-i)) + v[min(i+1,len(v)-1)]*(u-i)


def evaluate(rows):
    values = [r["nino12_anom_c"] for r in rows]
    folds = []
    for origin in range(TRAIN_MIN-1, len(values)-1):
        issue = rows[origin]["mes"]
        if issue < BACKTEST_FROM:
            continue
        a, b = ar1(values[:origin+1])
        pred_ar = a + b * values[origin]
        pred_persist = values[origin]
        target = values[origin+1]
        folds.append({
            "origen": issue, "objetivo": rows[origin+1]["mes"],
            "observado": target, "ar1": pred_ar,
            "persistencia": pred_persist, "climatologia_cero": 0.0
        })
    if len(folds) < MIN_SAMPLES:
        raise ValueError("Too few independent monthly forecast verifications")
    def measures(method):
        errors = [r[method]-r["observado"] for r in folds]
        return {
            "mae_c": round(statistics.mean(abs(e) for e in errors),4),
            "rmse_c": round(math.sqrt(statistics.mean(e*e for e in errors)),4),
            "n": len(errors)
        }
    scores = {k: measures(k) for k in ["ar1","persistencia","climatologia_cero"]}
    mae_ar=scores["ar1"]["mae_c"]
    mae_p=scores["persistencia"]["mae_c"]
    skill=1-mae_ar/mae_p if mae_p>0 else None
    recent=folds[-12:]
    def raw_mae(method, subset):
        return sum(abs(r[method]-r["observado"]) for r in subset)/len(subset)
    recent_ar=raw_mae("ar1",recent)
    recent_p=raw_mae("persistencia",recent)
    recent_skill=1-recent_ar/recent_p if recent_p>0 else None
    # Resampling of paired out-of-sample forecast errors by 12-month blocks.
    # Descriptive robustness check, NOT a calibrated probability of skill.
    rnd=random.Random(20261014)
    replicates=[]
    for _ in range(2000):
        sample=[]
        while len(sample)<len(folds):
            start=rnd.randrange(0,len(folds)-12+1)
            sample.extend(folds[start:start+12])
        sample=sample[:len(folds)]
        ar_b=raw_mae("ar1",sample)
        persist_b=raw_mae("persistencia",sample)
        if persist_b>0:
            replicates.append(1-ar_b/persist_b)
    confidence=[quantile(replicates,.025),quantile(replicates,.975)]
    consistent=bool(skill is not None and skill>0 and recent_skill is not None and recent_skill>0 and confidence[0]>0)
    a,b=ar1(values)
    latest=values[-1]
    forecast=a+b*latest
    residuals=[r["observado"]-r["ar1"] for r in folds]
    lo=forecast+quantile(residuals,.10)
    hi=forecast+quantile(residuals,.90)
    run_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "fase":"6B",
        "fuente":"NOAA CPC",
        "producto":"OISST v2.1 mensual Niño 1+2 (sstoi.indices)",
        "region":"0-10°S, 90-80°W",
        "indice_enfen_oficial":False,
        "es_icen":False,
        "es_pronostico_institucional":False,
        "estado_modelo":"EXPERIMENTAL_NO_VALIDADO_OPERATIVAMENTE",
        "fecha_procesamiento_utc":run_utc,
        "archivo_fuente":URL,
        "mes_primero":rows[0]["mes"],
        "mes_ultimo_observado":rows[-1]["mes"],
        "mes_predicho":month_after(rows[-1]["mes"]),
        "ultimo_valor_anomalia_c":round(latest,2),
        "pronostico_persistencia_c":round(latest,2),
        "pronostico_ar1_c":round(forecast,2),
        "intervalo_empirico_ar1_p10_p90_c":[round(lo,2),round(hi,2)],
        "ar1_intercepto":round(a,5),
        "ar1_pendiente":round(b,5),
        "evaluacion":{
            "procedimiento":"expanding window month-ahead retrospectivo",
            "primer_origen":folds[0]["origen"],
            "ultimo_origen":folds[-1]["origen"],
            "num_folds":len(folds),
            "metricas":scores,
            "habilidad_mae_respecto_persistencia":round(skill,4) if skill is not None else None,
            "supera_persistencia_mae":(skill is not None and skill>0),
            "reciente_12_meses":{
                "mae_ar1_c":round(recent_ar,4),
                "mae_persistencia_c":round(recent_p,4),
                "habilidad_relativa":round(recent_skill,4) if recent_skill is not None else None,
                "supera_persistencia":bool(recent_skill is not None and recent_skill>0)
            },
            "intervalo_heuristico_skill_95": [round(v,4) for v in confidence],
            "intervalo_metodo":"2000 remuestreos de bloques móviles de 12 meses, sobre errores pareados ya evaluados",
            "habilidad_consistente_demostrada":consistent,
            "advertencia":"La evaluación con una serie NOAA reprocesada y normal 1991-2020 no equivale a archivos de emisión real-time; el intervalo P10-P90 de residuos retrospectivos no garantiza cobertura futura."
        },
        "series_recientes":rows[-24:],
        "limitaciones":[
            "OISST NOAA CPC no es ICEN ENFEN, que utiliza ERSSTv5 y un índice trimestral según definición vigente.",
            "Predicción experimental de anomalía oceánica de un mes, NO predicción categórica de El Niño Costero ni de lluvias en Lambayeque.",
            "AR(1) usa solo rezagos históricos; sin variables de viento/subsuperficie ni ensambles.",
            "No usar como alerta meteorológica o fitosanitaria."
        ]
    }, folds


def write_files(rows, report, folds):
    OUTPUT.mkdir(parents=True,exist_ok=True)
    csv_path=OUTPUT/"noaa_nino12_oisst_mensual.csv"
    with csv_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["mes","nino12_tsm_c","nino12_anom_c"])
        w.writeheader()
        w.writerows(rows)
    back=OUTPUT/"nino12_backtest_walkforward.csv"
    with back.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["origen","objetivo","observado","ar1","persistencia","climatologia_cero"])
        w.writeheader()
        for fold in folds:
            w.writerow({k:round(v,4) if isinstance(v,float) else v for k,v in fold.items()})
    path=OUTPUT/"modelo_nino12_experimental.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return [str(csv_path),str(back),str(path)]


def self_test():
    rows=[]
    for year in range(1982,2027):
        for mon in range(1,13):
            value=round(0.7*math.sin(len(rows)/9)+0.1*math.cos(len(rows)/3),2)
            rows.append({"mes":f"{year:04d}-{mon:02d}","nino12_tsm_c":24.0,"nino12_anom_c":value})
    original = "YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM\n"
    original += "\n".join(f"{r['mes'][:4]} {int(r['mes'][5:])} {r['nino12_tsm_c']:.2f} {r['nino12_anom_c']:.2f} 26 0 28 0 27 0" for r in rows)
    parsed=parse_text(original)
    assert len(parsed)==540 and month_after("2026-12")=="2027-01"
    report,folds=evaluate(parsed)
    assert report["evaluacion"]["num_folds"]==203
    assert folds[0]["origen"]=="2010-01"
    assert folds[-1]["objetivo"]=="2026-12"
    assert report["mes_predicho"]=="2027-01"
    assert report["es_icen"] is False
    assert not report["es_pronostico_institucional"]
    assert "reciente_12_meses" in report["evaluacion"]
    assert len(report["evaluacion"]["intervalo_heuristico_skill_95"])==2
    try:
        parse_text(original.replace("1982 2 ", "1982 4 ", 1))
    except ValueError:
        pass
    else:
        raise AssertionError("Gaps must be rejected")
    print("Autopruebas del modelo 6B aprobadas (datos sintéticos).")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test()
        return
    source=download_text()
    rows=parse_text(source)
    now=datetime.now(timezone.utc)
    current=now.strftime("%Y-%m")
    if rows[-1]["mes"] >= current:
        raise ValueError("Latest NOAA monthly row is not yet a closed month")
    latest_year,latest_month=map(int,rows[-1]["mes"].split("-"))
    age=(now.year-latest_year)*12+now.month-latest_month
    if age>3:
        raise ValueError("Source older than 3 months; refusing outdated report")
    report,folds=evaluate(rows)
    filenames=write_files(rows,report,folds)
    print(json.dumps({"files":filenames,"last_month":rows[-1]["mes"],"forecast_month":report["mes_predicho"],"skill":report["evaluacion"]["habilidad_mae_respecto_persistencia"]},ensure_ascii=False))


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}",file=sys.stderr)
        raise SystemExit(1)
