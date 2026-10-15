#!/usr/bin/env python3
"""Fase 6F OAF: comparar pronóstico original, corrección básica y corrección
con radiación solar, humedad relativa y viento. Todos los predictores proceden
del archivo previous_day1 (emitidos 24 h antes de su hora válida).
Objetivo: ERA5-Land temperatura 2m REANALIZADA, no estación SENAMHI.
Entrenamiento: 2024–2025; evaluación aislada: enero–septiembre de 2026.
No es modelo de enfermedad, Niño Costero ni alerta operativa.
"""
import argparse
import csv
import json
import math
import random
import statistics as st
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode

SITES={"Chiclayo":(-6.77140,-79.84090),"Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),"Olmos":(-5.98825,-79.74723)}
FIELDS=["temperature_2m_previous_day1","relative_humidity_2m_previous_day1",
        "shortwave_radiation_previous_day1","wind_speed_10m_previous_day1"]
END="2026-09-30"
ALPHA=20.0

def get(host,args):
    url=host+"?"+urlencode(args)
    error=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"OAF-Lambayeque-academic-6F/1.0"})
            with urllib.request.urlopen(req,timeout=90) as response:data=json.load(response)
            if data.get("error"):raise ValueError(data.get("reason") or "API error")
            return data
        except (OSError,ValueError) as err:
            error=err
            if attempt<2:time.sleep(3)
    raise RuntimeError("Data source unavailable: "+str(error))

def obtain(site):
    lat,lon=SITES[site]
    common={"latitude":lat,"longitude":lon,"start_date":"2024-01-01",
            "end_date":END,"timezone":"America/Lima"}
    f=get("https://previous-runs-api.open-meteo.com/v1/forecast",
          {**common,"hourly":",".join(FIELDS)})
    r=get("https://archive-api.open-meteo.com/v1/archive",
          {**common,"hourly":"temperature_2m","models":"era5_land"})
    hf,hr=f["hourly"],r["hourly"]
    stamps=hf["time"]
    if len(stamps)<18000 or len(set(stamps))!=len(stamps):
        raise ValueError("Historical previous forecast timestamps invalid")
    if len(hr["time"])!=len(set(hr["time"])):raise ValueError("Duplicate reanalysis timestamps")
    if any(not isinstance(hf.get(key),list) or len(hf[key])!=len(stamps) for key in FIELDS):
        raise ValueError("Predictors unavailable or incomplete")
    observations=dict(zip(hr["time"],hr["temperature_2m"]))
    rows=[]
    for i,stamp in enumerate(stamps):
        v=[hf[k][i] for k in FIELDS]
        y=observations.get(stamp)
        if not isinstance(y,(float,int)) or not math.isfinite(y):continue
        if any(not isinstance(x,(float,int)) or not math.isfinite(x) for x in v):continue
        t,rh,rad,wind=v
        if not (-15<=y<=50 and -15<=t<=50 and 0<=rh<=100 and 0<=rad<=1400 and 0<=wind<=180):continue
        day,hour=stamp[:10],int(stamp[11:13])
        d=date.fromisoformat(day)
        doy=d.timetuple().tm_yday
        seasonal=[math.sin(2*math.pi*hour/24),math.cos(2*math.pi*hour/24),
                  math.sin(2*math.pi*doy/365.25),math.cos(2*math.pi*doy/365.25)]
        base=[t]+seasonal
        rows.append({"day":day,"target":float(y),"raw":float(t),
                     "base":base,"plus":base+[rad,rh,wind]})
    train=[x for x in rows if x["day"]<"2026-01-01"]
    test=[x for x in rows if "2026-01-01"<=x["day"]<=END]
    if len(train)<8000 or len(test)<3000:
        raise ValueError(f"Insufficient hourly coverage for {site}: {len(train)} training, {len(test)} test")
    meta={"forecast_cell":[f.get("latitude"),f.get("longitude")],
          "reanalysis_cell":[r.get("latitude"),r.get("longitude")],
          "hours_input":len(stamps),"hours_training":len(train),"hours_holdout":len(test)}
    return train,test,meta

