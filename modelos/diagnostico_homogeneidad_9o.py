#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9O: homogeneidad exploratoria, CHIRPS 0.05º y ERA5/ERA5-Land 1996-2025.

Reproduce observaciones derivadas de bloques congelados 8O+8P y series CHIRPS
con huellas de fuente. No existe validación instrumental independiente regional.
Ningún índice aquí implica habilidad de predicción por zona.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import perfiles_climaticos_8o as p8o
import clima_vecindades_8p as p8p

BASE=ROOT/"datos/homogeneidad_9o"
SOURCES=BASE/"fuentes_chirps_9o.json"
SERIES=BASE/"serie_sectores_chirps_9o.csv"
WITNESS=BASE/"serie_testigos_chirps_9o.csv"
SUMMARY=BASE/"diagnostico_homogeneidad_9o.json"
MONTHLY=BASE/"normales_sectoriales_chirps_9o.csv"
WITNORMS=BASE/"normales_testigos_multivariable_9o.csv"
LINKS=ROOT/"datos/sensibilidad_9m/grupos_hidrofisicos_9m.geojson"
FAMILIES=ROOT/"datos/sectores_agroclimaticos_9k/estado_sectores_9k.json"
SECTORS=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
DEF_YEARS=tuple(range(1996,2026))
VARS=("temp_c","rain_era5_mm","rh_pct","radiation_mj_m2")
NCOLS=("sector","mes_calendario","precipitacion_chirps_mm","dispersion_espacial_med_mm",
       "n_anios_mes_con_datos","n_celdas_terrestres_en_promedio",
       "periodo_fuente","homogeneidad_validada")
WCOLS=("testigo","estrato","mes_calendario","temp_c","rain_era5_mm","rh_pct",
       "radiation_mj_m2","rain_chirps_pixel_mm","n_meses_fuentes_chirps",
       "n_anios_perfil_era5","metodo")

