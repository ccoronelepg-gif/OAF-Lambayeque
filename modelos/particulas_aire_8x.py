#!/usr/bin/env python3
"""Fase 8X. Particulas atmosfericas CAMS Global via Open-Meteo.
NO son sensores SENAMHI, ni base 1996-2025, ni evaluacion normativa ECA.
Sin datos válidos: estado explicito; nunca generar series sinteticas.
"""
import argparse
import calendar
import csv
import gzip
import hashlib
import io
import json
import math
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT=Path('datos/aire_8x')
SITES={
    'Chiclayo':(-6.77140,-79.84090),
    'Jayanca':(-6.39278,-79.82280),
    'Motupe':(-6.15083,-79.71420),
    'Olmos':(-5.98825,-79.74723),
}
BASE='https://air-quality-api.open-meteo.com/v1/air-quality'
EXPECTED_UNIT={'pm2_5':'μg/m³','pm10':'μg/m³'}
REQUIRED=['pm2_5','pm10']
MIN_VALID_RATIO=.80
USER_AGENT='OAF-Lambayeque-8X-science/1.0 (non-operational)'

def month_days(year,month):
    return calendar.monthrange(year,month)[1]

def build_url(site,year):
    lat,lon=SITES[site]
    return BASE+'?'+urlencode(dict(latitude=lat,longitude=lon,
       start_date=f'{year}-01-01',end_date=f'{year}-12-31',
       hourly=','.join(REQUIRED),domains='cams_global',timezone='UTC'))

def safe_numeric(value,key):
    if value is None: return None
    if not isinstance(value,(float,int)) or not math.isfinite(value):
        raise ValueError(f'{key}: invalid or non-finite')
    if value<0 or value>10000:
        raise ValueError(f'{key}: out of physical review range')
    return float(value)

