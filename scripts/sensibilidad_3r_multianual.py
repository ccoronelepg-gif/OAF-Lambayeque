"""OAF Fase 3R — Sensibilidad de celdas CHIRPS v3 a coordenadas
alternativas por bloques quinquenales de 1996-2015.

Cada archivo mensual es fuente oficial CHIRPS v3. Todos los datos de SENAMHI
se obtienen de meses completos, y se coteja el resultado del punto original
contra la extraccion CHIRPS de la fase 3Q. El candidato geografico NO se
interpreta como emplazamiento historico probado ni se selecciona por menor MAE.
"""
from __future__ import annotations
import os
import json
import math
import time
from pathlib import Path
import requests
import numpy as np
import pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as reproject

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"
YEAR_START = int(os.environ.get("OAF_YEAR_START", "1996"))
YEAR_END = int(os.environ.get("OAF_YEAR_END", "2000"))
if YEAR_START not in (1996, 2001, 2006, 2011) or YEAR_END != YEAR_START + 4:
    raise ValueError("Solo se admiten los cuatro bloques quinquenales acordados")
SUFFIX = str(YEAR_START) + "_" + str(YEAR_END)
BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "OAF-Lambayeque-academic-geographic-sensitivity/1.1"})

def distance_km(lat1, lon1, lat2, lon2):
    a = math.radians(lat1)
    b = math.radians(lat2)
    dlat = b - a
    dlon = math.radians(lon2 - lon1)
    h = math.sin(dlat/2)**2 + math.cos(a)*math.cos(b)*math.sin(dlon/2)**2
    return 12742.0176*math.asin(min(1, math.sqrt(h)))

def fetch_raster(ym):
    year, month = ym.split("-")
    url = BASE_URL + "chirps-v3.0." + year + "." + month + ".tif"
    err = None
    for attempt in range(3):
        try:
            response = SESSION.get(url, timeout=(20, 95))
            response.raise_for_status()
            if len(response.content) < 100000:
                raise ValueError("GeoTIFF demasiado pequeno")
            return url, response.content
        except (requests.RequestException, ValueError) as e:
            err = e
            if attempt < 2:
                print("REINTENTO", ym, type(e).__name__, flush=True)
                time.sleep((attempt+1)*5)
    raise RuntimeError("Sin GeoTIFF CHIRPS: " + str(err)[:190])

def pixels_for_month(ym, variants):
    url, binary = fetch_raster(ym)
    rows = []
    with MemoryFile(binary) as mem:
        with mem.open() as ds:
            if ds.count != 1 or ds.crs is None:
                raise ValueError("Raster sin CRS o bandas inesperadas")
            if abs(abs(ds.res[0]) - 0.05) > 0.0001 or abs(abs(ds.res[1]) - 0.05) > 0.0001:
                raise ValueError("Resolucion distinta de 0,05 grados")
            for x in variants.itertuples(index=False):
                lat, lon = float(x.latitud), float(x.longitud)
                xx, yy = reproject("EPSG:4326", ds.crs, [lon], [lat])
                px, py = xx[0], yy[0]
                if not (ds.bounds.left <= px <= ds.bounds.right and
                        ds.bounds.bottom <= py <= ds.bounds.top):
                    raise ValueError("Punto fuera del raster " + x.estacion)
                sample = next(ds.sample([(px, py)], indexes=1, masked=True))[0]
                if np.ma.is_masked(sample) or not np.isfinite(float(sample)) or float(sample) < 0:
                    raise ValueError("Precipitacion faltante/negativa " + x.estacion)
                row, col = ds.index(px, py)
                cx, cy = ds.xy(row, col, offset="center")
                gx, gy = reproject(ds.crs, "EPSG:4326", [cx], [cy])
                rows.append({
                    "estacion": x.estacion, "mes": ym, "variante": x.variante,
                    "latitud_consultada": lat, "longitud_consultada": lon,
                    "precipitacion_mm": round(float(sample), 4),
                    "fila_pixel": int(row), "columna_pixel": int(col),
                    "latitud_pixel": round(float(gy[0]), 7),
                    "longitud_pixel": round(float(gx[0]), 7),
                    "distancia_pixel_km": round(distance_km(lat, lon, gy[0], gx[0]), 3),
                    "url_raster": url,
                })
    return rows

