"""Pruebas 8U: fuentes viento ERA5, NOAA SST y ausencia de corrientes inventadas."""
import csv,importlib.util,json,math,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf8u",ROOT/"modelos/viento_oceano_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestWindOcean8U(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
  rel="datos/sensibilidad_vecindad_8m/puntos_8m.csv"
  out=self.root/rel;out.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(ROOT/rel,out)
 def example(self):
  points=m.locations(self.root)
  docs=[]
  for p in points:
   docs.append({"latitude":p["latitud"],"longitude":p["longitud"],"elevation":35,
    "timezone":"America/Lima","utc_offset_seconds":-18000,
    "daily_units":{"wind_speed_10m_mean":"m/s",
          "wind_speed_10m_max":"m/s","wind_direction_10m_dominant":"°"},
    "daily":{"time":["1996-01-01","1996-01-02"],
       "wind_speed_10m_mean":[3.1,3.4],
       "wind_speed_10m_max":[5.5,6.1],
       "wind_direction_10m_dominant":[180,190]}})
  return points,docs
 def test_centers_match_original_four_cities(self):
  points=m.locations(self.root)
  self.assertEqual([p["id"] for p in points],["Chiclayo","Jayanca","Motupe","Olmos"])
  self.assertEqual(len(points),4)
 def test_meteorological_direction_from_south_means_northward_wind(self):
  direction=math.radians(180)
  self.assertAlmostEqual(-3*math.sin(direction),0.,places=10)
  self.assertAlmostEqual(-3*math.cos(direction),3.,places=10)
 def test_daily_validators_accept_complete_verifiable_blocks(self):
  coords,payload=self.example()
  with patch.object(m.oaf,"dates",return_value=["1996-01-01","1996-01-02"]):
   rows=m.validate(json.dumps(payload).encode(),(1996,2005),coords)
  self.assertEqual(len(rows),4)
 def test_null_daily_wind_rejected_not_interpolated(self):
  pts,obj=self.example();obj[0]["daily"]["wind_speed_10m_mean"][0]=None
  with patch.object(m.oaf,"dates",return_value=["1996-01-01","1996-01-02"]):
   with self.assertRaisesRegex(ValueError,"nulo"):m.validate(json.dumps(obj).encode(),(1996,2005),pts)
 def test_physical_range_rejects_speed_and_direction(self):
  pts,obj=self.example()
  obj[0]["daily"]["wind_direction_10m_dominant"][1]=401
  with patch.object(m.oaf,"dates",return_value=["1996-01-01","1996-01-02"]):
   with self.assertRaisesRegex(ValueError,"fuera de rango"):m.validate(json.dumps(obj).encode(),(1996,2005),pts)
 def test_expected_partial_without_any_source_or_noaa(self):
  report,rows=m.run(self.root)
  self.assertEqual(rows,[])
  self.assertEqual(report["bloques_viento_obtenidos"],0)
  self.assertFalse(report["corrientes_marinas_serie_historica_verificada"])
  self.assertTrue(report["corrientes_no_inferibles_del_viento_ni_del_SST"])
  self.assertEqual(report["zonas_homogeneas_certificadas"],0)
  m.publish(self.root);m.publish(self.root,check=True)
 def test_tampered_reference_center_must_be_rejected(self):
  p=self.root/"datos/sensibilidad_vecindad_8m/puntos_8m.csv"
  a=p.read_text(encoding="utf-8")
  p.write_text(a.replace("Chiclayo,C,","Chiclayo,Z,",1),encoding="utf-8")
  with self.assertRaisesRegex(ValueError,"8M incompleto"):m.run(self.root)
 def test_duplicate_compressed_file_without_metadata_is_not_valid(self):
  f,_=m.paths(self.root,(1996,2005))
  f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b"not-reanalysis")
  with self.assertRaisesRegex(ValueError,"parcialmente"):m.run(self.root)
if __name__=="__main__":unittest.main()
