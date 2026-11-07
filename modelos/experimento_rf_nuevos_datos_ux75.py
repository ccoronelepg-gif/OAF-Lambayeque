#!/usr/bin/env python3
"""OAF UX75: experimento controlado de RF con nuevas observaciones ERA5.

Incumbente: RF autoregresivo de lluvia/Tmax (lag 1,2,3,7,14).
Candidato: RF directo por horizonte 1-7 con predictores historicos adicionales:
HR media, radiacion, viento y T media. SOLO historicos al origen.
Seleccion: 2024, sin tocar 2025/2026. Backtest 2025 y 2026 con ventana
expansiva por ano: NO as-issued. No se publica como pronostico operativo.
"""
from __future__ import annotations
import calendar, datetime as dt, json, math, os, pathlib, hashlib
from collections import defaultdict
from urllib.parse import urlencode
import numpy as np
import requests
from sklearn.ensemble import RandomForestRegressor

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"datos"/"rf_experimento_ux75"/"evaluacion_reentrenamiento.json"
TZ=dt.timezone(dt.timedelta(hours=-5))
TODAY=dt.datetime.now(TZ).date()
MAX_DATE=TODAY-dt.timedelta(days=7)
SOURCE="https://archive-api.open-meteo.com/v1/archive"
LOCATIONS={"Chiclayo":(-6.7714,-79.8409),"Jayanca":(-6.39278,-79.8228),
           "Motupe":(-6.15083,-79.7142),"Olmos":(-5.98825,-79.74723)}
VARIABLES={
 "rain":"precipitation_sum","temp":"temperature_2m_max",
 "mean":"temperature_2m_mean","hr":"relative_humidity_2m_mean",
 "wind":"wind_speed_10m_mean","radiation":"shortwave_radiation_sum"
}
SEED=20261107

def download(city,point):
    p={"latitude":point[0],"longitude":point[1],"start_date":"2021-01-01",
       "end_date":MAX_DATE.isoformat(),"timezone":"America/Lima",
       "models":"era5","daily":",".join(VARIABLES.values())}
    response=requests.get(SOURCE,params=p,timeout=(20,110),
       headers={"User-Agent":"OAF-Lambayeque scientific RF benchmark UX75"})
    response.raise_for_status()
    raw=response.json()
    if raw.get("error"):raise ValueError(str(raw.get("reason"))[:150])
    daily=raw.get("daily",{});dates=daily.get("time",[])
    if len(dates)<1950 or any(len(daily.get(key,[]))!=len(dates) for key in VARIABLES.values()):
        raise ValueError("Series ERA5 incompletas para "+city)
    result={}
    for i,stamp in enumerate(dates):
        row={}
        for field,key in VARIABLES.items():
            value=daily[key][i]
            if not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError("Dato no finito "+city+" "+key+" "+stamp)
            row[field]=float(value)
        if not (0<=row["rain"]<=1200 and -10<=row["temp"]<=55
                and -10<=row["mean"]<=55 and row["mean"]<=row["temp"]+1
                and 0<=row["hr"]<=100 and 0<=row["wind"]<=180
                and 0<=row["radiation"]<=55):
            raise ValueError("Rangos invalidos "+city+" "+stamp)
        result[stamp]=row
    expected=(dt.date.fromisoformat(max(result))-dt.date(2021,1,1)).days+1
    if len(result)!=expected or max(result)<(MAX_DATE-dt.timedelta(days=2)).isoformat():
        raise ValueError("ERA5 incompleto hasta ventana reciente en "+city)
    return result, response.url

def dates_of(series,step=1):
    first=dt.date.fromisoformat(min(series))
    last=dt.date.fromisoformat(max(series))
    for n in range(14,(last-first).days+1,step):
        yield first+dt.timedelta(days=n)

def seasonal(day,city):
    doy=day.timetuple().tm_yday
    return [math.sin(2*math.pi*doy/365.25),math.cos(2*math.pi*doy/365.25),
            math.sin(2*math.pi*day.month/12),math.cos(2*math.pi*day.month/12)]+[
            int(city==c) for c in LOCATIONS]

def lag(series,day,delay):
    return series.get((day-dt.timedelta(days=delay)).isoformat())

