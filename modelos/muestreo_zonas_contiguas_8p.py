#!/usr/bin/env python3
"""8P: diseño de densificación climática y aristas espaciales de muestreo.

NO clasifica 420 puntos por clima sin observaciones ni identifica parcelas.
Se priorizan estratos infrarepresentados, altitud y separación espacial;
las aristas son únicamente proximidad geográfica (no vecindad ecológica).
"""
from __future__ import annotations
import csv,io,json,math,hashlib,argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NODES="datos/muestreo_8o/nodos_dem_8o.csv"
PILOTS="datos/muestreo_8o/testigos_climaticos_8o.csv"
OUT="datos/zonas_contiguas_8p"
# Nuevas muestras seleccionadas sin volver a descargar los 19 testigos 8O.
QUOTAS={"llanura_costa":10,"valle_bajo":10,"piedemonte":12,
        "montana_baja":10,"montana_media":8,"montana_alta":12}
COLUMNS=("id","latitud","longitud","altitud_dem_m","estrato_fisico_preliminar",
         "prioridad_muestreo","tipo_muestreo","origen",
         "apto_para_zona_operativa")
EDGE=("origen_id","destino_id","distancia_km","desnivel_m",
      "criterio_cercania","homogeneidad_climatica_comprobada")

def haversine(a,b,c,d):
    p=math.pi/180
    z=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(z)))

def read(root,path):
    file=root/path
    with file.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows:return []
    for x in rows:
        for k in ("latitud","longitud","altitud_dem_m"):
            x[k]=float(x[k])
        if x.get("homogeneidad_validada")!="false":
            raise ValueError("Algunos nodos ya se publicaron falsamente como clima validado")
    return rows

def input_data(root):
    rows=read(root,NODES); old=read(root,PILOTS)
    if len(rows)!=420 or len(old)!=19 or len({r["id"] for r in rows})!=420:
        raise ValueError("8P requiere 420 centros DEM y 19 testigos originales verificables")
    byid={x["id"]:x for x in rows}
    if any(p["id"] not in byid for p in old):
        raise ValueError("Testigo 8O sin correspondencia con DEM 8P")
    if any(p["altitud_dem_m"]!=byid[p["id"]]["altitud_dem_m"] for p in old):
        raise ValueError("Altitud previa inconsistente con malla DEM")
    return rows,old

def select(root):
    nodes,old=input_data(root)
    old_ids={x["id"] for x in old}
    new=[]
    byname={r["id"]:r for r in nodes}
    for name,quota in QUOTAS.items():
        options=[p for p in nodes if p["estrato_fisico_preliminar"]==name
                  and p["id"] not in old_ids and p["altitud_dem_m"]>5]
        if len(options)<quota:
            raise ValueError("No hay suficientes nodos terrestres candidatos: "+name)
        # Farthest-first starting with original sample within stratum, then
        # spread new nodes in space and elevation. Ensures geographic coverage,
        # not a climatic homogeneity assertion.
        chosen=[p for p in old if p["estrato_fisico_preliminar"]==name]
        local=[]
        while len(local)<quota:
            avail=[x for x in options if x["id"] not in {p["id"] for p in local}]
            def score(p):
                return min(haversine(p["latitud"],p["longitud"],
                                     q["latitud"],q["longitud"]) for q in chosen) if chosen else 0
            pick=max(avail,key=lambda p:(score(p),-abs(p["altitud_dem_m"]-600),
                                             -p["latitud"],-p["longitud"],p["id"]))
            chosen.append(pick);local.append(pick)
        new.extend(local)
    if len(new)!=sum(QUOTAS.values()) or len(set(p["id"] for p in new))!=len(new):
        raise ValueError("Selección espacial incompleta o duplicada")
    output=[{"id":p["id"],"latitud":p["latitud"],
      "longitud":p["longitud"],"altitud_dem_m":p["altitud_dem_m"],
      "estrato_fisico_preliminar":p["estrato_fisico_preliminar"],
      "prioridad_muestreo":"alta_montana_o_transicion" if p["altitud_dem_m"]>=300 else "cobertura_baja",
      "tipo_muestreo":p["tipo_muestreo"],
      "origen":"8P_nuevos_no_instrumentales","apto_para_zona_operativa":"false"}
      for p in new]
    # undirected edges defined as physical-neighborhood candidates.
    graph=[]
    for i,p in enumerate(nodes):
        for q in nodes[i+1:]:
            distance=haversine(p["latitud"],p["longitud"],q["latitud"],q["longitud"])
            if distance<=8.5:
                graph.append({"origen_id":p["id"],"destino_id":q["id"],
                     "distancia_km":round(distance,4),
                     "desnivel_m":abs(p["altitud_dem_m"]-q["altitud_dem_m"]),
                     "criterio_cercania":"distancia_le_8_5km_no_topologia_oficial",
                     "homogeneidad_climatica_comprobada":"false"})
    return output,graph,nodes,old

