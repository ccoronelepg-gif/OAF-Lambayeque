#!/usr/bin/env python3
"""8U: descriptively align 2017–2025 atmospheric winds, SST and sea currents.

Not a forecast. Same-season monthly anomalies calculated on full 2017–2025
for exploratory correlations only (would LEAK in a backtest). No claimed
causality or oceanic dynamical attribution.
"""
from __future__ import annotations
import argparse,csv,io,json,math,statistics,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOTS={
 "viento":"datos/meteorologia_8u/vientos_mensuales_8u.csv",
 "sst":"datos/oceanografia_8u/tsm_nino12_mensual_8u.csv",
 "corrientes":"datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv",
 "estado_viento":"datos/meteorologia_8u/estado_viento_8u.json",
 "estado_corrientes":"datos/corrientes_8u/estado_corrientes_8u.json",
 "estado_sst":"datos/oceanografia_8u/estado_oceanografia_8u.json"
}
PAIRS=(("Mar_frente_Pimentel","Aguas_frente_Pimentel"),
       ("Mar_norte_Lambayeque","Aguas_norte_Lambayeque"))
OUT="datos/relaciones_fisicas_8u"
FIELDS=("punto_marino","punto_viento_atmosferico",
  "n_meses_2017_2025","r_anomalia_u_viento_vs_u_geostrofica",
  "r_anomalia_v_viento_vs_v_geostrofica",
  "r_anomalia_velocidad_viento_vs_rapidez_geostrofica",
  "r_anomalia_sst_nino12_t_menos_2_vs_u_geostrofica",
  "r_anomalia_sst_nino12_t_menos_2_vs_v_geostrofica",
  "correlaciones_solo_descriptivas_no_predictivas")
def read(root,path):
 with (root/path).open(encoding="utf-8-sig",newline="") as f:
  return list(csv.DictReader(f))
def corr(a,b):
 if len(a)!=len(b) or len(a)<24:raise ValueError("Relación con pocos meses")
 x=statistics.mean(a);y=statistics.mean(b)
 xx=[v-x for v in a];yy=[v-y for v in b]
 norm=math.sqrt(sum(t*t for t in xx)*sum(t*t for t in yy))
 return None if norm<1e-10 else sum(v*w for v,w in zip(xx,yy))/norm
def anomalies(vals):
 dates=sorted(vals)
 if len(dates)!=108 or dates[0]!="2017-01" or dates[-1]!="2025-12":
  raise ValueError("Se exigen 108 meses 2017–2025 sin imputación")
 base={m:statistics.mean(vals[f"{y}-{m:02d}"] for y in range(2017,2026)) for m in range(1,13)}
 return {day:vals[day]-base[int(day[-2:])] for day in dates}
def previous_month(day,count):
 y,m=map(int,day.split("-"))
 k=y*12+m-1-count
 return f"{k//12:04d}-{k%12+1:02d}"
def check_states(root):
 wind=json.loads((root/ROOTS["estado_viento"]).read_text())
 marine=json.loads((root/ROOTS["estado_corrientes"]).read_text())
 sst=json.loads((root/ROOTS["estado_sst"]).read_text())
 if wind["n_bloques_verificados"]!=3 or wind["n_filas_publicadas"]!=2160:
  raise ValueError("Viento 8U no completó 30 años")
 if marine["n_series_punto_periodo_verificadas"]!=4 or marine["n_filas_geostroficas_reales_fuente_modelada_publicadas"]!=216:
  raise ValueError("No se completó historia NOAA/AOML 2017–2025")
 if sst["meses_tsm_historia"]!=360 or sst["tsm_costa_lambayeque_medido"] is not False:
  raise ValueError("NOAA SST Niño1+2 incompleto o etiquetado como costa")
 return wind,marine,sst
