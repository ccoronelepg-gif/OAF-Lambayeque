"""OAF fase 3P: audita seleccion espacial y modelos historicos de Open-Meteo.
Coordenadas de estaciones preliminares; valores solo exploratorios.
"""
import calendar
import json
import math
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'datos'
DATA.mkdir(exist_ok=True, parents=True)
STATIONS = {
    'Jayanca (La Viña)': (-6.322, -79.779),
    'Cayaltí': (-6.88079444, -79.54701389),
    'Reque': (-6.88613, -79.8355),
    'Lambayeque': (-6.73152778, -79.90983611),
    'Cueva Blanca': (-6.13130, -79.40450),
}
MODELS = ('era5_seamless', 'era5', 'era5_land')
CASES = ((1998, 'nearest'), (1998, 'land'), (2000, 'nearest'))
URL = 'https://archive-api.open-meteo.com/v1/archive'
session = requests.Session()
session.headers.update({'User-Agent': 'OAF-Lambayeque/0.6 scientific-audit'})


def distance_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    a, b = math.radians(lat1), math.radians(lat2)
    q = math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin(math.radians(lon2-lon1)/2)**2
    return r*2*math.asin(min(1, math.sqrt(q)))


def download(lat, lon, model, year, cell_selection):
    params = {'latitude':lat, 'longitude':lon, 'daily':'precipitation_sum',
              'start_date':f'{year}-01-01', 'end_date':f'{year}-12-31',
              'timezone':'America/Lima', 'models':model,
              'cell_selection':cell_selection}
    error = None
    for attempt in range(3):
        try:
            res = session.get(URL, params=params, timeout=(15,75))
            res.raise_for_status()
            obj = res.json()
            if obj.get('error'):
                raise ValueError(obj.get('reason','Error API'))
            daily = obj['daily']
            if obj.get('daily_units',{}).get('precipitation_sum')!='mm':
                raise ValueError('Unidad API distinta de mm')
            dates = pd.to_datetime(daily['time'])
            rain = pd.to_numeric(pd.Series(daily['precipitation_sum']),errors='coerce')
            n = 366 if calendar.isleap(year) else 365
            calendar_days = pd.date_range(f'{year}-01-01',f'{year}-12-31',freq='D')
            if len(dates)!=n or len(rain)!=n or list(dates)!=list(calendar_days):
                raise ValueError('Serie diaria incompleta, desordenada o duplicada')
            if rain.isna().any() or (rain<0).any():
                raise ValueError('Precipitacion negativa o ausente en un dia')
            monthly = pd.DataFrame({'mes':dates.strftime('%Y-%m'),'estimado_mm':rain}).groupby('mes',as_index=False).sum()
            return obj, monthly
        except (requests.RequestException,TypeError,KeyError,ValueError) as exc:
            error=exc
            if attempt<2:
                print('REINTENTO',model,year,cell_selection,type(exc).__name__,flush=True)
                time.sleep(5*(attempt+1))
    raise RuntimeError(str(error)[:250])


