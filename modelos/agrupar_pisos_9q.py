#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9Q: comparar seis pisos altitudinales e identificar agrupaciones exploratorias.
Nunca confundir bandas de elevación con pisos ecológicos oficiales SENAMHI/IGN.
No permite fusiones automáticas de sectores sin datos y sin verificación instrumental.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import shape,Point
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/recuperacion_9q"
BASE.mkdir(parents=True,exist_ok=True)
M=BASE/"fuentes_chirps_9q.json"
S=BASE/"sectores_mensuales_9q.csv"
REPORT=BASE/"diagnostico_pisos_y_agrupaciones_9q.json"
FLOORS=BASE/"comparacion_pisos_9q.csv"
PAIRS=BASE/"pares_hidroclimaticos_9q.csv"
GROUPS=BASE/"agrupaciones_exploratorias_9q.geojson"
METADATA=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
HYDRO=ROOT/"datos/sensibilidad_9m/cruces_hidrograficos_9m.geojson"
NORMS=ROOT/"datos/homogeneidad_9o/normales_testigos_multivariable_9o.csv"
M9O=ROOT/"datos/homogeneidad_9o/fuentes_chirps_9o.json"
S9O=ROOT/"datos/homogeneidad_9o/serie_sectores_chirps_9o.csv"
M9P=ROOT/"datos/continuidad_9p/fuentes_adicionales_chirps_9p.json"
S9P=ROOT/"datos/continuidad_9p/meses_adicionales_sectores_9p.csv"

CLASSES={
 "llanura_costa":("Planicie litoral",0,100),
 "valle_bajo":("Valle bajo",100,300),
 "piedemonte":("Piedemonte",300,800),
 "montana_baja":("Ladera baja",800,1600),
 "montana_media":("Ladera media",1600,2500),
 "montana_alta":("Montaña alta",2500,None),
 "cota_negativa_revisar":("Cota negativa DSM: revisar",None,0)}
PERIODS={"1996-2005":range(1996,2006),"2006-2015":range(2006,2016),
         "2016-2025":range(2016,2026)}
FCOLS=("clase_piso","etiqueta","cota_min_m","cota_max_m","n_sectores",
 "sectores_con_lluvia_valida","n_sectores_con_perfil_era5","n_anios_referencia_fuentes",
 "lluvia_anual_mediana_sectores_mm","lluvia_anual_min_sectores_mm",
 "lluvia_anual_max_sectores_mm","lluvia_anual_cv_entre_sectores",
 "temperatura_era5land_media_testigos_c","humedad_era5_media_testigos_pct",
 "radiacion_era5_media_testigos_mj_m2_dia_equiv",
 "interpretacion")
PCOLS=("sector_a","sector_b","piso","codigos_hidrograficos_comunes",
 "pixeles_chirps_compartidos_n","n_píxeles_a","n_píxeles_b",
 "n_anios_completos_comunes","correlacion_anomalias_lluvia",
 "corr_sin_1996_2005","corr_sin_2006_2015","corr_sin_2016_2025",
 "diferencia_lluvia_anual_pct","diferencia_t_era5_c",
 "diferencia_hr_era5_pctp","diferencia_radiacion_era5_pct",
 "distancia_geom_grados","criterio_lluvia_exploratorio","todas_variables_comprobadas",
 "candidato_agrupacion_provisional","agrupacion_validada")

def j(path):return json.loads(path.read_text(encoding="utf8"))
def csvrows(path):
 with path.open(encoding="utf8-sig",newline="") as f:return list(csv.DictReader(f))
def rounded(v,dec=3):return round(float(v),dec) if v is not None and math.isfinite(float(v)) else None
def pearson(a,b):
 if len(a)<24:return None
 mx,my=statistics.mean(a),statistics.mean(b)
 x=[z-mx for z in a];y=[z-my for z in b]
 denom=math.sqrt(sum(v*v for v in x)*sum(v*v for v in y))
 return rounded(sum(p*q for p,q in zip(x,y))/denom,5) if denom>1e-12 else None
def corr(a,b,years):
 xs=[];ys=[]
 for m in range(1,13):
  c=[(a[f"{y}-{m:02d}"],b[f"{y}-{m:02d}"]) for y in years]
  if len(c)<2:return None
  q=[math.log1p(x) for x,y in c];r=[math.log1p(y) for x,y in c]
  mq,mr=statistics.mean(q),statistics.mean(r)
  xs.extend(v-mq for v in q);ys.extend(v-mr for v in r)
 return pearson(xs,ys)

