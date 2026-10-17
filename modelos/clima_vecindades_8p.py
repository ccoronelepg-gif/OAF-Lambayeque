#!/usr/bin/env python3
"""8P: nuevos perfiles 1996–2025, comparación de vecinos realmente climatológicos.

Se parte de 19 testigos climatológicos ya archivados en 8O y se añaden 62
en cuatro lotes <=16, dos modelos × tres décadas por lote = 24 fuentes.
Los resultados parciales de cada lote necesitan las seis fuentes completas.
No se producen polígonos zonales validados ni se asume independencia de ERA5.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import perfiles_climaticos_8o as ref

ROOT=Path(__file__).resolve().parents[1]
SAMPLE="datos/zonas_contiguas_8p/nuevos_testigos_8p.csv"
SAMPLE_STATE="datos/zonas_contiguas_8p/estado_muestreo_8p.json"
OLD_NORMALS="datos/perfiles_climaticos_8o/normales_mensuales_testigos_8o.csv"
OLD_NODES="datos/perfiles_climaticos_8o/grupos_testigos_8o.csv"
OLD_STATE="datos/perfiles_climaticos_8o/estado_climatico_8o.json"
RAW="datos/clima_contiguo_8p/fuentes"
OUT="datos/clima_contiguo_8p"
BLOCKS=ref.BLOCKS
FEATS=ref.FEATS
METHODS=ref.VARS
GROUP_SIZE=16
FIELDS=("id","latitud","longitud","altitud_dem_m","estrato_fisico_preliminar",
        "fase_fuente","perfil_completo_1996_2025","apto_para_zona_operativa")
EDGE_FIELDS=("nodo_a","nodo_b","distancia_geografica_km","desnivel_dem_m",
  "distancia_climatica_estandarizada","diferencia_tmedia_anual_c",
  "diferencia_precipitacion_anual_mm","diferencia_humedad_pct",
  "igual_celda_temperatura_referencia","criterio_filtro_vecindad",
  "zona_homogenea_verificada")
NORMAL_FIELDS=("id","mes_calendario")+FEATS

def sha(data):return hashlib.sha256(data).hexdigest()
def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def nodes(root):
    stat=json.loads((root/SAMPLE_STATE).read_text(encoding="utf-8"))
    if stat.get("fase")!="8P" or stat.get("n_testigos_climaticos_nuevos_8p")!=62:
        raise ValueError("Diseño 8P no verificado")
    p=read_csv(root/SAMPLE)
    if len(p)!=62 or len({r["id"] for r in p})!=62:
        raise ValueError("Faltan nuevos puntos testigo")
    for item in p:
        if item.get("apto_para_zona_operativa")!="false" or float(item["altitud_dem_m"])<=5:
            raise ValueError("Punto DEM comprometido o franja costera en muestra")
        for key in ("latitud","longitud","altitud_dem_m"):
            item[key]=float(item[key])
    return p

def old(root):
    state=json.loads((root/OLD_STATE).read_text(encoding="utf-8"))
    if state.get("fase")!="8O" or state.get("n_fuentes_archivadas")!=6 or state.get("n_testigos_con_perfil_30anios")!=19:
        raise ValueError("8O no tiene 19 perfiles completos acreditados")
    positions=read_csv(root/OLD_NODES)
    normals=read_csv(root/OLD_NORMALS)
    if len(positions)!=19 or len(normals)!=19*12:
        raise ValueError("Referencia climatológica 8O incompleta")
    bysite={}
    for p in positions:
        for k in ("latitud","longitud","altitud_dem_m"):p[k]=float(p[k])
        bysite[p["id"]]=p
    n={}
    for p in normals:
        key=(p["id"],int(p["mes_calendario"]))
        if key in n:raise ValueError("Normal 8O repetida")
        n[key]={f:float(p[f]) for f in FEATS}
        if not all(math.isfinite(v) for v in n[key].values()):
            raise ValueError("Normal 8O no finita")
    return bysite,n

def chunked(rows):
    return [rows[i:i+GROUP_SIZE] for i in range(0,len(rows),GROUP_SIZE)]

def paths(root,group,model,start,end):
    stem=f"g{group:02d}_{model}_{start}_{end}"
    base=root/RAW
    return base/(stem+".json.gz"),base/(stem+".meta.json")

def inspect(root,group,model,start,end,points):
    p,m=paths(root,group,model,start,end)
    if not p.exists() and not m.exists():return None
    if not p.exists() or not m.exists():raise ValueError("Archivo climático parcial")
    raw=gzip.decompress(p.read_bytes())
    if len(raw)>20_000_000:raise ValueError("Bloque demasiado grande")
    meta=json.loads(m.read_text(encoding="utf-8"))
    expected=ref.query(model,start,end,points)
    if (meta.get("fase")!="8P" or meta.get("modelo")!=model or
        meta.get("periodo")!=[start,end] or meta.get("grupo")!=group or
        meta.get("ids")!=[z["id"] for z in points] or
        meta.get("url")!=expected or meta.get("sha256_original")!=sha(raw)):
        raise ValueError("Metadatos SHA, periodo o identidad de fuente 8P inválidos")
    return ref.validate_blob(raw,model,start,end,points)

def fetch(root,max_new=2):
    pts=nodes(root)
    (root/RAW).mkdir(parents=True,exist_ok=True)
    counter=0
    for group,part in enumerate(chunked(pts),1):
        for model in METHODS:
            for start,end in BLOCKS:
                if inspect(root,group,model,start,end,part) is not None:continue
                if counter>=max_new:
                    print("Cuota conservadora de consultas alcanzada.");return
                url=ref.query(model,start,end,part)
                try:
                    with urlopen(Request(url,headers={"User-Agent":"OAF-8P-zones-climate-profiles/1.0"}),timeout=135) as response:
                        if response.status!=200:raise ValueError("HTTP inesperado")
                        raw=response.read(20_000_001)
                    if len(raw)>20_000_000:raise ValueError("Respuesta supera 20 MB")
                    ref.validate_blob(raw,model,start,end,part)
                except HTTPError as exc:
                    if exc.code==429:
                        print("HTTP 429 del proveedor: respetar espera sin imputar datos.",flush=True)
                        return
                    raise
                except (OSError,ValueError,TimeoutError,json.JSONDecodeError) as exc:
                    print("Bloque proveedor no verificable:",model,start,end,str(exc),flush=True)
                    return
                f,m=paths(root,group,model,start,end)
                meta={"fase":"8P","grupo":group,"modelo":model,
                      "periodo":[start,end],"ids":[p["id"] for p in part],
                      "url":url,"sha256_original":sha(raw),
                      "consultado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "dato_reanalisis_no_sensor":True}
                f.write_bytes(gzip.compress(raw,mtime=0))
                m.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                counter+=1
                print("Histórico 8P recuperado:",group,model,start,end,flush=True)
                if counter<max_new:time.sleep(2)

def candidate(a,b,norma,scaling,limit=20):
    from math import sin,cos,asin,sqrt,pi
    x=sin((b["latitud"]-a["latitud"])*pi/360)**2+cos(a["latitud"]*pi/180)*cos(b["latitud"]*pi/180)*sin((b["longitud"]-a["longitud"])*pi/360)**2
    distance=12742.0176*asin(min(1,sqrt(x)))
    if distance>limit or distance<0.01:return None
    ae={feat:[norma[(a["id"],m)][feat] for m in range(1,13)] for feat in FEATS}
    be={feat:[norma[(b["id"],m)][feat] for m in range(1,13)] for feat in FEATS}
    deltas=[(ae[f][m]-be[f][m])/scaling[f][1] for f in FEATS for m in range(12)]
    clim=math.sqrt(sum(x*x for x in deltas)/len(deltas))
    t=statistics.mean(ae["tmedia_c"])-statistics.mean(be["tmedia_c"])
    rain=sum(ae["precipitacion_mm"])-sum(be["precipitacion_mm"])
    rh=statistics.mean(ae["humedad_relativa_pct"])-statistics.mean(be["humedad_relativa_pct"])
    return {"nodo_a":a["id"],"nodo_b":b["id"],
      "distancia_geografica_km":round(distance,4),
      "desnivel_dem_m":round(abs(a["altitud_dem_m"]-b["altitud_dem_m"]),2),
      "distancia_climatica_estandarizada":round(clim,5),
      "diferencia_tmedia_anual_c":round(t,4),
      "diferencia_precipitacion_anual_mm":round(rain,3),
      "diferencia_humedad_pct":round(rh,3),
      "igual_celda_temperatura_referencia":"desconocido",
      "criterio_filtro_vecindad":"distancia<=20km;perfil_30anios;no_afirma_contiguidad_ecologica",
      "zona_homogenea_verificada":"false"}

def textcsv(rows,fields):
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n")
    w.writeheader()
    for r in rows:w.writerow({k:r.get(k,"") for k in fields})
    return s.getvalue()

def evaluate(root):
    pts=nodes(root);oldsites,oldnormals=old(root)
    groups=chunked(pts)
    sources={};full=[]
    for i,part in enumerate(groups,1):
        for model in METHODS:
            for start,end in BLOCKS:
                obj=inspect(root,i,model,start,end,part)
                if obj is not None:sources[(i,model,start,end)]=obj
        if all((i,model,start,end) in sources for model in METHODS for start,end in BLOCKS):
            full.append(i)
    profiles=dict(oldsites)
    normals=dict(oldnormals)
    for i in full:
        part=groups[i-1]
        values={}
        for model in METHODS:
            for start,end in BLOCKS:
                rows=ref.monthly(sources[(i,model,start,end)],model,part)
                for key,d in rows.items():values.setdefault(key,{}).update(d)
        if len(values)!=len(part)*360:raise ValueError("Lote 8P no reúne 360 meses por punto")
        for p in part:
            profiles[p["id"]]=p
            for m in range(1,13):
                cases=[v for (pid,mon),v in values.items() if pid==p["id"] and int(mon[-2:])==m]
                if len(cases)!=30:raise ValueError("Climatología mensual 8P con huecos")
                normals[(p["id"],m)]={
                  "tmedia_c":statistics.mean(d["temperature_2m_mean"] for d in cases),
                  "amplitud_termica_c":statistics.mean(d["temperature_2m_max"]-d["temperature_2m_min"] for d in cases),
                  "precipitacion_mm":statistics.mean(d["precipitation_sum"] for d in cases),
                  "humedad_relativa_pct":statistics.mean(d["relative_humidity_2m_mean"] for d in cases),
                  "radiacion_mj_m2":statistics.mean(d["shortwave_radiation_sum"] for d in cases)
                }
    means={}
    # Fixed reference scaling 8O to avoid artificial drifts as new 8P chunks arrive.
    for feat in FEATS:
        v=[oldnormals[(pid,m)][feat] for pid in oldsites for m in range(1,13)]
        means[feat]=(statistics.mean(v),max(1e-6,statistics.pstdev(v)))
    legitimate=[p for p in profiles.values() if p["altitud_dem_m"]>5]
    edges=[]
    for i,p in enumerate(legitimate):
        for q in legitimate[i+1:]:
            e=candidate(p,q,normals,means)
            if e:edges.append(e)
    # Not zones. Physical controls only for ranking LOCAL comparison candidates.
    eligible=[e for e in edges if e["distancia_climatica_estandarizada"]<=0.6 and
              e["desnivel_dem_m"]<=300 and
              abs(e["diferencia_tmedia_anual_c"])<=1.5 and
              abs(e["diferencia_precipitacion_anual_mm"])<=150]
    eligible.sort(key=lambda e:(e["distancia_climatica_estandarizada"],e["distancia_geografica_km"],e["nodo_a"],e["nodo_b"]))
    summary={
      "fase":"8P","estado":"expansion_climatica_completa" if len(full)==len(groups) else
                       "ampliacion_climatica_en_ejecucion",
      "periodo":"1996–2025","nuevos_testigos_planeados":len(pts),
      "testigos_climaticos_reutilizados_8o":len(oldsites),
      "testigos_nuevos_con_30_anios":sum(len(groups[i-1]) for i in full),
      "testigos_total_con_30_anios":len(profiles),
      "lotes_climaticos_esperados":len(groups)*6,
      "lotes_climaticos_verificados":len(sources),
      "grupos_de_descarga_completos":full,
      "pares_vecinos_hasta_20km_comparados":len(edges),
      "pares_que_superan_filtro_exploratorio":len(eligible),
      "umbrales_filtro_exploratorio_no_normativos":{"distancia_km":20,
         "distancia_climatica_estandarizada":0.6,"desnivel_m":300,
         "diferencia_tmedia_anual_abs_c":1.5,
         "diferencia_precipitacion_anual_abs_mm":150},
      "zonas_homogeneas_geograficas_certificadas":0,
      "n_poligonos_agricolas_validados":0,
      "validacion_instrumental":False,"precision_predictiva_zonal_demostrada":False,
      "mascara_tierra_mar_ine_i_ign_verificada":False,
      "reanalisis_ERA5_y_ERA5Land_no_estaciones":True,
      "testigos_no_independientes_entre_pixeles_demostrado":False,
      "nota":"Los pares comparan perfiles 30 años y proximidad; no establecen polígonos contiguos, sensores independientes o zonas productivas.",
      "trazabilidad":{"sha256_muestreo":sha((root/SAMPLE).read_bytes()),
       "sha256_8o_normales":sha((root/OLD_NORMALS).read_bytes())}
    }
    profrows=[{"id":p["id"],"latitud":p["latitud"],"longitud":p["longitud"],
               "altitud_dem_m":p["altitud_dem_m"],
               "estrato_fisico_preliminar":p["estrato_fisico_preliminar"],
               "fase_fuente":"8O" if p["id"] in oldsites else "8P",
               "perfil_completo_1996_2025":"true","apto_para_zona_operativa":"false"}
            for p in profiles.values()]
    return summary,profrows,edges,eligible

def publish(root,check=False):
    state,pts,edges,eligible=evaluate(root)
    base=root/OUT
    outputs={
      base/"estado_clima_8p.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
      base/"testigos_perfil_completo_8p.csv":textcsv(pts,FIELDS),
      base/"pares_climaticos_cercanos_8p.csv":textcsv(edges,EDGE_FIELDS),
      base/"pares_similares_exploratorios_8p.csv":textcsv(eligible,EDGE_FIELDS)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for p,s in outputs.items():
        if check:
            if not p.exists() or p.read_text(encoding="utf-8")!=s:
                raise ValueError("Salida 8P diferente de sus fuentes verificadas")
        elif not p.exists() or p.read_text(encoding="utf-8")!=s:
            p.write_text(s,encoding="utf-8")
    print(json.dumps({"fase":"8P","perfiles":state["testigos_total_con_30_anios"],
     "fuentes":state["lotes_climaticos_verificados"],"cercanos":len(edges),
     "similares_piloto":len(eligible),"check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--max-new",type=int,default=2)
    p.add_argument("--check",action="store_true")
    o=p.parse_args()
    if o.fetch:fetch(o.root,o.max_new)
    publish(o.root,o.check)
