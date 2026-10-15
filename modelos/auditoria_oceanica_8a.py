#!/usr/bin/env python3
"""OAF Fase 8A: immutable oceanic experimental forecast issuances and subsequent verification.

NCEI ERSSTv5 Niño1+2 anomalies *rebased by OAF* from 1971-2000 to 1991-2020.
Not the official ICEN, ENFEN forecast, probability, or coastal-El-Niño alert.
Important: a forecast made AFTER the target month began is labeled a NOWCAST,
not a clean out-of-sample before-month forecast.

Inputs: versioned Phase 6D results and monthly adjusted NOAA series.
Emissions are append-only, keyed by latest observed month. Each stores SHA256
digests of its original source files. Verification against subsequently
available *revised* monthly data is delayed until 10th of month AFTER target.
"""
import argparse
import csv
import hashlib
import json
import math
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MODEL = Path("datos/modelo_ersstv5_ncei_6d.json")
OBS = Path("datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv")
DIR = Path("datos/pronosticos_oceanicos_emitidos")
REPORT = Path("datos/verificacion_oceanica_8a.json")
DETAIL = Path("datos/verificacion_oceanica_8a.csv")
LOCAL = ZoneInfo("America/Lima")
MONTH = re.compile(r"^(19|20)\d{2}-(0[1-9]|1[0-2])$")
FIELDS = ["emision_utc","mes_origen","mes_objetivo","horizonte_meses",
          "emitido_antes_de_inicio_mes","pronostico_ar1_c","persistencia_c",
          "observado_revisado_c","error_ar1_c","error_persistencia_c",
          "mae_beneficio_c"]


def move(ym, offset):
    if not MONTH.fullmatch(ym):
        raise ValueError("Mes inválido "+str(ym))
    yr,mo=map(int,ym.split("-"))
    n=yr*12+(mo-1)+offset
    return f"{n//12:04d}-{n%12+1:02d}"


def month_day(ym, day=1):
    yr,mo=map(int,ym.split("-"))
    return date(yr,mo,day)


def number(x):
    return type(x) in (float,int) and math.isfinite(x)


def read_monthly(path=OBS):
    if not path.is_file():
        raise ValueError("Falta serie observacional mensual NOAA reajustada")
    with path.open(encoding="utf-8",newline="") as file:
        reader=csv.DictReader(file)
        if not reader.fieldnames or not {"mes","anomalia_ersstv5_c"}<=set(reader.fieldnames):
            raise ValueError("Columnas de referencia NOAA no verificadas")
        data={}
        for r in reader:
            ym=r["mes"]
            if not MONTH.fullmatch(ym) or ym in data:
                raise ValueError("Mes NOAA inválido/duplicado "+str(ym))
            x=float(r["anomalia_ersstv5_c"])
            if not math.isfinite(x) or abs(x)>12:
                raise ValueError("Anomalía NOAA fuera de límites "+ym)
            data[ym]=x
    months=sorted(data)
    if len(months)<600 or months[0]!="1950-01":
        raise ValueError("Serie NOAA inusualmente corta")
    for before,after in zip(months,months[1:]):
        if move(before,1)!=after:
            raise ValueError("Serie NOAA mensual discontinua")
    return data


