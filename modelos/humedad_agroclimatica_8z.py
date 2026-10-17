#!/usr/bin/env python3
"""Fase 8Z: RH media diaria ERA5 y VPD máximo diario (archivo Open-Meteo).
Descarga únicamente 1996–2025; NO observación de estación ni humedad del dosel.
Cada localidad tiene coordenadas de celda efectivas y fuente original comprimida.
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
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SITES={
 'Chiclayo':(-6.77140,-79.84090),
 'Jayanca':(-6.39278,-79.82280),
 'Motupe':(-6.15083,-79.71420),
 'Olmos':(-5.98825,-79.74723)
}
BASE='https://archive-api.open-meteo.com/v1/archive'
FIELDS=('relative_humidity_2m_mean','vapour_pressure_deficit_max')
OUT=Path('datos/humedad_8z')
START=date(1996,1,1); END=date(2025,12,31)

def build_url(site):
    lat,lon=SITES[site]
    return BASE+'?'+urlencode({'latitude':lat,'longitude':lon,
        'daily':','.join(FIELDS),'start_date':START.isoformat(),
        'end_date':END.isoformat(),'timezone':'America/Lima',
        'models':'era5'})

def sha(b):return hashlib.sha256(b).hexdigest()

def get(url):
    last=None
    for n in range(2):
        try:
            with urlopen(Request(url,headers={'User-Agent':'OAF-8Z-agroclima-reanalysis/1.0'}),
                         timeout=125) as f:
                data=f.read(5_000_001)
                if len(data)>5_000_000:raise ValueError('Respuesta superior a 5 MB')
                return data
        except (OSError,ValueError) as exc:
            last=exc
            if n==0:time.sleep(10)
    raise RuntimeError('ERA5 no disponible: '+str(last))

def finite(value,key):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value):
        raise ValueError('Número no finito o ausente '+key)
    return float(value)

def aggregate(raw,site):
    d=json.loads(raw)
    if d.get('error'):raise ValueError('Error proveedor: '+str(d.get('reason')))
    if d.get('timezone')!='America/Lima':
        raise ValueError('Husos horarios inconsistentes')
    try:
        lat=finite(d['latitude'],'lat');lon=finite(d['longitude'],'lon')
    except KeyError as e:raise ValueError('Sin geolocalización real') from e
    ref_lat,ref_lon=SITES[site]
    if abs(lat-ref_lat)>0.75 or abs(lon-ref_lon)>0.75:raise ValueError('Celda fuera de referencia')
    unit=d.get('daily_units',{})
    if unit.get('relative_humidity_2m_mean')!='%':
        raise ValueError('Unidad de RH debe ser %')
    if unit.get('vapour_pressure_deficit_max')!='kPa':
        raise ValueError('Unidad VPD debe ser kPa')
    daily=d.get('daily',{})
    timestamps=daily.get('time')
    if not isinstance(timestamps,list):raise ValueError('Sin calendario')
    for var in FIELDS:
        if not isinstance(daily.get(var),list) or len(daily[var])!=len(timestamps):
            raise ValueError('Campo ausente o longitud inconsistente '+var)
    dates=[]
    for stamp in timestamps:
        dt=date.fromisoformat(stamp)
        dates.append(dt)
    if dates!=sorted(set(dates)):raise ValueError('Fechas duplicadas o desordenadas')
    expected=(END-START).days+1
    if len(dates)!=expected or dates[0]!=START or dates[-1]!=END or any(
        b-a!=timedelta(days=1) for a,b in zip(dates,dates[1:])):
        raise ValueError('Calendario 1996–2025 incompleto')
    grouped=defaultdict(list)
    for i,day in enumerate(dates):
        rh=finite(daily[FIELDS[0]][i],FIELDS[0])
        vpd=finite(daily[FIELDS[1]][i],FIELDS[1])
        if not 0<=rh<=100 or not 0<=vpd<=15:raise ValueError('Fuera de rangos RH/VPD')
        grouped[day.strftime('%Y-%m')].append((rh,vpd))
    result=[]
    for mon,values in sorted(grouped.items()):
        yr,mo=map(int,mon.split('-'))
        nd=calendar.monthrange(yr,mo)[1]
        if len(values)!=nd:raise ValueError('No cobertura diaria mes '+mon)
        result.append({
         'mes':mon,'localidad':site,
         'rh_2m_media_pct':round(sum(z[0] for z in values)/nd,5),
         'vpd_max_diario_media_mes_kpa':round(sum(z[1] for z in values)/nd,5),
         'vpd_max_diario_max_mes_kpa':round(max(z[1] for z in values),5),
         'dias_validos':nd,'celda_era5_lat':lat,'celda_era5_lon':lon,
         'fuente':'ERA5 via Open-Meteo (reanálisis NO estación)',
         'no_es_humedad_del_dosel':True
        })
    if len(result)!=360:raise ValueError('No 360 meses')
    return result

def csv_payload(rows):
    mem=io.StringIO(newline='')
    writer=csv.DictWriter(mem,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return mem.getvalue().encode('utf-8')

def run(root='.',fetch=False,only=None,check=False):
    root=Path(root);dst=root/OUT;src=dst/'fuentes'
    if fetch:
        src.mkdir(parents=True,exist_ok=True)
        targets=[only] if only else list(SITES)
        # Archive only ORIGINALS during fetch. Derived files rebuilt separately on synced main.
        for site in targets:
            path=src/f'era5_humedad_{site}_1996_2025.json.gz'
            meta=src/f'era5_humedad_{site}_1996_2025.meta.json'
            if path.exists() and meta.exists():continue
            url=build_url(site);payload=get(url)
            validated=aggregate(payload,site)
            with path.open('wb') as rawout:
                with gzip.GzipFile(fileobj=rawout,mode='wb',mtime=0) as writer:writer.write(payload)
            meta.write_text(json.dumps({'localidad':site,'url':url,
                 'modelo':'ERA5','hash_sha256_original':sha(payload),
                 'timestamp_descarga_utc':datetime.now(timezone.utc).isoformat(),
                 'intervalo':'1996-01-01/2025-12-31','registros_mensuales':len(validated),
                 'fuente_modelada':True,'observacion_instrumental':False,
                 'unidades':'RH %, VPD kPa'},ensure_ascii=False,indent=2)+'\n',
                 encoding='utf-8')
            time.sleep(2)
    rows=[];issues=[];sources=[]
    for site in SITES:
        path=src/f'era5_humedad_{site}_1996_2025.json.gz'
        meta=src/f'era5_humedad_{site}_1996_2025.meta.json'
        if not path.exists() or not meta.exists():continue
        try:
            with gzip.open(path,'rb') as f:original=f.read()
            m=json.loads(meta.read_text(encoding='utf-8'))
            if m['hash_sha256_original']!=sha(original):
                raise ValueError('SHA original inválido')
            part=aggregate(original,site)
            rows.extend(part)
            sources.append({'site':site,'sha256':sha(original),'archivo':str(path.relative_to(root))})
        except (OSError,ValueError,TypeError,KeyError) as exc:
            issues.append({'site':site,'error':str(exc)})
    rows.sort(key=lambda v:(v['localidad'],v['mes']))
    pairs=defaultdict(list)
    for r in rows:pairs[r['localidad']].append((r['rh_2m_media_pct'],r['vpd_max_diario_media_mes_kpa']))
    twins=[]
    for i,a in enumerate(SITES):
        for b in list(SITES)[i+1:]:
            if a in pairs and b in pairs and pairs[a]==pairs[b]:
                twins.append([a,b])
    report={'fase':'8Z','tipo':'humedad_y_vpd_de_ERA5_modelados',
            'periodo_referencia':'1996-2025','localidades_esperadas':list(SITES),
            'localidades_serie_completa':sorted(pairs),
            'registros_mes_sitio':len(rows),'registros_esperados':1440,
            'cobertura_regional_cuatro_sitios_completa':len(rows)==1440,
            'datos_reanalisis_no_sensor':True,'no_mide_humedad_dosel':True,
            'vpd_mensual_es_media_de_maximos_diarios':True,
            'series_humedad_vpd_identicas':twins,
            'fuentes_original_sha256':sources,
            'errores_fuentes':issues,'no_alertas_fitosanitarias':True,
            'no_validacion_instrumental_senamhi':True}
    if not check:
        dst.mkdir(parents=True,exist_ok=True)
        if rows:(dst/'humedad_vpd_mensual_8z.csv').write_bytes(csv_payload(rows))
        (dst/'estado_humedad_8z.json').write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        if rows and (dst/'humedad_vpd_mensual_8z.csv').read_bytes()!=csv_payload(rows):
            raise AssertionError('CSV mensual distinto de fuente original')
        if json.loads((dst/'estado_humedad_8z.json').read_text())!=report:
            raise AssertionError('Reporte de cobertura desactualizado')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    p.add_argument('--fetch',action='store_true');p.add_argument('--site',choices=list(SITES))
    p.add_argument('--check',action='store_true')
    x=p.parse_args()
    print(json.dumps(run(x.root,x.fetch,x.site,x.check),ensure_ascii=False,indent=2))
