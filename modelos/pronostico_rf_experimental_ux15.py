#!/usr/bin/env python3
"""OAF / RF experimental: daily 7-day and monthly 6-month candidates.

Never operational alerts, NOT as-issued validation. ERA5 via Open-Meteo is a
reanalysis (not a station observation). Test is retrospective one-step, not
the same as multi-step forecast skill. Future steps are autoregressive.
All dates and source vintages are retained; fail closed on bad inputs.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, io, json, math, os, pathlib
from collections import defaultdict
from urllib.parse import urlencode
import numpy as np
import requests
from sklearn.ensemble import RandomForestRegressor

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"datos"/"rf_experimental_ux15.json"
ERA5="https://archive-api.open-meteo.com/v1/archive"
PLACES={"Chiclayo":(-6.7714,-79.8409),"Jayanca":(-6.39278,-79.8228),
        "Motupe":(-6.15083,-79.7142),"Olmos":(-5.98825,-79.74723)}
RAIN="precipitation_sum"
TEMP="temperature_2m_max"
TMEAN="temperature_2m_mean"
TODAY=dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).date()

def source(city):
    lat,lon=PLACES[city]
    # ERA5 can lag 5 days; only completed days are ingested.
    latest=TODAY-dt.timedelta(days=7)
    params={"latitude":lat,"longitude":lon,"start_date":"2021-01-01",
            "end_date":latest.isoformat(),"daily":f"{RAIN},{TEMP},{TMEAN}",
            "timezone":"America/Lima","models":"era5"}
    url=ERA5+"?"+urlencode(params)
    response=requests.get(url,timeout=(15,100),headers={"User-Agent":"OAF-Lambayeque/2.0 research"})
    response.raise_for_status()
    payload=response.json().get("daily",{})
    dates=payload.get("time",[]);rain=payload.get(RAIN,[]);temp=payload.get(TEMP,[]);means=payload.get(TMEAN,[])
    if len(dates)<1700 or len(dates)!=len(rain) or len(dates)!=len(temp) or len(dates)!=len(means):
        raise ValueError("Archivo ERA5 incompleto para "+city)
    rows={}
    for key,p,t,mean in zip(dates,rain,temp,means):
        if p is None or t is None or mean is None or not(0<=float(p)<=1200) or not(-5<=float(t)<=55) or not(-5<=float(mean)<=55) or float(mean)>float(t)+1:
            raise ValueError("Dato diario faltante/fuera de rango: "+city+" "+key)
        rows[key]={"rain":float(p),"temp":float(t),"mean":float(mean)}
    return rows,url

def angles(d):
    doy=d.timetuple().tm_yday
    return [math.sin(2*math.pi*doy/365.25),math.cos(2*math.pi*doy/365.25),
            math.sin(2*math.pi*d.month/12),math.cos(2*math.pi*d.month/12)]

def city_features(name):
    """Identidad geográfica explícita de la localidad, fija antes de entrenar."""
    return [1.0 if name==city else 0.0 for city in PLACES]

def daily_features(series,day,city):
    hist=[]
    for days in (1,2,3,7,14):
        s=series.get((day-dt.timedelta(days=days)).isoformat())
        if s is None:return None
        hist.extend([math.log1p(max(0,s["rain"])),s["temp"]])
    return hist+angles(day)+city_features(city)

def fit_daily(data):
    X=[];y1=[];y2=[];days=[];sites=[]
    for loc,series in data.items():
        for key,row in series.items():
            day=dt.date.fromisoformat(key)
            feat=daily_features(series,day,loc)
            if feat is None:continue
            X.append(feat);y1.append(math.log1p(row["rain"]));y2.append(row["temp"])
            days.append(day);sites.append(loc)
    X=np.asarray(X,float);d=np.asarray(days,dtype="datetime64[D]")
    train=d<np.datetime64("2025-01-01")
    test=(d>=np.datetime64("2025-01-01"))&(d<np.datetime64("2026-01-01"))
    if train.sum()<3500 or test.sum()<1000:raise ValueError("Sin datos suficientes o test temporal")
    opt={"n_estimators":120,"max_depth":14,"min_samples_leaf":7,"n_jobs":2,"random_state":20261021}
    rain=RandomForestRegressor(**opt).fit(X[train],np.asarray(y1)[train])
    temp=RandomForestRegressor(**opt).fit(X[train],np.asarray(y2)[train])
    observed_r=np.expm1(np.asarray(y1)[test])
    er=float(np.mean(np.abs(observed_r-np.maximum(0,np.expm1(rain.predict(X[test]))))))
    et=float(np.mean(np.abs(np.asarray(y2)[test]-temp.predict(X[test]))))
    baseline_r=float(np.mean(np.abs(observed_r-np.median(np.expm1(np.asarray(y1)[train])))))
    baseline_t=float(np.mean(np.abs(np.asarray(y2)[test]-np.median(np.asarray(y2)[train]))))
    # Refit through all available observed archive ONLY after closed holdout.
    rain.fit(X,np.asarray(y1));temp.fit(X,np.asarray(y2))
    return rain,temp,{"mae_lluvia_mm":round(er,2),"mae_temperatura_c":round(et,2),
                      "baseline_global_lluvia_mm":round(baseline_r,2),
                      "baseline_global_temperatura_c":round(baseline_t,2),
                      "periodo_prueba":"2025 completo","tipo_prueba":"retrospectiva un paso con rezagos reales, NO pronosticos as-issued",
                      "n_entrenamiento":int(train.sum()),"n_prueba":int(test.sum())}

def predict_daily(models,series,city):
    rain,temp=models
    s=dict(series)
    last=dt.date.fromisoformat(max(s))
    target_end=TODAY+dt.timedelta(days=6)
    result=[]
    date=last+dt.timedelta(days=1)
    while date<=target_end:
        X=daily_features(s,date,city)
        if X is None:raise ValueError("Faltan retardos para generar siguiente día")
        x=np.asarray([X],float)
        val1=round(max(0,min(800,math.expm1(float(rain.predict(x)[0])))),2)
        val2=round(max(-5,min(55,float(temp.predict(x)[0]))),2)
        row={"fecha":date.isoformat(),"precipitacion_mm":val1,"temperatura_max_c":val2}
        s[date.isoformat()]={"rain":val1,"temp":val2}
        if date>=TODAY:result.append(row)
        date+=dt.timedelta(days=1)
    if len(result)!=7:raise ValueError("Horizonte semanal incompleto")
    return result

def monthly_features(series,year,month,city):
    result=[]
    for offset in (1,2,3,6,12):
        y=year; m=month-offset
        while m<1:y-=1;m+=12
        record=series.get(f"{y:04d}-{m:02d}")
        if record is None:return None
        result.extend([math.log1p(max(0,record["rain"])),record["temp"]])
    result.extend([math.sin(2*math.pi*month/12),math.cos(2*math.pi*month/12)])
    return result+city_features(city)

def from_csv():
    path=ROOT/"datos"/"lambayeque_mensual_era5_8d.csv"
    raw=path.read_bytes(); d=defaultdict(dict)
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        if row["localidad"] in PLACES:
            d[row["localidad"]][row["mes"]]={"rain":float(row["precipitacion_mm"]),
                                              "temp":float(row["temperatura_c"])}
    return d,hashlib.sha256(raw).hexdigest()

def latest_monthly_era5(history,archives):
    # Full January-September 2026 from daily ERA5 archive.
    for city,series in archives.items():
        month=defaultdict(list)
        for date,entry in series.items():
            if date.startswith("2026-") and date[:7]<f"{TODAY.year:04d}-{TODAY.month:02d}":
                month[date[:7]].append(entry)
        for key,rows in month.items():
            yr,mo=map(int,key.split("-"))
            if len(rows)<28:continue
            if len(rows)!=(__import__("calendar").monthrange(yr,mo)[1]):continue
            history[city][key]={"rain":sum(x["rain"] for x in rows),
                                "temp":sum(x["mean"] for x in rows)/len(rows)}
    return history

def fit_month(history):
    """Select RF hyperparameters and a conservative RF/climatology weight on 2019-20.
    Evaluate 2021-25 exactly once AFTER choices are frozen.
    A local seasonal baseline is more demanding than a global median.
    """
    X=[];yr=[];yt=[];times=[];cities=[]
    for city,series in history.items():
        for key,record in series.items():
            y,m=map(int,key.split("-"))
            features=monthly_features(series,y,m,city)
            if features is None:continue
            X.append(features);yr.append(math.log1p(record["rain"]))
            yt.append(record["temp"]);times.append(key);cities.append(city)
    X=np.asarray(X,float);yr=np.asarray(yr,float);yt=np.asarray(yt,float)
    d=np.asarray(times)
    train=d<"2019-01";validation=(d>="2019-01")&(d<"2021-01")
    traintest=d<"2021-01";test=(d>="2021-01")&(d<"2026-01")
    if train.sum()<800 or validation.sum()<60 or test.sum()<190:
        raise ValueError("Separación temporal insuficiente para seleccionar RF")
    def clim_table(end):
        result={}
        for city,series in history.items():
            for month in range(1,13):
                values=[x for key,x in series.items()
                        if key<end and key.endswith(f"-{month:02d}")]
                if not values:raise ValueError("Climatología incompleta "+city)
                result[city,month]=(float(np.mean([v["rain"] for v in values])),
                                    float(np.mean([v["temp"] for v in values])))
        return result
    def baseline(table,indices,col):
        return np.asarray([table[cities[i],int(times[i][-2:])][col]
                           for i in np.flatnonzero(indices)],float)
    old=clim_table("2019-01")
    valid_clim=baseline(old,validation,0)
    observed_val=np.expm1(yr[validation])
    params=[
        {"n_estimators":160,"max_depth":8,"min_samples_leaf":12},
        {"n_estimators":200,"max_depth":10,"min_samples_leaf":7},
        {"n_estimators":200,"max_depth":14,"min_samples_leaf":4},
    ]
    val=[]
    for conf in params:
        model=RandomForestRegressor(**conf,n_jobs=2,random_state=20261021)
        model.fit(X[train],yr[train])
        predicted=np.maximum(0,np.expm1(model.predict(X[validation])))
        raw=float(np.mean(np.abs(observed_val-predicted)))
        # Retain a nonzero RF component in an explicit candidate, never pretend
        # a 100% climatological baseline is a Random Forest forecast.
        for weight in (0.2,0.4,0.6,0.8,1.0):
            weighted=weight*predicted+(1-weight)*valid_clim
            mae=float(np.mean(np.abs(observed_val-weighted)))
            val.append((mae,raw,weight,conf))
    val.sort(key=lambda x:(x[0],x[1],x[2],x[3]["max_depth"]))
    valid_mae,valid_raw,weight,best=val[0]
    params_best={**best,"n_jobs":2,"random_state":20261021}
    rain=RandomForestRegressor(**params_best)
    temp=RandomForestRegressor(**params_best)
    rain.fit(X[traintest],yr[traintest]);temp.fit(X[traintest],yt[traintest])
    ref=clim_table("2021-01")       # 1996-2020 only, frozen before the test.
    obs=np.expm1(yr[test]);raw_rf=np.maximum(0,np.expm1(rain.predict(X[test])))
    local_ref=baseline(ref,test,0);tref=baseline(ref,test,1)
    hybrid=weight*raw_rf+(1-weight)*local_ref
    mae_raw=float(np.mean(np.abs(obs-raw_rf)))
    mae_hybrid=float(np.mean(np.abs(obs-hybrid)))
    mae_clim=float(np.mean(np.abs(obs-local_ref)))
    mae_temp=float(np.mean(np.abs(yt[test]-temp.predict(X[test]))))
    mae_temp_clim=float(np.mean(np.abs(yt[test]-tref)))
    # After reporting the untouched test, fit candidate on all completed records.
    rain.fit(X,yr);temp.fit(X,yt)
    metrics={
        "mae_lluvia_mm":round(mae_raw,2),
        "mae_rf_ajustado_mm":round(mae_hybrid,2),
        "mae_temp_c":round(mae_temp,2),
        "mae_climatologia_local_mm":round(mae_clim,2),
        "mae_temperatura_climatologia_local_c":round(mae_temp_clim,2),
        "peso_rf_ajustado":weight,
        "ventaja_rf_frente_a_climatologia_local_mm":round(mae_clim-mae_raw,2),
        "ventaja_hibrido_frente_a_climatologia_local_mm":round(mae_clim-mae_hybrid,2),
        "rf_supera_climatologia_local_en_prueba":bool(mae_raw<mae_clim),
        "rf_ajustado_supera_climatologia_en_prueba":bool(mae_hybrid<mae_clim),
        "seleccion_hyperparametros":best,
        "mae_validacion_2019_2020_ajustado_mm":round(valid_mae,2),
        "mae_validacion_2019_2020_rf_crudo_mm":round(valid_raw,2),
        "seleccion_solo_validacion":"2019-2020; test 2021-2025 no usado para seleccionar",
        "periodo_prueba":"2021-2025",
        "tipo_prueba":"retrospectiva a un paso con rezagos reales; 6 meses encadenados sin validacion",
        "n_entrenamiento":int(traintest.sum()),
        "n_prueba":int(test.sum()),
    }
    return (rain,temp,weight,ref),metrics

def next_month(year,month):
    if month==12:return year+1,1
    return year,month+1

def predict_month(model,series,city):
    rain,temp,weight,climatology=model;s=dict(series)
    latest=max(s);y,m=map(int,latest.split("-"))
    horizon=[]
    for _ in range(18):
        y,m=next_month(y,m);key=f"{y:04d}-{m:02d}"
        feat=monthly_features(s,y,m,city)
        if feat is None:raise ValueError("Sin retardos mensuales "+key)
        xr=np.asarray([feat],float)
        rf_raw=max(0,min(2000,math.expm1(float(rain.predict(xr)[0]))))
        clim=climatology.get((city,m),(rf_raw,0))[0]
        r=round(weight*rf_raw+(1-weight)*clim,1)
        t=round(float(temp.predict(xr)[0]),1)
        s[key]={"rain":r,"temp":t}
        if key>="2026-11":horizon.append({"mes":key,"precipitacion_mm":r,"temperatura_media_c":t,"recursivo":True})
        if len(horizon)>=6:break
    if len(horizon)!=6:raise ValueError("No se pudo obtener Nov-Abr")
    return horizon,latest

def main():
    now=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    audit={"tipo":"RandomForestRegressor original reproducible de investigación, NO modelo operativo",
           "unidades_temperatura":"Diario Tmax; mensual temperatura media (no promedio de Tmax)",
           "estrategia_mejora":"Características de localidad explicitas; climatologia mensual local y prueba temporal para lluvia y temperatura.",
           "fecha_generacion_utc":now,"fecha_local":TODAY.isoformat(),
           "fuente_historica":"ERA5 reanálisis por Open-Meteo; histórico mensual ERA5 8D del OAF",
           "documentacion":"https://open-meteo.com/en/docs/historical-weather-api",
           "interpretacion":"Candidatos autoregresivos propios; sin skill as-issued, sin validación instrumental, sin probabilidades de ocurrencia certificadas.",
           "alertas_automaticas":False,"operativo_certificado":False,
           "horizonte_semanal":7,"horizonte_mensual_inicio":"2026-11","estado":"en_calculo"}
    try:
        data={};urls={}
        for name in PLACES:
            data[name],urls[name]=source(name)
        models=fit_daily(data)
        history,sha=from_csv()
        history=latest_monthly_era5(history,data)
        mmodel,monthskill=fit_month(history)
        daily={name:predict_daily(models[:2],series,name) for name,series in data.items()}
        monthly={};lastdates={}
        for name,series in history.items():monthly[name],lastdates[name]=predict_month(mmodel,series,name)
        audit.update({"estado":"candidato_experimental_generado","metrica_diaria":models[2],
                      "metrica_mensual":monthskill,"datos_fuente":urls,"sha256_matriz_mensual":sha,
                      "ultimo_mes_con_datos":lastdates,"ultimos_dias_era5":{name:max(d) for name,d in data.items()},
                      "pronostico_diario_rf_experimental":daily,"escenarios_mensuales_rf_experimentales":monthly})
    except Exception as exc:
        audit["estado"]="no_disponible";audit["error"]=str(exc)[:400]
    OUT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(audit["estado"],audit.get("error",""),flush=True)

if __name__=="__main__":main()
