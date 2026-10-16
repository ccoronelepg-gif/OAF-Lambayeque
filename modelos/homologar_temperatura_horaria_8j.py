#!/usr/bin/env python3
"""OAF 8J. Homologación horaria conservadora, espacial y temporal.

No consulta APIs ni reemplaza observaciones faltantes. Las comparaciones con
ERA5-Land 8D son DESCRIPTIVAS, nunca validación instrumental independiente ni
habilidad prospectiva 8E. Python >=3.11, solo biblioteca estándar.
"""
from __future__ import annotations
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import re
from collections import defaultdict
from datetime import datetime, date, timezone
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
MANIFEST="datos/temperatura_horaria_8j/manifest.csv"
HIST="datos/lambayeque_mensual_era5_8d.csv"
OUTPUT="datos/homologacion_horaria_8j"
SITES={"Chiclayo":(-6.77140,-79.84090),"Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),"Olmos":(-5.98825,-79.74723)}
PERU=ZoneInfo("America/Lima")
DISTANCE_SCREEN_KM=20
ELEV_SCREEN_M=200
METADATA_FIELDS=(
"codigo_estacion","archivo_csv","sha256_archivo","url_fuente","publicado_utc",
"latitud","longitud","altitud_estacion_m","altitud_celda_era5_m",
"fuente_altitud_celda","localidad_oaf","codigo_verificado",
"coordenadas_verificadas","metodo_temporal_verificado",
"control_calidad_documentado","representatividad_espacial_evaluada",
"publicacion_derivados_autorizada","documento_metodologico"
)
HOUR_FIELDS=("codigo_estacion","instante_utc","temperatura_2m_c","calidad")
ROW_FIELDS=("codigo_estacion","localidad_oaf","mes","horas_validas","horas_calendario",
 "dias_con_24_horas","dias_mes","estado_completitud","temperatura_instrumental_horaria_c",
 "era5_land_8d_c","diferencia_era5_menos_estacion_c","distancia_estacion_punto_km",
 "desnivel_celda_estacion_m","estado_espacial","estado_comparacion")
NA={"","NA","N/A","null","NULL","-99.9","-999","-9999"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def csv_read(path,columns):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=list(columns):raise ValueError("Esquema CSV diferente del protocolo 8J: "+str(path))
        return list(reader)

def boolean(val):
    if val not in ("true","false"):raise ValueError("Bandera documental inválida: "+repr(val))
    return val=="true"

def number(v,allow_empty=False):
    if v is None or v in NA:
        if allow_empty:return None
        raise ValueError("Número instrumental/geográfico ausente")
    value=float(v)
    if not math.isfinite(value):raise ValueError("Valor no finito")
    return value

def parse_utc(s):
    if not isinstance(s,str):raise ValueError("Fecha inexistente")
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None or d.utcoffset().total_seconds()!=0:
        raise ValueError("Se requiere fecha explícitamente UTC")
    return d.astimezone(timezone.utc)

def haversine(lat1,lon1,lat2,lon2):
    if any(not math.isfinite(z) for z in (lat1,lon1,lat2,lon2)) or any(abs(z)>90 for z in (lat1,lat2)) or any(abs(z)>180 for z in (lon1,lon2)):
        raise ValueError("Coordenadas fuera de rango")
    d=math.pi/180
    a=math.sin((lat2-lat1)*d/2)**2+math.cos(lat1*d)*math.cos(lat2*d)*math.sin((lon2-lon1)*d/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(a)))

def era_months(root):
    with (root/HIST).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {"localidad","mes","temperatura_c"}.issubset(reader.fieldnames):
            raise ValueError("ERA5-Land mensual sin columnas requeridas")
        out={}
        for r in reader:
            key=(r["localidad"],r["mes"])
            if r["localidad"] not in SITES or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])",r["mes"]) or key in out:
                raise ValueError("Fila ERA5-Land inválida/duplicada")
            val=number(r["temperatura_c"])
            if not -40<val<55:raise ValueError("Temperatura ERA5-Land fuera de rango")
            out[key]=val
    return out

