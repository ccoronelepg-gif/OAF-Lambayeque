#!/usr/bin/env python3
"""OAF-Lambayeque 8I: importador seguro de temperatura instrumental SENAMHI.

Sin fuentes autorizadas, escribe explícitamente estado pendiente y CSV vacío.
No descarga, inventa ni altera observaciones. Contrasta descriptivamente
temperatura mensual homologada con la grilla ERA5-Land histórica 8D, NUNCA con
la habilidad prospectiva del predictor 8E. Python estándar >= 3.11.
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
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "datos/temperatura_senamhi_8i/manifest.csv"
HIST = "datos/lambayeque_mensual_era5_8d.csv"
OUTPUT = "datos/homologacion_temperatura_8i"
FIELDS_MANIFEST = (
 "codigo_estacion","nombre_estacion","archivo_csv","sha256_archivo","url_fuente",
 "fecha_publicacion_utc","unidad","zona_horaria","latitud","longitud","altitud_m",
 "codigo_confirmado","coordenadas_confirmadas","metodo_homologado",
 "calidad_confirmada","independencia_confirmada","autorizacion_publicacion_derivados",
 "punto_oaf_objetivo","documento_metodo"
)
FIELDS_DAILY = ("codigo_estacion","fecha","tmax_c","tmin_c","tmedia_c","metodo_tmedia","control_calidad")
FIELDS_MONTHLY = (
 "codigo_estacion","nombre_estacion","mes","dias_mes","dias_tmedia_validos",
 "estado_mes","metodo_tmedia","temperatura_media_observada_c","punto_oaf_objetivo",
 "distancia_punto_km","era5_land_8d_c","diferencia_era5_menos_estacion_c",
 "estado_comparacion","independencia_confirmada"
)
SITES = {
 "Chiclayo":(-6.77140,-79.84090),
 "Jayanca":(-6.39278,-79.82280),
 "Motupe":(-6.15083,-79.71420),
 "Olmos":(-5.98825,-79.74723),
}
LIMA=ZoneInfo("America/Lima")
MISSING={"","NA","N/A","null","NULL","-99.9","-999","-9999"}
METHODS={"promedio_horario_24h","media_diaria_metodo_documentado"}
ALLOWED_QA={"aprobado","rechazado"}
MIN_MONTHLY_PAIRS=12   # Solo indicador de muestra descriptiva; no certifica independencia.
SPATIAL_SCREEN_KM=20  # Criba administrativa, no garantía de representatividad.

def fieldnames(reader,expected):
    if reader.fieldnames != list(expected):
        raise ValueError("Esquema CSV incompatible: "+repr(reader.fieldnames))

def read_table(path,fields):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        fieldnames(rdr,fields)
        return list(rdr)

def parse_bool(s):
    if s not in ("true","false"):raise ValueError("Booleano no reconocido "+repr(s))
    return s=="true"

def number(v,empty=False):
    if v in MISSING:
        if empty:return None
        raise ValueError("Número faltante no autorizado")
    if v is None or not isinstance(v,str):raise ValueError("Número inválido")
    x=float(v)
    if not math.isfinite(x):raise ValueError("Número no finito")
    return x

def date_iso(s):
    if not isinstance(s,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",s):
        raise ValueError("Fecha diaria inválida")
    d=date.fromisoformat(s)
    if d.isoformat()!=s:raise ValueError("Fecha no canónica")
    return d

def timestamp(s):
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None:raise ValueError("Publicación sin zona horaria")
    return d.astimezone(timezone.utc)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def distance_km(lat,lon,lat2,lon2):
    if not -90<=lat<=90 or not -90<=lat2<=90 or not -180<=lon<=180 or not -180<=lon2<=180:
        raise ValueError("Coordenadas fuera de rango")
    p=math.pi/180
    a=math.sin((lat2-lat)*p/2)**2+math.cos(lat*p)*math.cos(lat2*p)*math.sin((lon2-lon)*p/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(a)))

def load_era(root):
    with (root/HIST).open(encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        if not rdr.fieldnames or not {"localidad","mes","temperatura_c"}.issubset(rdr.fieldnames):
            raise ValueError("El archivo 8D no incluye columnas de temperatura")
        lookup={}
        for row in rdr:
            k=(row["localidad"],row["mes"])
            if k in lookup:raise ValueError("Duplicado en temperatura 8D")
            if row["localidad"] not in SITES or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])",row["mes"]):
                raise ValueError("Localidad/mes ERA5 inesperado")
            val=number(row["temperatura_c"])
            if not -40<val<55:raise ValueError("ERA5 fuera de rango")
            lookup[k]=val
    return lookup

def load_manifest(root):
    out=[]
    seen=set()
    for r in read_table(root/MANIFEST,FIELDS_MANIFEST):
        code=r["codigo_estacion"].strip()
        if not re.fullmatch("[A-Za-z0-9_-]{2,48}",code) or code in seen:
            raise ValueError("Código inválido o repetido en manifest")
        seen.add(code)
        if not r["nombre_estacion"].strip():raise ValueError("Nombre de estación vacío")
        file=r["archivo_csv"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+\.csv",file) or file.startswith("."):
            raise ValueError("Nombre de archivo no seguro")
        digest=r["sha256_archivo"].lower()
        if not re.fullmatch("[0-9a-f]{64}",digest):
            raise ValueError("SHA-256 de entrada ausente o inválido")
        if not r["url_fuente"].startswith("https://"):
            raise ValueError("Falta procedencia documental HTTPS")
        if not r["documento_metodo"].startswith("https://"):
            raise ValueError("Falta documentación verificable del método Tmedia")
        published=timestamp(r["fecha_publicacion_utc"])
        if published>datetime.now(timezone.utc):
            raise ValueError("Archivo no puede estar publicado en el futuro")
        if r["unidad"]!="°C" or r["zona_horaria"]!="America/Lima":
            raise ValueError("Unidad o huso horario incompatibles")
        lat,lon=number(r["latitud"]),number(r["longitud"])
        alt=number(r["altitud_m"])
        if not -500<=alt<=7000:raise ValueError("Altitud documental inválida")
        site=r["punto_oaf_objetivo"]
        if site not in SITES:raise ValueError("Punto OAF no reconocido")
        dist=distance_km(lat,lon,*SITES[site])
        flags={k:parse_bool(r[k]) for k in (
          "codigo_confirmado","coordenadas_confirmadas","metodo_homologado",
          "calidad_confirmada","independencia_confirmada",
          "autorizacion_publicacion_derivados"
        )}
        if not flags["autorizacion_publicacion_derivados"]:
            raise ValueError("No publicar productos derivados sin autorización documental")
        path=root/"datos/temperatura_senamhi_8i/entradas"/file
        if not path.is_file():raise ValueError("Fuente instrumental declarada pero no aportada")
        if sha(path)!=digest:raise ValueError("El archivo instrumental no coincide con su SHA-256")
        out.append(dict(r,code=code,path=path,published=published,lat=lat,lon=lon,
                        alt=alt,site=site,distance=dist,flags=flags))
    return out

def normalize_days(meta):
    rows=read_table(meta["path"],FIELDS_DAILY)
    if not rows:raise ValueError("Archivo diario de estación sin filas")
    days={}
    for row in rows:
        if row["codigo_estacion"]!=meta["code"]:
            raise ValueError("Código diario distinto de manifiesto")
        day=date_iso(row["fecha"])
        if day in days:raise ValueError("Fecha diaria duplicada")
        if day>meta["published"].astimezone(LIMA).date():
            raise ValueError("Una observación se fecha después de la publicación del archivo")
        tmax=number(row["tmax_c"],True);tmin=number(row["tmin_c"],True)
        tmean=number(row["tmedia_c"],True)
        for v in (tmax,tmin,tmean):
            if v is not None and not -30<v<55:
                raise ValueError("Temperatura diaria físicamente inverosímil")
        if tmax is not None and tmin is not None and tmax<tmin:
            raise ValueError("Tmax menor que Tmin")
        if tmean is not None:
            if tmin is not None and tmean<tmin-0.1:raise ValueError("Tmedia debajo de Tmin")
            if tmax is not None and tmean>tmax+0.1:raise ValueError("Tmedia por encima de Tmax")
        method=row["metodo_tmedia"]
        if method and method not in METHODS:raise ValueError("Método Tmedia no reconocido")
        if row["control_calidad"] not in ALLOWED_QA:
            raise ValueError("Estado QA diario no reconocido")
        days[day]=(tmean,method,row["control_calidad"])
    return days

def monthly(meta,days,era):
    groups=defaultdict(dict)
    for d,value in days.items():groups[d.strftime("%Y-%m")][d.day]=value
    result=[]
    for mon,byday in sorted(groups.items()):
        year,mo=map(int,mon.split("-"))
        count=calendar.monthrange(year,mo)[1]
        valid=[byday[d] for d in range(1,count+1) if d in byday and
               byday[d][0] is not None and byday[d][2]=="aprobado" and
               byday[d][1] in METHODS]
        complete=(len(valid)==count and len(byday)==count)
        methods={x[1] for x in valid}
        comparable=(complete and len(methods)==1 and
                    meta["flags"]["codigo_confirmado"] and
                    meta["flags"]["coordenadas_confirmadas"] and
                    meta["flags"]["metodo_homologado"] and
                    meta["flags"]["calidad_confirmada"] and
                    meta["distance"]<=SPATIAL_SCREEN_KM)
        observed=mean(x[0] for x in valid) if complete else None
        ref=era.get((meta["site"],mon)) if comparable else None
        diff=ref-observed if ref is not None else None
        status=("sin_serie_diaria_completa" if not complete else
                "metodos_diarios_mixtos" if len(methods)!=1 else
                "metadatos_o_representatividad_pendientes" if not comparable else
                "mes_sin_era5_land_8d" if ref is None else
                "comparacion_descriptiva_sin_independencia_certificada" if not meta["flags"]["independencia_confirmada"] else
                "comparacion_preliminar_con_independencia_declarada")
        result.append({
         "codigo_estacion":meta["code"],"nombre_estacion":meta["nombre_estacion"],
         "mes":mon,"dias_mes":count,"dias_tmedia_validos":len(valid),
         "estado_mes":"completo" if complete else "incompleto",
         "metodo_tmedia":next(iter(methods)) if len(methods)==1 else "",
         "temperatura_media_observada_c":round(observed,5) if observed is not None else None,
         "punto_oaf_objetivo":meta["site"],"distancia_punto_km":round(meta["distance"],2),
         "era5_land_8d_c":round(ref,5) if ref is not None else None,
         "diferencia_era5_menos_estacion_c":round(diff,5) if diff is not None else None,
         "estado_comparacion":status,
         "independencia_confirmada":meta["flags"]["independencia_confirmada"]
        })
    return result

def measures(rows):
    errors=[r["diferencia_era5_menos_estacion_c"] for r in rows if r["diferencia_era5_menos_estacion_c"] is not None]
    n=len(errors)
    return {"n":n,
      "mae_c":round(mean(abs(e) for e in errors),5) if n else None,
      "rmse_c":round(math.sqrt(mean(e*e for e in errors)),5) if n else None,
      "sesgo_c":round(mean(errors),5) if n else None,
      "habilidad_predictiva_8e_demostrada":False,
      "validacion_independiente_certificada":False}

def evaluate(root):
    manifest=load_manifest(root)
    era=load_era(root)
    allrows=[]
    for meta in manifest:allrows.extend(monthly(meta,normalize_days(meta),era))
    if len({(r["codigo_estacion"],r["mes"]) for r in allrows})!=len(allrows):
        raise ValueError("Estación/mes repetido")
    out={
      "fase":"8I","tipo":"homologacion_instrumental_descriptiva_condicional",
      "estado":"sin_serie_termica_senamhi_instrumental" if not manifest else "datos_aportados_con_controles_sujetos_a_auditoria",
      "n_archivos_fuente_autorizados":len(manifest),
      "n_estaciones_con_fuente":len({m["code"] for m in manifest}),
      "n_meses_inspeccionados":len(allrows),
      "n_meses_completos":sum(r["estado_mes"]=="completo" for r in allrows),
      "n_meses_con_pares_estacion_era5":sum(r["diferencia_era5_menos_estacion_c"] is not None for r in allrows),
      "n_estaciones_con_par":len({r["codigo_estacion"] for r in allrows if r["diferencia_era5_menos_estacion_c"] is not None}),
      "estadisticos_descriptivos":measures(allrows),
      "por_localidad":{site:measures([r for r in allrows if r["punto_oaf_objetivo"]==site]) for site in SITES},
      "temperatura_senamhi_real_descargada_automaticamente":False,
      "validacion_instrumental_independiente_certificada":False,
      "habilidad_prospectiva_8e_demostrada":False,
      "intervalos_predictivos_90_calibrados":False,
      "comparacion_de_modelos":"ERA5-Land 8D con estación, NO error de emisión 8E",
      "notas":[
       "Los datos de entrada han de aportarse con autorización y trazabilidad; el programa no descarga SENAMHI.",
       "Solo meses con todos los días de Tmedia válida; no se imputa ausencia ni se estima Tmedia como (Tmax+Tmin)/2.",
       "La media diaria y su agregación mensual exigen documentación de comparabilidad temporal con ERA5-Land.",
       "Distancia de cribado 20 km no garantiza misma exposición, altitud ni representatividad; la auditoría humana continúa siendo necesaria.",
       "Incluso con pares ERA5-estación, la comparación no prueba habilidad de los pronósticos prospectivos 8E.",
       "La independencia frente a la asimilación/forzamiento del reanálisis necesita evidencia adicional."
      ],
      "trazabilidad":{"manifest_sha256":sha(root/MANIFEST),"serie_era5_8d_sha256":sha(root/HIST),
         "archivos_originales":[{"codigo_estacion":m["code"],"archivo":m["archivo_csv"],
            "sha256":sha(m["path"]),"fecha_publicacion_utc":m["fecha_publicacion_utc"],
            "url_fuente":m["url_fuente"]} for m in manifest]}
    }
    return out,allrows

def output_csv(rows):
    buf=io.StringIO(newline="")
    writer=csv.DictWriter(buf,fieldnames=FIELDS_MONTHLY,lineterminator="\n")
    writer.writeheader()
    for row in rows:writer.writerow({k:"" if row.get(k) is None else
                                     str(row[k]).lower() if isinstance(row.get(k),bool) else row.get(k)
                                     for k in FIELDS_MONTHLY})
    return buf.getvalue()

def publish(root,check):
    status,rows=evaluate(root)
    folder=root/OUTPUT
    targets={folder/"estado_8i.json":json.dumps(status,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
             folder/"comparacion_mensual_8i.csv":output_csv(rows)}
    if not check:folder.mkdir(parents=True,exist_ok=True)
    for path,content in targets.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("Salida 8I no corresponde a fuentes verificadas: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8I","archivos":status["n_archivos_fuente_autorizados"],
       "meses_pareados":status["n_meses_con_pares_estacion_era5"],
       "habilidad_prospectiva_demostrada":False,"revision":check},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    publish(args.root,args.check)

if __name__=="__main__":main()
