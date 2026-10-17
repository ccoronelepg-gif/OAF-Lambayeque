#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9I: ampliar CHIRPS v3 mensual sin elegir años ni celdas por su error.
Los TIFF originales se descargan y verifican; los originales instrumentales no se modifican.
1998 permanece en 9H, por lo que no se vuelve a descargar ni duplicar.
"""
import argparse
import calendar
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from contraste_instrumental_9h import (ROOT, CHIRPS_URL, catalog, station_months,
                                     fresh_bytes, distance)

YEARS = (1996, 2002, 2007, 2011, 2013)  # preregistro; 1998 ya en 9H
BASE = ROOT / "datos/validacion_estaciones_9i"
CSV = BASE / "pares_chirps_ampliacion_9i.csv"
META = BASE / "fuentes_chirps_ampliacion_9i.json"
FIELDS = ("codigo_archivo","nombre","escenario","producto","mes",
          "precipitacion_estacion_mm","precipitacion_producto_mm",
          "diferencia_producto_menos_estacion_mm","latitud_consulta","longitud_consulta",
          "latitud_celda","longitud_celda","distancia_celda_km","fuente_url",
          "sha256_respuesta")

def extraer():
    from rasterio.io import MemoryFile
    import rasterio
    points=catalog()
    observed=station_months()
    by_source=[]
    by_rows=[]
    issues=[]
    cell={}
    for year in YEARS:
        for m in range(1,13):
            ym=f"{year}-{m:02d}"
            url=CHIRPS_URL+f"chirps-v3.0.{year}.{m:02d}.tif"
            try:
                raw=fresh_bytes(url,attempts=3)
                if len(raw)<100_000:
                    raise ValueError("GeoTIFF inesperadamente pequeño")
                sha=hashlib.sha256(raw).hexdigest()
                month_rows=[]
                with MemoryFile(raw) as mem, mem.open() as ds:
                    if ds.crs is None or ds.crs.to_epsg()!=4326 or ds.count!=1:
                        raise ValueError("EPSG o bandas inesperados")
                    if not ds.transform.is_rectilinear:
                        raise ValueError("Transformación no rectilínea")
                    for i,p in enumerate(points):
                        row,col=ds.index(p["lon"],p["lat"])
                        if not (0<=row<ds.height and 0<=col<ds.width):
                            raise ValueError("Coordenada fuera del ráster")
                        v=float(ds.read(1,window=((row,row+1),(col,col+1)))[0,0])
                        latlon=(round(ds.xy(row,col)[1],8),round(ds.xy(row,col)[0],8))
                        if i in cell and cell[i]!=latlon:
                            raise ValueError("Centro de píxel CHIRPS cambió")
                        cell[i]=latlon
                        if distance((p["lat"],p["lon"]),latlon)>6:
                            raise ValueError("Píxel inverosímil")
                        if (ds.nodata is not None and abs(v-ds.nodata)<1e-5):
                            continue
                        if not (0<=v<100000):
                            continue
                        obs=observed.get((p["codigo_archivo"],ym))
                        if obs is None:
                            continue  # solo meses instrumentales completos
                        mm=round(v,4)
                        month_rows.append({
                          "codigo_archivo":p["codigo_archivo"],"nombre":p["nombre"],
                          "escenario":p["escenario"],"producto":"CHIRPS-v3 mensual LATAM",
                          "mes":ym,"precipitacion_estacion_mm":obs,
                          "precipitacion_producto_mm":mm,
                          "diferencia_producto_menos_estacion_mm":round(mm-obs,4),
                          "latitud_consulta":p["lat"],"longitud_consulta":p["lon"],
                          "latitud_celda":latlon[0],"longitud_celda":latlon[1],
                          "distancia_celda_km":distance((p["lat"],p["lon"]),latlon),
                          "fuente_url":url,"sha256_respuesta":sha})
                by_rows.extend(month_rows)
                by_source.append({"mes":ym,"url":url,"sha256":sha,
                                  "bytes":len(raw),"n_pares":len(month_rows),
                                  "consulta_utc":datetime.now(timezone.utc).isoformat(),
                                  "formato":"GeoTIFF mensual v3 LATAM, EPSG:4326"})
            except Exception as exc:
                issues.append({"mes":ym,"error":f"{type(exc).__name__}: {exc}"[:400]})
                print(f"Pendiente {ym}: {issues[-1]['error']}",flush=True)
    BASE.mkdir(parents=True,exist_ok=True)
    by_rows.sort(key=lambda r:(r["mes"],r["codigo_archivo"],r["escenario"]))
    with CSV.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(by_rows)
    report={
      "fase":"9I","producto":"CHIRPS v3 mensual LATAM",
      "anios_prespecificados":[1996,1998,2002,2007,2011,2013],
      "anios_descarga_nueva":list(YEARS),
      "anio_1998_reutiliza_9h":True,
      "metodo":"un pixel por coordenada documental; solo meses con observacion diaria al 100 por ciento",
      "fuentes":by_source,"problemas":issues,
      "meses_tiff_exitosos":len(by_source),
      "meses_tiff_solicitados":len(YEARS)*12,
      "pares_adicionales":len(by_rows),
      "filas_sin_observacion_no_imputadas":True,
      "independencia_chirps_certificada":False,
      "ubicacion_historica_certificada":False,
      "capacidad_predictiva_certificada":False,
      "nota":"La cantidad de pares duplica registros por hipótesis de ubicación; no son replicas independientes."
    }
    META.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    return report

def comprobar():
    meta=json.loads(META.read_text(encoding="utf8"))
    with CSV.open(newline="",encoding="utf8") as f: rows=list(csv.DictReader(f))
    assert meta["fase"]=="9I"
    assert meta["anios_descarga_nueva"]==list(YEARS)
    assert meta["meses_tiff_exitosos"]+len(meta["problemas"])==60
    assert meta["pares_adicionales"]==len(rows)
    assert not meta["independencia_chirps_certificada"]
    assert not meta["capacidad_predictiva_certificada"]
    shas={x["mes"]:x["sha256"] for x in meta["fuentes"]}
    assert len(shas)==meta["meses_tiff_exitosos"]
    assert len(set((r["mes"],r["codigo_archivo"],r["escenario"]) for r in rows))==len(rows)
    for r in rows:
        assert r["mes"][:4] in {str(y) for y in YEARS}
        assert r["sha256_respuesta"]==shas[r["mes"]]
        assert abs(float(r["precipitacion_producto_mm"])-float(r["precipitacion_estacion_mm"])-
                  float(r["diferencia_producto_menos_estacion_mm"]))<0.0002
    return meta

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    result=comprobar() if args.check else extraer()
    print("9I meses TIFF:",result["meses_tiff_exitosos"],"pares adicionales:",
          result["pares_adicionales"],"incidencias:",len(result["problemas"]))
