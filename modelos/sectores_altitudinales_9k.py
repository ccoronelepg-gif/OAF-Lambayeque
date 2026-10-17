#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF 9K: sectores SIG exploratorios con altitud, contigüidad y clima 1996–2025.
No son límites oficiales, parcelas, superficies homogéneas certificadas ni pronósticos.
Dependencias de generación: shapely>=2.1, pyproj>=3.6 (CI congelado por versión).
La salida es determinista y se audita frente al CSV y GeoJSON fuente.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict, Counter
from pathlib import Path
from shapely.geometry import shape, mapping, MultiPoint, Point, Polygon, MultiPolygon
from shapely import voronoi_polygons, make_valid
from shapely.ops import transform, unary_union
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
DEM=ROOT/"datos/muestreo_8o/nodos_dem_8o.csv"
WIT=ROOT/"datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv"
SIM=ROOT/"datos/clima_contiguo_8p/pares_similares_exploratorios_8p.csv"
BOUND=ROOT/"datos/zonificacion_8n/limite_lambayeque_referencial.geojson"
STATE=ROOT/"datos/clima_contiguo_8p/estado_clima_8p.json"
DEST=ROOT/"datos/sectores_agroclimaticos_9k"
GEO=DEST/"sectores_muestreo_9k.geojson"
OUT=DEST/"estado_sectores_9k.json"
TABLE=DEST/"asignacion_nodos_9k.csv"
PROJ=Transformer.from_crs("EPSG:4326","EPSG:32717",always_xy=True).transform
UNPROJ=Transformer.from_crs("EPSG:32717","EPSG:4326",always_xy=True).transform
MAX_R=5500 # polígono de influencia gráfica máxima 5.5 km, NO máscara DEM exhaustiva
DIST_W=12000 # testigo climático próximo hasta 12 km
DZ=180 # desnivel máximo para asignación exploratoria de núcleo climático
CLASSES=("llanura_costa","valle_bajo","piedemonte","montana_baja","montana_media",
         "montana_alta","cota_negativa_revisar")
COLS=("id","latitud","longitud","altitud_dem_m","estrato_fisico_preliminar",
      "testigo_climatico_asociado","distancia_testigo_km",
      "familia_multicelda","nivel_soporte","homogeneidad_validada")

def rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def source_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def read():
    dem=rows(DEM)
    witness=rows(WIT)
    similar=rows(SIM)
    state=json.loads(STATE.read_text("utf8"))
    region=json.loads(BOUND.read_text("utf8"))
    if len(dem)!=420 or len(witness)!=81 or state.get("testigos_total_con_30_anios")!=81:
        raise ValueError("Insumos DEM 420 y perfiles 81 incompletos")
    if state.get("zonas_homogeneas_geograficas_certificadas")!=0:
        raise ValueError("8P no conserva su estado experimental")
    if region["features"][0]["properties"]["codigo_ubigeo"]!="14":
        raise ValueError("Límite regional no corresponde a Lambayeque")
    region_m=transform(PROJ,shape(region["features"][0]["geometry"]))
    if region_m.is_empty or not region_m.is_valid:raise ValueError("Límite regional inválido")
    d={}
    for item in dem:
        ident=item["id"]
        if ident in d:raise ValueError("DEM duplicado")
        lat,lon,alt=(float(item[x]) for x in ("latitud","longitud","altitud_dem_m"))
        strat=item["estrato_fisico_preliminar"]
        if strat not in CLASSES:raise ValueError("Estrato DEM desconocido")
        pt=Point(PROJ(lon,lat))
        if not region_m.buffer(5).covers(pt):
            raise ValueError("Centro muestreado fuera del límite")
        d[ident]={"id":ident,"lat":lat,"lon":lon,"alt":alt,"estrato":strat,"p":pt}
    w={}
    for item in witness:
        code=item["id"]
        if code not in d or code in w or item["perfil_completo_1996_2025"]!="true":
            raise ValueError("Testigo climático fuera de DEM, duplicado o incompleto")
        if item["apto_para_zona_operativa"]!="false":
            raise ValueError("Perfil está indebidamente declarado operativo")
        if abs(float(item["altitud_dem_m"])-d[code]["alt"])>1e-5:
            raise ValueError("Testigo y DEM altitud no coinciden")
        w[code]=d[code]
    return d,w,similar,region_m

