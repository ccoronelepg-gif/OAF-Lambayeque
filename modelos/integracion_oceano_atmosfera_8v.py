#!/usr/bin/env python3
"""OAF 8V. Matrices de investigación 1996–2025 de fuentes ya archivadas.
No imputa, descarga, pronostica, ni considera NOAA Niño1+2 SST de playa/ICEN.
"""
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
from pathlib import Path

START, END = '1996-01', '2025-12'
SITES_LAND = ('Chiclayo', 'Jayanca', 'Motupe', 'Olmos')
SITES_SEA = ('Mar_frente_Pimentel', 'Mar_norte_Lambayeque')
SEA_TO_CURRENT = {'Mar_frente_Pimentel': 'Aguas_frente_Pimentel',
                  'Mar_norte_Lambayeque': 'Aguas_norte_Lambayeque'}
SOURCES = {
    'viento': 'datos/meteorologia_8u/vientos_mensuales_8u.csv',
    'sst': 'datos/oceanografia_8u/tsm_nino12_mensual_8u.csv',
    'corriente': 'datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv',
    'clima': 'datos/lambayeque_mensual_era5_8d.csv',
}
DEST = 'datos/integracion_8v'
LAND_FILE = 'matriz_terrestre_8v.csv'
SEA_FILE = 'matriz_marina_8v.csv'
STATUS_FILE = 'estado_integracion_8v.json'
MONTHS = tuple(f'{y}-{m:02d}' for y in range(1996, 2026) for m in range(1, 13))

def month_shift(month, lag):
    y, m = map(int, month.split('-'))
    ix = y * 12 + m - 1 - lag
    return f'{ix // 12:04d}-{ix % 12 + 1:02d}'

def finite(row, field, low=None, high=None):
    try:
        v = float(row[field])
    except (KeyError, ValueError, TypeError):
        raise ValueError(f'No numérico: {field} en {row!r}') from None
    if not math.isfinite(v) or (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f'Fuera de rango: {field}={v}')
    return v

def read_source(root, name):
    path = root / SOURCES[name]
    if not path.exists():
        if name == 'corriente':
            return [], None
        raise FileNotFoundError(f'Falta fuente obligatoria {path}')
    raw = path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if not rows:
        raise ValueError(f'Fuente vacía: {path}')
    return rows, hashlib.sha256(raw).hexdigest()

def keyed(rows, fields, name):
    out = {}
    for row in rows:
        if row.get('mes') not in MONTHS:
            continue
        key = tuple(row.get(field) for field in fields)
        if any(not x for x in key):
            raise ValueError(f'{name}: clave incompleta')
        if key in out:
            raise ValueError(f'{name}: clave duplicada {key}')
        out[key] = row
    return out

def strict_calendar(index, sites, name):
    target = {(site, mon) for site in sites for mon in MONTHS}
    if set(index) != target:
        raise ValueError(f'{name}: {len(target-set(index))} faltantes y {len(set(index)-target)} extra')

def month_days(row, field, month):
    year, mo = map(int, month.split('-'))
    n = calendar.monthrange(year, mo)[1]
    return int(finite(row, field, n, n))

def wind_features(row, month, medium):
    if row.get('ambiente') != medium or row.get('observacion_instrumental', '').lower() != 'false':
        raise ValueError(f'Trazabilidad del viento inválida: {row}')
    month_days(row, 'dias_validos', month)
    return {
        'viento_10m_m_s': finite(row, 'velocidad_media_10m_m_s', 0, 70),
        'viento_10m_max_media_m_s': finite(row, 'velocidad_maxima_diaria_media_m_s', 0, 100),
        'viento_u_aprox_m_s': finite(row, 'componente_este_aprox_m_s', -70, 70),
        'viento_v_aprox_m_s': finite(row, 'componente_norte_aprox_m_s', -70, 70),
        'celda_viento_lat': finite(row, 'celda_era5_lat', -20, 2),
        'celda_viento_lon': finite(row, 'celda_era5_lon', -95, -70),
    }