def make_metrics(comparison):
    rows = []
    for station, g in comparison.groupby("estacion"):
        for name, sub in (
            ("todos",g),
            ("sin_1998",g[g.mes.str[:4]!="1998"])
        ):
            if sub.empty: continue
            observed = sub.observado_mm.to_numpy(float)
            base = sub.original_mm.to_numpy(float)
            alt = sub.alternativo_mm.to_numpy(float)
            diff = alt-base
            base_err = base-observed
            alt_err = alt-observed
            rows.append({
                "estacion": station, "periodo": name, "meses": len(sub),
                "meses_mismo_pixel": int(sub.mismo_pixel.sum()),
                "distancia_coordenadas_km": round(float(sub.distancia_coordenadas_km.iloc[0]),3),
                "obs_total_mm": round(float(observed.sum()),3),
                "original_total_mm": round(float(base.sum()),3),
                "alternativo_total_mm": round(float(alt.sum()),3),
                "diferencia_total_mm": round(float(diff.sum()),3),
                "delta_mae_mm": round(float(np.abs(alt_err).mean()-np.abs(base_err).mean()),3),
                "mae_original_mm": round(float(np.abs(base_err).mean()),3),
                "mae_alternativo_mm": round(float(np.abs(alt_err).mean()),3),
                "cambio_picos_mm": round(float(np.max(np.abs(diff))),3)
            })
    return pd.DataFrame(rows)

