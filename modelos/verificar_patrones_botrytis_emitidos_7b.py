#!/usr/bin/env python3
"""Fase7B: verify genuine OAF-archived hourly atmospheric RH forecasts once mature.

The archived forecast emission is NEVER overwritten. Wait at least 7 calendar
days after forecast valid date before downloading ERA5 hourly RH at 2 m.
Outputs ONLY an atmospheric-indicator comparison, never Botrytis infection.
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request,urlopen

INPUT=Path("datos/patrones_botrytis_emitidos")
OUT=Path("datos/botrytis_humedad_7b_prospectivo.json")
CSV=Path("datos/botrytis_humedad_7b_prospectivo.csv")
LAG_DAYS=7
SITES=["Motupe","Jayanca","Olmos","Chiclayo"]

def full_daily_labels(values):
    """Map all complete 24-hour calendar days to RH-episode labels.
    Day is positive if 6th or any later continuous qualifying hour falls on it.
    """
    if len(values)!=168:
        raise ValueError("Expected 168 continuous forecast-hour entries")
    flags={}
    streak=0
    for i,entry in enumerate(values):
        day=entry["fecha"]
        hour=entry["hora"]
        if hour!=i%24 or day!=values[(i//24)*24]["fecha"]:
            raise ValueError("Invalid archive hourly alignment")
        rh=entry["relative_humidity_2m"]
        if not isinstance(rh,(int,float)) or not math.isfinite(rh) or not 0<=rh<=100:
            raise ValueError("Invalid archived atmospheric humidity")
        if day not in flags:flags[day]=False
        streak=streak+1 if rh>90 else 0
        if streak>=6:flags[day]=True
    if len(flags)!=7:raise ValueError("Seven future dates are required")
    expected=list(flags)
    for i,d in enumerate(expected):
        if date.fromisoformat(d)!=date.fromisoformat(expected[0])+timedelta(days=i):
            raise ValueError("Archive dates are not consecutive")
    return flags

def scan(today):
    items=[];total=0;first=None
    if not INPUT.exists():
        return items,total,first
    for f in sorted(INPUT.glob("????-??-??.json")):
        record=json.loads(f.read_text(encoding="utf-8"))
        issue=date.fromisoformat(record["fecha_emision_local"])
        if issue.isoformat()!=f.stem or record.get("fase")!="7A" or record.get("es_alerta") is not False or record.get("es_diagnostico") is not False:
            raise ValueError("Invalid archival provenance: "+str(f))
        emission=datetime.fromisoformat(record["emision_utc"].replace("Z","+00:00"))
        if emission.tzinfo is None:raise ValueError("Unsigned emission timestamp timezone")
        for site in SITES:
            locality=record.get("localidades",{}).get(site)
            if not isinstance(locality,dict):raise ValueError("Missing archival locality "+site)
            rows=locality.get("evaluacion",{}).get("variables_crudas_horarias",[])
            flags=full_daily_labels(rows)
            for horizon,(day,label) in enumerate(flags.items(),start=1):
                if date.fromisoformat(day)!=issue+timedelta(days=horizon):
                    raise ValueError("Archive future date differs from issue date")
                start=datetime.combine(date.fromisoformat(day),datetime.min.time(),ZoneInfo("America/Lima"))
                if emission>=start.astimezone(timezone.utc):
                    raise ValueError("Forecast was not archived before predicted day")
                total+=1
                dt=date.fromisoformat(day)
                if first is None or dt<first:first=dt
                if today-dt>=timedelta(days=LAG_DAYS):
                    items.append({"emision_utc":record["emision_utc"],
                                  "fecha_emision":issue.isoformat(),
                                  "localidad":site,"fecha_valida":day,
                                  "horizonte_dias":horizon,
                                  "episodio_pronosticado":bool(label)})
    return items,total,first

def fetch_era5(city,start,end):
    # Requested locations match OAF site reference points, not plot sensors.
    loc={"Motupe":(-6.15083,-79.7142),"Jayanca":(-6.39278,-79.8228),
         "Olmos":(-5.98825,-79.74723),"Chiclayo":(-6.7714,-79.8409)}
    lat,lon=loc[city]
    url="https://archive-api.open-meteo.com/v1/archive?"+urlencode({
      "latitude":lat,"longitude":lon,"timezone":"America/Lima",
      "start_date":start,"end_date":end,"hourly":"relative_humidity_2m","models":"era5"})
    with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-field-independent-reanalysis-7B/1.0"}),timeout=85) as resp:
        payload=json.load(resp)
    if payload.get("error") or payload.get("hourly_units",{}).get("relative_humidity_2m")!="%":
        raise ValueError("Unavailable ERA5 RH in percent")
    h=payload["hourly"]
    d=h.get("time",[]);v=h.get("relative_humidity_2m",[])
    if len(d)!=len(v) or len(d)!=len(set(d)):raise ValueError("ERA5 hourly data invalid")
    out=defaultdict(dict)
    for stamp,value in zip(d,v):
        if not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=100:
            continue
        out[stamp[:10]][int(stamp[11:13])]=value
    return out

def score(eligible,reanalysis):
    """Rebuild reference episode by issue to retain continuity across midnight."""
    groups=defaultdict(list)
    for item in eligible:
        groups[(item["emision_utc"],item["localidad"])].append(item)
    output=[];missing=0
    for (emission,site),items in groups.items():
        items.sort(key=lambda x:x["fecha_valida"])
        series=reanalysis.get(site,{})
        streak=0
        labels={}
        for item in items:
            day=item["fecha_valida"]
            data=series.get(day,{})
            if len(data)!=24 or any(h not in data for h in range(24)):
                missing+=1;streak=0
                continue
            flag=False
            for h in range(24):
                streak=streak+1 if data[h]>90 else 0
                if streak>=6:flag=True
            labels[day]=flag
            output.append({**item,"episodio_era5":bool(flag),
                           "acierto":item["episodio_pronosticado"]==flag})
    return output,missing

def metrics(rows):
    out=[]
    for site in SITES:
        sub=[r for r in rows if r["localidad"]==site]
        tp=sum(r["episodio_pronosticado"] and r["episodio_era5"] for r in sub)
        fp=sum(r["episodio_pronosticado"] and not r["episodio_era5"] for r in sub)
        fn=sum(not r["episodio_pronosticado"] and r["episodio_era5"] for r in sub)
        tn=len(sub)-tp-fp-fn
        div=lambda a,b:round(a/b,4) if b>0 else None
        out.append({"localidad":site,"n_jornadas":len(sub),
                    "verdaderos_positivos":tp,"falsos_positivos":fp,
                    "falsos_negativos":fn,"verdaderos_negativos":tn,
                    "sensibilidad":div(tp,tp+fn),"precision_positiva":div(tp,tp+fp),
                    "validacion_biologica":False})
    return out

def self_test():
    src=[]
    for i in range(168):
        d=date(2026,10,16)+timedelta(days=i//24)
        rh=95 if i in range(20,28) else 55
        src.append({"fecha":d.isoformat(),"hora":i%24,"relative_humidity_2m":rh})
    data=full_daily_labels(src)
    assert not data["2026-10-16"] and data["2026-10-17"]
    assert sum(data.values())==1
    assert date(2026,10,16)+timedelta(days=7)==date(2026,10,23)
    pending,missing=score([],{})
    assert pending==[] and missing==0
    print("7B prospective test: crossing midnight, date, no data => no invented verification PASSED")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test();return
    now=datetime.now(timezone.utc)
    today=now.astimezone(ZoneInfo("America/Lima")).date()
    eligible,total,first=scan(today)
    ref={}
    if eligible:
        for site in SITES:
            dates=[x["fecha_valida"] for x in eligible if x["localidad"]==site]
            if dates:ref[site]=fetch_era5(site,min(dates),max(dates))
    scored,missing=score(eligible,ref)
    report={
        "fase":"7B_prospectivo",
        "fecha_generacion_utc":now.isoformat(timespec="seconds"),
        "estado":"verificacion_meteorologica" if scored else "pendiente_reanalisis",
        "prediccion_emfermedad":False,
        "hay_validacion_biologica":False,
        "referencia":"ERA5 humedad a 2 m, no medición de humectación ni parcela",
        "umbral":"HR >90 % >=6 horas continuas; comparado como señal atmosférica",
        "demora_minima_dias":LAG_DAYS,
        "primer_dia_predicho":first.isoformat() if first else None,
        "primer_dia_elegible":(first+timedelta(days=LAG_DAYS)).isoformat() if first else None,
        "jornadas_archivadas":total,
        "jornadas_elegibles":len(eligible),
        "jornadas_verificadas":len(scored),
        "jornadas_referencia_incompleta":missing,
        "metricas":metrics(scored),
        "advertencia":"Se evalúa humedad del aire modelada, NO presencia de Botrytis ni humectación foliar real"
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with CSV.open("w",encoding="utf-8",newline="") as f:
        columns=["emision_utc","fecha_emision","localidad","fecha_valida",
                 "horizonte_dias","episodio_pronosticado","episodio_era5","acierto"]
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader();w.writerows(scored)
    print(json.dumps({k:report[k] for k in ("estado","jornadas_archivadas","jornadas_elegibles","jornadas_verificadas")},ensure_ascii=False))

if __name__=="__main__":
    try:main()
    except Exception as err:
        print("OAF 7B PROSPECTIVE ERROR:",err,file=sys.stderr)
        raise SystemExit(1)
