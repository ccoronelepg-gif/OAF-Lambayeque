#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF fase 9P: contraste temporal por años CHIRPS y décadas, sin extrapolar lagunas.
No sustituye validación independiente SENAMHI ni verifica pronósticos.
Un mes ausente se conserva ausente. Años definidos con 12 meses reales para ambos sectores.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/continuidad_9p"
FROM=ROOT/"datos/homogeneidad_9o"
SOURCE9O=FROM/"fuentes_chirps_9o.json"
SECTOR9O=FROM/"serie_sectores_chirps_9o.csv"
DIAG9O=FROM/"diagnostico_homogeneidad_9o.json"
SOURCE9P=BASE/"fuentes_adicionales_chirps_9p.json"
SECTOR9P=BASE/"meses_adicionales_sectores_9p.csv"
DIAG=BASE/"estado_estabilidad_9p.json"
PAIRS=BASE/"pares_estabilidad_temporal_9p.csv"
ANNUAL=BASE/"precipitacion_anual_9p.csv"
YEARS=tuple(range(1996,2026))
MONTHS={f"{y}-{m:02d}" for y in YEARS for m in range(1,13)}
PERIODS={"1996-2005":tuple(range(1996,2006)),
         "2006-2015":tuple(range(2006,2016)),
         "2016-2025":tuple(range(2016,2026))}
FIELDS=("par","sector_a","sector_b","codigo_hidrografico","n_anios_comunes",
        "anios_evaluados","r_todos_meses","r_sin_1996_2000",
        "r_sin_2016_2025","r_loyo_min","r_loyo_mediana","r_loyo_max",
        "variacion_r_loyo_max_min","diferencia_lluvia_anual_pct",
        "periodo_1996_2005_n_anios","periodo_2006_2015_n_anios",
        "periodo_2016_2025_n_anios","estabilidad_climatica_certificada")
YEARFIELDS=("sector","anio","precipitacion_anual_chirps_mm","n_meses_reales",
            "tiene_pixel_valido","normal_30_anios_valida")

def read(path):
 return json.loads(path.read_text(encoding="utf8"))
def rows(path):
 if not path.exists():return []
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def sources_and_series():
 old=read(SOURCE9O)
 if old["fase"]!="9O" or old["n_meses_reales"]<108:raise ValueError("Archivo 9O incompleto")
 unique={f["mes"]:(f["sha256"],"9O",f["url"]) for f in old["fuentes"]}
 if len(unique)!=old["n_meses_reales"]:raise ValueError("Mes 9O repetido")
 original=rows(SECTOR9O)
 if len(original)!=42*old["n_meses_reales"]:raise ValueError("Filas CHIRPS 9O incorrectas")
 source9p=read(SOURCE9P) if SOURCE9P.exists() else {"fase":"9P","nuevos":[],
     "errores":[],"mirroring_verificado":False}
 if source9p["fase"]!="9P":raise ValueError("Manifiesto alterno sin procedencia")
 for item in source9p.get("nuevos",[]):
  month=item["mes"]
  if month in unique:raise ValueError("Mes 9P duplicó fuente 9O "+month)
  unique[month]=(item["sha256"],"9P",item["url"])
 full=original+rows(SECTOR9P)
 observed=defaultdict(dict)
 seen=set()
 for row in full:
  month=row["mes"];sid=row["sector"]
  if month not in unique or month not in MONTHS:
   raise ValueError("Mes CHIRPS ajeno a fuente confirmada "+month)
  if row["sha256_tiff"]!=unique[month][0]:
   raise ValueError("SHA de valor mensual no corresponde a fuente "+month)
  key=(month,sid)
  if key in seen:raise ValueError("Duplicado sector-mes "+str(key))
  seen.add(key)
  if row["precipitacion_promedio_pixel_mm"]!="":
   v=float(row["precipitacion_promedio_pixel_mm"])
   if not (math.isfinite(v) and 0<=v<10000):
    raise ValueError("Precipitación fuera de rango")
   observed[sid][month]=v
 if len(seen)!=42*len(unique):
  raise ValueError("Faltan filas explícitas sector-mes para fuente archivada")
 return unique,observed,source9p

