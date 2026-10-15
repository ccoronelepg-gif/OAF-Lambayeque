#!/usr/bin/env python3
"""OAF: snapshot dated real external forecasts before their verification date.
These are NOT OAF-derived disease or El Niño predictions.
Use Open-Meteo outputs only and never substitute missing values.
"""
import argparse
import json
import math
from datetime import datetime,timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

COORD={"Chiclayo":(-6.77140,-79.84090),"Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),"Olmos":(-5.98825,-79.74723)}
DAILY=["temperature_2m_mean","temperature_2m_max","temperature_2m_min",
       "relative_humidity_2m_mean","precipitation_sum","shortwave_radiation_sum",
       "wind_speed_10m_max","vapour_pressure_deficit_max",
       "et0_fao_evapotranspiration","sunshine_duration"]
ROOT=Path("datos/pronosticos_emitidos")


def query(site):
    latitude,longitude=COORD[site]
    params={"latitude":latitude,"longitude":longitude,
            "daily":",".join(DAILY),"timezone":"America/Lima","forecast_days":8}
    url="https://api.open-meteo.com/v1/forecast?"+urlencode(params)
    with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-Prospective-Archive/1.0"}),timeout=60) as response:
        data=json.load(response)
    if data.get("error") or not isinstance(data.get("daily"),dict):
        raise ValueError("Source API failure: "+str(data.get("reason")))
    return data


def extract(source,today):
    daily=source["daily"]
    dates=daily.get("time")
    if not isinstance(dates,list) or len(dates)!=8:
        raise ValueError("Expected current day plus 7 future dates")
    expected=[(today+timedelta(days=i)).isoformat() for i in range(8)]
    if dates!=expected:
        raise ValueError("Date mismatch or discontinuity: "+repr(dates[:3]))
    if source.get("timezone")!="America/Lima":
        raise ValueError("Wrong forecast timezone")
    units=source.get("daily_units",{})
    if units.get("shortwave_radiation_sum") not in ["MJ/m²","MJ/m2"]:
        raise ValueError("Solar radiation unit mismatch")
    if units.get("vapour_pressure_deficit_max")!="kPa":
        raise ValueError("VPD unit mismatch")
    byday=[]
    for i in range(1,8):
        row={"fecha_valida":dates[i]}
        for name in DAILY:
            arr=daily.get(name)
            if not isinstance(arr,list) or len(arr)!=8:
                raise ValueError("Missing forecast field "+name)
            value=arr[i]
            if not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError("Missing or invalid "+name+" at "+dates[i])
            row[name]=value
        byday.append(row)
    return {"latitud_celda":source.get("latitude"),
            "longitud_celda":source.get("longitude"),
            "unidades":{n:units.get(n) for n in DAILY},
            "jornadas_futuras":byday}


def self_test():
    today=datetime(2026,10,14).date()
    dates=[(today+timedelta(days=i)).isoformat() for i in range(8)]
    fake={"timezone":"America/Lima","daily_units":{
        **{v:"dummy" for v in DAILY},"shortwave_radiation_sum":"MJ/m²","vapour_pressure_deficit_max":"kPa"},
        "daily":{"time":dates,**{v:[5.0]*8 for v in DAILY}}}
    got=extract(fake,today)
    assert len(got["jornadas_futuras"])==7
    assert got["jornadas_futuras"][0]["fecha_valida"]=="2026-10-15"
    fake["daily"]["shortwave_radiation_sum"][2]=None
    try:extract(fake,today)
    except ValueError:pass
    else:raise AssertionError("Missing radiation data was accepted")
    print("Snapshot date, completeness and no-imputation tests passed.")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test();return
    local=datetime.now(ZoneInfo("America/Lima"))
    today=local.date()
    now=datetime.now(ZoneInfo("UTC"))
    record={
        "version":"1.0",
        "tipo":"pronostico_meteorologico_externo_archivado",
        "emision_utc":now.isoformat(timespec="seconds"),
        "consulta_local_peru":local.isoformat(timespec="seconds"),
        "fecha_consulta_local":today.isoformat(),
        "proveedor":"Open-Meteo Forecast API",
        "url_documentacion":"https://open-meteo.com/en/docs",
        "horizonte":"dias calendario siguientes 1 a 7 desde la consulta local",
        "son_predicciones_propias_oaf":False,
        "son_alertas_fitosanitarias":False,
        "localidades":{}
    }
    for site in COORD:
        record["localidades"][site]=extract(query(site),today)
        print("Fetched complete future forecast:",site,flush=True)
    ROOT.mkdir(parents=True,exist_ok=True)
    target=ROOT/(today.isoformat()+".json")
    # Refuse silent overwrite of an earlier emission from the same local day.
    if target.exists():
        old=json.loads(target.read_text(encoding="utf-8"))
        if old.get("fecha_consulta_local")==today.isoformat():
            print("Existing emitted forecast for today preserved:",target)
            return
        raise ValueError("Conflicting emission file")
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Forecast archived as-issued:",target)


if __name__=="__main__":
    main()
