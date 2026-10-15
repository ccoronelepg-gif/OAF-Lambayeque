#!/usr/bin/env python3
"""OAF 8C — pre-specified lagged subsurface ocean/atmosphere study.

Independent frozen training (all target months <= 2022-12) vs untouched 2023+
holdout. No future outcome leakage, including for horizons 2 or 3.
Predictors at nominal origin t: ERSSTv5 SST anomaly t, t-1; PMEL GODAS
T300 anomaly t-1; optionally NOAA CPC SOI/cpac850/epac850 at t-1.
Caution: NOAA current historical files are not vintage-as-of archives;
lagged t-1 DOES NOT guarantee real-time availability on day of issuance.
Only comparison research; not official ENFEN ICEN, ENSO warning or forecast.
"""
import argparse
import csv
import json
import math
import random
import statistics as st
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

from benchmark_atmosferico_8b import fit,predict,shift,load_target

DIR=Path("datos")
ATM_FILE=DIR/"noaa_cpc_predictores_atmosfericos_8b.csv"
T300_SOURCE="https://www.pmel.noaa.gov/tao/wwv/data/t300.dat"
HEAT_FILE=DIR/"noaa_pmel_t300_8c.csv"
RESULT=DIR/"benchmark_subsuperficial_8c.json"
SCORES=DIR/"benchmark_subsuperficial_8c_test.csv"
TRAIN_END="2022-12"
TEST_START="2023-01"
H=(1,2,3)
ALPHA=20.0
PREDICTORS=("soi_estandarizado","alisios_pacifico_central","alisios_pacifico_oriental")


def load_atmosphere(path=ATM_FILE):
    if not path.is_file():raise ValueError("Missing NOAA CPC 8B archived index CSV")
    series={x:{} for x in PREDICTORS}
    with path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {"mes",*PREDICTORS}<=set(reader.fieldnames):
            raise ValueError("Atmosphere CSV columns modified")
        for row in reader:
            ym=row["mes"]
            if ym in series[PREDICTORS[0]]:raise ValueError("Duplicate CPC month "+ym)
            for name in PREDICTORS:
                value=float(row[name])
                if not math.isfinite(value) or abs(value)>100:raise ValueError("CPC invalid magnitude")
                series[name][ym]=value
    if len(series[PREDICTORS[0]])<500:raise ValueError("Insufficient CPC month coverage")
    return series


def parse_t300(raw):
    """NOAA PMEL text 198001 0.1935662E+02 0.3304958E+00
    Date, temperature Celsius, T300 anomaly Celsius, 1981-2010 baseline.
    """
    if not all(x in raw for x in ("Depth Averaged Temps","T300","Anomaly")):
        raise ValueError("PMEL T300 source metadata missing")
    values={}
    for line in raw.splitlines():
        cells=line.split()
        if len(cells)!=3 or len(cells[0])!=6 or not cells[0].isdigit():
            continue
        y,m=int(cells[0][:4]),int(cells[0][4:])
        if not 1980<=y<=2100 or not 1<=m<=12:
            raise ValueError("Invalid date in T300 file")
        ym=f"{y:04d}-{m:02d}"
        if ym in values:raise ValueError("Duplicate T300 month "+ym)
        temp,anomaly=map(float,cells[1:])
        if (not math.isfinite(temp) or not math.isfinite(anomaly)
            or not 10<=temp<=30 or not -10<=anomaly<=10):
            raise ValueError("T300 value abnormal "+ym)
        values[ym]={"t300_c":temp,"t300_anomalia_c":anomaly}
    months=sorted(values)
    if len(months)<500 or months[0]!="1980-01":
        raise ValueError("PMEL T300 archive coverage too short")
    for x,y in zip(months,months[1:]):
        if shift(x,1)!=y:raise ValueError("Gap in NOAA PMEL T300")
    return values


def fetch():
    err=None
    for attempt in range(3):
        try:
            req=Request(T300_SOURCE,headers={"User-Agent":"OAF-Lambayeque-8C-research/1.0"})
            with urlopen(req,timeout=70) as r:raw=r.read()
            if not 8000<len(raw)<180000:raise ValueError("Unexpected T300 byte count")
            return raw.decode("ascii")
        except (OSError,ValueError) as x:
            err=x
            if attempt<2:time.sleep(3)
    raise ValueError("NOAA PMEL T300 unavailable: "+str(err))


def feature(ym,sea,atm,heat,variant):
    """Every additional predictor is from t-1, never future.
    Ocean SST t originates from monthly series subject to publication lag.
    """
    prev=shift(ym,-1)
    if ym not in sea or prev not in sea:return None
    ocean=[sea[ym],sea[prev]]
    if variant=="sst_tendencia":return ocean
    if prev not in heat:return None
    warm=heat[prev]["t300_anomalia_c"]
    if variant=="sst_tendencia_t300":return ocean+[warm]
    if variant=="sst_tendencia_t300_atmosfera":
        if any(prev not in atm[p] for p in PREDICTORS):return None
        return ocean+[warm]+[atm[p][prev] for p in PREDICTORS]
    raise ValueError("Unknown feature variant")


