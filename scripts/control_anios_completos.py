"""OAF-Lambayeque — año límite calculado solo con observaciones completas.

Entrada: meses con TODOS los días válidos, elaborados de los archivos
históricos diarios SENAMHI del proyecto. Se exige 12/12 meses por año antes
de calcular totales anuales observados; sin relleno con PISCOp/CHIRPS/ERA5.

Esta verificación controla completitud y consistencia temporal; NO acredita
código de estación, emplazamiento, cambios de instrumento ni independencia.
"""
from __future__ import annotations
import calendar
import csv
import datetime as dt
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"
START_YEAR = 1996
END_YEAR = 2015
STATIONS = [
    "Jayanca (La Viña)", "Cayaltí", "Reque", "Lambayeque", "Cueva Blanca"
]
EXPECTED_ROWS = 1109


def export_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    source = DATA / "senamhi_mensual_completo_1996_2015.csv"
    with source.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    required = {"estacion", "mes", "observado_mm", "dias_validos", "dias_mes"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("CSV histórico con columnas faltantes")
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"Se esperaban {EXPECTED_ROWS} meses históricos, llegaron {len(rows)}")
    by_station_year = defaultdict(dict)
    for r in rows:
        station = r["estacion"].strip()
        if station not in STATIONS:
            raise ValueError("Estación fuera de catálogo: " + station)
        try:
            year, month = map(int, r["mes"].split("-"))
            yyyy_mm = f"{year:04}-{month:02}"
            rain = float(r["observado_mm"])
            valid = int(r["dias_validos"])
            days = int(r["dias_mes"])
            actual = calendar.monthrange(year, month)[1]
        except (ValueError, TypeError) as e:
            raise ValueError("Fecha o unidad mal formada: "+repr(r)) from e
        if yyyy_mm != r["mes"] or not START_YEAR <= year <= END_YEAR:
            raise ValueError("Fecha fuera del intervalo 1996–2015")
        if not math.isfinite(rain) or rain < 0:
            raise ValueError("Precipitación no válida; el cero real sí es admisible")
        if days != actual or valid != days:
            raise ValueError("Mes no completo indebidamente incluido: " + repr(r))
        if month in by_station_year[(station, year)]:
            raise ValueError(f"Mes duplicado para {station} {year}-{month:02}")
        by_station_year[(station, year)][month] = rain
    observed_counts = {
        station: sum(len(by_station_year[(station,year)]) for year in range(START_YEAR,END_YEAR+1))
        for station in STATIONS
    }
    expected_station_counts = {
        "Jayanca (La Viña)":219, "Cayaltí":235, "Reque":233,
        "Lambayeque":204, "Cueva Blanca":218
    }
    if observed_counts != expected_station_counts:
        raise ValueError("Los meses por estación cambiaron respecto de la fuente controlada")

    coverage = []
    complete_annual = []
    all_complete = []
    for year in range(START_YEAR, END_YEAR + 1):
        months_all = []
        for station in STATIONS:
            months = by_station_year[(station, year)]
            complete = len(months) == 12
            days_year = 366 if calendar.isleap(year) else 365
            matched_days = sum(calendar.monthrange(year, month)[1] for month in months)
            if matched_days > days_year:
                raise ValueError("Suma de días excede calendario")
            coverage.append({
                "estacion":station, "anio":year,
                "meses_observados_completos":len(months),
                "meses_requeridos":12,
                "dias_en_meses_completos":matched_days,
                "dias_calendario_anio":days_year,
                "anio_completo":str(complete).lower(),
                "acumulado_anual_observado_mm": (
                    f"{sum(months.values()):.3f}" if complete else ""
                ),
                "regla_aplicada":"sin_imputacion",
            })
            if complete:
                if matched_days != days_year:
                    raise ValueError("Los 12 meses no cubren todos los días del año")
                complete_annual.append({
                    "estacion":station,"anio":year,
                    "meses_completos":12, "dias_validos":days_year,
                    "precipitacion_anual_observada_mm":f"{sum(months.values()):.3f}",
                    "origen":"SENAMHI TXT histórico recibido",
                    "identidad_instrumental_historica_certificada":"no",
                })
            months_all.append(complete)
        if all(months_all):
            all_complete.append(year)
    summary=[]
    for station in STATIONS:
        complete_years=[r["anio"] for r in coverage
                        if r["estacion"]==station and r["anio_completo"]=="true"]
        if not complete_years:
            raise ValueError("Estación sin año completo: " + station)
        summary.append({
            "estacion":station,
            "ultimo_anio_temporalmente_completo":max(complete_years),
            "anios_temporalmente_completos":len(complete_years),
            "meses_historicos_validos":observed_counts[station],
        })
    if not all_complete or max(all_complete) != 2012:
        raise ValueError("Control de última intersección alterado; revisar series")
    last={r["estacion"]:r["ultimo_anio_temporalmente_completo"] for r in summary}
    expected_last={"Jayanca (La Viña)":2012,"Cayaltí":2013,"Reque":2013,
                   "Lambayeque":2013,"Cueva Blanca":2013}
    if last != expected_last:
        raise ValueError("El año completo último por estación cambió")
    if len(complete_annual) != 79:
        raise ValueError(f"Cantidad de estación-año completa inesperada: {len(complete_annual)}")

    export_csv(DATA/"cobertura_anual_oficial.csv",coverage,list(coverage[0]))
    export_csv(DATA/"acumulados_anuales_completos.csv",complete_annual,list(complete_annual[0]))
    export_csv(DATA/"ultimo_anio_completo_por_estacion.csv",summary,list(summary[0]))
    state={
        "fuente_instrumental":"archivos TXT SENAMHI históricos aportados al OAF",
        "archivo_mensual":"datos/senamhi_mensual_completo_1996_2015.csv",
        "periodo_fuente":"1996-2015",
        "meses_estacion_completos":len(rows),
        "estaciones":len(STATIONS),
        "combinaciones_estacion_anio_completas":len(complete_annual),
        "ultimo_anio_temporalmente_completo_compartido_cinco_estaciones":max(all_complete),
        "anios_completos_compartidos":all_complete,
        "ultimo_anio_completo_por_estacion":last,
        "minimo_meses_para_acumulado_anual":12,
        "dias_por_anio": "365 o 366, todos válidos",
        "imputacion_de_faltantes_permitida":False,
        "serie_continua_2016_2025_certificada":False,
        "boletines_2024_2025_son_evidencia_documental_no_anual":True,
        "identidad_instrumental_y_cambios_de_ubicacion_verificados":False,
        "nota":"Completitud temporal no equivale a certificación del emplazamiento histórico ni a validación independiente de grillas.",
    }
    (DATA/"estado_cobertura_oficial.json").write_text(
        json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=[
        "# OAF-Lambayeque | Resultado automático de la política de años completos","",
        "Se analizaron los **1 109 meses completos por estación** extraídos de las series históricas SENAMHI, sin rellenar meses faltantes.",
        "Para calcular un total anual se exigen **12 meses completos** y, en conjunto, los 365/366 días calendario del año.","",
        "| Estación | Último año completo (12 meses) | Años completos disponibles |",
        "|---|---:|---:|"
    ]
    for r in summary:
        report.append(f"| {r['estacion']} | {r['ultimo_anio_temporalmente_completo']} | "
                      f"{r['anios_temporalmente_completos']} |")
    report+=["",
       f"**Último año completo compartido por las cinco estaciones: {max(all_complete)}.**",
       f"**Años comunes completos:** {', '.join(map(str,all_complete))}.",
       f"**Total de combinaciones estación-año completas:** {len(complete_annual)}.","",
       "Los años posteriores que solo contienen meses aislados **no se han sumado a totales anuales**.",
       "Una tabla de boletín de 2025 no sustituye la falta de 12 meses completos y documentación instrumental.",
       "**El corte se actualiza si se obtienen y verifican datos completos más recientes**; 2012 es el corte actual de estos archivos y estas cinco estaciones, no un límite permanente.",
       "Los códigos y desplazamientos históricos de estaciones aún requieren validación oficial.","",
       "Archivos: datos/cobertura_anual_oficial.csv, datos/acumulados_anuales_completos.csv,",
       "datos/ultimo_anio_completo_por_estacion.csv, datos/estado_cobertura_oficial.json.",
       "Código: scripts/control_anios_completos.py.",
       "Política: CRITERIO_COBERTURA_OFICIAL.md.",""]
    (ROOT/"RESULTADO_COBERTURA_OFICIAL.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"estado":"correcto","ultimo_comun":max(all_complete),
                      "ultimo_por_estacion":last,"anios_completos":len(complete_annual)},ensure_ascii=False),flush=True)

if __name__ == "__main__":
    main()
