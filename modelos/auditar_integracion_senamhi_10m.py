#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10M: enforce quality gates for unreviewed SENAMHI station rainfall archive."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,math,hashlib,datetime as dt,calendar
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/"datos/senamhi_estaciones_10m"
CSV=DIRECTORY/"resumen_mensual_senamhi_observado.csv"
MANIFEST=DIRECTORY/"manifest_fuentes_10m.json"
def analyze():
 source=json.loads(MANIFEST.read_text("utf-8"))
 with CSV.open(newline="",encoding="utf-8-sig") as fp:rows=list(csv.DictReader(fp))
 if len(rows)!=48 or source["fase"]!="10M" or source["resumen"]["archivos_nuevos"]!=50:raise ValueError("Invalid 10M station archive")
 if source["validacion"]["control_calidad_formal"] or source["validacion"]["entrenamiento_RF_activado"] or source["validacion"]["independencia_de_CHIRPS"]:raise ValueError("Unjustified observational/operational assertion")
 keys=set();count=Counter();complete=Counter();sums=defaultdict(float)
 for r in rows:
  key=(r["codigo_estacion"],r["mes"]);sid,month=key
  if len(sid)!=6 or not sid.isdigit() or key in keys:raise ValueError("Repeated or invalid station-month "+str(key))
  keys.add(key);count[sid]+=1
  year,mo=map(int,month.split("-"))
  days=calendar.monthrange(year,mo)[1]
  if int(r["dias_del_mes"])!=days:raise ValueError("Calendar mismatch "+str(key))
  total=r["acumulado_mm_completo"].strip()
  is_complete=r["completo_qc_formal"].lower()=="true"
  if is_complete:
   if int(r["dias_con_registro"])!=days or int(r["dias_sin_fila"]) or int(r["registros_sin_dato"]) or int(r["registros_traza"]) or not total:raise ValueError("Full-month declaration incorrect "+str(key))
   rain=float(total)
   if not math.isfinite(rain) or rain<0:raise ValueError("Rain invalid")
   complete[sid]+=1;sums[sid]+=rain
  elif total:raise ValueError("Partial month includes rainfall sum falsely reported "+str(key))
 if count["153102"]!=26 or count["000307"]!=14 or complete["153102"]!=26 or complete["000307"]!=14:
  raise ValueError("Mountain months missing")
 if abs(sums["153102"]-2434.8)>0.001 or abs(sums["000307"]-1065.0)>0.001:
  raise ValueError("Rainfall total changed")
 sources=source["fuentes_nuevas"]
 if len(sources)!=50 or sum(x["n_registros"] for x in sources)!=1515 or len(set(x["archivo"] for x in sources))!=50:raise ValueError("Missing original-file hashes")
 if any(len(x["sha256"])!=64 or not all(y in "0123456789abcdef" for y in x["sha256"].lower()) for x in sources):
  raise ValueError("SHA digest format")
 print("10M_AUDITORIA_EXITOSA",json.dumps({"n_meses_estaciones":len(rows),"cueva":dict(n=count["153102"],mm=round(sums["153102"],1)),"incahuasi":dict(n=count["000307"],mm=round(sums["000307"],1)),"entradas_al_RF":False,"fuentes":len(sources)}))
if __name__=="__main__":analyze()
