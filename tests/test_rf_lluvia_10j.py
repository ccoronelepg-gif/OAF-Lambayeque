"""10J regression and intense-rain safeguards; no infection prediction."""
import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import rf_lluvia_extremos_10j as m

class Audit10J(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  nodes,A,edges,fixed,floors,polygons,data,audit=m.base.previous.inputs()
  cls.nodes=nodes
  x0,x1,y,raw,thr,dates,tr,va,ca,te=m.base.matrix(nodes,fixed,data)
  cls.x0=x0;cls.x1=x1;cls.raw=raw;cls.dates=dates;cls.tr=tr;cls.va=va;cls.ca=ca;cls.te=te
 def test_no_infection_outputs(self):
  self.assertTrue(all("enfermedad" not in x and "infeccion" not in x for x in m.OUT_FIELDS))
  self.assertIn("lluvia_predicha_rf_mm",m.OUT_FIELDS)
  self.assertIn("probabilidad_rf_p95",m.OUT_FIELDS)
 def test_source_39_with_four_feature_families(self):
  arms,audit=m.previous.arm_inputs(self.nodes,self.x0,self.x1,self.dates)
  self.assertEqual(tuple(arms),m.ARMS)
  self.assertEqual({k:a.shape[-1] for k,a in arms.items()},
    {"lluvia":11,"lluvia_oceano":18,"lluvia_atmosfera":19,"lluvia_oceano_atmosfera":26})
  self.assertLess(audit["n_bins_aproximados"],39)
 def test_train_only_thresholds(self):
  p90=np.quantile(self.raw[self.tr],.90,axis=0)
  p95=np.quantile(self.raw[self.tr],.95,axis=0)
  self.assertTrue(np.all(p95>=p90))
  self.assertTrue(np.all(p90>0))
 def test_prob_shrinks_to_baseline_when_validation_prefers(self):
  normal=np.array([[.1],[.1],[.1],[.1]],dtype=float)
  model=np.array([[.9],[.9],[.9],[.9]],dtype=float)
  y=np.array([[0],[0],[0],[0]],dtype=float)
  val=np.array([True,True,True,True])
  w,_=m.choose_weight(normal,model,y,val,"event")
  self.assertEqual(w,0)
  self.assertEqual(float(m.blend_probability(normal,model,w)[0,0]),.1)
 def test_monthly_climatology_from_train_only(self):
  normal=m.normal(self.raw,self.tr,self.dates)
  self.assertEqual(normal.shape,(348,39))
  idx=0
  test_month=np.flatnonzero(self.te)[0]
  predicted=normal[test_month,idx]
  altered=self.raw.copy()
  altered[self.te]=altered[self.te]+100000.
  self.assertAlmostEqual(predicted,m.normal(altered,self.tr,self.dates)[test_month,idx])
 def test_splits_and_order(self):
  self.assertEqual([int(x.sum()) for x in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
  self.assertEqual(self.dates[0],"1997-01")
  self.assertEqual(self.dates[-1],"2025-12")
 def test_finite_sample_calibration(self):
  q=m.finite_interval([1,2,3,4,5,6,7,8,9,10],.9)
  self.assertEqual(q,10.)
 def test_full_month_probability_not_hourly(self):
  self.assertTrue(all("hora" not in field and "foliar" not in field for field in m.OUT_FIELDS))
  self.assertTrue(all(-1<=w<=1 for w in m.WEIGHTS))
if __name__=="__main__":unittest.main()
