#!/usr/bin/env python3
"""OAF-Lambayeque fase 7C — control de calidad, NO modelo de enfermedad.

Los registros privados se conservan en datos/_privados/botrytis_7c/ y están
excluidos por .gitignore. En GitHub solo se publica un estado agregado prudente.
Las plantillas publicadas están VACÍAS y no constituyen observaciones.

Uso: python modelos/validar_campo_botrytis_7c.py
     python modelos/validar_campo_botrytis_7c.py --self-test
     python modelos/validar_campo_botrytis_7c.py --input-dir PATH --output PATH
"""
import argparse
import csv
import json
import math
import re
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PRIVATE_DIR = Path("datos/_privados/botrytis_7c")
REPORT = Path("datos/estado_campo_botrytis_7c.json")
SAMPLE_NAME = "monitoreo_botrytis.csv"
SENSOR_NAME = "microclima_horario.csv"
SAMPLE_FIELDS = [
    "id_evaluacion", "fecha_muestreo_local", "id_parcela_anonimo",
    "departamento", "provincia", "distrito", "cultivo", "variedad",
    "fenologia", "unidad_muestreo", "unidades_evaluadas",
    "unidades_con_sintomas", "descripcion_signos_sintomas",
    "estado_diagnostico", "metodo_diagnostico", "fecha_diagnostico_local",
    "riego_aspersion_ultimos_7d", "fungicida_ultimos_14d",
    "codigo_evidencia", "observaciones_tecnicas"
]
SENSOR_FIELDS = [
    "id_lectura", "fecha_hora_local", "id_parcela_anonimo", "id_sensor",
    "tipo_sensor", "altura_m", "temperatura_dosel_c", "hr_dosel_pct",
    "humectacion_foliar_binaria", "radiacion_w_m2", "precipitacion_mm",
    "control_calibracion"
]
PROVINCES = {"chiclayo", "lambayeque", "ferreñafe"}
PHENOLOGIES = {
    "vegetativo", "prefloracion", "floracion", "cuajado", "maduracion",
    "cosecha", "postcosecha", "desconocida"
}
SAMPLE_UNITS = {"flor", "racimo_floral", "fruto", "planta"}
DIAGNOSES = {
    "sin_analisis", "sospechoso", "compatible_laboratorio",
    "confirmado_botrytis_cinerea", "descartado"
}
METHODS = {
    "ninguno", "inspeccion_visual", "microscopia",
    "aislamiento_morfologia", "pcr_especifica", "secuenciacion"
}
SENSOR_TYPES = {"dosel_combinado", "humectacion_hoja", "estacion_meteorologica"}
YES_NO_UNKNOWN = {"si", "no", "desconocido"}
ID = re.compile(r"^[A-Za-z0-9_-]{3,40}$")


