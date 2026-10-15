#!/usr/bin/env python3
"""OAF-Lambayeque Fase 6C: ERSSTv5 Niño 1+2, evaluación 1/2/3 meses.

NO ES EL ICEN OFICIAL. La serie ERSSTv5 permite reproducir un PROMEDIO
MÓVIL TRIMESTRAL ILUSTRATIVO; ENFEN define oficialmente el índice,
diagnóstico, eventos y sistema de alertas. No inferir categorías.
NOAA CPC ERSSTv5: 1991-2020 base, región Niño 1+2.
"""
import argparse
import csv
import json
import math
import random
import statistics as stats
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii"
DIR = Path("datos")
OISST_CSV = DIR / "noaa_nino12_oisst_mensual.csv"
MIN_TRAIN = 120
FIRST_ORIGIN = "2010-01"
MIN_FOLDS = 120
HORIZONS = (1, 2, 3)


def advance_month(month, offset=1):
    y,m = map(int, month.split("-"))
    z = y*12+(m-1)+offset
    return f"{z//12:04d}-{z%12+1:02d}"


def parse_source(content):
    """The NOAA CPC data table contains 10 columns, Niño 1+2 in columns 2 and 3."""
    out, seen = [], set()
    for line in content.splitlines():
        p=line.split()
        if len(p)<10 or not (p[0].isdigit() and p[1].isdigit()):
            continue
        yr,mo=int(p[0]),int(p[1])
        if not (1950<=yr<=2100 and 1<=mo<=12):
            continue
        date=f"{yr:04d}-{mo:02d}"
        if date in seen:
            raise ValueError("Duplicate month: "+date)
        sea,anomaly=float(p[2]),float(p[3])
        if not(math.isfinite(sea) and math.isfinite(anomaly)
               and 10<=sea<=35 and -10<=anomaly<=12):
            raise ValueError("Suspicious Niño 1+2 data in "+date)
        seen.add(date)
        out.append({"mes":date,"tsm_c":sea,"anomalia_ersstv5_c":anomaly})
    out.sort(key=lambda x:x["mes"])
    if len(out)<850 or out[0]["mes"]!="1950-01":
        raise ValueError("NOAA ERSSTv5 series too short or changed format")
    for a,b in zip(out,out[1:]):
        if advance_month(a["mes"])!=b["mes"]:
            raise ValueError("Gap: "+a["mes"]+" then "+b["mes"])
    return out


def fetch_noaa():
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"OAF-Lambayeque/0.2 (scientific index monitoring)"})
    error=None
    for tries in range(3):
        try:
            with urllib.request.urlopen(req,timeout=45) as r:
                blob=r.read()
            if len(blob)>300000:
                raise ValueError("Unexpected NOAA file size")
            return blob.decode("ascii")
        except (OSError,UnicodeError,ValueError) as err:
            error=err
            if tries<2:
                time.sleep(3)
    raise RuntimeError("Could not retrieve ERSSTv5 NOAA: "+str(error))


def fit_ar1(known):
    if len(known)<MIN_TRAIN:
        raise ValueError("Not enough training months")
    x,y=known[:-1],known[1:]
    xm,ym=stats.mean(x),stats.mean(y)
    var=sum((p-xm)**2 for p in x)
    if var<1e-9:
        return ym,0.0
    slope=sum((p-xm)*(q-ym) for p,q in zip(x,y))/var
    return ym-slope*xm,slope


def predict_steps(known,h):
    a,b=fit_ar1(known)
    x=known[-1]
    for _ in range(h):
        x=a+b*x
    return x


def metrics(folds,method):
    errs=[f[method]-f["observado"] for f in folds]
    return {"n":len(errs),"mae_c":round(stats.mean(map(abs,errs)),4),
            "rmse_c":round(math.sqrt(stats.mean(e*e for e in errs)),4)}


def bootstrap_delta(folds, reps=1200, block=12):
    """Bootstrap heuristic for MAE skill, serially dependent paired errors."""
    rng=random.Random(20261014)
    samples=[]
    n=len(folds)
    for _ in range(reps):
        picked=[]
        while len(picked)<n:
            start=rng.randrange(max(1,n-block+1))
            picked.extend(folds[start:start+block])
        picked=picked[:n]
        ar=stats.mean(abs(x["ar1"]-x["observado"]) for x in picked)
        persist=stats.mean(abs(x["persistencia"]-x["observado"]) for x in picked)
        if persist>0:
            samples.append(1-ar/persist)
    if len(samples)<50:
        raise ValueError("Bootstrap insufficient")
    samples.sort()
    return [round(samples[int((len(samples)-1)*.025)],4),
            round(samples[int((len(samples)-1)*.975)],4)]