def precip_anomalies(d1,d2,keys):
 # Años completos para cada pareja, sin calendario seleccionado por skill.
 m1={m:v for m,v in d1.items() if m in keys}
 m2={m:v for m,v in d2.items() if m in keys}
 series1=[];series2=[]
 for mo in range(1,13):
  subset=[m for m in sorted(keys) if int(m[-2:])==mo]
  x=[math.log1p(m1[m]) for m in subset]
  y=[math.log1p(m2[m]) for m in subset]
  a=statistics.mean(x);b=statistics.mean(y)
  series1.extend(v-a for v in x)
  series2.extend(v-b for v in y)
 if len(series1)<24 or len(series2)<24:return None
 mx,my=statistics.mean(series1),statistics.mean(series2)
 dx=[v-mx for v in series1];dy=[v-my for v in series2]
 dot=sum(a*b for a,b in zip(dx,dy))
 denom=math.sqrt(sum(a*a for a in dx)*sum(b*b for b in dy))
 return round(dot/denom,5) if denom>1e-10 else None

def get():
 unique,obs,src=sources_and_series()
 previous=read(DIAG9O)
 if previous["zonas_climaticas_homogeneas_certificadas"]!=0:
  raise ValueError("9O cambió certificación climática")
 expected=previous["candidatos_hidro_climaticos"]
 if len(expected)!=2:raise ValueError("Candidatos hidrográficos 9O cambiaron")
 out=[];yearsrows=[]
 for sid in [f"S{i:03d}" for i in range(1,43)]:
  d=obs.get(sid,{})
  for year in YEARS:
   keys=[f"{year}-{mo:02d}" for mo in range(1,13)]
   avail=[m for m in keys if m in d]
   value=round(sum(d[m] for m in keys),3) if len(avail)==12 else ""
   yearsrows.append({"sector":sid,"anio":year,"precipitacion_anual_chirps_mm":value,
    "n_meses_reales":len(avail),"tiene_pixel_valido":"true" if avail else "false",
    "normal_30_anios_valida":"false"})
 for p in expected:
  a,b=p["sectores"]
  common=sorted(y for y in YEARS if all(
   f"{y}-{mo:02d}" in obs[a] and f"{y}-{mo:02d}" in obs[b]
   for mo in range(1,13)))
  def r(years):
   keys={f"{y}-{mo:02d}" for y in years for mo in range(1,13)}
   return precip_anomalies(obs[a],obs[b],keys) if len(years)>=2 else None
  allr=r(common)
  lo=[r([v for v in common if v!=leave]) for leave in common] if len(common)>=4 else []
  valid=[v for v in lo if v is not None]
  ra=sum(obs[a][f"{y}-{mo:02d}"] for y in common for mo in range(1,13))
  rb=sum(obs[b][f"{y}-{mo:02d}"] for y in common for mo in range(1,13))
  gap=round(200*abs(ra-rb)/(ra+rb),3) if ra+rb>0 else None
  row={"par":a+"_"+b,"sector_a":a,"sector_b":b,
   "codigo_hidrografico":",".join(p["unidades_hidrograficas"]),
   "n_anios_comunes":len(common),"anios_evaluados":";".join(str(y) for y in common),
   "r_todos_meses":allr,
   "r_sin_1996_2000":r([y for y in common if y not in range(1996,2001)]),
   "r_sin_2016_2025":r([y for y in common if y not in range(2016,2026)]),
   "r_loyo_min":min(valid) if valid else None,
   "r_loyo_mediana":round(statistics.median(valid),5) if valid else None,
   "r_loyo_max":max(valid) if valid else None,
   "variacion_r_loyo_max_min":round(max(valid)-min(valid),5) if valid else None,
   "diferencia_lluvia_anual_pct":gap,
   **{"periodo_"+per.replace("-","_")+"_n_anios":sum(y in yr for y in common)
      for per,yr in PERIODS.items()},
   "estabilidad_climatica_certificada":"false"}
  out.append(row)
 missing=sorted(MONTHS-set(unique))
 complete=[y for y in YEARS if all(f"{y}-{m:02d}" in unique for m in range(1,13))]
 summary={"fase":"9P","corte":"2026-10-17",
   "n_meses_chirps_existentes_9o":previous["meses_fuente_chirps"],
   "n_meses_chirps_agregados_9p":len(src.get("nuevos",[])),
   "n_meses_chirps_comprobados_total":len(unique),
   "n_meses_historicos_objetivo":360,"n_meses_no_comprobados":len(missing),
   "anios_fuente_completos":complete,
   "n_anios_fuente_completos":len(complete),
   "anios_por_decada_fuentes":{
     name:sum(y in values for y in complete) for name,values in PERIODS.items()},
   "periodo_chirps_30_anios_completo":len(unique)==360,
   "testigos_reanalisis_1996_2025_completos":81,
   "meses_reanalisis_por_testigo":360,
   "sectores_9k_totales":42,
   "sectores_sin_centro_pixel_chirps_9o":previous["sectores_sin_pixel_chirps_valido"],
   "pares_hidro_altitudinales_analizados":len(out),
   "verificacion_temporal":"Leave-one-year-out de correlaciones de anomalías CHIRPS log1p y exclusión de subperiodos: descriptivo, sin skill predictivo",
   "contribucion_CHIRPS_estaciones_no_independencia":True,
   "puntos_chirps_no_son_pluviometros":True,
   "n_estaciones_independientes_1996_2025_por_sector":0,
   "n_zonas_climaticamente_homogeneas_certificadas":0,
   "n_cuencas_con_vigencia_ANA_ratificada":0,
   "precision_predictiva_de_alertas_validada":False,
   "alertas_fitosanitarias_emitidas":False,
   "meses_ausentes":missing,
   "resumen_pares":out,
   "fuente_alternativa_9p":{
      "probada":src.get("sonda_repositorio",False),
      "misma_grilla_y_valores_replicados":src.get("mirroring_verificado",False),
      "cambios_permitidos_sin_prueba_equivalencia":False},
   "limitaciones":[
    "La correlación leave-one-year-out no es verificación predictiva ex-ante y puede aumentar debido a procesos regionales comunes.",
    "Los 3 periodos decenales cuentan con cantidades históricas diferentes; 1 o 2 años no permiten certificar estabilidad de una década.",
    "Una misma celda CHIRPS puede alimentar varios sectores y puntos testigo; no son sensores independientes.",
    "La lluvia CHIRPS combina datos de pluviómetros, por lo que el contraste directo puede compartir fuentes.",
    "Un centro de píxel CHIRPS fuera de un polígono no significa lluvia cero en la finca.",
    "El contraste de ERA5/ERA5-Land cubre 30 años, pero no sustituye verificación local instrumental.",
    "Los segmentos hidrofísicos 9M no son superficies de producción reconocidas ni cuencas vigentes certificadas."
   ]}
 return summary,out,yearsrows

def save(check=False):
 summary,comparison,annual=get()
 if check:
  if read(DIAG)!=summary:raise ValueError("9P no reproduce diagnóstico")
  if len(rows(PAIRS))!=len(comparison) or len(rows(ANNUAL))!=len(annual):
   raise ValueError("Tablas 9P incompletas")
 else:
  BASE.mkdir(parents=True,exist_ok=True)
  DIAG.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  for path,data,fields in ((PAIRS,comparison,FIELDS),(ANNUAL,annual,YEARFIELDS)):
   with path.open("w",encoding="utf8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
 print("9P: CHIRPS",summary["n_meses_chirps_comprobados_total"],
       "/360; años completos:",summary["n_anios_fuente_completos"],
       "; pares:",summary["pares_hidro_altitudinales_analizados"])
 return summary

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true")
 save(check=ap.parse_args().check)
