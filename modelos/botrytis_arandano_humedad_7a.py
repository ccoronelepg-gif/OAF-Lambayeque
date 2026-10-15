#!/usr/bin/env python3
"""OAF Lambayeque Fase 7A - examen de HR horaria pronosticada y Botrytis.

No determina infección, presencia, probabilidad, ni necesidad de tratamiento.
UC IPM: episodios >~90 % de HR >=6 h son condiciones favorables para Botrytis
en general, NO un umbral de daño calibrado para arándano de Lambayeque.
UF/IFAS: floración y humectación foliar prolongada son relevantes.
Emite archivo INMUTABLE de pronóstico horario externo (Open-Meteo).
"""
import argparse
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

SITES = {"Motupe": (-6.15083, -79.71420),
         "Jayanca": (-6.39278, -79.82280),
         "Olmos": (-5.98825, -79.74723),
         "Chiclayo": (-6.77140, -79.84090)}
VARIABLES = ("temperature_2m", "relative_humidity_2m",
             "precipitation", "shortwave_radiation", "vapour_pressure_deficit")
ROOT = Path("datos/patrones_botrytis_emitidos")
UNITS = {"temperature_2m": "°C", "relative_humidity_2m": "%",
         "precipitation": "mm", "shortwave_radiation": "W/m²",
         "vapour_pressure_deficit": "kPa"}


def valid_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def evaluate(hourly):
    """Evaluar ocho días horarias (hoy + 7 completos), no rellenar nulos."""
    stamps = hourly.get("time")
    if not isinstance(stamps, list) or len(stamps) < 192:
        raise ValueError("Ocho días horarios requeridos")
    for variable in VARIABLES:
        column = hourly.get(variable)
        if not isinstance(column, list) or len(column) != len(stamps):
            raise ValueError("Variable horaria ausente o desalineada: " + variable)
    grouped = {}
    for i, stamp in enumerate(stamps):
        if not isinstance(stamp, str) or len(stamp) != 16 or stamp[10] != "T" or stamp[-3:] != ":00":
            raise ValueError("Marca horaria inválida " + str(stamp))
        dt = datetime.strptime(stamp, "%Y-%m-%dT%H:%M")
        day, hour = dt.date().isoformat(), dt.hour
        byhour = grouped.setdefault(day, {})
        if hour in byhour:
            raise ValueError("Marca horaria duplicada: " + stamp)
        byhour[hour] = {v: hourly[v][i] for v in VARIABLES}

    today = date.fromisoformat(stamps[0][:10])
    dates = [(today + timedelta(days=i)).isoformat() for i in range(1, 8)]
    full = []
    daily = []
    for day in dates:
        entries = grouped.get(day)
        if entries is None or len(entries) != 24:
            raise ValueError("Día pronosticado sin 24 h: " + day)
        high = 0
        rain = 0.
        solar = 0.
        dpv_sum = 0.
        for hour in range(24):
            row = entries.get(hour)
            if row is None:
                raise ValueError("Hora faltante " + day)
            t,rh,p,rad,vpd = [row[key] for key in VARIABLES]
            if not all(valid_number(v) for v in [t,rh,p,rad,vpd]):
                raise ValueError("Dato horario nulo "+day)
            if not (-20 <= t <= 55 and 0 <= rh <= 100 and p >= 0 and rad >= 0 and vpd >= 0):
                raise ValueError("Dato fuera de rango en "+day)
            full.append({"fecha":day,"hora":hour,"temperature_2m":t,
                         "relative_humidity_2m":rh,"precipitation":p,
                         "shortwave_radiation":rad,"vapour_pressure_deficit":vpd})
            high += int(rh > 90)
            rain += p
            solar += rad*0.0036  # hourly mean W/m² -> MJ/m² over one hour
            dpv_sum += vpd
        daily.append({"fecha":day,"horas_hr_superior_90":high,
                      "lluvia_mm":round(rain,3),"radiacion_solar_mj_m2":round(solar,3),
                      "dpv_medio_kpa":round(dpv_sum/24,3),
                      "contiene_horas_de_episodio":False})
    if len(full) != 168:
        raise ValueError("No hay 168 horas futuras completas")
    group = {row["fecha"]:row for row in daily}
    longest=streak=episodes=0
    for entry in full:
        if entry["relative_humidity_2m"] > 90:
            streak += 1
            longest = max(longest,streak)
            if streak == 6:
                episodes += 1
                group[entry["fecha"]]["contiene_horas_de_episodio"]=True
            elif streak > 6:
                group[entry["fecha"]]["contiene_horas_de_episodio"]=True
        else:
            streak=0
    return {"horizonte_dias":7, "episodios_hr_continua_6h":episodes,
            "mayor_racha_horas":longest,
            "dias_con_horas_de_episodio":sum(x["contiene_horas_de_episodio"] for x in daily),
            "total_horas_hr_superior_90":sum(x["horas_hr_superior_90"] for x in daily),
            "por_dia":daily,
            "variables_crudas_horarias":full}