def load():
 original=[]
 for label,manifest_path,series_path,lookup in (
    ("9O",M9O,S9O,"fuentes"),("9P",M9P,S9P,"nuevos"),("9Q",M,S,"nuevos")):
  src=j(manifest_path)
  months={x["mes"]:x["sha256"] for x in src[lookup]}
  if len(months)!=len(src[lookup]):raise ValueError("CHIRPS meses duplicados en "+label)
  values=csvrows(series_path)
  if len(values)!=42*len(months):raise ValueError("CHIRPS incompleto "+label)
  for v in values:
   if v["mes"] not in months or v["sha256_tiff"]!=months[v["mes"]]:
    raise ValueError("Fuente sin SHA validada en "+label)
  original.append((months,values))
 months={}
 rain=defaultdict(dict)
 for monthsource,rs in original:
  if set(months)&set(monthsource):raise ValueError("Meses CHIRPS superpuestos entre fases")
  months.update(monthsource)
  for r in rs:
   if r["precipitacion_promedio_pixel_mm"]!="":
    x=float(r["precipitacion_promedio_pixel_mm"])
    if not 0<=x<10000:raise ValueError("Precipitación imposible")
    rain[r["sector"]][r["mes"]]=x
 sectors=j(METADATA)["features"]
 if len(sectors)!=42:raise ValueError("Se perdió sector")
 normals=csvrows(NORMS)
 if len(normals)!=81*12:raise ValueError("Reanálisis mensual testigos incompleto")
 return months,rain,sectors,normals

def masks_on_native_grid(sectors):
 # Huella de centros CHIRPS 0.05 grados inferida del transform ORIGINAL comprobado 9O.
 t=j(M9O)["fuentes"][0]["raster_transform"]
 step=float(t[0]);left=float(t[2]);top=float(t[3])
 cells={}
 for s in sectors:
  region=shape(s["geometry"]);p=s["properties"];found=set()
  for lonidx in range(39):
   lon=left+step*(lonidx+.5)
   if not region.bounds[0]<=lon<=region.bounds[2]:continue
   for latidx in range(40):
    lat=top-step*(latidx+.5)
    if region.bounds[1]<=lat<=region.bounds[3] and region.contains(Point(lon,lat)):
     found.add((latidx,lonidx))
  cells[p["id_sector"]]=found
 return cells