def families(w,edges):
    """Componentes SOLO entre centros ERA5 y ERA5-Land distintos, dentro de estrato."""
    parent={code:code for code in w}
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb:parent[max(ra,rb)]=min(ra,rb)
    accepted=[]
    n_shared=0
    for r in edges:
        a,b=r["nodo_a"],r["nodo_b"]
        if a not in w or b not in w or a==b:raise ValueError("Enlace a testigo inexistente")
        if r["zona_homogenea_verificada"]!="false":raise ValueError("Enlace falsamente validado")
        independent_grid=(r["centros_de_ambos_modelos_diferentes"]=="true"
            and r["igual_celda_era5"]=="no" and r["igual_celda_era5land"]=="no")
        n_shared+=int(not independent_grid)
        if not independent_grid:continue
        if w[a]["estrato"]!=w[b]["estrato"]:
            continue # No cruzar piso físico aunque haya parecido climático
        if not (float(r["distancia_geografica_km"])<=20.0001 and
                float(r["desnivel_dem_m"])<=300.001 and
                float(r["distancia_climatica_estandarizada"])<=0.60001 and
                abs(float(r["diferencia_tmedia_anual_c"]))<=1.50001 and
                abs(float(r["diferencia_precipitacion_anual_mm"]))<=150.001):
            raise ValueError("Enlace fuera del criterio preregistrado 8P")
        accepted.append((a,b))
        union(a,b)
    comps=defaultdict(list)
    for code in w:comps[find(code)].append(code)
    grp={}
    families=[]
    for members in sorted((sorted(m) for m in comps.values() if len(m)>1),key=lambda a:a[0]):
        name=f"C{len(families)+1:02d}"
        for code in members:grp[code]=name
        family_edges=[(a,b) for a,b in accepted if a in members and b in members]
        families.append({"id":name,"ids_testigos":members,"estrato":w[members[0]]["estrato"],
                         "n_testigos":len(members),"enlaces_celdas_ambos_modelos_distintas":len(family_edges),
                         "contigüidad_cartográfica_validada":False,"homogeneidad_instrumental_validada":False})
    return grp,families,accepted,n_shared

def polygon_parts(poly):
    if poly.is_empty:return []
    if poly.geom_type=="Polygon":return [poly]
    if poly.geom_type=="MultiPolygon":return list(poly.geoms)
    if hasattr(poly,"geoms"):
        return [p for g in poly.geoms for p in polygon_parts(g)]
    return []

