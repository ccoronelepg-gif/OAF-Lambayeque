"""Diagnóstico puntual de disponibilidad de precipitación ERA5-Land en Open-Meteo.
No es prueba de climatología ni permite rellenar datos ausentes.
"""
import json
import time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'datos'
OUT.mkdir(exist_ok=True,parents=True)
API='https://archive-api.open-meteo.com/v1/archive'
STATIONS={'Jayanca (La Viña)':(-6.322,-79.779),'Cueva Blanca':(-6.1313,-79.4045)}
MODELS=('era5_land','era5','era5_seamless')
rows=[]
for station,(lat,lon) in STATIONS.items():
    for model in MODELS:
        rec={'estacion':station,'modelo':model,'inicio':'1998-02-01','fin':'1998-02-10'}
        try:
            response=requests.get(API,params={'latitude':lat,'longitude':lon,
                 'start_date':'1998-02-01','end_date':'1998-02-10',
                 'daily':'precipitation_sum','hourly':'precipitation',
                 'models':model,'timezone':'America/Lima','cell_selection':'nearest'},
                 timeout=100)
            response.raise_for_status()
            data=response.json()
            if data.get('error'):
                raise ValueError(data.get('reason','Respuesta con error'))
            rec['lat_celda']=data.get('latitude')
            rec['lon_celda']=data.get('longitude')
            for kind,var in [('daily','precipitation_sum'),('hourly','precipitation')]:
                vals=data.get(kind,{}).get(var,[])
                rec[kind+'_n_total']=len(vals)
                rec[kind+'_n_nulos']=sum(x is None for x in vals)
                rec[kind+'_n_negativos']=sum(isinstance(x,(float,int)) and x<0 for x in vals)
                rec[kind+'_n_cero']=sum(x==0 for x in vals if x is not None)
                rec[kind+'_muestra']=vals[:6]
            rec['estado']='OK'
        except Exception as e:
            rec['estado']='SIN_RESULTADO'
            rec['error']=f'{type(e).__name__}: {str(e)[:240]}'
        rows.append(rec)
        print(station,model,rec['estado'],rec.get('daily_n_nulos'),rec.get('hourly_n_nulos'),flush=True)
        time.sleep(1)
(OUT/'diagnostico_era5_land_3p.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Diagnóstico complementario de ERA5-Land, fase 3P','',
 'Prueba puntual de 10 días (1–10 de febrero de 1998), estaciones Jayanca y Cueva Blanca.',
 'Se contrastó disponibilidad de precipitación diaria y horaria en Open-Meteo, no exactitud climática.','',
 '| Estación | Modelo | Estado | Nulos diarios/total | Nulos horarios/total |','|---|---|---|---:|---:|']
for x in rows:
    n=lambda kind:str(x.get(kind+'_n_nulos','—'))+'/'+str(x.get(kind+'_n_total','—'))
    lines.append('| '+x['estacion']+' | '+x['modelo']+' | '+x['estado']+' | '+n('daily')+' | '+n('hourly')+' |')
lines+=['','Si hay valores nulos o negativos, NO se deben interpretar como 0 mm. Si la serie de ERA5-Land no es aprovechable, su limitación debe consignarse y consultar fuentes oficiales alternativas.',
'','Documentación API: https://open-meteo.com/en/docs/historical-weather-api']
(ROOT/'DIAGNOSTICO_ERA5_LAND_3P.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
