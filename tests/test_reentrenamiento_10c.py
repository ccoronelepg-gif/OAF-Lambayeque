"""10C: verifies calendar split and strict exclusion of t-1 precipitation from features."""
import sys,unittest
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import reentrenamiento_lag2_10c as m
class Tests10C(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.nodes=[f"S{i:03}" for i in range(39)]
  cls.dates=[f"{y}-{mo:02d}" for y in range(1996,2026) for mo in range(1,13)]
  cls.data={s:{date:1. for date in cls.dates} for s in cls.nodes}
  cls.fixed=np.zeros((39,3),dtype=np.float32)
 def features(self,data):return m.features_matrix(self.nodes,self.fixed,data)
 def test_partition_counts(self):
  x,y,dates,tr,va,ca,te=self.features(self.data)
  self.assertEqual((int(tr.sum()),int(va.sum()),int(ca.sum()),int(te.sum())),(228,36,24,60))
  self.assertFalse(np.any(tr&va | tr&ca | tr&te | va&ca | va&te | ca&te))
 def test_tminus1_is_excluded(self):
  orig=self.features(self.data)
  data={s:dict(v) for s,v in self.data.items()}
  data[self.nodes[0]]["2005-04"]=500.
  revised=self.features(data)
  idx=list(orig[2]).index("2005-05")
  np.testing.assert_array_equal(orig[0][idx],revised[0][idx])
 def test_tminus2_is_used(self):
  orig=self.features(self.data)
  data={s:dict(v) for s,v in self.data.items()}
  data[self.nodes[0]]["2005-03"]=500.
  revised=self.features(data)
  idx=list(orig[2]).index("2005-05")
  self.assertNotEqual(float(orig[0][idx,0,0]),float(revised[0][idx,0,0]))
 def test_strict_chronology(self):
  self.assertEqual(m.TRAIN,("1997-01","2015-12"))
  self.assertEqual(m.VAL,("2016-01","2018-12"))
  self.assertEqual(m.CAL,("2019-01","2020-12"))
  self.assertEqual(m.TEST,("2021-01","2025-12"))
 def test_single_fold_no_future_targets(self):
  import inspect
  code=inspect.getsource(m.fit_fold)
  self.assertIn("exTrain[tr]",code)
  self.assertIn("y_train[va]",code)
  self.assertNotIn("y_train[te]",code)
 def test_experimental_status_by_design(self):
  self.assertNotEqual(m.BASE,m.ROOT/"datos/generalizacion_9x")
  self.assertEqual(m.N_FOLDS,5)
  self.assertEqual(len(m.MODELS),5)
if __name__=="__main__":unittest.main()
