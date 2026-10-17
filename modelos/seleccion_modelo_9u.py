#!/usr/bin/env python3
"""Fase 9U: selección objetiva entre climatología, persistencia y RF (sin GCN no evaluada).
Ejecutar DESPUÉS de 9T. Nunca afirma que RF es el mejor por anticipado.
"""
import argparse, json
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--predicciones",type=Path,required=True)
    p.add_argument("--salida",type=Path,default=Path("resultados/9u"))
    a=p.parse_args()
    d=pd.read_csv(a.predicciones,dtype={"sector_id":str})
    required={"sector_id","mes","periodo","modelo","observado_mm","predicho_mm"}
    if not required.issubset(d.columns): raise ValueError("Faltan columnas obligatorias")
    if d[list(required)].isnull().any().any(): raise ValueError("Valores ausentes")
    if d.duplicated(["sector_id","mes","periodo","modelo"]).any(): raise ValueError("Duplicados")
    d=d[d.periodo=="prueba"].copy()
    expected={"climatologia","persistencia","random_forest"}
    if not expected.issubset(set(d.modelo)): raise ValueError("Falta algún modelo base")
    if not np.isfinite(d[["observado_mm","predicho_mm"]].to_numpy()).all(): raise ValueError("No finitos")
    d["error_abs"]=abs(d.predicho_mm-d.observado_mm)
    d["error_sq"]=(d.predicho_mm-d.observado_mm)**2
    # Equidad: mismos sector-mes y los mismos objetivos por cada modelo.
    sets={m:set(zip(g.sector_id,g.mes)) for m,g in d.groupby("modelo") if m in expected}
    if not all(s==next(iter(sets.values())) for s in sets.values()):
        raise ValueError("Sector-mes no coincidentes")
    wide=d[d.modelo.isin(expected)].pivot(index=["sector_id","mes"],columns="modelo",values="observado_mm")
    if (wide.max(axis=1)-wide.min(axis=1)).abs().max()>1e-8:
        raise ValueError("Objetivos inconsistentes")
    overall=(d[d.modelo.isin(expected)].groupby("modelo")
        .agg(n=("error_abs","size"),mae_mm=("error_abs","mean"),mse=("error_sq","mean")).reset_index())
    overall["rmse_mm"]=np.sqrt(overall["mse"])
    overall=overall.drop(columns="mse").sort_values(["mae_mm","rmse_mm","modelo"])
    ref=float(overall.loc[overall.modelo=="climatologia","mae_mm"].iloc[0])
    rf=float(overall.loc[overall.modelo=="random_forest","mae_mm"].iloc[0])
    per=(d[d.modelo.isin(expected)].groupby(["sector_id","modelo"])
         .agg(n=("error_abs","size"),mae_mm=("error_abs","mean")).reset_index())
    # GCN no está presente. Solo candidato provisional con evidencia de prueba vs baseline.
    better=rf<ref
    decision=("RF_CANDIDATO_PROVISIONAL" if better else "RF_NO_SUPERA_CLIMATOLOGIA")
    a.salida.mkdir(parents=True,exist_ok=True)
    overall.to_csv(a.salida/"resumen_modelos.csv",index=False)
    per.to_csv(a.salida/"resumen_sector.csv",index=False)
    status={"fase":"9U","decision":decision,"ganador_descriptivo_entre_baselines":str(overall.iloc[0].modelo),
        "rf_mae_mm":rf,"climatologia_mae_mm":ref,
        "gc_n":"NO_ENTRENADA_NI_COMPARADA","validacion_instrumental":"NO_REALIZADA",
        "advertencia":"Comparación retrospectiva CHIRPS, no exactitud operativa; ranking sin intervalos robustos de confianza"}
    (a.salida/"decision.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(status,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
