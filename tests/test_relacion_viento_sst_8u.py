"""8U: quality tests for historical wind–SST descriptive comparison."""
import importlib.util,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("win8u",ROOT/"modelos/relacion_viento_sst_8u.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class WindSSTTests(unittest.TestCase):
 def test_month_lag_correct_cross_year(self):
  self.assertEqual(mod.lag("2020-01"),"2019-11")
  self.assertEqual(mod.lag("2016-02"),"2015-12")
 def test_pearson_direction(self):
  self.assertAlmostEqual(mod.pearson(list(range(50)),list(range(50))),1)
  self.assertAlmostEqual(mod.pearson(list(range(50)),list(reversed(range(50)))),-1)
 def test_cannot_correlate_small_series(self):
  with self.assertRaises(ValueError):mod.pearson([2,3],[1,2])
 def test_summary_does_not_claim_forecast(self):
  s,rows=mod.study(ROOT)
  self.assertEqual(len(rows),4)
  self.assertFalse(s["correlaciones_no_son_pronosticos"] is False)
  self.assertTrue(s["corrientes_marinas_no_estimadas_en_cruce"])
  for row in rows:
   self.assertGreaterEqual(row["n_meses_emparejados"],358)
   for name in ("correlacion_anomalia_viento_sst_nino12_rezago_2",
     "correlacion_anomalia_zonal_sst_nino12_rezago_2",
     "correlacion_anomalia_meridional_sst_nino12_rezago_2"):
    self.assertLessEqual(abs(row[name]),1)
if __name__=="__main__":unittest.main()
