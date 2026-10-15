#!/usr/bin/env python3
"""OAF 8D: paired moving-month-block resampling of retrospective local skill.

Uses the stored 2023-2026 genuine model hindcast rows, never fabricates
forecast or instrumental observations. Six-month blocks and 2000 seeded
replicates for relative MAE of Niño1+2 and Niño1+2+T300 vs local Ridge.
Descriptive temporal stability intervals only (NOT formal corrected CIs).
"""
import argparse
import csv
import json
import math
import random
import statistics as st
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

SOURCE=Path("datos/benchmark_impacto_lambayeque_8d_prueba.csv")
DEST=Path("datos/robustez_impacto_regional_8d.json")
RESULTS=2000
BLOCK=6


def read():
    with SOURCE.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)<1400:raise ValueError("Regional hindcast CSV absent or truncated")
    grouped=defaultdict(list)
    keys=("observado_anomalia","modelo_local","modelo_nino","modelo_nino_t300")
    for row in rows:
        city=row["localidad"];var=row["variable"];h=int(row["horizonte_meses"])
        if city not in ("Chiclayo","Jayanca","Motupe","Olmos") or var not in (
              "temperatura_c","precipitacion_mm","radiacion_mj_m2") or h not in (1,2,3):
            raise ValueError("Unknown model group in archived hindcast")
        values=[]
        for k in keys:
            x=float(row[k])
            if not math.isfinite(x):raise ValueError("Non finite monthly hindcast")
            values.append(x)
        grouped[(city,var,h)].append((row["mes_origen"],values))
    if len(grouped)!=36:raise ValueError("Expected 36 region-variable-horizon groups")
    return grouped


def interval(rows,compare,seed,iterations=RESULTS,block=BLOCK):
    # Records sorted chronologically, all alternatives evaluated on paired months.
    rows=sorted(rows)
    vals=[values for _,values in rows]
    n=len(vals)
    if n<35:raise ValueError("Not enough held-out monthly observations")
    baseline=[abs(r[1]-r[0]) for r in vals]
    competitor=[abs(r[compare]-r[0]) for r in vals]
    base=st.mean(baseline);other=st.mean(competitor)
    if base==0:raise ValueError("Baseline MAE zero, skill undefined")
    point=1-other/base
    rng=random.Random(seed)
    draws=[]
    for _ in range(iterations):
        indexes=[]
        while len(indexes)<n:
            origin=rng.randrange(n-block+1)
            indexes.extend(range(origin,origin+block))
        indexes=indexes[:n]
        b=sum(baseline[i] for i in indexes)/n
        a=sum(competitor[i] for i in indexes)/n
        if b>0:draws.append(1-a/b)
    if len(draws)<iterations*.9:raise ValueError("Too many degenerate bootstrap draws")
    draws.sort()
    lower=draws[int(.025*(len(draws)-1))]
    upper=draws[int(.975*(len(draws)-1))]
    return {"n_meses":n,"mejora_relativa":round(point,5),
            "intervalo_exploratorio_95":[round(lower,5),round(upper,5)],
            "intervalo_totalmente_positivo":lower>0,
            "intervalo_totalmente_negativo":upper<0}


def evaluate(groups):
    summary={}
    for ci,((city,var,h),rows) in enumerate(sorted(groups.items())):
        city_result=summary.setdefault(city,{})
        variable_result=city_result.setdefault(var,{})
        variable_result[str(h)]={
            "nino_vs_local":interval(rows,2,20261015+ci*2),
            "nino_t300_vs_local":interval(rows,3,20261015+ci*2+1)
        }
    return {
        "fase":"8D_robustez",
        "generado_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuente":"datos/benchmark_impacto_lambayeque_8d_prueba.csv",
        "evaluacion":"Solo orígenes de prueba 2023-2026, MAE emparejado",
        "metodo":"Remuestreo de bloques móviles de 6 meses contiguos, 2000 réplicas, semilla fija por comparación",
        "comparaciones":"Niño1+2 y Niño1+2+T300 contra Ridge local, mismas fechas",
        "validacion_prospectiva":False,
        "son_intervalos_de_confianza_formalmente_calibrados":False,
        "se_confirmo_habilidad_operativa":False,
        "resultado":summary,
        "advertencias":[
            "Los intervalos son descriptivos sobre meses contiguos de esta prueba, no garantía de pronóstico futuro.",
            "Datos climáticos de referencia ERA5/ERA5-Land reanalizados, no mediciones SENAMHI.",
            "ERA5 y fuentes oceánicas históricas pueden revisarse; el predictor mensual no necesariamente estaba publicado antes de iniciar el mes objetivo.",
            "El contraste posterior a 2022 sigue siendo retrospectivo, no archivo de pronósticos reales del modelo regional."
        ]
    }


def self_test():
    samples=[(f"2023-{i+1:02d}",[float(i),float(i)+1.,float(i)+.7,float(i)+.4]) for i in range(12)]
    samples+= [(f"2024-{i+1:02d}",[float(i),float(i)+1.,float(i)+.7,float(i)+.4]) for i in range(12)]
    samples+= [(f"2025-{i+1:02d}",[float(i),float(i)+1.,float(i)+.7,float(i)+.4]) for i in range(12)]
    result=interval(samples,3,20,100,6)
    assert result["intervalo_totalmente_positivo"] and abs(result["mejora_relativa"]-.6)<1e-5
    assert result["n_meses"]==36
    print("8D bootstrap PASSED: paired chronological months, synthetic 6-month blocks and no false precision")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    x=p.parse_args()
    if x.self_test:self_test();return
    report=evaluate(read())
    DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={site:[report["resultado"][site]["temperatura_c"][str(h)]["nino_t300_vs_local"]["intervalo_exploratorio_95"] for h in (1,2,3)] for site in ("Chiclayo","Jayanca","Motupe","Olmos")}
    print("8D descriptive weather stability evaluation: "+json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":
    main()
