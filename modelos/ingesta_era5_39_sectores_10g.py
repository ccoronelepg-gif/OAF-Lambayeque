#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10G — traceable ERA5 atmospheric grid samples for 39 experimental sectors.

ERA5 via Open-Meteo historical archive, NOT observations at farms or
instrumental ground truth. A polygon's representative point is one SAMPLE,
not a polygon area mean. Multiple polygons can map to the same ERA5 0.25° grid.
No inference/alerts until full QA and independent benchmarking.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math,time,urllib.error,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import shape,Point

ROOT=Path(__file__).resolve().parents[1]
GEO=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
AUDIT=ROOT/"datos/validacion_9w/auditoria_puente_9w.json"
OUT=ROOT/"datos/atmosfera_sectorial_10g"
MANIFEST=OUT/"puntos_y_advertencias_10g.json"
MONTHLY=OUT/"muestra_era5_mensual_10g.csv"
PROBE=OUT/"piloto_era5_2023_10g.json"
REPORT=OUT/"auditoria_atmosfera_10g.json"
API="https://archive-api.open-meteo.com/v1/archive"
VARS=("temperature_2m_mean","relative_humidity_2m_mean","wind_speed_10m_mean",
      "shortwave_radiation_sum","pressure_msl_mean","cloud_cover_mean",
      "vapour_pressure_deficit_max")
MONTH_COLS=("mes","sector","estrato","consulta_lat","consulta_lon","era5_celda_lat",
  "era5_celda_lon","era5_elevacion_m","dias_validos","temperatura_aire_c",
  "humedad_relativa_pct","viento_10m_m_s","radiacion_corta_mj_m2",
  "presion_nivel_mar_hpa","nubosidad_pct","vpd_max_diario_media_mes_kpa",
  "producto","seleccion_celda","punto_representativo_no_promedio_areal",
  "medicion_instrumental","fecha_extraccion_utc")
YEAR_CHUNKS=((1996,2005),(2006,2015),(2016,2025))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding="utf8"))
def manifest():
 a=read(AUDIT)
 if a["fase"]!="9W" or len(a["sectores_evaluables"])!=39:raise ValueError("Auditoría 9W no apta")
 collection=read(GEO)
 if collection.get("metadata",{}).get("limite_regional_oficial") is True:
  raise ValueError("Verificar por qué sectores 9K aparecen como límite oficial")
 out=[]
 for f in collection["features"]:
  sector=f["properties"]["id_sector"]
  if sector not in a["sectores_evaluables"]:continue
  geom=shape(f["geometry"])
  if geom.is_empty or not geom.is_valid:raise ValueError("Sector geometría inválida "+sector)
  p=geom.representative_point()
  if not geom.covers(Point(p.x,p.y)):raise ValueError("Punto fuera del sector "+sector)
  prop=f["properties"]
  lo,hi=prop.get("alt_min_nodos_m"),prop.get("alt_max_nodos_m")
  out.append({"sector":sector,"piso":prop.get("estrato"),
   "lon":round(p.x,6),"lat":round(p.y,6),
   "alt_min_nodos_m":lo,"alt_max_nodos_m":hi,
   "altitud_revisar":bool(lo is not None and float(lo)<0),
   "area_dibujo_km2":prop.get("area_dibujo_km2"),
   "proveniencia":"Punto interior representativo del polígono 9K, EPSG:4326",
   "no_es_estacion":True,"no_es_media_poligono":True,
   "homogeneidad_validada":False})
 out.sort(key=lambda v:v["sector"])
 if len(out)!=39 or len({r["sector"] for r in out})!=39:raise ValueError("No se obtuvieron 39 puntos")
 result={"fase":"10G","estado":"PUNTOS_AUDITADOS_NO_MEDICION_ESTACIONAL",
  "fecha_corte":"2026-10-17","fuentes_sha256":{
   "poligonos_9k":sha(GEO),"auditoria_9w":sha(AUDIT)},
  "seleccion_punto":"shapely.geometry.representative_point; garantizado dentro de la geometria 9K",
  "consulta":"Open-Meteo Historical ERA5; 0.25 grados; punto representativo NO promedios poligonales",
  "fuente_web":"https://open-meteo.com/en/docs/historical-weather-api",
  "cota_negativa_revisar":True,"n_sectores":39,"puntos":out,
  "no_autorizado_alertas":True}
 return result
