#!/usr/bin/env python3
"""OAF-Lambayeque Fase 7B — validation of the METEOROLOGICAL proxy only.

Tests whether RH >90% for >=6 continuous hours predicted at nominal 24-hour
lead time by Open-Meteo Previous Runs agrees with subsequent ERA5 reanalysis.

Days scored with same 7A core convention: an episode is marked for the day in
which its sixth hour is reached (or hours beyond sixth continue). A run can
span local midnight. Do NOT interpret as blueberry Botrytis infection, leaf
wetness, or field-validation. No threshold tuned using holdout results.
"""
import argparse
import csv
import json
import math
import statistics as st
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

COORDS={"Chiclayo":(-6.77140,-79.84090),"Jayanca":(-6.39278,-79.82280),
        "Motupe":(-6.15083,-79.71420),"Olmos":(-5.98825,-79.74723)}
START="2026-01-01"
END="2026-09-30"
THRESHOLD=90.0
MIN_HOURS=6
OUT=Path("datos")


def fetch(endpoint,params):
    url=endpoint+"?"+urlencode(params)
    error=None
    for retry in range(3):
        try:
            req=Request(url,headers={"User-Agent":"OAF-Lambayeque-research-7B/1.0"})
            with urlopen(req,timeout=90) as response:
                data=json.load(response)
            if data.get("error") or not isinstance(data.get("hourly"),dict):
                raise ValueError(data.get("reason","Missing hourly data"))
            return data
        except (OSError,ValueError) as exc:
            error=exc
            if retry<2:time.sleep(3)
    raise RuntimeError("API read unavailable: "+str(error))


def obtain(city,start,end):
    lat,lon=COORDS[city]
    common={"latitude":lat,"longitude":lon,
            "start_date":start,"end_date":end,"timezone":"America/Lima"}
    predicted=fetch("https://previous-runs-api.open-meteo.com/v1/forecast",{
        **common,"hourly":"relative_humidity_2m_previous_day1"})
    reference=fetch("https://archive-api.open-meteo.com/v1/archive",{
        **common,"hourly":"relative_humidity_2m","models":"era5"})
    # Both sources supply RH at 2m, not leaf wetness.
    pu=predicted.get("hourly_units",{}).get("relative_humidity_2m_previous_day1")
    ru=reference.get("hourly_units",{}).get("relative_humidity_2m")
    if pu!="%" or ru!="%":
        raise ValueError("Unexpected RH units: "+str((pu,ru)))
    stamps=predicted["hourly"].get("time",[])
    vals=predicted["hourly"].get("relative_humidity_2m_previous_day1",[])
    rdates=reference["hourly"].get("time",[])
    rvals=reference["hourly"].get("relative_humidity_2m",[])
    if len(stamps)!=len(vals) or len(rdates)!=len(rvals):
        raise ValueError("Time/value lengths differ")
    if len(set(stamps))!=len(stamps) or len(set(rdates))!=len(rdates):
        raise ValueError("Duplicate forecast/reference stamps")
    if len(stamps)<180*24 or len(rdates)<180*24:
        raise ValueError("Insufficient retrospective length")
    hist=dict(zip(rdates,rvals))
    aligned={}
    for timekey,value in zip(stamps,vals):
        actual=hist.get(timekey)
        if isinstance(timekey,str) and isinstance(value,(float,int)) and isinstance(actual,(float,int)):
            if math.isfinite(value) and math.isfinite(actual) and 0<=value<=100 and 0<=actual<=100:
                aligned[timekey]=(float(value),float(actual))
    return aligned,{"horas_pronosticadas":len(stamps),"horas_reanalisis":len(rdates),
                     "horas_alineadas_validas":len(aligned),
                     "celda_pronostico":[predicted.get("latitude"),predicted.get("longitude")],
                     "celda_reanalisis":[reference.get("latitude"),reference.get("longitude")]}


def labels(series,field):
    """Return per-day label for episode hour >=6, allowing midnight crossing.

    Missing timestamps break the run and the day is excluded from metrics.
    Calendar day label is True if hour 6 or later in a run lands on that day.
    """
    ordered=sorted(series)
    flags=defaultdict(bool)
    coverage=defaultdict(int)
    seq=0;prev=None;eps=0
    for stamp in ordered:
        if len(stamp)!=16 or stamp[10]!="T" or stamp[-3:]!=":00":
            raise ValueError("Bad hourly timestamp "+str(stamp))
        dt=datetime.strptime(stamp,"%Y-%m-%dT%H:%M")
        day=stamp[:10]
        if prev is None or dt-prev!=timedelta(hours=1):
            seq=0
        prev=dt
        coverage[day]+=1
        x=series[stamp][field]
        if x>THRESHOLD:
            seq+=1
            if seq>=MIN_HOURS:
                flags[day]=True
                if seq==MIN_HOURS:eps+=1
        else:
            seq=0
    return {day:bool(flags[day]) for day,n in coverage.items() if n==24},eps


