#!/usr/bin/env python3
"""9H complemento: ERA5 precipitación; ERA5-Land temperaturas máximas/mínimas.
Puntos: 2 referencias 9G x 3 estaciones. Periodo 1996–2013.
Comparación descriptiva, no pronóstico ni emplazamiento certificado.
"""
import argparse
import calendar
import csv
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json"
OBS=ROOT/"datos/estaciones_9d/series_mensuales_9d.csv"
BASE=ROOT/"datos/validacion_estaciones_9h"
OUTPUT=BASE/"contraste_era5_complementario_9h.json"
PAIRS=BASE/"pares_era5_complementarios_9h.csv"
SOURCES=[
    ("ERA5_atmosferico","era5",["precipitation_sum"]),
    ("ERA5-Land_temperatura","era5_land",["temperature_2m_max","temperature_2m_min"]),
]
FIELDNAMES=["nombre","codigo_archivo","escenario","producto","variable","mes",
            "observado","reanálisis","diferencia_reanalisis_menos_observado",
            "unidad","lat_celda","lon_celda","lat_documental","lon_documental",
            "distancia_celda_km","sha256_respuesta","url"]

def haversine(a,b):
    p1,q1=map(math.radians,a);p2,q2=map(math.radians,b)
    v=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin((q2-q1)/2)**2
    return round(2*6371.0088*math.asin(min(1,math.sqrt(v))),3)

def sites():
    q=json.loads(CAT.read_text("utf8"))
    assert q["fase"]=="9G" and not q["ubicacion_sensor_1963_2014_certificada"]
    points=[]
    for s in q["estaciones"]:
        for i in (1,2):
            r=s[f"coordenada_documental_{i}"]
            points.append({"name":s["nombre"],"code":s["codigo_archivo"],
                           "scenario":f"documental_{i}",
                           "lat":float(r["lat"]),"lon":float(r["lon"])})
    assert len(points)==6
    return points

def station_data():
    table={}
    with OBS.open(newline="",encoding="utf8") as f:
        for r in csv.DictReader(f):
            if not ("1996-01"<=r["mes"]<="2013-12"):continue
            d=calendar.monthrange(*map(int,r["mes"].split("-")))[1]
            assert int(r["dias_calendario"])==d
            for key,valid_col,value_col in [
              ("precipitation_sum","precip_dias_validos","precip_total_mm"),
              ("temperature_2m_max","tmax_dias_validos","tmax_media_c"),
              ("temperature_2m_min","tmin_dias_validos","tmin_media_c")]:
                value=float(r[value_col]) if r[value_col]!="" and int(r[valid_col])==d else None
                table[(r["codigo"],r["mes"],key)]=value
    return table

def fetch(url):
    import requests
    err=None
    for k in range(2):
        try:
            r=requests.get(url,timeout=(15,90),headers={"User-Agent":"OAF-9H-ERA5-verification/1.0"})
            r.raise_for_status()
            raw=r.content
            if len(raw)<100:raise ValueError("Respuesta menor de 100 bytes")
            return raw
        except Exception as e:
            err=e
            if k==0:time.sleep(2)
    raise RuntimeError(str(err)[:450])

