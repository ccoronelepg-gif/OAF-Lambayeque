#!/usr/bin/env python3
"""8U: velocidades/direcciones de viento atmosférico ERA5 1996-2025.

Puntos de referencia (no estaciones). Incluye dos puntos offshore para
observar viento sobre mar, que NO es una corriente oceánica.
Three blocks × 6 locations. Provider URL + SHA of unchanged JSON. Missing
sources do not produce 30-year climate. No retrospective predictive skill.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,time
from collections import defaultdict
from datetime import date,timedelta,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
RAW="datos/meteorologia_8u/fuentes"
OUT="datos/meteorologia_8u"
API="https://archive-api.open-meteo.com/v1/archive"
YEARS=((1996,2005),(2006,2015),(2016,2025))
VARS=("wind_speed_10m_mean","wind_speed_10m_max","wind_direction_10m_dominant")
LOCATIONS=(
 ("Chiclayo","tierra_referencia",-6.7714,-79.8409),
 ("Jayanca","tierra_referencia",-6.39278,-79.8228),
 ("Motupe","tierra_referencia",-6.1522,-79.7154),
 ("Olmos","tierra_referencia",-5.9849,-79.7454),
 ("Mar_frente_Pimentel","mar_abierto_muestreo",-6.8000,-81.0000),
 ("Mar_norte_Lambayeque","mar_abierto_muestreo",-5.9000,-81.5000)
)
FIELDS=("mes","sitio","ambiente","celda_era5_lat","celda_era5_lon",
   "velocidad_media_10m_m_s","velocidad_maxima_diaria_media_m_s",
   "componente_este_aprox_m_s","componente_norte_aprox_m_s",
   "direccion_dominante_vector_aprox_desde_grados",
   "dias_validos","observacion_instrumental")

def sha(raw):return hashlib.sha256(raw).hexdigest()
def expected_dates(a,b):
    start=date(a,1,1);end=date(b,12,31)
    return [(start+timedelta(days=n)).isoformat() for n in range((end-start).days+1)]

def url_for(start,end):
    return API+"?"+urlencode({
      "latitude":",".join(str(p[2]) for p in LOCATIONS),
      "longitude":",".join(str(p[3]) for p in LOCATIONS),
      "start_date":f"{start}-01-01","end_date":f"{end}-12-31",
      "daily":",".join(VARS),"models":"era5",
      "timezone":"America/Lima","wind_speed_unit":"ms",
      "cell_selection":"nearest"
    })

def filenames(root,start,end):
    base=root/RAW
    return base/f"era5_vientos_{start}_{end}.json.gz",base/f"era5_vientos_{start}_{end}.meta.json"

def validate(raw,start,end):
    j=json.loads(raw)
    if not isinstance(j,list) or len(j)!=len(LOCATIONS):
        raise ValueError("API vientos debe devolver seis ubicaciones distintas")
    expected=expected_dates(start,end)
    for obj,p in zip(j,LOCATIONS):
        d=obj.get("daily"); units=obj.get("daily_units",{})
        if (not isinstance(d,dict) or d.get("time")!=expected or
            obj.get("timezone")!="America/Lima"):
            raise ValueError("Serie viento faltante o zona horaria inconsistente")
        if not all(math.isfinite(float(obj[k])) for k in ("latitude","longitude")):
            raise ValueError("No hay centro de celda real")
        if units.get("wind_speed_10m_mean") not in ("m/s","ms"):
            raise ValueError("Viento no está en m/s")
        if units.get("wind_direction_10m_dominant") not in ("°","degrees"):
            raise ValueError("Dirección no viene en grados")
        for name in VARS:
            arr=d.get(name)
            if not isinstance(arr,list) or len(arr)!=len(expected):
                raise ValueError("Viento diario incompleto: "+name)
            if any(type(v) not in (int,float) or not math.isfinite(v) for v in arr):
                raise ValueError("Viento faltante o no numérico")
        if any(not(0<=v<=360) for v in d["wind_direction_10m_dominant"]):
            raise ValueError("Dirección del viento fuera de 0..360")
        if any(v<0 or v>70 for v in d["wind_speed_10m_mean"]):
            raise ValueError("Velocidad media del viento inverosímil")
        if any(v<0 or v>100 for v in d["wind_speed_10m_max"]):
            raise ValueError("Velocidad máxima fuera de rango de auditoría")
        if any(a>b+1e-6 for a,b in zip(d["wind_speed_10m_mean"],d["wind_speed_10m_max"])):
            raise ValueError("Promedio supera máximo diario")
    return j

def inspect(root,start,end):
    path,meta=filenames(root,start,end)
    if not path.exists() and not meta.exists():return None
    if not path.exists() or not meta.exists():raise ValueError("Bloque viento sin pareja de trazabilidad")
    data=gzip.decompress(path.read_bytes())
    j=json.loads(meta.read_text(encoding="utf-8"))
    if (j.get("fase")!="8U" or j.get("periodo")!=[start,end] or
        j.get("url")!=url_for(start,end) or j.get("sha256_original")!=sha(data) or
        j.get("sitios")!=[p[0] for p in LOCATIONS]):
        raise ValueError("Fuente viento sin SHA, URL o identidad auditables")
    return validate(data,start,end)

def fetch(root,max_new=1):
    (root/RAW).mkdir(parents=True,exist_ok=True)
    added=0
    for start,end in YEARS:
        if inspect(root,start,end) is not None:continue
        if added>=max_new:return
        url=url_for(start,end)
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-8U-ERA5-reanalysis/1.0"}),
                timeout=140) as response:
                if response.status!=200:raise ValueError("Respuesta HTTP viento inesperada")
                raw=response.read(15_000_001)
            if len(raw)>15_000_000:raise ValueError("JSON de viento demasiado grande")
            validate(raw,start,end)
        except HTTPError as exc:
            if exc.code==429:
                print("Open-Meteo HTTP 429. Respetar pausa, no sintetizar viento.",flush=True)
                return
            raise
        except (OSError,ValueError,TimeoutError,json.JSONDecodeError) as exc:
            print("Viento archivado pendiente por error real: "+str(exc),flush=True)
            return
        file,meta=filenames(root,start,end)
        file.write_bytes(gzip.compress(raw,mtime=0))
        meta.write_text(json.dumps({
           "fase":"8U","periodo":[start,end],"url":url,
           "sha256_original":sha(raw),
           "consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "sitios":[p[0] for p in LOCATIONS],
           "variables":list(VARS),
           "modelo":"ERA5 reanálisis no estación",
           "viento_10m_no_corriente_marina":True
        },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        added+=1
        print("ERA5 viento archivado:",start,end,flush=True)
        if added<max_new:time.sleep(3)

def export_csv(rows,fields):
    buffer=io.StringIO(newline="")
    wr=csv.DictWriter(buffer,fieldnames=fields,lineterminator="\n")
    wr.writeheader();wr.writerows(rows)
    return buffer.getvalue()

def calculate(root):
    blocks=[inspect(root,start,end) for start,end in YEARS]
    full=all(obj is not None for obj in blocks)
    centers=defaultdict(set);month_rows=defaultdict(list)
    source_count=sum(b is not None for b in blocks)
    for (start,end),block in zip(YEARS,blocks):
        if block is None:continue
        for loc,obs in zip(LOCATIONS,block):
            center=(round(obs["latitude"],5),round(obs["longitude"],5))
            centers[loc[0]].add(center)
            d=obs["daily"]
            for i,day in enumerate(d["time"]):
                speed=d["wind_speed_10m_mean"][i]
                angle=math.radians(d["wind_direction_10m_dominant"][i]%360)
                # Daily mean speed × daily dominant FROM-direction approximates
                # a daily mean u/v; it is NOT a true hourly/vector average.
                east=-speed*math.sin(angle)
                north=-speed*math.cos(angle)
                month_rows[(loc[0],day[:7])].append(
                    (speed,d["wind_speed_10m_max"][i],east,north))
    rows=[]
    if full:
        if len(month_rows)!=360*len(LOCATIONS):
            raise ValueError("Vientos 8U no tienen seis sitios × 360 meses")
        if any(len(centers[p[0]])!=1 for p in LOCATIONS):
            raise ValueError("Celda viento desplazada durante 1996–2025")
        for name,env,_,_ in LOCATIONS:
            lat,lon=next(iter(centers[name]))
            for year in range(1996,2026):
                for mon in range(1,13):
                    key=f"{year}-{mon:02d}";vv=month_rows[(name,key)]
                    if len(vv)!=len([x for x in expected_dates(year,year) if x[:7]==key]):
                        raise ValueError("Cobertura mensual del viento no íntegra")
                    east=statistics.mean(x[2] for x in vv)
                    north=statistics.mean(x[3] for x in vv)
                    direction=(math.degrees(math.atan2(-east,-north))+360)%360 if math.hypot(east,north)>1e-9 else ""
                    rows.append({
                      "mes":key,"sitio":name,"ambiente":env,
                      "celda_era5_lat":lat,"celda_era5_lon":lon,
                      "velocidad_media_10m_m_s":round(statistics.mean(x[0] for x in vv),5),
                      "velocidad_maxima_diaria_media_m_s":round(statistics.mean(x[1] for x in vv),5),
                      "componente_este_aprox_m_s":round(east,5),
                      "componente_norte_aprox_m_s":round(north,5),
                      "direccion_dominante_vector_aprox_desde_grados":round(direction,3) if direction!="" else "",
                      "dias_validos":len(vv),"observacion_instrumental":"false"})
    status={
      "fase":"8U","submodulo":"viento_atmosferico",
      "estado":"viento_completo_30_anos" if full else "fuentes_viento_incompletas",
      "modelo":"ERA5 vía Open-Meteo Historical Archive",
      "variables":list(VARS),"periodo":"1996–2025",
      "n_bloques_esperados":len(YEARS),"n_bloques_verificados":source_count,
      "n_ubicaciones_de_referencia":len(LOCATIONS),
      "n_ubicaciones_maritimas":sum(p[1]=="mar_abierto_muestreo" for p in LOCATIONS),
      "meses_por_ubicacion_completa":360 if full else 0,
      "n_filas_publicadas":len(rows),
      "numero_celdas_era5_unicas":len({next(iter(c)) for c in centers.values() if len(c)==1}) if full else 0,
      "procedimiento_componentes":"velocidad_media_diaria × direccion_dominante_diaria (FROM), estimación aproximada de u/v",
      "viento_inferido_no_es_corriente_oceanica":True,
      "interpretacion_celda_offshore_sin_verificacion_mascara_oceanica":True,
      "registro_instrumental_SENAMHI":False,
      "habilidad_predictiva_verificada":False,
      "informe_8U_no_asegura_seis_sensores":True,
      "sha_fuentes_originales":[{
         "periodo":[s,e],"sha256_original_comprimido":hashlib.sha256(filenames(root,s,e)[0].read_bytes()).hexdigest()
         if filenames(root,s,e)[0].exists() else None} for s,e in YEARS]
    }
    return status,rows

def publish(root,check=False):
    stat,rows=calculate(root)
    base=root/OUT
    outputs={
      base/"estado_viento_8u.json":json.dumps(stat,ensure_ascii=False,indent=2)+"\n",
      base/"vientos_mensuales_8u.csv":export_csv(rows,FIELDS)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,val in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=val:
                raise ValueError("8U viento no reproducible desde fuente ERA5")
        elif not path.exists() or path.read_text(encoding="utf-8")!=val:
            path.write_text(val,encoding="utf-8")
    print(json.dumps({"fase":"8U","wind":stat["n_bloques_verificados"],"rows":len(rows),"check":check}))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--fetch",action="store_true")
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--max-new",type=int,default=1)
    args=parser.parse_args()
    if args.fetch:fetch(args.root,args.max_new)
    publish(args.root,args.check)
