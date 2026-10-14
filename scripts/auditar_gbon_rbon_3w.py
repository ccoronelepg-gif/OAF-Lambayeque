"""OAF-Lambayeque Fase 3W: auditoría horaria GBON/RBON.
Datos públicos SENAMHI, CSV de 46 MB. No publica observaciones horarias.
Conteos de meses completos solo PRELIMINARES, no acumulados certificados:
periodo de integración de PP / horas de observación requieren diccionario oficial.
"""
from __future__ import annotations
import calendar,collections,csv,datetime as dt,io,json,math,re,unicodedata
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
DATA.mkdir(exist_ok=True)
URL="https://www.datosabiertos.gob.pe/sites/default/files/Variables%20Meteorologicas%20de%20las%20Estaciones%20autom%C3%A1ticas%20de%20intercambio%20internacional%20-%20%5BServicio%20Nacional%20de%20Meteorolog%C3%ADa%20e%20Hidrolog%C3%ADa%20del%20Per%C3%BA%20-%20SENAMHI%5D.csv"
CATALOG="https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio"
POINTS={"Jayanca":(-6.322,-79.779),"Cayaltí":(-6.88079444,-79.54701389),
 "Reque":(-6.88613,-79.8355),"Lambayeque":(-6.73152778,-79.90983611),
 "Cueva Blanca":(-6.1313,-79.4045)}
def normal(s):
    return "".join(c for c in unicodedata.normalize("NFKD",str(s or "").lower()) if c.isascii() and c.isalnum())
def number(x):
    s=str(x or "").strip().replace(" ","")
    if s.upper() in ("","NAN","NA","NULL","-99.9","-999","-9999","S/D","SIN DATO"):return None
    try:
        v=float(s.replace(",","."))
        return v if math.isfinite(v) else None
    except ValueError:return None
def dateparse(s):
    val=str(s or "").strip()
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%Y/%m/%d","%d-%m-%Y","%Y%m%d"):
        try:return dt.datetime.strptime(val,fmt).date()
        except ValueError:pass
    return None
def hourparse(s):
    val=str(s or "").strip()
    m=re.fullmatch(r"([01]?\d|2[0-3])(?::[0-5]\d){0,2}",val)
    if m:return int(m.group(1))
    return None
def distkm(a,b,c,d):
    x,y=math.radians(a),math.radians(c)
    da=y-x
    db=math.radians(d-b)
    h=math.sin(da/2)**2+math.cos(x)*math.cos(y)*math.sin(db/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(h)))