def to_csv(rows,cols):
    f=io.StringIO(newline="");w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
    w.writeheader()
    for row in rows:w.writerow({key:row.get(key,"") for key in cols})
    return f.getvalue()

def publish(root,check=False):
    points,edges,nodes,old=select(root)
    hist={k:sum(p["estrato_fisico_preliminar"]==k for p in points) for k in QUOTAS}
    stat={
      "fase":"8P","estado":"muestreo_adicional_definido_esperando_perfiles_climaticos",
      "periodo_climatologia":"1996–2025",
      "n_nodos_dem_region":len(nodes),
      "n_testigos_climaticos_8o_existentes":len(old),
      "n_testigos_climaticos_nuevos_8p":len(points),
      "n_testigos_totales_propuestos":len(points)+len(old),
      "n_candidatos_con_cota_dem_negativa_admitidos":0,
      "n_testigos_nuevos_por_estrato":hist,
      "aristas_cercania_fisica":len(edges),
      "distancia_maxima_para_cercania_km":8.5,
      "arista_significa_solo_proximidad_no_afinidad_climatica":True,
      "zona_climatica_homogenea_demostrada":False,
      "n_poligonos_agricolas_certificados":0,
      "cuencas_y_costa_verificadas_con_cartografia_oficial":False,
      "predicciones_zonales_verificadas":False,
      "validacion_SENAMHI_instrumental":False,
      "procedimiento":"Maximin de separación geográfica, con estratos DEM de diseño; alta prioridad 300 m+",
      "advertencias":[
       "Nodos con DEM <=5 m no se seleccionan para nuevos testigos: no implica que sean mar, solo cribado preventivo sin máscara agua/tierra.",
       "La franja 1600–2499 m tiene pocos puntos; 8 de 8 elegibles se incorporan sin pretender representar cada subcuenca.",
       "La densificación es muestreo de localizaciones, no 62 series instrumentales ni delimitación climática válida.",
       "La separación espacial <=8,5 km es solo un grafo de posibles vecinos; no verifica un camino libre de barreras o cuencas.",
       "Los centros de celdas ERA5/ERA5-Land pueden ser compartidos entre ubicaciones distintas y los datos no son independientes."
      ],
      "trazabilidad":{
        "csv_dem_sha256":hashlib.sha256((root/NODES).read_bytes()).hexdigest(),
        "csv_testigos_8o_sha256":hashlib.sha256((root/PILOTS).read_bytes()).hexdigest()
      }
    }
    base=root/OUT
    outputs={
       base/"estado_muestreo_8p.json":json.dumps(stat,ensure_ascii=False,indent=2)+"\n",
       base/"nuevos_testigos_8p.csv":to_csv(points,COLUMNS),
       base/"aristas_cercania_8p.csv":to_csv(edges,EDGE)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,data in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=data:
                raise ValueError("Muestreo 8P desactualizado o alterado")
        elif not path.exists() or path.read_text(encoding="utf-8")!=data:
            path.write_text(data,encoding="utf-8")
    print(json.dumps({"fase":"8P","nuevos_testigos":len(points),"aristas":len(edges),
                      "modo_check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    publish(a.root,a.check)
