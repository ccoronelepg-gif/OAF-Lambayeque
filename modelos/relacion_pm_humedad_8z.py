#!/usr/bin/env python3
"""OAF 8Z: asociacion descriptiva 2023–2025 de PM CAMS frente a RH/VPD ERA5.
Treinta años RH NO equivalen a treinta años PM; no causalidad, no predicción,
no aprendizaje supervisado ni prueba de respuesta fitosanitaria.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path

PM=Path('datos/aire_8x/particulas_mensuales_8x.csv')
AIR_STATUS=Path('datos/aire_8x/estado_aire_8x.json')
HUM=Path('datos/humedad_8z/humedad_vpd_mensual_8z.csv')
HUM_STATUS=Path('datos/humedad_8z/estado_humedad_8z.json')
OUTPUT=Path('datos/relaciones_pm_humedad_8z/estado_relacion_pm_humedad_8z.json')
SITES=('Chiclayo','Jayanca','Motupe','Olmos')
PARTICLES=('pm25_media_ug_m3','pm10_media_ug_m3')
COVARIATES=('rh_2m_media_pct','vpd_max_diario_media_mes_kpa')
MIN=24

def parse(p):
    b=p.read_bytes()
    return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')))),hashlib.sha256(b).hexdigest()

def pearson(values):
    n=len(values)
    if n<MIN:return None
    x=[a for a,b in values];y=[b for a,b in values]
    mx=sum(x)/n;my=sum(y)/n
    v1=sum((a-mx)**2 for a in x);v2=sum((b-my)**2 for b in y)
    if v1<1e-12 or v2<1e-12:return None
    return sum((a-mx)*(b-my) for a,b in values)/math.sqrt(v1*v2)

def residuals(pairs):
    grouping=defaultdict(list)
    for mon,x,y in pairs:grouping[mon[5:]].append((x,y))
    centers={m:(sum(a for a,b in val)/len(val),sum(b for a,b in val)/len(val))
        for m,val in grouping.items()}
    return [(x-centers[mon[5:]][0],y-centers[mon[5:]][1]) for mon,x,y in pairs]

def run(root='.',check=False):
    root=Path(root)
    pm,ph=parse(root/PM)
    h,hhash=parse(root/HUM)
    m1=json.loads((root/AIR_STATUS).read_text(encoding='utf-8'))
    m2=json.loads((root/HUM_STATUS).read_text(encoding='utf-8'))
    if m2['fase']!='8Z' or not m2['cobertura_regional_cuatro_sitios_completa']:
        raise ValueError('Humedad ERA5 de 4 sitios y 30 años NO acreditada')
    if m1['comparacion_legal_ECA_habilitada'] is not False:
        raise ValueError('PM no es instrumento')
    hm={}
    for row in h:
        k=(row['localidad'],row['mes'])
        if k in hm:raise ValueError('Humedad duplicada')
        hm[k]=row
    pmkeys=set(); pmlocal=defaultdict(list)
    for row in pm:
        k=(row['localidad'],row['mes'])
        if k in pmkeys:raise ValueError('PM duplicado')
        pmkeys.add(k)
        if row['mes_pm_completo_80pct']=='True' and row['localidad'] in SITES and '2023-01'<=row['mes']<='2025-12':
            pmlocal[row['localidad']].append(row)
    out=[]
    for site in SITES:
        for part in PARTICLES:
            for variable in COVARIATES:
                pairs=[]
                for row in sorted(pmlocal[site],key=lambda r:r['mes']):
                    other=hm.get((site,row['mes']))
                    if other is None:continue
                    x=float(row[part]);y=float(other[variable])
                    if math.isfinite(x) and math.isfinite(y):
                        pairs.append((row['mes'],x,y))
                enough=len(pairs)>=MIN
                raw=pearson([(x,y) for _,x,y in pairs]) if enough else None
                adj=pearson(residuals(pairs)) if enough else None
                byyear={}
                for year in (2023,2024,2025):
                    rest=[q for q in pairs if not q[0].startswith(str(year))]
                    byyear[str(year)]=pearson(residuals(rest)) if len(rest)>=MIN else None
                out.append({
                 'localidad':site,'particula':part,'covariable':variable,
                 'meses_solapados':len(pairs),'pearson_bruto':round(raw,6) if raw is not None else None,
                 'pearson_deseasonalizado':round(adj,6) if adj is not None else None,
                 'coeficiente_tras_excluir_anio':{k:round(v,6) if v is not None else None for k,v in byyear.items()},
                 'interpretacion':'descriptiva_no_causal','apto_analisis_descriptivo':enough,
                 'serie_pm_coincidente_otro_sitio':any(site in q['sitios'] for q in m1.get('series_pm_identicas',[]))
                })
    result={'fase':'8Z','estado':'analisis_PM_y_humedad_solo_descriptivo',
            'periodo_coincidente':'2023-2025',
            'serie_RH_30_anios_completa':True,
            'serie_PM_30_anios_completa':False,
            'pm_instrumental':False,'rh_instrumental':False,
            'numero_comparaciones':len(out),
            'comparaciones_evaluables':sum(x['apto_analisis_descriptivo'] for x in out),
            'pares_pm_series_identicas':m1.get('series_pm_identicas',[]),
            'correlacion_causal':False,'habilidad_predictiva_validada':False,
            'humedad_dosel_cultivo':False,'riesgo_fitosanitario_validado':False,
            'fuente_sha256':{'pm':ph,'humedad':hhash},'comparaciones':out}
    payload=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if (root/OUTPUT).read_bytes()!=payload:raise AssertionError('Relaciones PM/RH 8Z no reproducibles')
    else:
        (root/OUTPUT).parent.mkdir(parents=True,exist_ok=True)
        (root/OUTPUT).write_bytes(payload)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    d=run(a.root,a.check)
    print(json.dumps({k:v for k,v in d.items() if k!='comparaciones'},
                     ensure_ascii=False,indent=2))
