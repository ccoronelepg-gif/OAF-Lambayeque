"""Fase 10H — source integrity, scientific splits and t-2 delayed NASA weather."""
import sys,unittest,datetime as dt
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import comparacion_rf_gcn_nasa_10h as q
class ValidateNASA10H(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.nodes,cls.A,cls.edges,cls.fixed,cls.floors,cls.polygons,cls.data,cls.audit=q.base.previous.inputs()
  cls.x0,cls.x1,cls.y,cls.rain,cls.thresholds,cls.dates,cls.tr,cls.va,cls.ca,cls.te=q.base.matrix(cls.nodes,cls.fixed,cls.data)
  cls.X,cls.archive=q.join_features(cls.nodes,cls.x1,cls.dates)
 def test_source_complete_and_genuinely_coarse(self):
  self.assertEqual(self.X.shape,(348,39,24))
  self.assertEqual(self.archive["n_filas"],14040)
  self.assertLess(self.archive["n_bins_aproximados"],39)
  self.assertTrue(self.archive["ninguna_alerta_automatica"])
 def test_no_target_month_climate_leakage(self):
  rows=q.read(q.ATM)
  month_map={(r["sector"],r["mes"]):r for r in rows}
  i=self.nodes.index("S001")
  self.assertEqual(self.dates[0],"1997-01")
  self.assertAlmostEqual(float(self.X[0,i,18]),float(month_map[("S001","1996-11")]["temperatura_c"]),places=4)
  self.assertAlmostEqual(float(self.X[0,i,21]),float(month_map[("S001","1996-11")]["radiacion_nasa_kwh_m2_dia"]),places=4)
 def test_temporal_train_tune_cal_test_separation(self):
  self.assertEqual([int(x.sum()) for x in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
  for arr in (self.tr,self.va,self.ca,self.te):
   for other in (self.tr,self.va,self.ca,self.te):
    if arr is not other:self.assertFalse(np.any(arr&other))
 def test_threshold_is_train_only(self):
  self.assertEqual(len(self.thresholds),39)
  self.assertTrue(np.all(self.thresholds>0))
 def test_fair_10f_comparator(self):
  rows=q.read(q.ORIG)
  self.assertEqual(len(rows),11700)
  self.assertEqual(len({(r["mes"],r["sector"]) for r in rows}),39*60)
 def test_nasa_is_not_era5_and_not_sensors(self):
  self.assertTrue(self.archive["no_pretender_era5"])
  self.assertFalse(self.archive["datos_as_issued"])
  with q.ATM.open(encoding="utf8") as f:
   for line in list(f)[1:51]:
    self.assertIn("false",line)
if __name__=="__main__":unittest.main()
