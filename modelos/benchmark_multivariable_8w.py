#!/usr/bin/env python3
"""OAF 8W - walk-forward con climatologias fit SOLO en entrenamiento.
Objetivos: temperatura (°C), lluvia mensual (mm), P90 lluvias enero-abril.
Predictores al cierre del mes origen t, objetivo t+h (h=1,2,3).
NO prediccion operativa ni dato historico con version fecha-emision.
Dependencias: biblioteca estandar Python. NO usa matriz costera incompleta.
"""
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path

INPUT_LAND = Path('datos/integracion_8v/matriz_terrestre_8v.csv')
INPUT_SEA = Path('datos/integracion_8v/matriz_marina_8v.csv')
INPUT_STATE = Path('datos/integracion_8v/estado_integracion_8v.json')
OUT = Path('datos/benchmark_8w')
SITES = ('Chiclayo', 'Jayanca', 'Motupe', 'Olmos')
FOLDS = ((2011, 2013), (2014, 2016), (2017, 2019), (2020, 2022), (2023, 2025))
HORIZONS = (1,2,3)
TARGETS = ('temperatura_aire_c', 'precipitacion_mes_mm')
VARIANTS = ('climatologia', 'persistencia', 'local_ridge', 'local_viento', 'local_viento_sst')
SEASITES = ('Mar_frente_Pimentel', 'Mar_norte_Lambayeque')
CONTINUOUS_FIELDS = ('temperatura_aire_c','precipitacion_mes_mm','viento_10m_m_s',
                     'viento_u_aprox_m_s','viento_v_aprox_m_s')
ALPHA = 15.0

def shift(month, n):
    y, m = map(int, month.split('-'))
    ix = y * 12 + m - 1 + n
    return f'{ix // 12:04d}-{ix % 12 + 1:02d}'

def finite(value, desc):
    try:
        x=float(value)
    except (ValueError, TypeError):
        raise ValueError('Invalid '+desc) from None
    if not math.isfinite(x):
        raise ValueError('Nonfinite '+desc)
    return x

def load_csv(path):
    data=path.read_bytes()
    rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
    if not rows: raise ValueError('Empty data '+str(path))
    return rows, hashlib.sha256(data).hexdigest()

def load(root):
    root=Path(root)
    land, sha_land=load_csv(root/INPUT_LAND)
    sea, sha_sea=load_csv(root/INPUT_SEA)
    state=json.loads((root/INPUT_STATE).read_text(encoding='utf-8'))
    if len(land)!=1440 or len(sea)!=720 or not state.get('no_hay_validacion_prospectiva_de_prediccion'):
        raise ValueError('Matriz 8V no acreditada')
    def mk(rows, site_key):
        out={}
        for row in rows:
            k=(row[site_key],row['mes'])
            if k in out: raise ValueError('Duplicated key '+str(k))
            out[k]=row
        return out
    l=mk(land,'localidad')
    s=mk(sea,'punto_viento')
    months=[f'{yr}-{mo:02d}' for yr in range(1996,2026) for mo in range(1,13)]
    if set(l)!={(site,m) for site in SITES for m in months}: raise ValueError('Incomplete land')
    if set(s)!={(site,m) for site in SEASITES for m in months}: raise ValueError('Incomplete sea')
    for row in land:
        for field in CONTINUOUS_FIELDS+('anomalia_nino12_c','anomalia_nino34_c'):
            finite(row[field],field)
        if finite(row['precipitacion_mes_mm'],'precipitación')<0:
            raise ValueError('Negative rain')
    return l,s,sha_land,sha_sea

def mean(xs):
    if not xs: raise ValueError('Empty sample')
    return sum(xs)/len(xs)

def quantile(vals, probability):
    s=sorted(vals)
    if not s: raise ValueError('Empty quantile')
    pos=(len(s)-1)*probability
    lower=int(pos); higher=min(lower+1,len(s)-1)
    return s[lower]+(s[higher]-s[lower])*(pos-lower)

def solve(a,b):
    n=len(b)
    x=[row[:] + [val] for row,val in zip(a,b)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(x[j][i]))
        if abs(x[pivot][i])<1e-12: raise ValueError('Singular model')
        x[i],x[pivot]=x[pivot],x[i]
        factor=x[i][i]
        for c in range(i,n+1): x[i][c]/=factor
        for j in range(n):
            if j==i:continue
            q=x[j][i]
            for c in range(i,n+1): x[j][c]-=q*x[i][c]
    return [r[-1] for r in x]