def old_features(series,target,city):
    out=[]
    for delay in (1,2,3,7,14):
        row=lag(series,target,delay)
        if row is None:return None
        out.extend([math.log1p(row["rain"]),row["temp"]])
    return out+seasonal(target,city)

def new_features(series,origin,lead,city):
    """No futurables: todas las caracteristicas pertenecen al origen o antes."""
    out=[]
    for delay in (0,1,2,3,6,13):
        row=lag(series,origin,delay)
        if row is None:return None
        out.extend([math.log1p(row["rain"]),row["temp"],row["mean"],
                    row["hr"],row["wind"],row["radiation"]])
    for window in (3,7,14):
        rows=[lag(series,origin,k) for k in range(window)]
        if any(r is None for r in rows):return None
        out.extend([sum(r["rain"] for r in rows),sum(r["temp"] for r in rows)/window,
                    sum(r["hr"] for r in rows)/window])
    day=origin+dt.timedelta(days=lead)
    return out+seasonal(day,city)+[lead,lead/7.0]

def rows_direct(data,target_start,target_end,step):
    x=[];yr=[];yt=[];n=0
    for city,series in data.items():
        for origin in dates_of(series,step):
            for lead in range(1,8):
                day=origin+dt.timedelta(days=lead)
                if day<target_start or day>=target_end:continue
                actual=series.get(day.isoformat())
                if actual is None:continue
                f=new_features(series,origin,lead,city)
                if f is None:continue
                x.append(f);yr.append(math.log1p(actual["rain"]))
                yt.append(actual["temp"]);n+=1
    if n<1000:raise ValueError("Sin suficientes ejemplos directos para "+str(target_start))
    return np.asarray(x,float),np.asarray(yr,float),np.asarray(yt,float)

def rows_old(data,end):
    x=[];yr=[];yt=[]
    for city,series in data.items():
        for day in dates_of(series):
            if day>=end:break
            actual=series.get(day.isoformat())
            f=old_features(series,day,city)
            if f is None or actual is None:continue
            x.append(f);yr.append(math.log1p(actual["rain"]));yt.append(actual["temp"])
    if len(x)<2000:raise ValueError("Insuficiente aprendizaje del incumbente")
    return np.asarray(x),np.asarray(yr),np.asarray(yt)

def fit(x,yr,yt,conf):
    cfg={**conf,"n_jobs":2,"random_state":SEED}
    a=RandomForestRegressor(**cfg).fit(x,yr)
    b=RandomForestRegressor(**cfg).fit(x,yt)
    return a,b

def predict(model,features):
    xx=np.asarray([features],float)
    return max(0,float(math.expm1(model[0].predict(xx)[0]))),float(model[1].predict(xx)[0])

def tune(data):
    X,yr,yt=rows_direct(data,dt.date(2021,1,15),dt.date(2024,1,1),5)
    V,vr,vt=rows_direct(data,dt.date(2024,1,1),dt.date(2025,1,1),14)
    confs=[
        {"n_estimators":120,"max_depth":10,"min_samples_leaf":12},
        {"n_estimators":160,"max_depth":12,"min_samples_leaf":9},
        {"n_estimators":180,"max_depth":8,"min_samples_leaf":16},
    ]
    rankings=[]
    for conf in confs:
        models=fit(X,yr,yt,conf)
        pp=np.maximum(0,np.expm1(models[0].predict(V)))
        tt=models[1].predict(V)
        rankings.append({"params":conf,"mae_lluvia_2024":float(np.mean(np.abs(pp-np.expm1(vr)))),
                         "mae_tmax_2024":float(np.mean(np.abs(tt-vt)))})
    rain=min(rankings,key=lambda x:x["mae_lluvia_2024"])["params"]
    tmax=min(rankings,key=lambda x:x["mae_tmax_2024"])["params"]
    return rain,tmax,rankings

def fit_separately(x,yr,yt,rconf,tconf):
    return (RandomForestRegressor(**rconf,n_jobs=2,random_state=SEED).fit(x,yr),
            RandomForestRegressor(**tconf,n_jobs=2,random_state=SEED).fit(x,yt))

