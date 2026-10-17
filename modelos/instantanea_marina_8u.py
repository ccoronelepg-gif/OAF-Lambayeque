#!/usr/bin/env python3
"""8U: offshore snapshot forecast of currents and SST from Open-Meteo Marine.

This is NOT 1996–2025 climatology, NOT in situ observations and NOT
Humboldt current validation. Modelled current direction is TOWARDS heading,
unlike meteorological wind direction FROM heading. Audit raw JSON and units.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,math,statistics
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
BASE="datos/marino_8u"
API="https://marine-api.open-meteo.com/v1/marine"
POINTS=(
 {"id":"Norte_mar_abierto","latitude":-6.1,"longitude":-80.7},
 {"id":"Centro_mar_abierto","latitude":-6.5,"longitude":-80.7},
 {"id":"Sur_mar_abierto","latitude":-6.9,"longitude":-80.7})
VARS=("sea_surface_temperature","ocean_current_velocity","ocean_current_direction")
def sha(x):return hashlib.sha256(x).hexdigest()
def request():
 return API+"?"+urlencode({
   "latitude":",".join(str(p["latitude"]) for p in POINTS),
   "longitude":",".join(str(p["longitude"]) for p in POINTS),
   "hourly":",".join(VARS),"forecast_days":3,
   "timezone":"America/Lima","cell_selection":"sea",
   "velocity_unit":"ms"})
def source_path(root,day):
 base=root/BASE/"fuentes"
 return base/f"ocean_forecast_{day}.json.gz",base/f"ocean_forecast_{day}.meta.json"
def check(raw):
 d=json.loads(raw)
 if not isinstance(d,list) or len(d)!=3:raise ValueError("No hay tres puntos oceánicos")
 parsed=[]
 for p,obj in zip(POINTS,d):
  if not isinstance(obj,dict) or obj.get("error"):
   raise ValueError("Proveedor marino informó error")
  if obj.get("timezone")!="America/Lima" or obj.get("utc_offset_seconds")!=-18000:
   raise ValueError("Huso horario marino no coincide")
  positions=(obj.get("latitude"),obj.get("longitude"))
  if any(type(z) not in (int,float) or not math.isfinite(z) for z in positions):
   raise ValueError("Faltan coordenadas de celda marina")
  if abs(positions[0]-p["latitude"])>.3 or abs(positions[1]-p["longitude"])>.3:
   raise ValueError("Celda oceánica demasiado distante")
  hour=obj.get("hourly") or {}
  times=hour.get("time")
  units=obj.get("hourly_units") or {}
  if not isinstance(times,list) or not 40<=len(times)<=80 or len(set(times))!=len(times):
   raise ValueError("Pronóstico 3 días incompleto")
  for k in VARS:
   if not isinstance(hour.get(k),list) or len(hour[k])!=len(times):
    raise ValueError("Falta variable marina "+k)
  if units.get("sea_surface_temperature") not in ("°C","C"):
   raise ValueError("SST con unidad desconocida")
  if units.get("ocean_current_velocity") not in ("m/s","ms"):
   raise ValueError("Velocidad marina no está en m/s")
  if units.get("ocean_current_direction") not in ("°","deg"):
   raise ValueError("Dirección marina sin grados")
  # Null values are legitimately absent; do not manufacture inshore currents.
  valid=[]
  for i,t in enumerate(times):
   a,b,c=(hour[v][i] for v in VARS)
   if any(z is None for z in (a,b,c)):continue
   if any(type(z) not in (int,float) or not math.isfinite(z) for z in (a,b,c)):
    raise ValueError("Variable marina fuera de límites numéricos")
   if not(-3<a<38 and 0<=b<=5 and 0<=c<=360):
    raise ValueError("Variable marina fuera de rango de seguridad")
   rad=math.radians(c)
   # marine TO heading, positive east/north
   u=b*math.sin(rad);v=b*math.cos(rad)
   valid.append({"time":t,"sst_c":a,"speed_ms":b,"heading_to_deg":c,"u_east_ms":u,"v_north_ms":v})
  parsed.append({"id":p["id"],"latitud_solicitada":p["latitude"],
     "longitud_solicitada":p["longitude"],
     "latitud_celda":positions[0],"longitud_celda":positions[1],
     "n_horas_con_las_3_variables":len(valid),
     "n_horas_totales":len(times),
     "sst_media_modelada_c":round(statistics.mean(r["sst_c"] for r in valid),4) if valid else None,
     "velocidad_media_modelada_ms":round(statistics.mean(r["speed_ms"] for r in valid),4) if valid else None,
     "u_media_modelada_ms":round(statistics.mean(r["u_east_ms"] for r in valid),4) if valid else None,
     "v_media_modelada_ms":round(statistics.mean(r["v_north_ms"] for r in valid),4) if valid else None,
     "primer_horario":times[0],"ultimo_horario":times[-1]})
 return parsed

def gather(root,day):
 file,meta=source_path(root,day)
 if file.exists() or meta.exists():
  if not file.exists() or not meta.exists():
   raise ValueError("Fuente marina parcialmente archivada")
  raw=gzip.decompress(file.read_bytes())
  info=json.loads(meta.read_text(encoding="utf-8"))
  if info.get("sha256_original")!=sha(raw) or info.get("url")!=request() or info.get("date_utc")!=day:
   raise ValueError("Fuente oceánica archivada manipulada")
  return raw,info
 file.parent.mkdir(parents=True,exist_ok=True)
 url=request()
 with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-8U-Marine/1.0"}),timeout=100) as response:
  if response.status!=200:raise ValueError("API marina HTTP inesperado")
  raw=response.read(1_500_001)
 if len(raw)>1_500_000:raise ValueError("API marina demasiado grande")
 check(raw)
 info={"fase":"8U","componente":"pronostico_marino_archivado",
       "date_utc":day,"downloaded_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "sha256_original":sha(raw),"url":url,"periodo":"3_dias_pronosticados_no_30_anios",
       "fuente":"Open-Meteo Marine Forecast SMOC MeteoFrance",
       "modelo_no_corrientometro_ni_boya":True,
       "ocean_current_direction_hacia_donde_fluye":True,
       "corrientes_historicas_1996_2025_verificadas":False,
       "no_admite_alerta_ni_habilidad_predictiva_demostrada":True}
 file.write_bytes(gzip.compress(raw,mtime=0))
 meta.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return raw,info

def publish(root,day,fetch=False):
 if fetch:
  try: raw,meta=gather(root,day)
  except (HTTPError,ValueError,OSError,TimeoutError) as exc:
   print("No se publica observación marina inventada",str(exc));return
 else:
  f,m=source_path(root,day)
  if not f.exists():raise ValueError("No hay fuente marina del día")
  raw=gzip.decompress(f.read_bytes());meta=json.loads(m.read_text(encoding="utf-8"))
  if meta.get("sha256_original")!=sha(raw):raise ValueError("SHA marino no coincide")
 rows=check(raw)
 report={"fase":"8U","estado":"pronostico_marino_modelado_archivado",
   "fecha_de_consulta_utc":meta["downloaded_utc"],"archivo_fecha":day,
   "periodo":"hasta 3 días de pronóstico, no climatología 1996–2025",
   "fuente":"Open-Meteo Marine / corrientes y SST modeladas MeteoFrance",
   "sha256_respuesta_marina_original":meta["sha256_original"],
   "n_puntos_marinos":len(rows),
   "puntos":rows,
   "corrientes_historicas_30_anios_integradas":False,
   "vientos_modelados_son_distintos_de_corrientes_marinas":True,
   "celdas_modeladas_no_son_boyas":True,
   "validacion_instrumental_independiente":False,
   "habilidad_pronostico_marino_demostrada":False,
   "modelo_integrado_viento_sst_corriente_retrovalidado":False,
   "advertencias":[
    "Pronóstico generado por modelos marinos, no observación instrumental ni verificación futura.",
    "No extrapolar tres puntos marinos a la corriente de Humboldt ni al frente costero.",
    "Dirección marina HACIA donde fluye, viento meteorológico DESDE donde sopla.",
    "Los modelos cercanos a costa presentan incertidumbre elevada.",
    "No utilizar en backtest 1996-2025, esta fuente no cubre ese periodo."
   ]}
 out=root/BASE/"estado_marino_8u.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 print(json.dumps({"points":len(rows),"n_with_all_variables":sum(r["n_horas_con_las_3_variables"]>0 for r in rows)},ensure_ascii=False))

if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--root",type=Path,default=ROOT)
 parser.add_argument("--fetch",action="store_true")
 parser.add_argument("--date",default=datetime.now(timezone.utc).date().isoformat())
 a=parser.parse_args();publish(a.root,a.date,a.fetch)
