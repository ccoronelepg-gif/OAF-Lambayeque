"""OAF-Lambayeque Fase 3R: sensibilidad geográfica CHIRPS v3.
Extrae píxeles en pares de coordenadas documentales para 1998 y 2000.
No supone que un punto alternativo corresponda al emplazamiento histórico.
No infiere traslado instrumental ni validez de metadatos no corroborados.
"""
from __future__ import annotations
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio.io import MemoryFile
from rasterio.warp import transform as coords_transform

ROOT=Path(__file__).resolve().parents[1]
DAT=ROOT/"datos"
CAT=DAT/"catalogo_coordenadas_3r.csv"
OBS=DAT/"senamhi_mensual_completo_1996_2015.csv"
PREVIOUS=DAT/"comparacion_3q_1996_2015.csv"
BASE_URL="https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
YEARS=(1998,2000)
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"OAF-Lambayeque-research-geospatial-sensitivity/1.0"})

def distance_km(a,b,c,d):
    p1,p2=math.radians(a),math.radians(c)
    diff1=math.radians(c-a)
    diff2=math.radians(d-b)
    k=math.sin(diff1/2)**2+math.cos(p1)*math.cos(p2)*math.sin(diff2/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(k)))

def download(ym):
    year,month=ym.split("-")
    url=BASE_URL+"chirps-v3.0."+year+"."+month+".tif"
    last=None
    for trial in range(3):
        try:
            req=SESSION.get(url,timeout=(20,90))
            req.raise_for_status()
            if len(req.content)<100000:
                raise ValueError("Raster insuficiente")
            return url,req.content
        except (requests.RequestException, ValueError) as e:
            last=e
            if trial<2:
                print("reintento",ym,trial+1,flush=True)
                time.sleep(4*(trial+1))
    raise RuntimeError(str(last)[:230])

def raster_read(ym,cat):
    url,data=download(ym)
    result=[]
    with MemoryFile(data) as memory:
        with memory.open() as img:
            if img.count!=1 or img.crs is None:
                raise ValueError("Raster sin CRS válido")
            if abs(abs(img.res[0])-.05)>.0001 or abs(abs(img.res[1])-.05)>.0001:
                raise ValueError("Resolucion raster inesperada")
            for x in cat.itertuples(index=False):
                xx,yy=coords_transform("EPSG:4326",img.crs,
                                       [float(x.longitud)],[float(x.latitud)])
                lon,lat=xx[0],yy[0]
                if not(img.bounds.left<=lon<=img.bounds.right and
                       img.bounds.bottom<=lat<=img.bounds.top):
                    raise ValueError("Punto fuera del raster "+x.estacion)
                sample=next(img.sample([(lon,lat)],indexes=1,masked=True))[0]
                if np.ma.is_masked(sample) or not np.isfinite(float(sample)) or float(sample)<0:
                    raise ValueError("Dato faltante/negativo en "+str(x.estacion)+" "+ym)
                row,col=img.index(lon,lat)
                cx,cy=img.xy(row,col,offset="center")
                glon,glat=coords_transform(img.crs,"EPSG:4326",[cx],[cy])
                result.append(dict(estacion=x.estacion,variante=x.variante,
                     estado_documental=x.estado_documental,mes=ym,
                     chirps_mm=round(float(sample),4),
                     fila_pixel=int(row),columna_pixel=int(col),
                     latitud_pixel=round(float(glat[0]),7),
                     longitud_pixel=round(float(glon[0]),7),
                     distancia_pixel_km=round(distance_km(float(x.latitud),
                        float(x.longitud),float(glat[0]),float(glon[0])),3),
                     fuente_raster=url))
    return result

