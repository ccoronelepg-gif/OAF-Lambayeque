#!/usr/bin/env python3
"""OAF-Lambayeque phase 8B: do CPC atmosphere indices add predictive skill?

Target: OAF-rebased NOAA NCEI ERSSTv5 Niño1+2 monthly anomaly (NOT ENFEN ICEN).
Atmosphere at *origin month*: NOAA CPC SOI standardized and 850-hPa
trade-wind ANOMALIES central/eastern equatorial Pacific.
Models: persistence, fixed-alpha ridge SST-only, fixed-alpha ridge SST+3
atmospheric predictors, evaluation origins >=2010-01. Walk-forward expanding
train includes only labels known as of the forecast origin (train origin + h
<= current origin). Never train using a future target.
Caveat: retrospective CPC index files are revised and are NOT vintage-as-of
archives. No prospective validation or operational ENSO classification.
"""
import argparse
import csv
import json
import math
import random
import re
import statistics as st
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path("datos")
TARGET=ROOT/"noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv"
CPC={
    "soi_estandarizado":("https://www.cpc.ncep.noaa.gov/data/indices/soi","STANDARDIZED    DATA",1951),
    "alisios_pacifico_central":("https://www.cpc.ncep.noaa.gov/data/indices/cpac850","ANOMALY",1979),
    "alisios_pacifico_oriental":("https://www.cpc.ncep.noaa.gov/data/indices/epac850","ANOMALY",1979)
}
PREDICTORS=list(CPC)
HORIZONS=(1,2,3)
FIRST_ORIGIN="2010-01"
MIN_TRAIN=120
MIN_FOLDS=120
ALPHA=20.0
NUM=re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)")
OUT=ROOT/"benchmark_atmosferico_8b.json"
SAMPLE=ROOT/"benchmark_atmosferico_8b_fold.csv"
ATM=ROOT/"noaa_cpc_predictores_atmosfericos_8b.csv"


def shift(month,n):
    y,m=map(int,month.split("-"))
    z=y*12+(m-1)+n
    return f"{z//12:04d}-{z%12+1:02d}"


def parse_cpc(text, marker, first_year):
    """Select correct CPC section; parse joined -999.9 and 2027-999.9 columns."""
    lines=text.splitlines()
    at=-1
    for i,line in enumerate(lines):
        if marker.replace(" ","") in line.upper().replace(" ",""):
            at=i
            break
    if at<0:raise ValueError("CPC header marker missing: "+marker)
    header=next((i for i in range(at,min(len(lines),at+12))
                 if re.search(r"\bYEAR\b.*\bJAN\b",lines[i].upper())),None)
    if header is None:raise ValueError("CPC yearly data header missing: "+marker)
    result={}
    read=0
    for line in lines[header+1:]:
        value=line.strip()
        if not re.match(r"^(?:19|20)\d{2}",value):
            if read>0:break
            continue
        year=int(value[:4])
        if year<first_year or year>2100:raise ValueError("Unexpected CPC year "+str(year))
        nums=[float(v) for v in NUM.findall(value[4:])]
        if len(nums)!=12:
            raise ValueError("CPC year "+str(year)+" contains "+str(len(nums))+" months, not twelve")
        for m,number in enumerate(nums,start=1):
            if number<=-900:continue
            if not math.isfinite(number) or abs(number)>100:
                raise ValueError("CPC atmosphere value out of range")
            k=f"{year:04d}-{m:02d}"
            if k in result:raise ValueError("Duplicate CPC month "+k)
            result[k]=number
        read+=1
    if len(result)<400:raise ValueError("CPC atmosphere series too short: "+str(len(result)))
    period=[d for d in sorted(result) if "1991-01"<=d<="2025-12"]
    if len(period)!=420:raise ValueError("Atmosphere series incomplete over 1991–2025")
    return result


def get(url):
    error=None
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"OAF-Lambayeque-8B-scientific-benchmark/1.0"})
            with urllib.request.urlopen(req,timeout=60) as response:
                raw=response.read()
            if not 1500<len(raw)<250000:
                raise ValueError("CPC input suspicious byte count: "+str(len(raw)))
            return raw.decode("ascii")
        except (OSError,ValueError) as e:
            error=e
            if n<2:time.sleep(3)
    raise ValueError("CPC atmosphere download failed: "+str(error))


