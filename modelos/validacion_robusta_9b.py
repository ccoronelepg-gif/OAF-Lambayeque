#!/usr/bin/env python3
"""Fase 9B. Paired blocked validation; no real results without real CSV.

Usage: python modelos/validacion_robusta_9b.py entrada.csv salida.json
Columns: fecha_objetivo,localidad,horizonte,variable,observado,pred_ref,pred_candidato.
Optional for binary events: prob_ref,prob_candidato,evento,subzona,fecha_emision.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = ["fecha_objetivo", "localidad", "horizonte", "variable",
            "observado", "pred_ref", "pred_candidato"]
KEYS = ["fecha_objetivo", "localidad", "horizonte", "variable"]


def blocked_ci(delta, months, block=12, replicates=2000, seed=917):
    """Calendar-month block bootstrap with circular blocks; paired losses."""
    d = pd.DataFrame({"d": np.asarray(delta, dtype=float),
                      "m": pd.to_datetime(months).to_period("M").astype(str)})
    monthly = d.groupby("m", sort=True)["d"].mean()
    vals = monthly.to_numpy()
    n = len(vals)
    if n < max(2 * block, 24):
        return None
    rng = np.random.default_rng(seed)
    res = np.empty(replicates)
    k = int(np.ceil(n / block))
    for b in range(replicates):
        starts = rng.integers(0, n, size=k)
        ids = np.concatenate([(np.arange(s, s + block) % n) for s in starts])[:n]
        res[b] = vals[ids].mean()
    return [float(v) for v in np.quantile(res, [0.025, 0.975])]


def score_group(g, block, replicates):
    observed = g["observado"].to_numpy(float)
    ref = g["pred_ref"].to_numpy(float)
    cand = g["pred_candidato"].to_numpy(float)
    e_ref = abs(observed - ref)
    e_cand = abs(observed - cand)
    out = {
        "n": int(len(g)),
        "n_meses": int(g["fecha_objetivo"].dt.to_period("M").nunique()),
        "mae_referencia": float(np.mean(e_ref)),
        "mae_candidato": float(np.mean(e_cand)),
        "ganancia_mae": float(np.mean(e_ref - e_cand)),
        "ic95_ganancia_mae": blocked_ci(e_ref-e_cand, g["fecha_objetivo"],
                                        block, replicates),
    }
    yrs = g["fecha_objetivo"].dt.year
    out["sensibilidad_sin_anio"] = {
        str(int(y)): float((e_ref - e_cand)[(yrs != y).to_numpy()].mean())
        for y in sorted(yrs.unique()) if (yrs != y).any()
    }
    if {"prob_ref", "prob_candidato", "evento"}.issubset(g.columns):
        p = g["prob_ref"].to_numpy(float)
        q = g["prob_candidato"].to_numpy(float)
        y = g["evento"].to_numpy(float)
        valid = np.isfinite(p) & np.isfinite(q) & np.isfinite(y) & (p >= 0) & (p <= 1) & (q >= 0) & (q <= 1) & np.isin(y, [0, 1])
        if valid.any():
            v = g.loc[valid]
            b_ref, b_new = (p[valid] - y[valid])**2, (q[valid] - y[valid])**2
            events = int(y[valid].sum())
            out["extremos"] = {
                "n": int(valid.sum()), "eventos": events,
                "prevalencia": float(y[valid].mean()),
                "brier_referencia": float(b_ref.mean()),
                "brier_candidato": float(b_new.mean()),
                "ganancia_brier": float((b_ref - b_new).mean()),
                "ic95_ganancia_brier": blocked_ci(b_ref-b_new, v["fecha_objetivo"],
                                                  block, replicates),
                "evidencia_insuficiente": events < 20 or (len(y[valid])-events) < 20,
                "nota": "evento debe estar fijado por umbrales calculados sin datos de prueba"
            }
    return out


def evaluate(df, block=12, replicates=2000):
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError("Columnas ausentes: " + ", ".join(missing))
    df = df.copy()
    df["fecha_objetivo"] = pd.to_datetime(df["fecha_objetivo"], errors="raise")
    if df[KEYS].duplicated().any():
        raise ValueError("Claves repetidas: fecha_objetivo/localidad/horizonte/variable")
    if "fecha_emision" in df:
        df["fecha_emision"] = pd.to_datetime(df["fecha_emision"], errors="raise")
        if (df["fecha_emision"] >= df["fecha_objetivo"]).any():
            raise ValueError("Fecha de emisión posterior o igual al objetivo")
    for c in ["observado", "pred_ref", "pred_candidato"]:
        df[c] = pd.to_numeric(df[c], errors="raise")
    if not np.isfinite(df[["observado", "pred_ref", "pred_candidato"]].to_numpy()).all():
        raise ValueError("Valores ausentes o infinitos: no imputar")
    if {"prob_ref","prob_candidato","evento"}.issubset(df.columns):
        for c in ["prob_ref","prob_candidato","evento"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    grouping = ["variable", "horizonte", "localidad"] + (["subzona"] if "subzona" in df else [])
    records = []
    for key, g in df.groupby(grouping, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        vals = dict(zip(grouping, [str(x) for x in key]))
        vals.update(score_group(g, block, replicates))
        records.append(vals)
    return {
        "fase": "9B", "estado": "evaluacion_retrospectiva_no_operativa",
        "bloque_meses": block, "replicas": replicates,
        "n_total": int(len(df)), "grupos": records,
        "advertencias": [
            "Los intervalos no demuestran por sí solos capacidad prospectiva",
            "No se ajustaron p-valores por multiplicidad; no afirmar significación familiar",
            "Calidad y temporalidad de predictores deben comprobarse en archivos originales",
            "No confundir reanálisis con observación instrumental ni eventos con alertas oficiales"
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument("--bloque", type=int, default=12)
    parser.add_argument("--replicas", type=int, default=2000)
    args = parser.parse_args()
    if args.bloque <= 0 or args.replicas < 100:
        parser.error("bloque >0 y replicas >=100")
    result = evaluate(pd.read_csv(args.csv), args.bloque, args.replicas)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"Fase 9B: {result['n_total']} registros, {len(result['grupos'])} grupos. JSON: {args.salida}")


if __name__ == "__main__":
    main()
