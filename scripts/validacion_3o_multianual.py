"""OAF-Lambayeque Fase 3O — validación multianual preliminar SENAMHI/PISCOp/ERA5.

Se comparan únicamente meses con lluvia observada completa (enero 1996–octubre 2015).
El script NO afirma validación independiente de PISCOp: puede haber usado las
mismas observaciones para crear el producto. Ubicaciones documentales preliminares.

Requiere pandas, numpy, requests, scipy; acceso saliente a Fluviotech y Open-Meteo.
Archivos de salida en datos/ y VALIDACION_3O.md; resultado real, nunca simulado.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import math
import time

import numpy as np
import pandas as pd
import requests
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
PISCO_URL = "https://fluviotech.com/meteodata/pisco/monthly/series/"
ERA_URL = "https://archive-api.open-meteo.com/v1/archive"
HEADERS = {"User-Agent": "OAF-Lambayeque/0.5 (scientific; info: github.com/ccoronelepg-gif/OAF-Lambayeque)"}

# Coordenadas DOCUMENTALES PRELIMINARES, no ficha georreferenciada verificada en campo.
STATIONS = {
    "Jayanca (La Viña)": (-6.322, -79.779),
    "Cayaltí": (-6.88079444, -79.54701389),
    "Reque": (-6.88613, -79.8355),
    "Lambayeque": (-6.73152778, -79.90983611),
    "Cueva Blanca": (-6.13130, -79.40450),
}


def solicitar(metodo, url, **kwargs):
    ultimo = None
    for intento in range(3):
        try:
            r = requests.request(metodo, url, timeout=(20, 120), headers=HEADERS, **kwargs)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            ultimo = exc
            print(f"{metodo} {url.split('/')[2]} intento {intento+1}: {type(exc).__name__}: {str(exc)[:200]}", flush=True)
            if intento < 2:
                time.sleep(5 * (intento + 1))
    raise RuntimeError(f"3 intentos fallaron: {ultimo}")


def rangos(inicio, fin):
    """Dos ventanas, limitadas al intervalo requerido, evitando una petición enorme."""
    for d, f in [("1996-01", "2005-12"), ("2006-01", "2015-12")]:
        a = max(pd.Period(d, freq="M"), pd.Period(inicio, freq="M"))
        b = min(pd.Period(f, freq="M"), pd.Period(fin, freq="M"))
        if a <= b:
            yield str(a), str(b)


def pisco(lat, lon, inicio, fin):
    js = solicitar("POST", PISCO_URL, json={
        "start": inicio, "end": fin,
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    })
    if not isinstance(js, dict) or "data" not in js:
        raise ValueError("PISCOp no devolvió una clave data")
    d = pd.DataFrame(js["data"])
    if not {"date", "precipitation"}.issubset(d.columns):
        raise ValueError(f"Columnas PISCOp inesperadas: {d.columns.tolist()}")
    d = d[["date", "precipitation"]].rename(columns={"date": "mes", "precipitation": "estimado_mm"})
    d["mes"] = d.mes.astype(str).str[:7]
    d["estimado_mm"] = pd.to_numeric(d.estimado_mm, errors="coerce")
    if d.mes.duplicated().any():
        raise ValueError("PISCOp devolvió meses duplicados")
    esperado = set(pd.period_range(inicio, fin, freq="M").astype(str))
    d = d[d.mes.isin(esperado)]
    if not esperado.issubset(set(d.mes)):
        raise ValueError(f"PISCOp omitió {len(esperado-set(d.mes))} meses")
    if d.estimado_mm.isna().any() or (d.estimado_mm < 0).any():
        raise ValueError("PISCOp devolvió precipitaciones nulas/negativas")
    return d


def era5(lat, lon, inicio, fin):
    a = inicio + "-01"
    b = pd.Period(fin, freq="M").end_time.strftime("%Y-%m-%d")
    js = solicitar("GET", ERA_URL, params={
        "latitude": lat, "longitude": lon,
        "start_date": a, "end_date": b,
        "daily": "precipitation_sum", "models": "era5_seamless",
        "timezone": "America/Lima", "cell_selection": "nearest",
    })
    if "daily" not in js or not {"time", "precipitation_sum"}.issubset(js["daily"]):
        raise ValueError("Estructura ERA5 inesperada")
    d = pd.DataFrame({
        "fecha": pd.to_datetime(js["daily"]["time"], errors="raise"),
        "p": pd.to_numeric(js["daily"]["precipitation_sum"], errors="coerce"),
    })
    esperado = pd.date_range(a, b, freq="D")
    if len(d) != len(esperado) or d.fecha.duplicated().any() or set(d.fecha) != set(esperado):
        raise ValueError("ERA5 diario incompleto / calendario erróneo")
    d["mes"] = d.fecha.dt.strftime("%Y-%m")
    d["valido"] = d.p.notna() & (d.p >= 0)
    # ERA5 diario debe tener todos los días válidos para declarar mes completo.
    g = d.groupby("mes", as_index=False).agg(estimado_mm=("p", lambda s: s.sum(min_count=1)),
                                          validos=("valido", "sum"), registros=("valido", "size"))
    g = g[g.validos == g.registros]
    return g[["mes", "estimado_mm"]]


def metricas(m, est, prod, estrato):
    x = m.observado_mm.to_numpy(dtype=float)
    y = m.estimado_mm.to_numpy(dtype=float)
    dif = y-x
    with np.errstate(divide="ignore", invalid="ignore"):
        r = float(pearsonr(x, y).statistic) if len(x) >= 3 and np.std(x) > 0 and np.std(y) > 0 else float("nan")
        rho = float(spearmanr(x, y).statistic) if len(x) >= 3 and np.std(x) > 0 and np.std(y) > 0 else float("nan")
    return dict(estacion=est, producto=prod, estrato=estrato, meses=len(m),
                obs_acumulado_mm=round(float(x.sum()), 2),
                estim_acumulado_mm=round(float(y.sum()), 2),
                sesgo_mensual_mm=round(float(dif.mean()), 3),
                mae_mensual_mm=round(float(np.abs(dif).mean()), 3),
                rmse_mensual_mm=round(float(np.sqrt(np.mean(dif**2))), 3),
                sesgo_acumulado_pct=(round(float(100*dif.sum()/x.sum()), 2) if x.sum()>0 else np.nan),
                pearson=round(r, 4), spearman=round(rho, 4))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--obs", type=Path, default=ROOT / "datos/senamhi_mensual_completo_1996_2015.csv")
    p.add_argument("--salida", type=Path, default=ROOT / "datos")
    args = p.parse_args()
    args.salida.mkdir(exist_ok=True, parents=True)
    obs = pd.read_csv(args.obs)
    assert len(obs) == 1109, f"Se esperaban 1109 meses completos; se obtuvieron {len(obs)}"
    assert set(obs.estacion) == set(STATIONS), "Estaciones incorrectas"
    assert (obs.dias_validos == obs.dias_mes).all(), "Se detectó un mes incompleto"
    assert not obs.duplicated(["estacion", "mes"]).any(), "Mes-estación duplicado"
    incidentes, pares, met = [], [], []
    for est, (lat, lon) in STATIONS.items():
        o = obs[obs.estacion == est][["mes", "observado_mm"]].copy()
        ini, fin = o.mes.min(), o.mes.max()
        print(f"\n{est}, {ini} a {fin}, meses observados: {len(o)}", flush=True)
        for producto, metodo in [("PISCOp v3.0", pisco), ("ERA5-Seamless", era5)]:
            fragmentos = []
            for a, b in rangos(ini, fin):
                try:
                    print(f"  {producto} solicitando {a}..{b}", flush=True)
                    fragmentos.append(metodo(lat, lon, a, b))
                except Exception as exc:
                    incidentes.append(dict(estacion=est, producto=producto, ventana=f"{a}..{b}",
                                           error=f"{type(exc).__name__}: {str(exc)[:250]}"))
                    print("  ERROR", str(exc)[:250], flush=True)
            if not fragmentos:
                continue
            e = pd.concat(fragmentos, ignore_index=True)
            if e.mes.duplicated().any():
                incidentes.append(dict(estacion=est, producto=producto, error="Meses duplicados al juntar ventanas"))
                continue
            m = o.merge(e, on="mes", validate="one_to_one", how="inner").sort_values("mes")
            if m.empty:
                incidentes.append(dict(estacion=est, producto=producto, error="No existen meses pareados"))
                continue
            m.insert(0, "estacion", est)
            m.insert(1, "producto", producto)
            m["diferencia_mm"] = m.estimado_mm - m.observado_mm
            pares.append(m)
            for estrato, sel in [("todos", m), ("sin_1998", m[~m.mes.str.startswith("1998-")]),
                                 ("solo_1998", m[m.mes.str.startswith("1998-")])]:
                if len(sel) >= 3:
                    met.append(metricas(sel, est, producto, estrato))
            print(f"  OK: {len(m)} meses pareados; {producto}", flush=True)

    columnas = ["estacion","producto","mes","observado_mm","estimado_mm","diferencia_mm"]
    compar = pd.concat(pares, ignore_index=True)[columnas] if pares else pd.DataFrame(columns=columnas)
    compar.to_csv(args.salida / "comparacion_3o_multianual.csv", index=False, float_format="%.4f")
    metdf = pd.DataFrame(met, columns=["estacion","producto","estrato","meses","obs_acumulado_mm",
                                      "estim_acumulado_mm","sesgo_mensual_mm","mae_mensual_mm",
                                      "rmse_mensual_mm","sesgo_acumulado_pct","pearson","spearman"])
    metdf.to_csv(args.salida / "metricas_3o_multianual.csv", index=False)
    estado = dict(
        etapa="3O", creado_utc=datetime.now(timezone.utc).isoformat(),
        meses_estacion_observados_completos=len(obs), estaciones=len(STATIONS),
        productos=["PISCOp v3.0", "ERA5-Seamless"], pares_mensuales=len(compar),
        combinaciones_obtenidas=len({(x["estacion"],x["producto"]) for x in met if x["estrato"]=="todos"}),
        combinaciones_esperadas=10, incidencias=incidentes,
        coordenadas_preliminares=True,
        pisco_validacion_independiente=False,
        datos_fuentes_senamhi="archivos TXT aportados por el usuario, agregación mensual",
    )
    (args.salida / "estado_3o.json").write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")
    lineas = ["# Validación 3O: precipitación multianual 1996–2015", "",
        "> **RESULTADOS EXPLORATORIOS**. Los cálculos usan meses completos de cinco archivos", 
        "> históricos SENAMHI y ubicaciones documentales **preliminares**. PISCOp podría",
        "> usar estaciones del SENAMHI en su interpolación: NO es validación independiente.", "",
        "## Cobertura y procedimiento", "",
        f"- Meses-estación completos de lluvia instrumental: **{len(obs)}**.",
        f"- Pares observación-estimación obtenidos: **{len(compar)}**.",
        f"- Combinaciones estación × producto: **{estado['combinaciones_obtenidas']}/10**.",
        "- Comparación mes a mes, solo coincidencias de fecha y posición solicitada.",
        "- Las estadísticas separan todos los meses, el año 1998 y los otros años.",
        "- El porcentaje es sesgo acumulado (suma estimada - suma observada) / suma observada.",
        "- No existen datos SENAMHI disponibles posteriores a 2015 en los archivos cargados.", "",
        "## Estadísticas por estación/producto (solo estrato **todos**)", "",
        "| Estación | Producto | Meses | Obs. (mm) | Est. (mm) | Sesgo mes (mm) | MAE mes (mm) | RMSE mes (mm) | Sesgo total (%) | Pearson |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in met:
        if row["estrato"] != "todos":
            continue
        def fm(k):
            v=row[k]
            return "ND" if not pd.notna(v) else str(v)
        lineas.append("| " + " | ".join(map(fm, ["estacion","producto","meses","obs_acumulado_mm",
                                                        "estim_acumulado_mm","sesgo_mensual_mm","mae_mensual_mm",
                                                        "rmse_mensual_mm","sesgo_acumulado_pct","pearson"])) + " |")
    lineas += ["", "## Control de calidad y limitaciones", "",
        "- Valores diarios ausentes se conservan como ausentes: no se asignan a precipitación 0.",
        "- Meses con un día de observación ausente no se incluyen. ERA5 también requiere todos los días.",
        "- La serie PISCOp se obtiene mediante API externa Fluviotech. Evitar inferir independencia estadística.",
        "- El conjunto ERA5-Seamless de Open-Meteo es híbrido; no equipararlo automáticamente a ERA5-Land oficial.",
        "- Las celdas y representatividad orográfica difieren entre fuentes y estación.",
        "- Extremos como 1998 pueden dominar las métricas; por ello se informa estrato sin 1998.",
        "- Correlación alta no equivale a ausencia de sesgo.",
    ]
    if incidentes:
        lineas.extend(["", "## Consultas con errores (no se imputaron datos)", ""])
        for inc in incidentes:
            lineas.append("- " + " · ".join(str(inc.get(k,"")) for k in ["estacion","producto","ventana","error"]))
    lineas += ["", "## Fuentes técnicas", "",
        "- https://fluviotech.com/meteodata/pisco/api/docs/",
        "- https://open-meteo.com/en/docs/historical-weather-api",
        "- Archivos históricos SENAMHI TXT aportados por el investigador.", ""]
    (ROOT / "VALIDACION_3O.md").write_text("\n".join(lineas), encoding="utf-8")
    print("COMPLETADO", estado, flush=True)
    # Si no hubo series, falla el workflow: no se publican métricas simuladas.
    return 0 if pares else 2

if __name__ == "__main__":
    raise SystemExit(main())
