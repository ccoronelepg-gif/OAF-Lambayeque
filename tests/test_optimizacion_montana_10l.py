"""10L: high-altitude model safeguards, explicit spatial and validation periods."""
import sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import optimizacion_montana_rf_10l as m
class T10L(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.geo,cls.lookup,cls.floor=m.eco.catalog()
  cls.nodes,cls.A,cls.edges,cls.fixed,cls.legacy_floor,cls.polygons,cls.data,_=m.base.previous.inputs()
  cls.X0,cls.X1,cls.Y,cls.rain,cls.threshold,cls.dates,cls.tr,cls.va,cls.ca,cls.te=m.base.matrix(cls.nodes,cls.fixed,cls.data)
 def test_eleven_sectors_in_target_altitude_strata(self):
  mountain=[s for s in self.nodes if self.lookup[s] in m.TARGET]
  self.assertEqual(len(mountain),11)
  self.assertEqual(sum(self.lookup[s]=="ladera_media" for s in mountain),8)
  self.assertEqual(sum(self.lookup[s]=="cumbres" for s in mountain),3)
 def test_no_diseases_or_current_alerts(self):
  self.assertNotIn("infeccion",m.FIELD)
  self.assertIn("nuevo_rf_mm",m.FIELD)
  self.assertIn("intervalo_inf_90_mm",m.FIELD)
 def test_lagged_input_has_fixed_extra_climatology(self):
  ref=m.rain.normal(self.rain,self.tr,self.dates)
  fn=m.alt_features(self.nodes,self.geo,ref,self.rain,self.tr,self.dates)
  self.assertEqual(fn.shape,(348,39,5))
  self.assertTrue(np.isfinite(fn).all())
 def test_orography_does_not_use_new_rainfall_labels(self):
  old=m.rain.normal(self.rain,self.tr,self.dates)
  altered=self.rain.copy();altered[self.te]+=123456
  ref=m.rain.normal(altered,self.tr,self.dates)
  a=m.alt_features(self.nodes,self.geo,old,self.rain,self.tr,self.dates)
  b=m.alt_features(self.nodes,self.geo,ref,altered,self.tr,self.dates)
  self.assertTrue(np.allclose(a,b))
 def test_regression_can_fall_back_on_climatology(self):
  c=np.array([10.,80.]);v=np.array([.5,1.])
  self.assertTrue(np.allclose(m.predict(c,v,"normalized",0),c))
  self.assertTrue(np.allclose(m.predict(c,v,"log",0),c))
 def test_shrinkage_choice_without_test(self):
  c=np.array([10.,10.,10.,10.,10.,10.])
  y=np.array([11.,10.,10.,10.,9.,10.])
  raw=np.full(6,10.)
  mask=np.ones(6,bool)
  score,weight=m.sel_mae(y,c,raw,"normalized",mask)
  self.assertEqual(weight,0.)
 def test_bounds_and_no_negative_rainfall(self):
  c=np.array([10,100],float)
  v=np.array([-100,100],float)
  self.assertTrue(np.all(m.predict(c,v,"log",1)>=0))
  self.assertTrue(np.all(m.predict(c,v,"normalized",1)>=0))
 def test_train_tune_cal_test_separated(self):
  self.assertEqual([int(a.sum()) for a in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
  self.assertTrue(all(np.array_equal(self.tr&a,np.zeros(len(a),bool)) for a in (self.va,self.ca,self.te)))
if __name__=="__main__":unittest.main()
