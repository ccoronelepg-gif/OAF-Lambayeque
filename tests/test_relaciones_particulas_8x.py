"""Pruebas sintéticas de correlación PM: nunca causales."""
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'relaciones_particulas_8x.py'
spec=importlib.util.spec_from_file_location('rel8x',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Relations(unittest.TestCase):
    def test_full_correlation(self):
        self.assertAlmostEqual(m.pearson([1,2,3,4],[2,4,6,8]),1)
    def test_inverse(self):
        self.assertAlmostEqual(m.pearson([1,2,3],[6,4,2]),-1)
    def test_constant_no_declaration(self):
        self.assertIsNone(m.pearson([1,1,1],[2,3,4]))
    def test_months_gate(self):
        self.assertEqual(m.MIN_MONTHS,24)
    def test_not_sum_pm10_and_pm25(self):
        self.assertEqual(len(m.POLLUTANTS),2)
        self.assertNotEqual(m.POLLUTANTS[0],m.POLLUTANTS[1])
if __name__=='__main__':unittest.main()
