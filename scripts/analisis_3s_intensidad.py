"""OAF-Lambayeque, fase 3S: evaluación retrospectiva estratificada de lluvia.
Los umbrales 1, 20 y 50 mm/mes son criterios descriptivos NO oficiales,
no predicciones, ni alertas agroclimáticas o fitosanitarias.
CHIRPS y PISCOp pueden contener estaciones usadas en esta comparación.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DAT=ROOT/"datos"
SRC=("CHIRPS v3","PISCOp v3.0","ERA5-Seamless")
STATIONS={"Cayaltí":235,"Cueva Blanca":218,"Jayanca (La Viña)":219,"Lambayeque":204,"Reque":233}

def metrics(g,clase,periodo):
    obs=g.observado_mm.to_numpy(dtype=float)
    est=g.estimado_mm.to_numpy(dtype=float)
    err=est-obs
    corr=float(np.corrcoef(obs,est)[0,1]) if len(g)>=5 and np.std(obs)>0 and np.std(est)>0 else None
    return dict(estacion=g.estacion.iloc[0],producto=g.producto.iloc[0],
      clase=clase,periodo=periodo,meses=len(g),
      lluvia_observada_media_mm=round(float(obs.mean()),3),
      lluvia_estim_media_mm=round(float(est.mean()),3),
      mae_mm_mes=round(float(np.abs(err).mean()),3),
      rmse_mm_mes=round(float(np.sqrt(np.mean(err**2))),3),
      sesgo_mm_mes=round(float(err.mean()),3),
      sesgo_total_pct=round(float(100*err.sum()/obs.sum()),2) if obs.sum()>0 else None,
      pearson=round(corr,4) if corr is not None else None)

def detection(g,threshold,periodo):
    obs=g.observado_mm.to_numpy(dtype=float)>=threshold
    est=g.estimado_mm.to_numpy(dtype=float)>=threshold
    tp=int(np.sum(obs&est));tn=int(np.sum(~obs&~est))
    fp=int(np.sum(~obs&est));fn=int(np.sum(obs&~est))
    assert tp+tn+fp+fn==len(g)
    prec=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    spec=tn/(tn+fp) if tn+fp else None
    f1=2*prec*recall/(prec+recall) if prec is not None and recall is not None and prec+recall else None
    val=lambda x:round(float(x),4) if x is not None else None
    return dict(estacion=g.estacion.iloc[0],producto=g.producto.iloc[0],
      periodo=periodo,umbral_mm_mes=threshold,meses=len(g),
      eventos_observados=tp+fn,eventos_estimados=tp+fp,
      verdadero_positivo=tp,verdadero_negativo=tn,
      falso_positivo=fp,falso_negativo=fn,
      precision=val(prec),sensibilidad=val(recall),
      especificidad=val(spec),f1=val(f1),
      nota="Clasificación retrospectiva; NO pronóstico")

def main():
    data=pd.read_csv(DAT/"comparacion_3q_1996_2015.csv")
    required=["estacion","mes","producto","observado_mm","estimado_mm"]
    if data[required].isna().any().any() or len(data)!=3327 or set(data.producto)!=set(SRC):
        raise ValueError("Insumos faltantes o cobertura inesperada")
    if data.duplicated(["estacion","mes","producto"]).any() or (data[["observado_mm","estimado_mm"]]<0).any().any():
        raise ValueError("Duplicados o valores negativos")
    data["fecha"]=pd.to_datetime(data.mes+"-01",format="%Y-%m-%d",errors="raise")
    if not data.fecha.dt.year.between(1996,2015).all():
        raise ValueError("Año fuera de cobertura")
    grouped=data.groupby(["estacion","mes"]).agg(
        productos=("producto","nunique"),obs=("observado_mm","nunique")).reset_index()
    if len(grouped)!=1109 or not (grouped.productos==3).all() or not (grouped.obs==1).all():
        raise ValueError("Meses no emparejados o diferentes observaciones")
    if grouped.groupby("estacion").size().astype(int).to_dict()!=STATIONS:
        raise ValueError("Meses por estación no equivalen a fase 3Q")
    data["temporada"]=np.where(data.fecha.dt.month.isin([12,1,2,3,4]),"dic_abr","may_nov")
    data["clase"]=np.select([data.observado_mm<1,data.observado_mm<20,data.observado_mm>=20],
        ["seco_lt1","bajo_1a20","lluvioso_ge20"],default="error")
    if (data.clase=="error").any():raise ValueError("Clasificación sin cubrir")
    strata=[];seasonal=[];events=[];coverage=[]
    for station,s in data.groupby("estacion"):
        obs=s[s.producto=="PISCOp v3.0"]
        coverage.append(dict(estacion=station,meses=len(obs),
          seco_lt1=int((obs.observado_mm<1).sum()),
          bajo_1a20=int(((obs.observado_mm>=1)&(obs.observado_mm<20)).sum()),
          lluvioso_ge20=int((obs.observado_mm>=20).sum()),
          intenso_ge50=int((obs.observado_mm>=50).sum())))
        for model,g in s.groupby("producto"):
            for period,sub in [("todos",g),("sin_1998",g[g.fecha.dt.year!=1998])]:
                masks={"todos":np.ones(len(sub),dtype=bool),
                    "seco_lt1":sub.observado_mm.to_numpy()<1,
                    "bajo_1a20":(sub.observado_mm.to_numpy()>=1)&(sub.observado_mm.to_numpy()<20),
                    "lluvioso_ge20":sub.observado_mm.to_numpy()>=20,
                    "intenso_ge50":sub.observado_mm.to_numpy()>=50}
                for name,mask in masks.items():
                    if np.any(mask):
                        strata.append(metrics(sub.loc[mask],name,period))
                for season,ss in sub.groupby("temporada"):
                    if len(ss):seasonal.append(metrics(ss,season,period))
                for threshold in (20,50):
                    events.append(detection(sub,threshold,period))
    cov=pd.DataFrame(coverage).sort_values("estacion")
    strat=pd.DataFrame(strata).sort_values(["estacion","periodo","clase","producto"])
    sea=pd.DataFrame(seasonal).sort_values(["estacion","periodo","clase","producto"])
    evt=pd.DataFrame(events).sort_values(["estacion","periodo","umbral_mm_mes","producto"])
    if not (cov.seco_lt1+cov.bajo_1a20+cov.lluvioso_ge20==cov.meses).all():
        raise ValueError("Estratos no son exhaustivos")
    if (strat.groupby(["estacion","periodo","clase"]).meses.nunique()!=1).any():
        raise ValueError("Productos no comparados sobre mismos meses por estrato")
    if len(evt)!=60:
        raise ValueError("Se esperan 60 filas de clasificación")
    cov.to_csv(DAT/"cobertura_3s.csv",index=False)
    strat.to_csv(DAT/"metricas_intensidad_3s.csv",index=False)
    sea.to_csv(DAT/"metricas_estacionales_3s.csv",index=False)
    evt.to_csv(DAT/"clasificacion_mensual_3s.csv",index=False)
    status=dict(fase="3S",periodo="1996-2015",meses_estacion=1109,
        pares_modelo=3327,clasificacion_no_predictiva=True,
        clases_descriptivas_no_alertas=True,
        independencia_estadistica_no_demostrada=True,
        coordenadas_historicas_preliminares=True,
        observaciones_2016_2025_disponibles=False,
        eventos_20mm=coverage,
        estratos=["seco_lt1","bajo_1a20","lluvioso_ge20","intenso_ge50"],
        estrato_intenso_solapa_con_lluvioso=True)
    (DAT/"estado_3s.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")

    lines=[
        "# OAF-Lambayeque | Fase 3S: precisión según intensidad de lluvia","",
        "> Estudio exploratorio retrospectivo: no pronóstico, no alerta de lluvia y no riesgo fitosanitario.",
        "> 1, 20 y 50 mm mensuales son umbrales descriptivos elegidos para este estudio, no oficiales.",
        "> PISCOp y CHIRPS pueden usar estaciones SENAMHI; no es validación totalmente independiente.","",
        "## Cobertura instrumental 1996-2015","",
        "Se utilizaron 1 109 meses-estación completos y 3 327 estimaciones comparables.",
        "El subgrupo de 50 mm o más está incluido dentro de los meses de 20 mm o más.","",
        "| Estación | Meses | Secos (<1 mm) | Bajos (1 a <20 mm) | Lluviosos (>=20 mm) | Intensos (>=50 mm) |",
        "|---|---:|---:|---:|---:|---:|"]
    for z in coverage:
        lines.append("| "+str(z["estacion"])+" | "+str(z["meses"])+" | "+str(z["seco_lt1"])+" | "+str(z["bajo_1a20"])+" | "+str(z["lluvioso_ge20"])+" | "+str(z["intenso_ge50"])+" |")
    for period in ("todos","sin_1998"):
        lines+=["","## MAE mensual en meses lluviosos >=20 mm, "+("incluyendo 1998" if period=="todos" else "sin 1998"),"",
          "| Estación | Producto | Meses lluviosos | MAE (mm) | Sesgo medio (mm) |",
          "|---|---|---:|---:|---:|"]
        for z in strat[(strat.periodo==period)&(strat.clase=="lluvioso_ge20")].to_dict("records"):
            lines.append("| "+str(z["estacion"])+" | "+str(z["producto"])+" | "+str(z["meses"])+" | "+str(z["mae_mm_mes"])+" | "+str(z["sesgo_mm_mes"])+" |")
    lines+=["","## Clasificación histórica de meses >=20 y >=50 mm","",
      "Los archivos incluyen la tabla de verdaderos positivos, falsos positivos, verdaderos negativos y falsos negativos, precisión, sensibilidad, especificidad y F1.",
      "Estas estadísticas miden concordancia RETROSPECTIVA, no capacidad de anticipación.",
      "Cuando hay pocos meses intensos, la incertidumbre es alta y no corresponde generalizar.","",
      "## Estaciones climáticas","",
      "La partición diciembre–abril versus mayo–noviembre es solo una clasificación de calendario; no define la climatología de todos los pisos altitudinales.","",
      "## Trazabilidad","",
      "Base: datos/comparacion_3q_1996_2015.csv (series SENAMHI completas y productos históricos).",
      "Productos: PISCOp v3.0, CHIRPS v3 y ERA5-Seamless. No se consultaron ni añadieron nuevos datos observados.",
      "Código: scripts/analisis_3s_intensidad.py",
      "Archivos: datos/cobertura_3s.csv; datos/metricas_intensidad_3s.csv; datos/metricas_estacionales_3s.csv; datos/clasificacion_mensual_3s.csv; datos/estado_3s.json.",
      "Pendientes: metadatos oficiales de estaciones, series 2016–2025 y validación espacial independiente.",
      "Los resultados no son recomendaciones operativas de control de enfermedades agrícolas.",""]
    (ROOT/"ANALISIS_3S.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"pares":len(data),"meses_estacion":len(grouped),
        "cobertura":coverage,"filas_estrato":len(strat),"clasificaciones":len(evt)},ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