def climatology(data,train_end):
    grouped=defaultdict(list)
    for city,series in data.items():
        for date,row in series.items():
            if date<train_end.isoformat():
                grouped[(city,int(date[5:7]))].append(row)
    return {key:(float(np.mean([x["rain"] for x in rows])),
                  float(np.mean([x["temp"] for x in rows])))
            for key,rows in grouped.items()}

def origin_dates(year,latest):
    day=dt.date(year,1,14)
    while day+dt.timedelta(days=7)<=latest:
        yield day
        day+=dt.timedelta(days=28)

def backtest(data,year,conf_r,conf_t):
    limit=dt.date(year,1,1)
    X,yr,yt=rows_direct(data,dt.date(2021,1,15),limit,5)
    direct=fit_separately(X,yr,yt,conf_r,conf_t)
    A,ar,at=rows_old(data,limit)
    inc=fit_separately(A,ar,at,{"n_estimators":160,"max_depth":10,"min_samples_leaf":12},
                          {"n_estimators":160,"max_depth":10,"min_samples_leaf":12})
    baseline=climatology(data,limit)
    errors={m:{v:defaultdict(list) for v in ("rain","temp")}
            for m in ("direct","incumbente","climatologia")}
    samples=0
    for city,full in data.items():
        for origin in origin_dates(year,dt.date.fromisoformat(max(full))):
            if origin.year!=year:break
            origin_data={k:dict(value) for k,value in full.items()
                         if k<=origin.isoformat()}
            if not origin_data:continue
            simulated=dict(origin_data)
            records=[]
            for lead in range(1,8):
                target=origin+dt.timedelta(days=lead)
                actual=full.get(target.isoformat())
                f=new_features(origin_data,origin,lead,city)
                g=old_features(simulated,target,city)
                if actual is None or f is None or g is None:break
                r_new,t_new=predict(direct,f)
                r_old,t_old=predict(inc,g)
                r_clim,t_clim=baseline[(city,target.month)]
                records.append((lead,actual,(r_new,t_new),(r_old,t_old),(r_clim,t_clim)))
                simulated[target.isoformat()]={"rain":r_old,"temp":t_old}
            if len(records)!=7:continue
            samples+=1
            for lead,actual,pnew,pold,pclim in records:
                for name,pred in (("direct",pnew),("incumbente",pold),("climatologia",pclim)):
                    errors[name]["rain"][lead].append(pred[0]-actual["rain"])
                    errors[name]["temp"][lead].append(pred[1]-actual["temp"])
    if samples<24:raise ValueError("Backtest sin suficientes origenes para "+str(year))
    metrics={}
    for name,variables in errors.items():
        metrics[name]={}
        for var,horizons in variables.items():
            all_errors=[e for lead in range(1,8) for e in horizons[lead]]
            metrics[name][var]={
                "mae":round(float(np.mean(np.abs(all_errors))),4),
                "rmse":round(float(np.sqrt(np.mean(np.square(all_errors)))),4),
                "sesgo":round(float(np.mean(all_errors)),4),
                "mae_por_horizonte":[round(float(np.mean(np.abs(horizons[i]))),4) for i in range(1,8)]
            }
    comparacion={}
    for var in ("rain","temp"):
        new=metrics["direct"][var];old=metrics["incumbente"][var];base=metrics["climatologia"][var]
        wins=sum(a<b for a,b in zip(new["mae_por_horizonte"],old["mae_por_horizonte"]))
        wins_clim=sum(a<b for a,b in zip(new["mae_por_horizonte"],base["mae_por_horizonte"]))
        comparacion[var]={
            "reduccion_mae_vs_incumbente_pct":round(100*(old["mae"]-new["mae"])/old["mae"],2) if old["mae"] else None,
            "reduccion_mae_vs_climatologia_pct":round(100*(base["mae"]-new["mae"])/base["mae"],2) if base["mae"] else None,
            "horizontes_ganados_vs_incumbente":wins,
            "horizontes_ganados_vs_climatologia":wins_clim,
            "mejora_robusta":new["mae"]<old["mae"] and new["mae"]<base["mae"] and wins>=5
        }
    return {"ano_prueba":year,"origenes":samples,"pares":samples*7,"metodo":"siete dias sin variables futuras, modelado directo vs incumbente recursivo",
            "metricas":metrics,"comparacion":comparacion}