def evaluate(root):
 check_states(root)
 winds=read(root,ROOTS["viento"])
 sea=read(root,ROOTS["corrientes"])
 ssts=read(root,ROOTS["sst"])
 ocean={row["mes"]:float(row["anomalia_tsm_nino12_c"]) for row in ssts}
 if len(ocean)!=360:raise ValueError("SST Niño1+2 no cubre 360 meses")
 out=[]
 for wname,cname in PAIRS:
  w=[x for x in winds if x["sitio"]==wname and "2017-01"<=x["mes"]<="2025-12"]
  c=[x for x in sea if x["punto"]==cname]
  if len(w)!=108 or len(c)!=108 or len(set(x["mes"] for x in w))!=108 or len(set(x["mes"] for x in c))!=108:
   raise ValueError("Viento y corriente necesitan 108 meses emparejados")
  ww={p["mes"]:p for p in w};cc={p["mes"]:p for p in c}
  if set(ww)!=set(cc):raise ValueError("Meses distintos entre viento y corriente")
  def a(rows,name):return anomalies({date:float(x[name]) for date,x in rows.items()})
  wu=a(ww,"componente_este_aprox_m_s")
  wv=a(ww,"componente_norte_aprox_m_s")
  ws=a(ww,"velocidad_media_10m_m_s")
  cu=a(cc,"u_este_geostrofica_m_s")
  cv=a(cc,"v_norte_geostrofica_m_s")
  cm=a(cc,"magnitud_vector_media_m_s")
  # SST 2017–2025 anomalies are monthly NOAA CPC region values already,
  # but de-seasonalize again with 2017–2025 for comparable covariance.
  # t−2 uses 2016/2017 preceding months. No target-date SST is used.
  months=sorted(ww)
  osst={day:ocean[previous_month(day,2)] for day in months}
  osst_anom=anomalies(osst)
  def r(x,y):
   z=corr([x[d] for d in months],[y[d] for d in months])
   return round(z,5) if z is not None else None
  out.append({
   "punto_marino":cname,"punto_viento_atmosferico":wname,
   "n_meses_2017_2025":len(months),
   "r_anomalia_u_viento_vs_u_geostrofica":r(wu,cu),
   "r_anomalia_v_viento_vs_v_geostrofica":r(wv,cv),
   "r_anomalia_velocidad_viento_vs_rapidez_geostrofica":r(ws,cm),
   "r_anomalia_sst_nino12_t_menos_2_vs_u_geostrofica":r(osst_anom,cu),
   "r_anomalia_sst_nino12_t_menos_2_vs_v_geostrofica":r(osst_anom,cv),
   "correlaciones_solo_descriptivas_no_predictivas":"true"})
 state={
  "fase":"8U","estado":"108_meses_por_punto_correlacion_descriptiva",
  "n_puntos_marinos":len(out),"n_meses_por_punto":108,
  "n_parejas_mes_punto":216,"periodo":"2017–2025",
  "normal_descriptiva_estacional":"2017–2025",
  "normal_no_apta_para_backtest_porque_contiene_futuro":True,
  "uso_indice_nino12_rezagado_dos_meses":True,
  "vientos_aire_ERA5_no_corrientes_marinas":True,
  "corrientes_solo_componente_geostrofica":True,
  "no_asume_coincidencia_exacta_de_celdas_aire_y_mar":True,
  "asociacion_estadistica_no_causalidad":True,
  "habilidad_predictiva_evaluada":False,
  "validacion_instrumental_SENAMHI_IMARPE":False,
  "zonas_homogeneas_certificadas":0,
  "perfiles":out,
  "sha256_csv_entrada":{k:hashlib.sha256((root/ROOTS[k]).read_bytes()).hexdigest() for k in ("viento","sst","corrientes")}
 }
 return state,out
def csv_text(rows):
 buf=io.StringIO(newline="")
 w=csv.DictWriter(buf,fieldnames=FIELDS,lineterminator="\n")
 w.writeheader();w.writerows(rows)
 return buf.getvalue()
def publish(root,check=False):
 st,rows=evaluate(root)
 base=root/OUT
 results={
  base/"estado_relaciones_8u.json":json.dumps(st,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
  base/"correlaciones_fisicas_8u.csv":csv_text(rows)
 }
 if not check:base.mkdir(parents=True,exist_ok=True)
 for path,body in results.items():
  if check:
   if not path.exists() or path.read_text(encoding="utf-8")!=body:
    raise ValueError("8U correlación física no reproduce fuentes")
  elif not path.exists() or path.read_text(encoding="utf-8")!=body:
   path.write_text(body,encoding="utf-8")
 print(json.dumps({"fase":"8U","relaciones":len(rows),"check":check}))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--root",type=Path,default=ROOT)
 p.add_argument("--check",action="store_true")
 o=p.parse_args()
 publish(o.root,o.check)