def main():
    catalog = pd.read_csv(DATA/"catalogo_coordenadas_3r.csv")
    if catalog.estacion.nunique()!=5: raise ValueError("Faltan estaciones en catalogo")
    for station,g in catalog.groupby("estacion"):
        if len(g)!=2 or sum(g.variante=="analisis_3Q")!=1:
            raise ValueError("Variantes no unicas " + station)
    daily = pd.read_csv(DATA/"senamhi_mensual_completo_1996_2015.csv")
    monthly = daily[daily.dias_validos==daily.dias_mes].copy()
    monthly = monthly[monthly.mes.str[:4].astype(int).between(YEAR_START,YEAR_END)]
    if monthly.duplicated(["estacion","mes"]).any(): raise ValueError("Observaciones duplicadas")
    baseline = pd.read_csv(DATA/"comparacion_3q_1996_2015.csv")
    baseline = baseline[baseline.producto=="CHIRPS v3"][["estacion","mes","estimado_mm"]]
    baseline = baseline[baseline.mes.str[:4].astype(int).between(YEAR_START,YEAR_END)]
    if len(baseline)!=len(monthly): raise ValueError("No coincide cobertura historica SENAMHI-CHIRPS")
    months = sorted(monthly.mes.unique())
    items = []; failures = []
    for ym in months:
        names = monthly.loc[monthly.mes==ym, "estacion"]
        variants = catalog[catalog.estacion.isin(names)]
        try:
            result = pixels_for_month(ym,variants)
            if len(result)!=2*len(names): raise ValueError("Extracciones incompletas")
            items.extend(result)
            print("OK",ym,len(result),"pixeles",flush=True)
        except Exception as e:
            failures.append({"mes":ym,"error":f"{type(e).__name__}: {str(e)[:200]}"})
            print("ERROR",ym,str(e)[:200],flush=True)
        time.sleep(.25)
    extraction = pd.DataFrame(items)
    if extraction.empty:
        raise RuntimeError("No hay extracciones; sin resultados")
    extraction.sort_values(["estacion","mes","variante"]).to_csv(
         DATA/("pixeles_3r_"+SUFFIX+".csv"),index=False)
    original = extraction[extraction.variante=="analisis_3Q"].copy()
    alternative = extraction[extraction.variante!="analisis_3Q"].copy()
    original = original.rename(columns={"precipitacion_mm":"original_mm",
        "fila_pixel":"fila_original","columna_pixel":"col_original",
        "latitud_consultada":"lat_orig","longitud_consultada":"lon_orig"})
    alternative = alternative.rename(columns={"precipitacion_mm":"alternativo_mm",
        "fila_pixel":"fila_alt","columna_pixel":"col_alt",
        "latitud_consultada":"lat_alt","longitud_consultada":"lon_alt"})
    cols_base=["estacion","mes","original_mm","fila_original","col_original","lat_orig","lon_orig"]
    cols_alt=["estacion","mes","alternativo_mm","fila_alt","col_alt","lat_alt","lon_alt"]
    matched = original[cols_base].merge(alternative[cols_alt],on=["estacion","mes"],validate="one_to_one")
    matched = matched.merge(monthly[["estacion","mes","observado_mm"]],on=["estacion","mes"],validate="one_to_one")
    matched = matched.merge(baseline,on=["estacion","mes"],validate="one_to_one")
    if len(matched)!=len(items)//2:
        raise ValueError("Emparejamiento con multiplicidad incorrecta")
    if not np.allclose(matched.original_mm,matched.estimado_mm,atol=.0002):
        raise ValueError("La extraccion original CHIRPS no reproduce los resultados previos")
    matched.drop(columns=["estimado_mm"],inplace=True)
    matched["mismo_pixel"]=(matched.fila_original==matched.fila_alt)&(matched.col_original==matched.col_alt)
    matched["distancia_coordenadas_km"]=matched.apply(
        lambda x:distance_km(x.lat_orig,x.lon_orig,x.lat_alt,x.lon_alt),axis=1)
    matched["diferencia_mm"]=matched.alternativo_mm-matched.original_mm
    matched.sort_values(["estacion","mes"]).to_csv(DATA/("sensibilidad_3r_mensual_"+SUFFIX+".csv"),index=False)
    stat=make_metrics(matched)
    stat.sort_values(["estacion","periodo"]).to_csv(DATA/("sensibilidad_3r_metricas_"+SUFFIX+".csv"),index=False)
    status={
        "fase":"3R_multianual","bloque":f"{YEAR_START}-{YEAR_END}",
        "meses_calendario_con_observacion":len(months),
        "meses_estacion_validos_senamhi":len(monthly),
        "meses_estacion_comparados":len(matched),
        "filas_pixel":len(extraction),
        "raster_descargas_fallidas":failures,
        "identidad_instrumental_confirmada":False,
        "las_coordenadas_alternativas_son_candidatas":True
    }
    (DATA/("estado_3r_"+SUFFIX+".json")).write_text(
        json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
    report=[
      "# Fase 3R: sensibilidad geografica de CHIRPS " + f"{YEAR_START}-{YEAR_END}","",
      "> Analisis exploratorio: la ubicacion real de las estaciones historicas NO se determina por menor error.",
      "> Dos pares de metadatos por cada una de cinco estaciones; no afirmar traslados.","",
      "**Meses-estacion disponibles:** "+str(len(monthly)),
      "**Comparaciones con las dos ubicaciones:** "+str(len(matched)),
      "**Rasters con fallo:** "+str(len(failures)),"",
      "## Diferencias multianuales", "",
      "| Estacion | Meses | Meses mismo pixel | Diferencia CHIRPS (mm) | MAE original | MAE alternativo |",
      "|---|---:|---:|---:|---:|---:|"]
    for z in stat[stat.periodo=="todos"].to_dict("records"):
        report.append("| "+str(z["estacion"])+" | "+str(z["meses"])+" | "+str(z["meses_mismo_pixel"])+" | "+str(z["diferencia_total_mm"])+" | "+str(z["mae_original_mm"])+" | "+str(z["mae_alternativo_mm"])+" |")
    if failures:
        report+=["","## Incidencias de descarga",""]
        report.extend("- "+json.dumps(x,ensure_ascii=False) for x in failures)
    report+=["","Fuente GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/",
       "Datos instrumentales: registros históricos SENAMHI, solo meses completos.",
       "Coordenadas: datos/catalogo_coordenadas_3r.csv (identidad no certificada).",
       "PISCOp y ERA5 NO se recalcularon aquí; las diferencias son de CHIRPS.",""]
    (ROOT/("SENSIBILIDAD_3R_"+SUFFIX+".md")).write_text("\n".join(report),encoding="utf-8")
    if failures or len(matched)!=len(monthly):
        raise SystemExit("Bloque incompleto; estado y resultados parciales guardados")
    print("FIN",SUFFIX,"meses-estacion",len(matched),flush=True)

if __name__=="__main__":
    main()