def standardized(train_x, test_x):
    cols=list(zip(*train_x))
    means=[mean(col) for col in cols]
    sds=[max(math.sqrt(mean([(x-m)**2 for x in col])),0.000001) for col,m in zip(cols,means)]
    trans=lambda arr:[[(v-m)/sd for v,m,sd in zip(row,means,sds)] for row in arr]
    return trans(train_x),trans(test_x)

def ridge(train_x, train_y, test_x, alpha=ALPHA):
    if not train_x or len(train_x)!=len(train_y): raise ValueError('Empty/mismatched train')
    a,b=standardized(train_x,test_x)
    cols=len(a[0])+1
    # Unpenalized intercept, standardized predictors, fixed regularization.
    a=[[1]+r for r in a]; b=[[1]+r for r in b]
    gram=[[sum(row[i]*row[j] for row in a)+(alpha if i==j and i>0 else 0)
           for j in range(cols)] for i in range(cols)]
    cov=[sum(row[i]*y for row,y in zip(a,train_y)) for i in range(cols)]
    betas=solve(gram,cov)
    return [sum(x*v for x,v in zip(row,betas)) for row in b]

def logistic(train_x, labels, test_x):
    a,b=standardized(train_x,test_x)
    a=[[1]+r for r in a];b=[[1]+r for r in b]
    p=mean(labels)
    p=min(.99,max(.01,p))
    weights=[math.log(p/(1-p))]+[0]*(len(a[0])-1)
    # Constant objective/iterations: never fit thresholds or tuning on holdout.
    n=len(labels)
    for _ in range(260):
        grads=[0.0]*len(weights)
        for x,y in zip(a,labels):
            z=max(-30,min(30,sum(v*w for v,w in zip(x,weights))))
            err=1/(1+math.exp(-z))-y
            for j,val in enumerate(x): grads[j]+=err*val/n
        for j in range(len(weights)):
            if j>0:grads[j]+=0.1*weights[j]
            weights[j]-=.12*grads[j]
    return [max(.001,min(.999,1/(1+math.exp(-max(-30,min(30,sum(x*w for x,w in zip(row,weights))))))))
            for row in b]

def transformed(target, row):
    v=finite(row[target],target)
    return math.log1p(v) if target=='precipitacion_mes_mm' else v

def invert(target, val):
    return max(0,math.expm1(min(15,max(-15,val)))) if target=='precipitacion_mes_mm' else val

def normals(train, target):
    return {mo:mean([transformed(target,r) for r in train if int(r['mes'][5:])==mo])
            for mo in range(1,13)}

def normal_features(train, by_month, site, target):
    # All local climatologies belong exclusively to the training targets.
    keys=CONTINUOUS_FIELDS
    clim={}
    for key in keys:
        clim[key]={mo:mean([math.log1p(float(r[key])) if key=='precipitacion_mes_mm'
                            else float(r[key]) for r in train if int(r['mes'][5:])==mo])
                   for mo in range(1,13)}
    return clim

def feature(row, clim, variant, ocean_prev, maritime=None):
    mo=int(row['mes'][5:])
    temp=float(row['temperatura_aire_c'])-clim['temperatura_aire_c'][mo]
    rain=math.log1p(float(row['precipitacion_mes_mm']))-clim['precipitacion_mes_mm'][mo]
    xs=[temp,rain]
    if variant in ('local_viento','local_viento_sst','con_corrientes'):
        xs += [float(row[name])-clim[name][mo] for name in
               ('viento_10m_m_s','viento_u_aprox_m_s','viento_v_aprox_m_s')]
    if variant in ('local_viento_sst','con_corrientes'):
        xs += [float(row['anomalia_nino12_c']),float(row['anomalia_nino34_c']),
               float(ocean_prev['anomalia_nino12_c']),float(ocean_prev['anomalia_nino34_c'])]
    if variant=='con_corrientes':
        if maritime is None: return None
        xs+=maritime
    return xs

def candidate(by_month, origin, clim, variant, sea):
    row=by_month.get(origin)
    prev=by_month.get(shift(origin,-1))
    if not row or not prev: return None
    marine=None
    if variant=='con_corrientes':
        marine=[]
        for sea_site in SEASITES:
            record=sea[(sea_site,origin)]
            if record['corriente_2017_2025_disponible']!='True':
                return None
            for key in ('corriente_geostrofica_u_m_s','corriente_geostrofica_v_m_s'):
                marine.append(finite(record[key],key))
    return feature(row,clim,variant,prev,marine)

