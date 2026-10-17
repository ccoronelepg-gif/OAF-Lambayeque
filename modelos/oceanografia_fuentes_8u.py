#!/usr/bin/env python3
"""OAF 8U: monthly Niño1+2 absolute SST & anomaly; marine-current intake QA.

NOAA CPC Niño1+2 is an ocean REGION index, not a coastal point thermometer.
Currents require actual ocean u/v observations or model analysis. Metadata
does not substitute for valid time series. No sea-current claims from winds.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contraste_oceanico_8t as cpc
ROOT=Path(__file__).resolve().parents[1]
OUT="datos/oceanografia_8u"
FIELDS=("mes","tsm_nino12_c","anomalia_tsm_nino12_c",
        "tsm_nino34_c","anomalia_tsm_nino34_c",
        "region_cuadrante_no_punto","vintage_historica_verificada")

def csvout(rows):
    buf=io.StringIO(newline="")
    w=csv.DictWriter(buf,fieldnames=FIELDS,lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()

def original_sst(root):
    from gzip import decompress
    file,metadata=cpc.paths(root)
    if not file.exists() or not metadata.exists():
        raise ValueError("Falta índice original NOAA fase 8T")
    cpc.archive(root)  # SHA, URL and completeness
    raw=decompress(file.read_bytes()).decode("utf-8-sig")
    lines=[x.strip().split() for x in raw.splitlines()[1:] if x.strip()]
    bydate={}
    for a in lines:
        key=f"{int(a[0]):04d}-{int(a[1]):02d}"
        if key in bydate:raise ValueError("NOAA SST mes duplicado")
        bydate[key]=(float(a[2]),float(a[3]),float(a[8]),float(a[9]))
    dates=[f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)]
    if any(x not in bydate for x in dates):raise ValueError("NOAA 8U SST incompleta")
    out=[]
    for month in dates:
        sst,anom,other,otheranom=bydate[month]
        if not all(math.isfinite(v) for v in (sst,anom,other,otheranom)):
            raise ValueError("NOAA contiene valores no finitos")
        out.append({
          "mes":month,"tsm_nino12_c":sst,
          "anomalia_tsm_nino12_c":anom,
          "tsm_nino34_c":other,"anomalia_tsm_nino34_c":otheranom,
          "region_cuadrante_no_punto":"true",
          "vintage_historica_verificada":"false"
        })
    return out

def assemble(root):
    ocean=original_sst(root)
    dirs=[
      {"nombre":"NOAA CPC Niño 1+2 (TSM histórica)",
       "variable":"temperatura_superficial_mar_C / anomalía_C",
       "estado":"360_meses_verificados_SHA_y_cubierta_region_amplia",
       "cobertura":"1996–2025","zona":"Pacífico oriental Niño1+2; no Pimentel/Santa Rosa",
       "fuente":cpc.URL,
       "prediccion_prospectiva":False},
      {"nombre":"Viento atmosférico 10 m",
       "variable":"velocidad/dirección (no velocidad de corriente)",
       "estado":"consultar estado_viento_8u.json","fuente":"ERA5 Open-Meteo Historical Archive",
       "prediccion_prospectiva":False},
      {"nombre":"OSCAR versión 2 NASA/PO.DAAC",
       "variable":"corriente superficial u,v (m/s), capa mezclada ~30 m",
       "estado":"fuente_confirmada_acceso_y_descarga_granulos_pendientes",
       "fuente":"https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0",
       "distribucion":"NetCDF-4; acceso sujeto a servicios y credenciales Earthdata",
       "cobertura_catalogo":"1993–2026; cobertura local 1996–2025 NO verificada",
       "observacion_local_verificada":False,
       "prediccion_prospectiva":False},
      {"nombre":"Copernicus Marine Global Ocean Physics Reanalysis",
       "variable":"corriente este/norte y temperatura marina por nivel",
       "estado":"producto_elegible_acceso_y_subconjunto_pendiente",
       "fuente":"https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description",
       "observacion_local_verificada":False,
       "prediccion_prospectiva":False},
      {"nombre":"NOAA CoastWatch OSCAR histórico antiguo jplOscar",
       "estado":"DESCARTADO_serie_ERDDAP_real_2011_2014_no_30_anos",
       "fuente":"https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplOscar.html",
       "observacion_local_verificada":False}
    ]
    r={
      "fase":"8U","estado":"tsm_nino12_recuperada_viento_y_corrientes_en_integracion",
      "meses_tsm_historia":len(ocean),
      "periodo_tsm":"1996–2025",
      "fuente_tsm":"NOAA CPC SSTOI indices archivada por fase 8T",
      "sha256_fuente_original":json.loads((root/cpc.META).read_text(encoding="utf-8"))["sha256_original"],
      "tsm_costa_lambayeque_medido":False,
      "tsm_nino12_es_region_no_punto":True,
      "indice_serie_oceanica_vintage_realtime":False,
      "n_series_corriente_marina_1996_2025_descargadas_y_validadas":0,
      "NO_confundir_corriente_marina_con_viento":True,
      "catalogo_fuentes":dirs,
      "series_corrientes_pendientes":True,
      "zonas_agrícolas_homogeneas_certificadas":0,
      "validacion_senamhi_o_imarpe_real":False,
      "habilidad_predictiva_meteorologica_8u_demostrada":False,
      "advertencia":"TSM es Niño1+2, no sensor frente a Lambayeque; corrientes requerirán vectores u/v genuinos de agua de mar para el mismo periodo, no vectores ERA5 de viento."
    }
    return r,ocean

def publish(root,check=False):
    r,rows=assemble(root)
    folder=root/OUT
    data={
      folder/"estado_oceanografia_8u.json":json.dumps(r,ensure_ascii=False,indent=2)+"\n",
      folder/"tsm_nino12_mensual_8u.csv":csvout(rows)
    }
    if not check:folder.mkdir(parents=True,exist_ok=True)
    for path,content in data.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=content:
                raise ValueError("8U oceanografía no reproduce NOAA original")
        elif not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
    print(json.dumps({"fase":"8U","tsm_meses":len(rows),"corrientes_1996_2025":0,"check":check}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    publish(args.root,args.check)
