"""OAF fase 10D: tests against temporal leakage, scoring and exploratory regime labels."""
import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import experimento_factorial_10d as m
class Tests10D(unittest.TestCase):
 def test_no_operational_claims(self):
  self.assertEqual(m.CUTS,(50,100,150))
  self.assertEqual(m.ARMS,("lag1","lag2"))
  self.assertEqual(m.core.CAL,("2019-01","2020-12"))
  self.assertEqual(m.core.VAL,("2016-01","2018-12"))
  self.assertEqual(m.core.TEST,("2021-01","2025-12"))
 def test_rates_confusion(self):
  r=m.rates([0,120,150,0],[80,110,20,10],100,100)
  self.assertEqual((r["tp"],r["fn"],r["fp"],r["tn"]),(1,1,0,2))
  self.assertEqual(r["sensibilidad_pct"],50.)
 def test_tune_disallows_low_event_count(self):
  cal=[{"observado_mm":101. if k<3 else 0.,"estimado_mm":99.} for k in range(24)]
  r=m.tune(cal,100)
  self.assertEqual(r["estado"],"INSUFICIENTES_EVENTOS_CALIBRACION")
  self.assertIsNone(r["umbral_predicho_mm"])
 def test_tuning_uses_only_given_calibration(self):
  cal=[{"observado_mm":100. if k<12 else 0.,"estimado_mm":99. if k<12 else 1.} for k in range(24)]
  r=m.tune(cal,100)
  self.assertEqual(r["estado"],"CALIBRADA_EXPLORATORIA")
  self.assertLessEqual(r["fpr_calibracion_pct"],25.)
 def test_no_division_by_zero(self):
  r=m.rates([0,0],[0,0],100,100)
  self.assertEqual(r["eventos"],0)
  self.assertIsNone(r["sensibilidad_pct"])
 def test_regime_complete_and_not_enso_costero(self):
  r=m.regimes()
  self.assertEqual(len(r),60)
  self.assertEqual(r["2023-10"],"RONI_calido_geq_0.5")
  self.assertEqual(r["2023-01"],"RONI_frio_leq_-0.5")
 def test_metric_sign(self):
  r=m.stats([{"observado_mm":10,"estimado_mm":5},{"observado_mm":10,"estimado_mm":9}])
  self.assertEqual(r["sesgo_mm"],-3.)
  self.assertEqual(r["mae_mm"],3.)
 def test_split_original_features(self):
  import numpy as np
  nodes=[f"S{k:03}" for k in range(39)]
  dates=[f"{y}-{month:02d}" for y in range(1996,2026) for month in range(1,13)]
  data={sid:{mo:1. for mo in dates} for sid in nodes}
  fixed=np.zeros((39,3),dtype=np.float32)
  x1,y1,months1,tr1,va1,te1=m.lag1.features_matrix(nodes,fixed,data)
  x2,y2,months2,tr,va,cal,te=m.core.features_matrix(nodes,fixed,data)
  self.assertTrue(np.array_equal(y1,y2))
  self.assertTrue(np.array_equal(months1,months2))
  self.assertEqual((int(tr.sum()),int(va.sum()),int(cal.sum()),int(te.sum())),(228,36,24,60))
  self.assertEqual(x1.shape,x2.shape)
  d={sid:dict(v) for sid,v in data.items()}
  d[nodes[0]]["2005-04"]=200.
  original=m.core.features_matrix(nodes,fixed,data)[0]
  revised=m.core.features_matrix(nodes,fixed,d)[0]
  idx=list(months2).index("2005-05")
  np.testing.assert_array_equal(original[idx],revised[idx])
if __name__=="__main__":unittest.main()
