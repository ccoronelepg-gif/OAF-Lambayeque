"""OAF-Lambayeque Fase 3Q: CHIRPS v3 mensual 1996-2000.
Retoma 1998 del raster previamente auditado. Usa solo meses completos de SENAMHI
y compara CHIRPS/PISCOp/ERA5 en exactamente las mismas fechas.
ATENCION: coordenadas documentales preliminares; no validacion independiente.
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
from rasterio.warp import transform as reproject

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datos"
URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
YEARS = set(range(1996, 2001))
STATIONS = {
    "Jayanca (La Viña)": (-6.322, -79.779),
    "Cayaltí": (-6.88079444, -79.54701389),
    "Reque": (-6.88613, -79.8355),
    "Lambayeque": (-6.73152778, -79.90983611),
    "Cueva Blanca": (-6.13130, -79.40450)
}
MODELS = ["CHIRPS v3", "PISCOp v3.0", "ERA5-Seamless"]
session = requests.Session()
session.headers.update({"User-Agent":"OAF-Lambayeque-scientific-validation/0.8 (academic)"})

def dist_km(lat1,lon1,lat2,lon2):
    a,b=math.radians(lat1),math.radians(lat2)
    c=math.radians(lat2-lat1)
    d=math.radians(lon2-lon1)
    x=math.sin(c/2)**2+math.cos(a)*math.cos(b)*math.sin(d/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(x)))

def fetch_month(mes,station_names):
    year,month=map(int,mes.split("-"))
    url=URL+"chirps-v3.0.%04d.%02d.tif"%(year,month)
    error=None
    for attempt in range(3):
        try:
            response=session.get(url,timeout=(20,90))
            response.raise_for_status()
            blob=response.content
            if len(blob)<100000:raise ValueError("TIFF demasiado pequeño")
            with MemoryFile(blob) as mem, mem.open() as ds:
                if ds.count!=1 or ds.crs is None:raise ValueError("Metadatos raster invalidos")
                if abs(ds.res[0]-.05)>0.0001 or abs(ds.res[1]-.05)>0.0001:
                    raise ValueError("Resolucion CHIRPS inesperada: "+str(ds.res))
                values=[]
                for name in station_names:
                    lat,lon=STATIONS[name]
                    xx,yy=reproject("EPSG:4326",ds.crs,[lon],[lat])
                    x,y=xx[0],yy[0]
                    if not (ds.bounds.left<=x<=ds.bounds.right and
                            ds.bounds.bottom<=y<=ds.bounds.top):
                        raise ValueError("Estacion fuera del raster: "+name)
                    val=next(ds.sample([(x,y)],indexes=1,masked=True))[0]
                    if np.ma.is_masked(val) or not np.isfinite(float(val)) or float(val)<0:
                        raise ValueError("Pixel nulo/negativo: "+name)
                    ri,ci=ds.index(x,y)
                    cx,cy=ds.xy(ri,ci,offset="center")
                    gx,gy=reproject(ds.crs,"EPSG:4326",[cx],[cy])
                    values.append({
                        "estacion":name,"mes":mes,"chirps_mm":round(float(val),4),
                        "latitud_punto":lat,"longitud_punto":lon,
                        "latitud_pixel":round(float(gy[0]),7),
                        "longitud_pixel":round(float(gx[0]),7),
                        "distancia_pixel_km":round(dist_km(lat,lon,gy[0],gx[0]),3),
                        "resolucion_x":round(float(ds.res[0]),6),
                        "resolucion_y":round(float(ds.res[1]),6),
                        "sistema_referencia":str(ds.crs),"url_raster":url
                    })
                return values
        except (requests.RequestException,ValueError,TypeError,KeyError,RuntimeError) as exc:
            error=exc
            if attempt<2:time.sleep(5*(attempt+1))
    raise RuntimeError(str(error)[:250])

def metrics_for(part,model,stratum):
    o=part["observado_mm"].astype(float).to_numpy()
    e=part["estimado_mm"].astype(float).to_numpy()
    d=e-o
    denom=float(o.sum())
    return dict(estacion=part["estacion"].iloc[0],
       producto=model,estrato=stratum,meses=len(part),
       observado_total_mm=round(float(o.sum()),3),
       estimado_total_mm=round(float(e.sum()),3),
       sesgo_total_pct=round(float(d.sum()/denom*100),2) if denom>0 else None,
       sesgo_mensual_mm=round(float(d.mean()),3),
       mae_mensual_mm=round(float(np.abs(d).mean()),3),
       rmse_mensual_mm=round(float(np.sqrt((d**2).mean())),3),
       pearson=round(float(np.corrcoef(o,e)[0,1]),4) if len(o)>=3 and np.std(o)>0 and np.std(e)>0 else None)

def main():
    observation=pd.read_csv(DATA/"senamhi_mensual_completo_1996_2015.csv")
    observation["ano"]=observation.mes.str[:4].astype(int)
    subset=observation[(observation.ano.isin(YEARS)) &
                       (observation.dias_validos==observation.dias_mes)].copy()
    assert subset.estacion.nunique()==5
    assert not subset.duplicated(["estacion","mes"]).any()
    months=sorted(subset.mes.unique())
    past=pd.read_csv(DATA/"chirps_3q_pixeles_1998.csv")
    past=past[past.mes.str[:4]=="1998"]
    assert len(past)==60 and past[["estacion","mes"]].drop_duplicates().shape[0]==60
    pixels=[];errors=[];reused=0;downloaded=0
    for month in months:
        stations=sorted(subset.loc[subset.mes==month,"estacion"].unique())
        if month.startswith("1998-"):
            grab=past[(past.mes==month)&(past.estacion.isin(stations))]
            if len(grab)!=len(stations):
                errors.append({"mes":month,"error":"Registro 1998 incompleto en cache"});continue
            pixels.extend(grab.to_dict("records"))
            reused+=1
        else:
            try:
                result=fetch_month(month,stations)
                pixels.extend(result)
                downloaded+=1
                print("OK",month,len(result),"pixeles",flush=True)
            except Exception as exc:
                errors.append({"mes":month,"error":f"{type(exc).__name__}: {str(exc)[:240]}"})
                print("ERROR",month,str(exc)[:180],flush=True)
            time.sleep(.35)
    pix=pd.DataFrame(pixels)
    if len(pix)==0:raise RuntimeError("Sin pixeles validos, no se publica conclusion")
    pix.sort_values(["estacion","mes"]).to_csv(DATA/"chirps_3q_pixeles_1996_2000.csv",index=False)
    matched=subset[["estacion","mes","observado_mm"]].merge(
        pix[["estacion","mes","chirps_mm"]],on=["estacion","mes"],validate="one_to_one")
    previous=pd.read_csv(DATA/"comparacion_3o_multianual.csv")
    previous=previous[previous.mes.str[:4].astype(int).isin(YEARS)]
    other=previous.pivot(index=["estacion","mes"],columns="producto",values="estimado_mm").reset_index()
    matched=matched.merge(other,on=["estacion","mes"],validate="one_to_one")
    assert not matched.duplicated(["estacion","mes"]).any()
    for model in ("PISCOp v3.0","ERA5-Seamless"):
        if model not in matched.columns:raise ValueError("Falta producto "+model)
    n_before=len(matched)
    matched=matched.dropna(subset=["chirps_mm","PISCOp v3.0","ERA5-Seamless"])
    if len(matched)!=n_before:
        errors.append({"error":str(n_before-len(matched))+" meses sin tres estimaciones, excluidos"})
    records=[]
    for model,source in [("CHIRPS v3","chirps_mm"),("PISCOp v3.0","PISCOp v3.0"),
                         ("ERA5-Seamless","ERA5-Seamless")]:
        frame=matched[["estacion","mes","observado_mm",source]].rename(
            columns={source:"estimado_mm"}).copy()
        frame["producto"]=model
        frame["diferencia_mm"]=(frame.estimado_mm-frame.observado_mm).round(4)
        records.append(frame)
    compare=pd.concat(records,ignore_index=True)
    compare.sort_values(["estacion","mes","producto"]).to_csv(
        DATA/"comparacion_3q_multianual_1996_2000.csv",index=False)
    summary=[]
    for (station,product),group in compare.groupby(["estacion","producto"]):
        for stratum,rows in [("todos",group),("sin_1998",group[group.mes.str[:4]!="1998"]),
                             ("solo_1998",group[group.mes.str[:4]=="1998"])]:
            if len(rows):summary.append(metrics_for(rows,product,stratum))
    stat=pd.DataFrame(summary)
    stat.sort_values(["estacion","estrato","producto"]).to_csv(
        DATA/"metricas_3q_multianual_1996_2000.csv",index=False)
    state=dict(fase="3Q",bloque="1996-2000",meses_calendario=60,
        meses_raster_reutilizados_1998=reused,meses_raster_descargados=downloaded,
        meses_raster_con_falla=len([e for e in errors if e.get("mes")]),
        pares_estacion_mes=len(matched),pares_estimacion=len(compare),
        meses_estacion_validos_senamhi=len(subset),incidencias=errors,
        coordenadas_historicas_preliminares=True,validacion_independiente=False,
        ventana_climatica_general="1996-2025: NO validada en este bloque")
    (DATA/"estado_3q_multianual.json").write_text(
        json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=[
       "# Fase 3Q — Comparacion CHIRPS, PISCOp y ERA5, 1996–2000","",
       "> **Exploratoria.** Metadatos instrumentales geograficos preliminares.",
       "> CHIRPS y PISCOp incluyen pluviómetros y no constituyen muestras independientes.",
       "> Los meses incompletos se excluyen; no se convierten faltantes en 0 mm.","",
       "## Cobertura", "",
       "- Meses raster descargados para 1996,1997,1999,2000: "+str(downloaded)+".",
       "- Meses raster 1998 reutilizados y auditados: "+str(reused)+".",
       "- Meses-estacion SENAMHI completos en el bloque: "+str(len(subset))+".",
       "- Meses-estacion con las tres estimaciones validas: "+str(len(matched))+".",
       "- Pares estacion-mes-producto: "+str(len(compare))+".",
       "- Incidencias: "+str(len(errors))+".","",
       "## Comparacion equitativa: mismos meses para tres productos","",
       "| Estacion | Producto | Meses | MAE (mm/mes) | RMSE (mm/mes) | Sesgo total (%) | Pearson |",
       "|---|---|---:|---:|---:|---:|---:|"]
    for x in stat[stat.estrato=="todos"].to_dict("records"):
        lines.append("| "+str(x["estacion"])+" | "+str(x["producto"])+" | "+str(x["meses"])+" | "+
           str(x["mae_mensual_mm"])+" | "+str(x["rmse_mensual_mm"])+" | "+
           str(x["sesgo_total_pct"])+" | "+str(x["pearson"])+" |")
    lines+=["","## Sin El Niño extraordinario de 1998 (estrato 1996–2000 excluyendo 1998)","",
       "| Estacion | Producto | Meses | MAE (mm/mes) | Sesgo total (%) |",
       "|---|---|---:|---:|---:|"]
    for x in stat[stat.estrato=="sin_1998"].to_dict("records"):
        lines.append("| "+str(x["estacion"])+" | "+str(x["producto"])+" | "+str(x["meses"])+" | "+
           str(x["mae_mensual_mm"])+" | "+str(x["sesgo_total_pct"])+" |")
    if errors:
        lines+=["","## Descargas o emparejamientos pendientes",""]
        lines.extend("- "+json.dumps(z,ensure_ascii=False) for z in errors)
    lines+=["","## Método y procedencia","",
       "Se usaron mapas mensuales GeoTIFF CHIRPS v3 del Climate Hazards Center, coordenadas y píxel que contiene la estación.",
       "La tabla multianual de SENAMHI–PISCOp–ERA5 procede de la Fase 3O y conserva meses completos.",
       "Se reutilizan los 12 raster/píxeles 1998 auditados en Fase 3Q piloto.",
       "Los datos no demuestran generalización espacial, causalidad del error ERA5 ni habilidad de pronóstico.",
       "Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/",
       "Documentación: https://www.chc.ucsb.edu/data/chirps3",""]
    (BASE/"VALIDACION_3Q_MULTIANUAL.md").write_text("\n".join(lines),encoding="utf-8")
    print("FIN 3Q",json.dumps({k:state[k] for k in ("meses_raster_descargados","meses_raster_con_falla","pares_estacion_mes","pares_estimacion")}),flush=True)
    return len(compare)

if __name__=="__main__":
    if not main():raise SystemExit(1)