def registry(root):
    records=csv_read(root/MANIFEST,METADATA_FIELDS)
    seen=set()
    result=[]
    for r in records:
        code=r["codigo_estacion"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{2,48}",code) or code in seen:
            raise ValueError("Código de estación inválido o duplicado")
        seen.add(code)
        filename=r["archivo_csv"]
        if not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*\.csv",filename) or ".." in filename:
            raise ValueError("Ruta de entrada insegura")
        if not re.fullmatch("[0-9a-f]{64}",r["sha256_archivo"]):
            raise ValueError("SHA-256 instrumental incorrecto")
        for k in ("url_fuente","fuente_altitud_celda","documento_metodologico"):
            if not r[k].startswith("https://"):raise ValueError("Documento/fuente sin URL HTTPS: "+k)
        published=parse_utc(r["publicado_utc"])
        if published>datetime.now(timezone.utc):raise ValueError("Fuente publicada en fecha futura")
        site=r["localidad_oaf"]
        if site not in SITES:raise ValueError("Localidad OAF no permitida")
        lat,lon=number(r["latitud"]),number(r["longitud"])
        elev,grid=number(r["altitud_estacion_m"]),number(r["altitud_celda_era5_m"])
        if not -500<=elev<=6500 or not -500<=grid<=6500:raise ValueError("Elevaciones no físicas")
        dist=haversine(lat,lon,*SITES[site])
        delta=grid-elev
        flags={k:boolean(r[k]) for k in (
            "codigo_verificado","coordenadas_verificadas","metodo_temporal_verificado",
            "control_calidad_documentado","representatividad_espacial_evaluada",
            "publicacion_derivados_autorizada")}
        if not flags["publicacion_derivados_autorizada"]:
            raise ValueError("Publicación de datos derivados no autorizada")
        path=root/"datos/temperatura_horaria_8j/entradas"/filename
        if not path.is_file() or sha(path)!=r["sha256_archivo"]:
            raise ValueError("Archivo instrumental ausente o no coincide con SHA-256")
        spatial_ok=(dist<=DISTANCE_SCREEN_KM and abs(delta)<=ELEV_SCREEN_M and
                    all(flags[k] for k in ("codigo_verificado","coordenadas_verificadas",
                                          "metodo_temporal_verificado","control_calidad_documentado",
                                          "representatividad_espacial_evaluada")))
        result.append({"code":code,"path":path,"site":site,"published":published,
                       "distance":dist,"delta":delta,"flags":flags,
                       "spatial_ok":spatial_ok,"source":r["url_fuente"]})
    return result

def read_hourly(meta):
    inputs=csv_read(meta["path"],HOUR_FIELDS)
    if not inputs:raise ValueError("Archivo horario sin datos")
    hours={}
    for r in inputs:
        if r["codigo_estacion"]!=meta["code"]:raise ValueError("Inconsistencia de código de estación")
        instant=parse_utc(r["instante_utc"])
        if instant.minute or instant.second or instant.microsecond:
            raise ValueError("Se exige observación al inicio exacto de la hora UTC")
        if instant>=meta["published"]:
            raise ValueError("Observación futura respecto de la publicación")
        if instant in hours:raise ValueError("Duplicado horario UTC")
        if r["calidad"] not in ("aprobado","rechazado"):
            raise ValueError("Bandera QA no reconocida")
        v=number(r["temperatura_2m_c"],allow_empty=True)
        if v is not None and not -30<v<55:
            raise ValueError("Temperatura horaria físicamente inverosímil")
        hours[instant]=(v,r["calidad"])
    return hours

def aggregate(meta,hours,era):
    months=defaultdict(lambda:defaultdict(dict))
    for stamp,(val,qa) in hours.items():
        local=stamp.astimezone(PERU)
        month=local.strftime("%Y-%m")
        # clave: día local + hora local. Perú UTC−05, sin cambios horario actuales.
        months[month][local.day][local.hour]=(val,qa)
    out=[]
    for month,days in sorted(months.items()):
        year,mo=map(int,month.split("-"))
        n_days=calendar.monthrange(year,mo)[1]
        good_days=0
        vals=[]
        good_hours=0
        for day in range(1,n_days+1):
            by_hour=days.get(day,{})
            acceptable=(len(by_hour)==24 and all(h in by_hour and by_hour[h][0] is not None
                        and by_hour[h][1]=="aprobado" for h in range(24)))
            if acceptable:
                good_days+=1
                vals.extend(by_hour[h][0] for h in range(24))
                good_hours+=24
            else:
                good_hours+=sum(v is not None and qa=="aprobado" for v,qa in by_hour.values())
        complete=(good_days==n_days and len(vals)==n_days*24)
        observation=round(mean(vals),5) if complete else None
        grid=era.get((meta["site"],month)) if complete and meta["spatial_ok"] else None
        diff=round(grid-observation,5) if grid is not None else None
        state=("horas_o_dias_incompletos" if not complete else
               "representatividad_espacial_o_metadatos_pendientes" if not meta["spatial_ok"] else
               "mes_era5_land_8d_ausente" if grid is None else
               "comparacion_descriptiva_no_independiente")
        out.append({"codigo_estacion":meta["code"],"localidad_oaf":meta["site"],"mes":month,
            "horas_validas":good_hours,"horas_calendario":n_days*24,
            "dias_con_24_horas":good_days,"dias_mes":n_days,
            "estado_completitud":"completo" if complete else "incompleto",
            "temperatura_instrumental_horaria_c":observation,
            "era5_land_8d_c":round(grid,5) if grid is not None else None,
            "diferencia_era5_menos_estacion_c":diff,
            "distancia_estacion_punto_km":round(meta["distance"],3),
            "desnivel_celda_estacion_m":round(meta["delta"],2),
            "estado_espacial":"criba_documental_aprobada_no_certifica_equivalencia" if meta["spatial_ok"]
                              else "requiere_revision_geografica",
            "estado_comparacion":state})
    return out

def calculate(root):
    metadata=registry(root)
    era=era_months(root)
    rows=[]
    for entry in metadata:rows.extend(aggregate(entry,read_hourly(entry),era))
    errors=[r["diferencia_era5_menos_estacion_c"] for r in rows if r["diferencia_era5_menos_estacion_c"] is not None]
    per_site={}
    for site in SITES:
        vals=[r["diferencia_era5_menos_estacion_c"] for r in rows if
              r["localidad_oaf"]==site and r["diferencia_era5_menos_estacion_c"] is not None]
        per_site[site]={"n":len(vals),
           "mae_c":round(mean(abs(x) for x in vals),5) if vals else None,
           "rmse_c":round(math.sqrt(mean(x*x for x in vals)),5) if vals else None,
           "sesgo_c":round(mean(vals),5) if vals else None}
    summary={
       "fase":"8J","estado":"sin_series_horarias_instrumentales_autorizadas" if not metadata
                   else "homologacion_descriptiva_sujeta_a_revision",
       "registros_horarios_cargados":len(metadata),
       "estaciones_fuente_autorizada":len({x["code"] for x in metadata}),
       "meses_con_registros":len(rows),
       "meses_horarios_completos":sum(r["estado_completitud"]=="completo" for r in rows),
       "pares_descriptivos_estacion_era5":len(errors),
       "estadisticas_por_localidad":per_site,
       "datos_origen_observados_no_sinteticos":len(metadata)>0,
       "temperaturas_instrumentales_disponibles":bool(metadata),
       "no_se_imputan_horas":True,
       "correccion_gradiente_altitud_automatico":False,
       "validacion_independiente_demostrada":False,
       "habilidad_predictiva_8e_demostrada":False,
       "intervalos_predictivos_90_calibrados":False,
       "comparaciones_pueden_ser_publicadas_como_operativas":False,
       "criterios_cribado":{"distancia_km_max":DISTANCE_SCREEN_KM,"desnivel_absoluto_m_max":ELEV_SCREEN_M,
                             "son_criterios_suficientes_para_validacion":False},
       "definicion_horaria":"instantes UTC a hora exacta convertidos a America/Lima; 24 por día local, calendario completo",
       "tipo_contraste":"estación horaria vs temperatura mensual de reanálisis 8D (descriptivo, no error prospectivo de 8E)",
       "limitaciones":[
          "SENAMHI no ha proporcionado al repositorio datos instrumentales horarios autorizados.",
          "La media de 24 observaciones instantáneas horarias se compara exploratoriamente con la media mensual ERA5-Land 8D y puede diferir por método y cuadrícula.",
          "No se inventa Tmedia desde Tmax/Tmin ni se interpolan horas faltantes.",
          "Las coordenadas del punto OAF no son necesariamente las coordenadas reales de su cuadrícula ERA5-Land; comprobar metadatos de píxel antes de validar.",
          "La distancia y el desnivel son filtros de revisión, no demostración física de representatividad ni independencia.",
          "Sin metadatos originales no se atribuye un gradiente térmico vertical a las diferencias.",
          "Un contraste retrospectivo estación–reanálisis no evalúa habilidad prospectiva de las emisiones 8E."
       ],
       "trazabilidad":{"manifest_sha256":sha(root/MANIFEST),"era5_land_8d_sha256":sha(root/HIST),
                      "fuentes":[{"codigo_estacion":x["code"],"sha256":sha(x["path"]),
                                   "url_fuente":x["source"],"publicado_utc":x["published"].isoformat()}
                                 for x in metadata]}
    }
    return summary,rows

def serialize_csv(rows):
    sio=io.StringIO(newline="")
    wr=csv.DictWriter(sio,fieldnames=ROW_FIELDS,lineterminator="\n")
    wr.writeheader()
    for row in rows:
        wr.writerow({k:"" if row.get(k) is None else row[k] for k in ROW_FIELDS})
    return sio.getvalue()

def publish(root,check=False):
    result,rows=calculate(root)
    out=root/OUTPUT
    files={out/"estado_8j.json":json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+"\n",
           out/"comparaciones_horarias_8j.csv":serialize_csv(rows)}
    for path,value in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=value:
                raise ValueError("El reporte 8J publicado no corresponde a sus fuentes: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=value:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf-8")
    print(json.dumps({"fase":"8J","fuentes":result["estaciones_fuente_autorizada"],
                      "meses_completos":result["meses_horarios_completos"],
                      "pares":result["pares_descriptivos_estacion_era5"],"revision":check},
                     ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    publish(args.root,args.check)
