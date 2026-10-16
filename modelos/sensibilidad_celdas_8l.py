#!/usr/bin/env python3
"""OAF 8L — sensibilidad climática a selección de celda ERA5-Land vía Open-Meteo.

Descarga 1996–2025, por terceras décadas, para cuatro puntos OAF y métodos
land/nearest. Conserva los JSON *originales* comprimidos, con URL/SHA256.
Solo compara reanálisis, NUNCA estaciones SENAMHI ni habilidad prospectiva.
Python >=3.11 (biblioteca estándar). Sin rellenar datos ausentes.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import gzip
import hashlib
import io
import json
import math
import statistics as st
import time
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
INPUT="datos/fuentes_celdas_8l"
OUTPUT="datos/sensibilidad_celdas_8l"
HIST="datos/lambayeque_mensual_era5_8d.csv"
SITES={"Chiclayo":(-6.77140,-79.84090),
       "Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),
       "Olmos":(-5.98825,-79.74723)}
SELECTIONS=("land","nearest")
BLOCKS=((1996,2005),(2006,2015),(2016,2025))
DOCS="https://open-meteo.com/en/docs/historical-weather-api"
API="https://archive-api.open-meteo.com/v1/archive"
MONTH_FIELDS=("localidad","mes","tmedia_land_c","tmedia_nearest_c",
              "diferencia_nearest_menos_land_c","anomalia_land_c",
              "anomalia_nearest_c","diferencia_anomalias_c",
              "tmedia_era5_8d_archivada_c","diferencia_8d_menos_land_8l_c")
BASELINE_START="1996-01"
BASELINE_END="2025-12"
METADATA_VERSION=1

def finite(value):
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError("Valor térmico faltante/no finito")
    if not -40 < value < 55:
        raise ValueError("Valor térmico físicamente inverosímil")
    return float(value)

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def path_for(root,selection,start,end):
    return root/INPUT/f"{selection}_{start}_{end}.json.gz"

def sha_for(root,selection,start,end):
    return root/INPUT/f"{selection}_{start}_{end}.meta.json"

def build_url(selection,start,end):
    params={
      "latitude":",".join(str(v[0]) for v in SITES.values()),
      "longitude":",".join(str(v[1]) for v in SITES.values()),
      "start_date":f"{start}-01-01","end_date":f"{end}-12-31",
      "timezone":"America/Lima","daily":"temperature_2m_mean",
      "models":"era5_land","cell_selection":selection
    }
    return API+"?"+urlencode(params)

def expected_dates(start,end):
    first=date(start,1,1)
    final=date(end,12,31)
    for i in range((final-first).days+1):
        yield (first+timedelta(days=i)).isoformat()

def check_payload(payload,selection,start,end):
    if not isinstance(payload,list) or len(payload)!=len(SITES):
        raise ValueError("Se requieren cuatro respuestas, una por sitio OAF")
    lookup={}
    expected=list(expected_dates(start,end))
    for site,p in zip(SITES,payload):
        if not isinstance(p,dict) or p.get("error") or p.get("timezone")!="America/Lima":
            raise ValueError("Proveedor devolvió error o zona incorrecta: "+site)
        if p.get("utc_offset_seconds")!=-18000:
            raise ValueError("Respuesta sin huso Peru UTC−5")
        daily=p.get("daily",{})
        dates=daily.get("time")
        temps=daily.get("temperature_2m_mean")
        if dates!=expected or not isinstance(temps,list) or len(temps)!=len(expected):
            raise ValueError("Cobertura diaria 1996–2025 incompleta o desordenada: "+site)
        for value in temps:finite(value)
        lat,lon=p.get("latitude"),p.get("longitude")
        elevation=p.get("elevation")
        if any(type(z) not in (int,float) or not math.isfinite(z) for z in (lat,lon,elevation)):
            raise ValueError("Ubicación/elevación API faltante: "+site)
        if abs(lat)>90 or abs(lon)>180 or not -500<=elevation<=7000:
            raise ValueError("Metadatos geográficos fuera de rango")
        slat,slon=SITES[site]
        # Sanity check only; a provider grid cell is allowed to differ from point.
        if abs(slat-lat)>0.5 or abs(slon-lon)>0.5:
            raise ValueError("Respuesta de celda demasiado lejos: "+site)
        lookup[site]=p
    return lookup

def fetch_one(url):
    last=None
    for attempt in range(3):
        try:
            request=Request(url,headers={"User-Agent":"OAF-Lambayeque-8L-scientific-comparison/1.0",
                                          "Accept":"application/json"})
            with urlopen(request,timeout=100) as response:
                if response.status!=200:raise ValueError("HTTP "+str(response.status))
                blob=response.read(9_000_001)
            if len(blob)>9_000_000:raise ValueError("Respuesta API excede el máximo")
            return blob
        except (URLError,HTTPError,TimeoutError,OSError,ValueError) as e:
            last=e
            if attempt<2:time.sleep(4*(attempt+1))
    raise RuntimeError("Open-Meteo sin respuesta verificable: "+str(last))

def validate_source(blob,meta,method,start,end):
    data=json.loads(blob)
    check_payload(data,method,start,end)
    if meta.get("selection")!=method or meta.get("start")!=start or meta.get("end")!=end:
        raise ValueError("Metadatos y bloque temporal de proveedor inconsistentes")
    if meta.get("url")!=build_url(method,start,end):
        raise ValueError("URL no reproduce consulta publicada")
    if meta.get("sha256_json_original")!=sha(blob):
        raise ValueError("SHA-256 de respuesta original alterado")
    if meta.get("unidad")!="°C" or meta.get("agregacion")!="media_aritmetica_de_medias_diarias":
        raise ValueError("Unidad o método no homologado")
    if meta.get("fase")!="8L" or meta.get("dataset")!="ERA5-Land vía Open-Meteo Historical Weather API":
        raise ValueError("Fuente o tipo de metadatos alterados")
    return data

def source_bytes(root,method,start,end):
    path=path_for(root,method,start,end)
    meta_path=sha_for(root,method,start,end)
    if not path.is_file() or not meta_path.is_file():
        return None
    compressed=path.read_bytes()
    if len(compressed)>9_000_000:raise ValueError("Archivo comprimido demasiado grande")
    blob=gzip.decompress(compressed)
    metadata=json.loads(meta_path.read_text(encoding="utf-8"))
    validate_source(blob,metadata,method,start,end)
    return blob,metadata

def fetch_all(root,refresh=False):
    """Sin fallback: archiva los seis bloques solo después de validar TODOS."""
    folder=root/INPUT
    folder.mkdir(parents=True,exist_ok=True)
    keys=[(method,start,end) for method in SELECTIONS for start,end in BLOCKS]
    current=[source_bytes(root,*key) for key in keys]
    if all(x is not None for x in current) and not refresh:
        print("Los seis bloques originales verificables ya están archivados. No se descargan otra vez.")
        return
    # Nunca mezclar una revisión nueva y vieja si faltan una o varias fuentes.
    staged=[]
    for method,start,end in keys:
        url=build_url(method,start,end)
        blob=fetch_one(url)
        check_payload(json.loads(blob),method,start,end)
        meta={"fase":"8L","selection":method,"start":start,"end":end,
              "url":url,"sha256_json_original":sha(blob),
              "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "unidad":"°C","agregacion":"media_aritmetica_de_medias_diarias",
              "dataset":"ERA5-Land vía Open-Meteo Historical Weather API",
              "documentacion":DOCS,
              "metadata_version":METADATA_VERSION,
              "no_certifica_celda_original_8d":True}
        staged.append((method,start,end,blob,meta))
        print("Bloque validado sin observaciones faltantes:",method,start,end,flush=True)
    # Publicación tras validación: no se pierden entradas anteriores por un error API.
    for method,start,end,blob,meta in staged:
        path=path_for(root,method,start,end)
        path.write_bytes(gzip.compress(blob,mtime=0))
        sha_for(root,method,start,end).write_text(
            json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Seis bloques archivados: fuentes originales comprimidas con SHA, sin errores de cobertura.")

def read_8d(root):
    with (root/HIST).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {"localidad","mes","temperatura_c"}.issubset(reader.fieldnames):
            raise ValueError("Archivo 8D no incluye Tmedia")
        table={}
        for row in reader:
            site,mon=row["localidad"],row["mes"]
            if site not in SITES:raise ValueError("Localidad desconocida 8D")
            if BASELINE_START<=mon<=BASELINE_END:
                key=(site,mon)
                if key in table:raise ValueError("Mes duplicado 8D")
                table[key]=finite(float(row["temperatura_c"]))
        if len(table)!=len(SITES)*360:raise ValueError("Referencia 8D sin 360 meses por localidad")
    return table

def monthly_series(payload,selection,start,end):
    grouped={}
    for site,p in check_payload(payload,selection,start,end).items():
        dates=p["daily"]["time"]
        vals=p["daily"]["temperature_2m_mean"]
        last=None
        curr=[]
        for dt,val in zip(dates,vals):
            mon=dt[:7]
            if last is not None and last!=mon:
                grouped[(site,last)]=sum(curr)/len(curr)
                curr=[]
            curr.append(finite(val))
            last=mon
        if curr:grouped[(site,last)]=sum(curr)/len(curr)
    return grouped

def load_all(root):
    sources={}
    for method in SELECTIONS:
        for start,end in BLOCKS:
            pair=source_bytes(root,method,start,end)
            if pair is None:continue
            sources[(method,start,end)]=pair
    if not sources:return None
    if len(sources)!=len(SELECTIONS)*len(BLOCKS):
        raise ValueError("Archivo incompleto de seis fuentes: NO calcular ni imputar")
    return sources

def round5(x):
    return round(x,5) if x is not None else None

def evaluate(root):
    original=read_8d(root)
    sources=load_all(root)
    report={
      "fase":"8L","tipo":"sensibilidad_historica_seleccion_de_celda",
      "periodo_referencia":"1996–2025","normal_omm_comparativa":"1991–2020 (no calculada en esta fase)",
      "variable":"temperatura media diaria del aire a 2 m, agregada por mes (°C)",
      "fuente":"Open-Meteo Historical Weather API, ERA5-Land, cell_selection land/nearest",
      "criterios":["land","nearest"],
      "n_localidades":len(SITES),"meses_por_localidad_esperados":360,
      "meses_pareados_por_localidad":0,
      "n_pares_mensuales":0,"n_consultas_por_bloques":0,
      "resultado_disponible":False,
      "independencia_instrumental_demostrada":False,
      "habilidad_prospectiva_8e_demostrada":False,
      "apto_para_alertas_niño_o_fitosanitarias":False,
      "celdas_8d_originales_inequivocamente_identificadas":False,
      "parametro_elevacion_fijado":False,
      "metodos":{"land":"celda en tierra próxima y elevación semejante",
                 "nearest":"celda más cercana independientemente de preferencia terrestre"},
      "interpretacion":"Las diferencias land/nearest incluyen elección de celda y posibles efectos del ajuste del proveedor; NO equivalen a error instrumental ni impacto causal de altitud.",
      "advertencias":[
        "Solo reanálisis: nunca temperatura instrumental SENAMHI.",
        "ERA5-Land es 0,1° regular en CDS; la API tiene lógica adicional de selección y elevación, no es un muestreo raster CDS puro.",
        "Los metadatos de celda originales de 8D no quedaron archivados; comparar 8L con 8D es una auditoría retrospectiva descriptiva.",
        "Cada método calcula su propia normal mensual 1996–2025: una diferencia de anomalía no equivale a diferencia de temperatura absoluta.",
        "No utilizar diferencia de celda como probabilidad de El Niño o enfermedad vegetal."
      ],
      "por_localidad":{site:{"n":0,"diferencia_media_nearest_menos_land_c":None,
                             "mae_entre_selecciones_c":None,"rmse_entre_selecciones_c":None,
                             "max_abs_diferencia_c":None,"mae_diferencia_anomalias_c":None,
                             "n_meses_abs_diferencia_ge_0_5_c":None,
                             "n_meses_abs_diferencia_ge_1_0_c":None,
                             "centros_land":None,"centros_nearest":None,
                             "centros_distintos":None,"desplazamiento_centros_km":None,
                             "mae_8d_archivado_menos_land_8l_c":None}
                        for site in SITES},
      "trazabilidad":{"sha256_8d_reanalisis_archivado":hashlib.sha256((root/HIST).read_bytes()).hexdigest(),
                      "fuentes_originales":[]}
    }
    if sources is None:
        report["estado"]="pendiente_descarga_de_seis_bloques_completos"
        return report,[]
    bymethod={key:{} for key in SELECTIONS}
    centers={key:{city:set() for city in SITES} for key in SELECTIONS}
    for (method,start,end),(blob,meta) in sources.items():
        data=json.loads(blob)
        rows=monthly_series(data,method,start,end)
        for k,value in rows.items():
            if k in bymethod[method]:raise ValueError("Mes superpuesto en bloques")
            bymethod[method][k]=value
        for city,p in zip(SITES,data):
            centers[method][city].add((round(p["latitude"],6),round(p["longitude"],6)))
        report["trazabilidad"]["fuentes_originales"].append(meta)
    if any(len(v)!=len(SITES)*360 for v in bymethod.values()):
        raise ValueError("Serie climática incompleta: se requieren 360 meses por localidad")
    for city in SITES:
        for method in SELECTIONS:
            if len(centers[method][city])!=1:
                raise ValueError("Centro de celda cambia entre bloques: "+city+"/"+method)
    normals={}
    for method in SELECTIONS:
        for city in SITES:
            for m in range(1,13):
                values=[v for (site,mon),v in bymethod[method].items()
                        if site==city and int(mon[5:])==m]
                if len(values)!=30:raise ValueError("Normal 1996–2025 sin treinta años completos")
                normals[(method,city,m)]=st.mean(values)
    monthly=[]
    for city in SITES:
        for year in range(1996,2026):
            for m in range(1,13):
                mon=f"{year}-{m:02d}"
                land=bymethod["land"][(city,mon)]
                near=bymethod["nearest"][(city,mon)]
                normal_land=normals[("land",city,m)]
                normal_near=normals[("nearest",city,m)]
                record={
                   "localidad":city,"mes":mon,
                   "tmedia_land_c":round5(land),
                   "tmedia_nearest_c":round5(near),
                   "diferencia_nearest_menos_land_c":round5(near-land),
                   "anomalia_land_c":round5(land-normal_land),
                   "anomalia_nearest_c":round5(near-normal_near),
                   "diferencia_anomalias_c":round5((near-normal_near)-(land-normal_land)),
                   "tmedia_era5_8d_archivada_c":round5(original[(city,mon)]),
                   "diferencia_8d_menos_land_8l_c":round5(original[(city,mon)]-land)
                }
                monthly.append(record)
        selected=[r for r in monthly if r["localidad"]==city]
        diff=[r["diferencia_nearest_menos_land_c"] for r in selected]
        anom=[r["diferencia_anomalias_c"] for r in selected]
        hist=[r["diferencia_8d_menos_land_8l_c"] for r in selected]
        centerland=next(iter(centers["land"][city]))
        centernear=next(iter(centers["nearest"][city]))
        dist=haversine(*centerland,*centernear)
        report["por_localidad"][city]={
          "n":360,"diferencia_media_nearest_menos_land_c":round5(st.mean(diff)),
          "mae_entre_selecciones_c":round5(st.mean(abs(d) for d in diff)),
          "rmse_entre_selecciones_c":round5(math.sqrt(st.mean(d*d for d in diff))),
          "max_abs_diferencia_c":round5(max(abs(d) for d in diff)),
          "mae_diferencia_anomalias_c":round5(st.mean(abs(d) for d in anom)),
          "n_meses_abs_diferencia_ge_0_5_c":sum(abs(d)>=0.5 for d in diff),
          "n_meses_abs_diferencia_ge_1_0_c":sum(abs(d)>=1 for d in diff),
          "centros_land":list(centerland),"centros_nearest":list(centernear),
          "centros_distintos":centerland!=centernear,
          "desplazamiento_centros_km":round5(dist),
          "mae_8d_archivado_menos_land_8l_c":round5(st.mean(abs(d) for d in hist))
        }
    report["estado"]="comparacion_descriptiva_360_meses_completos"
    report["resultado_disponible"]=True
    report["meses_pareados_por_localidad"]=360
    report["n_pares_mensuales"]=len(monthly)
    report["n_consultas_por_bloques"]=len(sources)
    report["trazabilidad"]["fuentes_originales"].sort(key=lambda x:(x["selection"],x["start"]))
    return report,monthly

def haversine(lat1,lon1,lat2,lon2):
    p=math.pi/180
    a=math.sin((lat2-lat1)*p/2)**2+math.cos(lat1*p)*math.cos(lat2*p)*math.sin((lon2-lon1)*p/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(a)))

def outputs(root,check=False):
    report,rows=evaluate(root)
    out=root/OUTPUT
    f=io.StringIO(newline="")
    writer=csv.DictWriter(f,fieldnames=MONTH_FIELDS,lineterminator="\n")
    writer.writeheader()
    for row in rows:writer.writerow({name:row[name] for name in MONTH_FIELDS})
    targets={
      out/"estado_8l.json":json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
      out/"pares_mensuales_8l.csv":f.getvalue()
    }
    if not check:out.mkdir(parents=True,exist_ok=True)
    for path,content in targets.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("Salida histórica 8L desactualizada: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8L","estado":report["estado"],
       "meses_pareados":report["n_pares_mensuales"],"check":check},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--fetch",action="store_true")
    parser.add_argument("--refresh",action="store_true")
    parser.add_argument("--check",action="store_true")
    opt=parser.parse_args()
    if opt.fetch:fetch_all(opt.root,refresh=opt.refresh)
    outputs(opt.root,check=opt.check)