def sst_features(row):
    if row.get('region_cuadrante_no_punto', '').lower() != 'true':
        raise ValueError('El índice NOAA regional no es SST de punto costero')
    return {
        'tsm_nino12_c': finite(row, 'tsm_nino12_c', 12, 40),
        'anomalia_nino12_c': finite(row, 'anomalia_tsm_nino12_c', -15, 15),
        'tsm_nino34_c': finite(row, 'tsm_nino34_c', 15, 40),
        'anomalia_nino34_c': finite(row, 'anomalia_tsm_nino34_c', -15, 15),
    }

def climate_features(row):
    return {
        'temperatura_aire_c': finite(row, 'temperatura_c', -15, 50),
        'precipitacion_mes_mm': finite(row, 'precipitacion_mm', 0, 10000),
        'lluvia_modelada_ge_1000_mm_revisar': finite(row, 'precipitacion_mm', 0, 10000) >= 1000,
        'radiacion_mes_mj_m2': finite(row, 'radiacion_mj_m2', 0, 2000),
    }

def current_features(row, month):
    if row.get('modelo_geostrofico_no_corriente_total', '').lower() != 'true' or row.get('observacion_directa_campo', '').lower() != 'false':
        raise ValueError('La fuente debe ser corriente geostrófica, no corriente total')
    year, mo = map(int, month.split('-'))
    n = calendar.monthrange(year, mo)[1]
    days = int(finite(row, 'dias_con_dato', 0, n))
    month_days(row, 'dias_calendario', month)
    if days != n:
        return None
    return {
        'corriente_geostrofica_u_m_s': finite(row, 'u_este_geostrofica_m_s', -4, 4),
        'corriente_geostrofica_v_m_s': finite(row, 'v_norte_geostrofica_m_s', -4, 4),
        'corriente_geostrofica_vector_m_s': finite(row, 'magnitud_vector_media_m_s', 0, 4),
    }

def to_csv(rows):
    out = io.StringIO(newline='')
    fields = list(rows[0])
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({f: ('' if row.get(f) is None else row.get(f)) for f in fields})
    return out.getvalue().encode('utf-8')