def archive_model(model,observed,now):
    if model.get("fase")!="6D" or model.get("fuente")!="NOAA NCEI":
        raise ValueError("No es el modelo NCEI auditado de fase 6D")
    if model.get("es_icen_oficial") is not False or model.get("es_alerta") is not False or model.get("no_es_clasificacion_enfen") is not True:
        raise ValueError("No hay garantías de separación del ICEN y alertas")
    if model.get("serie_noaa_orig_anom_base")!="1971-2000" or model.get("serie_oaf_ajustada_base")!="1991-2020":
        raise ValueError("Referencias climatológicas mal etiquetadas")
    if model.get("prediccion_actual_disponible") is not True:
        raise ValueError("El modelo no ofrece pronósticos actuales verificables")
    comparison=model.get("contraste_cpc_ersstv5",{})
    if comparison.get("calidad_suficiente") is not True:
        raise ValueError("Contraste de NOAA CPC no satisfactorio")
    origin=model.get("mes_ultimo_observado")
    if not MONTH.fullmatch(str(origin)):
        raise ValueError("Mes de origen mal formado")
    if origin!=max(observed):
        raise ValueError("El origen no coincide con la última fila observada")
    if abs(observed[origin]-model.get("ultima_anomalia_ersstv5_c",999))>0.001:
        raise ValueError("La última anomalía del modelo no coincide con NOAA")
    local=now.astimezone(LOCAL)
    current=local.strftime("%Y-%m")
    # New experimental predictions from an old origin are unacceptable.
    if move(origin,1)!=current:
        raise ValueError("Para emitir una proyección nueva exigimos mes observado inmediatamente anterior al actual; NOAA o el modelo no están vigentes")
    issued=[]
    for horizon in (1,2,3):
        x=model.get("modelos_horizontes",{}).get(str(horizon),{})
        target=move(origin,horizon)
        if x.get("mes_objetivo")!=target or not number(x.get("pronostico_ar1_c")) or not number(x.get("pronostico_persistencia_c")):
            raise ValueError("Falta pronóstico verificable al horizonte "+str(horizon))
        if abs(x["pronostico_ar1_c"])>12 or abs(x["pronostico_persistencia_c"])>12:
            raise ValueError("Pronóstico anómalo fuera de límite")
        prior=local.date()<month_day(target)
        issued.append({
            "horizonte_meses":horizon,
            "mes_objetivo":target,
            "pronostico_ar1_c":x["pronostico_ar1_c"],
            "persistencia_c":x["pronostico_persistencia_c"],
            "emitido_antes_de_inicio_mes":prior,
            "clase_emision":"pronostico_previo_al_mes" if prior else "estimacion_intramensual_nowcast",
            "mae_historico_ar1_c":x.get("metricas",{}).get("ar1",{}).get("mae_c"),
            "mae_historico_persistencia_c":x.get("metricas",{}).get("persistencia",{}).get("mae_c"),
            "mae_ultimos12_ar1_c":x.get("metricas_ultimos_12",{}).get("ar1",{}).get("mae_c"),
            "mae_ultimos12_persistencia_c":x.get("metricas_ultimos_12",{}).get("persistencia",{}).get("mae_c"),
            "validacion_prospectiva":False
        })
    stamp=now.astimezone(timezone.utc)
    return {
        "fase":"8A",
        "tipo":"emision_inmutable_experimental_anomalia_oceanica_mensual",
        "emision_utc":stamp.isoformat(timespec="seconds"),
        "emision_local_peru":local.isoformat(timespec="seconds"),
        "mes_origen":origin,
        "anomalia_observada_origen_c":observed[origin],
        "producto":"NOAA NCEI ERSSTv5 Niño 1+2, anomalía 1991-2020 reconstruida por OAF",
        "climatologia_noaa_archivo":"1971-2000",
        "climatologia_oaf_ajustada":"1991-2020",
        "fuente_noaa":"https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat",
        "sha256_modelo_ncei_6d":hashlib.sha256(MODEL.read_bytes()).hexdigest(),
        "sha256_serie_reajustada":hashlib.sha256(OBS.read_bytes()).hexdigest(),
        "fecha_elaboracion_modelo_utc":model.get("fecha_procesamiento_utc"),
        "calidad_contraste_fuentes":comparison.get("calidad_suficiente"),
        "pronosticos":issued,
        "es_icen_oficial":False,
        "es_alerta_enfen":False,
        "prediccion_elnino_costero_validada":False,
        "modelo_supera_persistencia_demostrado":False,
        "observaciones":[
            "Si el pronóstico se emite después del inicio del mes objetivo, se declara estimación intramensual, NO predicción enteramente previa al mes.",
            "Esta emisión fija cálculos y fuentes como evidencia fechada; verificaciones futuras contra series NOAA pueden usar datos revisados.",
            "Modelo AR(1) experimental; MAE reciente peor que persistencia al preparar fase 8A. No usar como alerta ENSO, ICEN oficial ni recomendación agrícola."
        ]
    }


def freeze(now=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError("Se necesita hora absoluta de emisión")
    if not MODEL.is_file():raise ValueError("Modelo NCEI todavía no generado")
    model=json.loads(MODEL.read_text(encoding="utf-8"))
    observed=read_monthly()
    # If model/source is not fresh, never manufacture a new monthly forecast.
    origin=model.get("mes_ultimo_observado")
    if MONTH.fullmatch(str(origin)):
        target=DIR/(origin+".json")
        if target.exists():
            stored=json.loads(target.read_text(encoding="utf-8"))
            if stored.get("mes_origen")!=origin or stored.get("fase")!="8A":
                raise ValueError("Conflicto de emisión congelada, NO sobrescribir")
            print("Emisión preexistente preservada sin sobrescritura:",target)
            return stored,False
    frozen=archive_model(model,observed,now)
    DIR.mkdir(parents=True,exist_ok=True)
    target=DIR/(frozen["mes_origen"]+".json")
    if target.exists():raise ValueError("Race condition, never overwrite frozen issue")
    target.write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Emisión oceánica sellada:",target,
          "primera ahora-cast mensual vs mes siguiente claramente etiquetada",flush=True)
    return frozen,True


