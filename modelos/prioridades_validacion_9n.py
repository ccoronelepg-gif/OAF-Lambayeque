#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9N: priorización de validación CLIMÁTICA posterior al cierre DEM.
Esta tabla NO es comprobación de homogeneidad; únicamente prioriza campo y clima.
Usa metadatos originales 8P, 9I y DEM 9N, nunca imputación de lluvia o temperatura.
"""
import argparse,csv,json,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"datos/cobertura_multitesela_9n"
PREV=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
CLIMATE=ROOT/"datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv"
PAIRS=ROOT/"datos/clima_contiguo_8p/pares_similares_exploratorios_8p.csv"
STATIONS=ROOT/"datos/validacion_estaciones_9i/diagnostico_multianual_9i.json"
ROW=PATH/"evaluacion_42_sectores_9n.json"
OUTPUT=PATH/"prioridades_validacion_climatica_9n.json"
def j(p):return json.loads(p.read_text("utf8"))
def csvrows(p):
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def generate():
 dem=j(ROW);byid={r["id_sector"]:r for r in dem}
 sectors=j(PREV)["features"];climate=csvrows(CLIMATE);pairs=csvrows(PAIRS)
 stations=j(STATIONS);known={s["id"]:s for s in climate}
 if len(sectors)!=42 or len(dem)!=42 or len(climate)!=81 or stations["meses_estacion_unicos_emparejados"]!=213:
  raise ValueError("Fuentes originales no tienen la cobertura esperada")
 if stations["cobertura_1996_2025_de_estaciones"]:
  raise ValueError("9I no debe convertirse en validación instrumental 30 años")
 distinct=[r for r in pairs if r["centros_de_ambos_modelos_diferentes"]=="true"]
 same_floor=[r for r in distinct if known[r["nodo_a"]]["estrato_fisico_preliminar"]==
             known[r["nodo_b"]]["estrato_fisico_preliminar"]]
 allrows=[]
 for f in sectors:
  p=f["properties"];sid=p["id_sector"];r=byid[sid]
  reasons=[]
  if r["cobertura"]!="completa":reasons.append("dem_incompleto")
  if r["piso_nominal"]=="cota_negativa_revisar":reasons.append("elevacion_dem_negativa_revisar")
  if r["compatible_270m_30"] is not None and r["compatible_270m_30"]<.35:
   reasons.append("piso_del_nodo_no_representa_el_relieve_raster")
  if r["diferencia_abs_30_270_vs_450"] is not None and r["diferencia_abs_30_270_vs_450"]>.08:
   reasons.append("pendiente_sensible_a_resolucion")
  if p["n_testigos_perfil_30anios"]==0:
   reasons.append("sin_testigo_climatico_con_perfil_30anios")
  if p["familia_similitud"] and p["familia_similitud"] not in ("C01","C02","C03"):
   raise ValueError("Familia nueva sin verificación 8P")
  grade=("alta" if len(reasons)>=2 else "media" if len(reasons)==1 else
         "basica_pendiente_de_validacion")
  allrows.append({"sector":sid,"piso":p["estrato"],"familia":p["familia_similitud"],
      "prioridad_verificacion":grade,"motivos":reasons,
      "n_testigos_reanalisis_proximos":p["n_testigos_perfil_30anios"],
      "cobertura_dem":r["cobertura"],
      "fraccion_piso_pendiente":r["compatible_270m_30"],
      "diferencia_resoluciones":r["diferencia_abs_30_270_vs_450"],
      "n_estaciones_instrumentales_vinculadas_y_verificadas":0,
      "homogeneidad_climatica_demostrada":False,
      "pronostico_anticipatorio_validado":False})
 counts=Counter(row["prioridad_verificacion"] for row in allrows)
 summary={"fase":"9N","fecha_corte":"2026-10-17",
    "tipo":"priorizacion_para_observaciones_independientes_no_verificacion_de_homogeneidad",
    "n_sectores":len(allrows),"n_testigos_perfil_reanalisis_1996_2025":len(climate),
    "n_pares_vecindad_exploratoria_8p":len(pairs),
    "n_pares_distintos_ambos_reanalisis":len(distinct),
    "n_pares_distintos_dentro_mismo_piso":len(same_floor),
    "n_familias_exploratorias_8p":3,
    "verificacion_instrumental_9i":{"estaciones_n":stations["estaciones_n"],
       "meses_estacion_unicos":stations["meses_estacion_unicos_emparejados"],
       "anios":stations["anios_prespecificados"],
       "normales_instrumentales_1996_2025_cubiertas":False,
       "independencia_CHIRPS_de_pluviometros_comprobada":False,
       "coordenadas_historicas_confirmadas":False},
    "conteos_prioridad":dict(sorted(counts.items())),
    "observaciones_instrumentales_que_certifican_los_42_sectores":0,
    "zonas_climaticamente_homogeneas_certificadas":0,
    "limites":[
       "81 puntos con 1996-2025 son perfiles de ERA5 y ERA5-Land, no 81 estaciones meteorológicas independientes.",
       "Los parecidos de píxeles compartidos no constituyen confirmación espacial independiente.",
       "Los tres pluviómetros 9I solo aportan meses históricos 1996, 1998, 2002, 2007, 2011 y 2013, con ubicaciones documentales alternativas.",
       "CHIRPS v3 incorpora pluviómetros; su contraste con estaciones puede tener dependencia de insumos.",
       "Ninguna prioridad es predicción de plaga, evidencia de aptitud para arándano/vid ni pronóstico por polígono."],
    "sectores":allrows}
 return summary
def run(check=False):
 state=generate()
 if check:
  if j(OUTPUT)!=state:raise ValueError("Prioridades científicas 9N no reproducibles")
 else:
  OUTPUT.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n","utf8")
 print("9N priorización:",state["conteos_prioridad"],"sectores; estaciones zonales certificadas: 0")
 return state
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 run(p.parse_args().check)
