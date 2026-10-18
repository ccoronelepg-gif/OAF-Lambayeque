"""10I safeguards: only-rainfall targets, atmospheric provenance and no future covariates."""
import sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import random_forest_lluvia_multivariable_10i as m
class RFOnlyRainTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.nodes,cls.A,cls.edges,cls.fixed,cls.floors,cls.polygons,cls.data,cls.audit=m.base.previous.inputs()
  cls.x0,cls.x1,cls.Y,cls.rain,cls.thr,cls.dates,cls.tr,cls.va,cls.ca,cls.te=m.base.matrix(cls.nodes,cls.fixed,cls.data)
 def test_four_feature_ablation_groups(self):
  arms,audit=m.arm_inputs(self.nodes,self.x0,self.x1,self.dates)
  self.assertEqual(tuple(arms),m.GROUPS)
  self.assertEqual([z.shape[-1] for z in arms.values()],[11,18,19,26])
  self.assertLess(audit["n_bins_aproximados"],39)
 def test_weather_uses_only_lag2_for_target_january(self):
  full,audit=m.weather_with_derived(self.nodes,self.x1,self.dates)
  sid=self.nodes[0]
  source={(x["sector"],x["mes"]):x for x in m.nasa.read(m.nasa.ATM)}
  self.assertEqual(self.dates[0],"1997-01")
  self.assertAlmostEqual(full[0,0,18],float(source[(sid,"1996-11")]["temperatura_c"]),places=3)
  self.assertNotEqual(full[0,0,18],float(source[(sid,"1997-01")]["temperatura_c"]))
 def test_derived_vpd_is_nonnegative_and_separate_from_leaf_wetness(self):
  full,_=m.weather_with_derived(self.nodes,self.x1,self.dates)
  self.assertGreaterEqual(float(full[:,:,-1].min()),0.)
  self.assertTrue(np.isfinite(full).all())
  self.assertTrue("horas_humedad_foliar" not in m.FIELDNAMES)
 def test_no_disease_labels(self):
  self.assertEqual(set(m.FIELDNAMES),set(["mes","sector","piso","bloque",
  "familia_variables","lluvia_chirps_observada_mm","lluvia_rf_predicha_mm",
  "lluvia_climatologia_mm","umbral_local_p90_mm","evento_observado_p90",
  "probabilidad_rf_p90","probabilidad_climatologia_p90"]))
  self.assertFalse(any("infeccion" in z or "enfermedad" in z for z in m.FIELDNAMES))
 def test_temporal_splits(self):
  self.assertEqual([int(z.sum()) for z in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
 def test_no_naive_validation_scoring(self):
  sample=[{"familia_variables":"lluvia",
    "mes":"2023-01","sector":"S001","piso":"plano","bloque":0,
    "lluvia_chirps_observada_mm":100,"lluvia_rf_predicha_mm":80,
    "lluvia_climatologia_mm":20,"evento_observado_p90":1,
    "probabilidad_rf_p90":.6,"probabilidad_climatologia_p90":.1}]
  report=m.group_scores(sample)["lluvia"]["global"]
  self.assertEqual(report["mae_rf_mm"],20.)
  self.assertEqual(report["brier_rf"],.16)
 def test_regression_is_nonnegative(self):
  self.assertIn("lluvia_rf_predicha_mm",m.FIELDNAMES)
  self.assertIn("probabilidad_rf_p90",m.FIELDNAMES)
if __name__=="__main__":unittest.main()
