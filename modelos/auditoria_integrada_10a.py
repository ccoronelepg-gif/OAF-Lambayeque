#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10A: reproducir QA y métricas retrospectivas 9X, sin alertas ni 'as issued' ficticios."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from collections import defaultdict
MODELS={"climatologia_global","climatologia_piso","persistencia_anual","random_forest","gcn"}
MONTHS={f"{y}-{m:02d}" for y in range(2021,2026) for m in range(1,13)}
COLS={"mes","anio","sector","piso","bloque","modelo","observado_CHIRPS_mm","predicho_mm"}
def load(path):return json.loads(Path(path).read_text(encoding="utf8"))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def metric(rows):
 e=[r["p"]-r["y"] for r in rows]; n=len(e)
 return {"n":n,"mae_mm":round(sum(abs(x) for x in e)/n,4),
         "rmse_mm":round(math.sqrt(sum(x*x for x in e)/n),4),
         "sesgo_mm":round(sum(e)/n,4)}
def groups(rows,keys):
 by=defaultdict(list)
 for r in rows:by[tuple(r[k] for k in keys)].append(r)
 return [{**dict(zip(keys,k)),**metric(v)} for k,v in sorted(by.items())]
def read(path):
 with open(path,newline="",encoding="utf-8-sig") as f:
  rd=csv.DictReader(f)
  if set(rd.fieldnames or [])!=COLS:raise ValueError("Columnas 9X incompatibles")
  out=[]
  for n,r in enumerate(rd,2):
   if r["mes"] not in MONTHS or r["anio"]!=r["mes"][:4] or r["modelo"] not in MODELS:
    raise ValueError(f"Fila {n}: fecha o modelo incompatible")
   y,p=float(r["observado_CHIRPS_mm"]),float(r["predicho_mm"])
   if not all(math.isfinite(v) and v>=0 for v in (y,p)):raise ValueError(f"Fila {n}: lluvia inválida")
   out.append({"mes":r["mes"],"anio":r["anio"],"sector":r["sector"],"piso":r["piso"],
               "bloque":r["bloque"],"modelo":r["modelo"],"y":y,"p":p})
 return out
def evaluate(rows,original,folds):
 keys=set(); targets={}; pair=defaultdict(set)
 sectors={r["sector"] for r in rows}; months={r["mes"] for r in rows}
 for r in rows:
  k=(r["sector"],r["mes"]); allk=(*k,r["modelo"])
  if allk in keys:raise ValueError("Predicción sector-mes-modelo repetida")
  keys.add(allk); pair[k].add(r["modelo"])
  sig=(r["y"],r["piso"],r["bloque"])
  if k in targets and targets[k]!=sig:raise ValueError("Observaciones objetivo no pareadas")
  targets[k]=sig
 if len(rows)!=11700 or len(sectors)!=39 or months!=MONTHS or len(pair)!=2340 or any(v!=MODELS for v in pair.values()):
  raise ValueError("Matriz 9X incompleta: NO inventar meses")
 assigned={s:str(f["id"]) for f in folds["folds"] for s in f["sectores_holdout"]}
 if set(assigned)!=sectors or any(r["bloque"]!=assigned[r["sector"]] for r in rows):
  raise ValueError("Bloque/sector no coincide con archivo original")
 overall=groups(rows,("modelo",))
 for r in overall:
  ref=original["metricas_globales"][r["modelo"]]
  if any(abs(r[x]-ref[x])>.00011 for x in ("mae_mm","rmse_mm","sesgo_mm")) or r["n"]!=ref["n"]:
   raise ValueError("Métricas no coinciden con resultados 9X")
 sector=groups(rows,("sector","piso","bloque","modelo"))
 ss=defaultdict(dict)
 for r in sector:ss[r["sector"]][r["modelo"]]=r["mae_mm"]
 return {"fase":"10A","estado":"HABILIDAD_RETROSPECTIVA_EXPERIMENTAL","fuente_tipo":"CHIRPS_v3_FINAL_retroactivo",
 "periodo_prueba":"2021-01/2025-12","datos_as_issued":False,"fecha_emision_original_conservada":False,
 "matriz_calibracion_fuera_de_muestra_2016_2020":False,"calibracion_conformal_9y_ejecutable":False,
 "modelo_operativo_ganador":None,"alertas_habilitadas":False,
 "integridad":{"filas":len(rows),"sectores":len(sectors),"meses":len(months),"pares":len(pair),
 "duplicados":0,"objetivos_divergentes":0},
 "metricas_globales":overall,"por_anio":groups(rows,("anio","modelo")),
 "por_piso":groups(rows,("piso","modelo")),"por_bloque":groups(rows,("bloque","modelo")),
 "por_sector":sector,"por_piso_2023":[r for r in groups(rows,("anio","piso","modelo")) if r["anio"]=="2023"],
 "resumen_sectores":{"rf_menor_mae_que_gcn":sum(x["random_forest"]<x["gcn"] for x in ss.values()),
 "rf_menor_mae_que_climatologia_piso":sum(x["random_forest"]<x["climatologia_piso"] for x in ss.values()),
 "rf_menor_mae_de_tres":sum(x["random_forest"]==min(x[m] for m in ("random_forest","gcn","climatologia_piso")) for x in ss.values())},
 "advertencia":"Solo CHIRPS v3 final retrospectivo. Fechas de emisión no archivadas. Validación 2016-2020 utilizada para tuning; no usar para intervalos conformales sin nueva partición."}
def main():
 p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument("--salida",type=Path)
 a=p.parse_args();d=a.repo/"datos/generalizacion_9x"
 pred=d/"predicciones_sector_bloque_9x.csv"; original=load(d/"evaluacion_bloques_espaciales_9x.json")
 if sha(pred)!=original.get("sha256_predicciones_9x"):raise ValueError("SHA256 de predicciones 9X no coincide")
 result=evaluate(read(pred),original,load(d/"bloques_geograficos_9x.json"))
 result["sha256_fuente"]=sha(pred)
 output=a.salida or a.repo/"datos/integracion_10a/auditoria_regenerada_10a.json"
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps({"estado":result["estado"],"integridad":result["integridad"],"alertas":False},ensure_ascii=False))
if __name__=="__main__":main()
