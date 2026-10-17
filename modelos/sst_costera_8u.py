#!/usr/bin/env python3
"""8U: NOAA OISST v2.1 daily SST offshore Lambayeque at two actual ocean pixels.

Queries NOAA NCEI ERDDAP (final analyzed SST, not thermometer records), with
10-year source blocks and SHA. Reject null or land pixels; never impute missing
days or mislabel Niño1+2 as local SST. Sites are *offshore test points*, not
coastline nor official monitoring stations.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,statistics
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import perfiles_climaticos_8o as common

ROOT=Path(__file__).resolve().parents[1]
DATA="datos/sst_costera_8u"
API="https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv"
SOURCE="NOAA NCEI OISST v2.1 AVHRR-only final 0.25deg"
PERIODS=((1996,2005),(2006,2015),(2016,2025))
POINTS=(("Pacifico_sur_Lambayeque",-6.625,-80.625),
        ("Pacifico_norte_Lambayeque",-6.125,-80.625))
HEADER=("sitio_marino","mes","sst_media_c","n_dias","sst_anomalia_1996_2025_c",
        "latitud_oceanica","longitud_oceanica","valor_analizado_no_termometro")

def hash256(x):return hashlib.sha256(x).hexdigest()
def request(site,period):
    _,lat,lon=site;first,last=period
    dates=f"({first}-01-01T12:00:00Z):1:({last}-12-31T12:00:00Z)"
    grid=f"sst[{dates}][(0.0)][({lat})][({lon})]"
    return API+"?"+quote(grid,safe=":-.,0123456789TZW")

def paths(root,site,period):
    s=site[0];first,last=period
    stem=f"{s}_{first}_{last}"
    return root/DATA/"fuentes"/(stem+".csv.gz"),root/DATA/"fuentes"/(stem+".meta.json")

def validate(blob,site,period):
    try:
        raw=blob.decode("utf-8-sig")
        entries=list(csv.reader(io.StringIO(raw)))
    except UnicodeError as e:raise ValueError("SST NOAA no es CSV UTF-8") from e
    if not entries or entries[0]!=["time","zlev","latitude","longitude","sst"]:
        raise ValueError("NOAA SST sin encabezado griddap esperado")
    rows=entries[1:]
    if rows and rows[0][0].strip() in ("UTC","UTC (ISO 8601)"):rows=rows[1:]
    expected=common.dates(*period)
    if len(rows)!=len(expected):raise ValueError(f"No hay un valor SST diario por día de década: {len(rows)} vs {len(expected)}; primer={rows[0][:1] if rows else []}; ultimo={rows[-1][:1] if rows else []}")
    result={}
    for expected_date,row in zip(expected,rows):
        if len(row)!=5 or row[0][:10]!=expected_date or not row[0].endswith("Z"):
            raise ValueError("SST NOAA con días desordenados o duplicados")
        try:z,lat,lon,temp=map(float,row[1:])
        except (ValueError,TypeError) as e:raise ValueError("SST NOAA sin coordenadas/válidos") from e
        if (not all(map(math.isfinite,(z,lat,lon,temp))) or z!=0 or
            abs(lat-site[1])>.15 or abs(lon-site[2])>.15 or
            not -2.5<temp<38):
            raise ValueError("Dato SST inválido, máscara terrestre o celda distinta")
        result[expected_date]=temp
    return result

def load(root,site,period):
    rawpath,metapath=paths(root,site,period)
    if not rawpath.exists() and not metapath.exists():return None
    if not rawpath.exists() or not metapath.exists():
        raise ValueError("SST en archivo parcial sin trazabilidad")
    blob=gzip.decompress(rawpath.read_bytes())
    meta=json.loads(metapath.read_text(encoding="utf-8"))
    if (meta.get("fase")!="8U" or meta.get("origen")!=SOURCE or
        meta.get("url")!=request(site,period) or meta.get("sha256_original")!=hash256(blob) or
        meta.get("sitio")!=site[0] or meta.get("periodo")!=list(period)):
        raise ValueError("SST NOAA con SHA o geometría inconsistentes")
    return validate(blob,site,period)

def fetch(root,max_new=1):
    added=0
    for site in POINTS:
        for period in PERIODS:
            if load(root,site,period) is not None:continue
            if added>=max_new:return
            uri=request(site,period)
            try:
                with urlopen(Request(uri,headers={"User-Agent":"OAF-Lambayeque-8U-OSST/1.0"}),timeout=130) as response:
                    if response.status!=200:raise ValueError("SST NOAA HTTP inadecuado")
                    raw=response.read(2_500_001)
                if len(raw)>2_500_000:raise ValueError("SST supera 2,5 MB")
                clean=validate(raw,site,period)
            except HTTPError as exc:
                print("No se recupera SST: HTTP",exc.code,"No se inventan valores.");return
            except (ValueError,URLError,OSError,TimeoutError) as exc:
                print("No se recupera SST verificado:",str(exc));return
            path,meta=paths(root,site,period);path.parent.mkdir(parents=True,exist_ok=True)
            info={"fase":"8U","origen":SOURCE,"sitio":site[0],
                  "periodo":list(period),"url":uri,"sha256_original":hash256(raw),
                  "fecha_consulta_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "n_dias":len(clean),"no_sensor_individual":True,"mar_criterio_sst_finita":True,
                  "revision_retroactiva_posible":True}
            path.write_bytes(gzip.compress(raw,mtime=0))
            meta.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("SST oceánica validada:",site[0],period,len(clean),hash256(raw)[:12]);added+=1

def report(root):
    output=[];completed={};source_count=0;missing=[]
    for site in POINTS:
        days={}
        for period in PERIODS:
            sub=load(root,site,period)
            if sub is not None:
                source_count+=1
                days.update(sub)
            else:missing.append({"sitio":site[0],"bloque":list(period)})
        if len(days)==len(common.dates(1996,2025)):
            monthly=defaultdict(list)
            for date,v in sorted(days.items()):
                monthly[date[:7]].append(v)
            means={m:statistics.mean(vals) for m,vals in monthly.items()}
            clim={m:statistics.mean(val for dt,val in means.items() if int(dt[5:7])==m)
                  for m in range(1,13)}
            completed[site[0]]={"n_dias":len(days),"n_meses":len(means),
                    "sst_media_anual_c":round(statistics.mean(means.values()),3),
                    "sst_max_media_mensual_c":round(max(means.values()),3),
                    "sst_min_media_mensual_c":round(min(means.values()),3)}
            for month,mean in means.items():
                output.append({"sitio_marino":site[0],"mes":month,
                  "sst_media_c":round(mean,4),"n_dias":len(monthly[month]),
                  "sst_anomalia_1996_2025_c":round(mean-clim[int(month[5:7])],5),
                  "latitud_oceanica":site[1],"longitud_oceanica":site[2],
                  "valor_analizado_no_termometro":"true"})
    output.sort(key=lambda x:(x["sitio_marino"],x["mes"]))
    state={"fase":"8U","fuente":SOURCE,"periodo":"1996–2025",
       "puntos_oceanicos_de_ensayo":len(POINTS),"estaciones_mareas_o_marinas_instrumentales":0,
       "archivos_sst_verificados":source_count,"archivos_sst_previstos":len(POINTS)*3,
       "sitios_con_sst_30anios_completa":len(completed),
       "resumen_sst_oceanica":completed,
       "bloques_pendientes":missing,
       "n_meses_oceanicos_publicados":len(output),
       "coordenadas_marinas_pendientes_de_mascara_oficial":True,
       "sst_no_es_velocidad_de_corrientes":True,
       "sst_costera_no_es_promedio_indice_nino12":True,
       "normal_local_1996_2025_es_descriptiva_no_baseline_para_backtest":True,
       "no_hay_validacion_independiente_de_boyas_o_peru":True,
       "prediccion_oceanica_aun_no_probada":True,
       "fuente_agua_batimetrias_y_mascaras_verificadas":False,
       "nota":"Puntos oceánicos fijos sin comprobación oficial de máscara litoral, separados 0,5 grados; SST diaria OISST analizada, no sensor puntual."}
    return state,output

def savecsv(rows):
    buff=io.StringIO(newline="");writer=csv.DictWriter(buff,fieldnames=HEADER,lineterminator="\n")
    writer.writeheader();writer.writerows(rows);return buff.getvalue()

def publish(root,check=False):
    state,rows=report(root)
    base=root/DATA
    files={base/"estado_sst_8u.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
           base/"sst_mensual_8u.csv":savecsv(rows)}
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,val in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=val:
                raise ValueError("SST estado diferente al archivo fuente NOAA")
        elif not path.exists() or path.read_text(encoding="utf-8")!=val:
            path.write_text(val,encoding="utf-8")
    print(json.dumps({"fase":"8U","sst_bloques":state["archivos_sst_verificados"],
        "sitios_completos":state["sitios_con_sst_30anios_completa"],"check":check},ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--fetch",action="store_true");ap.add_argument("--check",action="store_true")
    ap.add_argument("--max-new",type=int,default=1);a=ap.parse_args()
    if a.fetch:fetch(a.root,a.max_new)
    publish(a.root,a.check)
