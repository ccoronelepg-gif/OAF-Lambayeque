#!/usr/bin/env python3
# OAF 10B — revisión histórica, NO validación operativa as-issued.
import csv,json,math,hashlib,argparse
from pathlib import Path
from collections import defaultdict
NAMES={'climatologia_global','climatologia_piso','persistencia_anual','random_forest','gcn'}
DATES={f'{y}-{m:02d}' for y in range(2021,2026) for m in range(1,13)}
def quantile(errors,alpha=.10):
    if len(errors)!=24:raise ValueError('Calibración no contiene 24 meses')
    k=math.ceil((len(errors)+1)*(1-alpha))
    return sorted(abs(v) for v in errors)[k-1] if k<=len(errors) else float('inf')
def summarize(rows):
    n=len(rows)
    return {'n':n,'cobertura_pct':round(100*sum(r['ok'] for r in rows)/n,2),
            'mae_mm':round(sum(abs(r['err']) for r in rows)/n,4),
            'ancho_medio_mm':round(sum(r['width'] for r in rows)/n,2),
            'sesgo_mm':round(sum(r['err'] for r in rows)/n,4)}
def group(rows,fields):
    d=defaultdict(list)
    for r in rows:d[tuple(r[f] for f in fields)].append(r)
    return [{**dict(zip(fields,k)),**summarize(v)} for k,v in sorted(d.items())]
def events(rows):
    out=[]
    for mm in (50,100,150):
        for model in ('random_forest','gcn','climatologia_piso'):
            pts=[r for r in rows if r['modelo']==model and r['obs']>=mm]
            hit=sum(r['pred']>=mm for r in pts)
            out.append({'modelo':model,'umbral_mm':mm,'n_eventos':len(pts),'detectados':hit,
                        'omitidos':len(pts)-hit,'sensibilidad_pct':round(100*hit/len(pts),2) if pts else None})
    return out
def calculate(csvfile,meta):
    if hashlib.sha256(csvfile.read_bytes()).hexdigest()!=meta['sha256_predicciones_9x']:
        raise ValueError('SHA256 distinto del inventario 9X')
    allrows=[]
    with csvfile.open(newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f)
        req={'mes','anio','sector','piso','bloque','modelo','observado_CHIRPS_mm','predicho_mm'}
        if set(rd.fieldnames or [])!=req:raise ValueError('Cabeceras de predicción inesperadas')
        for row in rd:
            if row['mes'] not in DATES or row['anio']!=row['mes'][:4] or row['modelo'] not in NAMES:
                raise ValueError('Fecha o modelo incorrectos')
            obs,pred=float(row['observado_CHIRPS_mm']),float(row['predicho_mm'])
            if not all(math.isfinite(v) and v>=0 for v in (obs,pred)):raise ValueError('Precipitación inválida')
            allrows.append({'mes':row['mes'],'anio':row['anio'],'sector':row['sector'],
                'piso':row['piso'],'bloque':row['bloque'],'modelo':row['modelo'],
                'obs':obs,'pred':pred,'err':pred-obs})
    if len(allrows)!=11700 or len({r['sector'] for r in allrows})!=39 or {r['mes'] for r in allrows}!=DATES:
        raise ValueError('Matriz 9X incompleta')
    items=defaultdict(list);observed=defaultdict(set);modelpairs=defaultdict(set)
    for r in allrows:
        key=(r['sector'],r['mes'])
        observed[key].add((r['obs'],r['piso'],r['bloque']))
        modelpairs[key].add(r['modelo'])
        items[(r['sector'],r['modelo'])].append(r)
    if len(modelpairs)!=2340 or any(len(observed[k])!=1 or modelpairs[k]!=NAMES for k in modelpairs):
        raise ValueError('Objetivos no pareados')
    # Debe haber EXACTAMENTE un valor sector/mes/modelo.
    if any(len(v)!=60 or len({r['mes'] for r in v})!=60 for v in items.values()):
        raise ValueError('Duplicados o vacíos sector-mes-modelo')
    tested=[]
    for key,rr in items.items():
        cal=[r for r in rr if r['anio'] in ('2021','2022')]
        test=[r for r in rr if r['anio'] in ('2023','2024','2025')]
        if len(cal)!=24 or len(test)!=36:raise ValueError('Split fuera de especificación')
        q=quantile([r['err'] for r in cal])
        for r in test:
            lower=max(0,r['pred']-q)
            tested.append({**r,'ok':lower<=r['obs']<=r['pred']+q,
                           'width':r['pred']+q-lower})
    return {'global':group(tested,('modelo',)),
            'por_anio':group(tested,('anio','modelo')),
            'por_piso_2023':group([r for r in tested if r['anio']=='2023'],('piso','modelo')),
            'umbrales_exploratorios':events(tested)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args()
    path=a.repo/'datos/generalizacion_9x/predicciones_sector_bloque_9x.csv'
    meta=json.loads((a.repo/'datos/generalizacion_9x/evaluacion_bloques_espaciales_9x.json').read_text('utf8'))
    calc=calculate(path,meta)
    archived=json.loads((a.repo/'datos/calibracion_10b/evaluacion_temporal_10b.json').read_text('utf8'))
    for name,value in calc.items():
        if value!=archived[name]:raise ValueError('10B no reproduce el archivo publicado: '+name)
    if archived.get('alertas_activadas') is not False or archived.get('as_issued_verificado') is not False:
        raise ValueError('Activación o certificación no permitida')
    print('10B: 11700 predicciones auditadas, 195 calibraciones y 7020 pruebas sector-modelo; alerta=NO')
if __name__=='__main__':main()
