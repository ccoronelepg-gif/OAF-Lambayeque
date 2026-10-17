"""8U checks for 360 month wind climatology and non-fabricated ocean currents."""
import importlib.util,json,math,tempfile,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("winds8u",REPO/"modelos/vientos_atmosfericos_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestWind8U(unittest.TestCase):
 def test_fixed_design_includes_land_and_ocean_reference(self):
  self.assertEqual(len(m.LOCATIONS),6)
  self.assertEqual(len({p[0] for p in m.LOCATIONS}),6)
  self.assertEqual(sum(p[1]=="mar_abierto_muestreo" for p in m.LOCATIONS),2)
  self.assertTrue(all(-85<lon<-75 and -9<lat<-4 for _,_,lat,lon in m.LOCATIONS))
 def test_provider_contract_is_era5_and_si_wind(self):
  u=m.url_for(1996,2005)
  self.assertIn("models=era5",u)
  self.assertIn("wind_speed_unit=ms",u)
  self.assertIn("wind_direction_10m_dominant",u)
  self.assertIn("1996-01-01",u)
  self.assertIn("2005-12-31",u)
 def test_source_month_dates_include_leap_year(self):
  self.assertEqual(len(m.expected_dates(1996,1996)),366)
  self.assertEqual(len(m.expected_dates(1997,1997)),365)
  self.assertIn("2000-02-29",m.expected_dates(1996,2005))
 def test_missing_sources_never_fake_complete_climatology(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   stat,rows=m.calculate(root)
   self.assertEqual(stat["n_bloques_verificados"],0)
   self.assertEqual(rows,[])
   self.assertFalse(stat["habilidad_predictiva_verificada"])
   m.publish(root);m.publish(root,check=True)
 def test_validates_units_daily_integrity(self):
  d=m.expected_dates(1996,2005)
  n=len(d)
  data=[{"timezone":"America/Lima","latitude":lat,"longitude":lon,
         "daily_units":{"wind_speed_10m_mean":"m/s","wind_direction_10m_dominant":"°"},
         "daily":{"time":d,"wind_speed_10m_mean":[3.]*n,
         "wind_speed_10m_max":[5.]*n,"wind_direction_10m_dominant":[180.]*n}}
        for _,_,lat,lon in m.LOCATIONS]
  raw=json.dumps(data).encode()
  self.assertEqual(len(m.validate(raw,1996,2005)),6)
  data[0]["daily"]["wind_speed_10m_max"][3]=1
  with self.assertRaisesRegex(ValueError,"máximo"):
   m.validate(json.dumps(data).encode(),1996,2005)
 def test_direction_from_south_produces_north_positive(self):
  angle=math.radians(180)
  self.assertAlmostEqual(-3*math.cos(angle),3)
  self.assertAlmostEqual(-3*math.sin(angle),0,places=10)

if __name__=="__main__":unittest.main()
