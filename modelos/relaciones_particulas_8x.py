#!/usr/bin/env python3
"""8X. Asociación descriptiva PM2.5/PM10 vs viento, lluvia, radiación y Niño1+2.
No prueba causalidad ni constituye predictor validado.
Exige ≥24 meses coincidentes (2023-2025), sin imputar faltantes.
"""
import argparse
import csv
import io
import json
import math
from pathlib import Path

ROOT_PM=Path('datos/aire_8x/particulas_mensuales_8x.csv')
STATE_PM=Path('datos/aire_8x/estado_aire_8x.json')
ROOT_CLIM=Path('datos/integracion_8v/matriz_terrestre_8v.csv')
OUT=Path('datos/relaciones_pm_8x')
SITES=('Chiclayo','Jayanca','Motupe','Olmos')
POLLUTANTS=('pm25_media_ug_m3','pm10_media_ug_m3')
PREDICTORS=('precipitacion_mes_mm','viento_10m_m_s',
            'radiacion_mes_mj_m2','anomalia_nino12_c')
MIN_MONTHS=24

def csv_rows(path):
    return list(csv.DictReader(io.StringIO(Path(path).read_text(encoding='utf-8-sig'))))

def pearson(x,y):
    if len(x)!=len(y) or len(x)<3:raise ValueError('Insufficient values')
    xbar=sum(x)/len(x); ybar=sum(y)/len(y)
    sx=sum((v-xbar)**2 for v in x); sy=sum((v-ybar)**2 for v in y)
    if sx<=1e-14 or sy<=1e-14:return None
    return sum((a-xbar)*(b-ybar) for a,b in zip(x,y))/math.sqrt(sx*sy)

def run(root='.',check=False):
    root=Path(root)
    state=json.loads((root/STATE_PM).read_text(encoding='utf-8'))
    if state['tipo']!='modelo_atmosferico_no_medicion_instrumental':
        raise ValueError('Origen PM no modelado')
    pm=csv_rows(root/ROOT_PM) if (root/ROOT_PM).exists() else []
    climate=csv_rows(root/ROOT_CLIM)
    c={(r['localidad'],r['mes']):r for r in climate}
    groups=[]
    for site in SITES:
        records=[r for r in pm if r['localidad']==site and
                 r.get('mes_pm_completo_80pct')=='True' and '2023-01'<=r['mes']<='2025-12']
        if len({r['mes'] for r in records})!=len(records):
            raise ValueError('Mes PM duplicado')
        for pm_key in POLLUTANTS:
            for climate_key in PREDICTORS:
                pairs=[]
                for row in sorted(records,key=lambda r:r['mes']):
                    key=(site,row['mes'])
                    if key not in c:continue
                    try:
                        px=float(row[pm_key]);cv=float(c[key][climate_key])
                    except (ValueError,TypeError,KeyError):
                        continue
                    if math.isfinite(px) and math.isfinite(cv):
                        pairs.append((px,cv))
                corr=pearson([r[0] for r in pairs],[r[1] for r in pairs]) if len(pairs)>=MIN_MONTHS else None
                groups.append(dict(localidad=site,particula=pm_key,
                    variable=climate_key,meses_emparejados=len(pairs),
                    correlacion_pearson=round(corr,6) if corr is not None else None,
                    evaluable_descriptivamente=corr is not None))
    pairs=state.get('series_pm_identicas',[])
    report=dict(
        fase='8X',estado='asociacion_retrospectiva_no_causal',
        periodo='2023-2025 solamente',
        modelos_no_instrumentos=True,serie_climatica_1996_2025_no_compatible_con_PM=True,
        controles_sin_imputacion=True,
        correlaciones_no_son_habilidad_predictiva=True,
        pares_series_pm_identicas=pairs,
        correlaciones=groups,
        n_relaciones_evaluables=sum(x['evaluable_descriptivamente'] for x in groups),
        n_relaciones_totales=len(groups),
        no_emitir_alertas=True
    )
    out=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    folder=root/OUT
    if check:
        if (folder/'estado_relaciones_pm_8x.json').read_bytes()!=out:
            raise AssertionError('Desactualizado')
    else:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'estado_relaciones_pm_8x.json').write_bytes(out)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--check',action='store_true')
    o=p.parse_args()
    d=run(o.root,o.check)
    print(json.dumps({k:v for k,v in d.items() if k!='correlaciones'},ensure_ascii=False,indent=2))