def fetch(place):
    lat,lon=SITES[place]
    params={"latitude":lat,"longitude":lon,"timezone":"America/Lima",
            "hourly":",".join(VARIABLES),"forecast_days":8}
    url="https://api.open-meteo.com/v1/forecast?"+urlencode(params)
    request=Request(url,headers={"User-Agent":"OAF-Lambayeque-Botrytis-7A-validation/1.0"})
    with urlopen(request,timeout=60) as handle:body=json.load(handle)
    if body.get("error") or not isinstance(body.get("hourly"),dict):
        raise ValueError("Open-Meteo no entregó datos válidos "+str(body.get("reason","")))
    units=body.get("hourly_units",{})
    for v,needed in UNITS.items():
        if units.get(v) != needed and not (needed == "W/m²" and units.get(v) == "W/m2"):
            raise ValueError("Unidad inesperada "+v+": "+str(units.get(v)))
    return body


def run(mode):
    now=datetime.now(timezone.utc)
    local=now.astimezone(ZoneInfo("America/Lima"))
    today=local.date().isoformat()
    names=("Motupe",) if mode=="smoke" else tuple(SITES)
    sites={}
    for place in names:
        raw=fetch(place)
        if raw["hourly"]["time"][0][:10] != today:
            raise ValueError("Día inicial del proveedor no coincide con Perú: "+place)
        assessed=evaluate(raw["hourly"])
        sites[place]={
            "coordenada_solicitada":{"latitud":SITES[place][0],"longitud":SITES[place][1]},
            "celda_modelada":{"latitud":raw.get("latitude"),"longitud":raw.get("longitude")},
            "unidades":{v:raw["hourly_units"][v] for v in VARIABLES},
            "evaluacion":assessed}
        print(place,"7 days / 168 hours:",assessed["episodios_hr_continua_6h"],
              "periods of >90% RH for at least 6h",flush=True)
    if mode=="smoke":
        print("Open-Meteo Botrytis 7A hourly API smoke test passed")
        return
    archive={
        "fase":"7A","fecha_emision_local":today,
        "emision_utc":now.isoformat(timespec="seconds"),
        "tipo":"pronostico_meteorologico_externo_no_indice_de_enfermedad",
        "fuente":"https://api.open-meteo.com/v1/forecast",
        "metodologia":"HR del aire a 2 m > 90 % durante >=6 h seguidas; no humectación foliar",
        "es_diagnostico":False,"es_alerta":False,
        "probabilidad_infeccion_calibrada":False,
        "validacion_campo":False,"localidades":sites}
    ROOT.mkdir(parents=True,exist_ok=True)
    target=ROOT/(today+".json")
    if target.exists():
        print("Emisión de esta fecha ya archivada y conservada:",target)
        return
    target.write_text(json.dumps(archive,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Pronóstico archivado prospectivamente:",target)


def self_test():
    start=datetime(2026,10,14)
    stamps=[(start+timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(192)]
    def sample(high):
        return {"time":stamps,
            "temperature_2m":[23.0]*192,
            "relative_humidity_2m":[95.0 if i in high else 65. for i in range(192)],
            "precipitation":[0.]*192,
            "shortwave_radiation":[200.]*192,
            "vapour_pressure_deficit":[0.5]*192}
    ten=evaluate(sample(range(24,34)))
    assert ten["episodios_hr_continua_6h"]==1 and ten["mayor_racha_horas"]==10
    assert len(ten["variables_crudas_horarias"])==168
    assert evaluate(sample([]))["episodios_hr_continua_6h"]==0
    span=evaluate(sample(range(46,52)))
    assert span["episodios_hr_continua_6h"]==1 and span["por_dia"][1]["contiene_horas_de_episodio"]
    missing=sample([]);missing["relative_humidity_2m"][29]=None
    try:evaluate(missing)
    except ValueError:pass
    else:raise AssertionError("Null values incorrectly accepted")
    print("Botrytis 7A: synthetic 10h, no event, midnight, null rejection PASSED")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    try:
        if args.self_test:self_test()
        else:run("smoke" if args.smoke else "archive")
    except Exception as error:
        print("Botrytis 7A FAILED:",error,file=sys.stderr)
        raise SystemExit(1)
