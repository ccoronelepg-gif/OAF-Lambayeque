#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10J paired uncertainty audit reading REAL full (>1MB) CSV in CI."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/rf_robusto_10j"
PRED=BASE/"predicciones_rf_tres_objetivos_10j.csv"
SUMMARY=BASE/"auditoria_y_seleccion_10j.json"
OUT=BASE/"comparacion_pareada_incertidumbre_10j.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(values):
 n=len(values)
 if n!=5:raise ValueError("Exactly 5 temporal/spatial blocks expected")
 stats=sorted(statistics.mean(values[k] for k in draw) for draw in itertools.product(range(n),repeat=n))
 def q(x):
  i=x*(len(stats)-1);lo=int(i);hi=min(len(stats)-1,lo+1)
  return round(stats[lo]+(stats[hi]-stats[lo])*(i-lo),7)
 return [q(.025),q(.975)]
def main():
 summary=json.loads(SUMMARY.read_text("utf8"))
 if summary["fase"]!="10J" or sha(PRED)!=summary["sha256_predicciones"]:
  raise ValueError("CSV large original changed SHA")
 with PRED.open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
 if len(rows)!=9360:raise ValueError("Missing candidate arms")
 selected=summary["seleccion_por_bloque"]
 targets={
 "mm":lambda r:abs(float(r["lluvia_predicha_rf_mm"])-float(r["lluvia_observada_mm"]))-
               abs(float(r["lluvia_climatologia_mm"])-float(r["lluvia_observada_mm"])),
 "p90":lambda r:(float(r["probabilidad_rf_p90"])-float(r["evento_p90_observado"]))**2-
                 (float(r["probabilidad_base_p90"])-float(r["evento_p90_observado"]))**2,
 "p95":lambda r:(float(r["probabilidad_rf_p95"])-float(r["evento_p95_observado"]))**2-
                 (float(r["probabilidad_base_p95"])-float(r["evento_p95_observado"]))**2}
 result={}
 for name,fn in targets.items():
  chosen={k:str(v) for k,v in selected[name]["familia_por_bloque"].items()}
  subset=[r for r in rows if r["familia_rf"]==chosen[r["bloque"]]]
  if len(subset)!=2340 or len({(r["sector"],r["mes"]) for r in subset})!=2340:
   raise ValueError("Sample not paired 39x60")
  dif=[fn(r) for r in subset]
  if not all(math.isfinite(z) for z in dif):raise ValueError("Nonfinite paired delta")
  yr={str(year):round(statistics.mean(fn(r) for r in subset if r["mes"].startswith(str(year))),7) for year in range(2021,2026)}
  block={str(b):round(statistics.mean(fn(r) for r in subset if r["bloque"]==str(b)),7) for b in range(5)}
  result[name]={"diferencia_global_RF_menos_climatologia":round(statistics.mean(dif),7),
    "por_anio":yr,"por_bloque":block,
    "intervalo_exploratorio_anual_95":bounds(list(yr.values())),
    "intervalo_exploratorio_bloques_95":bounds(list(block.values())),
    "tamanio_muestra":len(subset),
    "interpretacion":"Negativo favorece RF; 5 años/bloques dependientes, NO intervalos confirmatorios"}
 out={"fase":"10J","estado":"AUDITORIA_RECALCULADA_DESDE_CSV_COMPLETO",
  "comparacion":"Se eligen familias por validación 2016-2018; comparación por pares en 2021-2025",
  "fuente":str(PRED.relative_to(ROOT)),"sha256_fuente":sha(PRED),
  "comparaciones":result,
  "clase_de_intervalos":"Remuestreo exhaustivo de 5 años/bloques. Pocos conglomerados, dependencia entre observaciones. Exploratorios, NO garantía de p-valor.",
  "habilidad_operativa_certificada":False,"alertas_activadas":False}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10J_AUDITORIA_PAREADA",json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
