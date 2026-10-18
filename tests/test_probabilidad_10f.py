"""OAF 10F: source coverage, lag2 no leakage, sector-normal P90, QA."""
import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import probabilidad_39_sectores_10f as f
class Test10F(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.nodes,cls.A,cls.edges,cls.fixed,cls.floors,cls.polygons,cls.data,cls.audit=f.previous.inputs()
  cls.x0,cls.x1,cls.Y,cls.rain,cls.t,cls.dates,cls.tr,cls.va,cls.ca,cls.te=f.matrix(cls.nodes,cls.fixed,cls.data)
 def test_exact_39_sectors(self):
  self.assertEqual((len(self.nodes),self.x0.shape,self.x1.shape),(39,(348,39,11),(348,39,18)))
 def test_disjoint_splits(self):
  self.assertEqual([int(m.sum()) for m in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
  for a in (self.tr,self.va,self.ca,self.te):
   for b in (self.tr,self.va,self.ca,self.te):
    if a is not b:self.assertFalse(np.any(a&b))
 def test_event_reference_does_not_include_2023(self):
  changed={s:dict(v) for s,v in self.data.items()}
  sid=self.nodes[0]
  changed[sid]["2023-03"]+=10000.
  altered=f.matrix(self.nodes,self.fixed,changed)
  self.assertAlmostEqual(self.t[0],altered[4][0])
 def test_no_t_minus_one_in_rain_and_ocean(self):
  changed={s:dict(v) for s,v in self.data.items()}
  sid=self.nodes[0]
  changed[sid]["2005-04"]+=10000.
  altered=f.matrix(self.nodes,self.fixed,changed)
  idx=list(self.dates).index("2005-05")
  np.testing.assert_array_equal(self.x0[idx],altered[0][idx])
  np.testing.assert_array_equal(self.x1[idx],altered[1][idx])
  n=list(self.dates).index("2005-06")
  self.assertNotEqual(self.x0[n,0,0],altered[0][n,0,0])
 def test_global_indices_shared_and_no_local_imputation(self):
  idx=list(self.dates).index("2023-09")
  a=self.x1[idx,:,11:]
  np.testing.assert_array_equal(a,np.repeat(a[:1],39,axis=0))
  self.assertNotIn("radiacion_solar",f.COV_NAMES)
  self.assertNotIn("corriente_geostrofica",f.COV_NAMES)
 def test_roni_limited_to_expost_grouping(self):
  self.assertEqual(set(f.load(f.RONI)["datos"]),{f"{y}-{m:02d}" for y in range(2021,2026) for m in range(1,13)})
  self.assertEqual(f.regime("2023-11",f.load(f.RONI)["datos"]),"calido_RONI")
 def test_strict_calendar(self):
  self.assertEqual(f.TRAIN,("1997-01","2015-12"))
  self.assertEqual(f.VAL,("2016-01","2018-12"))
  self.assertEqual(f.CAL,("2019-01","2020-12"))
  self.assertEqual(f.TEST,("2021-01","2025-12"))
if __name__=="__main__":unittest.main()
