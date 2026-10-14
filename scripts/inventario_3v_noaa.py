"""OAF-Lambayeque | Fase 3V: inventario NOAA GHCN-Daily 2016–2025.

NO atribuye estaciones a Lambayeque por proximidad, ni las identifica con las
cinco series SENAMHI del OAF. La independencia de CHIRPS/PISCOp está pendiente.
Se consulta inventario PRCP y, cuando se consigue, observación diaria QC NOAA.
Solo se publican METADATOS/CONTADORES; no se sustituyen datos instrumentales.
"""
from __future__ import annotations
import csv
import datetime as dt
import io
import json
import math
import time
from collections import defaultdict, Counter
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
DATA.mkdir(exist_ok=True)
STATIONS={
 "Jayanca (La Viña)":(-6.322,-79.779),
 "Cayaltí":(-6.88079444,-79.54701389),
 "Reque":(-6.88613,-79.8355),
 "Lambayeque":(-6.73152778,-79.90983611),
 "Cueva Blanca":(-6.13130,-79.40450)
}
MAX_KM=160
MAX_REMOTE_CANDIDATES=25
URLS=[
 "https://www.ncei.noaa.gov/pub/data/ghcn/daily/",
 "https://noaa-ghcn-pds.s3.amazonaws.com/"
]
HEADERS={"User-Agent":"OAF-Lambayeque/1.5 scientific metadata validation"}
SESSION=requests.Session()
SESSION.headers.update(HEADERS)

def download(name,cache=False):
    problems=[]
    for base in URLS:
        url=base+name
        for retry in range(2):
            try:
                response=SESSION.get(url,timeout=(18,100))
                response.raise_for_status()
                content=response.content
                if not content or content[:100].lstrip().startswith(b"<html"):
                    raise ValueError("Contenido inesperado HTML/vacío")
                return url,content
            except (requests.RequestException,ValueError) as err:
                problems.append(f"{url}: {type(err).__name__}: {str(err)[:90]}")
                if retry==0:time.sleep(3)
    raise RuntimeError("Descarga imposible: "+" | ".join(problems)[-1100:])

def distance_km(lat1,lon1,lat2,lon2):
    p1,p2=map(math.radians,(lat1,lat2))
    dlat=p2-p1;dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(a)))

def parse_stations(raw):
    stations={}
    for line in raw.decode("latin-1").splitlines():
        try:
            sid=line[:11].strip()
            if len(sid)!=11 or not sid.startswith("PE"):continue
            lat=float(line[12:20]);lon=float(line[21:30])
            elev=line[31:37].strip();name=line[41:71].strip()
            if not (-90<=lat<=90 and -180<=lon<=180):continue
            closest=min((distance_km(lat,lon,*coord),target) for target,coord in STATIONS.items())
            if closest[0]>MAX_KM:continue
            stations[sid]={"id_ghcnd":sid,"nombre_noaa":name,
                "latitud":lat,"longitud":lon,"elevacion_m":elev,
                "distancia_punto_oaf_km":round(closest[0],2),
                "punto_oaf_mas_cercano":closest[1]}
        except (ValueError,TypeError):
            continue
    return stations

def parse_inventory(raw,candidates):
    for line in raw.decode("latin-1").splitlines():
        sid=line[:11].strip()
        if sid not in candidates or line[31:35].strip()!="PRCP":continue
        try:
            first=int(line[36:40]);last=int(line[41:45])
        except ValueError:
            continue
        current=candidates[sid]
        if current.get("inventario_prcp_inicio") is None or first<current["inventario_prcp_inicio"]:
            current["inventario_prcp_inicio"]=first
        if current.get("inventario_prcp_fin") is None or last>current["inventario_prcp_fin"]:
            current["inventario_prcp_fin"]=last
    return candidates

