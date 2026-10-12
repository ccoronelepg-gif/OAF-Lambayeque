"""OAF-Lambayeque: primera comparacion exploratoria de lluvia mensual, 1998.
Datos observados: cinco estaciones SENAMHI (archivos de usuario, agregados).
Productos: PISCOp v3.0 (API de terceros Fluviotech), ERA5-Seamless (Open-Meteo).
ADVERTENCIA: ubicacion historica de las estaciones pendiente de confirmacion;
PISCOp puede incorporar las estaciones en su entrenamiento/interpolacion.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OBS = ROOT / 'datos' / 'senamhi_mensual_1998.csv'
OUT = ROOT / 'datos'

# Coordenadas publicadas, elegidas para esta auditoria (metadatos historicos
# aun sujetos a confirmacion; nunca reemplazan la ficha original de estacion).
STATIONS = {
    'Jayanca (La Viña)': (-6.322, -79.779, 'SENAMHI informe de Jayanca 2017'),
    'Cayaltí': (-6.88079444, -79.54701389, 'SENAMHI ficha Cayalti 000320'),
    'Reque': (-6.88613, -79.8355, 'ANA citada en repositorio Universidad Ricardo Palma'),
    'Lambayeque': (-6.73152778, -79.90983611, 'Ficha SENAMHI reproducida en documento historico; confirmar'),
    'Cueva Blanca': (-6.13130, -79.40450, 'SENAMHI informe norte 2020: ~-6.13,-79.40, 3300 m'),
}

PISCO_URL = 'https://fluviotech.com/meteodata/pisco/monthly/series/'
ERA_URL = 'https://archive-api.open-meteo.com/v1/archive'
HEADERS = {'User-Agent': 'OAF-Lambayeque-research/0.4 (noncommercial-scientific-validation)'}


def get_json(method: str, url: str, **kwargs):
    """Peticion con reintentos acotados, sin esconder errores de red/HTTP."""
    error = None
    for intento in range(3):
        try:
            response = requests.request(method, url, timeout=90,
                                        headers=HEADERS, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            error = exc
            print(f'ERROR intento {intento + 1}/3: {type(exc).__name__} {str(exc)[:130]}', flush=True)
            if intento < 2:
                time.sleep(5 + 5 * intento)
    raise RuntimeError(f'Consulta sin respuesta util: {error}')


def pisco_mensual(lat: float, lon: float):
    respuesta = get_json('POST', PISCO_URL, json={
        'start': '1998-01', 'end': '1998-12',
        'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
    })
    valores = pd.DataFrame(respuesta['data'])
    if not {'date', 'precipitation'}.issubset(valores.columns):
        raise ValueError('Respuesta PISCOp carece de date/precipitation')
    resultado = valores[['date', 'precipitation']].rename(
        columns={'date': 'mes', 'precipitation': 'estimado_mm'})
    resultado['estimado_mm'] = pd.to_numeric(resultado['estimado_mm'], errors='coerce')
    return validar_mensual(resultado, 'PISCOp')


def era5_mensual(lat: float, lon: float):
    datos = get_json('GET', ERA_URL, params={
        'latitude': lat, 'longitude': lon,
        'start_date': '1998-01-01', 'end_date': '1998-12-31',
        'daily': 'precipitation_sum', 'models': 'era5_seamless',
        'timezone': 'America/Lima', 'cell_selection': 'nearest',
    })
    diario = pd.DataFrame({
        'fecha': datos['daily']['time'],
        'estimado_mm': datos['daily']['precipitation_sum'],
    })
    diario['fecha'] = pd.to_datetime(diario['fecha'], errors='raise')
    diario['estimado_mm'] = pd.to_numeric(diario['estimado_mm'], errors='coerce')
    if (len(diario) != 365 or diario['fecha'].nunique() != 365
        or diario['estimado_mm'].isna().any()
        or (diario['estimado_mm'] < 0).any()):
        raise ValueError('ERA5 diario incompleto o invalido en 1998')
    diario['mes'] = diario['fecha'].dt.strftime('%Y-%m')
    resultado = diario.groupby('mes', as_index=False).estimado_mm.sum()
    return validar_mensual(resultado, 'ERA5-Seamless')


def validar_mensual(frame: pd.DataFrame, nombre: str):
    frame = frame.copy()
    frame['mes'] = frame['mes'].astype(str).str[:7]
    esperado = pd.period_range('1998-01', '1998-12', freq='M').astype(str).tolist()
    frame = frame.sort_values('mes').reset_index(drop=True)
    if (frame['mes'].tolist() != esperado
        or frame['estimado_mm'].isna().any()
        or (frame['estimado_mm'] < 0).any()):
        raise ValueError(f'Mensual {nombre}: meses faltantes/duplicados/invalidos')
    return frame


def metrica(observado: pd.Series, estimado: pd.Series, estacion: str, fuente: str):
    import numpy as np
    o, e = observado.to_numpy(dtype=float), estimado.to_numpy(dtype=float)
    d = e - o
    return {
        'estacion': estacion, 'producto': fuente, 'meses': len(o),
        'obs_1998_mm': round(float(o.sum()), 2),
        'estimado_1998_mm': round(float(e.sum()), 2),
        'sesgo_mensual_mm': round(float(d.mean()), 3),
        'mae_mensual_mm': round(float(np.abs(d).mean()), 3),
        'rmse_mensual_mm': round(float(np.sqrt(np.mean(d**2))), 3),
        'r_pearson_mensual': (round(float(np.corrcoef(o, e)[0,1]), 4)
                             if np.std(o) and np.std(e) else None),
    }


def main():
    observado = pd.read_csv(OBS)
    assert len(observado) == 60 and observado.estacion.nunique() == 5
    assert (observado.dias_validos == observado.dias_mes).all()
    assert set(observado.estacion) == set(STATIONS)
    esperado = pd.period_range('1998-01', '1998-12', freq='M').astype(str).tolist()
    for est, grupo in observado.groupby('estacion'):
        assert sorted(grupo.mes.tolist()) == esperado, est

    resultados = []
    comparaciones = []
    incidencias = []
    for estacion, (lat, lon, metadatos) in STATIONS.items():
        print(f'\nProcesando {estacion} @ {lat}, {lon} ({metadatos})', flush=True)
        obs = observado.loc[observado.estacion == estacion, ['mes','observado_mm']]
        for fuente, funcion in [('PISCOp v3.0', pisco_mensual),
                                ('ERA5-Seamless', era5_mensual)]:
            try:
                serie = funcion(lat, lon)
                unido = obs.merge(serie, on='mes', how='inner', validate='one_to_one')
                if len(unido) != 12:
                    raise ValueError('12 meses comunes requeridos')
                indicador = metrica(unido.observado_mm, unido.estimado_mm,
                                   estacion, fuente)
                resultados.append(indicador)
                unido.insert(0, 'estacion', estacion)
                unido.insert(1, 'producto', fuente)
                unido['diferencia_mm'] = (unido['estimado_mm'] - unido['observado_mm']).round(3)
                comparaciones.append(unido)
                print(f'  OK {fuente}: {indicador}', flush=True)
            except Exception as exc:
                incidencias.append({'estacion': estacion, 'producto': fuente,
                                   'error': f'{type(exc).__name__}: {str(exc)[:240]}'})
                print(f'  SIN RESULTADO {fuente}: {exc}', flush=True)

    OUT.mkdir(exist_ok=True, parents=True)
    if comparaciones:
        pd.concat(comparaciones, ignore_index=True).to_csv(
            OUT / 'comparacion_3n_1998.csv', index=False)
    else:
        (OUT / 'comparacion_3n_1998.csv').write_text(
            'estacion,producto,mes,observado_mm,estimado_mm,diferencia_mm\n', encoding='utf-8')
    pd.DataFrame(resultados,columns=['estacion','producto','meses','obs_1998_mm',
       'estimado_1998_mm','sesgo_mensual_mm','mae_mensual_mm',
       'rmse_mensual_mm','r_pearson_mensual']).to_csv(OUT / 'metricas_3n_1998.csv', index=False)
    (OUT / 'estado_3n_1998.json').write_text(json.dumps({
        'version': '3N.1998', 'n_comparaciones': len(resultados),
        'esperadas': 10, 'incidencias': incidencias,
        'coordenadas_preliminares': True,
        'exactitud_validada_independientemente': False,
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    lineas = [
      '# Fase 3N — Comparación de precipitación en estaciones de Lambayeque (1998)',
      '', '> **EXPLORATORIO.** Las coordenadas documentales son preliminares y su',
      '> correspondencia con emplazamientos históricos todavía requiere confirmación.',
      '> PISCOp puede haber integrado estas observaciones en la producción del',
      '> conjunto de datos; su contraste no equivale a validación independiente.',
      '', 'Se han comparado acumulados mensuales de 12 meses íntegros de 1998.',
      'Sesgo = estimado - observado. MAE/RMSE calculados sobre **meses**.',
      '', f'Comparaciones obtenidas: **{len(resultados)}/10**.', '',
      '| Estación | Producto | Observado anual (mm) | Estimado anual (mm) | Sesgo mensual (mm) | MAE mensual (mm) | RMSE mensual (mm) | r Pearson |',
      '|---|---|---:|---:|---:|---:|---:|---:|',
    ]
    for x in resultados:
        coef = 'no calculable' if x['r_pearson_mensual'] is None else str(x['r_pearson_mensual'])
        lineas.append(f"| {x['estacion']} | {x['producto']} | {x['obs_1998_mm']} | {x['estimado_1998_mm']} | {x['sesgo_mensual_mm']} | {x['mae_mensual_mm']} | {x['rmse_mensual_mm']} | {coef} |")
    if incidencias:
        lineas.extend(['','## Consultas sin resultado',''])
        for x in incidencias:
            lineas.append(f"- **{x['estacion']} – {x['producto']}**: {x['error']}")
    lineas.extend(['', '## Procedencia y advertencias',
        '- Observaciones: agregados mensuales calculados de cinco archivos TXT SENAMHI aportados al estudio.',
        '- PISCOp: servicio externo https://fluviotech.com/meteodata/pisco/api/docs/',
        '- ERA5-Seamless: https://open-meteo.com/en/docs/historical-weather-api',
        '- Los productos se extraen para las mismas coordenadas solicitadas, pero **sus celdas espaciales son diferentes**.',
        '- Los extremos climáticos no deben explicarse solo por una correlación; verificar cobertura, metodología y estación.',
        '- No considerar esta primera muestra de un año como demostración de precisión histórica general.',
        '- No extrapolar resultados observados a parcelas de arándano sin validación en campo.', '',
        '## Metadatos espaciales empleados', '',
        '| Estación | Latitud | Longitud | Procedencia preliminar |',
        '|---|---:|---:|---|',
    ])
    for nombre, (lat, lon, src) in STATIONS.items():
        lineas.append(f'| {nombre} | {lat} | {lon} | {src} |')
    (ROOT / 'VALIDACION_3N.md').write_text('\n'.join(lineas)+'\n', encoding='utf-8')
    print(f'\nFINAL: {len(resultados)} comparaciones, {len(incidencias)} incidencias.', flush=True)

if __name__ == '__main__':
    main()