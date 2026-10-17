#!/usr/bin/env python3
"""8X: diagnóstico en años seleccionados de errores del benchmark 8W,
cuidando que 1997-1998 SOLO está en entrenamiento 8W y no es prueba.
No concede habilidad predictiva real, ni compara estación con reanálisis.
"""
import argparse
import csv
import io
import json
import math
from collections import defaultdict
from pathlib import Path

SOURCE=Path('datos/benchmark_8w/predicciones_mensuales_8w.csv')
STATE=Path('datos/benchmark_8w/estado_benchmark_8w.json')
TARGET=Path('datos/extremos_8x')
YEARS=(2017,2023)
TARGETS=('temperatura_aire_c','precipitacion_mes_mm')
MODELS=('climatologia','persistencia','local_ridge','local_viento','local_viento_sst')
SITES=('Chiclayo','Jayanca','Motupe','Olmos')

def read(root):
    data=list(csv.DictReader(io.StringIO((root/SOURCE).read_text(encoding='utf-8'))))
    benchmark=json.loads((root/STATE).read_text(encoding='utf-8'))
    if not data or benchmark.get('fase')!='8W' or benchmark.get('prediccion_operativa_validada') is not False:
        raise ValueError('8W source absent / invalid')
    return data

def compute(rows):
    seen=set()
    groups=defaultdict(list)
    for r in rows:
        if r['localidad'] not in SITES or r['objetivo'] not in TARGETS or r['modelo'] not in MODELS:
            raise ValueError('Unknown model/site/target')
        key=(r['localidad'],r['objetivo'],r['horizonte_meses'],r['modelo'],r['mes_objetivo'])
        if key in seen:raise ValueError('Duplicate independent forecast tuple')
        seen.add(key)
        year=int(r['mes_objetivo'][:4])
        if year not in YEARS:continue
        if int(r['horizonte_meses']) not in (1,2,3):raise ValueError('h')
        actual=float(r['observado']); pred=float(r['prediccion'])
        if not all(math.isfinite(x) for x in (actual,pred)):raise ValueError('nonfinite')
        bucket='enero_abril' if 1<=int(r['mes_objetivo'][5:])<=4 else 'mayo_diciembre'
        groups[(r['localidad'],r['objetivo'],r['horizonte_meses'],r['modelo'],year,bucket)].append(abs(pred-actual))
    out=[]
    for k,errors in sorted(groups.items()):
        site,target,h,model,year,bucket=k
        if len(errors)!=(4 if bucket=='enero_abril' else 8):
            raise ValueError('Incomplete event year / season '+str(k))
        out.append(dict(localidad=site,objetivo=target,horizonte_meses=h,
                        modelo=model,anio_prueba=year,estacion=bucket,
                        meses_prueba=len(errors),mae=round(sum(errors)/len(errors),6),
                        error_absoluto_max=round(max(errors),6)))
    return out

def csv_bytes(rows):
    o=io.StringIO(newline='')
    w=csv.DictWriter(o,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
    return o.getvalue().encode('utf-8')

def run(root='.',check=False):
    root=Path(root)
    matrix=compute(read(root))
    outcome={
      'fase':'8X',
      'analisis':'diagnostico_temporal_extremos_retrospectivo',
      'anios_prueba_diagnosticados':list(YEARS),
      'evento_1997_1998_no_tiene_holdout_en_8w':True,
      'eventos_2017_2023_son_subgrupos_de_la_misma_prueba_8w':True,
      'validacion_instrumental_SENAMHI':False,
      'prediccion_operativa':False,
      'n_grupos_mae_estacional':len(matrix),
      'periodo_historico_incorporado_a_modelo':'1996-2025',
      'n_celdas_homogeneas_certificadas':0,
      'interpretacion':'Analisis de errores retrospectivos en anos/eventos conocidos; no demuestra anticipacion de extremos no vistos.',
      'archivo_csv':'error_extremos_2017_2023_8x.csv',
    }
    out={
      'error_extremos_2017_2023_8x.csv':csv_bytes(matrix),
      'estado_extremos_8x.json':(json.dumps(outcome,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    }
    target=root/TARGET
    if check:
        for n,b in out.items():
            if (target/n).read_bytes()!=b:raise AssertionError('Not reproducible '+n)
    else:
        target.mkdir(parents=True,exist_ok=True)
        for n,b in out.items():(target/n).write_bytes(b)
    return outcome
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    p.add_argument('--check',action='store_true')
    x=p.parse_args()
    print(json.dumps(run(x.root,x.check),ensure_ascii=False,indent=2))