def check_daily(station_id):
    source,blob=download(f"csv/by_station/{station_id}.csv")
    parsed=csv.reader(io.StringIO(blob.decode("utf-8-sig",errors="replace")))
    days={};duplicates=0;bad_quality=0;out_of_range=0;head=0
    for row in parsed:
        if len(row)<7:continue
        if row[0].strip().upper() in ("ID","STATION"):
            head+=1;continue
        if row[0].strip()!=station_id or row[2].strip()!="PRCP":continue
        try:
            day=dt.datetime.strptime(row[1].strip(),"%Y%m%d").date()
            value=int(row[3].strip())
        except (ValueError,TypeError,IndexError):
            continue
        if not (2016<=day.year<=2025):
            out_of_range+=1;continue
        if day in days:
            duplicates+=1;continue
        # NOAA GHCN-Daily: PRCP tenths of mm; -9999 is missing.
        # Quality flag Q_FLAG: blank passes; any other value flagged invalid.
        qflag=row[5].strip()
        if value==-9999 or qflag or value<0:
            days[day]=None
            bad_quality+=1
        else:
            days[day]=value/10.0
    valid=sum(v is not None for v in days.values())
    fullmonths=0
    valid_years=set()
    for year in range(2016,2026):
        for month in range(1,13):
            ndays=(dt.date(year+month//12,month%12+1,1)-dt.date(year,month,1)).days
            coverage=[days.get(dt.date(year,month,d)) for d in range(1,ndays+1)]
            if all(v is not None for v in coverage):
                fullmonths+=1;valid_years.add(year)
    return {"url_datos_diarios_noaa":source,"dias_prcp_validos_2016_2025":valid,
        "meses_completos_2016_2025":fullmonths,
        "años_con_al_menos_un_mes_completo":",".join(map(str,sorted(valid_years))),
        "dias_flag_no_valido_o_sentinel":bad_quality,
        "registros_duplicados":duplicates,
        "descarga_diaria":"ok"}

def writecsv(path,rows,cols):
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def main():
    errors=[]
    try:
        stationurl,sdata=download("ghcnd-stations.txt")
        invurl,idata=download("ghcnd-inventory.txt")
        stations=parse_stations(sdata)
        stations=parse_inventory(idata,stations)
    except Exception as e:
        state={"fase":"3V","estado":"catalogo_no_disponible",
          "errores":[f"{type(e).__name__}: {str(e)[:900]}"],
          "independencia_confirmada":False,"nuevas_series_senamhi_incorporadas":0}
        (DATA/"estado_3v_noaa.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (ROOT/"INVENTARIO_3V_NOAA.md").write_text("# Inventario NOAA fase 3V\n\nSin descarga de inventario verificable; no se calcularon candidatos. Ver estado_3v_noaa.json.\n",encoding="utf-8")
        writecsv(DATA/"candidatos_3v_noaa.csv",[],["id_ghcnd","nombre_noaa","latitud","longitud","elevacion_m",
          "distancia_punto_oaf_km","punto_oaf_mas_cercano","inventario_prcp_inicio","inventario_prcp_fin",
          "dias_prcp_validos_2016_2025","meses_completos_2016_2025","descarga_diaria"])
        print(json.dumps(state,ensure_ascii=False),flush=True)
        raise SystemExit(1)
    sample=list(stations.values())
    for x in sample:
        x["inventario_abarca_2016_2025"]=(x.get("inventario_prcp_inicio",9999)<=2025 and x.get("inventario_prcp_fin",0)>=2016)
        x["descarga_diaria"]="no_evaluada"
        x["dias_prcp_validos_2016_2025"]=""
        x["meses_completos_2016_2025"]=""
    sample.sort(key=lambda x:(not x["inventario_abarca_2016_2025"],x["distancia_punto_oaf_km"]))
    for x in [s for s in sample if s["inventario_abarca_2016_2025"]][:MAX_REMOTE_CANDIDATES]:
        try:
            x.update(check_daily(x["id_ghcnd"]))
            print("DATOS",x["id_ghcnd"],x["nombre_noaa"],x["meses_completos_2016_2025"],"meses completos",flush=True)
        except Exception as exc:
            x["descarga_diaria"]="error"
            x["error_descarga"]=f"{type(exc).__name__}: {str(exc)[:190]}"
            errors.append({"id_ghcnd":x["id_ghcnd"],"error":x["error_descarga"]})
            print("ERROR",x["id_ghcnd"],str(exc)[:200],flush=True)
    cols=["id_ghcnd","nombre_noaa","latitud","longitud","elevacion_m",
      "distancia_punto_oaf_km","punto_oaf_mas_cercano","inventario_prcp_inicio","inventario_prcp_fin",
      "inventario_abarca_2016_2025","descarga_diaria","dias_prcp_validos_2016_2025",
      "meses_completos_2016_2025","años_con_al_menos_un_mes_completo","error_descarga",
      "url_datos_diarios_noaa"]
    writecsv(DATA/"candidatos_3v_noaa.csv",sample,cols)
    countdaily=sum(1 for x in sample if x["descarga_diaria"]=="ok")
    months=sum(int(x["meses_completos_2016_2025"]) for x in sample if x["descarga_diaria"]=="ok")
    state={"fase":"3V","estado":"inventario_descargado","fecha_revision":"2026-10-14",
      "inventario_estaciones_url":stationurl,"inventario_prcp_url":invurl,
      "fuente":"NOAA GHCN-Daily",
      "radio_de_busqueda_km":MAX_KM,
      "delimitacion_administrativa_validada":False,
      "candidatas_geograficas_total":len(sample),
      "candidatas_con_intervalo_inventario_PRCP_solapado_2016_2025":
        sum(int(x["inventario_abarca_2016_2025"]) for x in sample),
      "estaciones_con_archivo_diario_consultado":countdaily,
      "meses_completos_QC_en_archivos_diarios_NOAA":months,
      "errores":errors,
      "nuevas_series_senamhi_originales_incorporadas":0,
      "independencia_de_CHIRPS_o_PISCOp_demostrada":False,
      "estaciones_identificadas_con_los_TT_SENAMHI_del_proyecto":0,
      "advertencia":"Búsqueda por distancia, no por límite departamental. NOAA puede reciclar fuentes SENAMHI o GSOD; no certificar independencia ni misma estación por nombre o GPS."
    }
    (DATA/"estado_3v_noaa.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=["# OAF-Lambayeque | Fase 3V: estaciones NOAA GHCN-Daily próximas al área de estudio","",
      "> **Inventario exploratorio, NO red SENAMHI validada**. Radio de 160 km alrededor de cualquiera de cinco puntos del OAF.",
      "> La pertenencia departamental NO se conoce aquí; una estación de Cajamarca o Piura NO debe presentarse como ubicada en Lambayeque.",
      "> NOAA combina datos de redes nacionales y resúmenes GSOD; fuentes pueden no ser independientes de SENAMHI ni de productos interpolados.","",
      "## Conteos comprobados","",
      "- Candidatos en el radio geográfico: **"+str(len(sample))+"**.",
      "- Con periodo PRCP en inventario que se solapa con 2016–2025: **"+
        str(state["candidatas_con_intervalo_inventario_PRCP_solapado_2016_2025"])+"**.",
      "- Archivos diarios descargados y revisados: **"+str(countdaily)+"**.",
      "- Meses completos 2016–2025 en archivos diarios de candidatos consultados: **"+str(months)+"**.",
      "- Nuevas series SENAMHI originales incorporadas al OAF: **0**.","",
      "## Candidatos geográficos (solo inventario)","",
      "| Código NOAA | Nombre | Distancia mínima a un punto OAF (km) | PRCP primer año | PRCP último año | Meses completos 2016–2025 | Estado descarga |",
      "|---|---|---:|---:|---:|---:|---|"]
    for x in sample:
        report.append("| "+str(x["id_ghcnd"])+" | "+str(x["nombre_noaa"])+" | "+str(x["distancia_punto_oaf_km"])+
          " | "+str(x.get("inventario_prcp_inicio","Sin PRCP"))+
          " | "+str(x.get("inventario_prcp_fin","Sin PRCP"))+
          " | "+str(x["meses_completos_2016_2025"] if x["meses_completos_2016_2025"] != "" else "No comprobado")+" | "+
          str(x["descarga_diaria"])+" |")
    report+=["","## Interpretación técnica","",
      "- El inventario contiene rangos de años por elemento, que NO implican continuidad diaria ni meses completos.",
      "- Para cada candidato descargado se leyeron registros de precipitación PRCP, cuyos valores en GHCN-Daily están en décimas de mm; valores -9999 y Q_FLAG no vacío no se aceptaron.",
      "- Se consideran meses completos solo cuando los días calendario contienen valores diarios válidos.",
      "- Los datos NOAA pueden derivar de intercambio meteorológico o redes nacionales; antes de usarlos hay que identificar códigos, fuente (S_FLAG), zona horaria/día de medición y posibles coincidencias con las cinco estaciones históricas SENAMHI.",
      "- No se ha añadido ningún registro de NOAA a los totales SENAMHI 1996–2015 ni a una validación instrumental de 2016–2025.",
      "- No se ha evaluado pertenencia al territorio administrativo de Lambayeque, ni equivalencia de emplazamientos.","",
      "## Fuentes","",
      "- Inventario NOAA: "+stationurl+" y "+invurl,
      "- GHCN-Daily: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily",
      "- Descripción de archivos: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt",
      "- SENAMHI GBON/RBON: https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio",
      "- Código: scripts/inventario_3v_noaa.py",
      "- Inventario: datos/candidatos_3v_noaa.csv; estado: datos/estado_3v_noaa.json.",
      "",
      "**Próximo paso:** cotejar identidad y localización oficial con SENAMHI, y comprobar fuentes originales y series diarias más recientes antes de una prueba realmente independiente." ]
    if errors:
        report+=["","## Consultas diarias fallidas", ""]
        report.extend("- "+json.dumps(x,ensure_ascii=False) for x in errors)
    (ROOT/"INVENTARIO_3V_NOAA.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2),flush=True)
    return state
if __name__=="__main__":
    result=main()
    if result["errores"]:
        print("ADVERTENCIA: Algunas descargas diarias fallaron; no presentar cobertura completa.",flush=True)