def baseline_prob(training_flags):
    # Smoothed event frequency, fixed rule on training only.
    return (sum(training_flags)+1)/(len(training_flags)+2)

def dataset(rows, train_rows, by_month, sea, fold, horizon, target, variant,
            train_start='1996-01'):
    start_year, end_year=fold
    first=f'{start_year}-01'; last=f'{end_year}-12'
    clim=normal_features(train_rows,by_month,'',target)
    target_clim=normals(train_rows,target)
    samples_train=[]; samples_test=[]
    for r in rows:
        month=r['mes']; origin=shift(month,-horizon)
        if month<train_start: continue
        x=candidate(by_month,origin,clim,variant,sea)
        if x is None:continue
        month_n=int(month[5:])
        item=(month,origin,x,transformed(target,r),float(r[target]),target_clim[month_n])
        if month<first:
            samples_train.append(item)
        elif first<=month<=last:
            samples_test.append(item)
    if len(samples_train)<48 or len(samples_test)<24: raise ValueError('Insufficient fold sample')
    if max(r[0] for r in samples_train)>=min(r[0] for r in samples_test):
        raise ValueError('Chronology leak')
    return samples_train,samples_test,target_clim

def predictions(rows, fold, horizon, target, sea, scope='historico_30a'):
    by_month={r['mes']:r for r in rows}
    start_year,end_year=fold
    cutoff=f'{start_year}-01'
    first_train='2017-01' if scope=='corriente_corta' else '1996-01'
    train_rows=[r for r in rows if first_train<=r['mes']<cutoff]
    if len(train_rows)<60: raise ValueError('Fewer than 60 months in training')
    variants=('local_viento_sst','con_corrientes') if scope=='corriente_corta' else VARIANTS[2:]
    all_pred={}
    for variant in variants:
        train,test,clim=dataset(rows,train_rows,by_month,sea,fold,horizon,target,variant,first_train)
        pred=ridge([r[2] for r in train],[r[3]-r[5] for r in train],[r[2] for r in test])
        out={}
        for record,val in zip(test,pred):
            mon,orig,x,yt,raw,norm=record
            out[mon]=invert(target,norm+val)
        all_pred[variant]=out
    if scope=='corriente_corta':return all_pred
    # Compare on EXACTLY the same targets as every ML variant.
    train,test,clim=dataset(rows,train_rows,by_month,sea,fold,horizon,target,'local_ridge')
    by_mon={r['mes']:r for r in rows}
    all_pred['climatologia']={r[0]:invert(target,r[5]) for r in test}
    all_pred['persistencia']={
        r[0]: invert(target,r[5]+
               transformed(target,by_mon[r[1]])-clim[int(r[1][5:])])
        for r in test}
    return all_pred

def events(rows, fold, horizon, sea, site):
    start,end=fold;first=f'{start}-01';last=f'{end}-12'
    train=[r for r in rows if r['mes']<first]
    test=[r for r in rows if first<=r['mes']<=last]
    by_month={r['mes']:r for r in rows}
    # P90 computed strictly from earlier years, separately for each calendar month.
    thresholds={m:quantile([float(r['precipitacion_mes_mm']) for r in train
                            if int(r['mes'][5:])==m],0.9) for m in (1,2,3,4)}
    climatology=normal_features(train,by_month,site,'precipitacion_mes_mm')
    result={}
    for model in ('climatologia_evento','local_ridge','local_viento','local_viento_sst'):
        tr=[];te=[]
        for r in rows:
            mon=r['mes'];mm=int(mon[5:])
            if mm not in thresholds or thresholds[mm]<=0: continue
            orig=shift(mon,-horizon)
            variant='local_ridge' if model=='climatologia_evento' else model
            x=candidate(by_month,orig,climatology,variant,sea)
            if x is None:continue
            item=(mon,x,int(float(r['precipitacion_mes_mm'])>thresholds[mm]))
            if mon<first:tr.append(item)
            elif first<=mon<=last:te.append(item)
        if len(tr)<40 or len(te)<10: raise ValueError('Insufficient event data')
        if model=='climatologia_evento':
            pp=[baseline_prob([r[2] for r in tr])]*len(te)
        else:
            pp=logistic([r[1] for r in tr],[r[2] for r in tr],[r[1] for r in te])
        result[model]={m:(int(y),p,thresholds[int(m[5:])]) for (m,x,y),p in zip(te,pp)}
    return result

