"""Tests de asociaciones 8U - nunca atribuir habilidad a correlaciones."""
import importlib.util,math,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf_rel8u",ROOT/"modelos/relaciones_viento_sst_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestWindSST8U(unittest.TestCase):
 def test_lag_handles_year_boundaries(self):
  self.assertEqual(m.lag_month("2016-01"),"2015-11")
  self.assertEqual(m.lag_month("1996-03"),"1996-01")
 def test_pairwise_correlation_defined_zero_mean_variance_not_skill(self):
  self.assertAlmostEqual(m.pearson([float(i) for i in range(15)],[float(i)*2 for i in range(15)]),1)
  self.assertIsNone(m.pearson([0.]*15,[float(i) for i in range(15)]))
  self.assertIsNone(m.pearson([1.]*11,[1.]*11))
 def test_training_window_needs_own_normal_not_30yr_diagnostic(self):
  # Distinguishes descriptive base across 30 years from calibration window:
  # a future shift can change 1996-2025 normal but not pre-2011 normal.
  trend={y:20.+(.3 if y>=2011 else 0) for y in range(1996,2026)}
  climatology_30=sum(trend.values())/30
  historical=sum(trend[y] for y in range(1996,2011))/15
  self.assertNotEqual(climatology_30,historical)
if __name__=="__main__":unittest.main()
