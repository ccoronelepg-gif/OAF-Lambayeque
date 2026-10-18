"""10G: lagged ERA5 from actual archive only; no same-month climate leakage."""
import sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import comparacion_atmosferica_rf_gcn_10g as m
class Tests10GAbla(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  nodes,A,edges,fixed,floors,polygons,data,audit=m.base.previous.inputs()
  cls.nodes=nodes;cls.fixed=fixed;cls.data=data
  cls.X0,cls.X1,cls.Y,cls.rain,cls.thr,cls.dates,cls.tr,cls.va,cls.ca,cls.te=m.base.matrix(nodes,fixed,data)
 def test_archive_complete_if_used(self):
  X,r=m.join_features(self.nodes,self.X1,self.dates)
  self.assertEqual(X.shape,(348,39,25))
  self.assertEqual(r["resumen"]["filas"],14040)
  self.assertFalse(r["alertas_activadas"])
 def test_no_target_month_weather_used(self):
  # The appended channel's first 1997-01 value MUST equal 1996-11,
  # not 1996-12 nor target 1997-01.
  rows=m.read(m.ATM)
  i={(r["sector"],r["mes"]):r for r in rows}
  X,_=m.join_features(self.nodes,self.X1,self.dates)
  j=0;sid=self.nodes[j]
  self.assertEqual(self.dates[0],"1997-01")
  self.assertAlmostEqual(float(X[0,j,18]),float(i[(sid,"1996-11")]["temperatura_aire_c"]),places=3)
  self.assertNotEqual(X[0,j,18],float(i[(sid,"1997-01")]["temperatura_aire_c"]))
 def test_scoring_against_exact_holdout_reference(self):
  m.check_ref=m.read(m.ORIG)
  self.assertEqual(len(m.check_ref),11700)
  self.assertEqual(set(x["modelo"] for x in m.check_ref),set(m.base.NAMES))
 def test_control_status_in_previous(self):
  self.assertFalse(m.load(m.base.REPORT)["alertas_habilitadas"])
  self.assertFalse(m.load(m.AUDIT)["alertas_activadas"])
 def test_source_is_not_field_observation(self):
  data=m.read(m.ATM)
  self.assertTrue(all(r["medicion_instrumental"]=="false" for r in data[:200]))
  self.assertTrue(all(r["punto_representativo_no_promedio_areal"]=="true" for r in data[:200]))
 def test_time_split(self):
  self.assertEqual([int(x.sum()) for x in (self.tr,self.va,self.ca,self.te)],[228,36,24,60])
if __name__=="__main__":unittest.main()