def metric(objs, probability=False):
    if not objs:return {'n':0}
    if probability:
        errs=[(o['prediccion']-o['observado'])**2 for o in objs]
        return {'n':len(objs),'eventos':sum(o['observado'] for o in objs),
                'brier':round(mean(errs),8),'prediccion_prob_media':round(mean([o['prediccion'] for o in objs]),6)}
    errs=[o['prediccion']-o['observado'] for o in objs]
    return {'n':len(objs),'mae':round(mean([abs(x) for x in errs]),6),
            'rmse':round(math.sqrt(mean([x*x for x in errs])),6),
            'sesgo':round(mean(errs),6)}

def csv_bytes(rows):
    o=io.StringIO(newline='')
    w=csv.DictWriter(o,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
    return o.getvalue().encode('utf-8')

def run(root='.',check=False):
    root=Path(root)
    l,s,hash_land,hash_sea=load(root)
    continuous=[];event_rows=[];current_rows=[]
    for site in SITES:
        rows=[l[(site,m)] for m in sorted(mon for loc,mon in l if loc==site)]
        for fold in FOLDS:
            for h in HORIZONS:
                for target in TARGETS:
                    pp=predictions(rows,fold,h,target,s)
                    for model,p in pp.items():
                        for month,estimate in p.items():
                            actual=finite(l[(site,month)][target],target)
                            continuous.append(dict(localidad=site,fold=f'{fold[0]}-{fold[1]}',
                                horizonte_meses=h,objetivo=target,modelo=model,
                                mes_objetivo=month,mes_origen=shift(month,-h),
                                observado=round(actual,6),prediccion=round(estimate,6),
                                precipitacion_extrema_modelada_sin_validar=
                                    l[(site,month)]['lluvia_modelada_ge_1000_mm_revisar']))
                ep=events(rows,fold,h,s,site)
                for model,p in ep.items():
                    for month,(y,prob,threshold) in p.items():
                        event_rows.append(dict(localidad=site,fold=f'{fold[0]}-{fold[1]}',
                            horizonte_meses=h,modelo=model,mes_objetivo=month,
                            mes_origen=shift(month,-h),observado=y,
                            prediccion=round(prob,8),umbral_p90_mm=round(threshold,5),
                            fuente='ERA5 reanalisis (no pluviómetro)'))
                if fold==(2023,2025):
                    # Sensibilidad marina 2017-2025, no comparación con el modelo completo 1996-2025.
                    for target in TARGETS:
                        pp=predictions(rows,fold,h,target,s,scope='corriente_corta')
                        for model,p in pp.items():
                            for month,value in p.items():
                                current_rows.append(dict(localidad=site,fold='2023-2025',
                                    entrenamiento='2017-2022',horizonte_meses=h,objetivo=target,
                                    modelo=model,mes_objetivo=month,mes_origen=shift(month,-h),
                                    observado=round(float(l[(site,month)][target]),6),
                                    prediccion=round(value,6)))
    summaries=[]
    grouped=defaultdict(list)
    for row in continuous:
        key=(row['localidad'],row['horizonte_meses'],row['objetivo'],row['modelo'])
        grouped[key].append(row)
    for key,rws in sorted(grouped.items()):
        site,h,target,model=key
        summaries.append(dict(localidad=site,horizonte_meses=h,objetivo=target,modelo=model,
                              **metric(rws)))
    # Estabilidad: NO inferir robustez a partir del promedio de cinco bloques.
    fold_groups=defaultdict(list)
    for row in continuous:
        fold_groups[(row['localidad'],row['objetivo'],row['horizonte_meses'],
                     row['fold'],row['modelo'])].append(row)
    per_fold=[dict(localidad=site,objetivo=target,horizonte_meses=h,
                   fold=fold,modelo=model,**metric(rr))
              for (site,target,h,fold,model),rr in sorted(fold_groups.items())]
    fold_index={(r['localidad'],r['objetivo'],r['horizonte_meses'],r['fold'],r['modelo']):r
                for r in per_fold}
    stability=[]
    for site in SITES:
        for target in TARGETS:
            for h in HORIZONS:
                for model in ('local_viento','local_viento_sst'):
                    delta=[]
                    for a,b in FOLDS:
                        fold=f'{a}-{b}'
                        base=fold_index[(site,target,h,fold,'local_ridge')]['mae']
                        other=fold_index[(site,target,h,fold,model)]['mae']
                        delta.append(100*(base-other)/base)
                    stability.append(dict(localidad=site,objetivo=target,horizonte_meses=h,
                         modelo=model,cortes_mejora=sum(x>0 for x in delta),
                         total_cortes=len(delta),mejora_por_corte_pct=[round(x,3) for x in delta]))
    events_summary=[]
    g=defaultdict(list)
    for row in event_rows:
        g[(row['localidad'],row['horizonte_meses'],row['modelo'])].append(row)
    for (site,h,model),rws in sorted(g.items()):
        events_summary.append(dict(localidad=site,horizonte_meses=h,modelo=model,
                                   **metric(rws,True)))
    g=defaultdict(list)
    for row in current_rows:
        g[(row['localidad'],row['horizonte_meses'],row['objetivo'],row['modelo'])].append(row)
    currents_summary=[dict(localidad=site,horizonte_meses=h,objetivo=target,modelo=model,**metric(rws))
                      for (site,h,target,model),rws in sorted(g.items())]
    state={
      'fase':'8W','estatus':'hindcast_retrospectivo_no_operativo',
      'periodo_referencia':'1996-2025','cortes':[{'train_hasta':f'{a-1}-12','test':f'{a}-01/{b}-12'} for a,b in FOLDS],
      'horizontes_meses':list(HORIZONS),
      'datos_mes_origen_completos_no_vintage':True,
      'aprendizaje_de_normales_umbral_y_escalado_solo_entrenamiento':True,
      'indicadores_ensorevisados_t_no_vintage':True,
      'viento_modelado_no_anemometro':True,
      'precipitacion_modelada_no_pluviometro':True,
      'eventos_lluvia_enero_abril_superacion_p90_training':True,
      'eventos_condicionales_solo_meses_p90_positivo':True,
      'corrientes_geostroficas_2017_2025_evaluadas_solo_sensibilidad':True,
      'corrientes_no_colocalizadas_con_viento':True,
      'prediccion_operativa_validada':False,'alertas_agricolas_permitidas':False,
      'n_predicciones_continuas':len(continuous),
      'n_pronosticos_probabilisticos_eventos':len(event_rows),
      'n_predicciones_sensibilidad_corrientes':len(current_rows),
      'metricas_continuas':summaries,
      'metricas_por_corte':per_fold,
      'estabilidad_variantes':stability,
      'metricas_eventos':events_summary,
      'metricas_sensibilidad_corrientes':currents_summary,
      'sha_8v_entrada':{'terrestre':hash_land,'marino':hash_sea},
      'cautelas':[
        'Hindcast reanalisis y datos oceanicos revisados, no emitidos en fecha historica',
        'Evaluar habilidad en SENAMHI y episodios extremos antes de dar recomendaciones',
        'Mes origen disponible tras cierre mensual: no pronostico antes del comienzo del mes siguiente',
        'Mismo indice oceanico en cuatro localidades: pseudorreplicacion espacial',
        'Corrientes geostroficas no equivalen a corriente total y no colocalizadas con viento',
        'Resultados de lluvia P90 solo enero-abril y threshold con train; no diagnostico de inundacion'
      ]
    }
    out={
      'predicciones_mensuales_8w.csv':csv_bytes(continuous),
      'probabilidades_lluvia_p90_8w.csv':csv_bytes(event_rows),
      'sensibilidad_corrientes_8w.csv':csv_bytes(current_rows),
      'estado_benchmark_8w.json':(json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    }
    directory=root/OUT
    if check:
        for name,blob in out.items():
            f=directory/name
            if not f.exists() or f.read_bytes()!=blob:
                raise AssertionError('Archivo 8W desactualizado '+str(f))
    else:
        directory.mkdir(parents=True,exist_ok=True)
        for name,blob in out.items():
            (directory/name).write_bytes(blob)
    return state

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path('.'))
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    status=run(a.root,a.check)
    print(json.dumps({k:v for k,v in status.items() if not k.startswith('metricas_')},ensure_ascii=False,indent=2))
