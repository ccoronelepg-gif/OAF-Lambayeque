#!/usr/bin/env python3
"""OAF 8D: Does NOAA Niño1+2 / T300 improve forecasts of Lambayeque local anomalies?

Observational local weather = reanalysis ERA5-Land 2m temperature + ERA5
precipitation and solar radiation via Open-Meteo Historical Weather API.
Fixed 1996-2022 seasonal mean defines ML targets for training/test, hence
test 2023-2026 cannot leak into anomaly definitions. Separate 1996-2025
climatology supplied for descriptive site comparisons (NOT ML test).
Predefined features: local anomaly at origin t; Niño1+2 t; T300 t-1.
Three Ridge variants (local lag; +SST; +SST+T300), persistence and
climatology-zero, with SAME examples and train labels <=2022-12.
These are modelled grid cells NOT SENAMHI observed station readings.
Monthly t SST generally available only in month t+1; h1 is normally
intramonth nowcast, not a pre-month prediction; historical reanalysis
also is revised, not a true vintage-as-issued prospective evaluation.
"""
import argparse
import calendar
import csv
import json
import math
import statistics as st
import sys
import time
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

from benchmark_atmosferico_8b import load_target,fit,predict,shift
from benchmark_calor_subsuperficial_8c import HEAT_FILE

ROOT=Path("datos")
MONTHLY=ROOT/"lambayeque_mensual_era5_8d.csv"
RESULT=ROOT/"benchmark_impacto_lambayeque_8d.json"
FOLDS=ROOT/"benchmark_impacto_lambayeque_8d_prueba.csv"
START="1996-01-01"
END="2026-09-30"
REFERENCE_START="1996-01"
REFERENCE_END="2025-12"
FREEZE_END="2022-12"
TEST_START="2023-01"
HORIZONS=(1,2,3)
ALPHA=20.0
SITES={"Chiclayo":(-6.77140,-79.84090),
       "Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),
       "Olmos":(-5.98825,-79.74723)}
VARS={
 "temperatura_c":{"model":"era5_land","daily":"temperature_2m_mean","unit":"°C","agg":"mean"},
 "precipitacion_mm":{"model":"era5","daily":"precipitation_sum","unit":"mm","agg":"sum"},
 "radiacion_mj_m2":{"model":"era5","daily":"shortwave_radiation_sum","unit":"MJ/m²","agg":"sum"}
}
VAR_ORDER=list(VARS)


def finite(value):
    return type(value) in (float,int) and math.isfinite(value)


def pull(site,lat,lon,model,fields,start=START,end=END):
    params={"latitude":lat,"longitude":lon,"start_date":start,"end_date":end,
            "timezone":"America/Lima","daily":",".join(fields),"models":model}
    url="https://archive-api.open-meteo.com/v1/archive?"+urlencode(params)
    last=None
    for retry in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-8D-research/1.0"}),
                         timeout=120) as response:
                obj=json.load(response)
            if obj.get("error") or not isinstance(obj.get("daily"),dict):
                raise ValueError("Open-Meteo API error "+str(obj.get("reason")))
            if obj.get("timezone")!="America/Lima":
                raise ValueError("API returned unexpected timezone "+str(obj.get("timezone")))
            d=obj["daily"];dates=d.get("time")
            if (not isinstance(dates,list) or not dates or
                dates[0]!=start or dates[-1]!=end):
                raise ValueError("Daily temporal coverage mismatch "+site)
            if len(dates)!=len(set(dates)):
                raise ValueError("Repeated daily timestamps")
            for variable in fields:
                if not isinstance(d.get(variable),list) or len(d[variable])!=len(dates):
                    raise ValueError("Missing/incomplete daily field "+variable)
            return obj
        except (OSError,ValueError) as e:
            last=e
            if retry<2:time.sleep(5)
    raise RuntimeError("Unavailable ERA reanalysis for "+site+" "+model+": "+str(last))