def evaluate(aligned,city):
    forecast,foreps=labels(aligned,0)
    actual,actualeps=labels(aligned,1)
    dates=sorted(set(forecast)&set(actual))
    if len(dates)<180:raise ValueError("Fewer than 180 complete evaluable days: "+city)
    days=[]
    for day in dates:
        days.append({"localidad":city,"fecha":day,
                     "episodio_pronosticado":int(forecast[day]),
                     "episodio_reanalisis":int(actual[day]),
                     "acuerdo":int(forecast[day]==actual[day])})
    tp=sum(x["episodio_pronosticado"] and x["episodio_reanalisis"] for x in days)
    fp=sum(x["episodio_pronosticado"] and not x["episodio_reanalisis"] for x in days)
    fn=sum(not x["episodio_pronosticado"] and x["episodio_reanalisis"] for x in days)
    tn=sum(not x["episodio_pronosticado"] and not x["episodio_reanalisis"] for x in days)
    assert tp+fp+fn+tn==len(days)
    # Ratios are null when the denominator is zero, never coerced to 100%.
    def divide(num,den):return round(num/den,4) if den else None
    sensitivity=divide(tp,tp+fn)
    specificity=divide(tn,tn+fp)
    precision=divide(tp,tp+fp)
    balanced=round((sensitivity+specificity)/2,4) if sensitivity is not None and specificity is not None else None
    report={
        "dias_evaluados":len(days),
        "episodios_diarios_previstos":tp+fp,
        "episodios_diarios_referencia":tp+fn,
        "matriz":{"verdaderos_positivos":tp,"falsos_positivos":fp,
                  "falsos_negativos":fn,"verdaderos_negativos":tn},
        "sensibilidad":sensitivity,"especificidad":specificity,
        "precision_positiva":precision,
        "exactitud_global":divide(tp+tn,len(days)),
        "exactitud_balanceada":balanced,
        "episodios_secuencia_previstos":foreps,
        "episodios_secuencia_reanalisis":actualeps,
        "aplica_a":"episodio atmosférico HR 2 m >90% por >=6 h; NO infección ni humectación de hoja",
        "validacion_biologica":False}
    return days,report


def self_test():
    def dates(start,n):
        base=datetime.strptime(start,"%Y-%m-%dT%H:%M")
        return [(base+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(n)]
    # Three days; episode crosses midnight. Include false positive in final day.
    stamps=dates("2026-01-01T00:00",72)
    values={}
    for i,x in enumerate(stamps):
        pred=95.0 if (i in range(23,30) or i in range(48,54)) else 60.
        obs=95.0 if i in range(23,30) else 60.
        values[x]=(pred,obs)
    pred,_=labels(values,0)
    truth,_=labels(values,1)
    assert len(pred)==3 and len(truth)==3
    assert pred["2026-01-02"] and truth["2026-01-02"]
    assert pred["2026-01-03"] and not truth["2026-01-03"]
    assert not pred["2026-01-01"]
    # Missing hour makes one day unevaluable, and breaks continuity.
    del values["2026-01-02T04:00"]
    pred,_=labels(values,0)
    assert "2026-01-02" not in pred
    print("7B tests: midnight, false alarms, missing-hour exclusion PASSED")


def run():
    result={}
    daily=[]
    for city in COORDS:
        aligned,meta=obtain(city,START,END)
        records,summary=evaluate(aligned,city)
        summary["control_fechas_y_celdas"]=meta
        result[city]=summary
        daily.extend(records)
        print(city,"days",summary["dias_evaluados"],"matrix",summary["matriz"],flush=True)
    out={
       "fase":"7B",
       "fecha_procesamiento_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "estado":"retrospectivo_meteorologico_no_validado_con_campo",
       "primer_dia":START,"ultimo_dia":END,
       "fuente_pronostico":"Open-Meteo Previous Model Runs API, relative_humidity_2m_previous_day1",
       "fuente_verificacion":"Open-Meteo Historical Weather API, ERA5 hourly relative_humidity_2m",
       "condicion":"RH >90% por >=6 horas continuas; cuenta día cuando se alcanza sexta hora o persiste episodio",
       "horizonte":"un día nominal previo a cada hora válida",
       "es_prediccion_de_botrytis":False,
       "es_verificacion_humectacion_foliar":False,
       "es_alerta":False,
       "son_registros_de_campo":False,
       "resultados":result,
       "limitaciones":[
          "Reanálisis ERA5 RH a 2m no es medición SENAMHI ni sensor en dosel.",
          "Se evalúa una señal de humedad, NO enfermedad, infección ni incidencia de Botrytis.",
          "La emisión Previous Runs es de horizonte nominal 24h, NO archivo inmutable del OAF.",
          "Umbral descriptivo externo no calibrado para arándano en Lambayeque.",
          "Evaluación retrospectiva de un único periodo 2026; faltan replicaciones independientes.",
          "Nunca inferir fungicidas, probabilidad de infección ni estado oficial ENSO."
       ]
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"botrytis_indicador_7b_backtest.json").write_text(
        json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"botrytis_indicador_7b_diario.csv").open("w",encoding="utf-8",newline="") as file:
        keys=["localidad","fecha","episodio_pronosticado","episodio_reanalisis","acuerdo"]
        writer=csv.DictWriter(file,fieldnames=keys)
        writer.writeheader();writer.writerows(daily)
    print("7B finished: retrospective METEOROLOGICAL proxy, no disease status")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    try:
        if args.self_test:self_test()
        else:run()
    except Exception as exc:
        print("OAF 7B validation failed:",exc,file=sys.stderr)
        raise SystemExit(1)
