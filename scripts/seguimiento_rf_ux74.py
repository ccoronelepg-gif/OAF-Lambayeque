#!/usr/bin/env python3
"""UX74. Conserva las emisiones RF y Open-Meteo en su fecha de origen.

Una prediccion solo puede verificarse despues del horizonte y con una fuente
distinta, aqui ERA5 REANALISIS (no estacion instrumental).
NUNCA usa predicciones emitidas como etiquetas de entrenamiento.
"""
from __future__ import annotations
import datetime as dt
import json
import math
import pathlib
from urllib.parse import urlencode
import requests

ROOT=pathlib.Path(__file__).resolve().parents[1]
INPUT=ROOT/"datos"/"rf_experimental_ux15.json"
OUT=ROOT/"datos"/"seguimiento_rf_ux74"/"emisiones.json"
CLIM=ROOT/"datos"/"seguimiento_rf_ux74"/"climatologia_diaria_era5_ux76.json"
ARCHIVE="https://archive-api.open-meteo.com/v1/archive"
FORECAST="https://api.open-meteo.com/v1/forecast"
PLACES={"Chiclayo":(-6.7714,-79.8409),"Jayanca":(-6.39278,-79.8228),
        "Motupe":(-6.15083,-79.7142),"Olmos":(-5.98825,-79.74723)}
HEADERS={"User-Agent":"OAF-Lambayeque/UX74 model-monitoring-research"}
FIELDS=("precipitation_sum","temperature_2m_max")

def get(url,params):
    r=requests.get(url,params=params,timeout=(15,60),headers=HEADERS)
    r.raise_for_status()
    return r.json()

def is_number(value):
    return isinstance(value,(int,float)) and math.isfinite(value)

def issued_open_meteo(forecast_dates):
    """Congela la respuesta externa en la fecha de emision; no descarga historicos reconstruidos."""
    comparison={}
    for city,(lat,lon) in PLACES.items():
        try:
            payload=get(FORECAST,{"latitude":lat,"longitude":lon,"daily":",".join(FIELDS),
               "timezone":"America/Lima","forecast_days":8,"cell_selection":"land"})
            daily=payload.get("daily",{})
            dates=daily.get("time",[])
            rain=daily.get("precipitation_sum",[])
            tmax=daily.get("temperature_2m_max",[])
            if not(len(dates)==len(rain)==len(tmax)):
                raise ValueError("Serie externa desalineada")
            byday={str(d):{"fecha":str(d),"precipitacion_mm":float(p),
                              "temperatura_max_c":float(t)}
                   for d,p,t in zip(dates,rain,tmax) if is_number(p) and is_number(t)}
            dates_needed=forecast_dates[city]
            if not all(d in byday for d in dates_needed):
                raise ValueError("Faltan fechas exactas del RF")
            comparison[city]=[byday[day] for day in dates_needed]
        except (requests.RequestException,ValueError,TypeError,KeyError) as error:
            comparison[city]={"estado":"no_disponible","razon":str(error)[:220]}
    return comparison