def read_csv(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def obj(path):return json.loads(path.read_text("utf8"))
def pearson(a,b):
 if len(a)<5:return None
 aa=np.asarray(a,dtype="float64");bb=np.asarray(b,dtype="float64")
 if np.std(aa)<1e-10 or np.std(bb)<1e-10:return None
 return round(float(np.corrcoef(aa,bb)[0,1]),5)

def climate_81():
 """Unir los originales diarios ERA5 (lluvia HR radiación) y ERA5-Land (T)."""
 old=p8o.read_testigos(ROOT)
 newer=p8p.nodes(ROOT)
 if len(old)!=19 or len(newer)!=62:raise ValueError("Censos de reanálisis 8O/8P no completos")
 allsite={p["id"]:p for p in old+newer}
 if len(allsite)!=81:raise ValueError("Testigos 8O y 8P duplicados")
 combined=defaultdict(dict)
 for model in p8o.VARS:
  for start,end in p8o.BLOCKS:
   data=p8o.read_source(ROOT,model,start,end,old)
   if data is None:raise ValueError("Bloque 8O faltante "+str((model,start,end)))
   record,_=data
   combined.update({k:{**combined[k],**v} for k,v in p8o.monthly(record,model,old).items()})
 for idx,part in enumerate(p8p.chunked(newer),1):
  for model in p8o.VARS:
   for start,end in p8o.BLOCKS:
    original=p8p.inspect(ROOT,idx,model,start,end,part)
    if original is None:raise ValueError("Bloque 8P faltante")
    for k,v in p8o.monthly(original,model,part).items():
     combined[k].update(v)
 if len(combined)!=81*360:raise ValueError("Climatología 81 x 360 incompleta")
 for (pid,month),v in combined.items():
  if not all(var in v for var in ("temperature_2m_mean","precipitation_sum",
       "relative_humidity_2m_mean","shortwave_radiation_sum")):
   raise ValueError("Variables multimodelo incompletas")
  if not (0<=v["precipitation_sum"]<100000 and -30<v["temperature_2m_mean"]<60 and
          0<=v["relative_humidity_2m_mean"]<=100 and 0<=v["shortwave_radiation_sum"]<1500):
   raise ValueError("Magnitud reanálisis mensual inválida")
 return allsite,combined

def group_compare(a,b,months,seasonality=True):
 """Comparación de series completas comunes, anomalías sin estacionalidad."""
 common=sorted(m for m in months if m in a and m in b)
 if len(common)<60:return {"n_meses_comunes":len(common),"estado":"insuficiente","corr":None,
                           "diferencia_relativa_precipitacion_media":None}
 xa=np.array([a[m] for m in common],dtype=float);xb=np.array([b[m] for m in common],dtype=float)
 if seasonality:
  for mo in range(1,13):
   mask=np.array([int(m[-2:])==mo for m in common])
   if mask.sum():
    xa[mask]=np.log1p(xa[mask])-np.log1p(xa[mask]).mean()
    xb[mask]=np.log1p(xb[mask])-np.log1p(xb[mask]).mean()
 med=(float(np.mean([a[m] for m in common]))+float(np.mean([b[m] for m in common])))/2
 gap=(abs(float(np.mean([a[m] for m in common]))-float(np.mean([b[m] for m in common])))/med
      if med>0 else None)
 return {"n_meses_comunes":len(common),"estado":"exploratorio_no_validado",
         "corr_anomalia_log_lluvia_estacional":pearson(xa,xb),
         "diferencia_relativa_precipitacion_media":round(gap,5) if gap is not None else None}

def analyse():
 src=obj(SOURCES)
 if src["fase"]!="9O" or src["n_sectores"]!=42 or src["n_testigos_reanalisis"]!=81:
  raise ValueError("Origen CHIRPS no verificado")
 sec=read_csv(SERIES);pix=read_csv(WITNESS)
 # Huellear la fuente a cada serie, no considerar resúmenes sin versión
 index={f["mes"]:f["sha256"] for f in src["fuentes"]}
 if len(index)!=src["n_meses_reales"] or len(sec)!=42*len(index) or len(pix)!=81*len(index):
  raise ValueError("Series no conservan mes, cantidad o SHA")
 climate,era=climate_81()
 series=defaultdict(dict);scatter=defaultdict(dict);cells=defaultdict(dict);pixs=defaultdict(dict)
 unique_cell=defaultdict(set)
 for x in sec:
  month=x["mes"];sid=x["sector"]
  if x["sha256_tiff"]!=index[month]:raise ValueError("Fuente CHIRPS por sector sin correspondencia")
  if x["precipitacion_promedio_pixel_mm"]!="":
   value=float(x["precipitacion_promedio_pixel_mm"])
   if not (0<=value<10000):raise ValueError("Lluvia sector fuera rango")
   series[sid][month]=value
   if x["dispersion_espacial_mm"]!="":scatter[sid][month]=float(x["dispersion_espacial_mm"])
   cells[sid][month]=int(x["n_pixeles_terrestres"])
 for x in pix:
  month=x["mes"];pid=x["testigo"]
  if x["sha256_tiff"]!=index[month]:raise ValueError("Fuente CHIRPS testigo no coincide")
  coord=(x["latitud_celda"],x["longitud_celda"])
  unique_cell[coord].add(pid)
  if x["precipitacion_pixel_mm"]!="":
   pixs[pid][month]=float(x["precipitacion_pixel_mm"])
 if len(series)!=42:raise ValueError("No hay píxeles CHIRPS en alguno de los sectores")
 geo=obj(SECTORS)
 sectorprops={f["properties"]["id_sector"]:f["properties"] for f in geo["features"]}
 if len(sectorprops)!=42:raise ValueError("GeoJSON SIG 9K alterado")
 years_complete=sorted(y for y in DEF_YEARS if
       all(f"{y}-{m:02d}" in index for m in range(1,13)))
 month_csv=[]
 sector_status=[]
 for sid in sorted(sectorprops):
  s=series[sid]
  for mo in range(1,13):
   keys=[m for m in s if int(m[-2:])==mo]
   values=[s[k] for k in sorted(keys)]
   dispersions=[scatter[sid][k] for k in keys if k in scatter[sid]]
   n_cells=[cells[sid][k] for k in keys]
   month_csv.append({"sector":sid,"mes_calendario":mo,
       "precipitacion_chirps_mm":round(statistics.mean(values),3) if values else "",
       "dispersion_espacial_med_mm":round(statistics.median(dispersions),3) if dispersions else "",
       "n_anios_mes_con_datos":len(values),
       "n_celdas_terrestres_en_promedio":round(statistics.mean(n_cells),2) if n_cells else "",
       "periodo_fuente":"1996-2025" if len(values)==30 else "parcial_1996_2025",
       "homogeneidad_validada":"false"})
  wet=[s.get(f"{y}-{m:02d}") for y in years_complete for m in (1,2,3)]
  annually=[sum(s[f"{y}-{m:02d}"] for m in range(1,13))
            for y in years_complete if all(f"{y}-{m:02d}" in s for m in range(1,13))]
  year_n=len(annually)
  prop=sectorprops[sid]
  sector_status.append({"id":sid,"piso":prop["estrato"],
      "n_pixeles_chirps_terrestres_mediana":int(statistics.median(cells[sid].values())) if cells[sid] else 0,
      "n_meses_chirps":len(s),"n_anios_completos":year_n,
      "precipitacion_anual_media_mm":round(statistics.mean(annually),2) if annually else None,
      "precipitacion_anual_cv":round(statistics.pstdev(annually)/statistics.mean(annually),4)
              if year_n>1 and statistics.mean(annually)>0 else None,
      "media_lluvia_ene_feb_mar_mm_mes":round(statistics.mean(wet),2) if wet and all(x is not None for x in wet) else None,
      "homogeneidad_climatica_certificada":False,
      "prediccion_fitosanitaria_validada":False})
 # climatologías de 81 testigos de reanálisis, más CHIRPS sobre píxel consultado
 witness_normal=[]
 for pid,p in sorted(climate.items()):
  for mo in range(1,13):
   entries=[era[(pid,f"{y}-{mo:02d}")] for y in DEF_YEARS]
   chirps=[v for m,v in pixs[pid].items() if int(m[-2:])==mo]
   witness_normal.append({"testigo":pid,"estrato":p["estrato_fisico_preliminar"],
     "mes_calendario":mo,
     "temp_c":round(statistics.mean(v["temperature_2m_mean"] for v in entries),4),
     "rain_era5_mm":round(statistics.mean(v["precipitation_sum"] for v in entries),4),
     "rh_pct":round(statistics.mean(v["relative_humidity_2m_mean"] for v in entries),4),
     "radiation_mj_m2":round(statistics.mean(v["shortwave_radiation_sum"] for v in entries),4),
     "rain_chirps_pixel_mm":round(statistics.mean(chirps),4) if chirps else "",
     "n_meses_fuentes_chirps":len(chirps),
     "n_anios_perfil_era5":30,
     "metodo":"reanálisis 30 años + CHIRPS píxel 0,05° (no sensor)"})
 families=obj(FAMILIES)["familias"]
 comparisons=[]
 for fam in families:
  pts=fam["ids_testigos"]
  for i,a in enumerate(pts):
   for b in pts[i+1:]:
    if a not in pixs or b not in pixs:continue
    d=group_compare(pixs[a],pixs[b],index)
    a_era={month:era[(a,month)]["temperature_2m_mean"] for month in index}
    b_era={month:era[(b,month)]["temperature_2m_mean"] for month in index}
    ta=[a_era[m] for m in sorted(index)];tb=[b_era[m] for m in sorted(index)]
    # Nota: correlación ERA5-Land entre píxeles: independencia no demostrada.
    comparisons.append({"familia":fam["id"],"testigo_a":a,"testigo_b":b,
        "piso":fam["estrato"],"misma_celda_chirps":next(
           (coord for coord,ids in unique_cell.items() if a in ids and b in ids),None)!=None,
        **d,"diferencia_tmedia_era5_land_c":round(abs(statistics.mean(ta)-statistics.mean(tb)),3),
        "reanálisis_independencia_validada":False})
 hydro=obj(LINKS)
 linked=defaultdict(set)
 for f in hydro["features"]:
  ids=f["properties"]["nodos_sectores_origen"]
  if len(ids)>1:
   for i,a in enumerate(ids):
    for b in ids[i+1:]:linked[(min(a,b),max(a,b))].add(f["properties"]["codigo_hidrografico"])
 candidate=[]
 for (a,b),codes in sorted(linked.items()):
  x=group_compare(series[a],series[b],index)
  candidate.append({"sectores":[a,b],"unidades_hidrograficas":sorted(codes),
     "mismo_piso":sectorprops[a]["estrato"]==sectorprops[b]["estrato"],
     "tiempo_1996_2025_completo":len(years_complete)==30,
     **x,"fusion_climatica_validada":False})
 station=obj(ROOT/"datos/validacion_estaciones_9i/diagnostico_multianual_9i.json")
 summary={"fase":"9O","periodo_objetivo":"1996-2025",
    "producto_grilla":"CHIRPS v3 final LATAM, 0.05° mensual",
    "meses_fuente_chirps":len(index),"anios_chirps_con_12_meses":years_complete,
    "numero_anios_completos_para_normales_chirps":len(years_complete),
    "n_normales_mes_sector":len(month_csv),"n_testigos_reanalisis_30anios":len(climate),
    "n_normales_mes_testigo_reanalisis":len(witness_normal),
    "n_testigos_chirps_con_pixel_unico":len(unique_cell),
    "n_celdas_chirps_compartidas_entre_testigos":sum(len(ids)>1 for ids in unique_cell.values()),
    "n_sectores":len(sector_status),
    "n_familias_comparadas":len(families),
    "n_pares_testigos_agrupados_chirps":len(comparisons),
    "n_pares_sector_misma_unidad_hidrografica":len(candidate),
    "periodo_completo_chirps":len(index)==360 and len(years_complete)==30,
    "validacion_externa_instrumental_independiente":False,
    "estaciones_instrumentales_9i":station["estaciones_n"],
    "meses_estacion_unicos_9i":station["meses_estacion_unicos_emparejados"],
    "observaciones_instrumentales_1996_2025_por_sector":0,
    "zonas_climaticas_homogeneas_certificadas":0,
    "modelo_predictivo_validado_por_sectores":False,
    "contraste_CHIRPS_vs_ERA5_no_es_prueba_independiente":True,
    "relieve_continuo_procede_de_Copernicus_DSM":True,
    "criterio_similitud_para_sugerir_agrupacion":"corr de anomalías log1p desestacionalizadas de lluvia y diferencia relativa media; descriptivo, sin umbral que certifique",
    "candidatos_hidro_climaticos":candidate,
    "comparaciones_testigos_nucleos":comparisons,
    "resumen_sectores":sector_status,
    "limitaciones":[
      "CHIRPS v3 es una combinación satélite/pluviómetros; puede compartir observaciones con series de estaciones.",
      "Una normal CHIRPS 1996–2025 requiere 360 meses disponibles, sin imputar meses faltantes.",
      "La variación en píxeles 0,05° dentro del polígono no mide la variabilidad a escala de parcela.",
      "ERA5 y ERA5-Land son modelos distintos y las celdas pueden repetirse entre testigos.",
      "No usar correlación climática de dos sectores como licencia de fusión; contrastar cuencas, relieve, estaciones independientes, cultivos y cambios históricos.",
      "Los indicadores retrospectivos no representan la precisión de una emisión predictiva ex ante.",
      "No se emiten umbrales fitosanitarios para arándano o vid sin evaluaciones reales de campo."] }
 return summary,month_csv,witness_normal

def save(check=False):
 j,rows,wn=analyse()
 if check:
  current=obj(SUMMARY)
  if current!=j:raise ValueError("Diagnóstico 9O no se reproduce")
  a=read_csv(MONTHLY);b=read_csv(WITNORMS)
  if len(a)!=len(rows) or len(b)!=len(wn):
   raise ValueError("CSV de normales incompleto")
 else:
  BASE.mkdir(parents=True,exist_ok=True)
  SUMMARY.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  for path,ls,cols in ((MONTHLY,rows,NCOLS),(WITNORMS,wn,WCOLS)):
   with path.open("w",encoding="utf8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(ls)
 print("9O:",j["meses_fuente_chirps"],"meses CHIRPS;",
       j["numero_anios_completos_para_normales_chirps"],"años completos;",
       len(j["candidatos_hidro_climaticos"]),"pares hidro-gráficos evaluados.")
 return j
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true")
 save(check=ap.parse_args().check)
