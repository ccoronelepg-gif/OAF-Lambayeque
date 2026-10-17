#!/usr/bin/env python3
"""8U NOAA AOML/CW ERDDAP geostrophic u/v, 2017–2025 (NOT 1996–2025).

Open public daily gridded NOAA/AOML reanalysis; u east, v north. A source
point is neither an in-situ current meter nor full Ekman+geostrophic current.
On provider access failure preserve partial data and report incomplete.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics
from collections import defaultdict
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
API="https://coastwatch.pfeg.noaa.gov/erddap/griddap/miamicurrents.csv"
DIR="datos/corrientes_8u"
BLOCKS=((2017,2020),(2021,2025))
POINTS=(("Aguas_frente_Pimentel",-6.7,-81.1),
        ("Aguas_norte_Lambayeque",-5.9,-81.5))
COLS=("mes","punto","latitude","longitude","u_este_geostrofica_m_s",
       "v_norte_geostrofica_m_s","magnitud_vector_media_m_s",
       "direccion_flujo_hacia_grados_desde_norte",
       "dias_con_dato","dias_calendario",
       "modelo_geostrofico_no_corriente_total","observacion_directa_campo")

def make_url(name,lat,lon,a,b):
    from_ =f"{a}-01-01T00:00:00Z"
    end=f"{b}-12-31T00:00:00Z"
    selector=f"[({from_}):1:({end})][({lat})][({lon})]"
    q=",".join(f"{v}{selector}" for v in ("u_current","v_current"))
    return API+"?"+quote(q,safe="[]():,.-")

def files(root,name,start,end):
    stem=f"{name}_{start}_{end}"
    return root/DIR/"fuentes"/(stem+".csv.gz"),root/DIR/"fuentes"/(stem+".meta.json")

def parse_original(blob,lat,lon,start,end):
    txt=blob.decode("utf-8-sig")
    reader=csv.reader(io.StringIO(txt))
    rows=list(reader)
    if len(rows)<3:raise ValueError("Respuesta corriente marina sin serie")
    heads=rows[0]
    if not all(x in heads for x in ("time","latitude","longitude","u_current","v_current")):
        raise ValueError("ERDDAP variables corrientes u/v ausentes")
    if not (rows[1][heads.index("u_current")].strip()=="m/s" and
            rows[1][heads.index("v_current")].strip()=="m/s"):
        raise ValueError("Unidades NOAA no son m/s")
    data={};invalid=0
    for values in rows[2:]:
        if not values or len(values)!=len(heads):raise ValueError("Filas ERDDAP inválidas")
        d=dict(zip(heads,values))
        day=d["time"][:10]
        if not (f"{start}-01-01"<=day<=f"{end}-12-31"):
            raise ValueError("Fecha NOAA fuera de intervalo solicitado")
        if day in data:raise ValueError("Fecha NOAA duplicada")
        if abs(float(d["latitude"])-lat)>.11 or abs(float(d["longitude"])-lon)>.11:
            raise ValueError("Coordenadas de rejilla desviadas del punto solicitado")
        u=d["u_current"].strip();v=d["v_current"].strip()
        if u.lower() in ("","nan") or v.lower() in ("","nan"):
            invalid+=1;continue
        try:a=float(u);b=float(v)
        except ValueError as exc:raise ValueError("Vector marino no numérico") from exc
        if not all(math.isfinite(x) and abs(x)<=6 for x in (a,b)):
            raise ValueError("Vector marino no verificable (m/s)")
        data[day]=(a,b)
    total=(date(end,12,31)-date(start,1,1)).days+1
    if len(data)<total*.70:
        raise ValueError(f"Cobertura marina insuficiente: {len(data)}/{total}")
    return data,invalid,total

def inspect(root,name,lat,lon,start,end):
    path,meta=files(root,name,start,end)
    if not path.exists() and not meta.exists():return None
    if not path.exists() or not meta.exists():raise ValueError("Corriente sin archivo y SHA")
    blob=gzip.decompress(path.read_bytes())
    m=json.loads(meta.read_text(encoding="utf-8"))
    if (m.get("fase")!="8U" or m.get("site")!=name or
       m.get("intervalo")!=[start,end] or m.get("url")!=make_url(name,lat,lon,start,end) or
       m.get("sha256_original")!=hashlib.sha256(blob).hexdigest()):
        raise ValueError("Corriente sin integridad original NOAA")
    return parse_original(blob,lat,lon,start,end)

def fetch(root,max_new=1):
    (root/DIR/"fuentes").mkdir(parents=True,exist_ok=True)
    n=0
    for name,lat,lon in POINTS:
        for start,end in BLOCKS:
            if inspect(root,name,lat,lon,start,end) is not None:continue
            if n>=max_new:return
            url=make_url(name,lat,lon,start,end)
            try:
                with urlopen(Request(url,headers={"User-Agent":"OAF-8U-marine-currents/1.0"}),
                  timeout=135) as response:
                    if response.status!=200:raise ValueError("NOAA ERDDAP HTTP")
                    blob=response.read(2_000_001)
                if len(blob)>2_000_000:raise ValueError("Respuesta oceánica demasiado grande")
                obs,miss,total=parse_original(blob,lat,lon,start,end)
            except HTTPError as e:
                print("ERDDAP respuesta HTTP",e.code,"- fuente pendiente",flush=True)
                return
            except (OSError,ValueError,TimeoutError) as e:
                print("NOAA/AOML no pudo acreditar serie marina:",str(e),flush=True)
                return
            file,meta=files(root,name,start,end)
            file.write_bytes(gzip.compress(blob,mtime=0))
            meta.write_text(json.dumps({
              "fase":"8U","site":name,"intervalo":[start,end],
              "url":url,"sha256_original":hashlib.sha256(blob).hexdigest(),
              "consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "dias_con_vectores_validos":len(obs),"dias_total_calendario":total,
              "fuente":"NOAA CoastWatch AOML miamicurrents, corrientes geostróficas",
              "no_es_OSCAR_total":True,"no_es_instrumento_campo":True
            },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("Corriente geostrófica NOAA archivada:",name,start,end,flush=True)
            n+=1

def output_csv(rows):
    text=io.StringIO(newline="")
    w=csv.DictWriter(text,fieldnames=COLS,lineterminator="\n")
    w.writeheader();w.writerows(rows)
    return text.getvalue()

def evaluate(root):
    blocks=[];rows=[]
    for name,lat,lon in POINTS:
        for a,b in BLOCKS:
            obj=inspect(root,name,lat,lon,a,b)
            if obj is not None:blocks.append((name,lat,lon,a,b,obj[0]))
    all_complete=len(blocks)==len(POINTS)*len(BLOCKS)
    values=defaultdict(list)
    for name,lat,lon,a,b,obs in blocks:
        for d,(u,v) in obs.items():values[(name,d[:7])].append((u,v))
    for name,lat,lon in POINTS:
        for y in range(2017,2026):
            for m in range(1,13):
                period=f"{y}-{m:02d}"
                number=(date(y+(m==12),m%12+1,1)-date(y,m,1)).days
                vals=values.get((name,period),[])
                # This is not a gap-filled continuous series.
                if len(vals)<max(10,math.ceil(number*.55)):
                    continue
                u=statistics.mean(p[0] for p in vals)
                v=statistics.mean(p[1] for p in vals)
                rows.append({
                  "mes":period,"punto":name,"latitude":lat,"longitude":lon,
                  "u_este_geostrofica_m_s":round(u,6),
                  "v_norte_geostrofica_m_s":round(v,6),
                  "magnitud_vector_media_m_s":round(math.hypot(u,v),6),
                  "direccion_flujo_hacia_grados_desde_norte":round(
                    (math.degrees(math.atan2(u,v))+360)%360,2),
                  "dias_con_dato":len(vals),"dias_calendario":number,
                  "modelo_geostrofico_no_corriente_total":"true",
                  "observacion_directa_campo":"false"})
    state={
      "fase":"8U","submodulo":"corrientes_geostroficas",
      "fuente":"NOAA/AOML CoastWatch near-real-time geostrophic currents",
      "periodo_fuente_disponible":"2016-07 hasta 2026-10 (según catálogo consultado)",
      "periodo_muestreo":"2017–2025",
      "n_series_punto_periodo_previstas":len(POINTS)*len(BLOCKS),
      "n_series_punto_periodo_verificadas":len(blocks),
      "periodos_realmente_archivados":[{"punto":name,"periodo":[a,b],"dias_verificados":len(obs)} for name,lat,lon,a,b,obs in blocks],
      "resultados_mensuales_parciales_permitidos_y_marcados":True,
      "n_meses_con_viento_o_corriente_simulada":0,
      "n_filas_geostroficas_reales_fuente_modelada_publicadas":len(rows),
      "periodo_1996_2025_de_corrientes_completo":False,
      "corrientes_completas_para_muestreo_2017_2025":all_complete,
      "no_incluye_corrientes_ekman_y_marea":True,
      "no_equivale_a_corriente_costera_in_situ":True,
      "n_fuentes_instrumentales_locales":0,
      "prediccion_validada":False,
      "advertencia":"Solo componente geostrófica superficial de NOAA/AOML; no corriente total de Humboldt, no observación in situ, no cobertura 1996–2025.",
      "muestras":[{"id":a,"lat":b,"lon":c} for a,b,c in POINTS]
    }
    return state,rows

def publish(root,check=False):
    report,rows=evaluate(root)
    base=root/DIR
    output={
       base/"estado_corrientes_8u.json":json.dumps(report,ensure_ascii=False,indent=2)+"\n",
       base/"corrientes_geostroficas_2017_2025.csv":output_csv(rows)
    }
    if not check:base.mkdir(parents=True,exist_ok=True)
    for p,v in output.items():
        if check:
            if not p.exists() or p.read_text(encoding="utf-8")!=v:
                raise ValueError("Archivo NOAA/AOML marine no reproducible")
        elif not p.exists() or p.read_text(encoding="utf-8")!=v:
            p.write_text(v,encoding="utf-8")
    print(json.dumps({"fase":"8U","corrientes_fuentes":report["n_series_punto_periodo_verificadas"],
      "meses":len(rows),"check":check}))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,default=ROOT)
    a.add_argument("--fetch",action="store_true")
    a.add_argument("--max-new",type=int,default=1)
    a.add_argument("--check",action="store_true")
    p=a.parse_args()
    if p.fetch:fetch(p.root,p.max_new)
    publish(p.root,p.check)
