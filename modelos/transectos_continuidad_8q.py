#!/usr/bin/env python3
"""OAF Fase 8Q: transectos reales DEM + contraste climatológico auditado.

La selección se congela ex ante en tres segmentos V1/V2, sin certificación
de polígonos. A cada 20/40/60/80 % se selecciona un nodo DEM interior
próximo al objetivo; registra distancia al objetivo, desnivel y procedencia.
Datos climáticos experimentales 1996–2025 en 6 descargas, ERA5-Land + ERA5.
Sin máscara oficial, estaciones SENAMHI ni alertas calibradas.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import perfiles_climaticos_8o as climate
import muestreo_zonas_contiguas_8p as design

ROOT=Path(__file__).resolve().parents[1]
NODES="datos/muestreo_8o/nodos_dem_8o.csv"
OLD_CLIMATE="datos/clima_contiguo_8p/estado_clima_8p.json"
BASE="datos/transectos_8q"
RAW="datos/transectos_8q/fuentes"
SEGMENTS=(("V1a","M0163","M0224"),("V1b","M0184","M0224"),
          ("V2","M0234","M0308"))
FRACTIONS=(.2,.4,.6,.8)
FIELDS=("testigo_id","transecto","extremo_inicio","extremo_fin",
        "fraccion_objetivo","distancia_al_objetivo_km",
        "latitud","longitud","altitud_dem_m","altitud_lineal_esperada_m",
        "salto_altitudinal_lineal_m","perfil_8p_completo_ya_existente",
        "homogeneidad_espacial_acreditada")
CMP_FIELDS=("transecto","testigo_id","altitud_dem_m","tmedia_1996_2025_c",
            "precipitacion_anual_media_mm","humedad_relativa_media_pct",
            "radiacion_anual_media_mj_m2","clima_instrumental_verificado")
CELL_FIELDS=("transecto","testigo_id","modelo","latitud_celda_api",
             "longitud_celda_api","n_centros_distintos_en_decadas",
             "coincide_con_otra_muestra_mismo_transecto","valor_de_celda_no_es_sensor")
COH_FIELDS=("transecto","testigo_a","testigo_b",
            "distancia_geografica_km","desnivel_dem_m",
            "correlacion_anomalia_tmedia_360_meses",
            "mae_diferencia_anomalia_tmedia_c",
            "correlacion_anomalia_precipitacion_360_meses",
            "igual_celda_temperatura","igual_celda_precipitacion",
            "independencia_instrumental_verificada")

def csv_data(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def sha(x):return hashlib.sha256(x).hexdigest()
def csv_text(rows,cols):
    buf=io.StringIO(newline="")
    w=csv.DictWriter(buf,fieldnames=cols,lineterminator="\n")
    w.writeheader()
    for r in rows:w.writerow({k:r.get(k,"") for k in cols})
    return buf.getvalue()

def samples(root):
    nodes=csv_data(root/NODES)
    if len(nodes)!=420:raise ValueError("No hay 420 elevaciones DEM 8O verificadas")
    byid={}
    for n in nodes:
        if n.get("homogeneidad_validada")!="false":raise ValueError("8O no declara zonas homogéneas")
        for k in ("latitud","longitud","altitud_dem_m"):n[k]=float(n[k])
        byid[n["id"]]=n
    if len(byid)!=420:raise ValueError("Malla DEM duplicada")
    if any(a not in byid or b not in byid for _,a,b in SEGMENTS):
        raise ValueError("Nodos de investigación V1/V2 ausentes del inventario")
    current=root/OLD_CLIMATE
    previous={}
    if current.exists():
        j=json.loads(current.read_text(encoding="utf-8"))
        if j.get("fase")!="8P" or j.get("zonas_homogeneas_geograficas_certificadas")!=0:
            raise ValueError("Referencia de 8P inconsistente con verificación regional")
        complete=root/"datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv"
        if complete.exists():previous={r["id"] for r in csv_data(complete)}
    # Lock selections to DEM input and reference transect, not to newly
    # arriving 8P observations. Allows deterministic tests and audit.
    seen=set()
    selected=[]
    layout=[]
    for transect,a,b in SEGMENTS:
        start=byid[a];end=byid[b]
        route_km=design.haversine(start["latitud"],start["longitud"],
                     end["latitud"],end["longitud"])
        recorded=[]
        for f in FRACTIONS:
            lat=start["latitud"]*(1-f)+end["latitud"]*f
            lon=start["longitud"]*(1-f)+end["longitud"]*f
            expected=start["altitud_dem_m"]*(1-f)+end["altitud_dem_m"]*f
            candidates=sorted(((design.haversine(lat,lon,p["latitud"],p["longitud"]),p)
               for p in nodes if p["id"] not in (a,b) and p["altitud_dem_m"]>5
               and p["id"] not in seen),key=lambda item:(item[0],item[1]["id"]))
            if not candidates or candidates[0][0]>5:
                recorded.append({"fraccion":f,"sin_punto_cercano":True})
                continue
            distance,p=candidates[0]
            seen.add(p["id"])
            row={"testigo_id":p["id"],"transecto":transect,
              "extremo_inicio":a,"extremo_fin":b,"fraccion_objetivo":f,
              "distancia_al_objetivo_km":round(distance,4),
              "latitud":p["latitud"],"longitud":p["longitud"],
              "altitud_dem_m":p["altitud_dem_m"],
              "altitud_lineal_esperada_m":round(expected,1),
              "salto_altitudinal_lineal_m":round(p["altitud_dem_m"]-expected,1),
              "perfil_8p_completo_ya_existente":"true" if p["id"] in previous else "false",
              "homogeneidad_espacial_acreditada":"false"}
            selected.append(row);recorded.append(row)
        layout.append({
           "transecto":transect,"inicio":a,"fin":b,
           "distancia_entre_extremos_km":round(route_km,3),
           "altitud_extremo_inicio_m":start["altitud_dem_m"],
           "altitud_extremo_fin_m":end["altitud_dem_m"],
           "numero_nodos_intermedios_dem":len([x for x in recorded if "testigo_id" in x]),
           "muestras":[{"fraccion_objetivo":r["fraccion_objetivo"],"id":r["testigo_id"],
                "altitud_dem_m":r["altitud_dem_m"],"desviacion_alt_lineal_m":r["salto_altitudinal_lineal_m"]}
                for r in recorded if "testigo_id" in r],
           "altitud_maxima_muestra_intermedia_m":max((r["altitud_dem_m"] for r in recorded if "testigo_id" in r),default=None),
           "altitud_minima_muestra_intermedia_m":min((r["altitud_dem_m"] for r in recorded if "testigo_id" in r),default=None),
           "continuidad_climatica_demostrada":False,
           "distancia_objetivo_interpolada_no_camino_real":True
        })
    if len(selected)<8 or len(selected)>12:
        raise ValueError("La malla carece de densidad para transectos V1/V2")
    return selected,layout

def points(selected):
    return [{"id":p["testigo_id"],"latitud":p["latitud"],
             "longitud":p["longitud"],"altitud_dem_m":p["altitud_dem_m"]}
            for p in selected]

def source_paths(root,model,start,end):
    return (root/RAW/f"{model}_{start}_{end}.json.gz",
            root/RAW/f"{model}_{start}_{end}.meta.json")

def inspect(root,model,start,end,pts):
    p,m=source_paths(root,model,start,end)
    if not p.exists() and not m.exists():return None
    if not p.exists() or not m.exists():raise ValueError("8Q fuente climática incompleta")
    blob=gzip.decompress(p.read_bytes())
    info=json.loads(m.read_text(encoding="utf-8"))
    if (info.get("fase")!="8Q" or info.get("modelo")!=model or
        info.get("periodo")!=[start,end] or info.get("url")!=climate.query(model,start,end,pts) or
        info.get("ids")!=[x["id"] for x in pts] or info.get("sha256_original")!=sha(blob)):
        raise ValueError("8Q fuente SHA/URL/identidad no verificable")
    return climate.validate_blob(blob,model,start,end,pts)

def fetch(root,max_new=1):
    chosen,_=samples(root)
    pts=points(chosen)
    (root/RAW).mkdir(parents=True,exist_ok=True)
    added=0
    for model in climate.VARS:
        for start,end in climate.BLOCKS:
            if inspect(root,model,start,end,pts) is not None:continue
            if added>=max_new:return
            url=climate.query(model,start,end,pts)
            try:
                with urlopen(Request(url,headers={"User-Agent":"OAF-8Q-climate-transects/1.0"}),timeout=140) as resp:
                    if resp.status!=200:raise ValueError("HTTP inesperado")
                    blob=resp.read(22_000_001)
                if len(blob)>22_000_000:raise ValueError("Respuesta demasiado grande")
                climate.validate_blob(blob,model,start,end,pts)
            except HTTPError as exc:
                if exc.code==429:
                    print("Cuota histórica agotada (429), fuentes originales conservadas.",flush=True)
                    return
                raise
            except (OSError,ValueError,TimeoutError,json.JSONDecodeError) as exc:
                print("Proveedor 8Q fuente no verificable:",str(exc),flush=True)
                return
            p,m=source_paths(root,model,start,end)
            info={"fase":"8Q","modelo":model,"periodo":[start,end],
                  "url":url,"ids":[x["id"] for x in pts],
                  "sha256_original":sha(blob),
                  "consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "reanálisis_no_instrumental":True}
            p.write_bytes(gzip.compress(blob,mtime=0))
            m.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            added+=1
            print("Bloque 8Q validado",model,start,end,flush=True)
            if added<max_new:time.sleep(3)

def corr(x,y):
    """Pearson without numpy; undefined when either anomaly variance is zero."""
    if len(x)!=len(y) or len(x)<2:raise ValueError("Series de anomalía incompatibles")
    mx=statistics.mean(x);my=statistics.mean(y)
    a=[v-mx for v in x];b=[v-my for v in y]
    sx=math.sqrt(sum(v*v for v in a));sy=math.sqrt(sum(v*v for v in b))
    return None if sx<1e-9 or sy<1e-9 else sum(v*w for v,w in zip(a,b))/(sx*sy)

def coherence(months,selected,centers):
    """Only descriptive covariability of matched monthly anomalies 1996–2025.

    Baseline is EACH site's 1996–2025 calendar-month mean, not a blended
    regional normal. No forecasting/hindcast accuracy is inferred.
    """
    keys=sorted({mon for _,mon in months})
    if len(keys)!=360:raise ValueError("Anomalías requieren 360 meses históricos")
    bysite={}
    for p in selected:
        pid=p["testigo_id"]
        sequences={}
        for variable in ("temperature_2m_mean","precipitation_sum"):
            norm={m:statistics.mean(months[(pid,key)][variable] for key in keys
                    if int(key[5:7])==m) for m in range(1,13)}
            if any(sum(int(key[5:7])==m for key in keys)!=30 for m in range(1,13)):
                raise ValueError("Cada normal mensual necesita 30 años")
            sequences[variable]=[months[(pid,k)][variable]-norm[int(k[5:7])] for k in keys]
        bysite[pid]=sequences
    rows=[]
    for name in sorted(set(p["transecto"] for p in selected)):
        group=[p for p in selected if p["transecto"]==name]
        for i,a in enumerate(group):
            for b in group[i+1:]:
                aid=a["testigo_id"];bid=b["testigo_id"]
                tempA=bysite[aid]["temperature_2m_mean"]
                tempB=bysite[bid]["temperature_2m_mean"]
                rainA=bysite[aid]["precipitation_sum"]
                rainB=bysite[bid]["precipitation_sum"]
                rT=corr(tempA,tempB);rP=corr(rainA,rainB)
                tSame=(len(centers.get(("era5_land",aid),set()))==1 and
                        centers.get(("era5_land",aid))==centers.get(("era5_land",bid)))
                pSame=(len(centers.get(("era5",aid),set()))==1 and
                        centers.get(("era5",aid))==centers.get(("era5",bid)))
                rows.append({
                  "transecto":name,"testigo_a":aid,"testigo_b":bid,
                  "distancia_geografica_km":round(design.haversine(
                    a["latitud"],a["longitud"],b["latitud"],b["longitud"]),4),
                  "desnivel_dem_m":round(abs(a["altitud_dem_m"]-b["altitud_dem_m"]),1),
                  "correlacion_anomalia_tmedia_360_meses":round(rT,5) if rT is not None else "",
                  "mae_diferencia_anomalia_tmedia_c":round(statistics.mean(
                     abs(x-y) for x,y in zip(tempA,tempB)),5),
                  "correlacion_anomalia_precipitacion_360_meses":round(rP,5) if rP is not None else "",
                  "igual_celda_temperatura":"true" if tSame else "false",
                  "igual_celda_precipitacion":"true" if pSame else "false",
                  "independencia_instrumental_verificada":"false"})
    return rows

def evaluate(root):
    selected,layout=samples(root);pts=points(selected)
    sources={}
    for model in climate.VARS:
        for start,end in climate.BLOCKS:
            blob=inspect(root,model,start,end,pts)
            if blob is not None:sources[(model,start,end)]=blob
    # Coordenadas de cada respuesta histórica real, conservando separación
    # entre ERA5 y ERA5-Land. Se admiten resultados de modelos con al menos
    # una década disponible, pero no se reclama estabilidad sin tres.
    centers={}
    for (model,begin,end),blob in sources.items():
        for p,obj in zip(selected,blob):
            key=(model,p["testigo_id"])
            centers.setdefault(key,set()).add(
              (round(float(obj["latitude"]),5),round(float(obj["longitude"]),5)))
    by_transect={}
    for p in selected:
        by_transect.setdefault(p["transecto"],[]).append(p["testigo_id"])
    cellrows=[]
    for p in selected:
        for model in climate.VARS:
            coords=centers.get((model,p["testigo_id"]),set())
            if not coords:continue
            unique=sorted(coords)
            center=unique[0] if len(unique)==1 else (None,None)
            same=any(len(coords)==1 and coords==centers.get((model,other),set())
                 for other in by_transect[p["transecto"]]
                 if other!=p["testigo_id"])
            cellrows.append({"transecto":p["transecto"],
              "testigo_id":p["testigo_id"],"modelo":model,
              "latitud_celda_api":center[0] if center[0] is not None else "",
              "longitud_celda_api":center[1] if center[1] is not None else "",
              "n_centros_distintos_en_decadas":len(unique),
              "coincide_con_otra_muestra_mismo_transecto":"true" if same else "false",
              "valor_de_celda_no_es_sensor":"true"})
    complete=len(sources)==6
    comparables=[]
    covariation=[]
    if complete:
        months={}
        for (model,start,end),blob in sources.items():
            for key,records in climate.monthly(blob,model,pts).items():
                months.setdefault(key,{}).update(records)
        if len(months)!=360*len(pts):raise ValueError("8Q periodos mensuales incompletos")
        covariation=coherence(months,selected,centers)
        for p in selected:
            values=[r for (id,month),r in months.items() if id==p["testigo_id"]]
            if len(values)!=360:raise ValueError("8Q faltan 360 meses")
            comparables.append({
              "transecto":p["transecto"],"testigo_id":p["testigo_id"],
              "altitud_dem_m":p["altitud_dem_m"],
              "tmedia_1996_2025_c":round(statistics.mean(v["temperature_2m_mean"] for v in values),4),
              "precipitacion_anual_media_mm":round(sum(v["precipitation_sum"] for v in values)/30,3),
              "humedad_relativa_media_pct":round(statistics.mean(v["relative_humidity_2m_mean"] for v in values),3),
              "radiacion_anual_media_mj_m2":round(sum(v["shortwave_radiation_sum"] for v in values)/30,3),
              "clima_instrumental_verificado":"false"})
    report={
       "fase":"8Q","estado":"transectos_climaticos_completos_no_zonas_validadas" if complete
                 else "transectos_dem_con_clima_historico_pendiente",
       "segmentos_originales_ex_ante":len(SEGMENTS),
       "testigos_intermedios_dem_seleccionados":len(selected),
       "n_muestras_previas_8p":sum(p["perfil_8p_completo_ya_existente"]=="true" for p in selected),
       "fuentes_climaticas_verificadas":len(sources),
       "fuentes_climaticas_previstas":6,
       "n_testigos_intermedios_30_anios_completos":len(comparables),
       "n_comparaciones_de_anomalias_por_pares":len(covariation),
       "comparaciones_con_celda_temperatura_compartida":sum(
           r["igual_celda_temperatura"]=="true" for r in covariation),
       "comparaciones_con_celda_precipitacion_compartida":sum(
           r["igual_celda_precipitacion"]=="true" for r in covariation),
       "covariacion_de_anomalias_no_es_habilidad_predictiva":True,
       "periodo":"1996–2025",
       "transectos":layout,
       "centros_de_celda_api_revisados":len(cellrows),
       "muestras_con_celda_era5_repetida_en_mismo_transecto":len({
          c["testigo_id"] for c in cellrows if c["modelo"]=="era5" and
          c["coincide_con_otra_muestra_mismo_transecto"]=="true"
       }),
       "muestras_con_celda_era5land_repetida_en_mismo_transecto":len({
          c["testigo_id"] for c in cellrows if c["modelo"]=="era5_land" and
          c["coincide_con_otra_muestra_mismo_transecto"]=="true"
       }),
       "identidad_de_celda_no_garantiza_medicion_independiente":True,
       "zonas_contiguas_homogeneas_demostradas":0,
       "poligonos_agroclimaticos_certificados":0,
       "instrumentos_SENAMHI_confirmados":0,
       "modelo_predictivo_zonal_validado":False,
       "mascara_tierra_agua_y_limite_oficial_confirmados":False,
       "laderas_orientacion_cuencas_verificadas":False,
       "elevaciones_es_dem_modelado_no_sensor":True,
       "diferencias_fisicas_no_prueban_diferencias_climaticas":True,
       "interpolacion_de_coordenadas_no_es_ruta_topografica":True,
       "todas_las_zonas_homogeneas_pendientes":True,
       "advertencias":[
          "Transectos lineales son muestreo ex ante, no perfiles continuos del terreno.",
          "Elevaciones del DEM evidencian heterogeneidad física; la altitud de un punto no permite inferir clima en otro.",
          "El mismo centro ERA5-Land o ERA5 puede repetirse entre puntos intermedios. Debe verificarse antes de inferir independencia.",
          "Sin cartografía oficial, máscara de mar, orientación de laderas y cuencas no se delimitan polígonos agrícolas.",
          "Datos de reanálisis no sustituyen observaciones instrumentales SENAMHI ni campo, ni respaldan alertas operativas."
       ],
       "proveniencia":{"dem_csv_sha256":sha((root/NODES).read_bytes()),
          "segmentos":[list(g) for g in SEGMENTS],
          "fuentes_SHA_original":{f"{m}_{a}_{b}":sha(gzip.decompress(source_paths(root,m,a,b)[0].read_bytes()))
             for (m,a,b) in sources}}
    }
    return report,selected,comparables,cellrows,covariation

def publish(root,check=False):
    state,samples_,metrics,cellrows,covariation=evaluate(root)
    base=root/BASE
    outputs={
      base/"estado_transectos_8q.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
      base/"muestras_intermedias_8q.csv":csv_text(samples_,FIELDS),
      base/"comparacion_climatica_8q.csv":csv_text(metrics,CMP_FIELDS),
      base/"centros_modelados_8q.csv":csv_text(cellrows,CELL_FIELDS),
      base/"coherencia_anomalias_8q.csv":csv_text(covariation,COH_FIELDS)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,contents in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=contents:
                raise ValueError("8Q reporte no coincide con evidencia de origen")
        elif not path.exists() or path.read_text(encoding="utf-8")!=contents:
            path.write_text(contents,encoding="utf-8")
    print(json.dumps({"fase":"8Q","n_intermedios":len(samples_),
      "n_fuentes":state["fuentes_climaticas_verificadas"],
      "n_perfiles_completos":state["n_testigos_intermedios_30_anios_completos"],
      "check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--max-new",type=int,default=1)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    if args.fetch:fetch(args.root,args.max_new)
    publish(args.root,args.check)
