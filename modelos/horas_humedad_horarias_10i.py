#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Meteorología auxiliar NO predictiva de enfermedades. Horas de humedad.

Input: observations/hourly_model_data CSV with ONE record per clock hour,
without gaps. These are NOT reconstructable from monthly rainfall CHIRPS or
monthly NASA RH. Output is humidity-duration statistics, NOT leaf-wetness
hours nor infection prediction. Use hourly in consistent local timestamp.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,json,math
from collections import defaultdict
from pathlib import Path

FIELDS=("fecha_hora_local","localidad","humedad_relativa_pct","lluvia_hora_mm")
def analyze(rows,threshold=90.0):
 if not 0<threshold<=100:raise ValueError("Umbral RH fuera de (0,100]")
 groups=defaultdict(list)
 for r in rows:
  if any(not r.get(k) for k in FIELDS):raise ValueError("Hora, localidad, RH y lluvia son necesarios")
  time=dt.datetime.fromisoformat(r["fecha_hora_local"])
  if time.minute or time.second:raise ValueError("Hora debe iniciar en HH:00")
  rh=float(r["humedad_relativa_pct"]);rain=float(r["lluvia_hora_mm"])
  if not math.isfinite(rh) or not math.isfinite(rain) or not 0<=rh<=100 or rain<0:
   raise ValueError("Dominio RH o lluvia horario inválido")
  groups[(r["localidad"],time.date())].append((time,rh,rain))
 output=[]
 for (place,day),xs in sorted(groups.items()):
  xs.sort(key=lambda x:x[0])
  # Exactly one record for each hour in a civil day; DST locations can be 23/25:
  # the user must supply timezone-adjusted data consistently; this implementation
  # rejects partial/ambiguous days instead of inventing missing hours.
  if len(xs)!=24 or len({x[0].hour for x in xs})!=24:
   raise ValueError("Datos horarios incompletos o repetidos "+str((place,day)))
  wet=[x[1]>=threshold for x in xs];runs=0;longest=0
  for item in wet:runs=runs+1 if item else 0;longest=max(longest,runs)
  output.append({"localidad":place,"fecha":day.isoformat(),
    "horas_hr_elevada":sum(wet),"umbral_rh_pct":threshold,
    "mayor_bloque_continuo_horas_hr_elevada":longest,
    "horas_con_lluvia":sum(x[2]>0 for x in xs),
    "lluvia_total_mm":round(sum(x[2] for x in xs),3),
    "horas_humedad_foliar":None,"prediccion_enfermedad":None,
    "interpretacion":"Horas con RH alta, NO horas de hoja mojada ni infecciones."})
 return output
def run():
 parser=argparse.ArgumentParser()
 parser.add_argument("--csv",type=Path,required=True)
 parser.add_argument("--umbral-rh",type=float,default=90.)
 parser.add_argument("--salida",type=Path,required=True)
 opt=parser.parse_args()
 with opt.csv.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
 res=analyze(rows,opt.umbral_rh)
 opt.salida.parent.mkdir(parents=True,exist_ok=True)
 opt.salida.write_text(json.dumps({"metodo":"observaciones horarias completas, NO deriva de lluvia mensual",
   "horas_humedad_foliar_validada":False,"predicciones_fitosanitarias":False,
   "datos":res},indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("HORAS_RH_DOCUMENTADAS",len(res),flush=True)
if __name__=="__main__":run()