def main():
    report={"fase":"UX75","fecha":dt.datetime.now(dt.timezone.utc).isoformat(),
       "fecha_maxima_solicitada_era5":MAX_DATE.isoformat(),
       "estado":"iniciando","operativo_certificado":False,"alertas_automaticas":False,
       "descripcion":"Benchmark nuevo RF directo multivariable contra RF incumbente autoregresivo y climatologia",
       "admisibilidad":"Solo candidatatura investigacion; no recalibra mapa fitosanitario ni activa decisiones.",
       "fuente":"ERA5 reanalisis Open-Meteo, NO observacion de estacion.",
       "separacion_temporal":"Hiperparametros validados en 2024, pruebas en 2025 y 2026, sin variables futuras"}
    try:
        data={};sources={}
        for city,point in LOCATIONS.items():
            data[city],sources[city]=download(city,point)
            print("DATOS",city,len(data[city]),max(data[city]),flush=True)
        report["ultimas_fechas"]={city:max(rows) for city,rows in data.items()}
        report["n_registros"]={city:len(rows) for city,rows in data.items()}
        report["url_fuente"]=sources
        rconf,tconf,ranking=tune(data)
        report["seleccion_2024"]={"candidatos":ranking,"mejor_lluvia":rconf,"mejor_tmax":tconf}
        print("TUNING_2024",rconf,tconf,flush=True)
        tests={}
        for year in (2025,2026):
            tests[str(year)]=backtest(data,year,rconf,tconf)
            print("BACKTEST",year,json.dumps(tests[str(year)]["comparacion"]),flush=True)
        report["pruebas"]=tests
        # Reentrenamiento final REAL hasta la ultima observacion ERA5.
        # Se guarda modelo de INVESTIGACION como artefacto CI, no se publica operativo.
        from joblib import dump
        last=min(max(rows) for rows in data.values())
        until=dt.date.fromisoformat(last)+dt.timedelta(days=1)
        FX,Fyr,Fyt=rows_direct(data,dt.date(2021,1,15),until,5)
        final_models=fit_separately(FX,Fyr,Fyt,rconf,tconf)
        from hashlib import sha256
        artifact=OUT.parent/"rf_candidato_multivariable_ux75.joblib"
        artifact.parent.mkdir(parents=True,exist_ok=True)
        dump({"lluvia":final_models[0],"temperatura_maxima":final_models[1],
              "fecha_ultimo_era5":last,"calidad":"experimental_no_operativo",
              "configuracion_lluvia":rconf,"configuracion_temperatura":tconf},artifact,compress=3)
        report["reentrenamiento_final"]={
           "ultimo_dato_incorporado":last,"ejemplos_supervisados":len(FX),
           "dimensiones_predictoras":int(FX.shape[1]),
           "modelo_guardado_en_artefacto":"rf_candidato_multivariable_ux75.joblib",
           "sha256_modelo":sha256(artifact.read_bytes()).hexdigest(),
           "publicado_como_operativo":False,
           "caracteristicas":{"variables":["precipitacion","temperatura_maxima",
                    "temperatura_media","humedad_relativa_media",
                    "viento_medio","radiacion_solar_diaria"],
                    "restriccion":"Solo variables del dia origen y previas"}
        }
        print("MODELO_FINAL",last,"filas",len(FX),"sha256",report["reentrenamiento_final"]["sha256_modelo"],flush=True)
        report["comparacion_final"]={}
        for var in ("rain","temp"):
            p2025=tests["2025"]["comparacion"][var]
            p2026=tests["2026"]["comparacion"][var]
            report["comparacion_final"][var]={
                "mejora_2025":p2025["mejora_robusta"],
                "mejora_2026":p2026["mejora_robusta"],
                "habilitar_piloto":p2025["mejora_robusta"] and p2026["mejora_robusta"],
                "criterio":"MAE inferior a RF actual y climatologia; 5/7 horizontes mejores que RF actual en ambos anos"}
        report["estado"]="evaluacion_completa"
    except Exception as exc:
        report["estado"]="sin_validacion"
        report["error"]=str(exc)[:400]
        import traceback
        traceback.print_exc()
        print("ERROR",repr(exc),flush=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ESTADO_FINAL",report["estado"],flush=True)
    if report["estado"]!="evaluacion_completa":raise SystemExit(1)

if __name__=="__main__":main()
