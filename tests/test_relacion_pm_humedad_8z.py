"""Pruebas sintéticas del solapamiento PM y humedad, sin pruebas causales."""
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'relacion_pm_humedad_8z.py'
sp=importlib.util.spec_from_file_location('rhpm8z',P)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class TestRHPM(unittest.TestCase):
    def test_positive(self):
        self.assertAlmostEqual(m.pearson([(i,i*2) for i in range(36)]),1)
    def test_negative(self):
        self.assertAlmostEqual(m.pearson([(i,36-i) for i in range(36)]),-1)
    def test_two_years_min(self):
        self.assertIsNone(m.pearson([(i,i) for i in range(12)]))
        self.assertAlmostEqual(m.pearson([(i,i) for i in range(24)]),1)
    def test_seasonal_removed(self):
        data=[(f'{y}-{mth:02d}',mth,mth*3) for y in (2023,2024,2025)
              for mth in range(1,13)]
        self.assertIsNone(m.pearson(m.residuals(data)))
    def test_units_and_names_distinct(self):
        self.assertIn('pm10_media_ug_m3',m.PARTICLES)
        self.assertIn('vpd_max_diario_media_mes_kpa',m.COVARIATES)
        self.assertNotIn('humedad_de_hoja',m.COVARIATES)

if __name__=='__main__':unittest.main()
