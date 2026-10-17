"""Pruebas exclusivamente con series sintéticas, NO datos observados."""
import calendar
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]/'modelos'/'integracion_oceano_atmosfera_8v.py'
spec = importlib.util.spec_from_file_location('integracion_8v', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def write_rows(root, name, rows):
    path = root/m.SOURCES[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        wind, climate, sst, current = [], [], [], []
        for month in m.MONTHS:
            y, mm = map(int, month.split('-'))
            n = calendar.monthrange(y, mm)[1]
            sst.append(dict(mes=month, tsm_nino12_c=24, anomalia_tsm_nino12_c=mm,
                            tsm_nino34_c=27, anomalia_tsm_nino34_c=mm/10,
                            region_cuadrante_no_punto='true', vintage_historica_verificada='false'))
            for site in m.SITES_LAND + m.SITES_SEA:
                marine = site in m.SITES_SEA
                wind.append(dict(mes=month, sitio=site,
                                 ambiente='mar_abierto_muestreo' if marine else 'tierra_referencia',
                                 celda_era5_lat=-6.5, celda_era5_lon=-80.5,
                                 velocidad_media_10m_m_s=3, velocidad_maxima_diaria_media_m_s=4,
                                 componente_este_aprox_m_s=-2, componente_norte_aprox_m_s=1,
                                 dias_validos=n, observacion_instrumental='false'))
                if not marine:
                    climate.append(dict(localidad=site, mes=month, temperatura_c=24,
                                        precipitacion_mm=mm, radiacion_mj_m2=500))
            if y >= 2017:
                for point in m.SEA_TO_CURRENT.values():
                    current.append(dict(mes=month, punto=point, latitude=-6.5, longitude=-81,
                                        u_este_geostrofica_m_s=0.1, v_norte_geostrofica_m_s=-0.1,
                                        magnitud_vector_media_m_s=0.14,
                                        dias_con_dato=n, dias_calendario=n,
                                        modelo_geostrofico_no_corriente_total='true',
                                        observacion_directa_campo='false'))
        self.rows = {'viento': wind, 'clima': climate, 'sst': sst, 'corriente': current}
        self.save()

    def save(self):
        for key, data in self.rows.items():
            write_rows(self.root, key, data)

    def test_integracion_reproducible_y_lags(self):
        d = m.build(self.root)
        self.assertEqual((d['filas_matriz_terrestre'],d['filas_matriz_marina']), (1440,720))
        self.assertEqual(d['meses_corriente_geostrofica_integrados'], 216)
        self.assertEqual(d['meses_sin_corriente_geostrofica'], 504)
        m.build(self.root, check=True)
        with (self.root/m.DEST/m.LAND_FILE).open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]['anomalia_nino12_t_m1_c'], '')
        self.assertEqual(rows[1]['anomalia_nino12_t_m1_c'], '1.0')
        self.assertEqual(rows[2]['anomalia_nino12_t_m2_c'], '1.0')
        with (self.root/m.DEST/m.SEA_FILE).open() as f:
            sea = list(csv.DictReader(f))
        self.assertEqual(sea[0]['corriente_geostrofica_u_m_s'], '')
        self.assertEqual(sea[21*12]['corriente_geostrofica_u_m_s'], '0.1')

    def test_falta_mes_climatico(self):
        self.rows['clima'].pop(0)
        self.save()
        with self.assertRaisesRegex(ValueError, 'Clima: 1 faltantes'):
            m.build(self.root)

    def test_mes_viento_incompleto(self):
        self.rows['viento'][0]['dias_validos'] = 20
        self.save()
        with self.assertRaisesRegex(ValueError, 'dias_validos'):
            m.build(self.root)

    def test_corriente_faltante_no_imputada(self):
        self.rows['corriente'].pop(0)
        self.save()
        self.assertEqual(m.build(self.root)['meses_corriente_geostrofica_integrados'], 215)

    def test_indice_noaa_duplicado(self):
        self.rows['sst'].append(self.rows['sst'][0].copy())
        self.save()
        with self.assertRaisesRegex(ValueError, 'duplicada'):
            m.build(self.root)

    def test_mes_corriente_incompleto_no_se_usa(self):
        self.rows['corriente'][0]['dias_con_dato'] = 17
        self.save()
        self.assertEqual(m.build(self.root)['meses_corriente_geostrofica_integrados'], 215)

if __name__ == '__main__':
    unittest.main()