def retrieve(product,model,variables,points):
    out=defaultdict(lambda:defaultdict(dict));cell={};provenance=[]
    chunks=[(1996,2005),(2006,2013)] if model=="era5" else [
        (1996,1999),(2000,2003),(2004,2007),(2008,2011),(2012,2013)
    ]
    for y1,y2 in chunks:
        url="https://archive-api.open-meteo.com/v1/archive?"+urlencode({
          "latitude":",".join(str(p["lat"]) for p in points),
          "longitude":",".join(str(p["lon"]) for p in points),
          "start_date":f"{y1}-01-01","end_date":f"{y2}-12-31",
          "daily":",".join(variables),"models":model,"timezone":"America/Lima",
          "cell_selection":"land","temperature_unit":"celsius"})
        raw=fetch(url);sha=hashlib.sha256(raw).hexdigest()
        api=json.loads(raw)
        if not isinstance(api,list) or len(api)!=len(points):
            raise ValueError("API no devolvió los 6 candidatos para "+product)
        for i,obj in enumerate(api):
            if obj.get("error"):raise ValueError(str(obj))
            position=(float(obj["latitude"]),float(obj["longitude"]))
            if haversine((points[i]["lat"],points[i]["lon"]),position)>24:
                raise ValueError("Centro de celda fuera del rango de búsqueda")
            if i in cell and haversine(cell[i],position)>.01:
                raise ValueError("Centro diferente entre periodos para "+product)
            cell[i]=position
            dates=(obj.get("daily") or {}).get("time",[])
            if not dates:raise ValueError("Serie diaria no disponible")
            for var in variables:
                unit=(obj.get("daily_units") or {}).get(var)
                if unit!=("mm" if var=="precipitation_sum" else "°C"):
                    raise ValueError("Unidad externa inesperada: "+var+"="+str(unit))
                values=obj["daily"].get(var)
                if not isinstance(values,list) or len(values)!=len(dates):
                    raise ValueError("Variable diaria no retornada: "+var)
                grouped=defaultdict(list)
                for date,v in zip(dates,values):
                    if date[:7] not in [f"{year}-{month:02d}" for year in range(1996,2014) for month in range(1,13)]:
                        raise ValueError("Fecha fuera del periodo objetivo")
                    grouped[date[:7]].append((date,v))
                for mon,values_month in grouped.items():
                    year,month=map(int,mon.split("-"))
                    n_days=calendar.monthrange(year,month)[1]
                    if len(values_month)!=n_days or len(set(t for t,v in values_month))!=n_days:
                        continue
                    if not all(isinstance(v,(float,int)) and math.isfinite(v)
                               and (var!="precipitation_sum" or v>=0) for t,v in values_month):
                        continue
                    vals=[v for t,v in values_month]
                    avg=(sum(vals) if var=="precipitation_sum" else sum(vals)/len(vals))
                    if mon in out[i][var]:raise ValueError("Mes duplicado API")
                    out[i][var][mon]=(round(avg,4),sha,url)
        provenance.append({"producto":product,"periodo":f"{y1}-{y2}","url":url,
                           "sha256":sha,"bytes":len(raw),
                           "utc":datetime.now(timezone.utc).isoformat()})
    return out,cell,provenance

def scores(rows):
    if not rows:return None
    diffs=[r["reanálisis"]-r["observado"] for r in rows]
    n=len(diffs)
    return {"n_meses":n,"inicio":min(r["mes"] for r in rows),"fin":max(r["mes"] for r in rows),
       "mae":round(sum(abs(x) for x in diffs)/n,3),
       "sesgo":round(sum(diffs)/n,3),
       "rmse":round(math.sqrt(sum(x*x for x in diffs)/n),3),
       "unidad":"mm" if rows[0]["variable"]=="precipitation_sum" else "°C",
       "validacion_independiente":False,"es_pronostico":False}

