#!/usr/bin/env python3
"""OAF-Lambayeque 8G: auditar emisiones inmutables y evaluar errores reales.

Lee exclusivamente las emisiones originales 8E, el CSV de contraste posterior
con ERA5-Land y el informe de verificación 8E. Nunca consulta una API ni
entrena, emite o modifica pronósticos. Sin una observación posterior elegible,
conserva las métricas como null. Requiere Python >=3.10, sin dependencias externas.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SITES = ("Chiclayo", "Jayanca", "Motupe", "Olmos")
MODELS = ("local", "nino_t300", "climatologia", "persistencia")
DIR_ISSUES = "datos/pronosticos_temperatura_regional_8e"
PATH_CSV = "datos/verificacion_temperatura_regional_8e.csv"
PATH_LEDGER = "datos/verificacion_temperatura_regional_8e.json"
OUTPUT = "datos/evaluacion_prospectiva_8g"
UTC_PERU = ZoneInfo("America/Lima")
DETAIL_FIELDS = (
    "emision_utc", "mes_origen", "mes_objetivo", "localidad",
    "horizonte_meses", "tipo_emision", "emitido_antes_inicio_mes",
    "estado_verificacion", "fecha_minima_verificacion", "fuente_observacion",
    "pronostico_local_c", "pronostico_nino_t300_c",
    "pronostico_climatologia_c", "pronostico_persistencia_c",
    "observacion_era5_land_c", "error_local_c", "error_nino_t300_c",
    "error_climatologia_c", "error_persistencia_c"
)
ERROR_TOLERANCE = 0.00012  # 8E conserva cinco decimales.


def month_date(month: str) -> date:
    if not isinstance(month, str) or len(month) != 7 or month[4] != "-":
        raise ValueError("Mes inválido: " + repr(month))
    if not month[:4].isdigit() or not month[-2:].isdigit():
        raise ValueError("Mes inválido: " + repr(month))
    value = date(int(month[:4]), int(month[5:]), 1)
    if value.strftime("%Y-%m") != month:
        raise ValueError("Mes no canónico")
    return value


def next_month(month: str, count: int = 1) -> str:
    d = month_date(month)
    n = d.year * 12 + d.month - 1 + count
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


def start_of_month(month: str) -> date:
    return month_date(month)


def first_eligible(month: str) -> date:
    d = month_date(next_month(month))
    return d.replace(day=10)


def timestamp(value: str) -> datetime:
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("No se acepta fecha sin zona horaria")
    return d.astimezone(timezone.utc)


def num(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError("Número inválido: " + name)
    if not math.isfinite(value):
        raise ValueError("Número no finito: " + name)
    return float(value)


def from_csv_num(value: str, name: str) -> float:
    if value is None or not value.strip():
        raise ValueError("Observación o error faltante: " + name)
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError("Valor no numérico: " + name) from None
    return num(number, name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(record) -> tuple:
    return (
        record["emision_utc"], record["mes_origen"], record["mes_objetivo"],
        record["localidad"], int(record["horizonte_meses"])
    )


def read_inputs(root: Path):
    src = root / DIR_ISSUES
    originals = sorted(src.glob("????-??.json")) if src.is_dir() else []
    report_path = root / PATH_LEDGER
    csv_path = root / PATH_CSV
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("fase") != "8E" or report.get("habilidad_prospectiva_demostrada") is not False:
        raise ValueError("Informe 8E inválido o atribuye habilidad no demostrada")
    if report.get("validacion_instrumental") is not False:
        raise ValueError("ERA5-Land no constituye validación instrumental")
    if report.get("probabilidades_calibradas") is not False:
        raise ValueError("No existe calibración probabilística prospectiva")
    cut = timestamp(report["generado_utc"])
    all_predictions = {}
    originals_info = []
    for path in originals:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        if snapshot.get("fase") != "8E" or snapshot.get("mes_origen") != path.stem:
            raise ValueError("Archivo original corrupto: " + str(path))
        if snapshot.get("validacion_instrumental") is not False or snapshot.get("habilidad_prospectiva_demostrada") is not False:
            raise ValueError("Estado de emisión indebido")
        issued = timestamp(snapshot["emision_utc"])
        if issued > cut:
            raise ValueError("El reporte es anterior a una de las emisiones")
        forecasts = snapshot.get("pronosticos")
        if not isinstance(forecasts, list) or len(forecasts) != 12:
            raise ValueError("Se requieren doce registros por emisión")
        originals_info.append({"archivo": str(path.relative_to(root)), "sha256": sha(path), "emision_utc": snapshot["emision_utc"]})
        for x in forecasts:
            city = x.get("localidad")
            h = x.get("horizonte_meses")
            target = x.get("mes_objetivo")
            if city not in SITES or type(h) is not int or h not in (1, 2, 3) or target != next_month(path.stem, h):
                raise ValueError("Localidad/objetivo/horizonte inconsistente")
            pre = issued.astimezone(UTC_PERU).date() < start_of_month(target)
            if x.get("emitido_antes_inicio_mes") is not pre:
                raise ValueError("Clasificación premes/intramensual inválida")
            classification = "pronostico_antes_inicio_mes" if pre else "estimacion_intramensual"
            if x.get("tipo_emision") != classification:
                raise ValueError("Tipo de emisión no concuerda con fecha original")
            for field in ("pronostico_local_c", "pronostico_nino_t300_c", "climatologia_cero_c", "persistencia_anomalia_c"):
                num(x.get(field), field)
            r = {
                "emision_utc": snapshot["emision_utc"],
                "mes_origen": path.stem, "mes_objetivo": target,
                "localidad": city, "horizonte_meses": h,
                "tipo_emision": classification, "emitido_antes_inicio_mes": pre,
                "pronostico_local_c": x["pronostico_local_c"],
                "pronostico_nino_t300_c": x["pronostico_nino_t300_c"],
                "pronostico_climatologia_c": x["climatologia_cero_c"],
                "pronostico_persistencia_c": x["persistencia_anomalia_c"],
                "_source": x
            }
            identity = key(r)
            if identity in all_predictions:
                raise ValueError("Emisión original duplicada")
            all_predictions[identity] = r
    if int(report["pronosticos_originales_archivados"]) != len(all_predictions):
        raise ValueError("Conteo de predicciones no coincide con informe 8E")
    if int(report["numero_emisiones_originales"]) != len(originals):
        raise ValueError("Conteo de emisiones originales no coincide")
    if int(report["pronosticos_anteriores_al_mes"]) != sum(r["emitido_antes_inicio_mes"] for r in all_predictions.values()):
        raise ValueError("Conteo premes 8E incorrecto")
    if int(report["estimaciones_intramensuales"]) != sum(not r["emitido_antes_inicio_mes"] for r in all_predictions.values()):
        raise ValueError("Conteo intramensual 8E incorrecto")

    verified = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"emision_utc", "mes_origen", "mes_objetivo", "localidad", "horizonte_meses",
                    "tipo_emision", "pronostico_local_c", "pronostico_nino_t300_c",
                    "observacion_era5_land_c", "error_local_c", "error_nino_t300_c"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV de contraste 8E sin campos requeridos")
        for row in reader:
            identity = key(row)
            if identity in verified:
                raise ValueError("Comparación duplicada")
            if identity not in all_predictions:
                raise ValueError("Comparación sin emisión original")
            original = all_predictions[identity]
            if row["tipo_emision"] != original["tipo_emision"]:
                raise ValueError("Tipo de evaluación alterado")
            if cut.astimezone(UTC_PERU).date() < first_eligible(row["mes_objetivo"]):
                raise ValueError("Comparación publicada antes de la ventana permitida")
            for field in ("pronostico_local_c", "pronostico_nino_t300_c"):
                if abs(from_csv_num(row[field],field) - original[field]) > ERROR_TOLERANCE:
                    raise ValueError("Una predicción archivada fue modificada en la tabla")
            obs = from_csv_num(row["observacion_era5_land_c"], "observacion")
            if not -20 < obs < 55:
                raise ValueError("Temperatura de contraste físicamente inverosímil")
            e_local = from_csv_num(row["error_local_c"], "error_local")
            e_ocean = from_csv_num(row["error_nino_t300_c"], "error_nino")
            if abs(e_local - (original["pronostico_local_c"] - obs)) > ERROR_TOLERANCE or abs(e_ocean - (original["pronostico_nino_t300_c"] - obs)) > ERROR_TOLERANCE:
                raise ValueError("Errores incompatibles con la predicción y el reanálisis")
            verified[identity] = obs
    if int(report["pronosticos_comparados"]) != len(verified):
        raise ValueError("Informe 8E y CSV no tienen la misma cantidad de comparaciones")
    if int(report["comparados_realmente_previos_al_mes"]) != sum(all_predictions[k]["emitido_antes_inicio_mes"] for k in verified):
        raise ValueError("Informe 8E cuenta erróneamente predicciones premes")
    return all_predictions, verified, cut, originals_info, {"csv": sha(csv_path), "reporte": sha(report_path)}


def round_metric(value):
    return round(value, 5) if value is not None else None


def describe(rows: list) -> dict:
    n = len(rows)
    out = {"n": n, "modelos": {}, "mejora_mae_nino_vs_local_pct": None, "interpretacion": "insuficiente"}
    for model in MODELS:
        errors = [r["error_" + model + "_c"] for r in rows]
        out["modelos"][model] = {
            "mae_c": round_metric(statistics.mean(abs(e) for e in errors)) if n else None,
            "rmse_c": round_metric(math.sqrt(statistics.mean(e * e for e in errors))) if n else None,
            "sesgo_c": round_metric(statistics.mean(errors)) if n else None,
            "intervalo_90_cobertura": None,
            "n_intervalos_90_calibrados": 0
        }
    if n:
        ml = out["modelos"]["local"]["mae_c"]
        mn = out["modelos"]["nino_t300"]["mae_c"]
        if ml and ml > 0:
            out["mejora_mae_nino_vs_local_pct"] = round_metric(100 * (1 - mn / ml))
        out["interpretacion"] = "muestra_exploratoria_sin_habilidad_demostrada"
    return out


def build(root: Path):
    originals, verified, cut, issue_hashes, input_hashes = read_inputs(root)
    today = cut.astimezone(UTC_PERU).date()
    details = []
    for identity, x in sorted(originals.items(), key=lambda z: (z[1]["mes_objetivo"], z[1]["localidad"], z[1]["horizonte_meses"], z[1]["emision_utc"])):
        due = first_eligible(x["mes_objetivo"])
        obs = verified.get(identity)
        if obs is not None:
            status = "comparado_era5_land_no_instrumental"
        elif today < start_of_month(x["mes_objetivo"]):
            status = "mes_futuro"
        elif today < due:
            status = "esperando_cierre_o_fecha_minima"
        else:
            status = "fuente_pendiente"
        r = {k: v for k, v in x.items() if k != "_source"}
        r.update({"estado_verificacion": status, "fecha_minima_verificacion": due.isoformat(),
                  "fuente_observacion": "ERA5-Land via Open-Meteo (reanálisis revisable)" if obs is not None else "",
                  "observacion_era5_land_c": round_metric(obs) if obs is not None else None})
        for model in MODELS:
            r["error_" + model + "_c"] = round_metric(r["pronostico_" + model + "_c"] - obs) if obs is not None else None
        details.append(r)

    def metric_group(rows):
        return describe([r for r in rows if r["observacion_era5_land_c"] is not None])
    pre = [r for r in details if r["emitido_antes_inicio_mes"]]
    within = [r for r in details if not r["emitido_antes_inicio_mes"]]
    groups = {"premes": {}, "intramensual": {}}
    for typ, part in (("premes", pre), ("intramensual", within)):
        groups[typ]["total"] = metric_group(part)
        groups[typ]["por_localidad"] = {site: metric_group([r for r in part if r["localidad"] == site]) for site in SITES}
        groups[typ]["por_horizonte"] = {str(h): metric_group([r for r in part if r["horizonte_meses"] == h]) for h in (1, 2, 3)}
        groups[typ]["por_localidad_horizonte"] = {
            site: {str(h): metric_group([r for r in part if r["localidad"] == site and r["horizonte_meses"] == h]) for h in (1, 2, 3)}
            for site in SITES
        }

    evaluated = [r for r in details if r["observacion_era5_land_c"] is not None]
    result = {
        "fase": "8G",
        "evaluado_con_corte_utc": cut.isoformat(),
        "clasificacion": "evaluador retrospectivo de emisiones archivadas, NO sistema operativo validado",
        "fuente_verificacion": "ERA5-Land via Open-Meteo; reanálisis no instrumental",
        "periodo_climatologia_entrenamiento": "1996–2022",
        "periodo_climatologia_descriptiva": "1996–2025 (no usada para entrenar)",
        "n_emisiones_originales": len(issue_hashes),
        "n_registros_archivados": len(details),
        "n_premes_archivados": len(pre),
        "n_intramensuales_archivados": len(within),
        "n_verificados_total": len(evaluated),
        "n_verificados_premes": sum(r["emitido_antes_inicio_mes"] for r in evaluated),
        "n_verificados_intramensuales": sum(not r["emitido_antes_inicio_mes"] for r in evaluated),
        "n_pendientes": len(details) - len(evaluated),
        "primera_fecha_elegible": min((r["fecha_minima_verificacion"] for r in details), default=None),
        "metricas": groups,
        "intervalos_calibrados_disponibles": False,
        "cobertura_intervalos_90_evaluable": False,
        "habilidad_prospectiva_demostrada": False,
        "validacion_instrumental": False,
        "no_es_alerta_enfen_senamhi": True,
        "mensajes": [
            "El CSV de origen 8E solo debe contener observaciones posteriores al mes objetivo y a la fecha mínima habilitada.",
            "Las estimaciones intramensuales nunca se mezclan en las métricas de predicción anterior al mes.",
            "Una mejora porcentual descriptiva no demuestra habilidad operativa, causalidad o significancia estadística.",
            "No existen intervalos predictivos 90% guardados ex ante: cobertura y probabilidades se mantienen como null.",
            "Observaciones de ERA5-Land pueden revisarse; los pronósticos originales no se reescriben."
        ],
        "trazabilidad": {"emisiones_inmutables": issue_hashes,
                         "sha256_csv_verificacion_8e": input_hashes["csv"],
                         "sha256_reporte_verificacion_8e": input_hashes["reporte"]}
    }
    return result, details


def json_file(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def csv_file(records: list) -> str:
    import io
    io_obj = io.StringIO(newline="")
    writer = csv.DictWriter(io_obj, fieldnames=DETAIL_FIELDS, lineterminator="\n")
    writer.writeheader()
    for r in records:
        writer.writerow({k: "" if r.get(k) is None else r[k] for k in DETAIL_FIELDS})
    return io_obj.getvalue()


def publish(root: Path, check: bool):
    report, details = build(root)
    output = root / OUTPUT
    files = {
        output / "metricas_8g.json": json_file(report),
        output / "detalle_8g.csv": csv_file(details)
    }
    if check:
        for path, content in files.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise ValueError("Reporte 8G requiere regeneración: " + str(path))
    else:
        output.mkdir(parents=True, exist_ok=True)
        for path, content in files.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8")
    print(json.dumps({"fase": "8G", "evaluados": report["n_verificados_total"],
                      "premes_evaluados": report["n_verificados_premes"],
                      "pendientes": report["n_pendientes"], "check": check}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Verificar que salidas publicadas concuerden con las fuentes")
    group.add_argument("--run", action="store_true", help="Regenerar solo los resultados derivados")
    args = parser.parse_args()
    publish(args.root, check=args.check)


if __name__ == "__main__":
    main()
