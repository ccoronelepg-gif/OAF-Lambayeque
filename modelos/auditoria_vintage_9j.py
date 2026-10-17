#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF fase 9J: auditoría *as-issued* de emisiones 6F, 8E y 8A.
No calcula habilidad sin verificaciones maduras; ningún hindcast se declara emisión real.
Python estándar, sin acceso de red. Requiere git con historia completa para prueba de contenido.
"""
import argparse
import csv
import hashlib
import json
import math
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"datos/auditoria_vintage_9j"
SOURCES=BASE/"manifiesto_fuentes_9j.json"
REPORT=BASE/"estado_prospectivo_9j.json"
CUT=date(2026,10,17)
PERU=ZoneInfo("America/Lima")
CITIES=("Chiclayo","Jayanca","Motupe","Olmos")
DAILY_VARS={"temperature_2m_mean":"°C","precipitation_sum":"mm",
            "shortwave_radiation_sum":"MJ/m²"}

def jread(path):
    return json.loads(path.read_text(encoding="utf8"))

def timestamp(value):
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.tzinfo is None: raise ValueError("Emisión sin zona horaria")
    return d.astimezone(timezone.utc)

def decimal(value):
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError("Pronóstico numérico ausente o no finito")
    return float(value)

def month_plus(month,n):
    y,m=map(int,month.split("-"))
    i=y*12+m-1+n
    return f"{i//12:04d}-{i%12+1:02d}"

def monthly_eligible(month):
    return date.fromisoformat(month_plus(month,1)+"-10")

def archive_proof(path,sha,root=ROOT):
    """Comprueba que el contenido actual coincide con lo registrado EN ESE commit."""
    original=subprocess.run(["git","show",f"{sha}:{path}"],cwd=root,
                 capture_output=True,check=False)
    if original.returncode:
        raise ValueError("Falta commit histórico / checkout shallow: "+path)
    now=(root/path).read_bytes()
    if now!=original.stdout:
        raise ValueError("Archivo original modificado tras el commit: "+path)
    return hashlib.sha256(now).hexdigest()

def daily_audit(manifest,root=ROOT,cut=CUT):
    issues=manifest["archivos_diarios"]
    if [s["fecha"] for s in issues]!=["2026-10-14","2026-10-15","2026-10-16","2026-10-17"]:
        raise ValueError("Inventario original diario modificado")
    details=[]
    total=0
    unique_valid=set()
    earliest=None
    for src in issues:
        path=src["path"]
        issue_day=date.fromisoformat(src["fecha"])
        original_sha=src["primer_commit"]
        if src["path"]!=f"datos/pronosticos_emitidos/{issue_day.isoformat()}.json":
            raise ValueError("Nombre no coincide con fecha")
        digest=archive_proof(path,original_sha,root)
        rec=jread(root/path)
        if rec.get("tipo")!="pronostico_meteorologico_externo_archivado":
            raise ValueError("Pronóstico externo mal clasificado")
        if rec.get("son_predicciones_propias_oaf") is not False or rec.get("son_alertas_fitosanitarias") is not False:
            raise ValueError("Alerta o pronóstico propio falsamente atribuido")
        emit=timestamp(rec["emision_utc"])
        commit=timestamp(src["fecha_commit_utc"])
        if emit.astimezone(PERU).date()!=issue_day:
            raise ValueError("Emisión UTC y fecha peruana no coinciden")
        if commit < emit-timedelta(minutes=1):
            raise ValueError("Commit es anterior a emisión declarada")
        if rec.get("fecha_consulta_local")!=issue_day.isoformat():
            raise ValueError("Fecha del archivo diferente de consulta")
        local=datetime.fromisoformat(rec["consulta_local_peru"])
        if local.tzinfo is None or abs((local.astimezone(timezone.utc)-emit).total_seconds())>90:
            raise ValueError("Hora local/UTC contradictorias")
        sites=rec.get("localidades")
        if not isinstance(sites,dict) or set(sites)!=set(CITIES):
            raise ValueError("Cuatro localidades requeridas en emisión diaria")
        for city in CITIES:
            info=sites[city]
            days=info["jornadas_futuras"]
            if len(days)!=7:raise ValueError("Siete fechas futuras requeridas")
            for step,row in enumerate(days,1):
                valid=issue_day+timedelta(days=step)
                if row["fecha_valida"]!=valid.isoformat():
                    raise ValueError("Horizon erróneo")
                # Verificabilidad pública reforzada: el commit ya existía antes del día válido.
                if commit.astimezone(PERU).date()>=valid:
                    raise ValueError("Commit demasiado tardío para probar pronóstico previo: "+path)
                for field,unit in DAILY_VARS.items():
                    decimal(row[field])
                    if info.get("unidades",{}).get(field) not in (
                        (unit,"MJ/m2") if field=="shortwave_radiation_sum" else (unit,)):
                        raise ValueError("Unidad incompatible: "+field)
                total+=1
                unique_valid.add((city,valid.isoformat()))
                target=valid+timedelta(days=7)
                earliest=min(earliest,target) if earliest else target
        details.append({"fecha_emision_local":src["fecha"],"emision_utc":rec["emision_utc"],
                        "commit_git":original_sha,"commit_utc":src["fecha_commit_utc"],
                        "archivo":path,"sha256_contenido":digest,
                        "n_localidad_dia_pronosticados":28,
                        "primera_fecha_valida":(issue_day+timedelta(days=1)).isoformat(),
                        "primera_fecha_elegible":(issue_day+timedelta(days=8)).isoformat(),
                        "conteo_verificable_al_corte":sum(1 for n in range(1,8) if
                            issue_day+timedelta(days=n+7)<=cut)*4})
    return {"producto":"Open-Meteo Forecast API (externo, no modelo OAF)",
            "n_emisiones":len(details),"n_localidad_dia_pronosticados":total,
            "n_localidad_dia_valido_unicos":len(unique_valid),
            "n_emisiones_con_commit_y_bytes_comprobados":len(details),
            "fecha_primer_contraste_posible":earliest.isoformat() if earliest else None,
            "n_comparables_temporalmente_al_corte":sum(e["conteo_verificable_al_corte"] for e in details),
            "estado":"pendiente_de_reanalisis" if cut<earliest else "comprobar_reanalisis_en_fase_6G",
            "emisiones":details}

def monthly_8e(root=ROOT,cut=CUT):
    rootpath=root/"datos/pronosticos_temperatura_regional_8e"
    arr=sorted(rootpath.glob("????-??.json"))
    old=jread(root/"datos/verificacion_temperatura_regional_8e.json")
    if old.get("fase")!="8E" or old.get("habilidad_prospectiva_demostrada") is not False:
        raise ValueError("Estado 8E incompatible")
    counts={"premes":0,"intramensual":0,"maduras_al_corte":0}
    first=None; entries=[]
    for file in arr:
        rec=jread(file)
        if rec["fase"]!="8E" or rec["mes_origen"]!=file.stem or rec["validacion_instrumental"] is not False:
            raise ValueError("Emisión 8E inválida")
        issued=timestamp(rec["emision_utc"]).astimezone(PERU).date()
        if issued>cut:
            continue
        records=rec["pronosticos"]
        if len(records)!=12:raise ValueError("Emisión 8E sin doce pronósticos")
        for item in records:
            h=item["horizonte_meses"]; m=item["mes_objetivo"]
            if type(h)!=int or h not in (1,2,3) or m!=month_plus(rec["mes_origen"],h):
                raise ValueError("Horizonte mensual alterado")
            pre=issued<date.fromisoformat(m+"-01")
            if item["emitido_antes_inicio_mes"] is not pre:
                raise ValueError("Etiqueta premensual incorrecta")
            if item["tipo_emision"]!=("pronostico_antes_inicio_mes" if pre else "estimacion_intramensual"):
                raise ValueError("Clasificación 8E incorrecta")
            if item["localidad"] not in CITIES:raise ValueError("Localidad no prevista")
            for k in ("pronostico_local_c","pronostico_nino_t300_c",
                      "climatologia_cero_c","persistencia_anomalia_c"):
                decimal(item[k])
            eligibility=monthly_eligible(m)
            counts["premes" if pre else "intramensual"]+=1
            if eligibility<=cut:counts["maduras_al_corte"]+=1
            first=min(first,eligibility) if first else eligibility
        entries.append({"mes_origen":rec["mes_origen"],"fecha_emision_utc":rec["emision_utc"],
                        "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                        "n_registros":len(records)})
    if old["pronosticos_originales_archivados"]!=counts["premes"]+counts["intramensual"]:
        raise ValueError("Libro 8E no sincronizado")
    if old["pronosticos_anteriores_al_mes"]!=counts["premes"]:
        raise ValueError("Libro 8E cambió premes")
    if old["pronosticos_comparados"]!=0 and cut<first:
        raise ValueError("Fuga temporal en verificaciones 8E")
    return {"producto":"Modelo OAF 8E temperatura mensual experimental",
            "n_emisiones":len(entries),"n_predicciones_premes":counts["premes"],
            "n_nowcasts_intramensuales":counts["intramensual"],
            "n_temporalmente_elegibles":counts["maduras_al_corte"],
            "n_contrastes_en_libro_8e":old["pronosticos_comparados"],
            "primera_fecha_elegible_teorica":first.isoformat() if first else None,
            "primera_validacion_premes_teorica":"2026-12-10",
            "clasificacion":"temperatura de rejilla frente a ERA5-Land, no sensor SENAMHI",
            "emisiones":entries}

def ocean_8a(root=ROOT,cut=CUT):
    files=sorted((root/"datos/pronosticos_oceanicos_emitidos").glob("????-??.json"))
    npre=0; nintra=0; entries=[]
    for file in files:
        rec=jread(file)
        if rec["fase"]!="8A" or rec["mes_origen"]!=file.stem or rec["prediccion_elnino_costero_validada"] is not False:
            raise ValueError("Registro 8A inválido")
        issued=timestamp(rec["emision_utc"]).astimezone(PERU).date()
        if issued>cut: continue
        for item in rec["pronosticos"]:
            m=item["mes_objetivo"];h=item["horizonte_meses"]
            if m!=month_plus(file.stem,h):raise ValueError("Objetivo oceánico incorrecto")
            pre=issued<date.fromisoformat(m+"-01")
            if item["emitido_antes_de_inicio_mes"] is not pre:raise ValueError("Clase 8A no coincide")
            for k in ("pronostico_ar1_c","persistencia_c"):decimal(item[k])
            npre+=int(pre); nintra+=int(not pre)
        entries.append({"origen":file.stem,"emision_utc":rec["emision_utc"],
                        "sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
    return {"producto":"AR(1) propio de SST Niño 1+2 (no ICEN ni alerta ENFEN)",
            "n_emisiones":len(entries),"n_predicciones_premes":npre,
            "n_nowcasts_intramensuales":nintra,
            "n_contrastes_realizados_en_fase_9j":0,
            "primera_fecha_objetivo_para_contrastar":"2026-10",
            "nota":"La publicación/revisión del índice NOAA determina la disponibilidad de su observación, no un plazo inventado.",
            "emisiones":entries}

def build(root=ROOT,cut=CUT):
    manifest=jread(root/"datos/auditoria_vintage_9j/manifiesto_fuentes_9j.json")
    if cut.isoformat()!=manifest["corte_local"]:raise ValueError("Corte 9J no corresponde al preregistro")
    daily=daily_audit(manifest,root,cut)
    monthly=monthly_8e(root,cut)
    ocean=ocean_8a(root,cut)
    sixg=jread(root/"datos/evaluacion_prospectiva_6g.json")
    eightg=jread(root/"datos/evaluacion_prospectiva_8g/metricas_8g.json")
    if sixg["fase"]!="6G" or eightg["fase"]!="8G":raise ValueError("Verificaciones origen incorrecto")
    if sixg["jornadas_verificadas"]>0 and cut<date.fromisoformat(daily["fecha_primer_contraste_posible"]):
        raise ValueError("6G adelantó verificación")
    if eightg["n_verificados_total"]>0 and cut<date.fromisoformat(monthly["primera_fecha_elegible_teorica"]):
        raise ValueError("8G adelantó verificación")
    pending=[
      {"evento":"Primer pronóstico diario Open-Meteo elegible contra ERA5/ERA5-Land",
       "fecha_minima":"2026-10-22","estado":"futuro_al_corte"},
      {"evento":"Temperatura OAF octubre 2026 (intramensual, no premés)",
       "fecha_minima":"2026-11-10","estado":"futuro_al_corte"},
      {"evento":"Temperatura OAF noviembre 2026 (emisión premes)",
       "fecha_minima":"2026-12-10","estado":"futuro_al_corte"}
    ]
    return {"fase":"9J","corte_local":cut.isoformat(),"zona_horaria":"America/Lima",
      "tipo":"auditoria_de_temporalidad_y_preparacion_prospectiva",
      "estado":"sin_verificaciones_maduras_al_corte",
      "oaf_habilidad_prospectiva_demostrada":False,
      "enso_nino_costero_predictivo_validado":False,
      "alertas_fitosanitarias_derivadas":False,
      "normal_1996_2025_validada_instrumentalmente":False,
      "pronosticos_sst_nino12_no_son_ICEN":True,
      "diarios_externos":daily,"temperatura_mensual_propia":monthly,
      "sst_mensual_propia":ocean,
      "verificacion_externa_6g":{"n_dias_verificados":sixg["jornadas_verificadas"],
         "reporte_fase":"6G","fuente_contraste":"ERA5 / ERA5-Land posterior; no estación"},
      "verificacion_temperatura_8g":{"n_pronosticos_verificados":eightg["n_verificados_total"],
          "reporte_fase":"8G","fuente_contraste":"ERA5-Land posterior; no estación"},
      "metricas_predictivas_observadas":{"MAE":None,"RMSE":None,
           "sesgo":None,"mejora_frente_persistencia":None,
           "probabilidades_calibradas":None},
      "fechas_control":pending,
      "inventario_estacional_NOAA_C3S":manifest["fuentes_estacionales_candidatas"],
      "predicciones_estacionales_NOAA_descargadas_y_verificadas_n":0,
      "advertencias":[
        "La comprobación git demuestra que se conservan bytes idénticos en commits históricos; no certifica horas externas al repositorio ni la exactitud meteorológica.",
        "Las múltiples emisiones de una misma fecha válida no constituyen observaciones independientes.",
        "Los pronósticos diarios archivados corresponden a Open-Meteo, no a un modelo propio del OAF.",
        "Las emisiones OAF de octubre sobre octubre son intramensuales, no predicciones anteriores al mes.",
        "NMME real-time y sus hindcasts se deben separar por tipo, inicialización, modelo, resolución y emisión original.",
        "No hay validación sobre parcelas, pluviómetros ni enfermedades de arándano o vid."
      ]}
def run(check=False):
    result=build()
    if check:
        if result!=jread(REPORT):raise ValueError("El informe no se reproduce exactamente")
    else:
        BASE.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("9J:",result["diarios_externos"]["n_localidad_dia_pronosticados"],
          "pronósticos externos; elegibles:",
          result["diarios_externos"]["n_comparables_temporalmente_al_corte"],
          "; OAF temperatura premes:",
          result["temperatura_mensual_propia"]["n_predicciones_premes"])
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    run(check=args.check)
