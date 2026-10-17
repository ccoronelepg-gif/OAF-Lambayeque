#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9K: recuperar dos NetCDF oficiales NOAA NMME 2026-10, conservar huellas SHA.
Se reporta solo la señal ENSEMBLE de gran escala (~1º), JAMÁS pronóstico altitudinal.
No convertir anomalias a anomalías OMM ni identificar leads si falta CF metadata.
"""
import argparse
import hashlib
import json
import gzip
import re
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen,Request
import netCDF4
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"datos/sectores_agroclimaticos_9k"
OUTPUT=DEST/"inventario_nmme_9k.json"
RAW_DIR=DEST/"fuentes_netcdf_gzip"
URL_ROOT="https://ftp.cpc.ncep.noaa.gov/NMME/realtime_anom/ENSMEAN/2026100800/"
FILE_NAMES={"temp":"NMME.tmp2m.202610.ENSMEAN.anom.nc",
            "lluvia":"NMME.prate.202610.ENSMEAN.anom.nc"}
SITES={"Chiclayo":(-6.7714,-79.8409),"Jayanca":(-6.39278,-79.8228),
       "Motupe":(-6.15083,-79.7142),"Olmos":(-5.98825,-79.74723)}

def fetch(url):
    with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-scientific-9K/1.0"}),timeout=80) as r:
        raw=r.read(8_000_001)
    if len(raw)>=8_000_001 or len(raw)<500000:raise ValueError("NetCDF tamaño sospechoso")
    if not (raw[:3]==b"CDF" or raw[:8]==b"\x89HDF\r\n\x1a\n"):
        raise ValueError("No es NetCDF")
    return raw

def frozen_source(kind,url):
    """Congelar bytes del NetCDF de NOAA; futuras ejecuciones no reescriben su vintage."""
    target=RAW_DIR/(FILE_NAMES[kind]+".gz")
    if target.exists():
        raw=gzip.decompress(target.read_bytes())
        if len(raw)<500000:raise ValueError("Archivo NOAA congelado inválido")
        return raw
    raw=fetch(url)
    RAW_DIR.mkdir(parents=True,exist_ok=True)
    target.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
    return raw

def months_from_axis(ds,axis):
    if axis not in ds.variables:raise ValueError("No se pudo leer eje target")
    v=ds.variables[axis]
    units=str(getattr(v,"units",""))
    found=re.fullmatch(r"months since (\\d{4})-(\\d{2})-\\d{2}.*",units)
    if not found:raise ValueError("Unidad temporal NOAA no reconocida: "+units)
    origin=int(found.group(1))*12+int(found.group(2))-1
    months=[]
    for x in np.ma.filled(v[:],np.nan):
        if not np.isfinite(x) or abs(x-round(float(x)))>1e-7:
            raise ValueError("Target mensual no entero")
        ordinal=origin+int(x)
        months.append(f"{ordinal//12:04d}-{ordinal%12+1:02d}")
    if months!=[f"{(2026*12+9+i)//12:04d}-{(2026*12+9+i)%12+1:02d}" for i in range(12)]:
        raise ValueError("Eje target NOAA inesperado: "+str(months))
    return months

def coordinate(ds,candidates,standard):
    for name in ds.variables:
        v=ds.variables[name]
        if name.lower() in candidates or getattr(v,"standard_name","").lower()==standard:
            if len(v.dimensions)==1 and v.dimensions[0] in ds.dimensions:
                return name
    raise ValueError("No encuentro coordenada "+standard)

def inspect(raw,kind,url):
    # netCDF4 permite analizar en memoria, sin reescribir o modificar el original.
    ds=netCDF4.Dataset("in-memory",mode="r",memory=raw)
    try:
        latkey=coordinate(ds,{"lat","latitude","y"},"latitude")
        lonkey=coordinate(ds,{"lon","longitude","x"},"longitude")
        lat=np.asarray(ds.variables[latkey][:],dtype="float64")
        lon=np.asarray(ds.variables[lonkey][:],dtype="float64")
        if lat.ndim!=1 or lon.ndim!=1 or lat.size<4 or lon.size<4:
            raise ValueError("Coordenadas NetCDF no 1D")
        lat_dim=ds.variables[latkey].dimensions[0]
        lon_dim=ds.variables[lonkey].dimensions[0]
        varlist=[(name,v) for name,v in ds.variables.items()
                 if lat_dim in v.dimensions and lon_dim in v.dimensions
                 and len(v.dimensions)>=3]
        if len(varlist)!=1:
            raise ValueError("Variable NMME única inesperada: "+repr([x[0] for x in varlist]))
        name,var=varlist[0]
        attrs={k:str(getattr(var,k))[:180] for k in var.ncattrs()
               if k in {"units","long_name","standard_name","description"}}
        if var.dimensions!=("target",lat_dim,lon_dim) or len(var.shape)!=3:
            raise ValueError("NMME debe tener eje target y lat/lon verificados")
        targets=months_from_axis(ds,"target")
        whole=np.ma.filled(var[:],np.nan).astype("float64")
        flags=[]
        for k,monthly in enumerate(whole):
            finite=monthly[np.isfinite(monthly)]
            if finite.size<100:
                flags.append("sin_datos_globales")
            elif np.all(finite==0):
                flags.append("cero_en_toda_la_malla_probable_relleno")
            else:
                flags.append("campo_numerico_real")
        # Se excluyen bloques enteros de cero usados como probable relleno;
        # nunca se les atribuye anomalia neutra validada.
        if flags[0]!="campo_numerico_real":
            raise ValueError("Primer target NMME sin señal numérica")
        # NMME es un pronóstico de escala gruesa; no generar 420 predicciones diferentes
        # con idéntico valor de la misma celda oceano-atmosférica.
        select={}
        spatial=[]
        for city,(la,lo) in SITES.items():
            ix=int(np.argmin(abs(lat-la)))
            mod_lon=lo%360 if lon.min()>=0 else lo
            iy=int(np.argmin(abs(lon-mod_lon)))
            selected=(float(lat[ix]),float(lon[iy]))
            if abs(selected[0]-la)>2 or min(abs(selected[1]-mod_lon),360-abs(selected[1]-mod_lon))>2:
                raise ValueError("Centro de celda NMME fuera de Lambayeque")
            varidx=tuple(ix if d==lat_dim else iy if d==lon_dim else slice(None)
                         for d in var.dimensions)
            vals=np.ma.asarray(var[varidx])
            nym=np.ma.filled(vals,np.nan).astype("float64")
            val_list=[round(float(x),6) if np.isfinite(x) and abs(x)<1e9 else None
                      for x in nym.flatten()]
            other=[d for d in var.dimensions if d not in (lat_dim,lon_dim)]
            if len(other)>2 or len(val_list)>180:
                raise ValueError("Otros ejes o plazos ambiguos: "+str(other))
            axes={axis:{
                 "valores":(np.ma.filled(ds.variables[axis][:],np.nan).tolist()
                     if axis in ds.variables and ds.variables[axis].ndim==1 else None),
                 "unidades":str(getattr(ds.variables[axis],"units","")) if axis in ds.variables else None,
                 "long_name":str(getattr(ds.variables[axis],"long_name","")) if axis in ds.variables else None
                } for axis in other}
            spatial.append({"localidad_referencial":city,"celda_latitud":selected[0],
                "celda_longitud_archivo":selected[1],
                "dimensiones_restantes":other,"ejes_nativos":axes,
                "valores_anomalia_original":[v if flags[i]=="campo_numerico_real" else None for i,v in enumerate(val_list)],
                "n_finitos":sum(v is not None and flags[i]=="campo_numerico_real" for i,v in enumerate(val_list)),
                "meses_objetivo":targets,
                "estado_target_malla_global":flags,
                "n_target_reales_en_celda":sum(v is not None and flags[i]=="campo_numerico_real" for i,v in enumerate(val_list)),
                "mes_valido_interpretado":None,
                "prediccion_altitudinal_por_sector":False})
        return {"variable_etiqueta":kind,"nombre_variable_netcdf":name,
                "dimensiones_originales":list(var.dimensions),
                "forma_original":list(var.shape),
                "metadatos_unidades":attrs,"lat_nombre":latkey,"lon_nombre":lonkey,
                "fuente_url":url,"sha256":hashlib.sha256(raw).hexdigest(),
                "bytes":len(raw),
                "resolucion_latitud_deg":round(float(np.median(abs(np.diff(lat)))),4),
                "resolucion_longitud_deg":round(float(np.median(abs(np.diff(lon)))),4),
                "tipo_emision":"pronostico_anomalia_realtime_archivo_NOAA_NMME",
                "fecha_inicializacion_en_nombre":"2026-10",
                "meses_objetivo_verificados_por_eje_CF":targets,
                "meses_con_campo_numerico":[m for m,q in zip(targets,flags) if q=="campo_numerico_real"],
                "meses_con_ceros_globales_sin_dato":[m for m,q in zip(targets,flags) if q!="campo_numerico_real"],
                "archivo_congelado_ruta":str((RAW_DIR/(FILE_NAMES[kind]+".gz")).relative_to(ROOT)),
                "advertencia_unidades":"Temp es anomalía K (incremento equivale °C); prate es anomalía de tasa mm/s y NO mm/mes sin conversión temporal.",
                "caracterización_vintage":"directorio publicacion NOAA 2026100800, no timestamp de creación de cada valor certificado externamente",
                "sitios_celda":spatial}
    finally:ds.close()

def generate():
    sources=[];issues=[]
    for kind,name in FILE_NAMES.items():
        url=URL_ROOT+name
        try:
            sources.append(inspect(frozen_source(kind,url),kind,url))
            print("NMME",kind,"NetCDF original inspeccionado",flush=True)
        except Exception as e:
            issues.append({"variable":kind,"fuente_url":url,"error":f"{type(e).__name__}: {e}"[:300]})
            print("NMME sin comprobación",kind,issues[-1]["error"],flush=True)
    return {"fase":"9K","fuente":"NOAA/CPC NMME real-time ensemble anomaly 2026-10",
      "fecha_descripcion_utc":datetime(2026,10,17,tzinfo=timezone.utc).isoformat(),
      "fecha_corte_modelo":"2026-10",
      "periodo_modelo_historico_desde":"2011-08",
      "fuentes_netcdf_comprobadas":len(sources),
      "fuentes_netcdf_esperadas":2,"fuentes":sources,"errores_consulta":issues,
      "pronostico_oaf_propio":False,"n_pares_con_observacion_validada":0,
      "habilidad_noaa_para_zonas_lambayeque_demostrada":False,
      "downscaling_zonal_aplicado":False,
      "probabilidad_calibrada_por_poligono":False,
      "mes_objetivo_cf_validado":len(sources)==2,
      "ejes_mensuales_condicionados_a_fecha_de_emision_NOAA":True,
      "nota":"Los valores originales no se comparan con 1996–2025 hasta confirmar unidad, eje lead, normal/anomalía de modelo y tiempo válido; una celda NMME gruesa cubre varios pisos altitudinales."}

def save():
    j=generate();DEST.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return j

def check():
    j=json.loads(OUTPUT.read_text("utf8"))
    assert j["fase"]=="9K" and len(j["fuentes"])+len(j["errores_consulta"])==2
    assert j["fuentes_netcdf_comprobadas"]==len(j["fuentes"])
    assert not j["downscaling_zonal_aplicado"]
    assert j["mes_objetivo_cf_validado"]==(len(j["fuentes"])==2)
    for s in j["fuentes"]:
        assert len(s["sha256"])==64 and s["bytes"]>500000
        assert len(s["sitios_celda"])==4
        assert s["resolucion_latitud_deg"]>=0.5
        assert s["resolucion_longitud_deg"]>=0.5
        assert s["meses_objetivo_verificados_por_eje_CF"][0]=="2026-10"
        assert all(len(z["meses_objetivo"])==12 for z in s["sitios_celda"])
        assert all(z["mes_valido_interpretado"] is None for z in s["sitios_celda"])
        assert (ROOT/s["archivo_congelado_ruta"]).exists()
    return j
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    j=check() if args.check else save()
    print("9K NOAA: fuentes NetCDF",j["fuentes_netcdf_comprobadas"],"/2")
