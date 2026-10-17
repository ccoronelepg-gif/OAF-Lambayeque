#!/usr/bin/env python3
"""8U-B: cruce descriptivo de anomalías de viento local con Niño 1+2 NOAA.

No estima teleconexión causal ni modelo predictivo y emplea la serie NOAA
revisada, con rezago fijo t-2 definido antes de analizar resultados.
"""
from __future__ import annotations
import csv,io,json,math,statistics,argparse,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contraste_oceanico_8t as noaa
import viento_oceano_8u as wind
ROOT=Path(__file__).resolve().parents[1]
OUT="datos/viento_8u"
FILE="datos/viento_8u/viento_mensual_8u.csv"
FIELDS=("localidad","n_meses_emparejados","correlacion_anomalia_viento_sst_nino12_rezago_2",
        "correlacion_anomalia_zonal_sst_nino12_rezago_2",
        "correlacion_anomalia_meridional_sst_nino12_rezago_2",
        "velocidad_media_ms","mismos_pixeles_comprobados","interpretacion")
def lag(date,months=2):
    yr,mo=map(int,date.split("-"))
    idx=yr*12+mo-1-months
    return f"{idx//12:04d}-{idx%12+1:02d}"

def pearson(x,y):
    if len(x)!=len(y) or len(x)<40:raise ValueError("Pares insuficientes")
    a=statistics.mean(x);b=statistics.mean(y)
    xx=[v-a for v in x];yy=[v-b for v in y]
    d=math.sqrt(sum(v*v for v in xx)*sum(v*v for v in yy))
    return None if d<1e-10 else sum(u*v for u,v in zip(xx,yy))/d

def study(root):
    with (root/FILE).open(encoding="utf-8-sig",newline="") as f:
        records=list(csv.DictReader(f))
    state=json.loads((root/OUT/"estado_factores_8u.json").read_text(encoding="utf-8"))
    if state.get("bloques_viento_obtenidos")!=3 or state.get("testigos_viento_historico_completos")!=4:
        raise ValueError("No se han completado los 1440 meses de viento reales")
    if len(records)!=4*360:raise ValueError("Viento mensual incompleto")
    index,metadata=noaa.archive(root)
    result=[]
    for locality in wind.LOCATIONS:
        rows=sorted((r for r in records if r["localidad"]==locality),key=lambda r:r["mes"])
        if len(rows)!=360 or [r["mes"] for r in rows]!=[
            f"{yr}-{mo:02d}" for yr in range(1996,2026) for mo in range(1,13)]:
            raise ValueError("Cobertura mensual de localidad incompleta")
        vars=("viento_10m_media_ms","componente_zonal_aproximada_ms",
              "componente_meridional_aproximada_ms")
        values={v:[float(r[v]) for r in rows] for v in vars}
        if any(not math.isfinite(x) for seq in values.values() for x in seq):
            raise ValueError("Vientos no numéricos")
        # Subtract own month-calendar 1996-2025 normal, descriptive only.
        norm={v:{m:statistics.mean(values[v][i] for i,r in enumerate(rows)
                if int(r["mes"][-2:])==m) for m in range(1,13)} for v in vars}
        anomalies={v:[values[v][i]-norm[v][int(r["mes"][-2:])]
                      for i,r in enumerate(rows)] for v in vars}
        present=[i for i,r in enumerate(rows) if lag(r["mes"]) in index]
        sst=[index[lag(rows[i]["mes"])]["nino12_anom_c"] for i in present]
        def corr(name):
            z=pearson([anomalies[name][i] for i in present],sst)
            return round(z,6) if z is not None else None
        result.append({
          "localidad":locality,"n_meses_emparejados":len(present),
          "correlacion_anomalia_viento_sst_nino12_rezago_2":corr(vars[0]),
          "correlacion_anomalia_zonal_sst_nino12_rezago_2":corr(vars[1]),
          "correlacion_anomalia_meridional_sst_nino12_rezago_2":corr(vars[2]),
          "velocidad_media_ms":round(statistics.mean(values[vars[0]]),4),
          "mismos_pixeles_comprobados":"no",
          "interpretacion":"asociacion_descriptiva_no_causal_ni_predictiva"})
    status={
      "fase":"8U","componente":"contraste_descriptivo_vientos_sst",
      "n_localidades":4,"n_meses_maximos_por_localidad":360,
      "periodo_viento":"1996–2025","rezago_SST_meses":2,
      "modelo_viento":"ERA5 modelo no anemometro",
      "indice_SST":"NOAA Niño1+2 revisado, no SST costera in situ ni ICEN oficial",
      "periodo_de_normales_descriptivas":"1996–2025, no usar en backtest",
      "anomalías_de_viento_por_media_calendario_local":True,
      "correlaciones_no_son_pronosticos":True,
      "corrientes_marinas_no_estimadas_en_cruce":True,
      "frentes_fisicos_y_causalidad_no_verificados":True,
      "sha256_NOAA_original":metadata["sha256_original"],
      "sha256_serie_viento_mensual":hashlib.sha256((root/FILE).read_bytes()).hexdigest(),
      "correlaciones":result
    }
    return status,result

def csvout(rows):
    f=io.StringIO(newline="")
    w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n")
    w.writeheader();w.writerows(rows);return f.getvalue()

def publish(root,check=False):
    state,rows=study(root)
    base=root/OUT
    items={
      base/"correlaciones_viento_sst_8u.json":json.dumps(state,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
      base/"correlaciones_viento_sst_8u.csv":csvout(rows)}
    if not check:base.mkdir(parents=True,exist_ok=True)
    for path,value in items.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=value:
                raise ValueError("Correlaciones 8U no son reproducibles")
        elif not path.exists() or path.read_text(encoding="utf-8")!=value:
            path.write_text(value,encoding="utf-8")
    print(json.dumps({"localidades":len(rows),"correlacion":rows,"check":check},ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args();publish(a.root,a.check)
