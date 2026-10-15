#!/usr/bin/env python3
"""OAF-Lambayeque — fase 6G, verificación REALMENTE prospectiva de emisiones.

Lee pronósticos externos archivados con sello temporal (no modifica originales).
Compara SOLO jornadas COMPLETAS cuyo día válido finalizó al menos 7 días atrás:
ERA5-Land temperatura media 2m; ERA5 lluvia y radiación solar diaria.

No confundir reanálisis con estación SENAMHI o medición en dosel.
Si no existen fechas maduras, publica "pendiente_reanalisis" SIN fabricar aciertos.
Stdlib Python 3.11; ver --self-test. Genera resultados auditables con fecha.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics as st
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

RECORDS = Path("datos/pronosticos_emitidos")
OUT_JSON = Path("datos/evaluacion_prospectiva_6g.json")
OUT_CSV = Path("datos/evaluacion_prospectiva_6g.csv")
LAG_DAYS = 7
VARS = {
    "temperature_2m_mean": ("ERA5-Land", "°C"),
    "precipitation_sum": ("ERA5", "mm"),
    "shortwave_radiation_sum": ("ERA5", "MJ/m²")
}
SITES = ("Chiclayo", "Jayanca", "Motupe", "Olmos")
FIELDS = (
    "fecha_emision_local", "emision_utc", "localidad", "horizonte_dias",
    "fecha_valida", "variable", "unidad", "pronosticado",
    "referencia_reanalisis", "error", "modelo_referencia",
    "fuente_pronostico", "fuente_referencia",
)

def number(v):
    return type(v) in (float, int) and math.isfinite(v)


def records(today):
    """Validate immutable raw emissions and collect only eligible future forecasts."""
    if not RECORDS.is_dir():
        return [], 0, None
    selected, count = [], 0
    first_valid = None
    for file in sorted(RECORDS.glob("????-??-??.json")):
        payload = json.loads(file.read_text(encoding="utf-8"))
        issue_day = date.fromisoformat(payload["fecha_consulta_local"])
        if issue_day.isoformat() != file.stem:
            raise ValueError("Issue filename/date mismatch: " + str(file))
        issuance = datetime.fromisoformat(payload["emision_utc"].replace("Z", "+00:00"))
        if issuance.tzinfo is None:
            raise ValueError("Issue timestamp without UTC offset " + str(file))
        if payload.get("son_predicciones_propias_oaf") is not False:
            raise ValueError("Unverified provenance: " + str(file))
        if not isinstance(payload.get("localidades"), dict):
            raise ValueError("Missing sites: " + str(file))
        for site in SITES:
            location = payload["localidades"].get(site)
            if not isinstance(location, dict):
                raise ValueError("Missing locality " + site)
            future_days = location.get("jornadas_futuras")
            if not isinstance(future_days, list) or len(future_days) != 7:
                raise ValueError("Expected seven complete forecasts: " + site)
            if any(location.get(key) is None for key in ("latitud_celda", "longitud_celda")):
                raise ValueError("Missing model cell: " + site)
            for horizon, row in enumerate(future_days, start=1):
                valid_day = date.fromisoformat(row["fecha_valida"])
                if valid_day != issue_day + timedelta(days=horizon):
                    raise ValueError("Noncontiguous dates/horizons: " + site)
                if issuance.astimezone(timezone.utc) >= datetime.combine(valid_day, datetime.min.time(), ZoneInfo("America/Lima")).astimezone(timezone.utc):
                    raise ValueError("Forecast emission was not prior to valid day: " + site)
                count += 1
                if first_valid is None or valid_day < first_valid:
                    first_valid = valid_day
                # A minimum seven complete days is a conservative quality gate.
                if valid_day > today - timedelta(days=LAG_DAYS):
                    continue
                values = {}
                for variable, (_, unit) in VARS.items():
                    v = row.get(variable)
                    if not number(v) or (variable != "temperature_2m_mean" and v < 0):
                        raise ValueError("Missing/invalid predicted " + variable)
                    expected = location.get("unidades", {}).get(variable)
                    if expected != unit and not (unit == "MJ/m²" and expected == "MJ/m2"):
                        raise ValueError("Forecast units changed for " + variable)
                    values[variable] = v
                selected.append({
                    "site": site, "date": valid_day.isoformat(),
                    "issue": issue_day.isoformat(), "timestamp": issuance.isoformat(),
                    "horizon": horizon, "values": values,
                })
    return selected, count, first_valid


def fetch_reanalysis(site, start, end):
    # Approximate site coordinates must be aligned with forecast archival sites.
    coords = {
        "Chiclayo": (-6.77140, -79.84090),
        "Jayanca": (-6.39278, -79.82280),
        "Motupe": (-6.15083, -79.71420),
        "Olmos": (-5.98825, -79.74723)
    }
    lat, lon = coords[site]
    common = dict(latitude=lat, longitude=lon,
                  start_date=start, end_date=end, timezone="America/Lima")
    def fetch(model, fields):
        url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode({
            **common, "daily": ",".join(fields), "models": model
        })
        request = urllib.request.Request(
            url, headers={"User-Agent": "OAF-Lambayeque-6G-verification/1.0"})
        with urllib.request.urlopen(request, timeout=85) as response:
            result = json.load(response)
        if result.get("error") or not isinstance(result.get("daily"), dict):
            raise ValueError("Unavailable verified reanalysis " + model)
        dates = result["daily"].get("time")
        if not isinstance(dates, list) or len(dates) != len(set(dates)):
            raise ValueError("Missing or duplicated reanalysis dates: " + model)
        for field in fields:
            if not isinstance(result["daily"].get(field), list) or len(result["daily"][field]) != len(dates):
                raise ValueError("Incomplete reanalysis column " + field)
        return result
    temp = fetch("era5_land", ("temperature_2m_mean",))
    others = fetch("era5", ("precipitation_sum", "shortwave_radiation_sum"))
    result = {}
    for data, variables, model in [
        (temp, ("temperature_2m_mean",), "ERA5-Land"),
        (others, ("precipitation_sum", "shortwave_radiation_sum"), "ERA5")
    ]:
        daily = data["daily"]
        for i, valid_day in enumerate(daily["time"]):
            result.setdefault(valid_day, {})
            for variable in variables:
                value = daily[variable][i]
                if number(value) and (variable == "temperature_2m_mean" or value >= 0):
                    result[valid_day][variable] = value
    return result


def build_rows(eligible, reference):
    """Join by site/date, never by row position; no imputation of missing data."""
    out, missing = [], 0
    for item in eligible:
        data = reference.get(item["site"], {}).get(item["date"], {})
        # An incomplete reference day is not scored partially.
        if any(not number(data.get(name)) for name in VARS):
            missing += 1
            continue
        for variable, (model, unit) in VARS.items():
            prediction = item["values"][variable]
            reality = data[variable]
            out.append({
                "fecha_emision_local": item["issue"],
                "emision_utc": item["timestamp"],
                "localidad": item["site"],
                "horizonte_dias": item["horizon"],
                "fecha_valida": item["date"],
                "variable": variable,
                "unidad": unit,
                "pronosticado": prediction,
                "referencia_reanalisis": reality,
                "error": round(prediction-reality, 5),
                "modelo_referencia": model,
                "fuente_pronostico": "Open-Meteo Forecast API, emisión archivada",
                "fuente_referencia": "Open-Meteo Historical Weather API"
            })
    return out, missing


def aggregate(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["localidad"], r["horizonte_dias"], r["variable"])].append(r)
    metrics = []
    for (site, horizon, variable), items in sorted(groups.items()):
        errors = [x["error"] for x in items]
        metrics.append({
            "localidad": site, "horizonte_dias": horizon,
            "variable": variable, "unidad": VARS[variable][1],
            "n_emisiones_verificadas": len(errors),
            "mae": round(st.mean(map(abs, errors)), 4),
            "sesgo": round(st.mean(errors), 4),
            "rmse": round(math.sqrt(st.mean(e*e for e in errors)), 4),
            "validacion_operativa": False
        })
    return metrics


def create_report(eligible, total_days, first, reference, at):
    scored, missing = build_rows(eligible, reference)
    metrics = aggregate(scored)
    verified = len(scored)//len(VARS)
    distinct_issuances = len({r["emision_utc"] for r in scored})
    report = {
        "fase": "6G",
        "generado_utc": at.isoformat(timespec="seconds"),
        "hoy_local_peru": at.astimezone(ZoneInfo("America/Lima")).date().isoformat(),
        "estado": "con_resultados_reanalisis" if scored else "pendiente_reanalisis",
        "tipo": "verificacion_de_pronosticos_externos_emitidos_antes_del_evento",
        "son_predicciones_oaf": False, "validacion_instrumental": False,
        "retraso_seguridad_dias": LAG_DAYS,
        "primera_fecha_valida_archivada": first.isoformat() if first else None,
        "primera_fecha_elegible": first.__add__(timedelta(days=LAG_DAYS)).isoformat() if first else None,
        "jornadas_pronosticadas_en_archivo": total_days,
        "jornadas_elegibles": len(eligible),
        "jornadas_verificadas": verified,
        "jornadas_con_referencia_incompleta": missing,
        "emisiones_distintas_verificadas": distinct_issuances,
        "variables_evaluadas": [
            {"nombre": k, "unidad": unit, "referencia": model}
            for k, (model, unit) in VARS.items()
        ],
        "metricas_por_localidad_horizonte_y_variable": metrics,
        "referencias": {
            "temperatura": "Open-Meteo Historical Weather, ERA5-Land daily",
            "lluvia_y_radiacion": "Open-Meteo Historical Weather, ERA5 daily",
            "latencia_fuente": "ERA5 / ERA5-Land aprox. 5 días, margen de seguridad 7 días",
        },
        "advertencias": [
            "ERA5/ERA5-Land son reanálisis, no observaciones instrumentales SENAMHI.",
            "La información muestra error de pronóstico externo, no habilidad predictiva original del OAF.",
            "Los horizontes son días calendario desde emisión local, no exactamente horas de plazo.",
            "Faltan mediciones locales e información de incidencia de enfermedades en arándano y vid.",
            "No se infiere predicción de El Niño Costero ni se generan alertas fitosanitarias.",
            "Un número pequeño de emisiones verificadas no constituye validación operativa."
        ],
    }
    return report, scored


def self_test():
    issued = date(2026, 10, 14)
    first = date(2026, 10, 15)
    def row(x, date_string="2026-10-15"):
        return {
            "site": "Motupe", "date": date_string, "issue": issued.isoformat(),
            "timestamp": "2026-10-15T04:55:55+00:00", "horizon": 1,
            "values": {k: x for k in VARS}
        }
    assert first + timedelta(days=LAG_DAYS) == date(2026, 10, 22)
    reference = {"Motupe": {"2026-10-15": {k: 6.0 for k in VARS}}}
    scored, missing = build_rows([row(5.0)], reference)
    assert len(scored) == 3 and missing == 0
    assert all(v["error"] == -1.0 for v in scored)
    assert len(aggregate(scored)) == 3
    bad = {"Motupe": {"2026-10-15": {"temperature_2m_mean": 6.0}}}
    scored, missing = build_rows([row(5.0)], bad)
    assert len(scored) == 0 and missing == 1
    pending, scored = create_report([], 28, first, {}, datetime(2026, 10, 16, tzinfo=timezone.utc))
    assert pending["estado"] == "pendiente_reanalisis" and not scored
    print("6G tests: temporal gate, 3 variables, signed errors, no imputation, pending state PASSED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    now = datetime.now(timezone.utc)
    today = now.astimezone(ZoneInfo("America/Lima")).date()
    eligible, total, first = records(today)
    reference = {}
    if eligible:
        for site in SITES:
            subset = [r["date"] for r in eligible if r["site"] == site]
            if subset:
                reference[site] = fetch_reanalysis(site, min(subset), max(subset))
    report, rows = create_report(eligible, total, first, reference, now)
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "state": report["estado"], "eligible": report["jornadas_elegibles"],
        "verified": report["jornadas_verificadas"],
        "incomplete": report["jornadas_con_referencia_incompleta"]
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("OAF 6G ERROR: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
