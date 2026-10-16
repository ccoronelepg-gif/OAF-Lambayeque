#!/usr/bin/env python3
"""OAF 8K: correspondencia espacial exploratoria sin declarar validación.

Identifica puntos de estudio 8D, estaciones históricas de *lluvia* 8H y
coordenadas de celdas que Open-Meteo pueda devolver en una consulta
independiente. La selección real de celda USADA en 8D no quedó archivada:
una respuesta reconstruida en 8K no prueba identidad con ella.
Python >=3.11, sin librerías externas ni acceso a red.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import io
import json
import math
from decimal import Decimal,ROUND_HALF_UP
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse,parse_qs

BASE=Path(__file__).resolve().parents[1]
SOURCE_SCRIPT="modelos/benchmark_impacto_regional_8d.py"
STATIONS="datos/catalogo_instrumental_candidato_8h.csv"
CANDIDATES="datos/candidatas_termometricas_documentales_8k.csv"
AUDIT="datos/auditoria_instrumental_8h/estaciones_8h.csv"
CELLS="datos/metadatos_celdas_openmeteo_8k.csv"
TEMP8I="datos/homologacion_temperatura_8i/estado_8i.json"
TEMP8J="datos/homologacion_horaria_8j/estado_8j.json"
OUT="datos/seleccion_espacial_8k"
SITES=("Chiclayo","Jayanca","Motupe","Olmos")
SOURCE_SITES_8D={
 "Chiclayo":(-6.77140,-79.84090),
 "Jayanca":(-6.39278,-79.82280),
 "Motupe":(-6.15083,-79.71420),
 "Olmos":(-5.98825,-79.74723)
}
STATION_FIELDS=(
  "estacion","latitud_consultada","longitud_consultada",
  "latitud_candidata_publicada","longitud_candidata_publicada",
  "altitud_publicada_m","variable_archivo_historico",
  "codigo_instrumental_verificado","continuidad_emplazamiento_verificada",
  "identidad_con_serie_txt_verificada","referencia_documental","observacion")
CANDIDATE_FIELDS=(
 "estacion_mencionada","tipo_evidencia","variable_publicada",
 "fuente_institucional","serie_diaria_obtenida",
 "codigo_instrumental_historico_confirmado",
 "coordenadas_del_sensor_correspondientes_al_periodo_confirmadas",
 "identidad_con_archivos_8h_confirmada","elegible_validacion_instrumental","observacion")
CELL_FIELDS=(
  "localidad_oaf","latitud_solicitada","longitud_solicitada",
  "latitud_respuesta","longitud_respuesta","elevacion_respuesta_m",
  "tipo_elevacion","modelo_solicitado","seleccion_celda","fecha_muestra",
  "fecha_consulta_utc","url_consulta","fuente_documentacion","sha256_respuesta",
  "metadatos_celda_8d_originales_verificados")
ATLAS_FIELDS=(
  "localidad_oaf","latitud_solicitada","longitud_solicitada",
  "nodo_teorico_red_0_1_lat","nodo_teorico_red_0_1_lon",
  "nodo_teorico_distancia_km","celda_devuelta_por_openmeteo_lat",
  "celda_devuelta_por_openmeteo_lon","distancia_solicitud_celda_devuelta_km",
  "elevacion_reportada_openmeteo_m","significado_elevacion_openmeteo",
  "estado_celda_8d_original","estaciones_termometricas_confirmadas")
RANK_FIELDS=(
  "localidad_oaf","estacion_historica","variante_coordenada",
  "latitud_candidata","longitud_candidata","distancia_a_punto_oaf_km",
  "distancia_a_celda_openmeteo_8k_km","separacion_variantes_estacion_km",
  "altitud_estacion_documental_m","meses_historicos_lluvia_completos",
  "variable_archivo_historico","codigo_instrumental_confirmado",
  "identidad_serie_historica_confirmada","estacion_termometrica_verificada",
  "apta_validacion_temperatura","clase_seleccion",
  "fuente_documental")
DOC_URL="https://open-meteo.com/en/docs/historical-weather-api"

def hashfile(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path,fields):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=list(fields):
            raise ValueError("CSV con esquema incompatible "+str(path))
        return list(reader)

def finite(s,blank=False):
    if s=="" and blank:return None
    try:v=float(s)
    except (ValueError,TypeError):raise ValueError("Valor no numérico: "+str(s)) from None
    if not math.isfinite(v):raise ValueError("Número no finito")
    return v

def latlon(lat,lon):
    if lat<-90 or lat>90 or lon<-180 or lon>180:
        raise ValueError("Coordenada fuera del globo")

def haversine(a,b,c,d):
    latlon(a,b);latlon(c,d)
    p=math.pi/180
    v=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(v)))

def boolval(v):
    if v not in ("true","false"):raise ValueError("Bandera de verificación no reconocida")
    return v=="true"

def sites_from_8d(root):
    code=ast.parse((root/SOURCE_SCRIPT).read_text(encoding="utf-8"))
    hits=[v for n in code.body if isinstance(n,ast.Assign)
          for t in n.targets if isinstance(t,ast.Name) and t.id=="SITES"
          for v in [ast.literal_eval(n.value)]]
    if len(hits)!=1 or hits[0]!=SOURCE_SITES_8D or list(hits[0])!=list(SITES):
        raise ValueError("Las coordenadas originales 8D no coinciden con la fase 8K")
    for pair in hits[0].values():
        if len(pair)!=2:raise ValueError("Par de coordenadas 8D inválido")
        latlon(*pair)
    return hits[0]

def lattice_nearest(x):
    # Nodo geométrico candidato en malla 0,1°; NO es el píxel retornado.
    return float((Decimal(str(x))*10).quantize(Decimal("1"),rounding=ROUND_HALF_UP)/10)

def inspect_cells(root,sites):
    rows=read_csv(root/CELLS,CELL_FIELDS)
    cells={}
    for row in rows:
        site=row["localidad_oaf"]
        if site not in sites or site in cells:raise ValueError("Celda duplicada/localidad no reconocida")
        requested=(finite(row["latitud_solicitada"]),finite(row["longitud_solicitada"]))
        reported=(finite(row["latitud_respuesta"]),finite(row["longitud_respuesta"]))
        latlon(*requested);latlon(*reported)
        if any(abs(x-y)>0.000001 for x,y in zip(requested,sites[site])):
            raise ValueError("Coordenadas de solicitud no reproducen el estudio 8D")
        if haversine(*requested,*reported)>150:
            raise ValueError("Píxel proveedor demasiado alejado para revisarse")
        elevation=finite(row["elevacion_respuesta_m"])
        if not -500<=elevation<=7000:raise ValueError("Elevación respuesta fuera de rango")
        if row["tipo_elevacion"]!="altura_reportada_api_no_orografia_era5_verificada":
            raise ValueError("La elevación de la API no equivale al relieve del píxel")
        if row["modelo_solicitado"]!="era5_land" or row["seleccion_celda"]!="land":
            raise ValueError("Parámetros de modelo 8D no reproducidos")
        if row["fecha_muestra"]!="2020-07-01":
            raise ValueError("La muestra metadata no es la de 8K")
        stamped=datetime.fromisoformat(row["fecha_consulta_utc"].replace("Z","+00:00"))
        if stamped.tzinfo is None or stamped.utcoffset().total_seconds()!=0:
            raise ValueError("Fecha de consulta sin UTC")
        if not row["fuente_documentacion"].startswith("https://open-meteo.com/"):
            raise ValueError("Documentación proveedor desconocida")
        url=urlparse(row["url_consulta"])
        q=parse_qs(url.query)
        if url.scheme!="https" or url.netloc!="archive-api.open-meteo.com" or url.path!="/v1/archive":
            raise ValueError("URL de consulta ajena a Open-Meteo")
        for param,expected in (
          ("latitude",str(sites[site][0])),("longitude",str(sites[site][1])),
          ("models","era5_land"),("cell_selection","land"),("timezone","America/Lima"),
          ("start_date","2020-07-01"),("end_date","2020-07-01"),
          ("daily","temperature_2m_mean")):
            if q.get(param)!=[expected]:
                raise ValueError("Parámetros API no reproducibles: "+param)
        if not __import__("re").fullmatch("[0-9a-f]{64}",row["sha256_respuesta"]):
            raise ValueError("No hay huella de respuesta API")
        if boolval(row["metadatos_celda_8d_originales_verificados"]):
            raise ValueError("Una consulta nueva 8K NO certifica el píxel de la extracción 8D")
        cells[site]={"lat":reported[0],"lon":reported[1],"elev":elevation,
                     "date":row["fecha_consulta_utc"],"url":row["url_consulta"]}
    return cells

def load_stations(root):
    stations=read_csv(root/STATIONS,STATION_FIELDS)
    audit=read_csv(root/AUDIT,(
      "estacion","meses_completos_precipitacion","primer_mes","ultimo_mes",
      "anios_completos","ultimo_anio_completo",
      "latitud_referencia_no_certificada","longitud_referencia_no_certificada",
      "alternativa_publicada_disponible","diferencia_posiciones_km",
      "punto_oaf_provisional_mas_cercano","distancia_referencial_km",
      "altitud_publicada_m","serie_temperatura_t2m_instrumental_verificada",
      "codigo_instrumental_verificado","historial_emplazamiento_verificado",
      "identidad_serie_txt_verificada","apto_contraste_8e_temperatura","fuente_metadatos"))
    audit_index={r["estacion"]:r for r in audit}
    if len(stations)!=5 or len(audit_index)!=5 or len(audit)!=5 or {s["estacion"] for s in stations}!=set(audit_index):
        raise ValueError("Estaciones instrumentales de 8H incompletas/duplicadas")
    out=[]
    for r in stations:
        site=r["estacion"]
        if r["variable_archivo_historico"]!="precipitacion_mm":
            raise ValueError("No existe historial térmico en el catálogo original")
        a=audit_index[site]
        if a["serie_temperatura_t2m_instrumental_verificada"]!="false" or a["apto_contraste_8e_temperatura"]!="false":
            raise ValueError("8H informa temperatura o aptitud no corroborada")
        p=(finite(r["latitud_consultada"]),finite(r["longitud_consultada"]))
        latlon(*p)
        altlat=finite(r["latitud_candidata_publicada"],True)
        altlon=finite(r["longitud_candidata_publicada"],True)
        if (altlat is None)!=(altlon is None):
            raise ValueError("Variante de ubicación incompleta")
        candidate=(altlat,altlon) if altlat is not None else None
        if candidate:latlon(*candidate)
        for flag in ("codigo_instrumental_verificado","continuidad_emplazamiento_verificada","identidad_con_serie_txt_verificada"):
            if boolval(r[flag]):raise ValueError("Catálogo inicial sin certificación; actualizar el protocolo antes de aprobar")
        if not r["referencia_documental"].startswith("https://"):
            raise ValueError("Estación sin fuente documental")
        months=int(a["meses_completos_precipitacion"])
        if months<1 or months>240:raise ValueError("Conteo de lluvia histórico inválido")
        out.append({"name":site,"point":p,"alternate":candidate,
                    "alt":finite(r["altitud_publicada_m"],True),
                    "months":months,"source":r["referencia_documental"]})
    return out

def documentary_thermometric_candidates(root):
    rows=read_csv(root/CANDIDATES,CANDIDATE_FIELDS)
    if len(rows)<5 or len({r["estacion_mencionada"].casefold() for r in rows})!=len(rows):
        raise ValueError("Inventario documental de temperatura ausente o duplicado")
    for r in rows:
        if r["variable_publicada"]!="Tmax_y_Tmin" or r["tipo_evidencia"]!="boletin_climatico_direccion_zonal_2":
            raise ValueError("No confundir boletines Tmax/Tmin con series diarias Tmedia")
        if not r["fuente_institucional"].startswith("https://www.senamhi.gob.pe/load/file/"):
            raise ValueError("Fuente de estación termométrica no institucional")
        for flag in ("serie_diaria_obtenida","codigo_instrumental_historico_confirmado",
                     "coordenadas_del_sensor_correspondientes_al_periodo_confirmadas",
                     "identidad_con_archivos_8h_confirmada","elegible_validacion_instrumental"):
            if boolval(r[flag]):
                raise ValueError("La mención en un boletín no certifica una serie diaria")
    return rows

def ensure_not_termometric(root):
    for filename,key in ((TEMP8I,"n_estaciones_con_fuente"),(TEMP8J,"estaciones_fuente_autorizada")):
        val=json.loads((root/filename).read_text(encoding="utf-8"))
        if val.get(key,0)!=0:
            # Esta fase compara catálogos ya verificados; el ingreso nuevo debe
            # investigarse primero por procedimientos 8I/8J, no mezclarse aquí.
            raise ValueError("Hay instrumentos térmicos incorporados: reauditar catálogo antes de publicar 8K")

def build(root):
    sites=sites_from_8d(root)
    cells=inspect_cells(root,sites)
    station_list=load_stations(root)
    candidates=documentary_thermometric_candidates(root)
    ensure_not_termometric(root)
    atlas=[]
    ranked=[]
    for city,(lat,lon) in sites.items():
        nearest=(lattice_nearest(lat),lattice_nearest(lon))
        provider=cells.get(city)
        dprov=round(haversine(lat,lon,provider["lat"],provider["lon"]),3) if provider else None
        atlas.append(dict(
            localidad_oaf=city,latitud_solicitada=lat,longitud_solicitada=lon,
            nodo_teorico_red_0_1_lat=nearest[0],nodo_teorico_red_0_1_lon=nearest[1],
            nodo_teorico_distancia_km=round(haversine(lat,lon,*nearest),3),
            celda_devuelta_por_openmeteo_lat=provider["lat"] if provider else None,
            celda_devuelta_por_openmeteo_lon=provider["lon"] if provider else None,
            distancia_solicitud_celda_devuelta_km=dprov,
            elevacion_reportada_openmeteo_m=provider["elev"] if provider else None,
            significado_elevacion_openmeteo="API: elevación de estadística/downscaling, NO altitud de píxel 8D"
              if provider else "sin consulta proveedor confirmada",
            estado_celda_8d_original="no_almacenada_en_la_emision_original_8d",
            estaciones_termometricas_confirmadas=0))
        for station in station_list:
            p=station["point"];q=station["alternate"]
            discrepancy=round(haversine(*p,*q),3) if q else None
            for label,point in (("coordenada_analisis_8h",p),("alternativa_documental_no_confirmada",q)):
                if point is None:continue
                ranked.append(dict(
                    localidad_oaf=city,estacion_historica=station["name"],
                    variante_coordenada=label,latitud_candidata=point[0],
                    longitud_candidata=point[1],
                    distancia_a_punto_oaf_km=round(haversine(*point,lat,lon),3),
                    distancia_a_celda_openmeteo_8k_km=round(haversine(*point,provider["lat"],provider["lon"]),3) if provider else None,
                    separacion_variantes_estacion_km=discrepancy,
                    altitud_estacion_documental_m=station["alt"],
                    meses_historicos_lluvia_completos=station["months"],
                    variable_archivo_historico="precipitacion_mm",
                    codigo_instrumental_confirmado=False,
                    identidad_serie_historica_confirmada=False,
                    estacion_termometrica_verificada=False,
                    apta_validacion_temperatura=False,
                    clase_seleccion="referencia_geografica_historica_lluvia_no_apta_para_verificar_temperatura",
                    fuente_documental=station["source"]))
    ranked.sort(key=lambda v:(v["localidad_oaf"],v["distancia_a_punto_oaf_km"],v["estacion_historica"],v["variante_coordenada"]))
    report={
      "fase":"8K",
      "tipo":"auditoria_de_correspondencia_espacial_y_catalogo",
      "estaciones_documentales_historicas_lluvia":len(station_list),
      "estaciones_con_tmax_tmin_en_boletin_senamhi":len(candidates),
      "series_diarias_termometricas_descargadas":0,
      "variantes_de_coordenadas_estacion":sum(1+bool(s["alternate"]) for s in station_list),
      "localidades_oaf":len(sites),
      "respuestas_geograficas_proveedor_8k":len(cells),
      "coordenadas_celda_8d_originales_verificadas":0,
      "estaciones_termometricas_confirmadas":0,
      "pares_termicos_instrumentales_era5_confirmados":0,
      "validez_predictiva_8e_demostrada":False,
      "validacion_espacial_independiente":False,
      "punto_informe":"El nodo red 0,1° es hipotético. La celda retornada por Open-Meteo 8K no certifica el píxel efectivamente usado al generar los datos 8D.",
      "advertencias":[
       "El catálogo existente incluye solo cinco estaciones históricas de lluvia; no refleja la totalidad de estaciones SENAMHI de Lambayeque.",
       "La proximidad de una estación no acredita sus mediciones de temperatura, código oficial o ubicación del sensor durante el periodo evaluado.",
       "La API Open-Meteo selecciona celdas según terreno/costa (land por defecto); valores de elevación API no equivalen automáticamente a orografía ERA5-Land.",
       "El dataset 8D usa temperatura ERA5-Land y radiación/lluvia ERA5. No atribuir a todas las variables la misma rejilla.",
       "Repetir consulta 8K no garantiza reproducir versión original ni la selección espacial del proveedor en 8D.",
       "Las coordenadas OAF son localidades de referencia, no predios productores ni ubicaciones de instrumentos.",
       "El siguiente contraste térmico exige instrumentos SENAMHI con Tmedia válida y geometría/periodos corroborados."
      ],
      "fuentes":{
        "senamhi":"https://www.senamhi.gob.pe/servicios/?p=estaciones",
        "era5_land":"https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land",
        "openmeteo_api":DOC_URL
      },
      "trazabilidad":{
        "modelo_8d_sha256":hashfile(root/SOURCE_SCRIPT),
        "catalogo_instrumental_8h_sha256":hashfile(root/STATIONS),
        "boletin_candidatas_senamhi_sha256":hashfile(root/CANDIDATES),
        "auditoria_estaciones_8h_sha256":hashfile(root/AUDIT),
        "metadatos_proveedor_8k_sha256":hashfile(root/CELLS),
        "informe_8i_sha256":hashfile(root/TEMP8I),
        "informe_8j_sha256":hashfile(root/TEMP8J)
      }
    }
    return report,atlas,ranked

def csv_output(rows,fields):
    dest=io.StringIO(newline="")
    writer=csv.DictWriter(dest,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k:"" if row.get(k) is None else str(row[k]).lower() if isinstance(row[k],bool) else row[k] for k in fields})
    return dest.getvalue()

def publish(root,check=False):
    report,atlas,ranked=build(root)
    out=root/OUT
    nearest=[]
    for city in SITES:
        by_station={}
        for entry in ranked:
            if entry["localidad_oaf"]==city:
                name=entry["estacion_historica"]
                if name not in by_station:
                    by_station[name]=entry
        nearest.extend(list(by_station.values())[:2])
    view={
        "fase":"8K",
        "indicadores":report,
        "localidades":atlas,
        "estaciones_historicas_lluvia_cercanas":nearest,
        "candidatas_termometricas_documentadas":[{
          "nombre":row["estacion_mencionada"],
          "evidencia":"Tmax y Tmin en un boletín institucional, NO serie diaria",
          "serie_instrumental_tmedia_obtenida":False,
          "fuente":row["fuente_institucional"]
        } for row in candidates]
    }
    files={
      out/"vista_8k.json":json.dumps(view,ensure_ascii=False,indent=2,allow_nan=False)+"\\n",
      out/"estado_8k.json":json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
      out/"localidades_celdas_8k.csv":csv_output(atlas,ATLAS_FIELDS),
      out/"proximidad_estaciones_8k.csv":csv_output(ranked,RANK_FIELDS)
    }
    if not check:out.mkdir(parents=True,exist_ok=True)
    for path,text in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=text:
                raise ValueError("Recalcular reporte 8K: "+str(path))
        elif not path.exists() or path.read_text(encoding="utf-8")!=text:
            path.write_text(text,encoding="utf-8")
    print(json.dumps({
      "fase":"8K","respuestas_proveedor":report["respuestas_geograficas_proveedor_8k"],
      "estaciones_lluvia_documentadas":report["estaciones_documentales_historicas_lluvia"],
      "instrumentos_termometricos_aprobados":report["estaciones_termometricas_confirmadas"],
      "reproducible":check},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=BASE)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    publish(a.root,a.check)
