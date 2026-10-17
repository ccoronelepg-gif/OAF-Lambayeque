#!/usr/bin/env python3
"""Contraste estrictamente descriptivo de 3 archivos instrumentales OAF.

No establece distancia espacial, clima de zonas homogéneas, nombres de estaciones
ni habilidad predictiva. Fuente: salidas SHA verificadas de fase 9D.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "datos/estaciones_9d/series_mensuales_9d.csv"
AUDIT = ROOT / "datos/estaciones_9d/auditoria_estaciones_9d.json"
IDENTITY = ROOT / "datos/validacion_estaciones_9e/metadatos_identidad_9e.json"
OUT = ROOT / "datos/validacion_estaciones_9e/contraste_observacional_9e.json"
CODES = ("00000340", "00153114", "00152107")
YEARS = (1982, 1983, 1997, 1998, 2012, 2013)

def canonical(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"

def read_data():
    df = {}
    with SRC.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            code, month = r["codigo"], r["mes"]
            if code not in CODES:
                raise ValueError("Código no reconocido: " + code)
            if not len(month) == 7 or month[4] != "-":
                raise ValueError("Mes mal formado")
            key = (code, month)
            if key in df:
                raise ValueError("Observación mensual duplicada: " + str(key))
            days = int(r["dias_calendario"])
            coverage = int(r["precip_dias_validos"])
            if coverage > days or coverage < 0:
                raise ValueError("Cobertura fuera de rango")
            p = float(r["precip_total_mm"]) if r["precip_total_mm"] else None
            strict = days == coverage and p is not None
            if p is not None and p < 0:
                raise ValueError("Precipitación inválida")
            if strict and r["mes_precip_completo"] != "1":
                raise ValueError("Un mes estricto sin 90%")
            df[key] = {"rain": p, "strict": strict, "days": days,
                       "coverage": coverage, "mes": month}
    if len(df) != 1814:
        raise ValueError("Ingesta mensual 9D distinta: " + str(len(df)))
    return df

def correlation(a, b):
    if len(a) != len(b) or len(a) < 3:
        return None
    n = len(a)
    am, bm = sum(a)/n, sum(b)/n
    covariance = sum((x-am)*(y-bm) for x,y in zip(a,b))
    scatter1 = sum((x-am)**2 for x in a)
    scatter2 = sum((y-bm)**2 for y in b)
    if scatter1 <= 0 or scatter2 <= 0:
        return None
    return round(covariance/math.sqrt(scatter1*scatter2), 5)

def annual(df, code, year):
    ms=[df.get((code, f"{year:04}-{m:02}")) for m in range(1,13)]
    if any(x is None for x in ms):
        return {"anio": year, "meses_con_100pct_dias": sum(x is not None and x["strict"] for x in ms),
                "total_mm_estricto": None}
    n=sum(x["strict"] for x in ms)
    return {"anio": year, "meses_con_100pct_dias": n,
            "total_mm_estricto": round(sum(x["rain"] for x in ms),4) if n == 12 else None}

def summary():
    df=read_data()
    audit=json.loads(AUDIT.read_text(encoding="utf8"))
    identity=json.loads(IDENTITY.read_text(encoding="utf8"))
    if [x["codigo"] for x in audit["estaciones"]] != list(CODES):
        raise ValueError("El inventario 9D cambió")
    if [x["codigo_archivo"] for x in identity["estaciones"]] != list(CODES):
        raise ValueError("Identificadores de estación desordenados")
    if any(x.get("certificado") or x.get("latitud") is not None or
           x.get("longitud") is not None for x in identity["estaciones"]):
        # La fase 9E no debe convertir silenciosamente un cambio de metadatos
        # en habilidad espacial: haría falta una validación de procedencia separada.
        raise ValueError("Cambió el estado documental; validar fuente y actualizar protocolo de emparejamiento.")
    stations=[]
    for code in CODES:
        period = [df.get((code,f"{y:04}-{m:02}")) for y in range(1996,2014) for m in range(1,13)]
        if any(x is None for x in period):
            raise ValueError("Faltan fechas 1996–2013")
        stations.append({
            "codigo_archivo":code,"n_meses_1996_2013":len(period),
            "meses_lluvia_100pct":sum(x["strict"] for x in period),
            "meses_lluvia_90pct":sum(x["rain"] is not None for x in period),
            "anios_ejemplo_100pct":[annual(df,code,y) for y in YEARS],
            "anios_1996_2013_100pct":[annual(df,code,y) for y in range(1996,2014)]
        })
    pairs=[]
    for i in range(len(CODES)):
        for j in range(i+1,len(CODES)):
            a,b=CODES[i],CODES[j]
            matches=[]
            for y in range(1996,2014):
                for m in range(1,13):
                    mon=f"{y:04}-{m:02}"
                    ra,rb=df[(a,mon)],df[(b,mon)]
                    if ra["strict"] and rb["strict"]:
                        matches.append((mon,ra["rain"],rb["rain"]))
            xx=[x[1] for x in matches]
            yy=[x[2] for x in matches]
            wet=[x for x in matches if int(x[0][-2:]) in (1,2,3,4)]
            pairs.append({
                "codigo_a":a,"codigo_b":b,"periodo":"1996-01 a 2013-12",
                "meses_comunes_100pct":len(matches),
                "correlacion_lluvia_mensual_cruda":correlation(xx,yy),
                "correlacion_log1p_lluvia_mensual":correlation([math.log1p(x) for x in xx],[math.log1p(x) for x in yy]),
                "enero_abril_meses_comunes_100pct":len(wet),
                "correlacion_log1p_enero_abril":correlation([math.log1p(x[1]) for x in wet],[math.log1p(x[2]) for x in wet]),
                "no_implica_cercania_espacial":True,
                "no_indica_capacidad_predictiva":True
            })
    result={
        "fase":"9E","fecha_revision":"2026-10-17",
        "dictamen":"contraste_observacional_temporal_descriptivo; contraste_grilla_bloqueado_por_falta_de_metadatos",
        "fuente":"datos/estaciones_9d/series_mensuales_9d.csv",
        "cobertura_exigida":"100% de días para análisis de precipitación estricta y años completos; se conserva indicador 90% de 9D separado",
        "tres_estaciones_certificadas":False,
        "comparacion_directa_era5_chirps_ejecutada":False,
        "razon_de_bloqueo":"No existen coordenadas, altitud, código oficial y día pluviométrico verificados que permitan emparejar archivos con rejillas científicamente.",
        "restricciones":[
            "Correlación descriptiva entre series codificadas, no homogeneidad espacial ni clima de pisos altitudinales.",
            "Lluvia 1983/1998 es registro instrumental histórico sin demostrar pronóstico emitido previamente.",
            "La ingestión no valida calidad de extremos, cambios de instrumento ni derechos de republicación.",
            "CHIRPS incluye pluviómetros potencialmente coincidentes con estaciones de referencia: la comparación podría no ser estrictamente independiente.",
            "ERA5 tiene distintos soportes y horarios; no convertir reanálisis en estación medida."
        ],
        "estaciones":stations,
        "pares":pairs
    }
    assert len(stations)==3 and len(pairs)==3
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=summary()
    output=canonical(data)
    if args.check:
        if OUT.read_text(encoding="utf8")!=output:
            raise SystemExit("Fase 9E: salida no coincide con entradas archivadas.")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(output,encoding="utf8")
    print("9E: 3 series, 3 contrastes temporales, 1996–2013, metadatos no acreditados; no se generó falsa comparación ERA5/CHIRPS.")
    for p in data["pares"]:
        print(p["codigo_a"],p["codigo_b"],"n=",p["meses_comunes_100pct"],"log1p=",p["correlacion_log1p_lluvia_mensual"])

if __name__=="__main__":
    main()
