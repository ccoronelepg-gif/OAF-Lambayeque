"""10I humidity-hours utility requires genuine hourly rows; no infections."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"modelos"))
import horas_humedad_horarias_10i as m
class TestHumidHours(unittest.TestCase):
 def rows(self):
  return [{"fecha_hora_local":f"2026-10-01T{h:02d}:00:00",
           "localidad":"Motupe","humedad_relativa_pct":str(95 if h<8 else 65),
           "lluvia_hora_mm":str(.5 if h in (3,4) else 0)} for h in range(24)]
 def test_counts_actual_hourly_observations(self):
  d=m.analyze(self.rows())[0]
  self.assertEqual(d["horas_hr_elevada"],8)
  self.assertEqual(d["horas_con_lluvia"],2)
  self.assertEqual(d["mayor_bloque_continuo_horas_hr_elevada"],8)
  self.assertIsNone(d["horas_humedad_foliar"])
  self.assertIsNone(d["prediccion_enfermedad"])
 def test_rejects_missing_hours(self):
  with self.assertRaises(ValueError):m.analyze(self.rows()[:-1])
 def test_rejects_invalid_rh(self):
  r=self.rows();r[0]["humedad_relativa_pct"]="109"
  with self.assertRaises(ValueError):m.analyze(r)
if __name__=="__main__":unittest.main()
