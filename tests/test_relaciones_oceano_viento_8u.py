"""8U vector association checks; no predictive leakage claims."""
import importlib.util,math,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("relation8u",REPO/"modelos/relaciones_oceano_viento_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestPhysicalRelation8U(unittest.TestCase):
 def test_time_alignment_with_ocean_t_minus_2(self):
  self.assertEqual(m.previous_month("2017-01",2),"2016-11")
  self.assertEqual(m.previous_month("2025-12",2),"2025-10")
 def test_anomalies_remove_each_month_calendar_mean(self):
  x={f"{y}-{mo:02d}":20+mo+0.5*(y-2017) for y in range(2017,2026) for mo in range(1,13)}
  residual=m.anomalies(x)
  self.assertEqual(len(residual),108)
  self.assertAlmostEqual(sum(residual[f"{y}-07"] for y in range(2017,2026)),0)
  self.assertNotEqual(residual["2017-01"],residual["2025-01"])
 def test_pearson_requires_nonstrict_coverage(self):
  x=[i/10 for i in range(108)]
  self.assertAlmostEqual(m.corr(x,[3*v+5 for v in x]),1.)
  self.assertAlmostEqual(m.corr(x,[-3*v+5 for v in x]),-1.)
  self.assertIsNone(m.corr([4]*108,x))
 def test_108_months_compulsory(self):
  with self.assertRaisesRegex(ValueError,"108 meses"):m.anomalies({"2017-01":2})
 def test_actual_files_allow_reproducible_descriptive_r_only(self):
  stat,rows=m.evaluate(REPO)
  self.assertEqual(stat["n_parejas_mes_punto"],216)
  self.assertEqual(len(rows),2)
  self.assertTrue(stat["normal_no_apta_para_backtest_porque_contiene_futuro"])
  self.assertFalse(stat["habilidad_predictiva_evaluada"])
  self.assertTrue(all(x["n_meses_2017_2025"]==108 for x in rows))
 def test_sha_original_data_present_for_all_components(self):
  state,records=m.evaluate(REPO)
  self.assertEqual(set(state["sha256_csv_entrada"]),{"viento","sst","corrientes"})
  self.assertTrue(all(len(s)==64 for s in state["sha256_csv_entrada"].values()))
if __name__=="__main__":unittest.main()