def daily_climatology():
    """Referencia baselina fija ERA5 1996-2025, calculada una vez por localidad.
    NO son predicciones de ERA5 para 2026/2027. Siempre usa solamente fechas
    anteriores a las emisiones, con el mismo corte fijo 1996-2025.
    """
    if CLIM.exists():
        try:
            data=json.loads(CLIM.read_text(encoding="utf8"))
            if data.get("periodo")=="1996-2025" and all(
               c in data.get("localidades",{}) and len(data["localidades"][c])>=365
               for c in PLACES):
                return data["localidades"]
        except (OSError,ValueError,TypeError,KeyError):pass
    output={}
    for city,(lat,lon) in PLACES.items():
        payload=get(ARCHIVE,{"latitude":lat,"longitude":lon,
           "start_date":"1996-01-01","end_date":"2025-12-31",
           "daily":",".join(FIELDS),"models":"era5","timezone":"America/Lima"})
        daily=payload.get("daily",{})
        dates=daily.get("time",[])
        rain=daily.get("precipitation_sum",[])
        temp=daily.get("temperature_2m_max",[])
        if not(len(dates)==len(rain)==len(temp)) or len(dates)<10000:
            raise ValueError("Climatologia historica incompleta en "+city)
        groups={}
        for date,p,t in zip(dates,rain,temp):
            if date<"1996-01-01" or date>"2025-12-31":continue
            g=groups.setdefault(date[5:],{"rain":[],"temp":[]})
            if is_number(p) and p>=0:g["rain"].append(float(p))
            if is_number(t):g["temp"].append(float(t))
        city_values={}
        for md,g in groups.items():
            if len(g["rain"])<20 or len(g["temp"])<20:continue
            city_values[md]={"precipitacion_mm":round(sum(g["rain"])/len(g["rain"]),5),
                             "temperatura_max_c":round(sum(g["temp"])/len(g["temp"]),5),
                             "muestras_lluvia":len(g["rain"]),
                             "muestras_tmax":len(g["temp"])}
        if len(city_values)<365:raise ValueError("Pocos dias historicos en "+city)
        output[city]=city_values
        print("ERA5_REFERENCIA_HISTORICA",city,len(city_values),flush=True)
    CLIM.parent.mkdir(parents=True,exist_ok=True)
    CLIM.write_text(json.dumps({"version":"UX76","periodo":"1996-2025",
        "fuente":"ERA5 reanalisis, no prediccion meteorologica futura",
        "localidades":output},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    return output

def issued_era5_reference(forecast_dates):
    """Valores de climatologia fijados en fecha de emision para un cotejo 3-vias."""
    try:
        histories=daily_climatology()
    except (requests.RequestException,OSError,TypeError,ValueError,KeyError) as err:
        print("CLIMATOLOGIA_INDISPONIBLE",str(err)[:200],flush=True)
        return {city:{"estado":"no_disponible","razon":str(err)[:120]} for city in PLACES}
    result={}
    for city,dates in forecast_dates.items():
        rows=[]
        for date in dates:
            val=histories.get(city,{}).get(date[5:])
            if not val:break
            rows.append({"fecha":date,"precipitacion_mm":val["precipitacion_mm"],
                         "temperatura_max_c":val["temperatura_max_c"]})
        result[city]=rows if len(rows)==7 else {"estado":"no_disponible","razon":"Faltan dias de referencia"}
    return result

def archivable(payload):
    if payload.get("estado")!="candidato_experimental_generado":
        return False
    if payload.get("operativo_certificado") is not False or payload.get("alertas_automaticas") is not False:
        raise ValueError("Modelo no autorizado como experimental")
    if set(payload.get("pronostico_diario_rf_experimental",{}))!=set(PLACES):
        raise ValueError("No estan completas las localidades")
    date=dt.date.fromisoformat(payload["fecha_local"])
    for city,values in payload["pronostico_diario_rf_experimental"].items():
        if len(values)!=7:raise ValueError("Siete dias incompletos: "+city)
        days=[dt.date.fromisoformat(v["fecha"]) for v in values]
        if days!=[date+dt.timedelta(days=i) for i in range(7)]:
            raise ValueError("RF diario desalineado: "+city)
        for v in values:
            if not all(is_number(v.get(k)) for k in ("precipitacion_mm","temperatura_max_c")):
                raise ValueError("Valor RF no numerico")
    return True

def create_entry(payload):
    daily=payload["pronostico_diario_rf_experimental"]
    dates={city:[v["fecha"] for v in values] for city,values in daily.items()}
    horizons=payload.get("metrica_diaria",{}).get("backtest_semanal_recursivo",{}).get("por_horizonte",[])
    monthly=payload.get("metrica_mensual",{}).get("evaluacion_multihorizonte",{}).get("por_horizonte",[])
    return {
        "fecha_local":payload["fecha_local"],
        "fecha_generacion_utc":payload["fecha_generacion_utc"],
        "fecha_era5_ultimo_dato":payload.get("entrenamiento_actualizado_con_era5_hasta"),
        "fuente_entrenamiento":"ERA5 - reanalisis por Open-Meteo",
        "rf_diario":daily,
        "rf_mensual":payload.get("escenarios_mensuales_rf_experimentales",{}),
        "open_meteo_diario_emitido":issued_open_meteo(dates),
        "era5_climatologia_diaria_emitida":issued_era5_reference(dates),
        "era5_periodo_referencia":"1996-2025; solo promedio historico, no prediccion",
        "ajuste_2024":payload.get("metrica_diaria",{}).get("seleccion_hiperparametros_2024"),
        "resumen_backtest": {
           "lluvia_mae_rf_mm":[r.get("mae_rf_lluvia_mm") for r in horizons],
           "lluvia_mae_climatologia_mm":[r.get("mae_climatologia_lluvia_mm") for r in horizons],
           "tmax_mae_rf_c":[r.get("mae_rf_temperatura_c") for r in horizons],
           "tmax_mae_climatologia_c":[r.get("mae_climatologia_temperatura_c") for r in horizons],
           "mensual_lluvia_mae_rf_mm":[r.get("mae_rf_mm") for r in monthly],
           "mensual_lluvia_mae_climatologia_mm":[r.get("mae_climatologia_local_mm") for r in monthly]
        },
        "verificacion_era5":None,
        "evaluacion_instrumental":False,
        "habilitado_operativo":False
    }

def issue(data,payload):
    date=payload["fecha_local"]
    if any(e["fecha_local"]==date for e in data["emisiones"]):
        return False
    data["emisiones"].append(create_entry(payload))
    data["emisiones"].sort(key=lambda x:x["fecha_local"])
    data["emisiones"]=data["emisiones"][-180:]
    return True

def historical_sample(city,start,end):
    lat,lon=PLACES[city]
    payload=get(ARCHIVE,{"latitude":lat,"longitude":lon,"start_date":start,
        "end_date":end,"daily":",".join(FIELDS),"models":"era5","timezone":"America/Lima"})
    d=payload.get("daily",{});days=d.get("time",[]);rain=d.get("precipitation_sum",[])
    tmax=d.get("temperature_2m_max",[])
    if not(len(days)==len(rain)==len(tmax)):
        raise ValueError("ERA5 fechas o variables incompletas")
    return {day:{"precipitacion_mm":p,"temperatura_max_c":t}
           for day,p,t in zip(days,rain,tmax) if is_number(p) and is_number(t)}

def score(issued,observed):
    matches={o["fecha"]:o for o in issued}
    if set(matches)!=set(observed):return None
    for day,obs in observed.items():
        prediction=matches.get(day)
        if not prediction or not all(is_number(prediction.get(k)) and is_number(obs.get(k))
                  for k in ("precipitacion_mm","temperatura_max_c")):return None
    return {
        "n_dias":len(observed),
        "mae_lluvia_mm":round(sum(abs(matches[d]["precipitacion_mm"]-v["precipitacion_mm"]) for d,v in observed.items())/len(observed),3),
        "mae_tmax_c":round(sum(abs(matches[d]["temperatura_max_c"]-v["temperatura_max_c"]) for d,v in observed.items())/len(observed),3)
    }

def evaluate_mature(data):
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).date()
    cutoff=now-dt.timedelta(days=9)  # retraso ERA5; nunca validar dias futuros
    pending=[e for e in data["emisiones"] if e.get("verificacion_era5") is None
          and dt.date.fromisoformat(e["fecha_local"])+dt.timedelta(days=6)<=cutoff][-25:]
    if not pending:return False
    dates=[dt.date.fromisoformat(v["fecha"]) for e in pending
           for values in e["rf_diario"].values() for v in values]
    start=min(dates).isoformat();end=max(dates).isoformat()
    observations={}
    for city in PLACES:
        try:observations[city]=historical_sample(city,start,end)
        except (requests.RequestException,ValueError,TypeError) as err:
            print("ERA5 NO DISPONIBLE",city,str(err)[:180])
            return False
    changed=False
    for entry in pending:
        evaluated={}
        for city in PLACES:
            daily=entry["rf_diario"][city]
            subset={x["fecha"]:observations[city][x["fecha"]] for x in daily
                    if x["fecha"] in observations[city]}
            if len(subset)!=7:break
            rf_score=score(daily,subset)
            compared=entry.get("open_meteo_diario_emitido",{}).get(city)
            external_score=score(compared,subset) if isinstance(compared,list) else None
            baseline=entry.get("era5_climatologia_diaria_emitida",{}).get(city)
            era5_score=score(baseline,subset) if isinstance(baseline,list) else None
            evaluated[city]={"rf":rf_score,"open_meteo":external_score,
             "era5_climatologia":era5_score,
             "referencia":"ERA5 reanalisis no instrumental","dias":len(subset)}
        if len(evaluated)==len(PLACES):
            entry["verificacion_era5"]={"evaluado_hasta":end,"por_localidad":evaluated,
             "criterio":"as-issued RF y Open-Meteo; climatologia ERA5 historica congelada en emision (UX76 si existe); verificacion posterior ERA5, NO estaciones",
             "apto_para_alertas":False}
            changed=True
    return changed

def main():
    payload=json.loads(INPUT.read_text(encoding="utf8"))
    if not archivable(payload):
        print("SIN EMISION NUEVA: RF no disponible; se conserva el historico.")
        return
    OUT.parent.mkdir(parents=True,exist_ok=True)
    # Crear y persistir la referencia fija aun si hoy ya existe una emision.
    # Un fallo de descarga no debe adulterar las emisiones existentes.
    try:daily_climatology()
    except (requests.RequestException,OSError,ValueError,TypeError,KeyError) as err:
        print("CLIMATOLOGIA_UX76_PENDIENTE",str(err)[:200],flush=True)
    data=json.loads(OUT.read_text(encoding="utf8")) if OUT.exists() else {
        "version":"UX74","modelo":"RF experimental","evaluacion":"as-issued diferida versus ERA5; no instrumental",
        "fuente_externa":"Open-Meteo Forecast archivado al emitir","emisiones":[]}
    added=issue(data,payload)
    reviewed=evaluate_mature(data)
    if added or reviewed or not OUT.exists():
        OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("NUEVA_EMISION",added,"COMPARACIONES_MADURAS",sum(bool(e.get("verificacion_era5")) for e in data["emisiones"]),
          "TOTAL",len(data["emisiones"]))

if __name__=="__main__":main()