def merge_reanalysis(site):
    lat,lon=SITES[site]
    t=pull(site,lat,lon,"era5_land",["temperature_2m_mean"])
    p=pull(site,lat,lon,"era5",["precipitation_sum","shortwave_radiation_sum"])
    if t["daily"]["time"]!=p["daily"]["time"]:
        raise ValueError("ERA5/ERA5-Land daily date alignment mismatch "+site)
    units_t=t.get("daily_units",{})
    units_p=p.get("daily_units",{})
    if (units_t.get("temperature_2m_mean")!="°C" or
        units_p.get("precipitation_sum")!="mm" or
        units_p.get("shortwave_radiation_sum") not in ("MJ/m²","MJ/m2")):
        raise ValueError("Unexpected ERA5 daily units "+site)
    grouped=defaultdict(lambda:{"temperature_2m_mean":[],"precipitation_sum":[],
                                 "shortwave_radiation_sum":[]})
    for i,day in enumerate(t["daily"]["time"]):
        dt=date.fromisoformat(day)
        v=[t["daily"]["temperature_2m_mean"][i],
           p["daily"]["precipitation_sum"][i],p["daily"]["shortwave_radiation_sum"][i]]
        if not all(finite(x) for x in v) or v[1]<0 or v[2]<0 or not -25<v[0]<55:
            raise ValueError("Missing/unphysical historical daily value "+site+" "+day)
        key=day[:7]
        grouped[key]["temperature_2m_mean"].append(v[0])
        grouped[key]["precipitation_sum"].append(v[1])
        grouped[key]["shortwave_radiation_sum"].append(v[2])
    out={}
    for month,values in sorted(grouped.items()):
        year,mo=map(int,month.split("-"))
        expected=calendar.monthrange(year,mo)[1]
        if month==END[:7]:expected=int(END[-2:])
        if len(values["temperature_2m_mean"])!=expected:
            raise ValueError("Incomplete month "+month+" "+site)
        out[month]={
            "temperatura_c":st.mean(values["temperature_2m_mean"]),
            "precipitacion_mm":sum(values["precipitation_sum"]),
            "radiacion_mj_m2":sum(values["shortwave_radiation_sum"])
        }
    if len(out)!=369 or min(out)!="1996-01" or max(out)!="2026-09":
        raise ValueError("Unexpected local monthly coverage "+site+" "+str(len(out)))
    return out,{"era5_land_celda":[t.get("latitude"),t.get("longitude")],
                "era5_celda":[p.get("latitude"),p.get("longitude")],
                "coordenadas_referencia":[lat,lon]}


def load_heat():
    if not HEAT_FILE.is_file():raise ValueError("Fase 8C monthly NOAA PMEL T300 not published")
    res={}
    with HEAT_FILE.open(encoding="utf-8",newline="") as f:
        rows=csv.DictReader(f)
        if not rows.fieldnames or not {"mes","t300_anomalia_c"}<=set(rows.fieldnames):
            raise ValueError("Wrong PMEL T300 source structure")
        for row in rows:
            ym=row["mes"];value=float(row["t300_anomalia_c"])
            if ym in res or not finite(value) or abs(value)>10:
                raise ValueError("Duplicate/invalid T300 anomaly "+ym)
            res[ym]=value
    if len(res)<550:raise ValueError("T300 archive too short")
    return res


def means(local,start,end):
    """Monthly climatology; no testing years may enter ML baseline."""
    result={}
    for var in VAR_ORDER:
        result[var]={}
        for month in range(1,13):
            items=[row[var] for ym,row in local.items()
                   if start<=ym<=end and int(ym[-2:])==month]
            if len(items)<25:raise ValueError("Climatology too short")
            result[var][month]=st.mean(items)
    return result


def anomaly(local,base):
    return {ym:{var:values[var]-base[var][int(ym[-2:])]
                for var in VAR_ORDER} for ym,values in local.items()}


def build(local,sea,heat,horizon,variable):
    periods=sorted(local)
    training=[];holdout=[]
    for origin in periods:
        future=shift(origin,horizon)
        prev=shift(origin,-1)
        if future not in local or prev not in heat or origin not in sea:
            continue
        if origin not in local or not finite(sea[origin]):
            continue
        values=[local[origin][variable],sea[origin],heat[prev]]
        if not all(finite(x) for x in values):
            continue
        example=(origin,future,values,local[future][variable])
        if future<=FREEZE_END:
            training.append(example)
        elif origin>=TEST_START:
            holdout.append(example)
        # months with origin <=2022-12, target >=2023 deliberately purged
    if len(training)<250 or len(holdout)<35:
        raise ValueError("Insufficient strict train/test "+variable+" h"+str(horizon)+
                         " counts="+str((len(training),len(holdout))))
    return training,holdout