def main():
    obs = pd.read_csv(DATA/'senamhi_mensual_completo_1996_2015.csv')
    obs['ano'] = obs['mes'].str[:4].astype(int)
    annual, monthly, errors = [], [], []
    for station,(lat,lon) in STATIONS.items():
        for year, selection in CASES:
            o=obs.loc[(obs.estacion==station)&(obs.ano==year)]
            o=o.loc[o.dias_validos==o.dias_mes]
            if len(o)!=12 or o.mes.nunique()!=12:
                errors.append({'estacion':station,'ano':year,'seleccion':selection,'modelo':'TODOS', 'error':'No hay 12 meses observados validos'})
                continue
            for model in MODELS:
                try:
                    reply, est = download(lat, lon, model, year, selection)
                    joined = o[['mes','observado_mm']].merge(est,on='mes',validate='one_to_one')
                    if len(joined)!=12:
                        raise ValueError('Menos de 12 meses coincidentes')
                    diff = joined.estimado_mm - joined.observado_mm
                    glat,glon = float(reply['latitude']),float(reply['longitude'])
                    row={'estacion':station,'ano':year,'seleccion':selection,'modelo':model,
                         'lat_solicitada':lat,'lon_solicitada':lon,'lat_celda':glat,'lon_celda':glon,
                         'distancia_celda_km':round(distance_km(lat,lon,glat,glon),3),
                         'altitud_celda_m':reply.get('elevation'),
                         'obs_anual_mm':round(float(joined.observado_mm.sum()),3),
                         'estimado_anual_mm':round(float(joined.estimado_mm.sum()),3),
                         'sesgo_anual_mm':round(float(diff.sum()),3),
                         'sesgo_anual_pct':round(float(100*diff.sum()/joined.observado_mm.sum()),2) if joined.observado_mm.sum()>0 else None,
                         'mae_mensual_mm':round(float(diff.abs().mean()),3),
                         'rmse_mensual_mm':round(float((diff.pow(2).mean())**0.5),3),
                         'meses':12}
                    annual.append(row)
                    joined['estacion']=station;joined['ano']=year
                    joined['modelo']=model;joined['seleccion']=selection
                    joined['diferencia_mm']=diff.round(3)
                    monthly.append(joined)
                    print('OK',station,year,selection,model,'mm=',row['estimado_anual_mm'],'celda=',glat,glon,flush=True)
                except Exception as exc:
                    errors.append({'estacion':station,'ano':year,'seleccion':selection,'modelo':model,'error':f'{type(exc).__name__}: {str(exc)[:200]}'})
                    print('ERROR',station,year,selection,model,str(exc)[:120],flush=True)
                time.sleep(0.5)
    pd.DataFrame(annual,columns=['estacion','ano','seleccion','modelo','lat_solicitada','lon_solicitada','lat_celda','lon_celda',
       'distancia_celda_km','altitud_celda_m','obs_anual_mm','estimado_anual_mm','sesgo_anual_mm','sesgo_anual_pct',
       'mae_mensual_mm','rmse_mensual_mm','meses']).to_csv(DATA/'auditoria_3p_celdas_modelos.csv',index=False)
    if monthly:
        pd.concat(monthly,ignore_index=True).to_csv(DATA/'auditoria_3p_mensual.csv',index=False)
    else:
        (DATA/'auditoria_3p_mensual.csv').write_text('mes,observado_mm,estimado_mm,estacion,ano,modelo,seleccion,diferencia_mm\n',encoding='utf-8')
    state={'fase':'3P','periodos':[1998,2000], 'esperados':45,'obtenidos':len(annual),'incidencias':errors,
        'coordenadas_estaciones_preliminares':True,'no_validacion_independiente':True}
    (DATA/'estado_3p.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# OAF-Lambayeque: Fase 3P — Auditoría espacial y modelos ERA5','',
        '> **Exploratorio**: los metadatos geográficos de las estaciones son provisionales.',
        '> No declarar este contraste como calibración operativa ni validación general 1996–2025.', '',
        '## Diseño','',
        'Se consultaron por separado ERA5-Seamless, ERA5 y ERA5-Land en el API de Open-Meteo.',
        'Los criterios `nearest` y `land` se prueban en 1998; en 2000 se usa `nearest`.',
        'Se muestran las coordenadas efectivamente devueltas por el API y su distancia al punto solicitado.',
        'La distancia espacial NO demuestra por sí misma la causa de los sesgos.','',
        f'**Consultas completas: {len(annual)} / 45; incidencias: {len(errors)}.**','',
        '## Acumulados y distancias','',
        '| Estación | Año | Celda | Modelo | Observado (mm) | Estimado (mm) | Sesgo (%) | Distancia (km) |',
        '|---|---:|---|---|---:|---:|---:|---:|']
    for row in annual:
        lines.append(f"| {row['estacion']} | {row['ano']} | {row['seleccion']} | {row['modelo']} | {row['obs_anual_mm']} | {row['estimado_anual_mm']} | {row['sesgo_anual_pct']} | {row['distancia_celda_km']} |")
    if errors:
        lines+=['','## Incidencias de consulta','']
        lines.extend('- '+str(z) for z in errors)
    lines+=['','## Interpretacion y fuentes','',
            '- Los modelos representan resoluciones y superficies de grid distintas; 1998 es un año extremo y no debe usarse aisladamente.',
            '- Open-Meteo: https://open-meteo.com/en/docs/historical-weather-api',
            '- CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3 (producto futuro, NO calculado aún).',
            '- PISCOp v3: https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru',
            '- SENAMHI: datos históricos de estaciones suministrados por el usuario.',
            '']
    (ROOT/'AUDITORIA_3P.md').write_text('\n'.join(lines),encoding='utf-8')
    print('COMPLETADO',len(annual),'de 45; fallos',len(errors),flush=True)
    if not annual:
        raise SystemExit(1)

if __name__=='__main__':
    main()