def metrics(rows,field):
    errors=[row[field]-row["observado_c"] for row in rows]
    if not errors:return {"n":0,"mae_c":None,"rmse_c":None,"sesgo_c":None}
    return {"n":len(errors),"mae_c":round(st.mean(abs(e) for e in errors),4),
            "rmse_c":round(math.sqrt(st.mean(e*e for e in errors)),4),
            "sesgo_c":round(st.mean(errors),4)}


def block_interval(rows,ref,trial,iterations=1200,block=6):
    """Descriptive block bootstrap over monthly origins, not significance test."""
    rng=random.Random(20261015)
    ratios=[]
    n=len(rows)
    if n<15:raise ValueError("Insufficient independent holdout months")
    for _ in range(iterations):
        selected=[]
        while len(selected)<n:
            i=rng.randrange(max(1,n-block+1))
            selected.extend(rows[i:i+block])
        selected=selected[:n]
        a=st.mean(abs(r[ref]-r["observado_c"]) for r in selected)
        b=st.mean(abs(r[trial]-r["observado_c"]) for r in selected)
        if a>0:ratios.append(1-b/a)
    ratios.sort()
    return [round(ratios[int(.025*(len(ratios)-1))],4),
            round(ratios[int(.975*(len(ratios)-1))],4)]


def evaluate(sea,atm,heat):
    variants=("sst_tendencia","sst_tendencia_t300","sst_tendencia_t300_atmosfera")
    result={};test_rows=[]
    for horizon in H:
        # Common universe for fair pairing: origin + t-1 heat/atmosphere present,
        # target known and origin is not a partial current-month.
        candidates=[month for month in sorted(sea) if
                    all(feature(month,sea,atm,heat,v) is not None for v in variants)
                    and shift(month,horizon) in sea]
        train=[month for month in candidates if
               shift(month,horizon)<=TRAIN_END]
        test=[month for month in candidates if month>=TEST_START]
        if len(train)<350 or len(test)<30:
            raise ValueError("Insufficient train/holdout: "+str((horizon,len(train),len(test))))
        trained={}
        for variant in variants:
            x=[(feature(o,sea,atm,heat,variant),sea[shift(o,horizon)]) for o in train]
            trained[variant]=fit(x,ALPHA)
        for origin in test:
            expected=sea[shift(origin,horizon)]
            row={"mes_origen":origin,"mes_objetivo":shift(origin,horizon),
                 "horizonte_meses":horizon,"observado_c":expected,
                 "persistencia_c":sea[origin],
                 "sst_tendencia_c":predict(trained["sst_tendencia"],
                       feature(origin,sea,atm,heat,"sst_tendencia")),
                 "sst_tendencia_t300_c":predict(trained["sst_tendencia_t300"],
                       feature(origin,sea,atm,heat,"sst_tendencia_t300")),
                 "sst_tendencia_t300_atmosfera_c":predict(trained["sst_tendencia_t300_atmosfera"],
                       feature(origin,sea,atm,heat,"sst_tendencia_t300_atmosfera"))
            }
            test_rows.append(row)
        rows=[r for r in test_rows if r["horizonte_meses"]==horizon]
        metrics_by={col:metrics(rows,col) for col in
                    ("persistencia_c","sst_tendencia_c",
                     "sst_tendencia_t300_c","sst_tendencia_t300_atmosfera_c")}
        base=metrics_by["sst_tendencia_c"]["mae_c"]
        heat_err=metrics_by["sst_tendencia_t300_c"]["mae_c"]
        atm_err=metrics_by["sst_tendencia_t300_atmosfera_c"]["mae_c"]
        result[str(horizon)]={
            "n_entrenamiento":len(train),"n_prueba":len(test),
            "primer_origen_prueba":test[0],"ultimo_origen_prueba":test[-1],
            "metricas":metrics_by,
            "mejora_t300_vs_tendencia":round(1-heat_err/base,4),
            "mejora_t300_y_atmosfera_vs_tendencia":round(1-atm_err/base,4),
            "intervalo_exploratorio_t300_vs_tendencia":block_interval(
                rows,"sst_tendencia_c","sst_tendencia_t300_c"),
            "intervalo_exploratorio_completo_vs_tendencia":block_interval(
                rows,"sst_tendencia_c","sst_tendencia_t300_atmosfera_c"),
            "habilidad_operativa_demostrada":False
        }
    last=min(max(sea),shift(max(heat),1),shift(max(atm[PREDICTORS[0]]),1))
    return test_rows,{
        "fase":"8C","fecha_procesamiento_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado":"evaluacion_temporal_retrospectiva_no_operativa",
        "hipotesis_predefinida":"Si la anomalía T300 y el SOI/vientos retrasados 1 mes aportan habilidad predictiva adicional al SST de origen y su tendencia",
        "base_oceanica":"NOAA NCEI ERSSTv5 Niño1+2 anomalía reconstruida por OAF a 1991-2020",
        "t300":"NOAA/PMEL GODAS anomalía temperatura media 0-300m 5N-5S 120E-80W, climatología 1981-2010",
        "fuente_t300":T300_SOURCE,
        "fuentes_atmosfericas":"NOAA CPC 850hPa y SOI de fase 8B",
        "desfase_t300_meses":1,"desfase_soi_y_vientos_meses":1,
        "corte_entrenamiento_por_mes_objetivo":TRAIN_END,
        "inicio_prueba_independiente":TEST_START,
        "fit_fijo_ridge_alpha":ALPHA,
        "sin_ajuste_con_periodo_prueba":True,
        "evaluacion_meses_1_2_3":result,
        "ultimo_mes_reanalisis_t300":max(heat),
        "ultimo_mes_oceanico":max(sea),
        "ultimo_origen_con_predictores_retrasados":last,
        "se_ha_emitido_pronostico_prospectivo_8c":False,
        "es_icen_oficial":False,"es_alerta_enfen":False,
        "prediccion_elnino_costero_validada":False,
        "cautelas":[
            "PMEL T300 mide temperatura media de los primeros 300 m del Pacífico ecuatorial, NO calor de superficie en las costas de Perú.",
            "El T300 de GODAS usa base 1981-2010, mientras que la anomalía SST objetivo fue reconstruida a base 1991-2020; NO restar ambos índices.",
            "Los archivos históricos públicos pueden ser revisados y no guardan vintage de fecha real de emisión; separar holdout temporal no elimina este sesgo.",
            "Desfasar 1 mes no garantiza que el dato T300 estuviera publicado en una fecha histórica concreta; fase 8A sigue siendo la línea de verificación de emisiones genuinas.",
            "No se demostró causalidad ni predicción operativa de lluvia, enfermedades o impacto de El Niño Costero en Lambayeque.",
            "Ningún pronóstico previo congelado se reemplaza por proyecciones calculadas con datos retrospectivos actuales.",
            "Tres comparaciones exploratorias preespecificadas; no seleccionar una variante por el mejor resultado sin replicación prospectiva."
        ]
    }


