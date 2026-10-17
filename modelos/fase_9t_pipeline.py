#!/usr/bin/env python3
"""Fase 9T: auditoría y benchmark temporal estricto de lluvia sector-mes.
Entrada CSV obligatoria: sector_id,mes,lluvia_mm. No inventa filas ni pronósticos.
Uso: python modelos/fase_9t_pipeline.py --input datos/sectores_mensuales.csv --out resultados/9t
Dependencias: pandas numpy scikit-learn. GCN queda NO_EJECUTADA hasta incorporar
geometrías, grafo y un dataset sectorial plenamente auditado.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

TRAIN_END = pd.Timestamp("2018-12-01")
VAL_END = pd.Timestamp("2021-12-01")
TEST_END = pd.Timestamp("2025-12-01")
MIN_MONTH = pd.Timestamp("1996-01-01")

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def audit(path):
    d = pd.read_csv(path, dtype={"sector_id": str})
    needed = {"sector_id", "mes", "lluvia_mm"}
    if not needed.issubset(d.columns):
        raise ValueError("Columnas ausentes: " + repr(sorted(needed-set(d.columns))))
    # Strict YYYY-MM: reject timestamps whose reference month is ambiguous.
    if not d.mes.astype(str).str.fullmatch(r"\d{4}-\d{2}").all():
        raise ValueError("mes debe expresarse YYYY-MM")
    d["mes"] = pd.to_datetime(d.mes, format="%Y-%m", errors="raise")
    d["lluvia_mm"] = pd.to_numeric(d.lluvia_mm, errors="raise")
    if d.sector_id.isna().any() or (d.sector_id.str.strip() == "").any():
        raise ValueError("sector_id vacío")
    if d[["sector_id", "mes"]].duplicated().any():
        raise ValueError("Fechas duplicadas por sector")
    if not np.isfinite(d.lluvia_mm).all() or (d.lluvia_mm < 0).any():
        raise ValueError("Lluvia ausente, no finita o negativa: abortar sin imputación")
    if d.mes.min() > MIN_MONTH or d.mes.max() < TEST_END:
        raise ValueError("Cobertura insuficiente para 1996–2025")
    expected = pd.date_range(MIN_MONTH, TEST_END, freq="MS")
    per_sector = {}
    for sector, x in d.groupby("sector_id"):
        got = pd.DatetimeIndex(x.mes)
        missing = expected.difference(got)
        extras = got.difference(expected)
        per_sector[sector] = {"meses_observados": len(got), "faltantes_1996_2025": [z.strftime("%Y-%m") for z in missing], "fuera_periodo": [z.strftime("%Y-%m") for z in extras]}
        if len(missing):
            raise ValueError("Serie incompleta en " + sector + ": " + str(len(missing)) + " meses; no imputar")
    return d.sort_values(["sector_id", "mes"]).reset_index(drop=True), per_sector

def prepare(d):
    # Objetivo mes t; SOLO lluvia de t-1 y anterior (disponibilidad de producto
    # históricamente publicado deberá verificarse antes de uso prospectivo).
    parts = []
    for sector, group in d.groupby("sector_id"):
        g = group.sort_values("mes").copy()
        for k in (1, 2, 3, 6, 12):
            g[f"lag_{k}"] = g.lluvia_mm.shift(k)
        g["rolling_3"] = g.lluvia_mm.shift(1).rolling(3).mean()
        g["rolling_12"] = g.lluvia_mm.shift(1).rolling(12).mean()
        g["month"] = g.mes.dt.month
        g["sin"] = np.sin(2 * np.pi * g["month"] / 12)
        g["cos"] = np.cos(2 * np.pi * g["month"] / 12)
        parts.append(g)
    d = pd.concat(parts, ignore_index=True).dropna(subset=["lluvia_mm","lag_1","lag_2","lag_3","lag_6","lag_12","rolling_3","rolling_12"])
    return d[(d.mes <= TEST_END)].copy()

def score(df, pred, model, split):
    obs = df.lluvia_mm.to_numpy()
    out = np.maximum(0, np.asarray(pred, dtype=float))
    return {"modelo": model, "periodo": split, "n": len(obs), "mae_mm": float(mean_absolute_error(obs, out)),
            "rmse_mm": float(np.sqrt(mean_squared_error(obs, out))),
            "sesgo_mm": float(np.mean(out - obs))}

def run(inp, out):
    out.mkdir(parents=True, exist_ok=True)
    raw, coverage = audit(inp)
    d = prepare(raw)
    features = ["lag_1","lag_2","lag_3","lag_6","lag_12","rolling_3","rolling_12","sin","cos"]
    rows, metrics = [], []
    for sector, g in d.groupby("sector_id"):
        tr = g[g.mes <= TRAIN_END]
        va = g[(g.mes > TRAIN_END) & (g.mes <= VAL_END)]
        te = g[(g.mes > VAL_END) & (g.mes <= TEST_END)]
        if min(len(tr), len(va), len(te)) == 0:
            raise ValueError("Partición vacía para " + sector)
        # Hiperparámetros fijos sin usar test. Se incluye validación para auditabilidad.
        rf = RandomForestRegressor(n_estimators=250, min_samples_leaf=3,
                                   max_features=0.8, random_state=42, n_jobs=1)
        rf.fit(tr[features], tr.lluvia_mm)
        clim = tr.groupby("month").lluvia_mm.mean().to_dict()
        for split, x in [("validacion",va),("prueba",te)]:
            candidates = {
                "climatologia": x["month"].map(clim).to_numpy(),
                "persistencia": x["lag_12"].to_numpy(),
                "random_forest": rf.predict(x[features]),
            }
            for model, p in candidates.items():
                metrics.append({"sector_id":sector,**score(x,p,model,split)})
                for month, y, pred in zip(x.mes, x.lluvia_mm, p):
                    rows.append({"sector_id":sector,"mes":month.strftime("%Y-%m"),
                                "periodo":split,"modelo":model,"observado_mm":float(y),
                                "predicho_mm":float(max(0,pred))})
    prediction_file = out / "predicciones_fuera_muestra.csv"
    metric_file = out / "metricas_por_sector.csv"
    pd.DataFrame(rows).to_csv(prediction_file,index=False)
    pd.DataFrame(metrics).to_csv(metric_file,index=False)
    manifest = {"fase":"9T","estado":"BASELINES_RF_EJECUTADOS_GCN_PENDIENTE",
        "fuente_entrada":str(inp),"sha256_entrada":sha(inp),
        "n_sectores":len(coverage),"cobertura":coverage,
        "periodo_entrenamiento":"1996-01/2018-12",
        "periodo_validacion":"2019-01/2021-12",
        "periodo_prueba":"2022-01/2025-12",
        "n_predictions":len(rows),"semilla":42,
        "advertencias":["CHIRPS no es observación instrumental SENAMHI",
          "La disponibilidad en tiempo de emisión de rezagos no está certificada",
          "Sin geometrías/grafo auditado, GCN no ejecutada",
          "No hay pronóstico ni alerta operativa"]}
    (out / "manifiesto.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"n_sectores":len(coverage),"n_predictions":len(rows),"out":str(out),"estado":manifest["estado"]},ensure_ascii=False))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("resultados/9t"))
    args=p.parse_args()
    run(args.input,args.out)
