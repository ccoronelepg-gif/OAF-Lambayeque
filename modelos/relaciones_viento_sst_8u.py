#!/usr/bin/env python3
"""8U: asociaciones DESCRIPTIVAS entre viento ERA5 y Niño1+2 SST NOAA.

Usa exclusivamente originales archivados, sin descargar: viento diario ERA5
(4 localidades, 1996–2025) e índice NOAA Niño1+2 (360 meses). Compara
anomalía de viento 10m por MES CALENDARIO con SST contemporánea y t−2.
No prueba causalidad, ni habilidad predictiva ni viento sobre océano.
"""
from __future__ import annotations
import argparse,csv,io,json,math,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import viento_oceano_8u as wind
import contraste_oceanico_8t as ocean
ROOT=Path(__file__).resolve().parents[1]
BASE="datos/relaciones_viento_sst_8u"
COLUMNS=("localidad","mes","anomalia_viento_10m_ms",
    "anomalia_sst_nino12_actual_c","anomalia_sst_nino12_t_2_c",
    "componente_u_10m_aproximada_ms","componente_v_10m_aproximada_ms",
    "fuentes_instrumentales_independientes")

def pearson(a,b):
    if len(a)!=len(b) or len(a)<12:return None
    aa=statistics.mean(a);bb=statistics.mean(b)
    x=[t-aa for t in a];y=[t-bb for t in b]
    xx=sum(z*z for z in x);yy=sum(z*z for z in y)
    return None if xx<=1e-12 or yy<=1e-12 else sum(q*r for q,r in zip(x,y))/math.sqrt(xx*yy)

def lag_month(name,lag=2):
    year,mon=map(int,name.split("-"))
    order=year*12+mon-1-lag
    return f"{order//12:04d}-{order%12+1:02d}"

def build(root):
    status,windmonths=wind.run(root)
    if status["bloques_viento_obtenidos"]!=3 or len(windmonths)!=1440:
        raise ValueError("8U necesita 360 meses de viento de cuatro centros")
    sst,meta=ocean.archive(root)
    if len(sst)!=360:raise ValueError("Niño1+2 no tiene historial completo")
    dates=[f"{y}-{m:02d}" for y in range(1996,2026) for m in range(1,13)]
    rows=[];summary=[]
    for locality in wind.LOCATIONS:
        sub={r["mes"]:r for r in windmonths if r["localidad"]==locality}
        if sorted(sub)!=dates:raise ValueError("Viento sin 360 meses ordenados por localidad")
        normal={m:statistics.mean(sub[f"{y}-{m:02d}"]["viento_10m_media_ms"] for y in range(1996,2026))
                for m in range(1,13)}
        this=[]
        for month in dates:
            lag=lag_month(month)
            this.append({"localidad":locality,"mes":month,
                "anomalia_viento_10m_ms":round(sub[month]["viento_10m_media_ms"]-normal[int(month[-2:])],6),
                "anomalia_sst_nino12_actual_c":sst[month]["nino12_anom_c"],
                "anomalia_sst_nino12_t_2_c":sst[lag]["nino12_anom_c"] if lag in sst else "",
                "componente_u_10m_aproximada_ms":sub[month]["componente_zonal_aproximada_ms"],
                "componente_v_10m_aproximada_ms":sub[month]["componente_meridional_aproximada_ms"],
                "fuentes_instrumentales_independientes":"false"})
        v=[x for x in this if x["anomalia_sst_nino12_t_2_c"]!=""]
        def correlated(key,index="anomalia_sst_nino12_t_2_c",items=v):
            result=pearson([x[key] for x in items],[x[index] for x in items])
            return round(result,5) if result is not None else None
        summary.append({"localidad":locality,"n_meses_contemporaneos":360,
           "n_meses_rezago_2":len(v),
           "r_anomalia_viento_sst_mismo_mes":correlated("anomalia_viento_10m_ms",
                  "anomalia_sst_nino12_actual_c",this),
           "r_anomalia_viento_sst_menos_2":correlated("anomalia_viento_10m_ms"),
           "r_componente_u_aproximada_sst_menos_2":correlated("componente_u_10m_aproximada_ms"),
           "r_componente_v_aproximada_sst_menos_2":correlated("componente_v_10m_aproximada_ms")})
        rows.extend(this)
    if len(rows)!=1440:raise ValueError("Faltan meses de comparación")
    return {"fase":"8U","estado":"asociacion_descriptiva_1996_2025_sin_pronostico",
       "periodo":"1996–2025","n_comparaciones":len(rows),
       "n_fuentes_viento_era5_archivadas":3,"n_fuentes_sst_noaa":1,
       "sha256_noaa_sst":meta["sha256_original"],
       "referencia_normales_viento_1996_2025":"solo_descriptiva",
       "localidades":summary,
       "corrientes_marinas_vectoriales_utilizadas":False,
       "el_indice_sst_no_mide_corrientes":True,
       "mismo_mes_no_es_predictor_ex_ante":True,
       "sst_rezagada_no_demuestra_predictibilidad":True,
       "correlacion_descriptiva_no_demuestra_causalidad":True,
       "datos_senamhi_instrumentales_independientes":False,
       "habilidad_predictiva_validada":False,
       "mascara_mar_y_viento_maritimo_en_puntos_regionales_verificados":False,
       "advertencias":[
          "Anomalías de viento normalizadas 1996–2025 usan datos posteriores a cada fecha; SOLO para diagnóstico, no entrenar un backtest con ellas.",
          "Niño1+2 NOAA es SST regional, no temperatura local de Lambayeque.",
          "El viento ERA5 proviene de cuadrícula terrestre y no mide forzamiento oceánico sobre agua.",
          "La misma climatología y reanálisis pueden contener autocorrelación y tendencias; no se aplican pruebas de significación aquí.",
          "Ninguna variable u/v de corrientes marinas reales se ha usado en los cálculos.",
          "Para modelos pronóstico ex ante, recalcular normales y parámetros exclusivamente con datos anteriores al periodo de prueba."
       ]},rows

def csvtext(rows):
    b=io.StringIO(newline="");w=csv.DictWriter(b,fieldnames=COLUMNS,lineterminator="\n")
    w.writeheader();w.writerows(rows);return b.getvalue()

def publish(root,check=False):
    state,rows=build(root)
    base=root/BASE
    outputs={base/"estado_relaciones_8u.json":json.dumps(state,ensure_ascii=False,indent=2)+"\n",
       base/"comparaciones_mensuales_8u.csv":csvtext(rows)}
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,val in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=val:
                raise ValueError("Diagnóstico 8U no reproduce archivos meteorológicos/NOAA")
        elif not path.exists() or path.read_text(encoding="utf-8")!=val:
            path.write_text(val,encoding="utf-8")
    print(json.dumps({"fase":"8U","meses":len(rows),
        "localidades":len(state["localidades"]),"check":check},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args();publish(args.root,args.check)
