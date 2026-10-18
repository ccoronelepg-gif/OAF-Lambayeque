"""Fase 10E: guarantees lag2 eligibility, independent calibration and honest scope."""
import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import probabilidad_multivariable_10e as m
class Test10E(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.months,cls.series,cls.flags=m.get_data()
  cls.dates,cls.X,cls.Y,cls.rain,cls.bad,cls.thr,cls.mask,cls.cols=m.design(cls.months,cls.series)
 def test_four_localities_30_years(self):
  self.assertEqual(m.LOCALITIES,("Chiclayo","Jayanca","Motupe","Olmos"))
  self.assertEqual(self.X.shape[1],4)
  self.assertEqual(len(self.months),360)
  self.assertEqual(len(self.flags),11)
 def test_temporal_split_no_overlap(self):
  names=("entrenamiento","ajuste","calibracion","prueba")
  self.assertEqual([int(self.mask[k].sum()) for k in names],[228,36,24,60])
  self.assertTrue(all(np.count_nonzero(self.mask[a]&self.mask[b])==0
    for i,a in enumerate(names) for b in names[i+1:]))
 def test_rain_t_minus_one_excluded(self):
  s={k:list(v) for k,v in self.series.items()}
  s["Chiclayo"]=[dict(v) for v in s["Chiclayo"]]
  s["Chiclayo"][self.months.index("2005-04")]["rain"]+=3000
  changed=m.design(self.months,s)
  index=self.dates.index("2005-05")
  np.testing.assert_array_equal(self.X[index],changed[1][index])
  self.assertNotEqual(self.X[self.dates.index("2005-06"),0,0],changed[1][self.dates.index("2005-06"),0,0])
 def test_train_only_percentiles(self):
  s={k:list(v) for k,v in self.series.items()}
  s["Chiclayo"]=[dict(v) for v in s["Chiclayo"]]
  s["Chiclayo"][self.months.index("2023-04")]["rain"]+=500
  changed=m.design(self.months,s)
  np.testing.assert_array_equal(self.thr,changed[5])
 def test_features_include_climate_ocean_humidity(self):
  for item in ("radiacion_t2","temperatura_t2","viento_u_t2","viento_v_t2",
               "humedad_t2","vpd_t2","anomalia_nino12_t2","anomalia_nino34_t2","soi_t2","viento_marino_t2"):
   self.assertIn(item,self.cols)
  self.assertNotIn("corriente_geostrofica",self.cols)
 def test_brier_and_probabilities(self):
  score=m.score([0,1],[.1,.9])
  self.assertAlmostEqual(score["brier"],.01,places=6)
 def test_rare_threshold_calibration_fallback(self):
  p=np.full((10,4),.1)
  Y=np.zeros((10,4),dtype=np.float32)
  mask=np.array([True]*5+[False]*5)
  self.assertIsNotNone(m.decision_threshold(p,Y,mask))
if __name__=="__main__":unittest.main()