def moving_three_month(rows):
    """Illustrative centered 3-month mean from NOAA ERSSTv5, NOT official ICEN."""
    out=[]
    for i in range(2,len(rows)):
        triplet=[rows[j]["anomalia_ersstv5_c"] for j in (i-2,i-1,i)]
        out.append({"mes_central":rows[i-1]["mes"],
                    "mes_publicacion_ultimo_dato":rows[i]["mes"],
                    "promedio_trimestral_ersstv5_c":round(sum(triplet)/3,3),
                    "es_icen_oficial":False})
    return out


def compare_oisst(rows):
    if not OISST_CSV.is_file():
        return {"estado":"archivo_no_disponible"}
    with OISST_CSV.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        comp={row["mes"]:float(row["nino12_anom_c"]) for row in reader}
    diffs=[{"mes":row["mes"],"delta_ersst_menos_oisst_c":round(row["anomalia_ersstv5_c"]-comp[row["mes"]],3)}
           for row in rows if row["mes"] in comp]
    if len(diffs)<300:
        return {"estado":"periodo_comun_insuficiente","meses":len(diffs)}
    absmean=stats.mean(abs(r["delta_ersst_menos_oisst_c"]) for r in diffs)
    return {"estado":"comparacion_exploratoria_no_validacion",
            "meses_comunes":len(diffs),"mae_entre_productos_c":round(absmean,4),
            "ultimo_mes_comun":diffs[-1]["mes"],
            "diferencia_ultimo_mes_c":diffs[-1]["delta_ersst_menos_oisst_c"],
            "nota":"Diferencias entre productos no son error de predicción ni validación instrumental"}


def evaluate(rows):
    v=[r["anomalia_ersstv5_c"] for r in rows]
    scores={}, {}
    results={}
    backtest=[]
    for h in HORIZONS:
        folds=[]
        for t in range(MIN_TRAIN-1,len(v)-h):
            if rows[t]["mes"]<FIRST_ORIGIN:
                continue
            obs=v[t+h]
            folds.append({"origen":rows[t]["mes"],"objetivo":rows[t+h]["mes"],
                          "horizonte_meses":h,"observado":obs,
                          "ar1":predict_steps(v[:t+1],h),
                          "persistencia":v[t],"cero":0.0})
        if len(folds)<MIN_FOLDS:
            raise ValueError("Insufficient walk-forward folds, h="+str(h))
        m={key:metrics(folds,key) for key in ("ar1","persistencia","cero")}
        recent=folds[-12:]
        m_recent={key:metrics(recent,key) for key in ("ar1","persistencia")}
        skill=1-m["ar1"]["mae_c"]/m["persistencia"]["mae_c"] if m["persistencia"]["mae_c"]>0 else None
        recent_skill=1-m_recent["ar1"]["mae_c"]/m_recent["persistencia"]["mae_c"] if m_recent["persistencia"]["mae_c"]>0 else None
        ci=bootstrap_delta(folds)
        consistent=(skill is not None and skill>0 and recent_skill is not None
                    and recent_skill>0 and ci[0]>0)
        results[str(h)]={"origen_inicial":folds[0]["origen"],
                         "origen_final":folds[-1]["origen"],
                         "metricas":m,"metricas_ultimos_12":m_recent,
                         "habilidad_mae_relativa":round(skill,4) if skill is not None else None,
                         "habilidad_ultimos_12":round(recent_skill,4) if recent_skill is not None else None,
                         "intervalo_bootstrap_skill_95":ci,
                         "mejora_consistente_demostrada":consistent,
                         "pronostico_ar1_c":round(predict_steps(v,h),3),
                         "pronostico_persistencia_c":round(v[-1],3),
                         "mes_objetivo":advance_month(rows[-1]["mes"],h)}
        backtest.extend(folds)
    monthly=moving_three_month(rows)
    now=datetime.now(timezone.utc)
    year,month=map(int,rows[-1]["mes"].split("-"))
    age=(now.year-year)*12+now.month-month
    if age>3 or age<1:
        raise ValueError("ERSSTv5 latest month outdated or not yet closed: "+rows[-1]["mes"])
    report={
        "fase":"6C",
        "fecha_procesamiento_utc":now.isoformat(timespec="seconds"),
        "fuente":"NOAA CPC",
        "url_fuente":SOURCE,
        "producto":"ERSSTv5 SST mensual Niño 1+2, anomalías base 1991-2020",
        "tipo_dato":"reanálisis SST oceánica",
        "es_icen_oficial":False,
        "es_pronostico_institucional":False,
        "es_alerta":False,
        "estado":"experimental_no_validado",
        "mes_inicial":rows[0]["mes"],
        "mes_ultimo_observado":rows[-1]["mes"],
        "ultima_anomalia_ersstv5_c":round(v[-1],3),
        "promedio_3m_indicativo":monthly[-1],
        "modelos_horizontes":results,
        "comparacion_oisst":compare_oisst(rows),
        "advertencias":[
            "Promedio trimestral ilustrativo no es ICEN oficial; para la clasificación se usa exclusivamente ENFEN.",
            "Modelo AR1 univariado, sin información de viento, termoclina, calor subsuperficial ni predicción dinámica.",
            "Walk-forward retrospectivo con la versión NOAA revisada, no con pronósticos archivados al momento de emisión.",
            "Un cambio del índice oceánico no implica por sí solo un evento El Niño Costero ni predice lluvia en Lambayeque.",
            "Comparar AR1 con persistencia; no divulgar habilidad no demostrada.",
            "No generar alertas meteorológicas o fitosanitarias a partir de estos resultados."
        ]
    }
    return report,monthly,backtest