def load_target():
    with TARGET.open(encoding="utf-8",newline="") as f:
        source=csv.DictReader(f)
        if not source.fieldnames or not {"mes","anomalia_ersstv5_c"}<=set(source.fieldnames):
            raise ValueError("Reference series schema invalid")
        res={}
        for row in source:
            d=row["mes"];v=float(row["anomalia_ersstv5_c"])
            if d in res or not math.isfinite(v) or abs(v)>12:
                raise ValueError("Duplicate/missing Niño 1+2 "+d)
            res[d]=v
    months=sorted(res)
    if len(months)<850 or months[0]!="1950-01":raise ValueError("Incomplete ERSSTv5 series")
    for a,b in zip(months,months[1:]):
        if shift(a,1)!=b:raise ValueError("Gap in oceanic monthly source")
    return res


def solve(matrix,rhs):
    n=len(rhs);m=[list(matrix[i])+[rhs[i]] for i in range(n)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(m[j][i]))
        if abs(m[pivot][i])<1e-9:raise ValueError("Singular regression matrix")
        m[pivot],m[i]=m[i],m[pivot]
        scale=m[i][i]
        for k in range(i,n+1):m[i][k]/=scale
        for j in range(n):
            if j==i:continue
            scale=m[j][i]
            for k in range(i,n+1):m[j][k]-=scale*m[i][k]
    return [m[i][n] for i in range(n)]


def features(month,sea,atmos,extended):
    ocean=sea.get(month)
    if ocean is None:return None
    values=[ocean]
    if extended:
        for p in PREDICTORS:
            datum=atmos[p].get(month)
            if datum is None:return None
            values.append(datum)
    return values


def fit(train,alpha=ALPHA):
    """Ridge with standardized predictors; targets in deg C; no penalty on intercept."""
    width=len(train[0][0])
    means=[st.mean(x[i] for x,_ in train) for i in range(width)]
    scales=[max(st.pstdev(x[i] for x,_ in train),1e-6) for i in range(width)]
    n=width+1;mat=[[0.0]*n for _ in range(n)];rhs=[0.0]*n
    for x,y in train:
        xx=[1.0]+[(v-means[i])/scales[i] for i,v in enumerate(x)]
        for i in range(n):
            rhs[i]+=xx[i]*y
            for j in range(i,n):mat[i][j]+=xx[i]*xx[j]
    for i in range(n):
        for j in range(i):mat[i][j]=mat[j][i]
        if i:mat[i][i]+=alpha
    return {"means":means,"scales":scales,"coef":solve(mat,rhs)}


def predict(model,values):
    norm=[1.0]+[(v-model["means"][i])/model["scales"][i]
                 for i,v in enumerate(values)]
    return sum(a*b for a,b in zip(norm,model["coef"]))


def score(rows,field):
    errors=[r[field]-r["observado_c"] for r in rows]
    return {"n":len(errors),
            "mae_c":round(st.mean(abs(e) for e in errors),4),
            "rmse_c":round(math.sqrt(st.mean(e*e for e in errors)),4),
            "sesgo_c":round(st.mean(errors),4)}


def bootstrap(rows,reps=800,block=12):
    """Paired contiguous block sampling; descriptive stability, NOT formal significance."""
    if len(rows)<50:raise ValueError("Insufficient bootstrap chronology")
    rng=random.Random(20261015);vals=[]
    for _ in range(reps):
        picked=[]
        while len(picked)<len(rows):
            start=rng.randint(0,max(0,len(rows)-block))
            picked.extend(rows[start:start+block])
        picked=picked[:len(rows)]
        a=st.mean(abs(r["ar1_c"]-r["observado_c"]) for r in picked)
        b=st.mean(abs(r["atm_c"]-r["observado_c"]) for r in picked)
        if a>0:vals.append(1-b/a)
    vals.sort()
    return [round(vals[int(.025*(len(vals)-1))],4),
            round(vals[int(.975*(len(vals)-1))],4)]