def solve(a,b):
    n=len(b);m=[list(row)+[b[i]] for i,row in enumerate(a)]
    for c in range(n):
        pivot=max(range(c,n),key=lambda i:abs(m[i][c]))
        if abs(m[pivot][c])<1e-10:raise ValueError("Singular design")
        m[c],m[pivot]=m[pivot],m[c]
        factor=m[c][c]
        for k in range(c,n+1):m[c][k]/=factor
        for i in range(n):
            if i==c:continue
            v=m[i][c]
            for k in range(c,n+1):m[i][k]-=v*m[c][k]
    return [m[i][n] for i in range(n)]

def fit(rows,field):
    n=len(rows[0][field])
    columns=[[r[field][j] for r in rows] for j in range(n)]
    centers=[st.mean(col) for col in columns]
    scales=[max(st.pstdev(col),1e-8) for col in columns]
    a=[[0.0]*(n+1) for _ in range(n+1)];b=[0.0]*(n+1)
    for row in rows:
        values=[1.0]+[(v-centers[i])/scales[i] for i,v in enumerate(row[field])]
        for i in range(n+1):
            b[i]+=values[i]*row["target"]
            for j in range(i,n+1):a[i][j]+=values[i]*values[j]
    for i in range(n+1):
        for j in range(i):a[i][j]=a[j][i]
        if i:a[i][i]+=ALPHA
    return (field,centers,scales,solve(a,b))

def predict(model,row):
    field,centers,scales,coef=model
    x=[1.0]+[(v-centers[i])/scales[i] for i,v in enumerate(row[field])]
    return sum(u*v for u,v in zip(x,coef))

def mae(data,kind):
    return st.mean(abs(r[kind]-r["target"]) for r in data)

def describe(data,kind):
    errors=[r[kind]-r["target"] for r in data]
    return {"n":len(errors),"mae_c":round(st.mean(abs(e) for e in errors),4),
            "rmse_c":round(math.sqrt(st.mean(e*e for e in errors)),4),
            "sesgo_c":round(st.mean(errors),4)}

def bootstrap(rows):
    dates=sorted(set(r["day"] for r in rows))
    bydate=defaultdict(list)
    for r in rows:bydate[r["day"]].append(r)
    rng=random.Random(20261014);values=[]
    for _ in range(600):
        subset=[]
        count=0
        while count<len(dates):
            start=rng.randrange(max(1,len(dates)-14+1))
            block=dates[start:start+14]
            subset.extend(x for d in block for x in bydate[d])
            count+=len(block)
        b=mae(subset,"corrected_base")
        if b>0:values.append(1-mae(subset,"corrected_plus")/b)
    values.sort()
    if len(values)<400:raise ValueError("Not enough bootstrap evaluations")
    return [round(values[int(.025*(len(values)-1))],4),round(values[int(.975*(len(values)-1))],4)]

def evaluate(train,test):
    mbase=fit(train,"base");mplus=fit(train,"plus")
    scored=[]
    for row in test:
        scored.append({"day":row["day"],"target":row["target"],
                       "raw":row["raw"],"corrected_base":predict(mbase,row),
                       "corrected_plus":predict(mplus,row)})
    scores={k:describe(scored,k) for k in ("raw","corrected_base","corrected_plus")}
    improvement=1-mae(scored,"corrected_plus")/mae(scored,"corrected_base")
    interval=bootstrap(scored)
    months=[]
    for period in sorted(set(x["day"][:7] for x in scored)):
        subset=[r for r in scored if r["day"].startswith(period)]
        months.append({"mes":period,"horas":len(subset),
                       "mae_pronostico_original_c":round(mae(subset,"raw"),4),
                       "mae_modelo_basico_c":round(mae(subset,"corrected_base"),4),
                       "mae_modelo_ampliado_c":round(mae(subset,"corrected_plus"),4)})
    return {"metricas":scores,"mejora_relativa_vs_basico":round(improvement,4),
            "intervalo_exploratorio_95":interval,
            "mejora_retrospectiva_consistente":improvement>0 and interval[0]>0,
            "validacion_operativa":False},months

