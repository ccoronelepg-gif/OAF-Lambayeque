#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent QA of OAF 10L mountain results and dashboard availability."""
import json,csv,hashlib,collections,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/montanas_10l"
SUMMARY=BASE/"evaluacion_montanas_10l.json"
PRED=BASE/"predicciones_lluvia_montanas_10l.csv"
MAP=BASE/"sectores_mejora_montana_10l.geojson"
SERIES=BASE/"series_montana_10l.json"
HTML=ROOT/"optimizacion-lluvia-montana-10l.html"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=json.loads(SUMMARY.read_text("utf8"))
 geo=json.loads(MAP.read_text("utf8"))
 ts=json.loads(SERIES.read_text("utf8"))["datos"]
 with PRED.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
 if r["fase"]!="10L" or r["n_sectores_objetivo"]!=11 or len(rows)!=660 or len(ts)!=660:
  raise ValueError("Highland data missing")
 if len(geo["features"])!=39 or r["restricciones"]["alertas_habilitadas"] or r["restricciones"]["modelo_enfermedades"]:
  raise ValueError("Highland map/claims invalid")
 for key,filename in (("resultados_csv",PRED),("mapa_geojson",MAP),("series_json",SERIES)):
  if sha(filename)!=r["hashes"][key]:raise ValueError("Checksum differ "+str(filename))
 keys={(x["sector"],x["mes"]) for x in rows}
 if len(keys)!=660 or any(y[:4] not in ("2021","2022","2023","2024","2025") for _,y in keys):
  raise ValueError("Data duplicate or temporal leakage into map")
 medium={x["sector"] for x in rows if x["paisaje"]=="ladera_media"}
 high={x["sector"] for x in rows if x["paisaje"]=="cumbres"}
 if len(medium)!=8 or len(high)!=3:raise ValueError("Strata counts wrong")
 for band in ("vertiente_media","alta_montana","total_montana"):
  metric=r["resultados"][band]
  subset=rows if band=="total_montana" else [x for x in rows if x["paisaje"]==("ladera_media" if band=="vertiente_media" else "cumbres")]
  yy=[float(x["observado_mm"]) for x in subset]
  for col,label in (("nuevo_rf_mm","mae_optimizado_mm"),("rf_10k_mm","mae_rf_10k_mm"),("climatologia_mm","mae_climatologia_mm")):
   value=sum(abs(float(x[col])-float(x["observado_mm"])) for x in subset)/len(subset)
   if abs(value-metric[label])>.001:raise ValueError("MAE inaccurate "+band+" "+label)
 high_dec=[x for x in r["seleccion_solo_2016_2018"] if x["paisaje"]=="cumbres" and x["n_hold_sites"]>0]
 if len(high_dec)!=1 or not high_dec[0]["sin_sector_alto_independiente"] or high_dec[0]["chosen_weight"]!=0:
  raise ValueError("Unverified highland RF incorrectly applied")
 if r["resultados"]["alta_montana"]["mae_optimizado_mm"]!=r["resultados"]["alta_montana"]["mae_climatologia_mm"]:
  raise ValueError("Highland abstention not transparent")
 h=HTML.read_text("utf8");portal=(ROOT/"index.html").read_text("utf8")
 for token in ['id="map"','id="summary"','id="sector"','id="year"','id="zona"','id="plot"','id="annual"',"NO han sido reentrenadas"]:
  if token not in h:raise ValueError("Missing dashboard element "+token)
 if 'id="oaf-montana-rf-10l"' not in portal:raise ValueError("Portal climate not linked")
 blocks=re.findall(r"<script[^>]*>(.*?)</script>",h,re.S)
 if len(blocks)<1 or len(blocks[-1])<4200:raise ValueError("Missing dashboard JavaScript")
 path=BASE/"_10l_js_validation.cjs";path.write_text(blocks[-1],encoding="utf8")
 print("10L_AUDITORIA_INTEGRAL_OK",{"n":len(rows),"altas":len(high),"medias":len(medium),
   "global":r["resultados"]["total_montana"],"high_fallback":True})
if __name__=="__main__":main()