def save(heat,rows,report):
    DIR.mkdir(exist_ok=True)
    with HEAT_FILE.open("w",encoding="utf-8",newline="") as f:
        names=["mes","t300_c","t300_anomalia_c"]
        w=csv.DictWriter(f,fieldnames=names);w.writeheader()
        for date in sorted(heat):w.writerow({"mes":date,**heat[date]})
    RESULT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with SCORES.open("w",encoding="utf-8",newline="") as f:
        fields=["mes_origen","mes_objetivo","horizonte_meses","observado_c",
                "persistencia_c","sst_tendencia_c",
                "sst_tendencia_t300_c","sst_tendencia_t300_atmosfera_c"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def self_test():
    rows=["Depth Averaged Temps (0/300m,deg C,5N-5S,120E-80W)",
          "GTMBA Project Office/NOAA/PMEL/Seattle", "date       T300        Anomaly"]
    d=datetime(1980,1,1)
    for i in range(564):
        yy=1980+i//12;mm=i%12+1
        rows.append(f"{yy:04d}{mm:02d} 0.1935662E+02 0.3304958E+00")
    parsed=parse_t300("\n".join(rows))
    assert len(parsed)==564 and abs(parsed["1980-01"]["t300_anomalia_c"]-.3304958)<1e-7
    assert shift("2026-01",-1)=="2025-12"
    sea={"2026-02":1.1,"2026-01":1.0}
    atm={p:{"2026-01":0.1} for p in PREDICTORS}
    heat={"2026-01":{"t300_anomalia_c":0.5}}
    assert feature("2026-02",sea,atm,heat,"sst_tendencia_t300_atmosfera")==[1.1,1.0,.5,.1,.1,.1]
    assert feature("2026-02",sea,atm,{},"sst_tendencia_t300") is None
    demo=[{"observado_c":1.0,"sst_tendencia_c":1.1,"sst_tendencia_t300_c":1.05} for i in range(20)]
    assert block_interval(demo,"sst_tendencia_c","sst_tendencia_t300_c")[0]>0
    print("8C PASS: T300 scientific notation, calendar lag, no missing-value fabrication, paired bootstrap")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:self_test();return
    sea=load_target()
    atm=load_atmosphere()
    heat=parse_t300(fetch())
    rows,report=evaluate(sea,atm,heat)
    save(heat,rows,report)
    for h,r in report["evaluacion_meses_1_2_3"].items():
        print("8C horizon",h,"n train",r["n_entrenamiento"],"n test",r["n_prueba"],
              "MAE",r["metricas"],"heat gain",r["mejora_t300_vs_tendencia"],flush=True)
    print("8C evaluation completed - NOT operational Niño Costero forecasts")


if __name__=="__main__":
    try:main()
    except Exception as e:
        print("OAF 8C FAILURE:",e,file=sys.stderr)
        raise SystemExit(1)
