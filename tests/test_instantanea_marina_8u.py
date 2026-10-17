"""8U marine: forecast is not 30-year climatology and directions are TO."""
import importlib.util,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("marine8u",ROOT/"modelos/instantanea_marina_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Marine8UTest(unittest.TestCase):
 def fake(self):
  arr=[]
  for p in m.POINTS:
   t=[f"2026-10-{17+i//24:02d}T{i%24:02d}:00" for i in range(72)]
   arr.append({"timezone":"America/Lima","utc_offset_seconds":-18000,
     "latitude":p["latitude"],"longitude":p["longitude"],
     "hourly_units":{"sea_surface_temperature":"°C",
       "ocean_current_velocity":"m/s","ocean_current_direction":"°"},
     "hourly":{"time":t,"sea_surface_temperature":[20.]*72,
       "ocean_current_velocity":[1.]*72,"ocean_current_direction":[90.]*72}})
  return arr
 def test_three_offshore_points_are_not_reclassified_as_land(self):
  self.assertEqual(len(m.POINTS),3)
  self.assertTrue(all(p["longitude"]< -80.2 for p in m.POINTS))
  self.assertIn("cell_selection=sea",m.request())
 def test_eastward_current_heading_is_towards_east(self):
  rows=m.check(json.dumps(self.fake()).encode())
  self.assertEqual(len(rows),3)
  self.assertTrue(all(z["n_horas_con_las_3_variables"]==72 for z in rows))
  self.assertTrue(all(abs(z["u_media_modelada_ms"]-1)<1e-6 for z in rows))
  self.assertTrue(all(abs(z["v_media_modelada_ms"])<1e-6 for z in rows))
 def test_nulls_excluded_never_set_to_zero(self):
  data=self.fake()
  data[0]["hourly"]["ocean_current_velocity"]=[None]*72
  rows=m.check(json.dumps(data).encode())
  self.assertEqual(rows[0]["n_horas_con_las_3_variables"],0)
  self.assertIsNone(rows[0]["velocidad_media_modelada_ms"])
 def test_reject_inland_shift(self):
  data=self.fake()
  data[1]["latitude"]+=1.5
  with self.assertRaises(ValueError):m.check(json.dumps(data).encode())
 def test_kmh_converted_to_ms_without_guessing(self):
  data=self.fake()
  data[0]["hourly_units"]["ocean_current_velocity"]="km/h"
  data[0]["hourly"]["ocean_current_velocity"]=[3.6]*72
  out=m.check(json.dumps(data).encode())
  self.assertAlmostEqual(out[0]["velocidad_media_modelada_ms"],1,places=5)
  self.assertEqual(out[0]["unidad_entrada_velocidad_corriente"],"km/h")
 def test_reject_wrong_velocity_unit(self):
  data=self.fake()
  data[0]["hourly_units"]["ocean_current_velocity"]="nautical_units"
  with self.assertRaisesRegex(ValueError,"desconocida"):m.check(json.dumps(data).encode())
 def test_no_sentinel_contamination(self):
  data=self.fake()
  data[2]["hourly"]["ocean_current_velocity"][2]=-999.0
  with self.assertRaises(ValueError):m.check(json.dumps(data).encode())
if __name__=="__main__":unittest.main()
