"""Fase 3T: estabilidad anual del error por estación y trazabilidad independiente.

Año evaluable = >=9 meses observados completos en ese año. La comparación
entre PISCOp y CHIRPS es pareada en los mismos meses SENAMHI.
El intervalo de remuestreo por año es DESCRIPTIVO, condicionado al periodo;
NO es evidencia de validación independiente, ni de precisión predictiva.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
STATION_N={"Cayaltí":235,"Cueva Blanca":218,"Jayanca (La Viña)":219,
           "Lambayeque":204,"Reque":233}
PRODUCTS={"PISCOp v3.0","CHIRPS v3","ERA5-Seamless"}
YEAR_MIN=1996
YEAR_MAX=2015
MIN_MONTHS=9
BOOTSTRAPS=2000
RANDOM_SEED=20261014

def main():
    df=pd.read_csv(DATA/"comparacion_3q_1996_2015.csv")
    expected={"estacion","mes","producto","observado_mm","estimado_mm"}
    if not expected.issubset(df.columns) or len(df)!=3327 or set(df.producto)!=PRODUCTS:
        raise ValueError("Fase 3Q insuficiente o modelos inesperados")
    if df[list(expected)].isna().any().any():
        raise ValueError("Nulos en series pareadas")
    if df.duplicated(["estacion","mes","producto"]).any():
        raise ValueError("Duplicados entre pares")
    if (df[["observado_mm","estimado_mm"]]<0).any().any():
        raise ValueError("Lluvias negativas")
    df["fecha"]=pd.to_datetime(df.mes+"-01",format="%Y-%m-%d",errors="raise")
    if not df.fecha.dt.year.between(YEAR_MIN,YEAR_MAX).all():
        raise ValueError("Fechas incorrectas")
    obs=df.groupby(["estacion","mes"]).agg(
        n_productos=("producto","nunique"),n_observados=("observado_mm","nunique")
    ).reset_index()
    if len(obs)!=1109 or not (obs.n_productos==3).all() or not (obs.n_observados==1).all():
        raise ValueError("Falta homogeneidad de los tres productos")
    if obs.groupby("estacion").size().to_dict()!=STATION_N:
        raise ValueError("Cobertura no corresponde a fase 3Q")
    df["anio"]=df.fecha.dt.year.astype(int)
    df["error_abs_mm"]=(df.estimado_mm-df.observado_mm).abs()
    annual=[]
    for (station,year,product),g in df.groupby(["estacion","anio","producto"]):
        annual.append({
            "estacion":station,"anio":year,"producto":product,
            "meses":len(g),"anio_evaluable":len(g)>=MIN_MONTHS,
            "mae_mm_mes":round(float(g.error_abs_mm.mean()),4),
            "rmse_mm_mes":round(float(np.sqrt(((g.estimado_mm-g.observado_mm)**2).mean())),4),
            "sesgo_mensual_mm":round(float((g.estimado_mm-g.observado_mm).mean()),4),
            "lluvia_observada_mes_media_mm":round(float(g.observado_mm.mean()),4)
        })
    yearly=pd.DataFrame(annual).sort_values(["estacion","anio","producto"])
    yearly.to_csv(DATA/"mae_estacion_anio_3t.csv",index=False)
    trace=pd.read_csv(DATA/"trazabilidad_independencia_3t.csv")
    if len(trace)!=15 or trace.duplicated(["estacion","producto"]).any():
        raise ValueError("Matriz independencia inesperada")
    pairs=trace[["estacion","producto"]]
    expected_pairs=pd.MultiIndex.from_product([sorted(STATION_N),sorted(PRODUCTS)],names=["estacion","producto"]).to_frame(index=False)
    if not pairs.sort_values(["estacion","producto"]).reset_index(drop=True).equals(
        expected_pairs.sort_values(["estacion","producto"]).reset_index(drop=True)):
        raise ValueError("Matriz de trazabilidad no coincide con estaciones y productos")
    allowed={"si","no"}
    if not set(trace.verificacion_externa_confirmada).issubset(allowed):
        raise ValueError("Estado independiente ilegible")
    # La evidencia externa necesita respaldo documental, no basta que el campo diga si.
    confirmed=int((trace.verificacion_externa_confirmada=="si").sum())
    if confirmed:
        raise ValueError("No hay soporte adjunto verificable para la independencia")
    comparisons=[]
    summaries=[]
    rng=np.random.default_rng(RANDOM_SEED)
    for station,group in yearly.groupby("estacion"):
        byyear=group.pivot(index="anio",columns="producto",values="mae_mm_mes")
        counts=group[group.producto=="PISCOp v3.0"].set_index("anio").meses
        eligible=byyear.loc[byyear.index[counts.reindex(byyear.index)>=MIN_MONTHS]].dropna()
        if eligible.empty:
            raise ValueError("Sin años evaluables para "+station)
        for year,row in eligible.iterrows():
            diff=round(float(row["CHIRPS v3"]-row["PISCOp v3.0"]),4)
            winner=("PISCOp v3.0" if diff>0.001 else "CHIRPS v3" if diff<-.001 else "empate")
            comparisons.append({"estacion":station,"anio":int(year),
                "meses":int(counts.loc[year]),"mae_piscop":float(row["PISCOp v3.0"]),
                "mae_chirps":float(row["CHIRPS v3"]),"mae_era5":float(row["ERA5-Seamless"]),
                "diferencia_chirps_menos_pisco_mm_mes":diff,"menor_mae":winner})
        comp=[c for c in comparisons if c["estacion"]==station]
        train=group.copy()
        train["error_abs_mm"] = np.nan
        # Se remuestrean años completos elegibles, conservando los meses
        # existentes de cada año y las tres estimaciones para cada mes.
        eligible_years=sorted(map(int,eligible.index))
        raw=df[(df.estacion==station)&(df.anio.isin(eligible_years))]
        compare=raw.pivot(index=["anio","mes"],columns="producto",values="error_abs_mm")
        count_by_year=np.array([len(compare.loc[y]) for y in eligible_years],dtype=int)
        sum_by_year=np.array([
            float((compare.loc[y]["CHIRPS v3"]-compare.loc[y]["PISCOp v3.0"]).sum())
            for y in eligible_years],dtype=float)
        picks=rng.integers(0,len(eligible_years),size=(BOOTSTRAPS,len(eligible_years)))
        sample=(sum_by_year[picks].sum(axis=1)/count_by_year[picks].sum(axis=1))
        ci_low,ci_high=map(float,np.quantile(sample,[.025,.975]))
        wins=[c["menor_mae"] for c in comp]
        summaries.append({
            "estacion":station,
            "anos_evaluables":len(eligible_years),
            "meses_en_anos_evaluables":int(count_by_year.sum()),
            "anos_piscop_menor_mae":wins.count("PISCOp v3.0"),
            "anos_chirps_menor_mae":wins.count("CHIRPS v3"),
            "anos_empate":wins.count("empate"),
            "diferencia_media_pareada_chirps_menos_piscop":round(float(sum_by_year.sum()/count_by_year.sum()),3),
            "rango_remuestreo_2_5":round(ci_low,3),
            "rango_remuestreo_97_5":round(ci_high,3),
            "anios_con_1998":1998 in eligible_years,
            "independencia_externa_confirmada":False,
        })
    byyear=pd.DataFrame(comparisons).sort_values(["estacion","anio"])
    summary=pd.DataFrame(summaries).sort_values("estacion")
    if len(summary)!=5 or len(byyear)==0:
        raise ValueError("Resultados de estabilidad incompletos")
    if not (summary.anos_piscop_menor_mae+summary.anos_chirps_menor_mae+
            summary.anos_empate==summary.anos_evaluables).all():
        raise ValueError("Clasificación anual incoherente")
    byyear.to_csv(DATA/"comparacion_anual_piscop_chirps_3t.csv",index=False)
    summary.to_csv(DATA/"resumen_robustez_3t.csv",index=False)
    state={
        "fase":"3T",
        "periodo":"1996-2015",
        "meses_estacion_observados":len(obs),
        "pares_producto_obs":len(df),
        "anos_evaluable_minimo_meses":MIN_MONTHS,
        "anos_estacion_evaluables":len(byyear),
        "pares_externamente_independientes_confirmados":confirmed,
        "pares_independencia_pendiente":len(trace)-confirmed,
        "intervalos_remuestreo":"descriptivos por año, no prueba de independencia externa",
        "bootstrap_semilla":RANDOM_SEED,
        "bootstrap_repeticiones":BOOTSTRAPS,
        "coordenadas_historicas_oficiales_comprobadas":False,
        "observaciones_senamhi_nuevas_2016_2025":False,
        "superioridad_predictiva_probada":False
    }
    (DATA/"estado_3t.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    report=[
      "# OAF-Lambayeque | Fase 3T: robustez temporal y protocolo de validacion independiente","",
      "> **Evaluación retrospectiva**, NO pronóstico ni validación independiente.",
      "> PISCOp v3.0 y CHIRPS v3 mezclan datos de estaciones meteorológicas.",
      "> Las ubicaciones históricas precisas de estaciones siguen pendientes de verificar.","",
      "## Auditoría realizada","",
      "- 1 109 meses-estación completos comparados con los mismos tres productos.",
      "- 3 327 pares de estimación-observación, 1996–2015.",
      "- Año evaluable: **al menos 9 meses observados completos** en cada estación.",
      "- Comparación año por año del MAE (no usar valores anuales incompletos como lluvia total).",
      "- Re-muestreo exploratorio por bloques anuales con 2 000 repeticiones y semilla fija.",
      "- El intervalo de remuestreo refleja sensibilidad a los años observados, no independencia ni causalidad.","",
      "## Estabilidad de la diferencia de errores anuales (PISCOp frente a CHIRPS)","",
      "| Estación | Años evaluables | Meses | PISCOp mejor | CHIRPS mejor | Empates | Diferencia MAE CHIRPS − PISCOp (mm/mes) | Rango remuestreo 95 % |",
      "|---|---:|---:|---:|---:|---:|---:|---|"]
    for x in summaries:
        report.append(f"| {x['estacion']} | {x['anos_evaluables']} | {x['meses_en_anos_evaluables']} | "
         f"{x['anos_piscop_menor_mae']} | {x['anos_chirps_menor_mae']} | {x['anos_empate']} | "
         f"{x['diferencia_media_pareada_chirps_menos_piscop']:.3f} | "
         f"[{x['rango_remuestreo_2_5']:.3f}; {x['rango_remuestreo_97_5']:.3f}] |")
    report+=["","## ¿Qué no demuestra este ejercicio?","",
       "- Comparar distintos años NO elimina la dependencia de estaciones en la elaboración de CHIRPS o PISCOp.",
       "- El intervalo es una exploración estadística por año, no un ensayo espacial fuera de muestra.",
       "- No hay suficientes estaciones certificadas para extrapolar a parcelas agrícolas ni demostrar errores regionales.",
       "- Pueden existir años incompletos y el mínimo de 9 meses es una regla de inclusión, NO un año de lluvia completa.",
       "- Las muestras de Cueva Blanca y estaciones costeras tienen régimen climático y representatividad espacial distintos.","",
       "## Independencia externa: evaluación documental actual","",
       "**0 de 15 combinaciones estación-producto tienen independencia externa comprobada documentalmente**.",
       "Esto NO significa que todas las estaciones estén incorporadas en cada producto; significa que aún no se ha acreditado si están o no.",
       "Matriz: datos/trazabilidad_independencia_3t.csv.","",
       "## Requisitos para afirmar validación independiente","",
       "1. Identificar para cada serie instrumental original su código, tipo, ubicación y fechas de operación según SENAMHI.",
       "2. Solicitar al equipo de PISCOp v3.0 y al CHC los inventarios de pluviómetros incorporados y el periodo de uso por estación.",
       "3. Obtener estaciones excluidas de entrenamiento/calibración y cotejar las coordenadas correctas para el mismo periodo.",
       "4. Repetir análisis con estaciones independientes por región/altitud, períodos coincidentes y métricas pareadas.",
       "5. Incorporar 2016–2025 de estaciones certificadas si están disponibles; no inferir registros faltantes.",
       "6. Publicar solo resultados debidamente identificados como retrospectivos, independientes comprobados o exploratorios.","",
       "## Fuentes metodológicas","",
       "- SENAMHI, PISCOp v3: https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru",
       "- CHIRPS3, artículo científico 2026: https://www.nature.com/articles/s41597-026-07096-4",
       "- Descarga de datos SENAMHI con registro: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos",
       "- Código de análisis: scripts/auditoria_3t_robustez.py",
       "- Resultados: datos/mae_estacion_anio_3t.csv, datos/comparacion_anual_piscop_chirps_3t.csv, datos/resumen_robustez_3t.csv, datos/estado_3t.json.",""]
    (ROOT/"AUDITORIA_3T.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"status":"ok","estado":state,"resumen":summaries},ensure_ascii=False,indent=2),flush=True)

if __name__=="__main__":
    main()
