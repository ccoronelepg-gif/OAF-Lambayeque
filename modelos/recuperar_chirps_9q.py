#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9Q: recuperación incremental de TODOS los 240 meses CHIRPS v3 restantes.
CHIRPS v3 FINAL USGS global sólo después de comprobar equivalencia 9O.
Conserva SHA-256, fechas y 42 + 81 muestras mensuales. No rellena ausencias.
Permite reanudar sin volver a descargar meses ya verificados y sin perder un lote.
"""
from __future__ import annotations
import argparse,csv,json,os,sys,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import mirror_chirps_9p as mirror
import chirps_homogeneidad_9o as chirps
BASE=ROOT/"datos/recuperacion_9q"
BASE.mkdir(parents=True,exist_ok=True)
MANIFEST=BASE/"fuentes_chirps_9q.json"
SECTORS=BASE/"sectores_mensuales_9q.csv"
WITNESS=BASE/"testigos_mensuales_9q.csv"
YEARS=range(1996,2026)
FULL=tuple(f"{year}-{m:02d}" for year in YEARS for m in range(1,13))
BATCH=24
def doc(path):return json.loads(path.read_text(encoding="utf8"))
def records(path):
 if not path.exists():return []
 with path.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def existing():
 o=doc(chirps.DAYS);p=doc(mirror.META)
 assert o["n_meses_reales"]==108 and p["n_meses_9p_nuevos"]==12
 assert p["mirroring_verificado"] and all(i["producto_equivalente_en_celdas_lambayeque"]
      for i in p["comparaciones_equivalencia"])
 known={x["mes"]:x["sha256"] for x in o["fuentes"]+p["nuevos"]}
 if len(known)!=120:raise ValueError("Duplicación entre fuentes iniciales 9O y 9P")
 return known,o,p
def signature(probes):
 return tuple(float(x) for x in probes[0]["raster_transform"]) if False else None
def read_state():
 if MANIFEST.exists():return doc(MANIFEST)
 return {"fase":"9Q","nuevos":[],"fallidos":[],"sondas":[],"detenido_por_servidor":False,
         "lotes_procesados":0,"regla":"Sin imputación, ni CHIRPS preliminar/v2, ni fusionar fuentes sin cotejo"}
def audit(state,known):
 newer={f["mes"]:f for f in state["nuevos"]}
 if set(newer)&set(known):raise ValueError("9Q colisiona con mes validado 9O/9P")
 rows=records(SECTORS);pts=records(WITNESS)
 if len(rows)!=42*len(newer) or len(pts)!=81*len(newer):
  raise ValueError("Filas 9Q y manifiesto inconsistentes")
 seen=set()
 for row in rows:
  key=(row["mes"],row["sector"])
  if key in seen:raise ValueError("Mes-sector 9Q repetido")
  seen.add(key)
  if row["sha256_tiff"]!=newer[row["mes"]]["sha256"]:raise ValueError("Fila sin SHA")
 for row in pts:
  if row["sha256_tiff"]!=newer[row["mes"]]["sha256"]:raise ValueError("Testigo sin SHA")
 assert len({(r["mes"],r["testigo"]) for r in pts})==len(pts)
 for x in newer.values():
  assert x["url"].startswith(mirror.GLOBAL) and x["crs"]==4326
 assert len(known)+len(newer)<=360
 return len(newer)
def persist(sources,errors,old,geoRows,pointRows,known,probes,stop,lots):
 newer=dict(old);newer.update({s["mes"]:s for s in sources})
 data=sorted(newer.values(),key=lambda x:x["mes"])
 mergedE={i["mes"]:i for i in read_state().get("fallidos",[])}
 for err in errors:mergedE[err["mes"]]=err
 for x in newer:mergedE.pop(x,None)
 meta={"fase":"9Q","periodo":"1996-2025","fuente":"USGS/FEWS CHIRPS v3 FINAL global",
   "fuente_institucional":mirror.GLOBAL,
   "producto_final_no_preliminar":True,"resolucion_grados":.05,
   "n_meses_preexistentes_9o_9p":len(known),
   "n_meses_nuevos_9q":len(newer),
   "n_meses_chirps_verificados":len(known)+len(newer),
   "n_meses_objetivo":360,
   "n_meses_no_comprobados":360-len(known)-len(newer),
   "n_anios_completos_fuente":sum(all(f"{y}-{m:02d}" in (set(newer)|set(known)) for m in range(1,13)) for y in YEARS),
   "todas_las_fechas_1996_2025_verificadas":len(known)+len(newer)==360,
   "nuevos":data,
   "fallidos":sorted(mergedE.values(),key=lambda x:x["mes"]),
   "sondas":probes,
   "pruebas_equivalencia_9p_previamente_aprobadas":True,
   "detenido_por_servidor":stop,"lotes_procesados":lots,
   "archivos_tiff_originales_guardados_en_repo":False,
   "reproducibilidad":"URL y SHA256 de cada TIFF, filas sector y testigo, derivadas sólo de píxeles originales.",
   "observaciones_SENAMHI_independientes_30_anios":0,
   "zonas_climaticas_homogeneas_certificadas":0,
   "pronostico_zonal_validado":False,
   "alertas_fitosanitarias_emitidas":False}
 for path,rows,fieldnames in ((SECTORS,geoRows,chirps.F_SEC),(WITNESS,pointRows,chirps.F_WIT)):
  with path.open("w",encoding="utf8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
   w.writerows(sorted(rows,key=lambda r:(r["mes"],r["sector" if path==SECTORS else "testigo"])))
 MANIFEST.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 audit(meta,known)
 print("9Q progreso CHIRPS:",meta["n_meses_chirps_verificados"],"/360;",
       "errores:",len(meta["fallidos"]),"lote:",lots,flush=True)
 return meta

def run(batch=BATCH,workers=4,max_months=240):
 known,old,prior=existing()
 state=read_state()
 audit(state,known) if MANIFEST.exists() else None
 previous={x["mes"]:x for x in state["nuevos"]}
 unobserved=[m for m in FULL if m not in previous and m not in known]
 if not unobserved:
  return persist([],[],previous,records(SECTORS),records(WITNESS),
                 known,state.get("sondas",[]),False,state["lotes_procesados"])
 probes=state.get("sondas",[])
 # Este ensayo USA DOS CONTROLES de la fuente global, cotejados de nuevo vs archivos 9O.
 # Si el servidor falla, detener sin borrar lo confirmado previamente.
 if not probes or not all(p.get("producto_equivalente_en_celdas_lambayeque") for p in probes):
  original={(r["mes"],r["sector"]):r for r in chirps.read_csv(chirps.SERIES)}
  stations={(r["mes"],r["testigo"]):r for r in chirps.read_csv(chirps.WITNESS)}
  sources={p["mes"]:p for p in old["fuentes"]}
  try:
   probes=[];sign=None
   for m in mirror.PROBES:
    x,sg=mirror.compare(m,original,stations,sources)
    if sign is not None and any(abs(a-b)>1e-6 for a,b in zip(sign,sg)):
     raise ValueError("Transform de fuente oficial difiere entre sondas")
    sign=sg;probes.append(x)
  except (HTTPError,URLError,TimeoutError,OSError,ValueError) as e:
   return persist([], [{"mes":"sonda","url":mirror.GLOBAL,
     "error":f"{type(e).__name__}: {e}"[:400]}],previous,records(SECTORS),
     records(WITNESS),known,probes,True,state["lotes_procesados"])
 # Al reanudar con controles archivados, el transform 9P original ha sido
 # comprobado contra las mismas dos fechas y queda registrado en el manifiesto.
 # El TIFF global deriva su transform con tolerancia 1e-6 durante cada lectura.
 sign=tuple(float(v) for v in prior["nuevos"][0]["transform"])
 geom,wit=chirps.inputs()
 sectors=records(SECTORS);testigos=records(WITNESS)
 errors=[];saved=[];stopped=False
 requested=unobserved[:max_months]
 # Evitar más de 4 descargas en paralelo; no forzar un servidor que devuelve 403.
 for i in range(0,len(requested),batch):
  months=requested[i:i+batch]
  def fetch_one(month):
   try:
    return month,mirror.one_month(month,sign,geom,wit),None
   except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
    return month,None,{"mes":month,"url":mirror.urlof(month),
                        "error":f"{type(exc).__name__}: {exc}"[:360]}
  with ThreadPoolExecutor(max_workers=workers) as pool:
   results=list(pool.map(fetch_one,months))
  for month,content,error in results:
   if error is not None:
    errors.append(error)
    if "HTTPError: HTTP Error 403" in error["error"] or "HTTPError: HTTP Error 429" in error["error"]:
     stopped=True
    continue
   meta,srows,wrows=content
   if month in known or month in previous:
    raise ValueError("No se permite sobrescribir un mes ya certificado")
   previous[month]=meta;saved.append(meta);sectors.extend(srows);testigos.extend(wrows)
  state=persist(saved,errors,read_state()["nuevos"] and
          {s["mes"]:s for s in read_state()["nuevos"]} or {},
          sectors,testigos,known,probes,stopped,state["lotes_procesados"]+1)
  # Si el servidor expresa bloqueo, conservar lo conseguido sin insistir.
  if stopped:break
  # Confirmar en cada lote que repositorio sigue siendo durable; el workflow
  # puede confirmar y subir esta carpeta por tanda.
  if os.environ.get("GITHUB_ACTIONS")=="true":
   os.system("git add datos/recuperacion_9q/ && git diff --cached --quiet || (git commit -m 'data(9Q): lote mensual CHIRPS v3 con SHA256' && git push origin HEAD:main)")
  if i+batch<len(requested):time.sleep(1)
 return state

def check():
 known,_,_=existing()
 return audit(read_state(),known)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--check",action="store_true")
 p.add_argument("--batch",type=int,default=24)
 p.add_argument("--workers",type=int,default=4)
 p.add_argument("--max-months",type=int,default=240)
 a=p.parse_args()
 if not (1<=a.batch<=36 and 1<=a.workers<=5 and 0<=a.max_months<=240):
  raise SystemExit("Parámetros fuera de límite")
 if a.check:print("9Q auditoría:",check(),"nuevos")
 else:run(batch=a.batch,workers=a.workers,max_months=a.max_months)
