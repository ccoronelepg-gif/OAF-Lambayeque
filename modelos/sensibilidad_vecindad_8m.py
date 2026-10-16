#!/usr/bin/env python3
"""OAF-Lambayeque 8M: sensibilidad histórica espacial ERA5-Land/Open-Meteo.

Diseño ex ante: 9 puntos por localidad (centro + 8 rumbos, ±0.05°),
cuatro localidades, 3 bloques decenales (1996–2025) = 12 consultas API.
Conservar respuestas JSON completas comprimidas y metadatos SHA-256.
La selección 'land' y el ajuste de elevación predeterminado del proveedor
se mantienen constantes. Esto NO aísla un efecto causal de orografía.
No usa datos instrumentales SENAMHI ni prueba capacidad prospectiva 8E.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import statistics
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INPUT = "datos/fuentes_vecindad_8m"
OUTPUT = "datos/sensibilidad_vecindad_8m"
REFERENCE = "datos/sensibilidad_celdas_8l/pares_mensuales_8l.csv"
SITES = {
    "Chiclayo": (-6.77140, -79.84090),
    "Jayanca": (-6.39278, -79.82280),
    "Motupe": (-6.15083, -79.71420),
    "Olmos": (-5.98825, -79.74723),
}
OFFSETS = {
    "C": (0.0, 0.0),
    "N": (0.05, 0.0), "S": (-0.05, 0.0),
    "E": (0.0, 0.05), "W": (0.0, -0.05),
    "NE": (0.05, 0.05), "NW": (0.05, -0.05),
    "SE": (-0.05, 0.05), "SW": (-0.05, -0.05),
}
BLOCKS = ((1996, 2005), (2006, 2015), (2016, 2025))
API = "https://archive-api.open-meteo.com/v1/archive"
DOCS = "https://open-meteo.com/en/docs/historical-weather-api"
PAIR_FIELDS = ("localidad", "direccion", "mes", "tmedia_c", "tmedia_centro_c",
               "delta_tmedia_c", "anomalia_c", "anomalia_centro_c",
               "delta_anomalia_c", "centro_celda_distinto")
POINT_FIELDS = ("localidad", "direccion", "latitud_solicitada", "longitud_solicitada",
                "distancia_solicitud_centro_km", "latitud_celda_devuelta",
                "longitud_celda_devuelta", "distancia_celda_base_km",
                "elevacion_reportada_api_m", "delta_elevacion_api_vs_centro_m",
                "celda_distinta", "n_meses", "delta_tmedia_promedio_c",
                "mae_tmedia_c", "rmse_tmedia_c", "max_abs_delta_c",
                "mae_diferencia_anomalias_c", "n_meses_abs_delta_ge_0_5_c",
                "n_meses_abs_delta_ge_1_c", "interpretacion")

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def round5(x):
    return round(x, 5) if x is not None else None

def finite(x):
    if type(x) not in (float, int) or not math.isfinite(x) or not -40 < x < 55:
        raise ValueError("Temperatura inexistente o fuera de rango físico")
    return float(x)

def haversine(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c-a)*p/2)**2 + math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 6371.0088*2*math.asin(min(1, math.sqrt(x)))

def locations(city):
    lat,lon=SITES[city]
    return [(key, (round(lat+dlat, 5), round(lon+dlon, 5)))
            for key,(dlat,dlon) in OFFSETS.items()]

def build_url(city, start, end):
    pts=locations(city)
    args={
        "latitude":",".join(str(lat) for _,(lat,lon) in pts),
        "longitude":",".join(str(lon) for _,(lat,lon) in pts),
        "start_date":f"{start}-01-01", "end_date":f"{end}-12-31",
        "timezone":"America/Lima", "daily":"temperature_2m_mean",
        "models":"era5_land", "cell_selection":"land"
    }
    return API+"?"+urlencode(args)

def calendar_dates(start,end):
    a=date(start,1,1);b=date(end,12,31)
    return [(a+timedelta(days=i)).isoformat() for i in range((b-a).days+1)]

def source_path(root,city,start,end):
    return root/INPUT/f"{city.lower()}_{start}_{end}.json.gz"

def meta_path(root,city,start,end):
    return root/INPUT/f"{city.lower()}_{start}_{end}.meta.json"

def validate_payload(payload,city,start,end):
    if type(payload) is not list or len(payload)!=len(OFFSETS):
        raise ValueError("Se esperaban 9 respuestas independientes: "+city)
    dates=calendar_dates(start,end)
    for (key,requested),p in zip(locations(city),payload):
        if not isinstance(p,dict) or p.get("error") or p.get("timezone")!="America/Lima" or p.get("utc_offset_seconds")!=-18000:
            raise ValueError("API respondió zona horaria o estado incompatible: "+city+"/"+key)
        daily=p.get("daily",{})
        if daily.get("time")!=dates or type(daily.get("temperature_2m_mean")) is not list or len(daily["temperature_2m_mean"])!=len(dates):
            raise ValueError("Días faltantes, duplicados o desplazados: "+city+"/"+key)
        for n in daily["temperature_2m_mean"]:finite(n)
        for tag in ("latitude","longitude","elevation"):
            v=p.get(tag)
            if type(v) not in (float,int) or not math.isfinite(v):
                raise ValueError("Coordenada/elevación no finita del proveedor")
        got=(float(p["latitude"]),float(p["longitude"]))
        if abs(got[0]-requested[0])>0.35 or abs(got[1]-requested[1])>0.35:
            raise ValueError("Celda excesivamente distante del punto solicitado")
        if abs(got[0])>90 or abs(got[1])>180 or not -500<=p["elevation"]<=7000:
            raise ValueError("Geografía reportada fuera de rango")
    return payload

def validate_raw(raw,metadata,city,start,end):
    if (metadata.get("fase")!="8M" or metadata.get("ciudad")!=city or
        metadata.get("periodo")!=[start,end] or
        metadata.get("url")!=build_url(city,start,end) or
        metadata.get("sha256_respuesta_original")!=sha(raw) or
        metadata.get("variable")!="temperature_2m_mean" or
        metadata.get("modelo")!="era5_land" or
        metadata.get("seleccion")!="land" or
        metadata.get("ajuste_elevacion")!="valor_predeterminado_openmeteo_90m" or
        metadata.get("sin_validacion_instrumental") is not True):
        raise ValueError("Datos originales y metadatos SHA/URL incompatibles")
    return validate_payload(json.loads(raw),city,start,end)

def source(root,city,start,end):
    p=source_path(root,city,start,end)
    m=meta_path(root,city,start,end)
    if not p.exists() and not m.exists():return None
    if not p.exists() or not m.exists():raise ValueError("Fuente parcial: "+str(p))
    blob=gzip.decompress(p.read_bytes())
    if len(blob)>16_000_000:raise ValueError("Respuesta original excesiva")
    metadata=json.loads(m.read_text(encoding="utf-8"))
    return validate_raw(blob,metadata,city,start,end),metadata

def api_get(url):
    last=None
    for i in range(3):
        try:
            with urlopen(Request(url,headers={
                "User-Agent":"OAF-Lambayeque-8M-research/1.0",
                "Accept":"application/json"}), timeout=110) as r:
                if r.status!=200:raise ValueError("HTTP "+str(r.status))
                raw=r.read(16_000_001)
            if len(raw)>16_000_000:raise ValueError("Respuesta muy grande")
            return raw
        except HTTPError as exc:
            if exc.code==429:
                raise RuntimeError("HTTP 429: Open-Meteo limita nuevas solicitudes. Conservar lo archivado y continuar después.") from exc
            last=exc
            if i<2:time.sleep((i+1)*6)
        except (URLError,TimeoutError,OSError,ValueError) as exc:
            last=exc
            if i<2:time.sleep((i+1)*6)
    raise RuntimeError("Proveedor no disponible: "+str(last))

def capture(root,refresh=False,max_new_blocks=2):
    if not 1<=max_new_blocks<=len(SITES)*len(BLOCKS):
        raise ValueError("Número de bloques nuevos por ejecución fuera del diseño")
    if refresh and max_new_blocks!=len(SITES)*len(BLOCKS):
        raise ValueError("Un refresh del estudio requiere los doce bloques en la misma ejecución")
    allkeys=[(city,start,end) for city in SITES for start,end in BLOCKS]
    existing=[source(root,*key) for key in allkeys]
    if all(x is not None for x in existing) and not refresh:
        print("Las doce fuentes originales 8M están verificadas; no se actualizan.")
        return
    # En reanudaciones no repetir consultas y datos ya comprobados, salvo refresh.
    # No publicar NINGUNA métrica mientras falte una fuente.
    rootdir=root/INPUT
    rootdir.mkdir(parents=True,exist_ok=True)
    downloaded=0
    for (city,start,end),old in zip(allkeys,existing):
        if old is not None and not refresh:continue
        if downloaded>=max_new_blocks:
            print("Límite conservador de consultas alcanzado; conservar bloques válidos y reanudar en otro ciclo.",flush=True)
            break
        url=build_url(city,start,end)
        raw=api_get(url)
        validate_payload(json.loads(raw),city,start,end)
        metadata={
            "fase":"8M", "ciudad":city,"periodo":[start,end],
            "url":url,"sha256_respuesta_original":sha(raw),
            "consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "variable":"temperature_2m_mean","modelo":"era5_land","seleccion":"land",
            "ajuste_elevacion":"valor_predeterminado_openmeteo_90m",
            "sin_validacion_instrumental":True,"documentacion":DOCS
        }
        # Almacenar solamente tras validar la integridad completa de un bloque.
        source_path(root,city,start,end).write_bytes(gzip.compress(raw,mtime=0))
        meta_path(root,city,start,end).write_text(
            json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        downloaded+=1
        print("Archivo validado:",city,start,end,
              "- nuevos en este ciclo:",downloaded,flush=True)

def load_reference(root):
    with (root/REFERENCE).open(encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        if not rdr.fieldnames or not {"localidad","mes","tmedia_land_c"}.issubset(rdr.fieldnames):
            raise ValueError("Referencia 8L sin campos suficientes")
        out={}
        for r in rdr:
            if r["localidad"] not in SITES:raise ValueError("Localidad 8L desconocida")
            key=(r["localidad"],r["mes"])
            if key in out:raise ValueError("Referencia 8L duplicada")
            out[key]=finite(float(r["tmedia_land_c"]))
    if len(out)!=len(SITES)*360:
        raise ValueError("Referencia 8L incompleta: se exigen 360 meses por localidad")
    return out

def reduce_months(p):
    dates=p["daily"]["time"]
    temps=p["daily"]["temperature_2m_mean"]
    months={}
    for d,t in zip(dates,temps):
        month=d[:7]
        months.setdefault(month,[]).append(finite(t))
    return {month:statistics.mean(values) for month,values in months.items()}

def report_template(root):
    return {
        "fase":"8M","estado":"pendiente_de_fuentes_historicas_completas",
        "objetivo":"Sensibilidad al desplazamiento espacial de puntos de consulta, no habilidad predictiva",
        "periodo":"1996–2025",
        "fuente":"ERA5-Land mediante API histórica Open-Meteo, seleccion land",
        "diseño":"Centro + ocho direcciones ±0,05° lat/lon (NO son parcelas ni sensores)",
        "puntos_por_localidad":9,"localidades":list(SITES),
        "meses_por_punto":360,"n_puntos_esperados":36,
        "n_pares_mensuales_esperados":8*4*360,
        "n_pares_mensuales_comparados":0,
        "resultados_disponibles":False,
        "localidades_con_periodo_completo":[],
        "bloques_presentes":0,
        "celdas_originales_8d_certificadas":False,
        "validacion_instrumental":False,"habilidad_prospectiva_8e_demostrada":False,
        "alerta_enfen_senamhi_o_fitosanitaria":False,
        "ajuste_elevacion_desactivado":False,
        "no_es_efecto_causal_aislado_de_altitud":True,
        "nodos_y_coordenadas_son_puntos_de_ensayo":True,
        "no_confundir": [
          "Las diferencias incorporan selección de píxel y ajuste estadístico de elevación predeterminado; no son sesgo instrumental.",
          "Temperaturas de reanálisis no son sensores SENAMHI ni mediciones de parcelas de arándano y vid.",
          "Una variación descriptiva de 0,5 o 1 °C no establece enfermedad, El Niño ni aviso operativo.",
          "Las anomalías por cada punto se centran en su propia normal 1996–2025.",
          "Los ocho rumbos son desplazamientos angulares ±0,05° (no distancia métrica exactamente igual)."
        ],
        "por_localidad":{city:{"n_puntos":0,"n_vecinos_con_celda_distinta":None,
              "n_vecinos_misma_celda":None,"max_mae_tmedia_c":None,
              "max_diferencia_mensual_absoluta_c":None,
              "max_mae_diferencia_anomalias_c":None,
              "max_distancia_centro_celda_km":None} for city in SITES},
        "trazabilidad":{"referencia_8l_sha256":hashlib.sha256((root/REFERENCE).read_bytes()).hexdigest(),
                        "fuentes":[]}
    }

def evaluate(root):
    baseline=load_reference(root)
    rep=report_template(root)
    sources={}
    for city in SITES:
        for start,end in BLOCKS:
            item=source(root,city,start,end)
            if item:sources[(city,start,end)]=item
    if not sources:return rep,[],[]
    complete_cities=[city for city in SITES
                     if all((city,start,end) in sources for start,end in BLOCKS)]
    rep["bloques_presentes"]=len(sources)
    rep["localidades_con_periodo_completo"]=complete_cities
    if not complete_cities:
        rep["estado"]="fuentes_parciales_sin_localidades_con_30_anios"
        return rep,[],[]
    pairs=[]
    points=[]
    for city in complete_cities:
        bypoint={direction:{} for direction in OFFSETS}
        centers={direction:set() for direction in OFFSETS}
        elevations={direction:set() for direction in OFFSETS}
        for start,end in BLOCKS:
            payload,meta=sources[(city,start,end)]
            rep["trazabilidad"]["fuentes"].append(meta)
            for (direction,xy),p in zip(locations(city),payload):
                monthly=reduce_months(p)
                if len(monthly)!=(end-start+1)*12:
                    raise ValueError("Cobertura mensual del bloque incorrecta")
                for month,val in monthly.items():
                    if month in bypoint[direction]:raise ValueError("Bloques mensuales superpuestos")
                    bypoint[direction][month]=val
                centers[direction].add((round(p["latitude"],6),round(p["longitude"],6)))
                elevations[direction].add(round(p["elevation"],2))
        for direction in OFFSETS:
            if len(bypoint[direction])!=360 or len(centers[direction])!=1 or len(elevations[direction])!=1:
                raise ValueError("Serie, centro o elevación cambian entre los tres bloques: "+city+"/"+direction)
        for month,value in bypoint["C"].items():
            if abs(value-baseline[(city,month)])>0.00003:
                raise ValueError("Punto central 8M no reproduce archivo 8L: "+city+"/"+month)
        normals={}
        for direction,values in bypoint.items():
            for m in range(1,13):
                month_values=[v for month,v in values.items() if int(month[-2:])==m]
                if len(month_values)!=30:
                    raise ValueError("Normal mensual incompleta 1996–2025")
                normals[(direction,m)]=statistics.mean(month_values)
        center_cell=next(iter(centers["C"]))
        center_elevation=next(iter(elevations["C"]))
        city_points=[]
        for direction,xy in locations(city):
            c=next(iter(centers[direction]))
            elev=next(iter(elevations[direction]))
            different=c!=center_cell
            delta=[]
            anomaly_delta=[]
            for month in sorted(bypoint[direction]):
                v=bypoint[direction][month]
                base=bypoint["C"][month]
                m=int(month[-2:])
                change=v-base
                anom=(v-normals[(direction,m)])
                anom_base=base-normals[("C",m)]
                difference=anom-anom_base
                if direction!="C":
                    pairs.append({
                        "localidad":city,"direccion":direction,"mes":month,
                        "tmedia_c":round5(v),"tmedia_centro_c":round5(base),
                        "delta_tmedia_c":round5(change),
                        "anomalia_c":round5(anom),
                        "anomalia_centro_c":round5(anom_base),
                        "delta_anomalia_c":round5(difference),
                        "centro_celda_distinto":different
                    })
                delta.append(change)
                anomaly_delta.append(difference)
            info={
                "localidad":city,"direccion":direction,
                "latitud_solicitada":xy[0],"longitud_solicitada":xy[1],
                "distancia_solicitud_centro_km":round5(haversine(*xy,*SITES[city])),
                "latitud_celda_devuelta":c[0],"longitud_celda_devuelta":c[1],
                "distancia_celda_base_km":round5(haversine(*c,*center_cell)),
                "elevacion_reportada_api_m":elev,
                "delta_elevacion_api_vs_centro_m":round5(elev-center_elevation),
                "celda_distinta":different,
                "n_meses":360,
                "delta_tmedia_promedio_c":round5(statistics.mean(delta)),
                "mae_tmedia_c":round5(statistics.mean(abs(x) for x in delta)),
                "rmse_tmedia_c":round5(math.sqrt(statistics.mean(x*x for x in delta))),
                "max_abs_delta_c":round5(max(abs(x) for x in delta)),
                "mae_diferencia_anomalias_c":round5(statistics.mean(abs(x) for x in anomaly_delta)),
                "n_meses_abs_delta_ge_0_5_c":sum(abs(x)>=.5 for x in delta),
                "n_meses_abs_delta_ge_1_c":sum(abs(x)>=1 for x in delta),
                "interpretacion":"comparacion_descriptiva_sin_validacion_instrumental"
            }
            points.append(info)
            if direction!="C":city_points.append(info)
        rep["por_localidad"][city]={
            "n_puntos":9,
            "n_vecinos_con_celda_distinta":sum(p["celda_distinta"] for p in city_points),
            "n_vecinos_misma_celda":sum(not p["celda_distinta"] for p in city_points),
            "max_mae_tmedia_c":round5(max(p["mae_tmedia_c"] for p in city_points)),
            "max_diferencia_mensual_absoluta_c":round5(max(p["max_abs_delta_c"] for p in city_points)),
            "max_mae_diferencia_anomalias_c":round5(max(p["mae_diferencia_anomalias_c"] for p in city_points)),
            "max_distancia_centro_celda_km":round5(max(p["distancia_celda_base_km"] for p in city_points))
        }
    if len(points)!=9*len(complete_cities) or len(pairs)!=8*360*len(complete_cities):
        raise ValueError("Matriz por localidad completa inconsistente (9 puntos, 2880 pares)")
    complete=len(complete_cities)==len(SITES)
    rep["estado"]=("sensibilidad_espacial_completa_1996_2025" if complete
                   else "localidades_completas_regional_pendiente")
    # Cada localidad publicada posee sus 360 meses. Los indicadores regionales
    # SOLO se marcarán completos cuando estén las cuatro localidades.
    rep["resultados_disponibles"]=complete
    rep["n_pares_mensuales_comparados"]=len(pairs)
    rep["trazabilidad"]["fuentes"].sort(key=lambda v:(v["ciudad"],v["periodo"][0]))
    return rep,points,pairs

def csv_data(rows,fields):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k:str(row[k]).lower() if isinstance(row[k],bool) else row[k] for k in fields})
    return out.getvalue()

def publish(root,check=False):
    report,points,pairs=evaluate(root)
    directory=root/OUTPUT
    files={
        directory/"estado_8m.json":json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
        directory/"puntos_8m.csv":csv_data(points,POINT_FIELDS),
        directory/"pares_mensuales_8m.csv":csv_data(pairs,PAIR_FIELDS),
        directory/"vista_8m.json":json.dumps({"fase":"8M","estado":report["estado"],
            "resultados_disponibles":report["resultados_disponibles"],
            "localidades_con_periodo_completo":report["localidades_con_periodo_completo"],
            "bloques_presentes":report["bloques_presentes"],
            "por_localidad":report["por_localidad"],"puntos":points,
            "n_pares_mensuales":len(pairs),"no_validacion_instrumental":True,
            "no_habilidad_predictiva_demostrada":True},
            ensure_ascii=False,indent=2,allow_nan=False)+"\n"
    }
    if not check:directory.mkdir(parents=True,exist_ok=True)
    for path,data in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=data:
                raise ValueError("Salida de fase 8M no corresponde a fuentes inmutables: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=data:
            path.write_text(data,encoding="utf-8")
    print(json.dumps({"fase":"8M","estado":report["estado"],
        "puntos":len(points),"pares_mensuales_vecino_centro":len(pairs),
        "check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--check",action="store_true")
    p.add_argument("--refresh",action="store_true")
    p.add_argument("--max-new-blocks",type=int,default=2,
                   help="Protección del proveedor: máximo dos solicitudes nuevas por ejecución")
    a=p.parse_args()
    if a.fetch:capture(a.root,refresh=a.refresh,max_new_blocks=a.max_new_blocks)
    publish(a.root,check=a.check)