def response_to_months(response,site,year):
    if response.get('error'):raise ValueError(str(response.get('reason','API error')))
    if response.get('timezone') not in ('GMT','UTC'):
        raise ValueError('Timezone non-UTC. Datos no comparables.')
    units=response.get('hourly_units',{})
    for key in REQUIRED:
        if units.get(key) not in ('μg/m³','µg/m³','ug/m3'):
            raise ValueError(f'Unidad inválida {key}: {units.get(key)}')
    hourly=response.get('hourly',{})
    times=hourly.get('time')
    if not isinstance(times,list) or not times:raise ValueError('Sin tiempos horarios')
    for key in REQUIRED:
        if not isinstance(hourly.get(key),list) or len(hourly[key])!=len(times):
            raise ValueError('PM no existe o longitud inconsistente')
    dt=[]
    for value in times:
        try:parsed=datetime.fromisoformat(value)
        except Exception:raise ValueError('Fecha inválida') from None
        if parsed.tzinfo is not None:
            parsed=parsed.astimezone(timezone.utc).replace(tzinfo=None)
        dt.append(parsed)
    if len(dt)!=len(set(dt)) or dt!=sorted(dt):
        raise ValueError('Fechas duplicadas o desordenadas')
    steps={(b-a).total_seconds()//3600 for a,b in zip(dt,dt[1:])}
    if steps not in ({1}, {3}):
        raise ValueError('Intervalo esperado 1h o 3h, datos escalonados o con huecos')
    step=1 if steps=={1} else 3
    first=datetime(year,1,1); last=datetime(year+1,1,1)-timedelta(hours=step)
    if dt[0]!=first or dt[-1]!=last:
        raise ValueError('Cobertura anual incompleta, no declarar año completo')
    by_month={}
    for m in range(1,13):
        inds=[i for i,t in enumerate(dt) if t.month==m]
        count_expected=month_days(year,m)*24//step
        if len(inds)!=count_expected:raise ValueError('Faltan marcas temporales del mes')
        row={'mes':f'{year}-{m:02d}','localidad':site,
             'fuente':'Open-Meteo CAMS Global modelado, NO estación',
             'modelado_no_instrumental':True,
             'resolucion_horas':step,'marcas_temporales_esperadas':count_expected}
        usable=True
        for col,name in [('pm2_5','pm25'),('pm10','pm10')]:
            nums=[safe_numeric(hourly[col][i],col) for i in inds]
            valid=[v for v in nums if v is not None]
            coverage=len(valid)/count_expected
            row['n_'+name+'_validas']=len(valid)
            row['cobertura_'+name+'_pct']=round(100*coverage,2)
            row[name+'_media_ug_m3']=round(sum(valid)/len(valid),4) if coverage>=MIN_VALID_RATIO else ''
            if coverage<MIN_VALID_RATIO:usable=False
        row['mes_pm_completo_80pct']=usable
        by_month[m]=row
    return [by_month[m] for m in range(1,13)],step

def read_original(path):
    with gzip.open(path,'rb') as f:return f.read()

def sha256(x):return hashlib.sha256(x).hexdigest()

def request(url):
    last=None
    for attempt in range(2):
        try:
            with urlopen(Request(url,headers={'User-Agent':USER_AGENT}),timeout=115) as r:
                body=r.read(6_000_000)
                if len(body)==6_000_000:raise ValueError('Respuesta mayor a 6 MB')
                return body
        except (OSError,ValueError) as ex:
            last=ex
            if attempt==0:time.sleep(8)
    raise RuntimeError(f'Descarga denegada/no disponible: {type(last).__name__}: {last}')

def write_csv(rows):
    out=io.StringIO(newline='')
    w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
    return out.getvalue().encode('utf-8')

def execute(root='.',fetch=False,year=2025,site=None,check=False):
    if not 2023<=year<=2025:raise ValueError('Piloto restringido a 2023-2025')
    root=Path(root);d=root/ROOT;sources=d/'fuentes'
    if fetch:
        sources.mkdir(parents=True,exist_ok=True)
        # Cada ejecución añade como máximo un sitio-año: respeta cuota y trazabilidad.
        targets=[site] if site else list(SITES)
        for sit in targets:
            dest=sources/f'cams_global_{sit}_{year}.json.gz'
            if dest.exists():continue
            url=build_url(sit,year)
            raw=request(url)
            obj=json.loads(raw)
            rows,step=response_to_months(obj,sit,year)
            with dest.open('wb') as fout:
                with gzip.GzipFile(fileobj=fout,mode='wb',mtime=0) as f:
                    f.write(raw)
            meta=dict(sitio=sit,year=year,modelo='CAMS Global forecast archive via Open-Meteo',
                      url=url,sha256_original=sha256(raw),timezone='UTC',
                      unidad='ug/m3',paso_horas=step,meses=12,
                      recuperado_utc=datetime.now(timezone.utc).isoformat(),
                      estacion_instrumental=False)
            (sources/f'cams_global_{sit}_{year}.meta.json').write_text(
                json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            break
    records=[];issues=[];years=set();source_hashes=[]
    for p in sorted(sources.glob('cams_global_*.json.gz')) if sources.exists() else []:
        try:
            stem=p.name.removeprefix('cams_global_').removesuffix('.json.gz')
            sit,yr=stem.rsplit('_',1)
            if sit not in SITES:raise ValueError('Ubicación fuera del inventario')
            yr=int(yr)
            raw=read_original(p)
            meta_path=p.with_suffix('').with_suffix('.meta.json')
            meta=json.loads(meta_path.read_text(encoding='utf-8'))
            if meta['sha256_original']!=sha256(raw):raise ValueError('SHA de fuente distinto')
            rows,step=response_to_months(json.loads(raw),sit,yr)
            records+=rows;years.add(yr)
            source_hashes.append(dict(file=str(p.relative_to(root)),sha256=sha256(raw),
                                      modelo=meta['modelo'],sitio=sit,year=yr))
        except (ValueError,KeyError,TypeError,FileNotFoundError) as exc:
            issues.append({'file':p.name,'error':str(exc)})
    if len({(x['mes'],x['localidad']) for x in records})!=len(records):
        raise ValueError('Mes/sitio duplicado entre fuentes')
    records.sort(key=lambda x:(x['localidad'],x['mes']))
    result_csv=write_csv(records) if records else None
    valid=sum(bool(x['mes_pm_completo_80pct']) for x in records)
    status={
        'fase':'8X','variable_nueva':'material_particulado_PM2.5_PM10',
        'fuente':'CAMS Global via Open-Meteo air quality API',
        'tipo':'modelo_atmosferico_no_medicion_instrumental',
        'periodo_piloto_predefinido':'2023-2025',
        'serie_pm_1996_2025_completa':False,
        'estaciones_pm_lambayeque_validadas':0,
        'sitios_referencia':list(SITES),
        'filas_mes_sitio':len(records),'meses_pm_80pct_aptos':valid,
        'registros_faltantes_no_imputados':True,
        'comparacion_legal_ECA_habilitada':False,
        'pronostico_pm_agricola_validado':False,
        'alerta_sanitaria_o_fitosanitaria_habilitada':False,
        'uso_modelo_anomalias_1996_2025':False,
        'fuentes_sha256':source_hashes,
        'errores_fuente':issues,
        'csv_publicado':bool(records),
        'pendientes':[
            'SENAMHI/MINAM/OEFA estaciones reales y cobertura Lambayeque',
            'CAMS EAC4 global 2003-2025 o MERRA-2, otras coberturas NO supuestas',
            'Validación independiente de PM2.5 y PM10; topografía, polvo carreteras, incendios',
            'Atribución causal e impactos agrícolas requieren diseño y medición específicos',
        ],
    }
    if not check:
        d.mkdir(parents=True,exist_ok=True)
        if result_csv:(d/'particulas_mensuales_8x.csv').write_bytes(result_csv)
        (d/'estado_aire_8x.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',
                                           encoding='utf-8')
    else:
        if result_csv and (d/'particulas_mensuales_8x.csv').read_bytes()!=result_csv:
            raise AssertionError('CSV no reproducible')
        if json.loads((d/'estado_aire_8x.json').read_text(encoding='utf-8'))!=status:
            raise AssertionError('Estado no reproducible')
    return status

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--fetch',action='store_true')
    p.add_argument('--year',type=int,default=2025)
    p.add_argument('--site',choices=list(SITES))
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    print(json.dumps(execute(a.root,a.fetch,a.year,a.site,a.check),ensure_ascii=False,indent=2))
