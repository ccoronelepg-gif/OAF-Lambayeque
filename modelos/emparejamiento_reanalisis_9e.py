#!/usr/bin/env python3
"""Validador geoespacial de estaciones y reanalisis: fase 9E del OAF.

No descarga datos externos ni presupone estaciones conocidas.
Activacion manual REQUIERE metadatos institucionales documentados antes del
emparejamiento y registros georreferenciados procedentes de fuentes reales.

Formato de la muestra geoespacial CSV:
 codigo_archivo,mes,producto,version,lat_celda,lon_celda,precipitacion_mm,
 disponibilidad_utc,fuente_url
- producto: CHIRPS-v3-final o ERA5-Land
- producto/version/unidades deben acreditar la extraccion y su calendario
- No confundir errores frente a estaciones con validacion predictiva.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IDENTITY=ROOT/"datos/validacion_estaciones_9e/metadatos_identidad_9e.json"
STATION=ROOT/"datos/estaciones_9d/series_mensuales_9d.csv"
ALLOWED={
    "CHIRPS-v3-final":{"max_center_distance_km":8.5},
    "ERA5-Land":{"max_center_distance_km":17.0}
}
REQUIRED=("codigo_archivo","mes","producto","version","lat_celda",
          "lon_celda","precipitacion_mm","disponibilidad_utc","fuente_url")
def haversine(lat1,lon1,lat2,lon2):
    r=6371.0
    la1,la2=math.radians(lat1),math.radians(lat2)
    dl=math.radians(lat2-lat1)
    dg=math.radians(lon2-lon1)
    x=math.sin(dl/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dg/2)**2
    return r*2*math.asin(min(1.0,math.sqrt(x)))

def approved_metadata(data):
    if not data.get("estaciones"):
        raise ValueError("No existen fichas de estacion")
    approved={}
    for r in data["estaciones"]:
        code=r["codigo_archivo"]
        if code in approved:
            raise ValueError("Identificador repetido "+code)
        if not r.get("certificado") or r.get("estado")!="identidad_confirmada":
            raise ValueError("La estacion "+code+" carece de identidad institucional documentada")
        for key in ("nombre","codigo_oficial","operador","url_ficha","fecha_verificacion","metodo_coincidencia"):
            if not isinstance(r.get(key),str) or not r[key].strip():
                raise ValueError("Metadato ausente: "+code+"/"+key)
        if not r["url_ficha"].startswith("https://"):
            raise ValueError("La ficha debe tener URL segura")
        # La propia URL NO demuestra una coincidencia: revisión humana con prueba
        # documental sigue siendo requisito previo al cambio de estado.
        coords=[r.get("latitud"),r.get("longitud"),r.get("altitud_m")]
        if any(v is None or not isinstance(v,(float,int)) or not math.isfinite(v) for v in coords):
            raise ValueError("Coordenadas/altitud incompletas en "+code)
        if not -18.5<coords[0]<-3.0 or not -82<coords[1]<-68 or not -500<coords[2]<7000:
            raise ValueError("La localizacion no es plausible para Perú")
        approved[code]=r
    return approved

def records_from_station(file):
    df={}
    with file.open(encoding="utf8",newline="") as f:
        for r in csv.DictReader(f):
            key=(r["codigo"],r["mes"])
            if key in df:
                raise ValueError("Duplicado en registro de estación")
            if r["precip_total_mm"] and int(r["dias_calendario"])==int(r["precip_dias_validos"]):
                df[key]=float(r["precip_total_mm"])
    return df

def evaluate(inputfile, metadata):
    approved=approved_metadata(metadata)
    observed=records_from_station(STATION)
    byproduct=defaultdict(list)
    seen=set()
    with inputfile.open(encoding="utf8",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames is None or any(key not in reader.fieldnames for key in REQUIRED):
            raise ValueError("Columnas geoespaciales ausentes")
        for row in reader:
            code=row["codigo_archivo"]
            if code not in approved:
                raise ValueError("Estacion sin metadatos aprobados: "+code)
            product=row["producto"]
            if product not in ALLOWED:
                raise ValueError("Producto no acreditado: "+product)
            month=row["mes"]
            if len(month)!=7 or month[4]!="-":
                raise ValueError("Mes no reconocido")
            key=(code,month,product)
            if key in seen:raise ValueError("Prediccion duplicada: "+str(key))
            seen.add(key)
            if not row["version"].strip() or not row["fuente_url"].startswith("https://"):
                raise ValueError("Version y URL del producto obligatorias")
            if not row["disponibilidad_utc"].strip():
                raise ValueError("Sin huella de disponibilidad temporal")
            try:
                datetime.fromisoformat(row["disponibilidad_utc"].replace("Z","+00:00"))
            except ValueError as e:
                raise ValueError("Fecha de disponibilidad incorrecta") from e
            lat,lon=float(row["lat_celda"]),float(row["lon_celda"])
            val=float(row["precipitacion_mm"])
            if not all(math.isfinite(x) for x in [lat,lon,val]) or val<0:
                raise ValueError("Valores climatologicos inválidos")
            station=approved[code]
            distance=haversine(station["latitud"],station["longitud"],lat,lon)
            if distance>ALLOWED[product]["max_center_distance_km"]:
                raise ValueError("Celda demasiado lejos de estacion "+code+
                                 ": "+str(round(distance,2))+" km")
            if (code,month) in observed:
                byproduct[(code,product)].append((month,observed[(code,month)],val))
    scores=[]
    for (code,product), pairs in sorted(byproduct.items()):
        n=len(pairs)
        if not n:continue
        diff=[model-obs for _,obs,model in pairs]
        abs_error=[abs(x) for x in diff]
        mse=sum(x*x for x in diff)/n
        scores.append({
            "codigo_archivo":code,"producto":product,"n_meses_estrictos":n,
            "mes_inicial":min(x[0] for x in pairs),"mes_final":max(x[0] for x in pairs),
            "mae_mm":round(sum(abs_error)/n,6),
            "sesgo_modelo_menos_estacion_mm":round(sum(diff)/n,6),
            "rmse_mm":round(math.sqrt(mse),6),
            "calificacion":"contraste retrospectivo de producto grillado vs observacion; no pronostico",
            "habilidad_predictiva_operativa":False,
        })
    return {
        "fase":"9E","tipo":"contraste_reanalisis_a_estaciones_con_ficha",
        "n_pares":sum(x["n_meses_estrictos"] for x in scores),
        "metricas":scores,
        "dependencia_chirps":"Cuidado: CHIRPS v3 incluye observaciones de pluviómetros; posible validación no independiente.",
        "latencia":"Disponibilidad de archivo no demuestra vintage histórico del pronóstico.",
        "prediccion_operativa_validada":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--grid",type=Path)
    p.add_argument("--metadata",type=Path,default=IDENTITY)
    p.add_argument("--salida",type=Path)
    a=p.parse_args()
    meta=json.loads(a.metadata.read_text(encoding="utf8"))
    approved_metadata(meta)  # fail-closed incluso sin archivo grillado
    if a.grid is None:
        raise SystemExit("Metadatos disponibles; falta archivo grillado validado --grid.")
    output=evaluate(a.grid,meta)
    text=json.dumps(output,indent=2,ensure_ascii=False)+"\n"
    if a.salida:a.salida.write_text(text,encoding="utf8")
    else:print(text)
if __name__=="__main__":
    main()