def evaluation(local,sea,heat):
    diagnostic=means(local,"1996-01","2025-12")    # 30y public climate
    training_base=means(local,"1996-01",FREEZE_END) # 27y fixed test baseline
    fixed=anomaly(local,training_base)
    records=[]
    blocks={}
    for var in VAR_ORDER:
        blocks[var]={}
        for horizon in HORIZONS:
            tr,test=build(fixed,sea,heat,horizon,var)
            # predefined baseline and nesting. Normalize on training only.
            models={}
            for name,position in (("local",[0]),("nino",[0,1]),("nino_t300",[0,1,2])):
                models[name]=fit([([x[i] for i in position],y) for _,_,x,y in tr],ALPHA)
            current=[]
            for origin,target,x,y in test:
                rec={
                  "localidad":None,"variable":var,"unidad":VARS[var]["unit"],
                  "mes_origen":origin,"mes_objetivo":target,"horizonte_meses":horizon,
                  "observado_anomalia":y,
                  "climatologia_cero":0.0,
                  "persistencia_local":x[0],
                  "modelo_local":predict(models["local"],[x[0]]),
                  "modelo_nino":predict(models["nino"],x[:2]),
                  "modelo_nino_t300":predict(models["nino_t300"],x)
                }
                current.append(rec)
            records+=current
            def metric(column):
                err=[r[column]-r["observado_anomalia"] for r in current]
                return {"n":len(err),"mae":round(st.mean(map(abs,err)),4),
                        "rmse":round(math.sqrt(st.mean(x*x for x in err)),4),
                        "sesgo":round(st.mean(err),4)}
            m={col:metric(col) for col in (
                "climatologia_cero","persistencia_local","modelo_local",
                "modelo_nino","modelo_nino_t300")}
            base=m["modelo_local"]["mae"]; ocean=m["modelo_nino"]["mae"]; heatmae=m["modelo_nino_t300"]["mae"]
            blocks[var][str(horizon)]={
                "n_entrenamiento":len(tr),"n_prueba":len(current),
                "origen_prueba_inicial":current[0]["mes_origen"],
                "origen_prueba_final":current[-1]["mes_origen"],
                "metricas":m,
                "mejora_nino_vs_local":round(1-ocean/base,4) if base else None,
                "mejora_nino_t300_vs_local":round(1-heatmae/base,4) if base else None,
                "mejora_nino_t300_vs_nino":round(1-heatmae/ocean,4) if ocean else None,
                "supera_climatologia":heatmae<m["climatologia_cero"]["mae"],
                "supera_persistencia":heatmae<m["persistencia_local"]["mae"],
                "validado_prospectivamente":False
            }
    # Use public climatology only for diagnostic table; never ML anomalies.
    public={var:{
      f"{month:02d}":round(diagnostic[var][month],3) for month in range(1,13)
    } for var in VAR_ORDER}
    return records,blocks,public


