#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAF Lambayeque · Fase 9D: ingestión trazable de tres archivos diarios.
Formato observado: anio mes dia precip Tmax Tmin; -99.9 = ausente.
Los nombres de estación y sus coordenadas NO figuran en las fuentes recibidas.
No atribuir la procedencia al SENAMHI hasta tener metadatos verificables.
No autoriza alertas ni valida predicciones 9A-9C con celdas no emparejadas.

Uso:
    python modelos/estaciones_instrumentales_9d.py
    python modelos/estaciones_instrumentales_9d.py --check
"""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "datos/estaciones_9d"
RAW = BASE / "originales"
JSON_FILE = BASE / "auditoria_estaciones_9d.json"
CSV_FILE = BASE / "series_mensuales_9d.csv"
INPUTS = {
    "00000340": {"filename": "qc00000340.txt", "sha256": "3805b295c8a6eddaf9606caf200747b814b7898fc561f7da40936827d0574618"},
    "00153114": {"filename": "qc00153114.txt", "sha256": "8a85d663750cbc4d361f62e5f4a43e338de24373a21c55337e9076f5ca740c0a"},
    "00152107": {"filename": "qc00152107.txt", "sha256": "0434dbc67f01fbb8013d95881452f567feffa9e2542a04eae6f9dc175e715b31"},
}
FIELDS = ["codigo", "mes", "dias_calendario", "dias_registrados",
          "precip_dias_validos", "precip_cobertura_pct", "precip_total_mm",
          "tmax_dias_validos", "tmax_cobertura_pct", "tmax_media_c",
          "tmin_dias_validos", "tmin_cobertura_pct", "tmin_media_c",
          "mes_precip_completo", "mes_tmax_completo", "mes_tmin_completo"]


def round4(v):
    return None if v is None else round(v, 4)


def load_source(code, info):
    path = RAW / info["filename"]
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != info["sha256"]:
        raise ValueError(f"SHA256 distinto en {code}: {sha}")
    by_month = defaultdict(list)
    dates = set()
    previous = None
    n = 0
    counts = {"precip": 0, "tmax": 0, "tmin": 0}
    missing = {"precip": 0, "tmax": 0, "tmin": 0}
    flags = []
    extreme = []
    last = None
    for line_number, text in enumerate(raw.decode("utf-8").splitlines(), 1):
        columns = text.split()
        if len(columns) != 6:
            raise ValueError(f"{code}:{line_number}: seis columnas requeridas")
        y, m, d = (int(c) for c in columns[:3])
        dt = date(y, m, d)
        if dt in dates:
            raise ValueError(f"{code}: fecha duplicada {dt}")
        if previous is not None and (dt - previous).days != 1:
            raise ValueError(f"{code}: salto de fecha tras {previous}")
        previous = dt
        dates.add(dt)
        vals = [float(v) for v in columns[3:]]
        if any(not math.isfinite(v) for v in vals):
            raise ValueError(f"{code}: valor numerico invalido {dt}")
        p, tx, tn = [None if v == -99.9 else v for v in vals]
        for key, val in (("precip", p), ("tmax", tx), ("tmin", tn)):
            if val is None:
                missing[key] += 1
            else:
                counts[key] += 1
        if p is not None:
            if p < 0:
                raise ValueError(f"{code}: lluvia negativa no-sentinel {dt}")
            if p >= 150:
                extreme.append({"fecha": dt.isoformat(), "precipitacion_mm": p,
                                "evaluacion": "conservar; confirmar con metadatos/informe QC"})
        if tx is not None and not (-10 <= tx <= 55):
            flags.append({"fecha": dt.isoformat(), "variable": "tmax", "valor": tx})
        if tn is not None and not (-20 <= tn <= 45):
            flags.append({"fecha": dt.isoformat(), "variable": "tmin", "valor": tn})
        if tx is not None and tn is not None and tx < tn:
            flags.append({"fecha": dt.isoformat(), "variable": "tmax_menor_tmin",
                          "tmax": tx, "tmin": tn})
        by_month[(y, m)].append((p, tx, tn))
        n += 1
        last = dt
    if not n:
        raise ValueError("Archivo sin filas: " + code)
    return {"raw_sha256": sha, "rows": n, "inicio": min(dates).isoformat(),
            "fin": last.isoformat(), "validos": counts, "ausentes": missing,
            "controles_manual": flags, "extremos_lluvia_150mm": extreme}, by_month


def aggregations(code, months):
    monthly = []
    for (y, m), rows in sorted(months.items()):
        expected = (date(y + (m == 12), m % 12 + 1, 1) - date(y, m, 1)).days
        n = len(rows)
        values = [[r[i] for r in rows if r[i] is not None] for i in range(3)]
        cover = [len(a) / expected for a in values]
        good = [ratio >= 0.9 for ratio in cover]
        rain = sum(values[0]) if good[0] else None
        tmax = sum(values[1]) / len(values[1]) if good[1] else None
        tmin = sum(values[2]) / len(values[2]) if good[2] else None
        monthly.append({
            "codigo": code, "mes": f"{y:04d}-{m:02d}",
            "dias_calendario": expected, "dias_registrados": n,
            "precip_dias_validos": len(values[0]), "precip_cobertura_pct": round4(cover[0] * 100),
            "precip_total_mm": round4(rain),
            "tmax_dias_validos": len(values[1]), "tmax_cobertura_pct": round4(cover[1] * 100),
            "tmax_media_c": round4(tmax),
            "tmin_dias_validos": len(values[2]), "tmin_cobertura_pct": round4(cover[2] * 100),
            "tmin_media_c": round4(tmin),
            "mes_precip_completo": int(good[0]), "mes_tmax_completo": int(good[1]),
            "mes_tmin_completo": int(good[2]),
        })
    return monthly


def annual_rain(monthly, year):
    a = [m for m in monthly if m["mes"].startswith(str(year) + "-")]
    if len(a) != 12 or any(m["precip_total_mm"] is None for m in a):
        return None
    return round4(sum(m["precip_total_mm"] for m in a))


def describe_station(code, info, summary, monthly):
    ref = [m for m in monthly if "1996-01" <= m["mes"] <= "2013-12"]
    return {
        "codigo": code, "nombre": None, "latitud": None, "longitud": None,
        "altitud_m": None, "metadatos_senamhi_verificados": False,
        "origen": "archivo enviado por usuario; operador y licencia no corroborados",
        "archivo_original": "datos/estaciones_9d/originales/" + info["filename"],
        **summary,
        "precip_cobertura_total_pct": round4(summary["validos"]["precip"] / summary["rows"] * 100),
        "tmax_cobertura_total_pct": round4(summary["validos"]["tmax"] / summary["rows"] * 100),
        "tmin_cobertura_total_pct": round4(summary["validos"]["tmin"] / summary["rows"] * 100),
        "meses_precip_utilizables": sum(m["mes_precip_completo"] for m in monthly),
        "meses_tmax_utilizables": sum(m["mes_tmax_completo"] for m in monthly),
        "meses_tmin_utilizables": sum(m["mes_tmin_completo"] for m in monthly),
        "periodo_1996_2013": {
            "meses_posibles": 216,
            "meses_precip_utilizables": sum(m["mes_precip_completo"] for m in ref),
            "meses_tmax_utilizables": sum(m["mes_tmax_completo"] for m in ref),
            "meses_tmin_utilizables": sum(m["mes_tmin_completo"] for m in ref),
            "no_es_normal_climatologica_1996_2025": True
        },
        "lluvia_anual_mm_si_12_meses_validos": {
            str(y): annual_rain(monthly, y) for y in (1982, 1983, 1997, 1998, 2012, 2013)
        }
    }


def compute():
    station_summaries = []
    all_months = []
    for code, info in INPUTS.items():
        summary, months = load_source(code, info)
        monthly = aggregations(code, months)
        all_months.extend(monthly)
        station_summaries.append(describe_station(code, info, summary, monthly))
    report = {
        "fase": "9D", "fecha_procesamiento": "2026-10-17",
        "estado": "series_diarias_con_ingesta_verificada_por_SHA; identidad_geografica_por_verificar",
        "fuente": "tres archivos diarios aportados por usuario; no hay cabeceras ni ficha oficial adjunta",
        "orden_columnas_inferido": ["anio", "mes", "dia", "precipitacion_mm",
                                     "temperatura_maxima_c", "temperatura_minima_c"],
        "sentinel_sin_dato": -99.9,
        "control_calidad": {
            "reglas": "6 columnas; fechas consecutivas y unicas; SHA-256; centinelas a NA; precip negativa rechazada; plausibilidad termica y Tmax<Tmin marcadas; lluvia >=150mm señalada para revision pero conservada",
            "mes_completo": "al menos 90 % de dias del mes calendario para cada variable por separado; no imputacion ni escalamiento",
            "anual": "suma de 12 meses completos; si falta alguno -> null",
            "prohibido": "convertir -99.9 a cero, normal 1996-2025 truncada, homogeneizacion no realizada, validar grilla espacial sin coordenadas",
        },
        "totales": {"archivos": 3, "registros_diarios": sum(x["rows"] for x in station_summaries),
                    "meses_en_csv": len(all_months)},
        "estaciones": station_summaries,
        "modelo_y_territorio": {
            "comparacion_directa_con_9A_9C": False,
            "razon": "no hay coordenadas ni altitud verificadas, ventanas 9A en 2011-2025 y las fuentes terminan en 2013/2014; reanalisis y estaciones no emparejados",
            "lluvias_el_nino": "solo retrospectiva; comparar episodios 1983 y 1998 sin atribucion causal automatica",
            "pisos_altitudinales_verificados": False,
            "alertas_operativas": False
        },
        "metadatos_pendientes": ["nombre oficial", "codigo institucional y equivalencia",
                                 "latitud", "longitud", "altitud", "tipo instrumento",
                                 "procedencia exacta", "licencia/restricciones",
                                 "fecha de actualizacion y control de calidad original"],
    }
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(all_months)
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n", stream.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="No alterar archivos: comparar salidas existentes")
    args = parser.parse_args()
    data_json, data_csv = compute()
    if args.check:
        if JSON_FILE.read_text("utf-8") != data_json or CSV_FILE.read_text("utf-8") != data_csv:
            raise SystemExit("Falló reproducibilidad 9D; datos cambiaron o falta regenerar salidas.")
    else:
        BASE.mkdir(parents=True, exist_ok=True)
        JSON_FILE.write_text(data_json, encoding="utf-8")
        CSV_FILE.write_text(data_csv, encoding="utf-8")
    report = json.loads(data_json)
    print(f"FASE 9D {'OK' if args.check else 'GENERADA'}: {report['totales']}, "
          "metadatos sin verificar; sin imputación ni alertas.")


if __name__ == "__main__":
    main()