def build():
    d,w,edges,border=read()
    group,climate_families,links,shared=families(w,edges)
    ordered=list(d.values()) # orden estable CSV
    points=MultiPoint([p["p"] for p in ordered])
    tiles=voronoi_polygons(points,extend_to=border.envelope,ordered=True)
    if len(tiles.geoms)!=len(ordered):
        raise ValueError("Voronoi no preservó orden/cantidad de 420 centros")
    records=[]
    by_group=defaultdict(list)
    for pt,tile in zip(ordered,tiles.geoms):
        near=sorted(((pt["p"].distance(v["p"]),code) for code,v in w.items()
                     if v["estrato"]==pt["estrato"] and
                     abs(v["alt"]-pt["alt"])<=DZ))
        distance,closest=(near[0] if near else (float("inf"),None))
        if distance>DIST_W or pt["alt"]<=5:
            closest=None;distance=float("inf")
        fam=group.get(closest) if closest else None
        # Las familias con vínculos independientes son hipótesis, no polígonos climáticos certificados.
        level=("nucleo_multicelda_hipotesis" if fam else
               "testigo_proximo_sin_nucleo" if closest else "solo_muestreo_altitudinal")
        key=(pt["estrato"], fam if fam else "sin_nucleo")
        # Voronoi espacial limitado al polígono regional y un buffer de influencia muestreada.
        geom=tile.intersection(border).intersection(pt["p"].buffer(MAX_R,resolution=10))
        if geom.is_empty or geom.area<=1:raise ValueError("Sector DEM sin superficie")
        by_group[key].append((pt["id"],geom,closest))
        records.append({"id":pt["id"],"latitud":pt["lat"],"longitud":pt["lon"],
          "altitud_dem_m":pt["alt"],"estrato_fisico_preliminar":pt["estrato"],
          "testigo_climatico_asociado":closest or "",
          "distancia_testigo_km":round(distance/1000,3) if closest else "",
          "familia_multicelda":fam or "","nivel_soporte":level,
          "homogeneidad_validada":"false"})
    feats=[]; ledger=[];totalarea=0.0
    for (stratum,fam),segments in sorted(by_group.items()):
        union=unary_union([poly for _,poly,_ in segments])
        for part in sorted(polygon_parts(union),key=lambda p:(round(p.centroid.x,1),round(p.centroid.y,1))):
            # Evitar informar geometrías espurias por diferencias de precisión submétricas
            if part.area<1:continue
            included=[(code,poly,closest) for code,poly,closest in segments
                 if part.intersection(poly).area>1]
            if not included:raise ValueError("Polígono sin respaldo de nodo")
            pids=sorted(code for code,_,_ in included)
            member_w=sorted({closest for _,_,closest in included if closest})
            supported=fam!="sin_nucleo" and len(set(pids)&set(group))>=2
            # Núcleos con un único testigo en pieza no implican continuidad entre testigos.
            state=("hipotesis_nucleo_conectado" if supported else
                   "influencia_altitudinal_exploratoria")
            g=transform(UNPROJ,part)
            if not g.is_valid:
                # Algunos anillos casi tangentes se vuelven autointersectantes por la
                # inversión UTM->WGS84. Reparar solo el aspecto geométrico de dibujo.
                g=unary_union(polygon_parts(make_valid(g)))
            if g.is_empty or not g.is_valid or g.area<=0:
                raise ValueError("Salida geométrica no reparable")
            z=[d[code]["alt"] for code in pids]
            name=f"S{len(feats)+1:03d}"
            prop={
              "id_sector":name,"estrato":stratum,
              "familia_similitud":fam if fam!="sin_nucleo" else None,
              "estado_evidencia":state,
              "n_nodos_dem":len(pids),"n_testigos_perfil_30anios":len(member_w),
              "alt_min_nodos_m":min(z),"alt_max_nodos_m":max(z),
              "nucleos_celdas_distintas_no_demuestran_independencia":True,
              "limite_oficial":False,"zona_homogenea_validada":False,
              "sector_agricola_certificado":False,"pronostico_zonal_validado":False,
              "area_dibujo_km2":round(part.area/1e6,3),
              "nodos_origen":pids,"testigos_asociados":member_w}
            feats.append({"type":"Feature","properties":prop,"geometry":mapping(g)})
            totalarea+=part.area
            ledger.append(prop)
    cover=unary_union([shape(f["geometry"]) for f in feats])
    # Verificación visual, en grados, de que ninguna pieza queda fuera de Lambayeque.
    region_wgs=transform(UNPROJ,border)
    if cover.difference(region_wgs.buffer(0.00002)).area>1e-8:
        raise ValueError("La capa sale fuera del límite departamental simplificado")
    assert len(records)==len(ordered) and len(feats)>7
    source={p:source_sha(q) for p,q in
        [("muestra_dem_420",DEM),("perfiles_climaticos_81",WIT),
         ("pares_similares_8p",SIM),("limite_departamental_referencial",BOUND)]}
    status={"fase":"9K","metodo":"Voronoi de 420 nodos en UTM 17S, recortado al polígono secundario y a buffers de 5,5 km; disolución por franja y familia climática; no es extensión exacta de relieve real.",
      "periodo_climatico_perfiles":"1996-2025","referencia_comparable_OMM":"1991-2020",
      "n_nodos_dem":len(ordered),"n_testigos_con_360_meses":len(w),
      "n_pares_8p_similares":len(edges),"n_enlaces_con_celdas_reanalisis_compartidas":shared,
      "n_enlaces_distintos_y_dentro_del_mismo_piso":len(links),
      "n_familias_multicelda_exploratorias":len(climate_families),
      "familias":climate_families,"n_poligonos_graficos_exploratorios":len(feats),
      "n_sectores_nucleo_conectado":sum(f["properties"]["estado_evidencia"]=="hipotesis_nucleo_conectado" for f in feats),
      "n_nodos_asociados_a_testigos":sum(bool(r["testigo_climatico_asociado"]) for r in records),
      "n_nodos_no_asociados":sum(not r["testigo_climatico_asociado"] for r in records),
      "nodos_por_piso":dict(sorted(Counter(p["estrato_fisico_preliminar"] for p in records).items())),
      "area_km2_solo_influencia_grafica":round(totalarea/1e6,2),
      "cobertura_territorial_oficial_estimada":False,
      "n_zonas_homogeneas_certificadas":0,"n_sectores_agricolas_certificados":0,
      "validacion_espacial_de_pronosticos":False,
      "geometria_referencial_no_oficial":True,
      "dem_90m_puntos_no_pendiente_ni_cuenca_verificadas":True,
      "altitud_solo_nodo_no_altitud_continua_de_todo_poligono":True,
      "independencia_estaciones_no_certificada":True,
      "prediccion_elnino_costero_zonal_validada":False,
      "fuentes_sha256":source,
      "limitaciones":["Voronoi es superficie gráfica asociada al nodo, no unidad natural de clima, vertiente, cuenca ni catastro.",
       "Buffer máximo 5,5 km evita extrapolar celdas lejanas; áreas sumadas NO son porcentajes de superficie por piso altitudinal.",
       "El apoyo climático de un testigo se limita a <=12 km, desnivel <=180 m y MISMO estrato físico.",
       "Cruzar un umbral físico de altitud impide disolver una pieza incluso si el reanálisis es parecido.",
       "Un píxel compartido de ERA5/ERA5-Land no acredita corroboración independiente.",
       "Las piezas con soporte de un único testigo no prueban continuidad climatológica.",
       "Faltan límite IGN/INEI vigente, DEM ráster continuo, vertientes/cuencas y estaciones SENAMHI con metadatos confiables.",
       "NO hay downscaling validado de NOAA NMME a estas piezas; 1° NMME no resuelve pisos de altitud de Lambayeque."]}
    geo={"type":"FeatureCollection","name":"OAF 9K sectores preliminares de influencia altitudinal",
         "metadata":{"fase":"9K","crs":"EPSG:4326","limite_regional_oficial":False,
           "son_zonas_homogeneas_validadas":False,"max_radio_influencia_km":5.5},
         "features":feats}
    return geo,status,records

def save():
    geo,status,records=build()
    DEST.mkdir(parents=True,exist_ok=True)
    GEO.write_text(json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    OUT.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with TABLE.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLS);w.writeheader();w.writerows(records)
    return status

def check():
    geo,status,records=build()
    if json.loads(GEO.read_text("utf8"))!=geo:raise ValueError("GeoJSON 9K no se reproduce")
    if json.loads(OUT.read_text("utf8"))!=status:raise ValueError("Metadatos 9K no se reproducen")
    if rows(TABLE)!=[{k:str(v) for k,v in r.items()} for r in records]:
        raise ValueError("Inventario de asignaciones distinto de DEM y testigos")
    return status

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    st=check() if args.check else save()
    print("9K:",st["n_nodos_dem"],"nodos DEM;",st["n_testigos_con_360_meses"],
          "testigos; sectores",st["n_poligonos_graficos_exploratorios"],
          "familias",st["n_familias_multicelda_exploratorias"])
