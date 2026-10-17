#!/usr/bin/env python3
"""OAF fase 8Z: formulas oficiales NASA MERRA-2 + prueba CMR de metadatos.
No atribuir PM2.5/PM10 a estaciones ni marcar serie descargada hasta leer NetCDF.
PM2.5: colección M2T1NXAER (superficie, kg/m3).
PM10: M2I3NVAER (mezcla kg/kg) nivel 72 + AIRDENS kg/m3, NO M2T1NXAER.
La colección mensual M2TMNXAER PM2.5 requiere mismos campos y control temporal;
PM10 no puede extraerse de PM2.5 con multiplicador arbitrario.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

NASA_FAQ='https://gmao.gsfc.nasa.gov/gmao-products/merra-2/faq_merra-2/'
NASA_CMR='https://cmr.earthdata.nasa.gov/search/granules.json'
COLLECTION_AER='M2T1NXAER'
COLLECTION_3D='M2I3NVAER'
OUT=Path('datos/merra2_8z/estado_piloto_merra2_8z.json')
CONV=1e9
SULFATE_25=132.14/96.06
SULFATE_10=1.375

def require(data,names):
    out={}
    for k in names:
        try:v=float(data[k])
        except (KeyError,TypeError,ValueError):raise ValueError('Falta componente NASA: '+k) from None
        if not math.isfinite(v) or v<0 or v>10:
            raise ValueError('Componente NASA inválido: '+k)
        out[k]=v
    return out

def pm25_surface_ug_m3(data):
    """NASA MERRA-2 PM2.5 seco, fórmula oficial GMAO, NO ajuste higroscópico."""
    x=require(data,('DUSMASS25','OCSMASS','BCSMASS','SSSMASS25','SO4SMASS'))
    return (x['DUSMASS25']+x['OCSMASS']+x['BCSMASS']+
            x['SSSMASS25']+SULFATE_25*x['SO4SMASS'])*CONV

def pm10_lowest_layer_ug_m3(data):
    """NASA MERRA-2 PM10: capa inferior 72 en 3D, mezcla por densidad aire."""
    names=('SO4','BCphobic','BCphilic','OCphobic','OCphilic',
           'DU001','DU002','DU003','DU004',
           'SS001','SS002','SS003','SS004','AIRDENS')
    x=require(data,names)
    if x['AIRDENS']<=0:raise ValueError('AIRDENS debe ser positiva')
    species=(SULFATE_10*x['SO4']+x['BCphobic']+x['BCphilic']+
             x['OCphobic']+x['OCphilic']+x['DU001']+x['DU002']+
             x['DU003']+.74*x['DU004']+x['SS001']+x['SS002']+
             x['SS003']+x['SS004'])
    return species*x['AIRDENS']*CONV

def cmr_query(collection,day):
    return NASA_CMR+'?'+urlencode({
      'short_name':collection,'version':'5.12.4',
      'temporal':f'{day}T00:00:00Z,{day}T23:59:59Z',
      'page_size':'2'})

def check_cmr_collection(collection,day):
    url=cmr_query(collection,day)
    with urlopen(Request(url,headers={'User-Agent':'OAF-Lambayeque-MERRA2-research/1.0'}),
                 timeout=45) as r:
        raw=r.read(500_001)
        if len(raw)>500_000:raise ValueError('CMR response too large')
    record=json.loads(raw)
    entries=record.get('feed',{}).get('entry',[])
    if not isinstance(entries,list):raise ValueError('NASA CMR incompatible')
    out=[]
    for e in entries:
        links=e.get('links') or []
        out.append({'id':e.get('id'),'title':e.get('title'),
                    'start_time':e.get('time_start'),
                    'data_links':[a.get('href') for a in links
                     if a.get('href','').startswith('https://') and not a.get('inherited')]
                    [:4]})
    return {'consulta_url':url,'entries':out,'n_granulos_muestra':len(out),
            'sha256_respuesta':hashlib.sha256(raw).hexdigest()}

def main(root='.',fetch_metadata=False):
    root=Path(root)
    path=root/OUT
    prior={}
    if path.exists():prior=json.loads(path.read_text(encoding='utf-8'))
    evidence=prior.get('catalogo_metadatos_nasa',{})
    problems=[]
    if fetch_metadata:
        for collection in (COLLECTION_AER,COLLECTION_3D):
            for day in ('1998-03-15','2025-07-15'):
                key=collection+'_'+day
                try:
                    evidence[key]=check_cmr_collection(collection,day)
                except Exception as exc:
                    # No false claims of granule availability.
                    problems.append({'key':key,'error':str(exc)[:350]})
    report={
      'fase':'8Z','coleccion_nasa_aerosol_superficie':COLLECTION_AER,
      'coleccion_nasa_pm10_3d':COLLECTION_3D,'faq_nasa':NASA_FAQ,
      'malla_grados':{'lat':0.5,'lon':0.625},
      'marco_climatico':'1996-2025', 'unidad_componentes_25':'kg/m3',
      'unidad_componentes_10':'kg/kg con AIRDENS kg/m3',
      'unidad_resultado':'µg/m3',
      'conversion_kg_m3_a_ug_m3':CONV,
      'pm25_seco_sin_agua_higroscopica':True,
      'capa_pm10_3d_numero':72,
      'no_usar_pm25_para_estimar_pm10':True,
      'colecciones_1996_2025_descargadas_en_oaf':False,
      'serie_merra2_pm_mensual_archivada':False,
      'metadatos_CMR_no_equivalen_a_valores_PM':True,
      'catalogo_metadatos_nasa':evidence,'errores_consulta_CMR':problems,
      'limitaciones':[
        'PM10 exige variables de mezcla inst3_3d_aer_Nv nivel 72 y densidad del aire',
        'PM2.5 seco calculado según FAQ NASA sin crecimiento higroscópico',
        'Sin descarga de NetCDF NASA no declarar promedios PM ni tendencias',
        'NASA Earthdata puede exigir autenticación para descargar datos y subsetting',
        'La validación SENAMHI de contaminantes sigue pendiente',
        'Centro de celda MERRA-2 distinto de parcela y pisos topográficos']
    }
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--fetch-metadata',action='store_true')
    a=p.parse_args()
    s=main(a.root,a.fetch_metadata)
    print(json.dumps({'fase':s['fase'],'colecciones':[
        s['coleccion_nasa_aerosol_superficie'],s['coleccion_nasa_pm10_3d']],
        'consultas':len(s['catalogo_metadatos_nasa']),
        'errores':s['errores_consulta_CMR'],
        'series_PM_archivadas':s['serie_merra2_pm_mensual_archivada']},
        ensure_ascii=False,indent=2))