def self_test():
    assert [round(v,5) for v in solve([[3,1],[1,2]],[5,5])]==[1,2]
    data=[]
    for i in range(300):
        temp=20+5*math.sin(i/11);hour=i%24
        rad=max(0.0,300*math.sin(2*math.pi*hour/24))
        hum=60+10*math.sin(i/7);wind=10+3*math.cos(i/9)
        baseline=[temp,math.sin(hour),math.cos(hour),math.sin(i/30),math.cos(i/30)]
        data.append({"day":f"2026-01-{i//24+1:02d}","target":temp+.015*rad+.05*hum-.03*wind,
                     "raw":temp,"base":baseline,"plus":baseline+[rad,hum,wind]})
    trained=fit(data[:180],"plus")
    assert len(trained[3])==9
    predicted=[abs(predict(trained,r)-r["target"]) for r in data[180:]]
    assert all(math.isfinite(v) for v in predicted)
    print("6F self test passed (synthetic only).")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test();return
    result={};table=[]
    for site in SITES:
        train,test,meta=obtain(site)
        outcome,months=evaluate(train,test)
        result[site]={**outcome,"celdas_y_cobertura":meta}
        table.extend({"localidad":site,**month} for month in months)
        print("RESULT",site,"train",len(train),"holdout",len(test),
              "MAE",outcome["metricas"],"improvement",outcome["mejora_relativa_vs_basico"],flush=True)
    output={"fase":"6F","fecha_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pregunta":"¿Radiación, humedad y viento pronosticados mejoran la corrección de temperatura a 24h?",
            "objetivo":"Temperatura del aire a 2m REANALIZADA por ERA5-Land, NO estación SENAMHI",
            "fuente_predictores":"Open-Meteo Previous Runs API",
            "fuente_referencia":"Open-Meteo Historical Weather ERA5-Land",
            "entrenamiento":"2024-01-01 a 2025-12-31",
            "evaluacion_separada":"2026-01-01 a 2026-09-30",
            "predictores_emitidos_antes_de_validez":True,
            "pronostico_original":"temperature_2m_previous_day1",
            "modelo_base":"Ridge fijo alpha=20, temperatura archivada más factores de hora y estacionalidad",
            "modelo_ampliado":"Mismo modelo con radiación solar, humedad relativa y viento archivados previous_day1",
            "sin_optimizacion_en_holdout":True,"estado":"experimental_retrospectivo",
            "resultados":result,
            "limitaciones":[
                "Se evalúa contra un REANÁLISIS ERA5-Land, no una estación instrumental independiente.",
                "Los campos previous_day1 se refieren a un desplazamiento de 24 h respecto a la hora válida.",
                "Una mejora de MAE retrospectiva no demuestra precisión en un despliegue futuro.",
                "No pronostica El Niño Costero ni probabilidades de enfermedades en arándano o vid.",
                "Archivos de modelos pueden ser revisados; faltan capturas prospectivas selladas y evaluación local de campo."
            ]}
    Path("datos").mkdir(exist_ok=True)
    Path("datos/benchmark_variables_6f.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with open("datos/benchmark_variables_6f_mes.csv","w",encoding="utf-8",newline="") as f:
        fields=["localidad","mes","horas","mae_pronostico_original_c","mae_modelo_basico_c","mae_modelo_ampliado_c"]
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(table)
    print("6F benchmark finished and saved.")

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("OAF 6F FAILED: "+str(exc),file=sys.stderr)
        sys.exit(1)
