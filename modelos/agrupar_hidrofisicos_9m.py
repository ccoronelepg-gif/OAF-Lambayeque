#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9M: agrupación cartográfica exploratoria por PISO + HIDROCODIGO + NÚCLEO.
No debe confundirse con delimitación oficial ANA ni zonas de pronóstico.
Geometrías de diferentes niveles de jerarquía se vuelven excluyentes por sector
(primero códigos más específicos) antes de disolver: evita contar área dos veces.
"""
import argparse,csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
from shapely.geometry import shape,mapping
from shapely.ops import unary_union, transform
from shapely import make_valid
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
ROOTD=ROOT/"datos/sensibilidad_9m"
IN_H=ROOTD/"cruces_hidrograficos_9m.geojson"
IN_HSTATE=ROOTD/"estado_cuencas_ana_9m.json"
IN_Z=ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson"
IN_T=ROOTD/"estado_relieve_9m.json"
GEO=ROOTD/"grupos_hidrofisicos_9m.geojson"
STATE=ROOTD/"estado_grupos_9m.json"
TABLE=ROOTD/"grupos_territoriales_9m.csv"
PROJ=Transformer.from_crs("EPSG:4326","EPSG:32717",always_xy=True).transform
BACK=Transformer.from_crs("EPSG:32717","EPSG:4326",always_xy=True).transform
COLUMNS=("id","piso","codigo_hidrografico","nombre_unidad","familia_climatica",
 "n_sectores_origen","nodos_sectores_origen","area_aprox_km2","cobertura_dem_regional",
 "clima_homogeneo_validado","cuenca_certificada")

def pieces(x):
 if not x.is_valid:x=make_valid(x)
 if x.geom_type=="Polygon":return [x] if x.area>0 else []
 if x.geom_type=="MultiPolygon":return [y for y in x.geoms if y.area>0]
 out=[]
 for g in getattr(x,"geoms",[]):out.extend(pieces(g))
 return out

def compute():
 h=json.loads(IN_H.read_text("utf8"))
 hs=json.loads(IN_HSTATE.read_text("utf8"))
 prev=json.loads(IN_Z.read_text("utf8"))
 terrain=json.loads(IN_T.read_text("utf8"))
 if len(prev["features"])!=42 or terrain["n_sectores_9k"]!=42:
  raise ValueError("Inventario 9K/9M incongruente")
 if hs["n_cuencas_certificadas_por_oaf"]!=0:
  raise ValueError("ANA no cumple condición de no certificación")
 if len(h["features"])!=hs["n_intersecciones_referenciales"]:
  raise ValueError("Cruces ANA alterados")
 props={f["properties"]["id_sector"]:f["properties"] for f in prev["features"]}
 # Priorizar códigos de mayor desagregación para no fusionar geometrías superpuestas.
 by_sector=defaultdict(list)
 for f in h["features"]:
  p=f["properties"];sid=p["sector_9k"]
  if sid not in props:raise ValueError("Sector hidrográfico desconocido")
  poly=transform(PROJ,shape(f["geometry"]))
  if poly.is_empty:continue
  code=p["codigo_referencial"]
  by_sector[sid].append((str(code),p["nombre_en_capa"],poly))
 groups=defaultdict(list)
 dup_area=0.
 n_atom=0
 for sid,items in sorted(by_sector.items()):
  used=None
  for code,name,poly in sorted(items,key=lambda z:(-len(z[0]),z[0])):
   if used is not None:
    dup_area+=poly.intersection(used).area
    poly=poly.difference(used)
   atoms=[p for p in pieces(poly) if p.area>=10000]  # min 0.01 km² de escala temática
   if not atoms:continue
   if used is None:used=unary_union(atoms)
   else:used=unary_union([used,*atoms])
   p=props[sid];fam=p["familia_similitud"] or "sin_nucleo"
   groups[(p["estrato"],code,fam,name)].extend((sid,part) for part in atoms)
   n_atom+=len(atoms)
 features=[];tab=[]
 for (floor,code,fam,name),items in sorted(groups.items()):
  joined=unary_union([g for _,g in items])
  for geom in sorted(pieces(joined),key=lambda x:(round(x.centroid.x,1),round(x.centroid.y,1))):
   if geom.area<10000:continue
   sids=sorted({sid for sid,piece in items if piece.intersection(geom).area>1000})
   if not sids:continue
   number=f"HM{len(features)+1:03d}"
   area=round(geom.area/1e6,3)
   limited=unary_union(pieces(transform(BACK,geom).simplify(.0002,preserve_topology=True)))
   if limited.is_empty:continue
   coverage=("parcial_DEM_S07W080" if terrain["n_sector_evaluados_con_dos_escalas"]<42
     else "DEM_contraste_en_42_sectores")
   pr={"id":number,"piso":floor,"codigo_hidrografico":code,
       "nombre_unidad":name,"familia_climatica":fam if fam!="sin_nucleo" else None,
       "n_sectores_origen":len(sids),"nodos_sectores_origen":sids,
       "area_aprox_km2":area,
       "cobertura_dem_regional":coverage,
       "clima_homogeneo_validado":False,
       "cuenca_certificada":False,
       "agrupacion_operativa":False,
       "vinculo_experimental":"piso + codigo fuente + núcleo 8P cuando existe"}
   features.append({"type":"Feature","properties":pr,"geometry":mapping(limited)})
   tab.append({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,list) else
                "" if v is None else v) for k,v in pr.items() if k in COLUMNS})
 summary={"fase":"9M","fecha_corte":"2026-10-17",
   "fuente_ANA_descargada":hs["cobertura_institucional_capa_descargada"],
   "n_sectores_9k_originales":42,
   "n_sectores_con_cruce":len(by_sector),
   "n_cruces_ANA_originales":len(h["features"]),
   "n_fragmentos_atomo_tras_quitar_duplicaciones":n_atom,
   "n_agrupaciones_hidrofisicas":len(features),
   "n_grupos_con_dos_o_mas_sectores":sum(f["properties"]["n_sectores_origen"]>=2 for f in features),
   "n_grupos_con_nucleo_climatico":sum(bool(f["properties"]["familia_climatica"]) for f in features),
   "n_pisos_con_grupos":len({f["properties"]["piso"] for f in features}),
   "area_solapada_entre_niveles_removida_km2":round(dup_area/1e6,3),
   "prioridad_de_desduplicacion":"Codigo hidrografico mas largo primero; luego orden lexicografico, dentro de cada sector 9K.",
   "cobertura_topografica_total":False,
   "n_cuencas_operativas_certificadas":0,
   "n_zonas_homogeneas_validadas":0,
   "modelo_zonal_con_habilidad_demostrada":False,
   "uso_agricola_certificado":False,
   "fuentes_sha256":{"9K":hashlib.sha256(IN_Z.read_bytes()).hexdigest(),
      "cruces_IDEP_ANA":hashlib.sha256(IN_H.read_bytes()).hexdigest(),
      "estado_dem":hashlib.sha256(IN_T.read_bytes()).hexdigest()},
   "interpretacion":"Agrupación física exploratoria y de cartografía ANA/IDEP. No implica microclima uniforme: los grupos sin núcleo climático son prioritariamente de muestreo.",
   "limites":["Se usan intersecciones de una capa servida por IDEP atribuida a ANA, no verificación jurídica ni catastral.",
    "El filtro de 9M sobre pendiente y aspecto cubre una tesela, no todo el ámbito de los grupos.",
    "Los códigos anidados de ANA se priorizan para evitar contar superficies duplicadas.",
    "El área es geométrica aproximada por UTM 17S de polígonos 9K ya simplificados, no hectáreas cultivadas.",
    "No se han calibrado pronósticos NOAA por agrupación o verificado fitosanidad de arándano y vid."]}
 geo={"type":"FeatureCollection","name":"OAF 9M agrupaciones exploratorias por hidrografía y piso",
      "metadata":{"fase":"9M","cuencas_oficialmente_certificadas":False,
       "zonas_climaticas_homogeneas_validadas":False,
       "criterio":"piso y código hidrográfico; no fusionar superficies desconectadas"},
      "features":features}
 return geo,summary,tab

def run(check=False):
 g,s,t=compute()
 if check:
  if json.loads(GEO.read_text("utf8"))!=json.loads(json.dumps(g)):
   raise ValueError("Agrupación 9M no reproducible")
  if json.loads(STATE.read_text("utf8"))!=s:
   raise ValueError("Estado 9M agrupado no reproducible")
  with TABLE.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
  if len(rows)!=len(t):raise ValueError("CSV de grupos incompleto")
 else:
  GEO.write_text(json.dumps(g,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
  STATE.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  with TABLE.open("w",newline="",encoding="utf-8") as f:
   writer=csv.DictWriter(f,fieldnames=COLUMNS);writer.writeheader();writer.writerows(t)
 print("9M agrupación hidrofísica:",s["n_agrupaciones_hidrofisicas"],"fragmentos,",
       s["n_grupos_con_dos_o_mas_sectores"],"multisector.")
 return s
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
 run(check=p.parse_args().check)