def evaluate(sea,atmos):
    common=sorted(set(sea)&set(atmos[PREDICTORS[0]])&
                  set(atmos[PREDICTORS[1]])&set(atmos[PREDICTORS[2]]))
    if len(common)<400:raise ValueError("Insufficient shared monthly atmosphere/ocean data")
    common_set=set(common)
    origins=sorted(x for x in common if FIRST_ORIGIN<=x<=max(sea))
    # All supervised features dated at their month of origin, label dated target.
    data={h:[] for h in HORIZONS}
    for horizon in HORIZONS:
        # Expand from shared post-1979 origins with known target and consistent source.
        examples=[(o,features(o,sea,atmos,True),sea.get(shift(o,horizon)))
                  for o in common if shift(o,horizon) in sea]
        examples=[(o,x,y) for o,x,y in examples if x is not None and y is not None]
        for origin in origins:
            if shift(origin,horizon) not in sea:continue
            current=features(origin,sea,atmos,True)
            if current is None:continue
            # Training labels must be issued/known at or before this origin.
            eligible=[(o,x,y) for o,x,y in examples
                      if shift(o,horizon)<=origin]
            if len(eligible)<MIN_TRAIN:continue
            t1=[([x[0]],y) for _,x,y in eligible]
            t4=[(x,y) for _,x,y in eligible]
            first=fit(t1);second=fit(t4)
            y=sea[shift(origin,horizon)]
            data[horizon].append({
                "mes_origen":origin,"mes_objetivo":shift(origin,horizon),
                "horizonte_meses":horizon,
                "observado_c":y,
                "persistencia_c":sea[origin],
                "ar1_c":predict(first,[current[0]]),
                "atm_c":predict(second,current),
                "soi_origen":current[1],"alisios_central_origen":current[2],
                "alisios_oriental_origen":current[3]
            })
        if len(data[horizon])<MIN_FOLDS:
            raise ValueError("Too few walk-forward folds for h"+str(horizon))
    result={}
    for h in HORIZONS:
        folds=data[h]
        month12=folds[-12:]
        base=score(folds,"ar1_c")
        expanded=score(folds,"atm_c")
        persistence=score(folds,"persistencia_c")
        latest1=score(month12,"ar1_c")
        latest4=score(month12,"atm_c")
        gain=1-expanded["mae_c"]/base["mae_c"]
        gain_p=1-expanded["mae_c"]/persistence["mae_c"]
        ci=bootstrap(folds)
        last12gain=1-latest4["mae_c"]/latest1["mae_c"]
        result[str(h)]={
            "n_origenes_evaluados":len(folds),
            "desde":folds[0]["mes_origen"],"hasta":folds[-1]["mes_origen"],
            "metricas":{"persistencia":persistence,"ar1_solo_tsm":base,"tsm_mas_atmosfera":expanded},
            "ultimos12":{"ar1_solo_tsm":latest1,"tsm_mas_atmosfera":latest4},
            "beneficio_vs_ar1":round(gain,4),
            "beneficio_vs_persistencia":round(gain_p,4),
            "beneficio_ultimos12_vs_ar1":round(last12gain,4),
            "intervalo_descriptivo_bloques_12m_95":ci,
            "mejora_retrospectiva_robusta_provisional":bool(ci[0]>0 and gain>0 and last12gain>0 and gain_p>0),
            "validacion_prospectiva":False
        }
    last=max(common_set&set(sea))
    if last!=max(sea):
        # NO extrapolation using outdated atmospheric data.
        current=None
    else:
        current={}
        for h in HORIZONS:
            eligible=[(o,features(o,sea,atmos,True),sea.get(shift(o,h)))
                      for o in common if shift(o,h) in sea and shift(o,h)<=last]
            eligible=[(o,x,y) for o,x,y in eligible if x is not None and y is not None]
            if len(eligible)<MIN_TRAIN:raise ValueError("Not enough final training data")
            cur=features(last,sea,atmos,True)
            if cur is None:raise ValueError("Final origin atmospheric data missing")
            m1=fit([([x[0]],y) for _,x,y in eligible])
            m4=fit([(x,y) for _,x,y in eligible])
            current[str(h)]={
                "mes_objetivo":shift(last,h),"horizonte_meses":h,
                "ar1_solo_tsm_c":round(predict(m1,[cur[0]]),4),
                "tsm_mas_atmosfera_c":round(predict(m4,cur),4),
                "persistencia_c":round(sea[last],4),
                "emision_prospectiva":False,
                "no_operativo":True
            }
    return data,{
        "fase":"8B","generado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado":"comparacion_historica_sin_habilidad_operativa",
        "predictores_mes_origen":PREDICTORS,
        "inicio_datos_atmosfericos":"1979-01",
        "origen_ultimo_comun":last,
        "mes_ultimo_oceanico":max(sea),
        "num_meses_comunes":len(common),
        "objetivo":"Anomalía Niño1+2 NOAA NCEI ERSSTv5 reajustada por OAF a 1991-2020; NO ICEN oficial",
        "entrenamiento":"ventana expansiva con solo objetivos cronológicamente disponibles",
        "primer_origen_de_prueba":FIRST_ORIGIN,
        "regularizacion_ridge_fija":ALPHA,
        "fuentes":{
            "soi":"https://www.cpc.ncep.noaa.gov/data/indices/soi",
            "viento_central":"https://www.cpc.ncep.noaa.gov/data/indices/cpac850",
            "viento_oriental":"https://www.cpc.ncep.noaa.gov/data/indices/epac850",
            "tsm":"NOAA NCEI ERSSTv5 rebasada por OAF; ver fase 6D"
        },
        "cobertura_prediccion_actual":bool(current),
        "predicciones_exploratorias_actuales":current,
        "resultados_por_horizonte":result,
        "es_icen_oficial":False,
        "es_alerta_enfen":False,
        "demuestra_prediccion_elnino_costero":False,
        "validacion_prospectiva":False,
        "advertencias":[
            "Archivo mensual CPC retrospectivo posiblemente revisado; NO conserva la versión disponible en cada fecha histórica, por lo que el walk-forward no es una auditoría as-of perfecta.",
            "Datos de índice del mes de origen se suponen disponibles al emitir tras publicación mensual; no emitir predicción actual si la fuente está rezagada.",
            "SOI y anomalías de viento no son variables locales de Lambayeque ni representan por sí solas intensidad del Niño Costero.",
            "Ningún resultado de Niño 1+2 reconstruido por OAF equivale al ICEN oficial ENFEN.",
            "El modelo atmosférico puede empeorar frente a persistencia; publicar también errores negativos.",
            "La serie y características de viento alisios se basan en índices NOAA CPC 850 hPa; no son datos de anemómetros en campo.",
            "Contenido de calor oceánico subsuperficial todavía no incluido; requiere versión, cobertura y disponibilidad históricas verificables.",
            "No se permiten categorías de alerta ENSO, predicciones de enfermedad ni probabilidades calibradas."
        ]
    }