def build(root, check=False):
    root = Path(root)
    data, shas = {}, {}
    for source in SOURCES:
        data[source], shas[source] = read_source(root, source)
    wind = keyed(data['viento'], ('sitio', 'mes'), 'ERA5')
    sst = keyed(data['sst'], ('mes',), 'NOAA')
    climate = keyed(data['clima'], ('localidad', 'mes'), 'Clima')
    current = keyed(data['corriente'], ('punto', 'mes'), 'Corriente')
    strict_calendar(wind, SITES_LAND + SITES_SEA, 'Viento')
    strict_calendar(climate, SITES_LAND, 'Clima')
    if set(sst) != {(x,) for x in MONTHS}:
        raise ValueError('Índices NOAA incompletos o fuera de periodo')
    if any(p not in SEA_TO_CURRENT.values() or month < '2017-01' for p, month in current):
        raise ValueError('Corrientes fuera del ámbito histórico 8V')
    land, sea = [], []
    n_current = 0
    for site in SITES_LAND:
        for mon in MONTHS:
            x = {
                'mes': mon, 'localidad': site,
                **climate_features(climate[(site, mon)]),
                **wind_features(wind[(site, mon)], mon, 'tierra_referencia'),
                **sst_features(sst[(mon,)]),
            }
            for lag in (1, 2, 3):
                prev = sst.get((month_shift(mon, lag),))
                x[f'anomalia_nino12_t_m{lag}_c'] = sst_features(prev)['anomalia_nino12_c'] if prev else ''
            x.update({
                'origen_clima': 'ERA5-Land temperatura; ERA5 lluvia/radiacion (Open-Meteo)',
                'origen_viento': 'ERA5 10m via Open-Meteo',
                'origen_oceano': 'NOAA CPC SSTOI indices revisados',
            })
            land.append(x)
    for site in SITES_SEA:
        for mon in MONTHS:
            point = SEA_TO_CURRENT[site]
            candidate = current.get((point, mon))
            c = current_features(candidate, mon) if candidate else None
            n_current += int(c is not None)
            sea.append({
                'mes': mon, 'punto_viento': site, 'punto_corriente': point,
                **wind_features(wind[(site, mon)], mon, 'mar_abierto_muestreo'),
                **sst_features(sst[(mon,)]),
                'corriente_2017_2025_disponible': bool(c),
                'malla_viento_corriente_no_colocalizada': True,
                'corriente_geostrofica_u_m_s': c['corriente_geostrofica_u_m_s'] if c else '',
                'corriente_geostrofica_v_m_s': c['corriente_geostrofica_v_m_s'] if c else '',
                'corriente_geostrofica_vector_m_s': c['corriente_geostrofica_vector_m_s'] if c else '',
                'fuente_corriente': 'NOAA/AOML geostrofica; NO corriente total' if c else '',
                'fuente_viento': 'ERA5 via Open-Meteo (rejilla marina de ensayo)',
                'fuente_sst': 'NOAA CPC regional Niño1+2/Niño3.4 (NO costa)',
            })
    if len(land) != 1440 or len(sea) != 720:
        raise AssertionError('Filas inesperadas')
    outputs = {LAND_FILE: to_csv(land), SEA_FILE: to_csv(sea)}
    status = {
        'fase': '8V', 'estado': 'matrices_retrospectivas_integradas_no_predictivas',
        'periodo': '1996-01/2025-12',
        'meses_esperados_por_ubicacion': 360,
        'localidades_terrestres': list(SITES_LAND),
        'puntos_de_viento_marino_no_validados_in_situ': list(SITES_SEA),
        'filas_matriz_terrestre': len(land),
        'meses_sitio_lluvia_modelada_ge_1000_mm_revision': sum(x['lluvia_modelada_ge_1000_mm_revisar'] for x in land),
        'registro_max_lluvia_modelada': {k: v for k, v in max(land, key=lambda x: x['precipitacion_mes_mm']).items() if k in ('mes','localidad','precipitacion_mes_mm')},
        'filas_matriz_marina': len(sea),
        'meses_corriente_geostrofica_integrados': n_current,
        'meses_sin_corriente_geostrofica': len(sea)-n_current,
        'meses_corriente_geostrofica_maximos_2017_2025': 216,
        'corrientes_marinas_30_anios_completas': False,
        'viento_es_modelo_no_estacion': True,
        'lluvia_y_temperatura_son_reanalisis_no_estacion': True,
        'indices_noaa_no_son_sst_costera_ni_icen': True,
        'no_son_vintages_historicas_fecha_emision': True,
        'no_hay_validacion_prospectiva_de_prediccion': True,
        'no_hay_alerta_fitosanitaria_derivada': True,
        'sin_imputacion_de_datos_faltantes': True,
        'climatologia_1996_2025_solo_para_descripcion_no_entrenamiento': True,
        'rutas_y_sha256_fuente_csv': {SOURCES[k]: shas[k] for k in SOURCES},
        'rutas_y_sha256_salidas': {n: hashlib.sha256(v).hexdigest() for n, v in outputs.items()},
        'limitaciones': [
            'Rejillas de viento y corrientes no colocalizadas',
            'Reanalisis no son estaciones instrumentales',
            'Corrientes geostroficas solo 2017-2025; no corriente total',
            'NOAA indices revisados ex post; sin vintage por fecha de emision',
            'Sin validacion externa, causal o prospectiva',
        ],
    }
    outputs[STATUS_FILE] = (json.dumps(status, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    output_dir = root / DEST
    if check:
        for file_name, payload in outputs.items():
            file = output_dir / file_name
            if not file.exists() or file.read_bytes() != payload:
                raise AssertionError(f'Salida desactualizada: {file}')
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        for file_name, payload in outputs.items():
            (output_dir / file_name).write_bytes(payload)
    return status

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--check', action='store_true')
    opt = parser.parse_args()
    print(json.dumps(build(opt.root, opt.check), ensure_ascii=False, indent=2))
