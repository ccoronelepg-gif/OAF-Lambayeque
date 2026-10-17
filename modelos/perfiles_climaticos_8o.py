#!/usr/bin/env python3
"""8O: climatologías de testigos estratificados y grupos de similitud preliminares.

Modelos de reanálisis diferenciados: ERA5-Land (Tmean/Tmax/Tmin) y
ERA5 (precipitación/RH/radiación). Mismas coordenadas, fechas y selección land;
estas variables NO se declaran instrumentales ni píxeles espaciales idénticos.
Grupos climáticos NO son zonas SIG homogéneas validadas.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics,time
from datetime import date,timedelta,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
TESTIGOS="datos/muestreo_8o/testigos_climaticos_8o.csv"
DEM_STATE="datos/muestreo_8o/estado_muestreo_8o.json"
INPUT="datos/perfiles_climaticos_8o/fuentes"
OUTPUT="datos/perfiles_climaticos_8o"
API="https://archive-api.open-meteo.com/v1/archive"
BLOCKS=((1996,2005),(2006,2015),(2016,2025))
VARS={
 "era5_land":("temperature_2m_mean","temperature_2m_max","temperature_2m_min"),
 "era5":("precipitation_sum","relative_humidity_2m_mean","shortwave_radiation_sum")
}
FEATS=("tmedia_c","amplitud_termica_c","precipitacion_mm","humedad_relativa_pct","radiacion_mj_m2")
PROFILE_COLUMNS=("id","latitud","longitud","altitud_dem_m","estrato_fisico_preliminar",
                 "grupo_similitud_exploratoria","distancia_centroide",
                 "zona_climatica_validada","periodo","n_meses_observados")
NORMAL_COLUMNS=("id","mes_calendario","tmedia_c","amplitud_termica_c","precipitacion_mm",
                "humedad_relativa_pct","radiacion_mj_m2","grupo_similitud_exploratoria")
BATCH_COUNT=6

def sha(blob):return hashlib.sha256(blob).hexdigest()
def read_testigos(root):
    state=json.loads((root/DEM_STATE).read_text(encoding="utf-8"))
    if state.get("fase")!="8O" or state.get("nodos_dem_verificados")!=state.get("nodos_diseno"):
        return []
    with (root/TESTIGOS).open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if not 12<=len(rows)<=25 or len({r["id"] for r in rows})!=len(rows):
        raise ValueError("Testigos climáticos sin selección geográfica válida")
    for r in rows:
        if r["homogeneidad_validada"]!="false" or r["candidato_testigo_climatico"]!="true":
            raise ValueError("Testigo indebidamente homologado como clima")
        for k in ("latitud","longitud","altitud_dem_m"):
            r[k]=float(r[k])
    return rows

def query(method,start,end,points):
    return API+"?"+urlencode({
      "latitude":",".join(str(p["latitud"]) for p in points),
      "longitude":",".join(str(p["longitud"]) for p in points),
      "start_date":f"{start}-01-01","end_date":f"{end}-12-31",
      "timezone":"America/Lima",
      "daily":",".join(VARS[method]),
      "models":method,"cell_selection":"land"
    })

def raw_paths(root,model,start,end):
    base=root/INPUT
    return base/f"{model}_{start}_{end}.json.gz",base/f"{model}_{start}_{end}.meta.json"

def dates(start,end):
    d0=date(start,1,1);d1=date(end,12,31)
    return [(d0+timedelta(days=i)).isoformat() for i in range((d1-d0).days+1)]

def validate_blob(raw,model,start,end,points):
    payload=json.loads(raw)
    if not isinstance(payload,list) or len(payload)!=len(points):
        raise ValueError("Reanálisis API sin el número exacto de testigos")
    full=dates(start,end)
    for point,obj in zip(points,payload):
        if (not isinstance(obj,dict) or obj.get("error") or
            obj.get("timezone")!="America/Lima" or obj.get("utc_offset_seconds")!=-18000):
            raise ValueError("Zona o error de reanálisis no aceptado")
        d=obj.get("daily") or {}
        if d.get("time")!=full:raise ValueError("Serie incompleta o fechas desordenadas")
        coords=(obj.get("latitude"),obj.get("longitude"),obj.get("elevation"))
        if any(type(v) not in (float,int) or not math.isfinite(v) for v in coords):
            raise ValueError("Proveedor no indica geometría de celda")
        if abs(coords[0]-point["latitud"])>.5 or abs(coords[1]-point["longitud"])>.5:
            raise ValueError("Centro de celda demasiado alejado")
        units=obj.get("daily_units") or {}
        for variable in VARS[model]:
            values=d.get(variable)
            if not isinstance(values,list) or len(values)!=len(full):
                raise ValueError("Variable meteorológica ausente")
            for value in values:
                if type(value) not in (int,float) or not math.isfinite(value):
                    raise ValueError("Dato meteorológico nulo/no numérico (no imputar)")
                if variable.startswith("temperature_2m") and not -45<value<58:
                    raise ValueError("Temperatura físicamente anómala")
                if variable=="precipitation_sum" and not 0<=value<2000:
                    raise ValueError("Precipitación diaria fuera de rango")
                if variable=="relative_humidity_2m_mean" and not 0<=value<=100:
                    raise ValueError("Humedad diaria fuera de rango")
                if variable=="shortwave_radiation_sum" and not 0<=value<=50:
                    raise ValueError("Radiación diaria fuera de rango")
        if model=="era5_land":
            for mn,mx,mean in zip(d["temperature_2m_min"],d["temperature_2m_max"],d["temperature_2m_mean"]):
                if mn>mx or mn-0.5>mean or mx+0.5<mean:
                    raise ValueError("Tmin/Tmedia/Tmax inconsistentes")
    return payload

def read_source(root,model,start,end,points):
    p,m=raw_paths(root,model,start,end)
    if not p.exists() and not m.exists():return None
    if not p.exists() or not m.exists():raise ValueError("Bloque meteorológico parcial en disco")
    raw=gzip.decompress(p.read_bytes())
    if len(raw)>25_000_000:raise ValueError("Bloque climático demasiado grande")
    meta=json.loads(m.read_text(encoding="utf-8"))
    if (meta.get("fase")!="8O" or meta.get("modelo")!=model or
        meta.get("periodo")!=[start,end] or meta.get("url")!=query(model,start,end,points) or
        meta.get("sha256_original")!=sha(raw) or
        meta.get("ids")!=[p["id"] for p in points]):
        raise ValueError("Integridad/URL temporal/identidad de fuente climática inválida")
    return validate_blob(raw,model,start,end,points),meta

def fetch(root,max_new=1):
    points=read_testigos(root)
    if not points:
        print("Aún no hay DEM completo y testigos seleccionados; sin consultas de clima.")
        return
    (root/INPUT).mkdir(parents=True,exist_ok=True)
    added=0
    for model in VARS:
        for start,end in BLOCKS:
            if read_source(root,model,start,end,points) is not None:continue
            if added>=max_new:return
            url=query(model,start,end,points)
            try:
                with urlopen(Request(url,headers={"User-Agent":"OAF-8O-stratified-climate-research/1.0"}),timeout=140) as response:
                    if response.status!=200:raise ValueError("HTTP != 200")
                    blob=response.read(25_000_001)
                if len(blob)>25_000_000:raise ValueError("Respuesta muy extensa")
                validate_blob(blob,model,start,end,points)
            except HTTPError as exc:
                if exc.code==429:
                    print("Proveedor informa HTTP429: esperar próximo ciclo; nada simulado.",flush=True)
                    return
                raise
            except (OSError,ValueError,json.JSONDecodeError) as exc:
                print("Respuesta no válida para",model,start,end,str(exc),flush=True)
                return
            p,m=raw_paths(root,model,start,end)
            meta={"fase":"8O","modelo":model,"periodo":[start,end],
                  "ids":[x["id"] for x in points],"url":url,
                  "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "sha256_original":sha(blob),
                  "reanálisis_no_instrumental":True,
                  "no_son_zonas_climaticas_certificadas":True}
            p.write_bytes(gzip.compress(blob,mtime=0))
            m.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            added+=1
            print("Fuente 8O validada:",model,start,end,flush=True)
            if added<max_new:time.sleep(4)

def monthly(payload,model,points):
    out={}
    for p,obj in zip(points,payload):
        vals=obj["daily"]
        months={}
        for i,day in enumerate(vals["time"]):
            key=day[:7]
            buf=months.setdefault(key,{v:[] for v in VARS[model]})
            for v in VARS[model]:buf[v].append(vals[v][i])
        for key,buf in months.items():
            result={}
            for variable,seq in buf.items():
                result[variable]=sum(seq) if variable in ("precipitation_sum","shortwave_radiation_sum") else statistics.mean(seq)
            out[(p["id"],key)]=result
    return out

def agglomerate(vectors,k):
    """Determinista, vinculación media, sin 'forzar' límites climáticos."""
    cl=[[i] for i in range(len(vectors))]
    def d(i,j):
        return math.sqrt(sum((a-b)**2 for a,b in zip(vectors[i],vectors[j]))/len(vectors[i]))
    while len(cl)>k:
        choices=[]
        for a in range(len(cl)):
            for b in range(a+1,len(cl)):
                distance=statistics.mean(d(i,j) for i in cl[a] for j in cl[b])
                choices.append((distance,tuple(cl[a]),tuple(cl[b]),a,b))
        _,_,_,a,b=min(choices)
        cl[a]=sorted(cl[a]+cl[b]);cl.pop(b)
    return sorted(cl,key=lambda g:min(g))

def silhouette(vec,clusters):
    label={p:i for i,g in enumerate(clusters) for p in g}
    if any(len(g)<2 for g in clusters):return None
    def dst(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(vec[a],vec[b]))/len(vec[a]))
    scores=[]
    for i in range(len(vec)):
        own=clusters[label[i]]
        a=statistics.mean(dst(i,j) for j in own if i!=j)
        b=min(statistics.mean(dst(i,j) for j in group) for n,group in enumerate(clusters) if n!=label[i])
        scores.append((b-a)/max(a,b) if max(a,b)>0 else 0)
    return statistics.mean(scores)

def adjusted_rand(full,other):
    """ARI de contingencia entre particiones; 1 equivale a identidad."""
    if len(full)!=len(other):raise ValueError("Comparación ARI de distinta longitud")
    n=len(full)
    if n<2:return None
    def c2(x):return x*(x-1)/2
    row={}
    col={}
    cont={}
    for a,b in zip(full,other):
        row[a]=row.get(a,0)+1
        col[b]=col.get(b,0)+1
        cont[(a,b)]=cont.get((a,b),0)+1
    obs=sum(c2(v) for v in cont.values())
    sumsA=sum(c2(v) for v in row.values())
    sumsB=sum(c2(v) for v in col.values())
    expected=sumsA*sumsB/c2(n)
    maximum=(sumsA+sumsB)/2
    return 1.0 if abs(maximum-expected)<1e-12 else (obs-expected)/(maximum-expected)

def csv_text(rows,cols):
    b=io.StringIO(newline="")
    w=csv.DictWriter(b,fieldnames=cols,lineterminator="\n")
    w.writeheader();w.writerows(rows)
    return b.getvalue()

def build(root):
    selected=read_testigos(root)
    keys=[(model,start,end) for model in VARS for start,end in BLOCKS]
    sources={}
    if selected:
        for key in keys:
            data=read_source(root,*key,selected)
            if data is not None:sources[key]=data
    out={
     "fase":"8O","estado":"perfiles_multivariables_pendientes",
     "n_testigos":len(selected),"n_fuentes_esperadas":6,"n_fuentes_archivadas":len(sources),
     "n_testigos_con_perfil_30anios":0,"n_grupos_similitud_exploratorios":0,
     "homogeneidad_espacial_certificada":False,"zonas_agroclimaticas_operativas":0,
     "capacidad_predictiva_zonal_demostrada":False,"validacion_instrumental_SENAMHI":False,
     "periodo":"1996–2025","modelos_fuente_por_variable":{
        "Tmedia_Tmax_Tmin":"ERA5-Land a través de Open-Meteo",
        "lluvia_humedad_radiacion":"ERA5 a través de Open-Meteo"},
     "sin_iguales_pixeles_entre_fuentes_demostrados":True,
     "sin_imputar_ausencias":True,"analisis":None,
     "restricciones":[
       "Testigos espaciales estratificados no son todos los nodos ni representan porcentajes de área.",
       "Grupo de similitud multivariable no es zona geográfica contigua ni pronóstico validado.",
       "ERA5 vs ERA5-Land pueden usar distinta resolución espacial y bajar escala por elevación.",
       "El umbral de separación de grupos se elige exploratoriamente con silueta, sujeto a estabilidad anual y muestreo denso.",
       "La altitud informa el diseño, pero no es una variable que fuerce directamente los conglomerados climáticos."
     ],
     "trazabilidad":{"archivo_testigos_sha256":hashlib.sha256((root/TESTIGOS).read_bytes()).hexdigest() if (root/TESTIGOS).exists() else None,
       "fuentes":[m for d,m in sources.values()]}
    }
    if len(sources)!=6:return out,[],[]
    profiles={}
    for (model,start,end),(p,meta) in sources.items():
        months=monthly(p,model,selected)
        for key,fields in months.items():
            profile=profiles.setdefault(key,{})
            if set(profile)&set(fields):raise ValueError("Variables meteorológicas duplicadas")
            profile.update(fields)
    if len(profiles)!=len(selected)*360:raise ValueError("No hay 360 meses por testigo")
    normal={}
    for point in selected:
        for m in range(1,13):
            values=[v for (pid,month),v in profiles.items()
                    if pid==point["id"] and int(month[-2:])==m]
            if len(values)!=30:raise ValueError("Climatología de 30 años incompleta")
            normal[(point["id"],m)]={
               "tmedia_c":statistics.mean(v["temperature_2m_mean"] for v in values),
               "amplitud_termica_c":statistics.mean(v["temperature_2m_max"]-v["temperature_2m_min"] for v in values),
               "precipitacion_mm":statistics.mean(v["precipitation_sum"] for v in values),
               "humedad_relativa_pct":statistics.mean(v["relative_humidity_2m_mean"] for v in values),
               "radiacion_mj_m2":statistics.mean(v["shortwave_radiation_sum"] for v in values)
            }
    vectors=[]
    ids=[p["id"] for p in selected]
    # Normalización por variable sobre todos los testigos y meses; 12 meses por variable.
    scaling={}
    for feat in FEATS:
        vals=[normal[(pid,m)][feat] for pid in ids for m in range(1,13)]
        scaling[feat]=(statistics.mean(vals),max(1e-6,statistics.pstdev(vals)))
    for pid in ids:
        vectors.append([round((normal[(pid,m)][feat]-scaling[feat][0])/scaling[feat][1],8)
             for feat in FEATS for m in range(1,13)])
    candidates=[]
    for k in range(2,min(6,len(ids)-1)+1):
        groups=agglomerate(vectors,k)
        quality=silhouette(vectors,groups)
        if quality is not None:candidates.append((quality,k,groups))
    if not candidates:
        out["estado"]="perfiles_completos_sin_agrupacion_estable_minima"
        return out,[],[]
    quality,k,groups=max(candidates,key=lambda x:(x[0],-x[1]))
    label={ids[point]:f"C{groupidx+1}" for groupidx,group in enumerate(groups)
           for point in group}
    # Distancia del nodo a su medoid, no predicción ni error de campo.
    dist={}
    for group in groups:
        for node in group:
            dist[node]=statistics.mean(math.sqrt(sum((a-b)**2 for a,b in zip(vectors[node],vectors[other]))/len(vectors[node])) for other in group if other!=node)
    nodes=[{"id":p["id"],"latitud":p["latitud"],"longitud":p["longitud"],
            "altitud_dem_m":p["altitud_dem_m"],"estrato_fisico_preliminar":p["estrato_fisico_preliminar"],
            "grupo_similitud_exploratoria":label[p["id"]],"distancia_centroide":round(dist[i],5),
            "zona_climatica_validada":"false","periodo":"1996–2025","n_meses_observados":360}
            for i,p in enumerate(selected)]
    norms=[{"id":p["id"],"mes_calendario":m,**{f:round(normal[(p["id"],m)][f],5) for f in FEATS},
            "grupo_similitud_exploratoria":label[p["id"]]}
            for p in selected for m in range(1,13)]
    out["estado"]="núcleos_de_similitud_multivariable_exploratorios"
    out["n_testigos_con_perfil_30anios"]=len(selected)
    out["n_grupos_similitud_exploratorios"]=k
    # Más homogéneo significa menor distancia climática interna entre
    # testigos, no un polígono operativo ni continuidad geográfica demostrada.
    ranking=[]
    for index,group in enumerate(groups,1):
        pairs=[math.sqrt(sum((x-y)**2 for x,y in zip(vectors[i],vectors[j]))/len(vectors[i]))
                for a,i in enumerate(group) for j in group[a+1:]]
        positions=[selected[j] for j in group]
        geographic=[6371.0088*2*math.asin(min(1.0,math.sqrt(
            math.sin((p["latitud"]-q["latitud"])*math.pi/360)**2+
            math.cos(p["latitud"]*math.pi/180)*math.cos(q["latitud"]*math.pi/180)*
            math.sin((p["longitud"]-q["longitud"])*math.pi/360)**2)))
            for a,p in enumerate(positions) for q in positions[a+1:]]
        ranking.append({"grupo":f"C{index}","n_testigos":len(group),
            "distancia_climatica_interna_media":round(statistics.mean(pairs),5),
            "distancia_climatica_interna_maxima":round(max(pairs),5),
            "diametro_geografico_testigos_km":round(max(geographic),3),
            "rango_altitudinal_testigos_m":round(max(p["altitud_dem_m"] for p in positions)-
                                               min(p["altitud_dem_m"] for p in positions),1),
            "testigos_cota_dem_menor_o_igual_cero":sum(p["altitud_dem_m"]<=0 for p in positions),
            "evaluacion_mascara_tierra_costa_pendiente":True,
            "viabilidad_de_zona_agricola_verificada":False,
            "poligono_homogeneo_demostrado":False})
    ranking.sort(key=lambda g:(g["distancia_climatica_interna_media"],g["grupo"]))
    # Estabilidad exploratoria al reagrupar por tres décadas de diez años,
    # comparada por ARI con la partición completa 1996–2025.
    full_part=[next(i for i,g in enumerate(groups) if t in g) for t in range(len(ids))]
    decade_ari={}
    for start,end in BLOCKS:
        vdec=[]
        for pid in ids:
            vector=[]
            for feat in FEATS:
                for mon in range(1,13):
                    vals=[profile for (loc,month),profile in profiles.items()
                        if loc==pid and start<=int(month[:4])<=end and int(month[-2:])==mon]
                    if len(vals)!=10:raise ValueError("Década incompleta para estabilidad climática")
                    if feat=="tmedia_c":v=statistics.mean(z["temperature_2m_mean"] for z in vals)
                    elif feat=="amplitud_termica_c":v=statistics.mean(
                           z["temperature_2m_max"]-z["temperature_2m_min"] for z in vals)
                    elif feat=="precipitacion_mm":v=statistics.mean(z["precipitation_sum"] for z in vals)
                    elif feat=="humedad_relativa_pct":v=statistics.mean(z["relative_humidity_2m_mean"] for z in vals)
                    else:v=statistics.mean(z["shortwave_radiation_sum"] for z in vals)
                    vector.append(round((v-scaling[feat][0])/scaling[feat][1],8))
            vdec.append(vector)
        groups_dec=agglomerate(vdec,k)
        partition_dec=[next(i for i,g in enumerate(groups_dec) if t in g) for t in range(len(ids))]
        decade_ari[str(start)+"-"+str(end)]=round(adjusted_rand(full_part,partition_dec),5)
    out["analisis"]={
      "metodo":"agglomerative average-linkage; normal 1996-2025; variables escaladas",
      "k_seleccionado":k,"coeficiente_silueta":round(quality,5),
      "grupos":[{"nombre":f"C{i+1}","n_testigos":len(group),
                 "ids":[ids[p] for p in group]} for i,group in enumerate(groups)],
      "ranking_cohesion_climatica_no_zonas":ranking,
      "ari_temporal_comparado_con_periodo_completo":decade_ari,
      "estabilidad_temporal_exploratoria_evaluada":True,
      "estabilidad_espacial_y_contigüidad_certificadas":False,
      "estabilidad_temporal_y_espacial_evaluada":False,
      "grupos_aptos_para_zonificacion_agricola_operativa":0,
      "interpretacion_cautelar":"El menor contraste climático interno no demuestra continuidad territorial, suelo agrícola ni coherencia de lluvia; revisar nodos costeros de cota <=0 m y el grupo muy extenso de varias altitudes.",
      "poligonos_homogeneos_certificados":False
    }
    return out,nodes,norms

def publish(root,check=False):
    state,nodes,norms=build(root)
    d=root/OUTPUT
    outputs={
       d/"estado_climatico_8o.json":json.dumps(state,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
       d/"grupos_testigos_8o.csv":csv_text(nodes,PROFILE_COLUMNS),
       d/"normales_mensuales_testigos_8o.csv":csv_text(norms,NORMAL_COLUMNS)
    }
    if not check:d.mkdir(parents=True,exist_ok=True)
    for path,txt in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=txt:
                raise ValueError("Reportes climáticos 8O no reproducen fuentes")
        elif not path.exists() or path.read_text(encoding="utf-8")!=txt:path.write_text(txt,encoding="utf-8")
    print(json.dumps({"fase":"8O","climatic":state["estado"],"fuentes":state["n_fuentes_archivadas"],
                      "clusters_pilot":state["n_grupos_similitud_exploratorios"],"check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--max-new-batches",type=int,default=1)
    p.add_argument("--check",action="store_true")
    x=p.parse_args()
    if x.fetch:fetch(x.root,x.max_new_batches)
    publish(x.root,x.check)