def self_test():
    assert shift("2026-12",2)=="2027-02"
    synthetic=lambda tag,first:tag+"\nYEAR JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC\n"+"\n".join(
        f"{year} "+" ".join(str(float(m)) for m in range(1,13))
        for year in range(first,2026))
    a=parse_cpc(synthetic("ANOMALY",1979),"ANOMALY",1979)
    b=parse_cpc(synthetic("STANDARDIZED    DATA",1951),"STANDARDIZED    DATA",1951)
    assert len(a)>400 and len(b)>400
    text="ANOMALY\nYEAR JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC\n"
    text+="\n".join(f"{yr} "+" ".join(["1.0"]*12) for yr in range(1979,2026))
    text+="\n2026"+" ".join(["1.0"]*8)+" 1.0-999.9-999.9-999.9\n"
    parsed=parse_cpc(text,"ANOMALY",1979)
    assert parsed["2026-09"]==1 and "2026-10" not in parsed
    demo=[([i*0.1],2+i*0.13) for i in range(30)]
    fit1=fit(demo)
    assert math.isfinite(predict(fit1,[2.0]))
    assert len(solve([[3,1],[1,2]],[5,5]))==2
    print("8B PASS: NOAA CPC section parsing, concatenated missing values, ridge, month handling")


def write(sea,atmos,folds,report):
    ROOT.mkdir(exist_ok=True)
    with ATM.open("w",encoding="utf-8",newline="") as f:
        cols=["mes"]+PREDICTORS
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        for month in sorted(set.intersection(*(set(atmos[x]) for x in PREDICTORS))):
            w.writerow({"mes":month,**{k:atmos[k][month] for k in PREDICTORS}})
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    cols=["mes_origen","mes_objetivo","horizonte_meses","observado_c",
          "persistencia_c","ar1_c","atm_c","soi_origen",
          "alisios_central_origen","alisios_oriental_origen"]
    with SAMPLE.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for h in HORIZONS:w.writerows(folds[h])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test();return
    sea=load_target()
    atmospheric={}
    for name,(url,marker,year) in CPC.items():
        atmospheric[name]=parse_cpc(get(url),marker,year)
        print("Source",name,len(atmospheric[name]),"last",max(atmospheric[name]),flush=True)
    folds,report=evaluate(sea,atmospheric)
    write(sea,atmospheric,folds,report)
    for h,r in report["resultados_por_horizonte"].items():
        print("HORIZON",h,"n",r["n_origenes_evaluados"],
              "MAE",r["metricas"],"gain_atm_vs_ar1",r["beneficio_vs_ar1"],flush=True)
    print("OAF 8B NOAA atmosphere model completed (historical only)")


if __name__=="__main__":
    try:main()
    except Exception as error:
        print("ERROR 8B:",str(error),file=sys.stderr)
        raise SystemExit(1)
