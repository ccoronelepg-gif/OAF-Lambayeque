#!/usr/bin/env python3
"""8U: viento 10m ERA5 histórico 1996–2025 en 4 localidades OAF, auditado.

Módulo descriptivo de viento mensual (dirección meteorológica 'desde')
y relaciones con SST Niño1+2 NOAA revisado. No mide corrientes oceánicas.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,statistics,io,time
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import perfiles_climaticos_8o as oaf
import contraste_oceanico_8t as ocean
ROOT=Path(__file__).resolve().parents[1]
BASE="datos/viento_8u"
BLOCKS=((1996,2005),(2006,2015),(2016,2025))
LOCATIONS=("Chiclayo","Jayanca","Motupe","Olmos")
FIELDS=("localidad","mes","viento_10m_media_ms","viento_10m_max_diario_prom_ms",
        "componente_zonal_aproximada_ms","componente_meridional_aproximada_ms",
        "direccion_resultante_desde_grados","dias_validos","celda_era5")
VARS=("wind_speed_10m_mean","wind_speed_10m_max","wind_direction_10m_dominant")

def hashdata(x):return hashlib.sha256(x).hexdigest()
def locations(root):
    with (root/"datos/sensibilidad_vecindad_8m/puntos_8m.csv").open(encoding="utf-8-sig",newline="") as f:
        data=list(csv.DictReader(f))
    result=[]
    for town in LOCATIONS:
        matching=[r for r in data if r["localidad"]==town and r["direccion"]=="C"]
        if len(matching)!=1 or matching[0]["n_meses"]!="360":
            raise ValueError("Centro geográfico previo 8M incompleto: "+town)
        x=matching[0]
        result.append({"id":town,"latitud":float(x["latitud_solicitada"]),
                       "longitud":float(x["longitud_solicitada"])})
    return result

def request(block,coords):
    start,end=block
    return oaf.API+"?"+urlencode({
        "latitude":",".join(str(p["latitud"]) for p in coords),
        "longitude":",".join(str(p["longitud"]) for p in coords),
        "start_date":f"{start}-01-01","end_date":f"{end}-12-31",
        "timezone":"America/Lima","daily":",".join(VARS),
        "models":"era5","cell_selection":"land","wind_speed_unit":"ms"})

def paths(root,block):
    start,end=block;stem=f"era5_viento_{start}_{end}"
    return root/BASE/"fuentes"/(stem+".json.gz"),root/BASE/"fuentes"/(stem+".meta.json")

def validate(blob,block,points):
    payload=json.loads(blob)
    if not isinstance(payload,list) or len(payload)!=len(points):
        raise ValueError("Respuesta ERA5 sin cuatro localidades")
    expected=oaf.dates(*block)
    for point,obj in zip(points,payload):
        if obj.get("error") or obj.get("timezone")!="America/Lima" or obj.get("utc_offset_seconds")!=-18000:
            raise ValueError("Respuesta viento ERA5 con error o huso horario distinto")
        d=obj.get("daily") or {}
        if d.get("time")!=expected:raise ValueError("Serie de viento ERA5 con fechas incompletas")
        u=obj.get("daily_units") or {}
        if u.get("wind_speed_10m_mean") not in ("m/s","ms") or u.get("wind_speed_10m_max") not in ("m/s","ms"):
            raise ValueError("Unidad viento ERA5 no es m/s")
        if u.get("wind_direction_10m_dominant") not in ("°","deg"):
            raise ValueError("Dirección ERA5 sin grados")
        if not all(isinstance(obj.get(k),(int,float)) and math.isfinite(obj[k])
                   for k in ("latitude","longitude","elevation")):
            raise ValueError("Coordenadas de celda ERA5 ausentes")
        if abs(obj["latitude"]-point["latitud"])>.5 or abs(obj["longitude"]-point["longitud"])>.5:
            raise ValueError("La celda ERA5 está demasiado distante")
        for key in VARS:
            seq=d.get(key)
            if not isinstance(seq,list) or len(seq)!=len(expected):
                raise ValueError("Variable diaria de viento ausente")
            if any(type(x) not in (int,float) or not math.isfinite(x) for x in seq):
                raise ValueError("Viento nulo o no numérico")
        for mn,mx,angle in zip(d[VARS[0]],d[VARS[1]],d[VARS[2]]):
            if not(0<=mn<=80 and mn<=mx+.11 and 0<=mx<100 and 0<=angle<=360):
                raise ValueError("Viento o dirección diaria fuera de rango")
    return payload

def verify(root,block,points):
    file,meta=paths(root,block)
    if not file.exists() and not meta.exists():return None
    if not file.exists() or not meta.exists():raise ValueError("Fuente ERA5 viento parcialmente almacenada")
    blob=gzip.decompress(file.read_bytes())
    info=json.loads(meta.read_text(encoding="utf-8"))
    if(info.get("fase")!="8U" or info.get("url")!=request(block,points) or
       info.get("periodo")!=list(block) or info.get("sha256_original")!=hashdata(blob) or
       info.get("localidades")!=list(LOCATIONS)):
        raise ValueError("Fuente ERA5 viento sin cadena de identidad SHA")
    return validate(blob,block,points)

def fetch(root,max_new=1):
    points=locations(root);created=0
    for block in BLOCKS:
        if verify(root,block,points) is not None:continue
        if created>=max_new:return
        url=request(block,points)
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-8U-wind-climate/1.0"}),timeout=150) as r:
                if r.status!=200:raise ValueError("Viento ERA5 HTTP inesperado")
                blob=r.read(19_000_001)
            if len(blob)>19_000_000:raise ValueError("ERA5 viento supera tamaño máximo")
            validate(blob,block,points)
        except HTTPError as exc:
            if exc.code==429:
                print("Cuota API 429; fuente viento pendiente sin rellenar.");return
            print("Fallo de viento HTTP:",exc.code);return
        except (OSError,ValueError,TimeoutError) as exc:
            print("Fuente de viento no verificable:",str(exc));return
        path,meta=paths(root,block);path.parent.mkdir(parents=True,exist_ok=True)
        info={"fase":"8U","url":url,"periodo":list(block),
              "sha256_original":hashdata(blob),"localidades":list(LOCATIONS),
              "consultado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "modelo":"ERA5 vía Open-Meteo","reanalisis_no_estacion":True,
              "direccion_es_de_donde_sopla":True,
              "vector_a_partir_de_media_diaria_y_dominante_es_aproximado":True}
        path.write_bytes(gzip.compress(blob,mtime=0))
        meta.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        created+=1
        print("Viento ERA5 bloque verificado",block,hashdata(blob)[:16])

def csv_text(rows):
    b=io.StringIO(newline="")
    w=csv.DictWriter(b,fieldnames=FIELDS,lineterminator="\n")
    w.writeheader();w.writerows(rows)
    return b.getvalue()

def run(root):
    coords=locations(root);data={}
    present=[]
    for block in BLOCKS:
        obj=verify(root,block,coords)
        if obj is not None:
            present.append(list(block))
            for point,archive in zip(coords,obj):
                buckets=defaultdict(list)
                d=archive["daily"]
                for k,date in enumerate(d["time"]):
                    speed=float(d[VARS[0]][k]);maximum=float(d[VARS[1]][k])
                    angle=math.radians(float(d[VARS[2]][k]))
                    # meteorological heading FROM converted to zonal/meridional TOWARDS
                    u=-speed*math.sin(angle);v=-speed*math.cos(angle)
                    buckets[date[:7]].append((speed,maximum,u,v))
                for ym,records in buckets.items():
                    key=(point["id"],ym)
                    if key in data:raise ValueError("Mes de viento duplicado")
                    u=statistics.mean(r[2] for r in records)
                    v=statistics.mean(r[3] for r in records)
                    heading=(math.degrees(math.atan2(-u,-v))+360)%360
                    data[key]={"localidad":point["id"],"mes":ym,
                      "viento_10m_media_ms":round(statistics.mean(r[0] for r in records),4),
                      "viento_10m_max_diario_prom_ms":round(statistics.mean(r[1] for r in records),4),
                      "componente_zonal_aproximada_ms":round(u,4),
                      "componente_meridional_aproximada_ms":round(v,4),
                      "direccion_resultante_desde_grados":round(heading,2),
                      "dias_validos":len(records),
                      "celda_era5":f"{archive['latitude']:.5f};{archive['longitude']:.5f}"}
    rows=[data[key] for key in sorted(data)]
    full=len(present)==3 and len(rows)==len(coords)*360
    aggregate=[]
    for name in LOCATIONS:
        same=[r for r in rows if r["localidad"]==name]
        if full:
            aggregate.append({"localidad":name,"viento_media_ms":round(statistics.mean(r["viento_10m_media_ms"] for r in same),3),
              "viento_max_diario_prom_ms":round(statistics.mean(r["viento_10m_max_diario_prom_ms"] for r in same),3),
              "dias_totales":sum(r["dias_validos"] for r in same),
              "meses":len(same),"n_centros_era5_distintos":len({r["celda_era5"] for r in same})})
    # NOAA has a separate SST series - it is NOT an ocean current.
    ocean_ready=False;ocean_hash=None;sst_stats=None
    try:
        index,metadata=ocean.archive(root)
        ocean_ready=True;ocean_hash=metadata["sha256_original"]
        sst_stats={"nino12_anom_mean_c":round(statistics.mean(r["nino12_anom_c"] for r in index.values()),4),
                   "nino12_anom_min_c":min(r["nino12_anom_c"] for r in index.values()),
                   "nino12_anom_max_c":max(r["nino12_anom_c"] for r in index.values())}
    except (ValueError,OSError):pass
    report={"fase":"8U","estado":"viento_historico_completo" if full else "viento_historico_parcial",
      "periodo":"1996–2025","localidades":list(LOCATIONS),
      "bloques_viento_obtenidos":len(present),"bloques_viento_previstos":3,
      "periodos_archivados":present,"meses_localidad_obtenidos":len(rows),
      "testigos_viento_historico_completos":len(aggregate),
      "resumen_viento_por_localidad":aggregate,
      "unidad_velocidad_viento":"m/s","direccion_de_donde_sopla":True,
      "componentes_vectoriales_aproximadas_con_promedios_diarios":True,
      "indices_sst_noaa_1996_2025_archivados":ocean_ready,
      "sha256_sst_noaa":ocean_hash,"resumen_sst_nino12":sst_stats,
      "corrientes_marinas_serie_historica_verificada":False,
      "corrientes_marinas_fuente_validada":None,
      "corrientes_no_inferibles_del_viento_ni_del_SST":True,
      "datos_no_son_observaciones_senamhi":True,
      "modelo_predictivo_viento_corriente_ya_validado":False,
      "riesgo_fitosanitario_validado":False,
      "zonas_homogeneas_certificadas":0,
      "fuentes_propuestas_para_corrientes":[
        {"institucion":"NASA PO.DAAC","producto":"OSCAR_L4_OC_FINAL_V2.0",
         "url":"https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0",
         "variables":"u,v m/s, velocidad superficial por análisis satelital, 0,25°",
         "periodo_catalogo":"1993–2026 (consultar cobertura final y acceso)",
         "descarga_y_QA_1996_2025":False,
         "acceso_puede_requerir_Earthdata_Login":True},
        {"institucion":"Copernicus Marine","producto":"GLOBAL_MULTIYEAR_PHY_001_030",
         "url":"https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description",
         "variables":"eastward_sea_water_velocity, northward_sea_water_velocity",
         "periodo_catalogo":"desde 1993, observar profundidad y máscara costera",
         "descarga_y_QA_1996_2025":False,
         "requiere_subconjunto_NetCDF":True}],
      "advertencias":[
         "Puntos regionales son centros 8M, no estaciones ni parcelas instrumentadas.",
         "Dirección dominante diaria y velocidad media diaria construyen componentes aproximadas, no viento vectorial horario promedio físico exacto.",
         "Temperatura del mar NOAA Niño1+2 representa promedio de amplia región marina, no SST frente a Santa Rosa/Pimentel directamente.",
         "El antiguo ERDDAP jplOscar etiquetado 1992-presente en octubre 2026 solo tiene cobertura 2011-12 a 2014-09; NO usarlo como serie 30 años.",
         "Velocidad y dirección de corrientes oceánicas requieren productos u/v y máscara agua; no es legítimo derivarlas de SST.",
         "Sin corrientes reales, no se prueba modelo viento+SST+corrientes ni su habilidad prospectiva.",
         "No se declara relación causal entre viento y anomalía marina por correlación descriptiva."
      ]}
    return report,rows

def publish(root,check=False):
    state,rows=run(root);base=root/BASE
    out={base/"estado_factores_8u.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
         base/"viento_mensual_8u.csv":csv_text(rows)}
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,content in out.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("Reporte de viento 8U no reproduce las fuentes con SHA")
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8U","bloques":state["bloques_viento_obtenidos"],
          "meses":len(rows),"localidades_completas":state["testigos_viento_historico_completos"],
          "corrientes_verificadas":False,"check":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--max-new",type=int,default=1)
    p.add_argument("--check",action="store_true")
    o=p.parse_args()
    if o.fetch:fetch(o.root,o.max_new)
    publish(o.root,o.check)