def csvwrite(name,rows,headers):
    with (DATA/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def main():
    state={"fase":"3W","estado":"pendiente","origen":URL,"fuente_catalogo":CATALOG,
       "archivo_verificado_en_prueba_previa":True,
       "fecha_modificacion_del_catalogo":"2025-09-08",
       "fecha_del_archivo_no_inferida_por_fecha_catalogo":True,
       "registros_nuevos_2016_2025_certificados":0,
       "estaciones_identificadas_con_cinco_txt_historicos":0,
       "independencia_de_productos_probada":False,
       "errores":[]}
    stations={}
    hourly=collections.defaultdict(set)
    dayrows=collections.Counter()
    invalid=collections.Counter()
    nrows=0;globalmin=None;globalmax=None
    try:
        with requests.get(URL,timeout=(25,160),headers={"User-Agent":"Mozilla/5.0 OAF-Lambayeque/3W Scientific Audit"}) as resp:
            resp.raise_for_status()
            # El CSV público ocupa ~46 MB: primero cargarlo íntegramente,
            # y luego analizarlo para evitar cierres prematuros del stream HTTP.
            payload=resp.content
            state["bytes_descargados"]=len(payload)
            reader=csv.DictReader(io.StringIO(payload.decode("utf-8-sig",errors="replace"),newline=""))
            headers=reader.fieldnames
            required={"ID","ESTACION","FECHA","HORA","LONGITUD","LATITUD","PP","RED","DEPARTAMENTO"}
            if not headers or not required.issubset(set(headers)):
                raise ValueError("Encabezados incompatibles: "+repr(headers))
            state["columnas"]=headers
            for row in reader:
                nrows+=1
                day=dateparse(row["FECHA"])
                if day is None:
                    invalid["fecha_no_interpretable"]+=1
                    continue
                daystr=day.isoformat()
                globalmin=min(globalmin,daystr) if globalmin else daystr
                globalmax=max(globalmax,daystr) if globalmax else daystr
                ident=str(row["ID"] or "").strip()
                name=str(row["ESTACION"] or "").strip()
                depart=str(row["DEPARTAMENTO"] or "").strip()
                lat,lon=number(row["LATITUD"]),number(row["LONGITUD"])
                if not name or lat is None or lon is None or not(-90<=lat<=90 and -180<=lon<=180):
                    invalid["estacion_o_coordenada_no_valida"]+=1;continue
                distances=[(distkm(lat,lon,*xy),point) for point,xy in POINTS.items()]
                nearest,point=min(distances)
                if normal(depart)!="lambayeque" and nearest>160:continue
                key=(ident,name,lat,lon,depart)
                if key not in stations:
                    stations[key]={
                        "id_publicado":ident,"nombre":name,"departamento":depart,
                        "provincia":str(row.get("PROVINCIA","") or "").strip(),
                        "distrito":str(row.get("DISTRITO","") or "").strip(),
                        "ubigeo":str(row.get("UBIGEO","") or "").strip(),
                        "red":str(row.get("RED","") or "").strip(),
                        "latitud":lat,"longitud":lon,
                        "altitud_m":number(row.get("ALTITUD")),
                        "punto_oaf_cercano":point,"distancia_minima_km":round(nearest,2),
                        "filas_horarias":0,"horas_precipitacion_validas_2016_2025":0,
                        "fecha_min":None,"fecha_max":None,"meses_horarios_completos_provisionales":0
                    }
                st=stations[key]
                st["filas_horarias"]+=1
                st["fecha_min"]=min(st["fecha_min"],daystr) if st["fecha_min"] else daystr
                st["fecha_max"]=max(st["fecha_max"],daystr) if st["fecha_max"] else daystr
                if not 2016<=day.year<=2025:continue
                hour=hourparse(row["HORA"])
                rain=number(row["PP"])
                daykey=(key,day)
                dayrows[daykey]+=1
                if hour is None:
                    invalid["hora_no_interpretable"]+=1;continue
                if rain is None or rain<0:
                    invalid["precipitacion_horaria_no_valida"]+=1;continue
                if hour in hourly[daykey]:
                    invalid["hora_duplicada"]+=1;continue
                hourly[daykey].add(hour)
                st["horas_precipitacion_validas_2016_2025"]+=1
                if rain>200:invalid["pp_horaria_mayor_200mm_revisar"]+=1
        gooddays=collections.Counter()
        for (key,day),hours in hourly.items():
            if len(hours)==24 and dayrows[(key,day)]==24:
                gooddays[(key,day.year,day.month)]+=1
        months=collections.Counter()
        for (key,year,month),nd in gooddays.items():
            if nd==calendar.monthrange(year,month)[1]:
                months[key]+=1
        items=[]
        for key,st in stations.items():
            st["meses_horarios_completos_provisionales"]=months[key]
            items.append(st)
        items.sort(key=lambda s:(normal(s["departamento"])!="lambayeque",
            -s["meses_horarios_completos_provisionales"],s["nombre"]))
        state.update({"estado":"completo_con_limitaciones",
            "filas_csv_examinadas":nrows,
            "fecha_min_global":globalmin,"fecha_max_global":globalmax,
            "num_estaciones_candidatas_160km_o_lambayeque":len(items),
            "num_estaciones_declaradas_lambayeque":sum(normal(x["departamento"])=="lambayeque" for x in items),
            "meses_horarios_completos_provisionales":sum(x["meses_horarios_completos_provisionales"] for x in items),
            "incidencias_horarias":dict(invalid)})
    except Exception as e:
        state.update({"estado":"error_acceso_o_formato","filas_csv_examinadas":nrows,
            "fecha_min_global":globalmin,"fecha_max_global":globalmax})
        state["errores"].append({"error":type(e).__name__+": "+str(e)[:600]})
        items=[]
    fields=["id_publicado","nombre","departamento","provincia","distrito","ubigeo","red",
        "latitud","longitud","altitud_m","punto_oaf_cercano","distancia_minima_km",
        "filas_horarias","horas_precipitacion_validas_2016_2025",
        "meses_horarios_completos_provisionales","fecha_min","fecha_max"]
    csvwrite("estaciones_gbon_rbon_3w.csv",items,fields)
    (DATA/"estado_3w.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=["# OAF-Lambayeque | Fase 3W: auditoría horaria SENAMHI GBON/RBON","",
      "> Inventario y cobertura temporal observada: NO es validación independiente ni equivalencia con las cinco estaciones históricas.",
      "> Para series horarias, el número de horas presentes NO certifica automáticamente totales mensuales de lluvia.",
      "## Estado de la descarga y cobertura","",
      "- Ejecución: "+state["estado"]+".",
      "- CSV origen: "+URL,
      "- Filas analizadas: "+str(state.get("filas_csv_examinadas",0))+".",
      "- Primer registro fechado: "+str(state.get("fecha_min_global"))+".",
      "- Último registro fechado: "+str(state.get("fecha_max_global"))+".",
      "- Estaciones candidatas por departamento declarado o radio 160 km: "+str(len(items))+".",
      "- Meses con conteo de horas completo (preliminares): "+str(state.get("meses_horarios_completos_provisionales",0))+".",
      "- Nuevos meses de lluvia SENAMHI certificados e incorporados: **0**.","",
      "## Estaciones candidatas (metadatos del archivo, no identidad instrumental certificada)","",
      "| ID del archivo | Estación | Departamento declarado | Red | Horas válidas 2016–2025 | Meses de 24 horas/día completos (provisionales) |",
      "|---|---|---|---|---:|---:|"]
    for x in items:
        report.append("| "+str(x["id_publicado"])+" | "+x["nombre"]+" | "+x["departamento"]+
             " | "+x["red"]+" | "+str(x["horas_precipitacion_validas_2016_2025"])+
             " | "+str(x["meses_horarios_completos_provisionales"])+" |")
    report+=["","## Límites y próximos pasos","",
      "- La fecha de actualización de la ficha del dataset no garantiza que el CSV incluya el año 2025.",
      "- La cobertura en el archivo puede ser de pocos meses o años aunque aparezca un inventario nacional.",
      "- El archivo utiliza FECHA, HORA, PP; se requiere consultar el diccionario para definir el periodo al que corresponde PP, huso horario y horario de acumulación.",
      "- Se ha contado un día como completo solo con 24 horas distintas y 24 filas con precipitación válida; un mes, solo con todos los días completos. Las fechas con horas duplicadas/ausentes no pasan el control.",
      "- Que una estación tenga el mismo nombre que otra no demuestra identidad de serie, continuidad histórica, ni independencia de PISCOp o CHIRPS.",
      "- No se sumó precipitación ni se alteró la validación instrumental 1996–2015; solo se publican conteos y metadatos agregados.",
      "- La pertenencia administrativa se transcribe del campo DEPARTAMENTO, y la búsqueda por 160 km también puede incluir Cajamarca, Piura y La Libertad.",
      "- Fuente: "+CATALOG,
      "- Código reproducible: scripts/auditar_gbon_rbon_3w.py",""]
    if state["errores"]:
        report+=["","## Incidencias",""]
        report.extend("- "+json.dumps(x,ensure_ascii=False) for x in state["errores"])
    (ROOT/"AUDITORIA_3W_GBON_RBON.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print("FIN",json.dumps({k:state.get(k) for k in ["estado","filas_csv_examinadas","fecha_min_global","fecha_max_global","num_estaciones_candidatas_160km_o_lambayeque","meses_horarios_completos_provisionales"]},ensure_ascii=False),flush=True)
    if state["estado"]!="completo_con_limitaciones":raise SystemExit(1)
if __name__=="__main__":
    main()