def verify(now=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError("Se necesita hora de evaluación con huso")
    local=now.astimezone(LOCAL).date()
    observed=read_monthly()
    all_predictions=[]
    for file in sorted(DIR.glob("????-??.json")) if DIR.exists() else []:
        p=json.loads(file.read_text(encoding="utf-8"))
        if p.get("fase")!="8A" or p.get("es_icen_oficial") is not False or p.get("es_alerta_enfen") is not False:
            raise ValueError("Pronóstico guardado sin garantías de origen")
        origin=p.get("mes_origen")
        issued=datetime.fromisoformat(p["emision_utc"].replace("Z","+00:00"))
        if not MONTH.fullmatch(str(origin)) or file.stem!=origin or issued.tzinfo is None:
            raise ValueError("Archivo oceánico congelado inconsistente")
        if not isinstance(p.get("pronosticos"),list) or len(p["pronosticos"])!=3:
            raise ValueError("Horizontes incorrectos en la emisión")
        for item in p["pronosticos"]:
            h=item["horizonte_meses"];month=item["mes_objetivo"]
            if type(h)!=int or h not in (1,2,3) or move(origin,h)!=month:
                raise ValueError("Horizonte o target incoherente")
            if not number(item.get("pronostico_ar1_c")) or not number(item.get("persistencia_c")):
                raise ValueError("Predicción archivada no numérica")
            previous=issued.astimezone(LOCAL).date()<month_day(month)
            if previous is not item.get("emitido_antes_de_inicio_mes"):
                raise ValueError("Tipo prospectivo / nowcast del archivo inválido")
            release=month_day(move(month,1),10)
            is_mature=local>=release
            observed_num=observed.get(month) if is_mature else None
            evaluated=is_mature and number(observed_num)
            e=round(item["pronostico_ar1_c"]-observed_num,5) if evaluated else None
            ep=round(item["persistencia_c"]-observed_num,5) if evaluated else None
            all_predictions.append({
                "emision_utc":p["emision_utc"],
                "mes_origen":origin,
                "mes_objetivo":month,
                "horizonte_meses":h,
                "emitido_antes_de_inicio_mes":previous,
                "pronostico_ar1_c":item["pronostico_ar1_c"],
                "persistencia_c":item["persistencia_c"],
                "observado_revisado_c":observed_num if evaluated else None,
                "error_ar1_c":e,
                "error_persistencia_c":ep,
                "mae_beneficio_c":round(abs(ep)-abs(e),5) if evaluated else None,
                "fecha_minima_verificacion":release.isoformat(),
                "estado":"verificado_con_serie_revisada" if evaluated else
                    "esperando_dato_fuente" if is_mature else "mes_aun_no_maduro"
            })
    verified=[x for x in all_predictions if x["estado"]=="verificado_con_serie_revisada"]
    true_before=[x for x in verified if x["emitido_antes_de_inicio_mes"]]
    summary=[]
    for h in (1,2,3):
        items=[x for x in true_before if x["horizonte_meses"]==h]
        summary.append({
            "horizonte_meses":h,"n_meses_realmente_pronosticados_antes_del_inicio":len(items),
            "mae_ar1_c":round(sum(abs(x["error_ar1_c"]) for x in items)/len(items),4) if items else None,
            "mae_persistencia_c":round(sum(abs(x["error_persistencia_c"]) for x in items)/len(items),4) if items else None,
            "habilidad_prospectiva_demostrada":False,
            "muestra_suficiente_para_evaluacion":len(items)>=12
        })
    latest=max(all_predictions,key=lambda x:x["emision_utc"]) if all_predictions else None
    latest_origin=latest["mes_origen"] if latest else None
    earliest=min((x["fecha_minima_verificacion"] for x in all_predictions),default=None)
    record={
        "fase":"8A",
        "estado":"con_verificaciones_exploratorias" if verified else "pendiente_maduracion_oceanica",
        "ultima_actualizacion_utc":now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "ultima_emision_almacenada":f"datos/pronosticos_oceanicos_emitidos/{latest_origin}.json" if latest_origin else None,
        "ultimo_mes_observado":max(observed),
        "numero_emisiones":len(set(x["emision_utc"] for x in all_predictions)),
        "pronosticos_archivados":len(all_predictions),
        "predicciones_previas_al_inicio_mes":sum(x["emitido_antes_de_inicio_mes"] for x in all_predictions),
        "estimaciones_intramensuales":sum(not x["emitido_antes_de_inicio_mes"] for x in all_predictions),
        "predicciones_verificadas":len(verified),
        "predicciones_verificadas_previas_al_mes":len(true_before),
        "primera_fecha_verificacion_posible":earliest,
        "demora_comprobacion":"No antes del día 10 del mes posterior al mes objetivo y solo cuando NOAA registre un valor finito",
        "estadisticas_por_horizonte_previas_al_mes":summary,
        "ultima_emision_pronosticos": [
            {k:item[k] for k in ("mes_objetivo","horizonte_meses",
               "emitido_antes_de_inicio_mes","pronostico_ar1_c","persistencia_c","estado",
               "fecha_minima_verificacion")}
            for item in all_predictions if item["mes_origen"]==latest_origin
        ] if latest_origin else [],
        "es_icen_oficial":False,
        "es_alerta_enfen":False,
        "son_proyecciones_oceanicas_experimentales":True,
        "validacion_operativa":False,
        "limitaciones":[
            "Las anomalías reconstruidas por OAF no son el ICEN publicado por ENFEN.",
            "Proyección de Niño 1+2 no equivale a predicción de lluvia o enfermedades en Lambayeque.",
            "El modelo univariado AR(1) NO demostró superar de forma consistente a persistencia.",
            "Pronósticos intramensuales no cuentan como emisiones anteriores al inicio del mes.",
            "La comprobación posterior usa anomalías NOAA potencialmente revisadas; no observaciones instrumentales independientes.",
            "No clasificar El Niño Costero ni presentar probabilidades ENSO con este producto."
        ]
    }
    # Avoid unsolicited revisions to frozen original emission documents.
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with DETAIL.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        for x in verified:
            w.writerow({k:x[k] for k in FIELDS})
    print("Fase 8A verificación:",record["estado"],"emitidos:",record["pronosticos_archivados"],
          "verificados:",len(verified),"anteriores al mes:",len(true_before))
    return record


def self_test():
    assert move("2026-12",1)=="2027-01"
    assert move("2026-09",3)=="2026-12"
    assert move("2026-01",-1)=="2025-12"
    now=datetime(2026,10,15,9,30,tzinfo=LOCAL)
    monthly={"2026-09":4.389}
    base={"fase":"6D","fuente":"NOAA NCEI","es_icen_oficial":False,
          "es_alerta":False,"no_es_clasificacion_enfen":True,
          "serie_noaa_orig_anom_base":"1971-2000",
          "serie_oaf_ajustada_base":"1991-2020",
          "prediccion_actual_disponible":True,
          "contraste_cpc_ersstv5":{"calidad_suficiente":True},
          "mes_ultimo_observado":"2026-09","ultima_anomalia_ersstv5_c":4.389,
          "modelos_horizontes":{
              str(i):{"mes_objetivo":move("2026-09",i),
                       "pronostico_ar1_c":4.389-i*.1,
                       "pronostico_persistencia_c":4.389}
              for i in (1,2,3)
          }}
    # Standalone test should not depend on files being available: monkeypatch
    # only the two SHA input reads when invoking the archive function.
    original_model,original_obs=MODEL,OBS
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            globals()["MODEL"]=Path(d)/"m.json"
            globals()["OBS"]=Path(d)/"o.csv"
            MODEL.write_text("test",encoding="utf-8")
            OBS.write_text("test",encoding="utf-8")
            frozen=archive_model(base,monthly,now)
    finally:
        globals()["MODEL"]=original_model
        globals()["OBS"]=original_obs
    assert len(frozen["pronosticos"])==3
    assert [x["emitido_antes_de_inicio_mes"] for x in frozen["pronosticos"]]==[False,True,True]
    assert frozen["pronosticos"][0]["clase_emision"]=="estimacion_intramensual_nowcast"
    try:
        archive_model({**base,"es_icen_oficial":True},monthly,now)
    except ValueError:
        pass
    else:
        raise AssertionError("Official ICEN mislabel was not rejected")
    assert month_day(move("2026-10",1),10)==date(2026,11,10)
    print("Fase 8A pruebas: nov/dic, nowcast, fuente, integridad mensual y latencia PASSED")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--snapshot",action="store_true")
    p.add_argument("--verify",action="store_true")
    args=p.parse_args()
    if args.self_test:self_test();return
    if args.snapshot or not args.verify:
        freeze()
    if args.verify or not args.snapshot:
        verify()


if __name__=="__main__":
    try:main()
    except Exception as e:
        print("ERROR Fase 8A:",e,file=sys.stderr)
        raise SystemExit(1)