def request(params):
 url=API+"?"+urllib.parse.urlencode(params)
 last=None
 for attempt in range(5):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"OAF-Lambayeque-10G-research/1.0 (GitHub Open Data)"})
   with urllib.request.urlopen(req,timeout=180) as response:
    if response.status!=200:raise ValueError("Respuesta "+str(response.status))
    data=response.read()
   return json.loads(data),{"request_url":url,"response_sha256":hashlib.sha256(data).hexdigest(),
      "response_bytes":len(data),"downloaded_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as err:
   last=err
   if isinstance(err,urllib.error.HTTPError) and err.code not in (429,500,502,503,504):
    detail=err.read(3000).decode("utf8","replace")
    raise RuntimeError("Open-Meteo solicitud inválida "+str(err)+"; detalle: "+detail+"; parametros: "+url) from err
   time.sleep(min(30,3*(attempt+1)**2))
 raise RuntimeError("No se pudo obtener ERA5 tras 5 intentos: "+str(last))
def chunks(seq,n):
 for i in range(0,len(seq),n):yield seq[i:i+n]
def build_params(points,start,end):
 return {"latitude":",".join(str(x["lat"]) for x in points),
  "longitude":",".join(str(x["lon"]) for x in points),
  "start_date":start,"end_date":end,"timezone":"GMT",
  "daily":",".join(VARS),"models":"era5",
  "wind_speed_unit":"ms","cell_selection":"nearest",
  "elevation":",".join(["nan"]*len(points))}
def mean(values):return sum(values)/len(values)
def convert(node,response,metadata,expected_first,expected_last):
 daily=response.get("daily")
 if not isinstance(daily,dict) or not isinstance(daily.get("time"),list):
  raise ValueError("La API no retornó fechas diarias")
 timestamps=daily["time"]
 if timestamps[0]!=expected_first or timestamps[-1]!=expected_last:
  raise ValueError("Ventana API equivocada: "+node["sector"])
 for name in VARS:
  if name not in daily or len(daily[name])!=len(timestamps):
   raise ValueError("Variable o longitud ausente: "+name+" "+node["sector"])
 cell_lat=float(response.get("latitude",999));cell_lon=float(response.get("longitude",999))
 if abs(cell_lat-node["lat"])>.26 or abs(cell_lon-node["lon"])>.26:
  raise ValueError("ERA5 cell demasiado distante "+node["sector"])
 if response.get("daily_units",{}).get("wind_speed_10m_mean") not in ("m/s","m s-1"):
  raise ValueError("Unidad de viento inesperada")
 if response.get("daily_units",{}).get("shortwave_radiation_sum") not in ("MJ/m²","MJ/m2"):
  raise ValueError("Radiación sin unidad MJ/m2")
 if response.get("daily_units",{}).get("pressure_msl_mean") not in ("hPa",):
  raise ValueError("Presión sin hPa")
 for column in ("temperature_2m_mean","relative_humidity_2m_mean","cloud_cover_mean"):
  if not response.get("daily_units",{}).get(column):
   raise ValueError("Unidad de "+column+" ausente")
 by=defaultdict(list)
 for i,day in enumerate(timestamps):
  observed=dt.date.fromisoformat(day)
  row={}
  for col in VARS:
   v=daily[col][i]
   if v is None or not math.isfinite(float(v)):
    raise ValueError("Dato diario ERA5 faltante "+node["sector"]+" "+day+" "+col)
   row[col]=float(v)
  if not (-40<=row["temperature_2m_mean"]<=60 and
         0<=row["relative_humidity_2m_mean"]<=100 and
         0<=row["cloud_cover_mean"]<=100 and
         870<=row["pressure_msl_mean"]<=1100 and
         0<=row["wind_speed_10m_mean"]<=70 and
         0<=row["shortwave_radiation_sum"]<=45 and
         0<=row["vapour_pressure_deficit_max"]<=20):
   raise ValueError("Dominio físico inesperado "+node["sector"]+" "+day)
  by[day[:7]].append(row)
 out=[]
 for month,rows in sorted(by.items()):
  year=int(month[:4]);mo=int(month[-2:])
  expected=(dt.date(year+int(mo==12),1 if mo==12 else mo+1,1)-dt.date(year,mo,1)).days
  if len(rows)!=expected:raise ValueError("Faltan días "+node["sector"]+" "+month)
  data={"mes":month,"sector":node["sector"],"estrato":node["piso"],
   "consulta_lat":node["lat"],"consulta_lon":node["lon"],
   "era5_celda_lat":round(cell_lat,5),"era5_celda_lon":round(cell_lon,5),
   "era5_elevacion_m":response.get("elevation",""),"dias_validos":len(rows),
   "temperatura_aire_c":round(mean([r["temperature_2m_mean"] for r in rows]),4),
   "humedad_relativa_pct":round(mean([r["relative_humidity_2m_mean"] for r in rows]),4),
   "viento_10m_m_s":round(mean([r["wind_speed_10m_mean"] for r in rows]),4),
   "radiacion_corta_mj_m2":round(sum(r["shortwave_radiation_sum"] for r in rows),4),
   "presion_nivel_mar_hpa":round(mean([r["pressure_msl_mean"] for r in rows]),4),
   "nubosidad_pct":round(mean([r["cloud_cover_mean"] for r in rows]),4),
   "vpd_max_diario_media_mes_kpa":round(mean([r["vapour_pressure_deficit_max"] for r in rows]),4),
   "producto":"ERA5-0.25deg-OpenMeteo-historical-reanalysis",
   "seleccion_celda":"nearest","punto_representativo_no_promedio_areal":"true",
   "medicion_instrumental":"false",
   "fecha_extraccion_utc":metadata["downloaded_utc"]}
  out.append(data)
 return out
def retrieve(points,year_chunks,limit_batches=None):
 results=[];ledger=[];samples={}
 for years in year_chunks:
  for batch_id,subset in enumerate(chunks(points,5)):
   if limit_batches is not None and batch_id>=limit_batches:break
   start=f"{years[0]}-01-01";end=f"{years[1]}-12-31"
   response,request_meta=request(build_params(subset,start,end))
   if isinstance(response,dict):
    response=[response]
   if len(response)!=len(subset):
    raise ValueError("Lista de ubicaciones API incompleta: esperado "+str(len(subset)))
   ledger.append({"batch":batch_id,"period":str(years[0])+"-"+str(years[1]),
     "sectores":[p["sector"] for p in subset],**request_meta})
   for node,resp in zip(subset,response):
    entries=convert(node,resp,request_meta,start,end)
    results.extend(entries)
    samples.setdefault(node["sector"],set()).add((entries[0]["era5_celda_lat"],entries[0]["era5_celda_lon"]))
   print("10G_BLOQUE",years,batch_id,"sectores",len(subset),"filas acumuladas",len(results),flush=True)
   time.sleep(.4)
 if any(len(v)!=1 for v in samples.values()):
  raise ValueError("Proveedor varió celda de un mismo sector entre periodos")
 return results,ledger
def audit_rows(rows,points,full):
 count_months=360 if full else 12
 keys=[(r["sector"],r["mes"]) for r in rows]
 if len(keys)!=len(set(keys)) or len(rows)!=len(points)*count_months:
  raise ValueError("Duplicados o registro incompleto ERA5")
 expected={f"{y}-{m:02d}" for y in (range(1996,2026) if full else [2023]) for m in range(1,13)}
 sector_cells=defaultdict(set)
 all_cols=set()
 for r in rows:
  if r["mes"] not in expected:raise ValueError("Mes inesperado")
  key=(r["era5_celda_lat"],r["era5_celda_lon"])
  sector_cells[r["sector"]].add(key);all_cols.add(key)
 if len(sector_cells)!=len(points) or any(len(v)!=1 for v in sector_cells.values()):
  raise ValueError("Celda no estable o sectores sin histórico")
 if len(all_cols)<2:raise ValueError("Consulta devolvió la misma celda para toda Lambayeque")
 unique=len(all_cols)
 pairs=defaultdict(list)
 for sid,loc in sector_cells.items():pairs[next(iter(loc))].append(sid)
 return {"n_sectores":len(points),"n_meses_por_sector":count_months,
   "filas":len(rows),"n_celdas_era5_distintas":unique,
   "sectores_en_celdas_era5_compartidas":sum(len(s) for s in pairs.values() if len(s)>1),
   "grupos_celdas_compartidas":[{"celda":list(k),"sectores":sorted(v)}
      for k,v in pairs.items() if len(v)>1],
   "observacion":"Un punto interior por polígono. NO promedio espacial, ni estación; 0.25° puede compartirse.",
   "altitud_inconsistente":"S001 cota negativa DEM revisar; ERA5 elevation es atributo diferente, no validación DEM.",
   "dataset_completo":full,"fecha_original_as_issued_disponible":False,
   "verificacion_instrumental":False,"alertas_activadas":False}
def write_csv(rows,path):
 with path.open("w",newline="",encoding="utf8") as f:
  writer=csv.DictWriter(f,fieldnames=MONTH_COLS);writer.writeheader();writer.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=("manifest","pilot","full","verify"),default="manifest")
 a=p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 document=manifest()
 if a.mode=="verify":
  if not REPORT.exists() or not MONTHLY.exists():raise ValueError("No existe ejecución completa")
  state=read(REPORT)
  with MONTHLY.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
  proof=audit_rows(rows,document["puntos"],full=True)
  if state["sha256_matriz"]!=sha(MONTHLY) or proof["filas"]!=14040 or state["alertas_activadas"] is not False:
   raise ValueError("La matriz no reproduce 39x360 o perdió integridad")
  print("10G_VERIFICADO",json.dumps(proof,ensure_ascii=False),flush=True);return
 MANIFEST.write_text(json.dumps(document,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 if a.mode=="manifest":
  print("10G_MANIFIESTO",len(document["puntos"]),"puntos,","cota_negativa",sum(x["altitud_revisar"] for x in document["puntos"]),flush=True)
  return
 if a.mode=="pilot":
  rows,ledger=retrieve(document["puntos"],((2023,2023),))
  summary=audit_rows(rows,document["puntos"],full=False)
  report={"fase":"10G","modo":"piloto_2023",
    "fuente_geometria_sha256":sha(GEO),"proveedor":"Open-Meteo ERA5 0.25°",
    "campos_requeridos":list(VARS),"resumen":summary,
    "auditoria_respuestas":ledger,
    "alertas_activadas":False}
  PROBE.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  print("10G_PILOTO",json.dumps(summary,ensure_ascii=False),flush=True);return
 rows,ledger=retrieve(document["puntos"],YEAR_CHUNKS)
 summary=audit_rows(rows,document["puntos"],full=True)
 rows.sort(key=lambda r:(r["sector"],r["mes"]))
 write_csv(rows,MONTHLY)
 report={"fase":"10G","modo":"extraccion_1996_2025",
  "periodo":"1996-01/2025-12","n_variables":7,
  "variable_radiacion":"MJ/m² mensual acumulado de shortwave_radiation_sum diaria",
  "variable_presion":"pressure_msl_mean al nivel del mar, NO presion de parcela",
  "fuente_geometria_sha256":sha(GEO),
  "proveedor":"Open-Meteo Historical ERA5 0.25° nearest; no elevation downscaling",
  "modelo_proveedor":"era5","cell_selection":"nearest","elevation_param":"nan",
  "campos_requeridos":list(VARS),"resumen":summary,
  "auditoria_respuestas":ledger,
  "sha256_matriz":sha(MONTHLY),"sha256_puntos":sha(MANIFEST),
  "no_usar_como_prediccion_operativa":True,"datos_ex_post_reprocesados":True,
  "verdaderos_promedios_poligonales":False,
  "variables_homologadas_solo_para_puntos_era5":True,
  "modelo_operativo_ganador":None,"alertas_activadas":False,
  "limitaciones":[
   "No estaciones ni registros de parcelas. Una ubicación representativa por polígono.",
   "La grilla ERA5 0,25 grados puede compartir celdas entre sectores. No hay 39 píxeles independientes garantizados.",
   "Las zonas 9K son polígonos experimentales, no los límites oficiales de Lambayeque.",
   "La cota negativa S001 no se corrige automáticamente.",
   "El producto ERA5 actualizado ex post no equivale a snapshots disponibles en la fecha histórica.",
   "No se ha realizado evaluación RF/GCN con variables 10G en esta etapa de adquisición.",
   "Ninguna probabilidad de lluvia significa probabilidad de El Niño o infección real." ]}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10G_COMPLETO",json.dumps({"filas":len(rows),"celdas":summary["n_celdas_era5_distintas"],
   "compartidas":summary["sectores_en_celdas_era5_compartidas"],
   "hash":report["sha256_matriz"]},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