def write(rows,report,quarter,back):
    DIR.mkdir(exist_ok=True)
    def write_csv(path,fields,data):
        with path.open("w",encoding="utf-8",newline="") as file:
            writer=csv.DictWriter(file,fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    write_csv(DIR/"noaa_ersstv5_nino12_mensual.csv",
              ["mes","tsm_c","anomalia_ersstv5_c"],rows)
    write_csv(DIR/"nino12_ersstv5_promedio_trimestral_experimental.csv",
              ["mes_central","mes_publicacion_ultimo_dato","promedio_trimestral_ersstv5_c","es_icen_oficial"],quarter)
    fields=["origen","objetivo","horizonte_meses","observado","ar1","persistencia","cero"]
    write_csv(DIR/"ersstv5_nino12_walkforward_1a3m.csv",
              fields,[{key:round(v,4) if isinstance(v,float) else v for key,v in f.items()} for f in back])
    (DIR/"modelo_ersstv5_nino12_6c.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def self_test():
    rows=[]
    for year in range(1950,2027):
        for mon in range(1,13):
            v=round(.8*math.sin(len(rows)/10)+.1*math.cos(len(rows)/3),2)
            rows.append({"mes":f"{year:04d}-{mon:02d}","tsm_c":24.0,"anomalia_ersstv5_c":v})
    text="YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM\n"
    text+="\n".join(f"{r['mes'][:4]} {int(r['mes'][5:])} {r['tsm_c']:.2f} {r['anomalia_ersstv5_c']:.2f} 26 0 28 0 27 0" for r in rows)
    parsed=parse_source(text)
    assert len(parsed)==924 and advance_month("2026-12",1)=="2027-01"
    assert abs(moving_three_month(parsed)[0]["promedio_trimestral_ersstv5_c"]-
               sum(r["anomalia_ersstv5_c"] for r in parsed[:3])/3)<0.001
    report,avg,folds=evaluate(parsed)
    assert all(report["modelos_horizontes"][str(h)]["metricas"]["ar1"]["n"]>180 for h in HORIZONS)
    assert set(f["horizonte_meses"] for f in folds)==set(HORIZONS)
    assert report["es_icen_oficial"] is False
    assert report["es_alerta"] is False
    try:
        parse_source(text.replace("1950 2 ", "1950 4 ",1))
    except ValueError:
        pass
    else:
        raise AssertionError("Missing months were not rejected")
    print("Tests ERSSTv5 6C passed, synthetic data only.")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test()
        return
    rows=parse_source(fetch_noaa())
    report,quarter,back=evaluate(rows)
    write(rows,report,quarter,back)
    print(json.dumps({"status":"ok","last_month":report["mes_ultimo_observado"],
                      "horizons":{k:{"ar1":v["pronostico_ar1_c"],
                                     "persistence":v["pronostico_persistencia_c"],
                                     "consistent":v["mejora_consistente_demostrada"]}
                                   for k,v in report["modelos_horizontes"].items()}},ensure_ascii=False))


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("OAF 6C failed: "+str(exc),file=sys.stderr)
        raise SystemExit(1)
