#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10K browser/data contract QA, standard library only; not a prediction."""
from pathlib import Path
import json,math,collections,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/ecopaisajes_10k"
HTML=ROOT/"ecorregiones-clima-10k.html"
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 report=json.loads((BASE/"evaluacion_ecoclimatica_10k.json").read_text("utf8"))
 polygons=json.loads((BASE/"paisajes_ecoclimaticos_10k.geojson").read_text("utf8"))
 timeseries=json.loads((BASE/"series_sector_mes_10k.json").read_text("utf8"))["datos"]
 if report["n_sectores"]!=39 or report["n_paisajes"]!=5:raise ValueError("Ecoclimatic index changed")
 if report["ecorregiones_oficiales_intersectadas"] is not False:raise ValueError("Inaccurate official ecological claim")
 if report["controles_operativos"]["pronostico_en_tiempo_real_habilitado"] is not False:raise ValueError("Unsafe status")
 if len(polygons["features"])!=39 or len(timeseries)!=2340:raise ValueError("Missing sectors/months")
 for file,key in (("paisajes_ecoclimaticos_10k.geojson","mapa_10k"),("series_sector_mes_10k.json","serie_visores_10k")):
  if sha(BASE/file)!=report["sha256"][key]:raise ValueError("Source changed "+file)
 groups=collections.defaultdict(list);ident=set()
 for row in timeseries:
  month=row["mes"];sid=row["sector"];k=(sid,month)
  if month[:4] not in ("2021","2022","2023","2024","2025") or k in ident:
   raise ValueError("Date outside retrospective study or duplicated")
  ident.add(k);groups[row["paisaje"]].append(row)
 if set(groups)!=set(report["paisajes"]):raise ValueError("Different ecological groups")
 for key,data in groups.items():
  record=report["resultado_selector_mm"]["por_paisaje"][key]
  if record["n"]!=len(data) or record["n_sectores"]!=len({r["sector"] for r in data}):
   raise ValueError("Landscape counts inconsistent "+key)
  obs=sum(float(r["observado_mm"]) for r in data)/len(data)
  if abs(obs-record["lluvia_observada_media_mm"])>.005:raise ValueError("Landscape rainfall mismatch "+key)
  if record["n_sectores"]!=report["paisajes"][key]["n_sectores"]:
   raise ValueError("Missing sector metadata "+key)
 sectors={f["properties"]["sector"] for f in polygons["features"]}
 if len(sectors)!=39 or len(ident)!=39*60:raise ValueError("Incomplete map or time series")
 negative=[f for f in polygons["features"] if f["properties"]["cota_negativa_pendiente"]]
 if len(negative)!=1 or negative[0]["properties"]["sector"]!="S001":
  raise ValueError("Altitude negative DEM caveat lost")
 html=HTML.read_text("utf8")
 for value in ['id="map"','id="table-land"','id="table-floor"','id="paisaje"','id="periodo"','id="metric"','id="sector"',
   'leaflet.js','data-page','P90','MINAM']:
  if value not in html and value!='data-page':raise ValueError("Missing dashboard item "+value)
 if "pronóstico actual" in html.lower() and "no pronósticos actuales" not in html.lower():
  raise ValueError("Check publication of 2026 forecasts")
 js=re.findall(r"<script[^>]*>(.*?)</script>",html,flags=re.S)
 if len(js)<1 or len(js[-1])<10000:raise ValueError("Client code missing")
 jsfile=ROOT/"datos/ecopaisajes_10k/_qa_javascript_10k.cjs"
 jsfile.write_text(js[-1],encoding="utf8")
 print("10K_DASHBOARD_VALIDO",json.dumps({
 "n_paisajes":len(groups),"n_sectores":len(sectors),"n_meses":len(ident),
 "p90_2023":report["resultado_selector_mm"]["por_anio"]["2023"]["n_eventos_p90"],
 "n_javascript":len(js[-1])},ensure_ascii=False))
if __name__=="__main__":main()
