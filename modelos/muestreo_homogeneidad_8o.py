#!/usr/bin/env python3
"""8O: malla regional adaptativa, DEM auditado y selección de testigos climáticos.

0.0625 grados regional, refinamiento 0.03125 grados alrededor de
laderas/puntos con fuerte gradiente DEM en fase 8N.
No son píxeles oficiales, parcelas, porcentajes de área ni zonas validadas.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="datos/zonificacion_8n/nodos_altitudinales_8n.csv"
BOUNDARY="datos/zonificacion_8n/limite_lambayeque_referencial.geojson"
DATA="datos/muestreo_8o"
ELEV_DIR="datos/muestreo_8o/fuentes_dem"
DEM_URL="https://api.open-meteo.com/v1/elevation"
COLUMNS=("id","latitud","longitud","tipo_muestreo","prioridad_refinamiento","altitud_dem_m",
         "estrato_fisico_preliminar","candidato_testigo_climatico","homogeneidad_validada")
CLASSES=((0,100,"llanura_costa"),(100,300,"valle_bajo"),(300,800,"piedemonte"),
         (800,1600,"montana_baja"),(1600,2500,"montana_media"),
         (2500,10000,"montana_alta"))
# Solo número de testigos pilotos. Clasificación final requerirá mayor cobertura.
QUOTAS={"llanura_costa":3,"valle_bajo":3,"piedemonte":3,
        "montana_baja":3,"montana_media":3,"montana_alta":3,
        "cota_negativa_revisar":1}
STEP=.0625
HALF=.03125
CHUNK=50

def filehash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sha(data):return hashlib.sha256(data).hexdigest()
def load8n(root):
    with (root/ORIGIN).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        rows=list(reader)
    if len(rows)!=69 or any(r["clima_homogeneo_validado"]!="false" for r in rows):
        raise ValueError("Inventario de 8N alterado o climáticamente sobreinterpretado")
    return [{"lat":float(r["latitud"]),"lon":float(r["longitud"]),
             "z":float(r["altitud_dem_m"])} for r in rows]

def geometry(root):
    obj=json.loads((root/BOUNDARY).read_text(encoding="utf-8"))
    f=obj["features"][0]
    if f["properties"]["codigo_ubigeo"]!="14" or f["geometry"]["type"]!="Polygon":
        raise ValueError("Polígono referencial Lambayeque no reproducible")
    ring=f["geometry"]["coordinates"][0]
    if len(ring)<10 or ring[0]!=ring[-1]:raise ValueError("Límite abierto")
    return ring

def inside(x,y,ring):
    flag=False
    for (a,b),(c,d) in zip(ring,ring[1:]):
        if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:
            flag=not flag
    return flag

def km(a,b,c,d):
    p=math.pi/180
    q=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(q)))

def definition(root):
    ring=geometry(root)
    old=load8n(root)
    # Punto con relieve alto, o cambio >350 m con un testigo vecino a <21 km.
    anchors=[r for r in old if r["z"]>=300 or any(
        0<km(r["lat"],r["lon"],a["lat"],a["lon"])<=21 and abs(r["z"]-a["z"])>350
        for a in old)]
    points={}
    for i in range(64):
        lat=round(-8+i*STEP,5)
        for j in range(64):
            lon=round(-81+j*STEP,5)
            if inside(lon,lat,ring):
                points[(lat,lon)]=("general_00625","regular")
    for r in anchors:
        for dlat in (-HALF,HALF):
            for dlon in (-HALF,HALF):
                lat=round(r["lat"]+dlat,5);lon=round(r["lon"]+dlon,5)
                if inside(lon,lat,ring):
                    points[(lat,lon)]=("refuerzo_003125","altitud_o_gradiente_8n")
    rows=[]
    for (lat,lon),(kind,why) in sorted(points.items()):
        rows.append({"id":f"M{len(rows)+1:04d}","latitud":lat,"longitud":lon,
                     "tipo_muestreo":kind,"prioridad_refinamiento":why})
    if len(rows)<350 or len(rows)>800 or not anchors:
        raise ValueError("Diseño adaptativo se apartó del control geográfico esperado")
    return rows,anchors

def batches(root):
    nodes,_=definition(root)
    return [nodes[i:i+CHUNK] for i in range(0,len(nodes),CHUNK)]

def url(group):
    return DEM_URL+"?"+urlencode({
      "latitude":",".join(str(n["latitud"]) for n in group),
      "longitude":",".join(str(n["longitud"]) for n in group)})

def paths(root,index):
    d=root/ELEV_DIR
    return d/f"bloque_{index:02d}.json.gz",d/f"bloque_{index:02d}.meta.json"

def decode(raw,group):
    obj=json.loads(raw)
    heights=obj.get("elevation") if isinstance(obj,dict) else None
    if not isinstance(heights,list) or len(heights)!=len(group):
        raise ValueError("Respuesta de elevaciones DEM incompleta")
    if any(type(v) not in (float,int) or not math.isfinite(v) or v<-100 or v>6500 for v in heights):
        raise ValueError("Altitud DEM inválida/no numérica")
    return [float(v) for v in heights]

def read(root,index,group):
    p,m=paths(root,index)
    if not p.exists() and not m.exists():return None
    if not p.exists() or not m.exists():raise ValueError("Fuente DEM parcialmente archivada")
    original=gzip.decompress(p.read_bytes())
    metadata=json.loads(m.read_text(encoding="utf-8"))
    if(metadata.get("fase")!="8O" or metadata.get("url")!=url(group) or
       metadata.get("sha256_original")!=sha(original) or
       metadata.get("ids")!=[n["id"] for n in group] or
       metadata.get("tipo")!="Elevación DEM Open-Meteo (GLO-90); no estación"):
       raise ValueError("Fuentes DEM perdieron integridad o metadatos")
    return decode(original,group)

def acquire(root,max_new=2):
    (root/ELEV_DIR).mkdir(parents=True,exist_ok=True)
    n=0
    for index,group in enumerate(batches(root),1):
        if read(root,index,group) is not None:continue
        if n>=max_new:break
        endpoint=url(group)
        try:
            with urlopen(Request(endpoint,headers={"User-Agent":"OAF-8O-regional-DEM/1.0"}),timeout=40) as response:
                if response.status!=200:raise ValueError("Estado HTTP inesperado")
                original=response.read(150000)
            if len(original)>=150000:raise ValueError("Respuesta DEM demasiado grande")
            decode(original,group)
        except HTTPError as exc:
            if exc.code==429:raise RuntimeError("Proveedor DEM límite 429; reintentar otro día") from exc
            raise
        p,m=paths(root,index)
        meta={"fase":"8O","url":endpoint,"sha256_original":sha(original),
              "ids":[r["id"] for r in group],
              "consultado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "tipo":"Elevación DEM Open-Meteo (GLO-90); no estación"}
        p.write_bytes(gzip.compress(original,mtime=0))
        m.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        n+=1
        print("Bloque DEM 8O validado",index,flush=True)
        if n<max_new:time.sleep(1.5)
    print("Nuevos bloques:",n)

def band(z):
    if z<0:return "cota_negativa_revisar"
    for lo,hi,key in CLASSES:
        if lo<=z<hi:return key
    raise ValueError("Elevación física imposible")

def select_testigos(rows):
    """Selección espacial maximin DENTRO de estrato; fija diseño y cobertura."""
    selected=[]
    for className,desired in QUOTAS.items():
        pool=[x for x in rows if x["estrato_fisico_preliminar"]==className]
        if not pool:continue
        chosen=[]
        # First most removed from other class/testigo nodes; deterministic.
        while len(chosen)<min(desired,len(pool)):
            available=[p for p in pool if p not in chosen]
            if not chosen:
                # Prefer an interior position rather than extremal mountain isolated.
                chosen.append(sorted(available,key=lambda x:(x["latitud"],x["longitud"]))[len(available)//2])
            else:
                chosen.append(max(available,key=lambda p:(
                    min(km(p["latitud"],p["longitud"],z["latitud"],z["longitud"]) for z in chosen),
                    -p["latitud"],-p["longitud"])))
        selected+=chosen
    return selected

def textcsv(rows,fields):
    buf=io.StringIO(newline="")
    w=csv.DictWriter(buf,fieldnames=fields,lineterminator="\n")
    w.writeheader()
    for row in rows:w.writerow({k:row.get(k,"") for k in fields})
    return buf.getvalue()

def compute(root):
    plan,anchor=definition(root)
    all_groups=batches(root)
    elevation={}
    found=0
    for i,group in enumerate(all_groups,1):
        results=read(root,i,group)
        if results is None:continue
        found+=1
        elevation.update({p["id"]:z for p,z in zip(group,results)})
    points=[]
    for p in plan:
        if p["id"] not in elevation:continue
        z=elevation[p["id"]]
        points.append({**p,"altitud_dem_m":z,"estrato_fisico_preliminar":band(z),
                       "candidato_testigo_climatico":"false",
                       "homogeneidad_validada":"false"})
    chosen=select_testigos(points) if len(elevation)==len(plan) else []
    ids={p["id"] for p in chosen}
    for p in points:
        p["candidato_testigo_climatico"]="true" if p["id"] in ids else "false"
    classes={key:{"n_puntos":sum(x["estrato_fisico_preliminar"]==key for x in points),
                  "altitud_min_m":min((x["altitud_dem_m"] for x in points if x["estrato_fisico_preliminar"]==key),default=None),
                  "altitud_max_m":max((x["altitud_dem_m"] for x in points if x["estrato_fisico_preliminar"]==key),default=None)}
             for key in [r[2] for r in CLASSES]+["cota_negativa_revisar"]}
    state={"fase":"8O",
      "estado":"inventario_fisico_completo_listo_para_muesteo_climatico" if ids else
               "muestra_dem_incompleta_sin_zonas_climaticas",
      "nodos_diseno":len(plan),"nodos_dem_verificados":len(points),
      "n_referencias_8n":len(load8n(root)),
      "n_anclas_refuerzo":len(anchor),
      "n_refuerzos":sum(p["tipo_muestreo"]=="refuerzo_003125" for p in plan),
      "n_lotes_esperados":len(all_groups),"n_lotes_archivados":found,
      "paso_regional_grados":STEP,"paso_refuerzo_grados":HALF,
      "tipos_muestreo_no_son_celdas_climaticas_independientes":True,
      "area_departamental_calculada":False,
      "limite_administrativo_validado_inei_ign":False,
      "n_testigos_climaticos_seleccionados":len(chosen),
      "zonas_homogeneas_demostradas":0,"series_climaticas_multivariables_1996_2025_completas":0,
      "validacion_espacial_independiente":False,"pronosticos_zonales_certificados":False,
      "bloques_altitudinales_preliminares":classes,
      "advertencias":[
        "Malla recortada con límite departamental histórico simplificado de fuente secundaria; NO superficie cartográfica oficial.",
        "Refinar alrededor de relieve detectado en 8N no excluye picos o transiciones DEM omitidos por la malla gruesa.",
        "Elevación DEM GLO-90 no equivale a altitud instrumental ni separa efecto del downscaling de Open-Meteo.",
        "Sin perfiles mensuales multivariables 1996–2025 y pruebas espaciales no existe homogeneidad climática demostrada.",
        "La selección de testigos climáticos es piloto maximin; no representa el área real de los estratos ni justifica extrapolación zonal.",
      ],
      "trazabilidad":{"limite_sha256":filehash(root/BOUNDARY),"8n_sha256":filehash(root/ORIGIN),
          "lotes":[{"index":i,"sha256_archivo_comprimido":filehash(paths(root,i)[0])}
                    for i,g in enumerate(all_groups,1) if paths(root,i)[0].exists()]}
      }
    return state,plan,points,chosen

def publish(root,check=False):
    state,plan,points,selected=compute(root)
    base=root/DATA
    outputs={
        base/"estado_muestreo_8o.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
        base/"diseno_malla_8o.csv":textcsv(plan,("id","latitud","longitud","tipo_muestreo","prioridad_refinamiento")),
        base/"nodos_dem_8o.csv":textcsv(points,COLUMNS),
        base/"testigos_climaticos_8o.csv":textcsv(selected,COLUMNS)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,content in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("El estado muestreo 8O no corresponde a sus fuentes")
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8O","nodos":state["nodos_diseno"],
        "elevaciones":state["nodos_dem_verificados"],"testigos":len(selected),
        "check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch-dem",action="store_true")
    p.add_argument("--max-new-batches",type=int,default=2)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    if args.fetch_dem:acquire(args.root,args.max_new_batches)
    publish(args.root,args.check)
