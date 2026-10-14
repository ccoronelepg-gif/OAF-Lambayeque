"""Consolidacion reproducible de sensibilidad geográfica CHIRPS 1996-2015.

Identidad instrumental histórica no demostrada. Las celdas se analizan como
candidatas geográficas, sin seleccionar coordenadas por ajuste del MAE.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
BLOCKS=["1996_2000","2001_2005","2006_2010","2011_2015"]
EXPECTED=1109
COLS=["estacion","mes","observado_mm","original_mm","alternativo_mm",
      "mismo_pixel","distancia_coordenadas_km","diferencia_mm"]
def main():
    data=[]
    state={}
    for block in BLOCKS:
        p=DATA/("sensibilidad_3r_mensual_"+block+".csv")
        st=DATA/("estado_3r_"+block+".json")
        if not p.is_file() or not st.is_file():
            raise FileNotFoundError("Bloque o estado faltante: "+block)
        f=pd.read_csv(p)
        if not set(COLS).issubset(f.columns):
            raise ValueError("Columnas faltantes "+block)
        if f.duplicated(["estacion","mes"]).any():
            raise ValueError("Duplicados "+block)
        data.append(f.assign(bloque=block))
        state[block]=json.loads(st.read_text(encoding="utf-8"))
        if state[block]["raster_descargas_fallidas"]:
            raise ValueError("Bloque con fallos de descarga "+block)
        if len(f)!=state[block]["meses_estacion_validos_senamhi"]:
            raise ValueError("Meses incompletos "+block)
    merged=pd.concat(data,ignore_index=True)
    if merged.duplicated(["estacion","mes"]).any():
        raise ValueError("Duplicacion entre bloques")
    if len(merged)!=EXPECTED:
        raise ValueError(f"Se esperan {EXPECTED} meses-estacion, hay {len(merged)}")
    if merged[["original_mm","alternativo_mm","observado_mm"]].isna().any().any():
        raise ValueError("Valores de precipitación faltantes")
    if (merged[["original_mm","alternativo_mm","observado_mm"]]<0).any().any():
        raise ValueError("Valores de precipitación negativos")
    if not np.allclose(merged.alternativo_mm-merged.original_mm,merged.diferencia_mm,atol=.0002):
        raise ValueError("Incoherencia de diferencia mensual")
    reference=pd.read_csv(DATA/"comparacion_3q_1996_2015.csv")
    reference=reference[reference.producto=="CHIRPS v3"]
    check=merged.merge(reference[["estacion","mes","observado_mm","estimado_mm"]],
         on=["estacion","mes"],how="left",validate="one_to_one",suffixes=("","_ref"))
    if check.estimado_mm.isna().any() or not np.allclose(check.original_mm,check.estimado_mm,atol=.0002):
        raise ValueError("Desacuerdo con CHIRPS de fase 3Q")
    if not np.allclose(check.observado_mm,check.observado_mm_ref,atol=.0002):
        raise ValueError("SENAMHI original no coincide con histórico")
    # Las 10 comparaciones del piloto 1998 y 2000 deben ser reproducibles.
    pilot=pd.read_csv(DATA/"sensibilidad_3r_resumen.csv")
    for x in pilot.itertuples(index=False):
        sample=merged[(merged.estacion==x.estacion)&
                 (merged.mes.str[:4].astype(int)==int(x.ano))]
        if len(sample)!=12:
            raise ValueError("No hay 12 meses para cotejo con piloto "+x.estacion)
        if abs(sample.original_mm.sum()-x.base_anual_mm)>.02 or \
           abs(sample.alternativo_mm.sum()-x.alternativo_anual_mm)>.02:
            raise ValueError("Diferencias con auditoria piloto 3R "+x.estacion)
    out=[]
    for station,group in merged.groupby("estacion"):
        for periodo,part in [("todos",group),("sin_1998",group[group.mes.str[:4]!="1998"])]:
            obs=part.observado_mm.to_numpy(float)
            base=part.original_mm.to_numpy(float)
            alt=part.alternativo_mm.to_numpy(float)
            oe=base-obs
            ae=alt-obs
            dist=part.distancia_coordenadas_km.to_numpy(float)
            if np.ptp(dist)>.0001:
                raise ValueError("Distancia entre coordenadas cambió para "+station)
            out.append({
              "estacion":station,"periodo":periodo,"meses":len(part),
              "meses_mismo_pixel":int(part.mismo_pixel.sum()),
              "cambio_pixel_pct":round(float(100*(~part.mismo_pixel).mean()),2),
              "distancia_coordenadas_km":round(float(dist[0]),3),
              "obs_total_mm":round(float(obs.sum()),3),
              "original_total_mm":round(float(base.sum()),3),
              "alternativo_total_mm":round(float(alt.sum()),3),
              "diferencia_total_mm":round(float((alt-base).sum()),3),
              "mae_original_mm":round(float(np.abs(oe).mean()),3),
              "mae_alternativo_mm":round(float(np.abs(ae).mean()),3),
              "diferencia_mae_mm":round(float(np.abs(ae).mean()-np.abs(oe).mean()),3),
              "rmse_original_mm":round(float(np.sqrt(np.mean(oe**2))),3),
              "rmse_alternativo_mm":round(float(np.sqrt(np.mean(ae**2))),3)
            })
    full=pd.DataFrame(out).sort_values(["estacion","periodo"])
    merged.sort_values(["estacion","mes"]).to_csv(DATA/"sensibilidad_3r_1996_2015.csv",index=False)
    full.to_csv(DATA/"metricas_sensibilidad_3r_1996_2015.csv",index=False)
    observed=merged.groupby("estacion").size().astype(int).to_dict()
    stat={"fase":"3R","periodo":"1996-2015",
       "meses_estacion_validos":len(merged),
       "extracciones_pixel":2*len(merged),
       "num_estaciones":merged.estacion.nunique(),
       "meses_por_estacion":observed,
       "bloques_completos":BLOCKS,
       "incidencias_en_bloques":sum(len(state[b]["raster_descargas_fallidas"]) for b in BLOCKS),
       "coincidencia_con_chirps_3q_verificada":True,
       "coincidencia_piloto_1998_2000_verificada":True,
       "identidad_geografica_historica_certificada":False,
       "cubre_climatologia_1996_2025":False}
    (DATA/"estado_3r_1996_2015.json").write_text(json.dumps(stat,ensure_ascii=False,indent=2),encoding="utf-8")
    report=["# OAF-Lambayeque | Sensibilidad geográfica multianual CHIRPS 1996–2015","",
      "> **Exploratorio**: no se ha confirmado la identidad ni continuidad instrumental entre coordenadas documentales.",
      "> La mejor coincidencia estadística NO demuestra la ubicación verdadera de la estación.",
      "> Los datos instrumentales de 2016–2025 no están incluidos.","",
      "## Auditoría de integridad","",
      "- Meses-estación completos de SENAMHI: **"+str(len(merged))+"**.",
      "- Extracciones de CHIRPS (dos coordenadas): **"+str(2*len(merged))+"**.",
      "- Reproducción de CHIRPS 3Q: **confirmada**.",
      "- Reproducción del piloto 3R de 1998 y 2000: **confirmada**.",
      "- Fallos de descarga en los bloques: **0**.","",
      "## Variación espacial y errores mensuales","",
      "| Estación | Meses | Meses mismo píxel | Distancia puntos (km) | Cambio acumulado CHIRPS (mm) | MAE coordenada 3Q | MAE alternativa |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for x in full[full.periodo=="todos"].to_dict("records"):
        report.append("| "+str(x["estacion"])+" | "+str(x["meses"])+" | "+str(x["meses_mismo_pixel"])+
             " | "+str(x["distancia_coordenadas_km"])+" | "+str(x["diferencia_total_mm"])+
             " | "+str(x["mae_original_mm"])+" | "+str(x["mae_alternativo_mm"])+" |")
    report+=["","## Sensibilidad excluyendo 1998","",
       "| Estación | Meses | Cambio acumulado CHIRPS (mm) | MAE original | MAE alternativa |",
       "|---|---:|---:|---:|---:|"]
    for x in full[full.periodo=="sin_1998"].to_dict("records"):
        report.append("| "+str(x["estacion"])+" | "+str(x["meses"])+" | "+
                      str(x["diferencia_total_mm"])+" | "+str(x["mae_original_mm"])+" | "+str(x["mae_alternativo_mm"])+" |")
    report+=["","## Interpretación y límites","",
       "El efecto observado depende de la celda CHIRPS de 0,05 grados. No equivale a la magnitud de un error de GPS, ni permite deducir reubicaciones de instrumentos.",
       "El punto de Cueva Blanca alternativo procede de un documento con código/ubicación discordantes; no atribuir sus valores a la serie histórica.",
       "Un cambio de píxel con mayor MAE puede deberse a heterogeneidad espacial o dependencia de pluviómetros; no evaluar ubicación mediante el ajuste estadístico.",
       "Las estaciones meteorológicas pueden haber intervenido en CHIRPS; no es una validación independiente.",
       "Solo lluvia mensual; no construir pronósticos ni alertas fitosanitarias a partir de esta sensibilidad.","",
       "Datos: datos/sensibilidad_3r_1996_2015.csv y datos/metricas_sensibilidad_3r_1996_2015.csv.",
       "Código reproducible: scripts/sensibilidad_3r_multianual.py y scripts/consolidar_sensibilidad_3r.py.",
       "Fuente CHIRPS: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"]
    (ROOT/"SENSIBILIDAD_3R_MULTIANUAL.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(stat,ensure_ascii=False),flush=True)
    return len(merged)

if __name__=="__main__":
    main()