def summarize(cat, frame, obs, baseline):
    catalog=cat.set_index(["estacion","variante"])
    annual=[]
    months=[]
    for sta,g in frame.groupby("estacion"):
        originals=g[g.variante=="analisis_3Q"]
        candidate=g[g.variante!="analisis_3Q"]
        if len(originals)!=24 or len(candidate)!=24:
            raise ValueError("24 meses requeridos por cada ubicación de "+sta)
        check=originals.merge(baseline[baseline.estacion==sta][["mes","estimado_mm"]],
                              on="mes",validate="one_to_one")
        if len(check)!=24 or not np.allclose(check.chirps_mm,check.estimado_mm,atol=.0002):
            raise ValueError("No reproduce los píxeles CHIRPS históricos de "+sta)
        old=originals[["mes","chirps_mm","fila_pixel","columna_pixel"]].rename(columns={
          "chirps_mm":"base_mm","fila_pixel":"fila_base","columna_pixel":"col_base"})
        new=candidate[["mes","variante","chirps_mm","fila_pixel","columna_pixel"]].rename(columns={
          "chirps_mm":"alternativo_mm","fila_pixel":"fila_alt","columna_pixel":"col_alt"})
        merged=old.merge(new,on="mes",validate="one_to_one")
        merged=merged.merge(obs[obs.estacion==sta][["mes","observado_mm"]],
                           on="mes",validate="one_to_one")
        if len(merged)!=24 or merged.observado_mm.isna().any():
            raise ValueError("Incoherencia con meses completos SENAMHI para "+sta)
        base=catalog.loc[(sta,"analisis_3Q")]
        altrow=catalog.loc[(sta,candidate.variante.iloc[0])]
        shift=distance_km(base.latitud,base.longitud,altrow.latitud,altrow.longitud)
        merged["estacion"]=sta
        merged["distancia_puntos_km"]=round(shift,3)
        merged["diferencia_modelo_mm"]=(merged.alternativo_mm-merged.base_mm).round(4)
        merged["mismo_pixel"]=(merged.fila_base==merged.fila_alt)&(merged.col_base==merged.col_alt)
        months.append(merged)
        for year,h in merged.groupby(merged.mes.str[:4].astype(int)):
            obs_total=float(h.observado_mm.sum())
            baseline_total=float(h.base_mm.sum())
            candidate_total=float(h.alternativo_mm.sum())
            annual.append({
             "estacion":sta,"ano":year,
             "variante_alternativa":candidate.variante.iloc[0],
             "distancia_puntos_km":round(shift,3),
             "meses_mismo_pixel":int(h.mismo_pixel.sum()),"meses":len(h),
             "observado_anual_mm":round(obs_total,3),
             "base_anual_mm":round(baseline_total,3),
             "alternativo_anual_mm":round(candidate_total,3),
             "diferencia_anual_mm":round(candidate_total-baseline_total,3),
             "diferencia_anual_pct_respecto_base":
                  round(100*(candidate_total-baseline_total)/baseline_total,2)
                      if baseline_total>0 else None,
             "mae_base_mm_mes":round(float(np.mean(np.abs(h.base_mm-h.observado_mm))),3),
             "mae_alternativo_mm_mes":round(float(np.mean(np.abs(h.alternativo_mm-h.observado_mm))),3),
             "sesgo_base_pct":round(100*(baseline_total-obs_total)/obs_total,2)
                      if obs_total>0 else None,
             "sesgo_alternativo_pct":round(100*(candidate_total-obs_total)/obs_total,2)
                      if obs_total>0 else None
            })
    return pd.DataFrame(annual),pd.concat(months,ignore_index=True)

