#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 10G: rate-aware one-segment retrieval and strict 24-part assembly.

Each invocation retrieves exactly ONE historical chunk of <=5 ERA5 point
locations across 10 years. Saves the completed data and HTTP provenance
before any further API request, avoiding loss if the provider rate-limits.
Do not run bulk/concurrent free API requests. No fake, imputed or partial
history is ever published as the complete 39-sector matrix.
"""
from __future__ import annotations
import argparse,csv,json,hashlib
from pathlib import Path
import ingesta_era5_39_sectores_10g as m
SEG=m.OUT/"fragmentos"
YEARS=m.YEAR_CHUNKS
def csv_write(path,rows):
 with path.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=m.MONTH_COLS);w.writeheader();w.writerows(rows)
def csv_read(path):
 with path.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def files(pi,bi):
 name=f"era5_{YEARS[pi][0]}_{YEARS[pi][1]}_grupo{bi:02d}"
 return SEG/(name+".csv"), SEG/(name+".json")
def select(points,pi,bi):
 if not 0<=pi<3 or not 0<=bi<8:raise ValueError("Periodo 0..2 y grupo 0..7")
 batches=list(m.chunks(points,5))
 return YEARS[pi],batches[bi]
def download(pi,bi):
 data=m.manifest()
 years,subset=select(data["puntos"],pi,bi)
 SEG.mkdir(parents=True,exist_ok=True)
 csv_path,meta_path=files(pi,bi)
 if csv_path.exists() or meta_path.exists():
  if csv_path.exists() and meta_path.exists():
   meta=m.read(meta_path)
   if meta.get("sha256_fragmento")==m.sha(csv_path) and meta.get("n_registros")==len(subset)*120:
    print("10G_SEGMENTO_YA_VERIFICADO",pi,bi,meta["n_registros"]);return
  raise ValueError("Fragmento existente inconsistente; detener sin sobrescribir")
 start=f"{years[0]}-01-01";end=f"{years[1]}-12-31"
 response,ledger=m.request(m.build_params(subset,start,end))
 if isinstance(response,dict):response=[response]
 if len(response)!=len(subset):raise ValueError("Proveedor omitió ubicaciones")
 rows=[]
 for node,blob in zip(subset,response):
  rows.extend(m.convert(node,blob,ledger,start,end))
 if len(rows)!=len(subset)*120:raise ValueError("No se recibieron 120 meses completos por sector")
 rows.sort(key=lambda r:(r["sector"],r["mes"]))
 csv_write(csv_path,rows)
 metadata={"fase":"10G","tipo":"FRAGMENTO_RETROSPECTIVO_SIN_VALIDACION_OPERATIVA",
   "periodo":list(years),"grupo":bi,"n_sectores":len(subset),
   "sectores":[p["sector"] for p in subset],"n_registros":len(rows),
   "fuente_geo_sha256":m.sha(m.GEO),
   "request":ledger,"sha256_fragmento":m.sha(csv_path),
   "no_es_historia_completa":True,"alertas_activadas":False}
 meta_path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10G_SEGMENTO_COMPLETO",pi,bi,len(rows),m.sha(csv_path),flush=True)
def assemble():
 inv=m.manifest()
 allrows=[];ledger=[]
 for pi in range(3):
  for bi in range(8):
   years,subset=select(inv["puntos"],pi,bi)
   path,meta_path=files(pi,bi)
   if not path.exists() or not meta_path.exists():
    raise ValueError(f"Falta el fragmento validado periodo={pi}, grupo={bi}. No completar datos por interpolación.")
   meta=m.read(meta_path);rows=csv_read(path)
   if (meta.get("sha256_fragmento")!=m.sha(path) or meta.get("n_registros")!=len(rows)
    or len(rows)!=len(subset)*120 or meta.get("sectores")!=[p["sector"] for p in subset]
    or meta.get("periodo")!=list(years) or meta.get("alertas_activadas") is not False
    or meta.get("fuente_geo_sha256")!=m.sha(m.GEO)):
    raise ValueError("Fragmento alterado "+str(path))
   allrows.extend(rows)
   ledger.append({"periodo":list(years),"grupo":bi,**meta["request"],
                  "csv_sha256":m.sha(path),"csv_relpath":str(path.relative_to(m.ROOT))})
 report=m.audit_rows(allrows,inv["puntos"],full=True)
 if report["filas"]!=14040 or len(ledger)!=24:raise ValueError("No hay 39 x 360 meses")
 allrows.sort(key=lambda r:(r["sector"],r["mes"]))
 m.OUT.mkdir(parents=True,exist_ok=True)
 m.MANIFEST.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 m.write_csv(allrows,m.MONTHLY)
 completed={"fase":"10G","modo":"extraccion_1996_2025",
  "periodo":"1996-01/2025-12","metodo_descarga":"24 fragmentos versionados con SHA y uno por llamada",
  "n_variables":7,"fuente_geometria_sha256":m.sha(m.GEO),
  "proveedor":"Open-Meteo Historical ERA5 0.25 grados; 1 punto por sector; nearest; elevation=nan",
  "modelo_proveedor":"era5","cell_selection":"nearest","elevation_param":"nan",
  "campos_requeridos":list(m.VARS),"resumen":report,
  "auditoria_respuestas":ledger,"sha256_matriz":m.sha(m.MONTHLY),
  "sha256_puntos":m.sha(m.MANIFEST),
  "no_usar_como_prediccion_operativa":True,"datos_ex_post_reprocesados":True,
  "verdaderos_promedios_poligonales":False,
  "variables_homologadas_solo_para_puntos_era5":True,
  "modelo_operativo_ganador":None,"alertas_activadas":False,
  "limitaciones":[
   "No son estaciones ni mediciones de parcelas, y no son promedios de cada poligono.",
   "Sectores 9K son experimentales, S001 con cota DEM negativa pendiente.",
   "17 celdas atmosfericas distintas en el piloto 2023; la cantidad completa se audita.",
   "Al menos una celda ERA5 cruza dos pliegues CHIRPS de 10F.",
   "ERA5 es reanalisis retrospectivo, NO versiones as-issued del periodo.",
   "Sin mediciones independientes ni autorizacion de avisos meteorologicos o fitosanitarios."
  ]}
 m.REPORT.write_text(json.dumps(completed,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("10G_ENSAMBLADO",json.dumps({"filas":report["filas"],
   "celdas":report["n_celdas_era5_distintas"],"sha":completed["sha256_matriz"]}),flush=True)
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--mode",choices=("segment","assemble"),required=True)
 parser.add_argument("--period",type=int)
 parser.add_argument("--batch",type=int)
 a=parser.parse_args()
 if a.mode=="segment":
  if a.period is None or a.batch is None:parser.error("segment requiere --period 0..2 y --batch 0..7")
  download(a.period,a.batch)
 else:assemble()
if __name__=="__main__":main()