def make(points,table,archives,provenance,errors):
    allrows=[];summaries=[]
    for product,model,variables in SOURCES:
        data,cell,_=archives.get(product,({}, {}, []))
        for i,point in enumerate(points):
            for var in variables:
                monthly=data.get(i,{}).get(var,{})
                rows=[]
                for mes,(v,sha,url) in sorted(monthly.items()):
                    obs=table.get((point["code"],mes,var))
                    if obs is None:continue
                    c=cell[i]
                    record={"nombre":point["name"],"codigo_archivo":point["code"],
                            "escenario":point["scenario"],"producto":product,
                            "variable":var,"mes":mes,"observado":obs,"reanálisis":v,
                            "diferencia_reanalisis_menos_observado":round(v-obs,4),
                            "unidad":"mm" if var=="precipitation_sum" else "°C",
                            "lat_celda":c[0],"lon_celda":c[1],
                            "lat_documental":point["lat"],"lon_documental":point["lon"],
                            "distancia_celda_km":haversine((point["lat"],point["lon"]),c),
                            "sha256_respuesta":sha,"url":url}
                    rows.append(record);allrows.append(record)
                summaries.append({
                    "nombre":point["name"],"codigo_archivo":point["code"],"escenario":point["scenario"],
                    "producto":product,"variable":var,"centro_celda":cell.get(i),
                    "n_pares":len(rows),"metricas_periodo":scores(rows),
                    "metricas_1998":scores([r for r in rows if r["mes"].startswith("1998-")]),
                    "estado":"comparacion_retroactiva_descriptiva" if rows else "sin_meses_pareados",
                    "autorizacion_validacion_operacional":False
                })
    result={"fase":"9H","submodulo":"ERA5-Land-temperatura_y_ERA5-atmosferico-precipitacion",
            "fecha_proceso_utc":datetime.now(timezone.utc).isoformat(),
            "productos":{a:b for a,b,v in SOURCES},
            "fuentes_sha256":provenance,
            "errores_descarga":errors,
            "n_pares_total":len(allrows),
            "n_pares_era5_precipitacion":sum(r["producto"]=="ERA5_atmosferico" for r in allrows),
            "n_pares_era5_land_temperatura":sum(r["producto"]=="ERA5-Land_temperatura" for r in allrows),
            "observaciones_mensuales_solo_cobertura_diaria_100pct":True,
            "periodo":"1996-01/2013-12",
            "normal_1996_2025_completa":False,
            "emplazamientos_historicos_9g_resueltos":False,
            "convencion_dia_pluviometrico_verificada":False,
            "estaciones_sin_temperaturas_no_imputadas":True,
            "era5_land_precipitacion": "No soportada directamente por el endpoint Open-Meteo; ERA5 atmósfera NO se etiqueta como ERA5-Land.",
            "producto_CHIRPS_en_archivo_separado":"comparacion_observacional_9h.json",
            "validacion_predictiva_operativa":False,
            "sintesis":summaries,
            "advertencias":[
             "ERA5 precipitación atmósfera 0,25° no es ERA5-Land 0,1°; su pixel y fuente son distintos.",
             "ERA5-Land temperatura a 2 metros modelada no es temperatura observada por termómetro en garita de estación.",
             "Los desplazamientos entre coordenadas publicadas y el manejo de altitud pueden cambiar la celda devuelta.",
             "Muestreo ERA5 mediante Open-Meteo, no producto ECMWF de estación individual.",
             "Condición del día meteorológico de estación y unidades originales pendiente de documentación instrumentada.",
             "Los valores reanalizados son retrospectivos, no pronósticos archivados con su fecha de emisión."
            ]}
    return sorted(allrows,key=lambda r:(r["producto"],r["codigo_archivo"],r["escenario"],r["variable"],r["mes"])),result

def save(rows,data):
    BASE.mkdir(parents=True,exist_ok=True)
    with PAIRS.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDNAMES);w.writeheader();w.writerows(rows)
    OUTPUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def check():
    j=json.loads(OUTPUT.read_text("utf8"));assert j["fase"]=="9H" and not j["validacion_predictiva_operativa"]
    assert len(j["sintesis"])==18  # 6 puntos x (lluvia, temperatura max, temp min)
    with PAIRS.open(encoding="utf8",newline="") as f:rows=list(csv.DictReader(f))
    assert len(rows)==j["n_pares_total"]
    assert sum(r["variable"]=="precipitation_sum" for r in rows)==j["n_pares_era5_precipitacion"]
    assert sum(r["variable"].startswith("temperature_") for r in rows)==j["n_pares_era5_land_temperatura"]
    shas=set(s["sha256"] for s in j["fuentes_sha256"])
    assert all(r["sha256_respuesta"] in shas for r in rows)
    assert len(set((r["codigo_archivo"],r["escenario"],r["variable"],r["mes"]) for r in rows))==len(rows)
    original=station_data()
    for r in rows:
        o=original.get((r["codigo_archivo"],r["mes"],r["variable"]))
        assert o is not None and abs(o-float(r["observado"]))<0.0001
        assert abs(float(r["diferencia_reanalisis_menos_observado"])-(float(r["reanálisis"])-o))<0.0002
        assert float(r["distancia_celda_km"])<=24
    print("9H complemento OK:",j["n_pares_era5_precipitacion"],"lluvia ERA5;",
          j["n_pares_era5_land_temperatura"],"pares de temperatura ERA5-Land.")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true");a=parser.parse_args()
    if a.check:return check()
    pts=sites();obs=station_data();provenance=[];errors={};archives={}
    for name,model,variables in SOURCES:
        try:
            data,cell,source=retrieve(name,model,variables,pts)
            archives[name]=(data,cell,source)
            provenance.extend(source)
        except Exception as e:
            errors[name]=f"{type(e).__name__}: {e}"[:400]
            print(name,"no disponible:",errors[name],file=sys.stderr)
    rows,out=make(pts,obs,archives,provenance,errors)
    save(rows,out);check()
if __name__=="__main__":main()