def main():
    cat=pd.read_csv(CAT)
    expected=["Jayanca (La Viña)","Cayaltí","Reque","Lambayeque","Cueva Blanca"]
    if sorted(cat.estacion.unique())!=sorted(expected):
        raise ValueError("Catálogo no contiene cinco estaciones")
    if any((g.variante=="analisis_3Q").sum()!=1 or len(g)!=2
           for _,g in cat.groupby("estacion")):
        raise ValueError("Dos coordenadas por estación, una de referencia")
    obs=pd.read_csv(OBS)
    obs=obs[(obs.dias_validos==obs.dias_mes)&
       obs.mes.str[:4].astype(int).isin(YEARS)]
    if len(obs)!=120:
        raise ValueError("Se esperan 120 meses-estación SENAMHI completos 1998/2000")
    baseline=pd.read_csv(PREVIOUS)
    baseline=baseline[(baseline.producto=="CHIRPS v3")&
         baseline.mes.str[:4].astype(int).isin(YEARS)]
    if len(baseline)!=120:
        raise ValueError("Se esperan 120 meses de CHIRPS validado previamente")
    rows=[]
    errors=[]
    for year in YEARS:
        for month in range(1,13):
            ym=f"{year}-{month:02d}"
            try:
                extract=raster_read(ym,cat)
                if len(extract)!=10:raise ValueError("No se extrajeron 10 píxeles")
                rows.extend(extract)
                print("OK",ym,"píxeles",len(extract),flush=True)
            except Exception as e:
                errors.append({"mes":ym,"error":f"{type(e).__name__}: {str(e)[:230]}"})
                print("ERROR",ym,str(e)[:160],flush=True)
            time.sleep(.35)
    data=pd.DataFrame(rows)
    if len(data):
        data.to_csv(DAT/"coordenadas_pixeles_3r_1998_2000.csv",index=False)
    state={"fase":"3R","anios":[1998,2000],"rasters_previstos":24,
      "rasters_utilizables":len(rows)//10,"puntos_por_mes":10,"filas_pixel":len(rows),
      "incidencias":errors,"identidad_emplazamientos_historicos_confirmada":False,
      "alcance":"Sensibilidad a candidatos documentales, no validacion de metadatos"}
    if len(rows)==240 and not errors:
        annual,monthly=summarize(cat,data,obs,baseline)
        annual.sort_values(["estacion","ano"]).to_csv(
             DAT/"sensibilidad_3r_resumen.csv",index=False)
        monthly.sort_values(["estacion","mes"]).to_csv(
             DAT/"sensibilidad_3r_mensual.csv",index=False)
        state["combinaciones_completas"]=len(annual)
        report=["# Fase 3R | Sensibilidad de CHIRPS v3 a coordenadas alternativas","",
            "> Analisis EXPLORATORIO. Las coordenadas alternativas NO se han validado como emplazamientos del mismo instrumento.",
            "> Una discrepancia en las coordenadas de fuentes NO demuestra traslado de estación meteorológica.",
            "> Solo se compara el producto CHIRPS mensual para 1998 y 2000; no se altera la serie instrumental SENAMHI.","",
            "## Método y controles","",
            "- GeoTIFF mensuales CHIRPS v3 de Climate Hazards Center, 0,05 grados.",
            "- Dos coordenadas por estación: punto consultado en 3Q y candidato documental.",
            "- Extracción del píxel contenedor sin interpolación.",
            "- Datos CHIRPS 3Q originales se reprodujeron en 24 meses por cada estación.",
            "- Comparación sobre meses con todos los días válidos SENAMHI.",
            "- No se imputan datos faltantes ni se considera mejora por coincidencia como prueba de ubicación correcta.","",
            "## Sensibilidad anual","",
            "| Estación | Año | Distancia entre puntos km | Meses mismo píxel /12 | CHIRPS original mm | CHIRPS alternativo mm | Δ anual mm | MAE original | MAE alternativo |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for a in annual.to_dict("records"):
            report.append(f"| {a['estacion']} | {a['ano']} | {a['distancia_puntos_km']} | {a['meses_mismo_pixel']}/12 | {a['base_anual_mm']} | {a['alternativo_anual_mm']} | {a['diferencia_anual_mm']} | {a['mae_base_mm_mes']} | {a['mae_alternativo_mm_mes']} |")
        report+=["","## Trazabilidad y límites","",
            "- Inventario de coordenadas y procedencias en datos/catalogo_coordenadas_3r.csv.",
            "- Especial cuidado con Cueva Blanca: códigos y emplazamientos discordantes en fuentes; NO inferir equivalencia instrumental.",
            "- Posibles cambios de celda en 0,05 grados no demuestran cambios meteorológicos a escala del pluviómetro.",
            "- Código fuente y datos: scripts/sensibilidad_geografica_3r.py y datos/sensibilidad_3r_resumen.csv.",
            "- Raster: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/",
            "- La ubicación exacta y código en la ficha original de descarga SENAMHI siguen pendientes de corroboración; no extrapolar a parcelas.",""]
        (ROOT/"SENSIBILIDAD_3R.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    else:
        state["combinaciones_completas"]=0
        (ROOT/"SENSIBILIDAD_3R.md").write_text(
            "# Fase 3R | Sensibilidad espacial\n\n"
            "Ejecución parcial, no se calcularon comparaciones completas.\n\n"
            +json.dumps(errors,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        pd.DataFrame().to_csv(DAT/"sensibilidad_3r_resumen.csv",index=False)
        pd.DataFrame().to_csv(DAT/"sensibilidad_3r_mensual.csv",index=False)
    (DAT/"estado_3r.json").write_text(
        json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print("ESTADO",json.dumps(state,ensure_ascii=False),flush=True)
    if state["combinaciones_completas"]!=10:raise SystemExit(1)

if __name__=="__main__":
    main()
