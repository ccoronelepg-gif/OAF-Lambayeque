#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9H - contraste retrospectivo de lluvia, 2 coordenadas por estación.
1996–2013 ERA5-Land vía Open-Meteo archive; CHIRPS v3 mensual LATAM, 1998.
No es una validación operativa de pronóstico, ni validación independiente CHIRPS.
La identidad nominal de 9F es corroborada, pero los emplazamientos históricos
siguen sin certificación. Datos ausentes nunca se imputan.
"""
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
GEO=ROOT/"datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json"
OBS=ROOT/"datos/estaciones_9d/series_mensuales_9d.csv"
DEST=ROOT/"datos/validacion_estaciones_9h"
OUT=DEST/"comparacion_observacional_9h.json"
CSV_OUT=DEST/"pares_mensuales_9h.csv"
ERA_URL="https://archive-api.open-meteo.com/v1/archive"
CHIRPS_URL="https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
FIELDS=["codigo_archivo","nombre","escenario","producto","mes","precipitacion_estacion_mm",
        "precipitacion_producto_mm","diferencia_producto_menos_estacion_mm",
        "latitud_consulta","longitud_consulta","latitud_celda","longitud_celda",
        "distancia_celda_km","fuente_url","sha256_respuesta"]
EXPECTED=[f"{yr}-{mo:02d}" for yr in range(1996,2014) for mo in range(1,13)]
CHIRPS_MONTHS=[f"1998-{m:02d}" for m in range(1,13)]

def distance(a,b):
    y1,x1=map(math.radians,a);y2,x2=map(math.radians,b)
    val=math.sin((y2-y1)/2)**2+math.cos(y1)*math.cos(y2)*math.sin((x2-x1)/2)**2
    return round(2*6371.0088*math.asin(min(1,math.sqrt(val))),3)

def catalog():
    j=json.loads(GEO.read_text(encoding="utf8"))
    if j["fase"]!="9G" or j["ubicacion_sensor_1963_2014_certificada"] is not False:
        raise ValueError("El catálogo geográfico no conserva advertencia 9G")
    points=[]
    for station in j["estaciones"]:
        for idx in (1,2):
            p=station[f"coordenada_documental_{idx}"]
            point={"codigo_archivo":station["codigo_archivo"],
                   "nombre":station["nombre"],"escenario":f"documental_{idx}",
                   "lat":float(p["lat"]),"lon":float(p["lon"]),
                   "fuente_documental":p["url"]}
            if not (-19<=point["lat"]<=-3 and -83<=point["lon"]<=-68):
                raise ValueError("Punto fuera de dominio geográfico documentado")
            points.append(point)
    if len(points)!=6 or len(set((p["codigo_archivo"],p["escenario"]) for p in points))!=6:
        raise ValueError("Se esperan seis emplazamientos documentales únicos")
    return points

def station_months():
    stations={}
    with OBS.open(encoding="utf8",newline="") as f:
        for r in csv.DictReader(f):
            if r["mes"] not in EXPECTED:continue
            key=(r["codigo"],r["mes"])
            if key in stations:raise ValueError("Mes estación duplicado "+str(key))
            days=calendar.monthrange(*map(int,r["mes"].split("-")))[1]
            good=(int(r["dias_calendario"])==days and
                  int(r["precip_dias_validos"])==days and
                  r["precip_total_mm"] not in ("",None))
            stations[key]=round(float(r["precip_total_mm"]),4) if good else None
    return stations

def fresh_bytes(url,attempts=2):
    import requests
    err=""
    for i in range(attempts):
        try:
            r=requests.get(url,timeout=(16,85),headers={"User-Agent":"OAF-Lambayeque-9H-scientific-archive/1.0",
              "Accept":"application/json, image/tiff, */*"})
            r.raise_for_status()
            if len(r.content)<100:
                raise ValueError("Respuesta demasiado pequeña o vacía")
            return r.content
        except Exception as e:
            err=f"{type(e).__name__}: {e}"
            if i+1<attempts:time.sleep(1.5*(i+1))
    raise RuntimeError(err[:500])

def hash_bytes(raw):return hashlib.sha256(raw).hexdigest()

def archive_era(points):
    import requests
    # Periodos grandes en solo dos lotes; coordenadas múltiples son soportadas
    # por la API documentada de Open-Meteo. Los centros son los *retornados*.
    source=[]
    series=defaultdict(dict)
    centers={}
    api_meta={}
    for start,end in [("1996-01-01","2005-12-31"),("2006-01-01","2013-12-31")]:
        params={
          "latitude":",".join(str(p["lat"]) for p in points),
          "longitude":",".join(str(p["lon"]) for p in points),
          "start_date":start,"end_date":end,"timezone":"America/Lima",
          "daily":"precipitation_sum","models":"era5_land","cell_selection":"land"
        }
        url=ERA_URL+"?"+urlencode(params)
        raw=fresh_bytes(url)
        digest=hash_bytes(raw)
        contents=json.loads(raw.decode("utf8"))
        if not isinstance(contents,list) or len(contents)!=6:
            raise ValueError("La API ERA5-Land no devolvió los seis puntos")
        for i,obj in enumerate(contents):
            if obj.get("error"):raise ValueError("ERA5 API: "+str(obj.get("reason")))
            daily=obj.get("daily") or {}
            dates=daily.get("time");values=daily.get("precipitation_sum")
            if not dates or len(dates)!=len(values or []):
                raise ValueError("ERA5 API: fecha/lluvia inconsistente")
            units=(obj.get("daily_units") or {}).get("precipitation_sum")
            if units!="mm":raise ValueError("ERA5 units not mm: "+str(units))
            lat=float(obj["latitude"]);lon=float(obj["longitude"])
            coord=(lat,lon)
            if i in centers and distance(centers[i],coord)>0.01:
                raise ValueError("Centro grilla cambió entre periodos")
            centers[i]=coord
            # Restricción conservadora: el reanálisis se asigna a una celda
            # próxima, pero no valida el emplazamiento de la estación.
            if distance((points[i]["lat"],points[i]["lon"]),coord)>18:
                raise ValueError("Celda ERA5-Land demasiado distante: "+str(coord))
            accum=defaultdict(list)
            dates_seen=set()
            for day,value in zip(dates,values):
                if day in dates_seen:raise ValueError("Día duplicado ERA5")
                dates_seen.add(day)
                month=day[:7]
                if month not in EXPECTED:raise ValueError("Mes ajeno a petición")
                accum[month].append((day,value))
            for month,rows in accum.items():
                year,num=map(int,month.split("-"))
                calendar_days=calendar.monthrange(year,num)[1]
                ordered=[d for d,v in rows]
                if len(rows)!=calendar_days or len(set(ordered))!=calendar_days or any(
                  not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for d,v in rows
                ): continue
                amount=round(sum(v for d,v in rows),4)
                if month in series[i]:raise ValueError("Mes duplicado por lotes")
                series[i][month]={"mm":amount,"sha256":digest,"url":url}
            api_meta[i]={"lat":lat,"lon":lon,
                         "elevation_grilla_m":obj.get("elevation"),
                         "timezone":obj.get("timezone"),"rain_unit":units}
        source.append({"producto":"ERA5-Land vía Open-Meteo","periodo":f"{start}/{end}",
                       "url":url,"sha256":digest,"bytes_recibidos":len(raw),
                       "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(),
                       "respuesta_celdas":len(contents)})
    return series,api_meta,source

def archive_chirps(points):
    import rasterio
    from rasterio.io import MemoryFile
    series=defaultdict(dict)
    centers={}
    source=[]
    for month in CHIRPS_MONTHS:
        year,m=map(int,month.split("-"))
        url=CHIRPS_URL+f"chirps-v3.0.{year}.{m:02d}.tif"
        raw=fresh_bytes(url)
        if len(raw)<100_000:raise ValueError("El TIFF de CHIRPS es demasiado pequeño")
        digest=hash_bytes(raw)
        with MemoryFile(raw) as mem:
            with mem.open() as ds:
                if not ds.crs or ds.crs.to_epsg()!=4326:
                    raise ValueError("CHIRPS TIFF CRS distinto a EPSG:4326")
                if ds.count!=1:raise ValueError("CHIRPS TIFF multibanda inesperada")
                for i,p in enumerate(points):
                    ri,ci=ds.index(p["lon"],p["lat"])
                    if ri<0 or ci<0 or ri>=ds.height or ci>=ds.width:
                        raise ValueError("Ubicación fuera del raster CHIRPS")
                    pixel=float(ds.read(1,window=((ri,ri+1),(ci,ci+1)))[0,0])
                    cell_lon,cell_lat=ds.xy(ri,ci)
                    if ds.nodata is not None and abs(pixel-ds.nodata)<1e-5:
                        continue
                    if not math.isfinite(pixel) or pixel<0:continue
                    if distance((p["lat"],p["lon"]),(cell_lat,cell_lon))>6:
                        raise ValueError("CHIRPS celda demasiado distante")
                    point=(round(cell_lat,8),round(cell_lon,8))
                    if i in centers and centers[i]!=point:raise ValueError("CHIRPS cambió centro de píxel en 1998")
                    centers[i]=point
                    series[i][month]={"mm":round(pixel,4),"sha256":digest,"url":url}
        source.append({"producto":"CHIRPS-v3 mensual LATAM","mes":month,"url":url,
                       "sha256":digest,"bytes_recibidos":len(raw),
                       "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(),
                       "tipo_producto":"CHIRPS v3 mensual latam/tifs; condición final/preliminar no certificada individualmente"})
    return series,{i:{"lat":x[0],"lon":x[1],"rain_unit":"mm"} for i,x in centers.items()},source

def metrics(pairs):
    n=len(pairs)
    if n<3:return None
    diffs=[r["model"]-r["obs"] for r in pairs]
    return {
       "n_meses":n,
       "mes_inicial":min(r["mes"] for r in pairs),
       "mes_final":max(r["mes"] for r in pairs),
       "mae_mm":round(sum(abs(x) for x in diffs)/n,3),
       "sesgo_producto_menos_estacion_mm":round(sum(diffs)/n,3),
       "rmse_mm":round(math.sqrt(sum(x*x for x in diffs)/n),3),
       "precipitacion_estacion_total_mm":round(sum(r["obs"] for r in pairs),3),
       "precipitacion_producto_total_mm":round(sum(r["model"] for r in pairs),3),
       "errores_mensuales":True,"independencia_y_calidad_original_certificadas":False
    }

def build_result(points,obs,archives,issues,sources):
    rows=[]
    result=[]
    for prod in ("ERA5-Land vía Open-Meteo","CHIRPS-v3 mensual LATAM"):
        archive=archives.get(prod)
        for i,p in enumerate(points):
            key=(prod,i)
            mes_vals=archive[0].get(i,{}) if archive else {}
            center=archive[1].get(i) if archive else None
            pairs=[]
            for month,obj in sorted(mes_vals.items()):
                value=obs.get((p["codigo_archivo"],month))
                if value is None:continue
                dist=distance((p["lat"],p["lon"]),(center["lat"],center["lon"]))
                entry={
                  "codigo_archivo":p["codigo_archivo"],"nombre":p["nombre"],
                  "escenario":p["escenario"],"producto":prod,"mes":month,
                  "precipitacion_estacion_mm":value,
                  "precipitacion_producto_mm":obj["mm"],
                  "diferencia_producto_menos_estacion_mm":round(obj["mm"]-value,4),
                  "latitud_consulta":p["lat"],"longitud_consulta":p["lon"],
                  "latitud_celda":center["lat"],"longitud_celda":center["lon"],
                  "distancia_celda_km":dist,"fuente_url":obj["url"],
                  "sha256_respuesta":obj["sha256"]}
                rows.append(entry)
                pairs.append({"mes":month,"obs":value,"model":obj["mm"]})
            all_score=metrics(pairs) if prod.startswith("ERA5") else None
            episode=metrics([r for r in pairs if r["mes"].startswith("1998-")])
            result.append({
              "producto":prod,"codigo_archivo":p["codigo_archivo"],
              "nombre":p["nombre"],"escenario":p["escenario"],
              "lat_consulta":p["lat"],"lon_consulta":p["lon"],
              "centro_celda_devuelto":center,
              "distancia_punto_centro_celda_km":distance(
                (p["lat"],p["lon"]),(center["lat"],center["lon"])) if center else None,
              "n_meses_pareados":len(pairs),
              "periodo_completo_1996_2013":all_score,
              "episodio_1998":episode,
              "estado":"comparacion_exploratoria_real_no_independiente" if pairs else "sin_datos_del_producto",
              "admisible_como_validacion_predictiva":False,
              "ubicacion_historica_sensor_certificada":False
            })
    rows=sorted(rows,key=lambda r:(r["producto"],r["codigo_archivo"],r["escenario"],r["mes"]))
    cell_sensitivity=[]
    for prod in ("ERA5-Land vía Open-Meteo","CHIRPS-v3 mensual LATAM"):
        for code in sorted(set(p["codigo_archivo"] for p in points)):
            both=[x for x in result if x["producto"]==prod and x["codigo_archivo"]==code]
            assert len(both)==2
            r1,r2=both
            x,y=r1["centro_celda_devuelto"],r2["centro_celda_devuelto"]
            same= x is not None and y is not None and distance((x["lat"],x["lon"]),(y["lat"],y["lon"]))<0.01
            name=r1["nombre"]
            pilot1=r1["episodio_1998"];pilot2=r2["episodio_1998"]
            cell_sensitivity.append({
               "nombre":name,"codigo_archivo":code,"producto":prod,
               "mismo_centro_celda_entre_escenarios":same if x and y else None,
               "centros_separados_km":distance((x["lat"],x["lon"]),(y["lat"],y["lon"])) if x and y else None,
               "n_meses_1998_escenario_1":pilot1["n_meses"] if pilot1 else 0,
               "n_meses_1998_escenario_2":pilot2["n_meses"] if pilot2 else 0,
               "diferencia_mae_1998_escenario2_menos1_mm":round(pilot2["mae_mm"]-pilot1["mae_mm"],3) if pilot1 and pilot2 else None,
               "diferencia_sesgo_1998_escenario2_menos1_mm":round(pilot2["sesgo_producto_menos_estacion_mm"]-pilot1["sesgo_producto_menos_estacion_mm"],3) if pilot1 and pilot2 else None,
               "nota":"Si un producto retorna la misma celda, dos emplazamientos no proporcionan réplicas independientes."
            })
    out={
      "fase":"9H","fecha_proceso_utc":datetime.now(timezone.utc).isoformat(),
      "objetivo":"contraste_estacion_vs_celda_en_sensibilidad_a_dos_coordenadas_documentales",
      "rango_estaciones_completas":"1996-2013",
      "era5_periodo_solicitado":"1996-01/2013-12",
      "chirps_periodo_piloto_solicitado":"1998-01/1998-12",
      "metodos":"lluvia estación solo meses con 100% de días, reanálisis Open-Meteo ERA5-Land diaria sumada por mes; CHIRPS v3 ráster mensual un píxel; no interpolación; excluye todos los meses de estación incompletos",
      "convencion_dia_pluviometrico_estacion_verificada":False,
      "emisiones_historicas_pronostico_con_vintage":False,
      "ajuste_altitud_realizado":False,
      "licencias_fuente_original_estacion_verificadas":False,
      "comparacion_chirps_independiente":False,
      "motivo_dependencia_chirps":"CHIRPS integra pluviómetros; no se ha establecido si los tres contribuyeron a la calibración/fusión del producto.",
      "identidad_estacion_9f_corroborada":True,
      "emplazamiento_historico_9g_certificado":False,
      "mae_rmse_exploratorios_solo_si_existen_pares":True,
      "habilidad_predictiva_operativa_certificada":False,
      "n_archivos_fuente_reales_con_sha256":len(sources),
      "fuentes_descargadas":sources,
      "problemas_descarga":issues,
      "resumen_por_producto_y_escenario":result,
      "sensibilidad_de_celdas":cell_sensitivity,
      "n_pares_totales":len(rows),
      "n_pares_era5":sum(x["producto"].startswith("ERA5") for x in rows),
      "n_pares_chirps":sum(x["producto"].startswith("CHIRPS") for x in rows),
      "advertencias":[
        "Dos coordenadas históricas documentales no equivalen a dos estaciones independientes.",
        "Open-Meteo expone ERA5-Land de forma interpolada/asignada a su celda elegida; el centro reportado no demuestra sensor real.",
        "Precipitación ERA5-Land procede de forzantes atmosféricos de ERA5, no de observaciones del sitio.",
        "CHIRPS v3 contiene información de pluviómetros; el contraste puede compartir datos con la estación.",
        "Convención de día pluviométrico de archivos originales no documentada; un calendario coincidente no garantiza misma ventana diaria.",
        "Los años posteriores a 2013/2014 no están presentes en los originales y no se reemplazan por reanálisis.",
        "Comparación retrospectiva de producto de grilla != validación de pronóstico emitido antes del evento."
      ]}
    return rows,out

def save(rows,out):
    DEST.mkdir(parents=True,exist_ok=True)
    with CSV_OUT.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def check():
    points=catalog()
    d=json.loads(OUT.read_text("utf8"))
    assert d["fase"]=="9H" and d["habilidad_predictiva_operativa_certificada"] is False
    assert d["emplazamiento_historico_9g_certificado"] is False
    assert d["n_archivos_fuente_reales_con_sha256"]==len(d["fuentes_descargadas"])
    assert len(d["resumen_por_producto_y_escenario"])==12
    assert len(d["sensibilidad_de_celdas"])==6
    with CSV_OUT.open(encoding="utf8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==d["n_pares_totales"]
    n_era=sum(x["producto"].startswith("ERA5") for x in rows)
    n_chirps=len(rows)-n_era
    assert n_era==d["n_pares_era5"] and n_chirps==d["n_pares_chirps"]
    permitted=set((p["codigo_archivo"],p["escenario"]) for p in points)
    assert all((r["codigo_archivo"],r["escenario"]) in permitted for r in rows)
    assert all(r["fuente_url"].startswith("https://") and len(r["sha256_respuesta"])==64 for r in rows)
    assert not len(rows) or all(float(r["distancia_celda_km"])<18 for r in rows)
    source_shas=set(x["sha256"] for x in d["fuentes_descargadas"])
    assert all(r["sha256_respuesta"] in source_shas for r in rows)
    assert len(set((r["codigo_archivo"],r["escenario"],r["producto"],r["mes"]) for r in rows))==len(rows)
    assert all(
      x["admisible_como_validacion_predictiva"] is False and not x["ubicacion_historica_sensor_certificada"]
      for x in d["resumen_por_producto_y_escenario"]
    )
    obs=station_months()
    for r in rows:
        x=obs.get((r["codigo_archivo"],r["mes"]))
        assert x is not None and abs(float(r["precipitacion_estacion_mm"])-x)<1e-6
        assert abs((float(r["precipitacion_producto_mm"])-x)-float(r["diferencia_producto_menos_estacion_mm"]))<0.0002
        if r["producto"].startswith("CHIRPS"):assert r["mes"].startswith("1998-")
    print(f"9H OK: {n_era} ERA5-Land, {n_chirps} CHIRPS, {len(source_shas)} fuentes distintas SHA-256.")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    if a.check:return check()
    points=catalog();obs=station_months();archives={};issues={};sources=[]
    for product,fn in (("ERA5-Land vía Open-Meteo",archive_era),("CHIRPS-v3 mensual LATAM",archive_chirps)):
        try:
            print("Consultando",product,flush=True)
            x=fn(points)
            archives[product]=x[:2]
            sources.extend(x[2])
        except Exception as e:
            issues[product]=f"{type(e).__name__}: {e}"[:350]
            print("9H sin fuente "+product+": "+issues[product],file=sys.stderr,flush=True)
    rows,out=build_result(points,obs,archives,issues,sources)
    save(rows,out)
    check()
    print(f"9H guardado: {out['n_pares_era5']} parejas ERA5-Land; {out['n_pares_chirps']} CHIRPS.")

if __name__=="__main__":main()
