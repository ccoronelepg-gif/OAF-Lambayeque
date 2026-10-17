"""Pruebas sintéticas de conversion NASA, no MERRA-2 descargado."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'piloto_merra2_pm_8z.py'
sp=importlib.util.spec_from_file_location('m2',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class TestMERRA2(unittest.TestCase):
    def test_pm25_nasa_gmao_dry_formula(self):
        x={'DUSMASS25':2e-9,'OCSMASS':3e-9,'BCSMASS':1e-9,
           'SSSMASS25':4e-9,'SO4SMASS':5e-9}
        expected=2+3+1+4+5*(132.14/96.06)
        self.assertAlmostEqual(m.pm25_surface_ug_m3(x),expected)

    def test_pm10_3d_lowest_model_level_with_density(self):
        x={k:1e-9 for k in ('SO4','BCphobic','BCphilic','OCphobic','OCphilic',
                            'DU001','DU002','DU003','DU004',
                            'SS001','SS002','SS003','SS004')}
        x['AIRDENS']=1.2
        expected=(1.375+4+3+.74+4)*1.2
        self.assertAlmostEqual(m.pm10_lowest_layer_ug_m3(x),expected)

    def test_pm10_rejects_wrong_2d_fields(self):
        x={'DUSMASS25':1e-9,'OCSMASS':1e-9,'BCSMASS':1e-9,
           'SSSMASS25':1e-9,'SO4SMASS':1e-9}
        with self.assertRaisesRegex(ValueError,'Falta componente'):
            m.pm10_lowest_layer_ug_m3(x)

    def test_negative_invalid(self):
        x={'DUSMASS25':-1e-9,'OCSMASS':3e-9,'BCSMASS':1e-9,
           'SSSMASS25':4e-9,'SO4SMASS':5e-9}
        with self.assertRaises(ValueError):m.pm25_surface_ug_m3(x)

    def test_m2_metadata_not_pm_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=m.main(tmp,False)
            self.assertFalse(d['serie_merra2_pm_mensual_archivada'])
            self.assertFalse(d['colecciones_1996_2025_descargadas_en_oaf'])
            self.assertTrue(d['metadatos_CMR_no_equivalen_a_valores_PM'])
            self.assertEqual(d['capa_pm10_3d_numero'],72)

    def test_catalog_only_nasa_links(self):
        url=m.cmr_query(m.COLLECTION_AER,'1998-03-15')
        self.assertTrue(url.startswith('https://cmr.earthdata.nasa.gov/'))
        self.assertIn('1998-03-15',url)

if __name__=='__main__':unittest.main()