def write(monthly,records,results):
    ROOT.mkdir(exist_ok=True)
    with MONTHLY.open("w",encoding="utf-8",newline="") as f:
        cols=["localidad","mes"]+VAR_ORDER
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for city,series in monthly.items():
            for ym,row in sorted(series.items()):
                w.writerow({"localidad":city,"mes":ym,**{
                    k:round(v,5) for k,v in row.items()}})
    with FOLDS.open("w",encoding="utf-8",newline="") as f:
        cols=["localidad","variable","unidad","mes_origen","mes_objetivo",
             "horizonte_meses","observado_anomalia","climatologia_cero",
             "persistencia_local","modelo_local","modelo_nino","modelo_nino_t300"]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in records:w.writerow(r)
    RESULT.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def self_test():
    assert shift("2022-12",2)=="2023-02"
    assert calendar.monthrange(2024,2)[1]==29
    mock={}
    for y in range(1996,2027):
        for m in range(1,10 if y==2026 else 13):
            mock[f"{y:04d}-{m:02d}"]={
                "temperatura_c":float(m)+float(y>=2023),
                "precipitacion_mm":float(m*2),
                "radiacion_mj_m2":float(m*8)}
    full=means(mock,"1996-01","2025-12")
    freeze=means(mock,"1996-01","2022-12")
    assert abs(freeze["temperatura_c"][1]-1.0)<1e-8
    assert full["temperatura_c"][1]>freeze["temperatura_c"][1]
    aa=anomaly(mock,freeze)
    assert aa["2024-01"]["temperatura_c"]==1.
    sea={ym:0.1 for ym in mock}
    heat={ym:0.2 for ym in mock}
    train,test=build(aa,sea,heat,2,"temperatura_c")
    assert all(month<=FREEZE_END for _,month,_,_ in train)
    assert all(origin>=TEST_START for origin,_,_,_ in test)
    assert train and test and all(v==1. for origin,_,_,v in test)
    print("8D PASS: 30yr public baseline, frozen 27yr testing reference, strict date embargo, leap years")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:self_test();return
    sea=load_target()
    heat=load_heat()
    monthly={};positions={}
    for site in SITES:
        monthly[site],positions[site]=merge_reanalysis(site)
        print("Fetched site",site,len(monthly[site]),"complete months",flush=True)
    all_records=[];results={}
    for site,series in monthly.items():
        records,summary,reference=evaluation(series,sea,heat)
        for row in records:row["localidad"]=site
        all_records+=records
        results[site]={"ubicaciones_celdas":positions[site],
                       "climatologia_publica_1996_2025":reference,
                       "resultados_modelos":summary}
        print("Evaluated",site,len(records),"rows",flush=True)
    if len(all_records)<1400:raise ValueError("Missing forecast evaluation records")
    report={
      "fase":"8D","fecha_generacion_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "estado":"retrospectivo_regional_no_validado_prospectivamente",
      "climatologia_publica":"1996–2025, 30 años (descriptiva, no usada en la prueba)",
      "climatologia_entrenamiento":"1996–2022, fija para toda predicción de prueba 2023–2026",
      "climatologia_omm_comparacion":"1991–2020 no computada en esta fase; referencia OMM para futuras comparaciones",
      "origenes_prueba":"2023-01 a 2026-09, objetivos limitados al último reanálisis completo",
      "objetivo":"anomalías mensuales locales en temperatura, precipitación y radiación",
      "modelo_temperatura":"ERA5-Land via Open-Meteo Historical Weather API",
      "modelo_lluvia_y_radiacion":"ERA5 via Open-Meteo Historical Weather API",
      "fuentes_oceanicas":"NOAA NCEI ERSSTv5 Niño1+2 (rebase OAF 1991–2020), PMEL GODAS T300 base 1981–2010",
      "temperatura_agregacion":"media mensual de 2m °C",
      "lluvia_agregacion":"suma mensual mm",
      "radiacion_agregacion":"suma mensual MJ/m²",
      "modelo_ridge_alpha_fijo":ALPHA,
      "horizontes_meses":[1,2,3],
      "predictores":[
        "anomalía local del mes de origen t",
        "anomalía Niño1+2 del mes de origen t",
        "T300 del mes t−1 (solo modelo más amplio)"
      ],
      "sin_datos_objetivo_futuros_en_training":True,
      "validacion_instrumental_senamhi":False,
      "validacion_prospectiva_real":False,
      "es_alerta_enfen":False,
      "es_icen_oficial":False,
      "n_filas_prueba":len(all_records),
      "localidades":results,
      "advertencias":[
        "ERA5 y ERA5-Land son reanálisis, no estaciones SENAMHI o sensores dentro de parcelas.",
        "El índice NOAA Niño1+2 del mes t se publica después de cerrar t; horizonte uno puede corresponder a una estimación intramensual, no pronóstico previo a inicio de mes.",
        "Las fuentes históricas pueden ser revisadas; este ensayo no es un archivo vintage-as-of de emisiones operativas.",
        "La climatología 1996–2025 se muestra para descripción, pero se usa exclusivamente 1996–2022 para calcular la anomalía de prueba y prevenir fuga de datos.",
        "La radiación solar global de onda corta no es radiación UV ni PAR.",
        "Correlación o menor error de Niño1+2 no prueban causalidad, ni implican lluvia extrema, daños o infecciones.",
        "El modelo extendido no genera pronóstico futuro ni sustituye alertas oficiales de ENFEN o SENAMHI.",
        "Las coordenadas son localidades referenciales y las cuadrículas ERA5/ERA5-Land pueden representar diferentes áreas espaciales."
      ]
    }
    write(monthly,all_records,report)
    print("8D finished:",len(all_records),"test records",flush=True)


if __name__=="__main__":
    try:main()
    except Exception as e:
        print("8D ERROR:",e,file=sys.stderr)
        raise SystemExit(1)