def compare():
 months,rain,sectors,normals=load()
 ids={s["properties"]["id_sector"]:s for s in sectors}
 decadal={k:sum(all(f"{y}-{m:02d}" in months for m in range(1,13)) for y in years)
          for k,years in PERIODS.items()}
 complete=[y for y in range(1996,2026) if all(f"{y}-{m:02d}" in months for m in range(1,13))]
 if len(months)==360 and len(complete)!=30:raise ValueError("Fuente con meses duplicados")
 witness=defaultdict(list)
 for r in normals:witness[r["testigo"]].append(r)
 meanw={}
 for wid,items in witness.items():
  meanw[wid]={
   "temp":statistics.mean(float(r["temp_c"]) for r in items),
   "rh":statistics.mean(float(r["rh_pct"]) for r in items),
   "rad":statistics.mean(float(r["radiation_mj_m2"]) for r in items)}
 sectorclim={}
 for sid,f in ids.items():
  refs=[meanw[x] for x in f["properties"]["testigos_asociados"] if x in meanw]
  sectorclim[sid]={k:statistics.mean(r[k] for r in refs) for k in ("temp","rh","rad")} if refs else None
 floorrows=[]
 for name,(label,lo,hi) in CLASSES.items():
  group=sorted([s for s,f in ids.items() if f["properties"]["estrato"]==name])
  rvalues=[];climate=[]
  for sid in group:
   vals=[sum(rain[sid][f"{y}-{m:02d}"] for m in range(1,13))
         for y in complete if all(f"{y}-{m:02d}" in rain[sid] for m in range(1,13))]
   if len(vals)==len(complete) and vals:rvalues.append(statistics.mean(vals))
   if sectorclim[sid]:climate.append(sectorclim[sid])
  mid=statistics.mean(rvalues) if rvalues else 0
  cvs=statistics.pstdev(rvalues)/mid if len(rvalues)>1 and mid>0 else None
  floorrows.append({"clase_piso":name,"etiqueta":label,"cota_min_m":lo,"cota_max_m":hi,
   "n_sectores":len(group),"sectores_con_lluvia_valida":len(rvalues),
   "n_sectores_con_perfil_era5":len(climate),
   "n_anios_referencia_fuentes":len(complete),
   "lluvia_anual_mediana_sectores_mm":rounded(statistics.median(rvalues),2) if rvalues else None,
   "lluvia_anual_min_sectores_mm":rounded(min(rvalues),2) if rvalues else None,
   "lluvia_anual_max_sectores_mm":rounded(max(rvalues),2) if rvalues else None,
   "lluvia_anual_cv_entre_sectores":rounded(cvs,4),
   "temperatura_era5land_media_testigos_c":rounded(statistics.mean(x["temp"] for x in climate),2) if climate else None,
   "humedad_era5_media_testigos_pct":rounded(statistics.mean(x["rh"] for x in climate),2) if climate else None,
   "radiacion_era5_media_testigos_mj_m2_dia_equiv":rounded(statistics.mean(x["rad"] for x in climate),2) if climate else None,
   "interpretacion":"clase_de_altitud_exploratoria_no_ecorregion_SENAMHI"})
 hydro=j(HYDRO)["features"]
 codes=defaultdict(set)
 for f in hydro:
  prop=f["properties"];codes[prop["sector_9k"]].add(prop["codigo_referencial"])
 cells=masks_on_native_grid(sectors)
 candidate=[]
 for i,a in enumerate(sorted(ids)):
  for b in sorted(ids)[i+1:]:
   fa,fb=ids[a],ids[b]
   floor=fa["properties"]["estrato"]
   if floor!=fb["properties"]["estrato"] or floor=="cota_negativa_revisar":continue
   common=sorted(codes[a]&codes[b])
   if not common:continue
   ga,gb=shape(fa["geometry"]),shape(fb["geometry"])
   dist=ga.distance(gb)
   if dist>0.14:continue
   years=[y for y in complete if all(f"{y}-{m:02d}" in rain[a] and
               f"{y}-{m:02d}" in rain[b] for m in range(1,13))]
   if len(years)<3:continue
   shared=cells[a]&cells[b]
   ra=sum(rain[a][f"{y}-{m:02d}"] for y in years for m in range(1,13))
   rb=sum(rain[b][f"{y}-{m:02d}"] for y in years for m in range(1,13))
   gap=200*abs(ra-rb)/(ra+rb) if ra+rb>0 else None
   correlations={n:corr(rain[a],rain[b],[y for y in years if y not in per])
            for n,per in PERIODS.items()
            if len([y for y in years if y not in per])>=3}
   r=corr(rain[a],rain[b],years)
   ca,cb=sectorclim[a],sectorclim[b]
   temp=abs(ca["temp"]-cb["temp"]) if ca and cb else None
   rh=abs(ca["rh"]-cb["rh"]) if ca and cb else None
   rad=200*abs(ca["rad"]-cb["rad"])/(ca["rad"]+cb["rad"]) if ca and cb and ca["rad"]+cb["rad"]>0 else None
   rainpass=bool(r is not None and r>=0.80 and gap is not None and gap<=25
      and len(years)>=10 and shared==set() and
      all(v is not None and v>=0.70 for v in correlations.values()))
   multi=bool(ca and cb and temp<=2 and rh<=12 and rad is not None and rad<=25)
   grouping=rainpass and multi
   candidate.append({"sector_a":a,"sector_b":b,"piso":floor,
      "codigos_hidrograficos_comunes":";".join(common),
      "pixeles_chirps_compartidos_n":len(shared),
      "n_píxeles_a":len(cells[a]),"n_píxeles_b":len(cells[b]),
      "n_anios_completos_comunes":len(years),"correlacion_anomalias_lluvia":r,
      "corr_sin_1996_2005":correlations.get("1996-2005"),
      "corr_sin_2006_2015":correlations.get("2006-2015"),
      "corr_sin_2016_2025":correlations.get("2016-2025"),
      "diferencia_lluvia_anual_pct":rounded(gap,3),
      "diferencia_t_era5_c":rounded(temp,3),
      "diferencia_hr_era5_pctp":rounded(rh,3),
      "diferencia_radiacion_era5_pct":rounded(rad,3),
      "distancia_geom_grados":rounded(dist,5),
      "criterio_lluvia_exploratorio":str(rainpass).lower(),
      "todas_variables_comprobadas":str(multi).lower(),
      "candidato_agrupacion_provisional":str(grouping).lower(),
      "agrupacion_validada":"false"})
 # Agrupar con condición estricta: nunca puente transitivo entre A-B y B-C sin A-C.
 chosen=sorted([r for r in candidate if r["candidato_agrupacion_provisional"]=="true"],
               key=lambda x:(x["piso"],x["sector_a"],x["sector_b"]))
 eligible={tuple(sorted((r["sector_a"],r["sector_b"]))) for r in chosen}
 groups=[];assigned=set()
 for x in chosen:
  a,b=x["sector_a"],x["sector_b"]
  if a in assigned or b in assigned:continue
  members=[a,b];assigned.update(members)
  same=[t for t in chosen if t["piso"]==x["piso"]]
  for r in same:
   for c in (r["sector_a"],r["sector_b"]):
    if c not in assigned and all(tuple(sorted((c,member))) in eligible for member in members):
     members.append(c);assigned.add(c)
  polygon=unary_union([shape(ids[v]["geometry"]) for v in members])
  groups.append({"type":"Feature","geometry":polygon.__geo_interface__,
   "properties":{"id":f"Q{len(groups)+1:02d}","piso":x["piso"],
     "sectores":members,"n_sectores":len(members),
     "estado":"hipotesis_hidrofisica_multivariable_no_certificada",
     "puntos_campo_independientes":0,
     "limite_oficial":False,"zona_homogenea_validada":False,
     "pronostico_zonal_validado":False}})
 result={"fase":"9Q","fecha_corte":"2026-10-17","serie_objetivo":"1996-2025",
  "meses_chirps_360":len(months),"n_meses_faltantes":360-len(months),
  "n_anios_fuente_completos":len(complete),"anios_completos":complete,
  "anios_completos_decada":decadal,
  "n_sectores":len(ids),"n_pisos_exploratorios":len(CLASSES),
  "n_sectores_sin_centro_pixel":sum(not rain[sid] for sid in ids),
  "comparacion_de_pisos":floorrows,
  "n_pares_mismo_piso_cuenca_cercanos_evaluados":len(candidate),
  "n_pares_lluvia_y_testigos_multivariable_satisfacen_criterios":len(chosen),
  "n_grupos_propuestos":len(groups),
  "n_zonas_homogeneas_instrumentalmente_certificadas":0,
  "n_estaciones_instrumentales_independientes_30anios":0,
  "precipitacion_chirps_satellites_y_pluviometros_no_independiente":True,
  "testigos_era5_era5land_no_estaciones_in_situ":True,
  "agrupacion_no_interpretable_como_ecorregion_senamhi":True,
  "aptitud_agricola_aranadano_vid_validada":False,
  "habilidad_pronostico_exante_validada":False,
  "reglas_exploratorias_predefinidas":{
   "mismo_estrato_altitudinal":True,"misma_unidad_hidrografica_referencial":True,
   "distancia_maxima_en_grados":.14,"pixeles_chirps_no_duplicados":True,
   "min_anios_comunes":10,"corr_log1p_anomalias_minima":.8,
   "diferencia_media_lluvia_maxima_pct":25,
   "corr_excluyendo_decadas_minima":.7,
   "diferencia_temp_reanalisis_maxima_c":2,
   "diferencia_hr_reanalisis_maxima_puntos":12,
   "diferencia_radiacion_reanalisis_maxima_pct":25,
   "fusion_sin_puentes_transitivos":True},
  "advertencias":[
   "Bandas altitudinales son estratos metodológicos y NO pisos ecológicos oficiales; comparar con mapa SENAMHI Thornthwaite.",
   "Medias entre sectores no están ponderadas por área y pueden reutilizar celdas CHIRPS.",
   "Anomalías históricas CHIRPS no demuestran habilidad de una predicción ex ante.",
   "La estación instrumental histórica y la asimilación de pluviómetros CHIRPS pueden compartir fuentes.",
   "Los umbrales de similitud son filtros experimentales; no se han calibrado contra parcelas.",
   "Radiación en tabla conserva unidades del reanálisis original; no inferir radiación solar diaria real sin conversión validada.",
   "Sectores sin píxel CHIRPS deben mantenerse separados, no interpolar al sector vecino."]}
 features={"type":"FeatureCollection","metadata":{"fase":"9Q",
   "agrupaciones_certificadas":0,"cartografia_experimental":True,
   "n_grupos":len(groups)},"features":groups}
 return result,floorrows,candidate,features

def run(check=False):
 state,perfloor,candidates,features=compare()
 if check:
  if j(REPORT)!=state or j(GROUPS)!=features:
   raise ValueError("Comparación 9Q no se reproduce")
  if len(csvrows(FLOORS))!=len(perfloor) or len(csvrows(PAIRS))!=len(candidates):
   raise ValueError("Salidas 9Q difieren en número de filas")
 else:
  REPORT.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  GROUPS.write_text(json.dumps(features,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
  for filename,items,cols in ((FLOORS,perfloor,FCOLS),(PAIRS,candidates,PCOLS)):
   with filename.open("w",encoding="utf8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(items)
 print("9Q pisos:",len(perfloor),"bandas;",
    state["meses_chirps_360"],"/360 meses;",
    len(candidates),"pares comparados;",
    len(features["features"]),"hipótesis de agrupación")
 return state
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 run(check=p.parse_args().check)
