#!/usr/bin/env python3
"""OAF-Lambayeque 9A. Experimental hindcast comparison with matched 8W.
Horizon +1/+2/+3 months; five expanding training folds, no future leakage.
Add ERA5 humidity or VPD at origin month (complete month and retrospective).
No historical vintage of ERA5/NOAA; NOT a prospective forecast.
All data are model/reanalysis, NOT field data or biological incidence.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path

import benchmark_multivariable_8w as b

HUMIDITY=Path('datos/humedad_8z/humedad_vpd_mensual_8z.csv')
HUM_STATE=Path('datos/humedad_8z/estado_humedad_8z.json')
BASE_CSV=Path('datos/benchmark_8w/predicciones_mensuales_8w.csv')
BASE_EVENT=Path('datos/benchmark_8w/probabilidades_lluvia_p90_8w.csv')
BASE_STATE=Path('datos/benchmark_8w/estado_benchmark_8w.json')
OUT=Path('datos/benchmark_9a')
MODELS=('base_viento_sst','base_mas_rh','base_mas_vpd','base_mas_rh_vpd')
BASE='base_viento_sst'
HKEYS=('rh_2m_media_pct','vpd_max_diario_media_mes_kpa')
VARIANT='local_viento_sst'

def read_csv(path):
    raw=path.read_bytes()
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if not rows:raise ValueError('Archivo vacío '+str(path))
    return rows,hashlib.sha256(raw).hexdigest()

def load(root):
    root=Path(root)
    land,sea,landhash,seahash=b.load(root)
    humidity,hhash=read_csv(root/HUMIDITY)
    state=json.loads((root/HUM_STATE).read_text(encoding='utf-8'))
    original=json.loads((root/BASE_STATE).read_text(encoding='utf-8'))
    if state.get('cobertura_regional_cuatro_sitios_completa') is not True or len(humidity)!=1440:
        raise ValueError('RH/VPD 1996-2025 incompletos')
    if original.get('fase')!='8W' or original.get('prediccion_operativa_validada') is not False:
        raise ValueError('Benchmark 8W no acreditado')
    index={}
    for r in humidity:
        k=(r['localidad'],r['mes'])
        if k in index:raise ValueError('RH/VPD duplicado')
        for name in HKEYS:
            v=b.finite(r[name],name)
            if name==HKEYS[0] and not 0<=v<=100:raise ValueError('RH fuera de rango')
            if name==HKEYS[1] and not 0<=v<=15:raise ValueError('VPD fuera de rango')
        if r.get('no_es_humedad_del_dosel')!='True':raise ValueError('Humid dosel mal rotulada')
        index[k]=r
    if set(index)!=set(land):raise ValueError('RH/VPD no coinciden por mes-localidad')
    original_rows,oldhash=read_csv(root/BASE_CSV)
    old={}
    for r in original_rows:
        if r['modelo']!=VARIANT:continue
        k=(r['localidad'],r['fold'],int(r['horizonte_meses']),r['objetivo'],r['mes_objetivo'])
        if k in old:raise ValueError('8W duplicó predicción')
        old[k]=r
    expected=4*5*3*2*36
    if len(old)!=expected:raise ValueError('Archivo 8W base incompleto')
    event_rows,eventhash=read_csv(root/BASE_EVENT)
    evt={}
    for r in event_rows:
        if r['modelo']!=VARIANT:continue
        k=(r['localidad'],r['fold'],int(r['horizonte_meses']),r['mes_objetivo'])
        if k in evt:raise ValueError('8W P90 evento duplicado')
        evt[k]=r
    if len(evt)!=4*5*3*12:raise ValueError('8W evento incompleto')
    return land,sea,index,old,evt,{
        '8w_land':landhash,'8w_marine':seahash,'humidity':hhash,
        'baseline':oldhash,'events':eventhash}

def means(training_months, humidity):
    if not training_months:raise ValueError('Sin entrenamiento')
    out={}
    for name in HKEYS:
        out[name]={}
        for mo in range(1,13):
            vals=[b.finite(humidity[r['mes']][name],name) for r in training_months
                  if int(r['mes'][5:])==mo]
            out[name][mo]=b.mean(vals)
    return out

def features(base_x,origin,humidity,clim,variant):
    """Only origin month t RH/VPD, NEVER t+h or predictors from test target."""
    if origin not in humidity:raise ValueError('RH/VPD ausente en origen '+origin)
    mo=int(origin[5:])
    rh=b.finite(humidity[origin][HKEYS[0]],HKEYS[0])-clim[HKEYS[0]][mo]
    vpd=b.finite(humidity[origin][HKEYS[1]],HKEYS[1])-clim[HKEYS[1]][mo]
    if variant==BASE:return list(base_x)
    if variant=='base_mas_rh':return list(base_x)+[rh]
    if variant=='base_mas_vpd':return list(base_x)+[vpd]
    if variant=='base_mas_rh_vpd':return list(base_x)+[rh,vpd]
    raise ValueError('Modelo 9A desconocido')

def continuous_for(site,rows,fold,h,target,sea,humidity,base):
    train_end=f'{fold[0]}-01'
    training=[r for r in rows if r['mes']<train_end]
    bymonth={r['mes']:r for r in rows}
    humidity_site={mon:humidity[(site,mon)] for mon in bymonth}
    clim_h=means(training,humidity_site)
    tr,te,_=b.dataset(rows,training,bymonth,sea,fold,h,target,VARIANT)
    out=[]
    label=f'{fold[0]}-{fold[1]}'
    for model in MODELS:
        train_x=[features(r[2],r[1],humidity_site,clim_h,model) for r in tr]
        test_x=[features(r[2],r[1],humidity_site,clim_h,model) for r in te]
        predicted=b.ridge(train_x,[r[3]-r[5] for r in tr],test_x)
        for r,p in zip(te,predicted):
            month,origin,x,ytrans,actual,normal=r
            val=b.invert(target,normal+p)
            if not math.isfinite(val):raise ValueError('Predicción no finita')
            k=(site,label,h,target,month)
            original=base[k]
            if abs(float(original['observado'])-actual)>0.000001:
                raise AssertionError('8W y 9A tienen observaciones diferentes')
            # Original 8W rounds to 6 decimals; model reproduces the same baseline.
            if model==BASE and abs(float(original['prediccion'])-val)>0.000002:
                raise AssertionError('9A does NOT reproduce baseline 8W '+str(k))
            if origin!=b.shift(month,-h):raise AssertionError('Fuga temporal')
            out.append(dict(localidad=site,fold=label,
                horizonte_meses=h,objetivo=target,modelo=model,mes_objetivo=month,
                mes_origen=origin,observado=round(actual,6),prediccion=round(val,6),
                modelo_reanalisis_no_validacion_prospectiva=True))
    if len(out)!=36*len(MODELS):raise ValueError('Periodo prueba incompleto')
    return out

def probability_for(site,rows,fold,h,sea,humidity,old_events):
    """Same P90 thresholds and test labels as 8W, compare calibrated Brier on test."""
    start,end=fold
    label=f'{start}-{end}'
    first=f'{start}-01';last=f'{end}-12'
    train=[r for r in rows if r['mes']<first]
    bymonth={r['mes']:r for r in rows}
    byhumidity={mon:humidity[(site,mon)] for mon in bymonth}
    hnormal=means(train,byhumidity)
    localclim=b.normal_features(train,bymonth,site,'precipitacion_mes_mm')
    thresholds={m:b.quantile([float(r['precipitacion_mes_mm']) for r in train
        if int(r['mes'][5:])==m],.9) for m in (1,2,3,4)}
    train_examples=[];test_examples=[]
    for r in rows:
        mon=r['mes'];mm=int(mon[5:])
        if mm not in thresholds or thresholds[mm]<=0:continue
        origin=b.shift(mon,-h)
        base=b.candidate(bymonth,origin,localclim,VARIANT,sea)
        if base is None:continue
        x=features(base,origin,byhumidity,hnormal,'base_mas_rh_vpd')
        item=(mon,origin,x,int(float(r['precipitacion_mes_mm'])>thresholds[mm]),thresholds[mm])
        if mon<first:train_examples.append(item)
        elif first<=mon<=last:test_examples.append(item)
    if len(train_examples)<40 or len(test_examples)!=12:raise ValueError('P90 fold incompleto')
    pred=b.logistic([q[2] for q in train_examples],[q[3] for q in train_examples],
                   [q[2] for q in test_examples])
    result=[]
    for item,p in zip(test_examples,pred):
        mon,origin,x,obs,th=item
        k=(site,label,h,mon)
        base=old_events[k]
        if int(base['observado'])!=obs:raise AssertionError('Evento 8W etiqueta distinta')
        if abs(float(base['umbral_p90_mm'])-th)>0.00002:
            raise AssertionError('8W umbral P90 no coincide')
        for model,prob in ((BASE,float(base['prediccion'])),('base_mas_rh_vpd',p)):
            if not 0<=prob<=1:raise ValueError('Probabilidad no válida')
            result.append(dict(localidad=site,fold=label,horizonte_meses=h,
                modelo=model,mes_objetivo=mon,mes_origen=origin,
                observado=obs,prediccion=round(prob,8),umbral_p90_train_mm=round(th,5),
                es_climatologia_train_p90=True))
    return result

def grouped_metrics(rows,events=False,fold=False):
    g=defaultdict(list)
    for r in rows:
        k=(r['localidad'],int(r['horizonte_meses']),
            r['objetivo'] if not events else 'precipitacion_p90',
            r['modelo'],r['fold'] if fold else 'agregado_2011_2025')
        g[k].append(r)
    out=[]
    for (site,h,target,model,period),r in sorted(g.items()):
        measures=b.metric(r,probability=events)
        out.append(dict(localidad=site,horizonte_meses=h,objetivo=target,
                        modelo=model,periodo=period,**measures))
    return out

def gains(metric_rows,key):
    index={(r['localidad'],r['horizonte_meses'],r['objetivo'],
           r['periodo'],r['modelo']):r for r in metric_rows}
    out=[]
    for x in metric_rows:
        if x['modelo']==BASE:continue
        k=(x['localidad'],x['horizonte_meses'],x['objetivo'],x['periodo'])
        b0=index[k+(BASE,)][key]
        value=x[key]
        out.append(dict(localidad=x['localidad'],horizonte_meses=x['horizonte_meses'],
            objetivo=x['objetivo'],periodo=x['periodo'],modelo=x['modelo'],
            metrica=key,baseline=b0,modelo_valor=value,
            mejoria_pct=round(100*(b0-value)/b0,4) if b0>0 else None))
    return out

def extreme_diagnostics(rows):
    out=[]
    for site in b.SITES:
        for yr in (2017,2023):
            for h in b.HORIZONS:
                for target in b.TARGETS:
                    for model in MODELS:
                        selection=[x for x in rows if x['localidad']==site and
                            x['objetivo']==target and x['horizonte_meses']==h and
                            x['modelo']==model and x['mes_objetivo'].startswith(str(yr)+'-') and
                            1<=int(x['mes_objetivo'][5:])<=4]
                        if len(selection)!=4:raise AssertionError('Cuatrimestre no cubierto')
                        m=b.metric(selection)
                        out.append(dict(localidad=site,anio=yr,meses='enero-abril',
                                        objetivo=target,horizonte_meses=h,
                                        modelo=model,**m))
    return out

def run(root='.',check=False):
    root=Path(root)
    land,sea,humid,old,old_events,hashes=load(root)
    continuous=[];events=[]
    for site in b.SITES:
        rows=[land[(site,m)] for m in sorted(mon for loc,mon in land if loc==site)]
        for fold in b.FOLDS:
            for h in b.HORIZONS:
                for target in b.TARGETS:
                    continuous.extend(continuous_for(site,rows,fold,h,target,sea,humid,old))
                events.extend(probability_for(site,rows,fold,h,sea,humid,old_events))
    overall=grouped_metrics(continuous)
    per_fold=grouped_metrics(continuous,fold=True)
    overall_event=grouped_metrics(events,events=True)
    per_fold_event=grouped_metrics(events,events=True,fold=True)
    gs=gains(overall,'mae')
    gs_fold=gains(per_fold,'mae')
    event_gains=gains(overall_event,'brier')
    gt=defaultdict(list)
    for r in gs_fold:
        gt[(r['localidad'],r['horizonte_meses'],r['objetivo'],r['modelo'])].append(r)
    stability=[dict(localidad=k[0],horizonte_meses=k[1],objetivo=k[2],
                    modelo=k[3],cortes_con_mejora=sum(x['mejoria_pct']>0 for x in vals),
                    total_cortes=len(vals),mejora_pct_por_corte=[x['mejoria_pct'] for x in vals])
              for k,vals in sorted(gt.items())]
    diagnostics=extreme_diagnostics(continuous)
    state=dict(
     fase='9A',tipo='backtesting_retroactivo_sin_vintages',
     validacion_prospectiva=False,alertas_agricolas_aprobadas=False,
     evaluacion_instrumental_senamhi=False,
     fechas_ensayo=[{'train_hasta':f'{x[0]-1}-12','test':f'{x[0]}-01/{x[1]}-12'} for x in b.FOLDS],
     horizontes_meses=list(b.HORIZONS),
     lugares=list(b.SITES),referencia_climatica='1996-2025',
     campo_humedad='RH media diaria 2m ERA5; no humedad dosel',
     campo_vpd='media mensual de VPD máximo diario ERA5; no VPD medio horario',
     covariables_humedad_solo_de_mes_origen=True,
     valores_revisados_no_vintage=True,
     normales_de_train_sin_test=True,escalado_de_train_sin_test=True,
     regularizacion_Ridge=b.ALPHA,
     eventos_P90_enero_abril_thresh_training=True,
     pm25_pm10_no_incluidos_por_cobertura_historica_insuficiente=True,
     n_predicciones_continuas=len(continuous),n_eventos_probabilisticos=len(events),
     metrica_mae=gs,metricas_continuas=overall,
     estabilidad_cortes=stability, metricas_por_corte=per_fold,
     mejoras_brier=event_gains,metricas_eventos=overall_event,
     metricas_eventos_por_corte=per_fold_event,
     auditoria_2017_2023_enero_abril=diagnostics,
     sha_entradas=hashes,
     advertencias=[
      'Comparación ajustada por igual sitio fecha objetivo y horizonte que la fase 8W',
      'Reanálisis ERA5 y series NOAA retrospectivas no son emisiones en tiempo real',
      '1998 es parte del entrenamiento en todos los cortes, no test ENSO independiente',
      'La humedad 2m no representa humectación foliar ni potencial de infección',
      'La lluvia ERA5 de 1998 tiene extremos a contrastar con estaciones SENAMHI',
      'No usar pruebas de 4 meses como demostración de habilidad en El Niño Costero',
      'No hay muestras de campo ni evaluación fitosanitaria por cultivo',
     ])
    output={'pronosticos_pareados_9a.csv':b.csv_bytes(continuous),
            'eventos_p90_pareados_9a.csv':b.csv_bytes(events),
            'estado_benchmark_9a.json':(json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode('utf-8')}
    folder=root/OUT
    if check:
        for filename,payload in output.items():
            if (folder/filename).read_bytes()!=payload:
                raise AssertionError('9A no reproducible: '+filename)
    else:
        folder.mkdir(parents=True,exist_ok=True)
        for filename,payload in output.items():
            (folder/filename).write_bytes(payload)
    return {k:v for k,v in state.items() if k not in ('metrica_mae',
        'metricas_continuas','estabilidad_cortes','metricas_por_corte','mejoras_brier',
        'metricas_eventos','metricas_eventos_por_corte','auditoria_2017_2023_enero_abril')}
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    print(json.dumps(run(a.root,a.check),ensure_ascii=False,indent=2))
