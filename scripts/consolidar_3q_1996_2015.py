"""OAF: consolidar los cuatro bloques CHIRPS/PISCOp/ERA5 1996-2015.
Usar solamente meses SENAMHI completos, con tres modelos coincidentes.
Los productos basados en pluviómetros no son validación independiente.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DAT=ROOT/"datos"
BLOCKS=("1996_2000","2001_2005","2006_2010","2011_2015")
PRODS=("CHIRPS v3","PISCOp v3.0","ERA5-Seamless")

def metrics(g,model,period):
    observed=g.observado_mm.to_numpy(dtype=float)
    modeled=g.estimado_mm.to_numpy(dtype=float)
    error=modeled-observed
    total=float(observed.sum())
    return dict(estacion=g.estacion.iloc[0],producto=model,periodo=period,
       meses=len(g),observado_mm=round(total,3),
       estimado_mm=round(float(modeled.sum()),3),
       sesgo_pct=round(float(100*error.sum()/total),2) if total>0 else None,
       sesgo_mensual_mm=round(float(error.mean()),3),
       mae_mensual_mm=round(float(np.abs(error).mean()),3),
       rmse_mensual_mm=round(float(np.sqrt(np.mean(error**2))),3),
       pearson=round(float(np.corrcoef(observed,modeled)[0,1]),4)
          if len(g)>=3 and np.std(observed)>0 and np.std(modeled)>0 else None)

def main():
    frames=[]
    states={}
    for block in BLOCKS:
        path=DAT/("comparacion_3q_multianual_"+block+".csv")
        meta=(DAT/"estado_3q_multianual.json" if block=="1996_2000"
              else DAT/("estado_3q_"+block+".json"))
        if not path.exists() or not meta.exists():
            raise FileNotFoundError("Bloque faltante: "+block)
        frame=pd.read_csv(path)
        frame["bloque"]=block
        frames.append(frame)
        states[block]=json.loads(meta.read_text(encoding="utf-8"))
    all_data=pd.concat(frames,ignore_index=True)
    if all_data.empty or all_data[["observado_mm","estimado_mm"]].isna().any().any():
        raise ValueError("Datos vacios o nulos")
    if (all_data.observado_mm<0).any() or (all_data.estimado_mm<0).any():
        raise ValueError("Precipitacion negativa")
    if all_data.duplicated(["estacion","mes","producto"]).any():
        raise ValueError("Duplicacion por mes/producto")
    if set(all_data.producto.unique())!=set(PRODS):
        raise ValueError("Producto inesperado")
    pairs=all_data.groupby(["estacion","mes"]).agg(
       cantidad=("producto","nunique"),obs=("observado_mm","nunique")).reset_index()
    if not ((pairs.cantidad==3).all() and (pairs.obs==1).all()):
        raise ValueError("Meses con producto faltante u observacion distinta")
    truth=pd.read_csv(DAT/"senamhi_mensual_completo_1996_2015.csv")
    truth=truth[truth.dias_validos==truth.dias_mes][["estacion","mes","observado_mm"]]
    if truth.duplicated(["estacion","mes"]).any():raise ValueError("Duplicados SENAMHI")
    chk=all_data.merge(truth,on=["estacion","mes"],validate="many_to_one",
       how="left",suffixes=("","_original"))
    if chk.observado_mm_original.isna().any() or not np.allclose(
        chk.observado_mm,chk.observado_mm_original,atol=.001):
        raise ValueError("Observaciones inconsistentes con SENAMHI original")
    full=all_data[["estacion","mes","producto","observado_mm","estimado_mm","diferencia_mm","bloque"]]
    full.sort_values(["estacion","mes","producto"]).to_csv(
        DAT/"comparacion_3q_1996_2015.csv",index=False)
    results=[]
    for (station,model),g in full.groupby(["estacion","producto"]):
        for period,chunk in [("todos",g),("sin_1998",g[g.mes.str[:4]!="1998"]),
                             ("solo_1998",g[g.mes.str[:4]=="1998"])]:
            if len(chunk):results.append(metrics(chunk,model,period))
    stat=pd.DataFrame(results).sort_values(["estacion","periodo","producto"])
    stat.to_csv(DAT/"metricas_3q_1996_2015.csv",index=False)
    n=len(pairs)
    state=dict(periodo="1996-2015",meses_senamhi_completos=len(truth),
       meses_coincidentes_tres_productos=n,pares_estimados=len(full),
       cobertura_sobre_validos_pct=round(100*n/len(truth),2),
       meses_por_estacion=pairs.groupby("estacion").size().astype(int).to_dict(),
       meses_por_ano=pairs.assign(ano=pairs.mes.str[:4]).groupby("ano").size().astype(int).to_dict(),
       incidencias_por_bloque={b:len(states[b].get("incidencias",[])) for b in BLOCKS},
       ubicaciones_instrumentales_provisionales=True,
       validacion_independiente=False,climatologia_1996_2025_completa=False)
    (DAT/"estado_3q_1996_2015.json").write_text(
      json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    report=[
      "# OAF-Lambayeque | Validacion CHIRPS, PISCOp y ERA5 1996-2015","",
      "> Exploratorio: coordenadas historicas de estaciones sin confirmar.",
      "> CHIRPS y PISCOp usan mediciones pluviometricas y pueden depender de estaciones contrastadas.",
      "> La evaluacion NO cubre 1996-2025 ni equivale a validacion independiente.","",
      "## Calidad y cobertura","",
      "- Meses-estacion SENAMHI completos: **"+str(len(truth))+"**.",
      "- Meses-estacion con los tres productos comparables: **"+str(n)+"**.",
      "- Pares estimacion-observacion: **"+str(len(full))+"**.",
      "- Cobertura sobre meses validos: **"+str(state["cobertura_sobre_validos_pct"])+" %**.",
      "- Sin imputacion de datos faltantes como lluvia cero.","",
      "## Estadisticas de todos los meses 1996-2015","",
      "| Estacion | Producto | Meses | MAE mm/mes | RMSE mm/mes | Sesgo % | Pearson |",
      "|---|---|---:|---:|---:|---:|---:|"]
    for r in stat[stat.periodo=="todos"].to_dict("records"):
        report.append("| "+str(r["estacion"])+" | "+str(r["producto"])+" | "+str(r["meses"])+
           " | "+str(r["mae_mensual_mm"])+" | "+str(r["rmse_mensual_mm"])+" | "+
           str(r["sesgo_pct"])+" | "+str(r["pearson"])+" |")
    report+=["","## Sensibilidad: excluyendo 1998","",
        "| Estacion | Producto | Meses | MAE mm/mes | Sesgo % |",
        "|---|---|---:|---:|---:|"]
    for r in stat[stat.periodo=="sin_1998"].to_dict("records"):
        report.append("| "+str(r["estacion"])+" | "+str(r["producto"])+" | "+
           str(r["meses"])+" | "+str(r["mae_mensual_mm"])+" | "+str(r["sesgo_pct"])+" |")
    report+=["","## Procedencia","",
      "CHIRPS v3 mensual GeoTIFF de Climate Hazards Center, píxel que contiene el punto provisional.",
      "SENAMHI: registros diarios descargados previamente, agregados solo con todos los días válidos.",
      "PISCOp y ERA5: comparaciones guardadas en fase 3O para las mismas fechas.",
      "Fuente CHIRPS: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/",
      "No usar como alerta fitosanitaria, pronóstico ni evidencia de precisión fuera de muestra.",""]
    for b in BLOCKS:
        report.append("Bloque "+b+": "+str(states[b].get("pares_estacion_mes"))+
                      " meses-estacion, "+str(len(states[b].get("incidencias",[])))+" incidencias.")
    (ROOT/"VALIDACION_3Q_1996_2015.md").write_text(
       "\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2),flush=True)
    return n

if __name__=="__main__":
    if not main():raise SystemExit(1)