def load(path, fields):
    """Missing files are legitimate; wrong headers or malformed CSV are not."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != fields:
            raise ValueError("Esquema CSV de campo incorrecto: "+path.name)
        rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError("Columnas excedentes en "+path.name)
        return rows


def parse_date(value, label):
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Formato no YYYY-MM-DD")
        d = date.fromisoformat(value)
        if d > datetime.now(timezone.utc).date():
            raise ValueError("Fecha futura")
        return d
    except (TypeError, ValueError) as err:
        raise ValueError(label+": fecha inválida") from err


def local_datetime(value):
    if not isinstance(value,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00-05:00",value):
        raise ValueError("La lectura debe llevar fecha/hora con huso Perú -05:00")
    dt=datetime.fromisoformat(value)
    if dt.utcoffset()!=timedelta(hours=-5) or dt.minute!=0 or dt.second!=0:
        raise ValueError("La lectura debe ser horaria y en America/Lima")
    if dt.astimezone(timezone.utc)>datetime.now(timezone.utc):
        raise ValueError("Lectura futura")
    return dt


def to_number(value, label, minimum, maximum, optional=False):
    if optional and value in ("",None):return None
    try:
        x=float(value)
        if not math.isfinite(x) or not minimum<=x<=maximum:raise ValueError()
        return x
    except (ValueError,TypeError) as err:
        raise ValueError(label+": valor fuera de rango o ausente") from err


def to_count(value, label):
    try:
        if not isinstance(value,str) or not re.fullmatch(r"\d+",value):raise ValueError()
        n=int(value)
        if n>100000:raise ValueError()
        return n
    except ValueError as err:
        raise ValueError(label+": entero no negativo obligatorio") from err


def check_id(value,label):
    if not isinstance(value,str) or not ID.fullmatch(value):
        raise ValueError(label+": identificador anónimo inválido")


def validate_sample(row):
    check_id(row["id_evaluacion"],"id_evaluacion")
    check_id(row["id_parcela_anonimo"],"id_parcela_anonimo")
    sampled=parse_date(row["fecha_muestreo_local"],"muestreo")
    if row["departamento"].strip().lower()!="lambayeque":
        raise ValueError("La región debe ser Lambayeque")
    if row["provincia"].strip().lower() not in PROVINCES:
        raise ValueError("Provincia no reconocida como Lambayeque")
    if not row["distrito"].strip() or not row["variedad"].strip():
        raise ValueError("Distrito y variedad deben identificarse")
    if row["cultivo"].lower().strip() not in ("arandano","arándano"):
        raise ValueError("El cultivo de esta ficha es arándano")
    if row["fenologia"] not in PHENOLOGIES or row["unidad_muestreo"] not in SAMPLE_UNITS:
        raise ValueError("Fenología o unidad de muestreo no definida")
    total=to_count(row["unidades_evaluadas"],"unidades_evaluadas")
    signs=to_count(row["unidades_con_sintomas"],"unidades_con_sintomas")
    if total<1 or signs>total:
        raise ValueError("El conteo sintomático debe estar entre 0 y el total")
    diagnosis=row["estado_diagnostico"]
    method=row["metodo_diagnostico"]
    if diagnosis not in DIAGNOSES or method not in METHODS:
        raise ValueError("Diagnóstico o método fuera del diccionario")
    if diagnosis=="confirmado_botrytis_cinerea":
        if signs==0 or method not in ("pcr_especifica","secuenciacion"):
            raise ValueError("Confirmación de especie requiere síntomas y método molecular específico")
        day=parse_date(row["fecha_diagnostico_local"],"fecha de confirmación")
        if day<sampled:raise ValueError("La confirmación precede al muestreo")
    elif row["fecha_diagnostico_local"]:
        d=parse_date(row["fecha_diagnostico_local"],"diagnóstico")
        if d<sampled:raise ValueError("Fecha diagnóstica anterior al muestreo")
    if diagnosis=="sin_analisis" and method!="ninguno":
        raise ValueError("Sin análisis no puede tener método confirmatorio")
    if diagnosis=="descartado" and method in ("ninguno","inspeccion_visual"):
        raise ValueError("No descartar Botrytis solo por inspección visual")
    for name in ("riego_aspersion_ultimos_7d","fungicida_ultimos_14d"):
        if row[name] not in YES_NO_UNKNOWN:raise ValueError("Manejo requiere si/no/desconocido")
    # Incidencia de síntomas = signos/total; NO incidencia confirmada por Botrytis.
    return {"parcela":row["id_parcela_anonimo"],"dia":sampled,"fenologia":row["fenologia"],
            "unidad":row["unidad_muestreo"],"n":total,"sintomas":signs,
            "estado_diagnostico":diagnosis}


def validate_sensor(row):
    for name in ("id_lectura","id_parcela_anonimo","id_sensor"):
        check_id(row[name],name)
    stamp=local_datetime(row["fecha_hora_local"])
    if row["tipo_sensor"] not in SENSOR_TYPES:
        raise ValueError("Tipo de sensor no admitido")
    to_number(row["altura_m"],"altura",0.05,8)
    to_number(row["temperatura_dosel_c"],"temperatura dosel",-20,55)
    to_number(row["hr_dosel_pct"],"HR dosel",0,100)
    to_number(row["radiacion_w_m2"],"radiación",0,1600,optional=True)
    to_number(row["precipitacion_mm"],"lluvia horaria",0,300,optional=True)
    wet=row["humectacion_foliar_binaria"]
    if wet not in ("","0","1"):raise ValueError("La humectación solo admite 0/1/sin dato")
    if wet and row["tipo_sensor"] not in ("dosel_combinado","humectacion_hoja"):
        raise ValueError("No confundir lectura de estación con sensor de humectación foliar")
    if row["control_calibracion"] not in YES_NO_UNKNOWN:
        raise ValueError("Falta estado explícito de calibración")
    return {"parcela":row["id_parcela_anonimo"],"hora":stamp,
            "wet_measured":wet in ("0","1"),"wet_positive":wet=="1",
            "wet_verified":wet in ("0","1") and row["control_calibracion"]=="si"}


def inspect(input_dir):
    samples=load(input_dir/SAMPLE_NAME,SAMPLE_FIELDS)
    sensors=load(input_dir/SENSOR_NAME,SENSOR_FIELDS)
    valid_s,valid_m=[],[]
    errors=[]
    seen_s,seen_m,seen_sensor_hours=set(),set(),set()
    for index,row in enumerate(samples,start=2):
        try:
            entry=validate_sample(row)
            if row["id_evaluacion"] in seen_s:raise ValueError("id_evaluacion duplicado")
            seen_s.add(row["id_evaluacion"])
            valid_s.append(entry)
        except (ValueError,KeyError,AttributeError) as error:
            errors.append(("monitoreo",index,str(error)))
    for index,row in enumerate(sensors,start=2):
        try:
            entry=validate_sensor(row)
            key=(row["id_sensor"],row["fecha_hora_local"])
            if row["id_lectura"] in seen_m or key in seen_sensor_hours:
                raise ValueError("Lectura duplicada de sensor/hora")
            seen_m.add(row["id_lectura"]);seen_sensor_hours.add(key)
            valid_m.append(entry)
        except (ValueError,KeyError,AttributeError) as error:
            errors.append(("microclima",index,str(error)))
    plots_s={x["parcela"] for x in valid_s}
    plots_m={x["parcela"] for x in valid_m}
    overlap=plots_s&plots_m
    return {"samples":samples,"sensors":sensors,"valid_samples":valid_s,
            "valid_sensors":valid_m,"errors":errors,"overlap":overlap,
            "unique_plots":plots_s|plots_m}


def public_report(checked):
    samples=checked["valid_samples"]
    sensors=checked["valid_sensors"]
    invalid=len(checked["errors"])
    has_raw=bool(checked["samples"] or checked["sensors"])
    has_wet=any(r["wet_verified"] for r in sensors)
    has_diag=any(r["estado_diagnostico"]=="confirmado_botrytis_cinerea" for r in samples)
    state=("sin_datos_campo" if not has_raw else
           "requiere_correccion" if invalid else
           "solo_vigilancia_sin_validacion" if not (checked["overlap"] and has_wet and has_diag) else
           "datos_parciales_pendientes_de_validacion")
    # No sample IDs, person names, GPS coordinates, photos or exact private dates
    # ever enter this report or the repository.
    publish_counts = len(checked["unique_plots"])>=5
    return {
        "fase":"7C",
        "fecha_generacion_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado":state,
        "fuentes":"archivos locales privados / plantillas de monitoreo y microclima",
        "hay_registros_campo":has_raw,
        "hay_errores_formato":bool(invalid),
        "n_errores_validacion":invalid,
        "conteos_ocultos_por_confidencialidad":not publish_counts and has_raw,
        "datos_publicos_agregados":(
            {"evaluaciones_validas":len(samples),"lecturas_validas":len(sensors),
             "parcelas_con_ambas_fuentes":len(checked["overlap"]),
             "lecturas_humectacion_calibradas":sum(x["wet_verified"] for x in sensors),
             "evaluaciones_con_diagnostico_especifico":sum(x["estado_diagnostico"]=="confirmado_botrytis_cinerea" for x in samples)}
            if publish_counts else None
        ),
        "se_calculo_incidencia_fitopatologica":False,
        "hay_modelo_predictivo_de_infeccion":False,
        "modelo_ajustado_con_datos_campo":False,
        "probabilidad_infeccion_calibrada":False,
        "validacion_prospectiva_en_parcela":False,
        "alerta_fitosanitaria":False,
        "criterios_pendientes":[
            "Casos sintomáticos, confirmados y negativos observados en campo con fechas",
            "Unidades de muestreo homogéneas y denominadores comprobados",
            "Humectación real con sensor calibrado y hora local trazable",
            "Vinculación de parcela-fecha a pronósticos archivados ANTES del evento",
            "Cobertura temporal y espacial independiente de entrenamiento y prueba"
        ],
        "advertencias":[
            "Síntomas sospechosos no equivalen a Botrytis cinerea confirmada.",
            "Un campo sin registros no significa incidencia cero.",
            "Este módulo valida estructura de datos; no estima daño ni recomienda tratamientos.",
            "Las parcelas se identifican por códigos anónimos en ficheros privados, nunca con coordenadas públicas.",
            "La señal de HR >90% durante >=6 h continúa siendo exploratoria."
        ]
    }


def write_privately(checked, private_dir):
    # For local investigator only, never upload; default directory ignored by git.
    private_dir.mkdir(parents=True,exist_ok=True)
    errors=[{"archivo":name,"fila":row,"motivo":message} for name,row,message in checked["errors"]]
    (private_dir/"reporte_qa_privado.json").write_text(
        json.dumps({"errores":errors,
                    "evaluaciones_validas":len(checked["valid_samples"]),
                    "lecturas_validas":len(checked["valid_sensors"])},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def self_test():
    with tempfile.TemporaryDirectory() as temp:
        directory=Path(temp)
        blank=inspect(directory)
        assert public_report(blank)["estado"]=="sin_datos_campo"
        sample=dict.fromkeys(SAMPLE_FIELDS,"")
        sample.update({
            "id_evaluacion":"E001","fecha_muestreo_local":"2026-09-12",
            "id_parcela_anonimo":"P001","departamento":"Lambayeque",
            "provincia":"Lambayeque","distrito":"Motupe","cultivo":"arandano",
            "variedad":"variedad_sin_identificar","fenologia":"floracion",
            "unidad_muestreo":"racimo_floral","unidades_evaluadas":"50",
            "unidades_con_sintomas":"4","estado_diagnostico":"sospechoso",
            "metodo_diagnostico":"inspeccion_visual",
            "riego_aspersion_ultimos_7d":"no","fungicida_ultimos_14d":"desconocido"})
        sensor=dict.fromkeys(SENSOR_FIELDS,"")
        sensor.update({
            "id_lectura":"L001","fecha_hora_local":"2026-09-11T11:00:00-05:00",
            "id_parcela_anonimo":"P001","id_sensor":"S001",
            "tipo_sensor":"dosel_combinado","altura_m":"1.2",
            "temperatura_dosel_c":"22.1","hr_dosel_pct":"93",
            "humectacion_foliar_binaria":"1","control_calibracion":"si"})
        assert validate_sample(sample)["sintomas"]==4
        assert validate_sensor(sensor)["wet_verified"]
        bad={**sample,"unidades_con_sintomas":"51"}
        try:validate_sample(bad)
        except ValueError:pass
        else:raise AssertionError("Numerator > denominator accepted")
        bad2={**sample,"estado_diagnostico":"confirmado_botrytis_cinerea"}
        try:validate_sample(bad2)
        except ValueError:pass
        else:raise AssertionError("Visual diagnosis accepted as species confirmation")
        bad3={**sensor,"fecha_hora_local":"2026-09-11T11:00:00"}
        try:validate_sensor(bad3)
        except ValueError:pass
        else:raise AssertionError("Local time without UTC offset accepted")
        def write(path,fields,rows):
            with path.open("w",newline="",encoding="utf-8") as file:
                w=csv.DictWriter(file,fieldnames=fields)
                w.writeheader();w.writerows(rows)
        write(directory/SAMPLE_NAME,SAMPLE_FIELDS,[sample])
        write(directory/SENSOR_NAME,SENSOR_FIELDS,[sensor])
        checked=inspect(directory)
        assert not checked["errors"] and len(checked["overlap"])==1
        report=public_report(checked)
        assert report["estado"]=="solo_vigilancia_sin_validacion"
        assert report["datos_publicos_agregados"] is None
        assert not report["hay_modelo_predictivo_de_infeccion"]
        write(directory/SAMPLE_NAME,SAMPLE_FIELDS,[sample,sample])
        assert inspect(directory)["errors"]
    print("OAF 7C PASS: blank data, valid field+sensor, duplicates, diagnostic, time zone, privacy, no disease forecast")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--input-dir",type=Path,default=PRIVATE_DIR)
    parser.add_argument("--output",type=Path,default=REPORT)
    args=parser.parse_args()
    if args.self_test:self_test();return
    checked=inspect(args.input_dir)
    summary=public_report(checked)
    # QA details stay private; the public artifact contains no raw field rows.
    if checked["samples"] or checked["sensors"]:
        write_privately(checked,args.input_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("7C estado:",summary["estado"],"datos reales:",summary["hay_registros_campo"],
          "errores:",summary["n_errores_validacion"],"modelo de infección:",False)


if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("OAF 7C QA ERROR:",str(exc),file=sys.stderr)
        raise SystemExit(1)
