"""10G - structural tests for spatial provenance and ERA5 month aggregation."""
import datetime as dt,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"modelos"))
import ingesta_era5_39_sectores_10g as m

class Test10G(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=m.manifest()
 def test_sector_points_from_author_geometry(self):
  p=self.m["puntos"]
  self.assertEqual(len(p),39)
  self.assertEqual(len({z["sector"] for z in p}),39)
  self.assertTrue(all(-82<z["lon"]<-78 and -9<z["lat"]<-5 for z in p))
 def test_no_official_zoning_claim(self):
  self.assertTrue(all(z["homogeneidad_validada"] is False for z in self.m["puntos"]))
  self.assertTrue(all(z["no_es_estacion"] and z["no_es_media_poligono"] for z in self.m["puntos"]))
 def test_negative_dem_not_hidden(self):
  self.assertTrue(any(x["altitud_revisar"] and x["sector"]=="S001" for x in self.m["puntos"]))
 def test_api_requires_homogeneous_model(self):
  args=m.build_params(self.m["puntos"][:3],"2023-01-01","2023-12-31")
  self.assertEqual(args["models"],"era5")
  self.assertEqual(args["elevation"],"nan,nan,nan")
  self.assertEqual(args["cell_selection"],"nearest")
  self.assertEqual(args["timezone"],"GMT")
  self.assertEqual(args["wind_speed_unit"],"ms")
  self.assertEqual(len(args["daily"].split(",")),7)
 def fixture(self,node):
  dates=[f"2023-01-{n:02d}" for n in range(1,32)]
  d={"time":dates}
  vals={"temperature_2m_mean":20.,"relative_humidity_2m_mean":60.,
    "wind_speed_10m_mean":3.,"shortwave_radiation_sum":10.,
    "pressure_msl_mean":1012.,"cloud_cover_mean":30.,"vapour_pressure_deficit_max":1.}
  for key,val in vals.items():d[key]=[val]*31
  return {"latitude":node["lat"],"longitude":node["lon"],"elevation":100.,
    "daily":d,"daily_units":{"wind_speed_10m_mean":"m/s",
      "shortwave_radiation_sum":"MJ/m²","pressure_msl_mean":"hPa",
      "temperature_2m_mean":"°C","relative_humidity_2m_mean":"%",
      "cloud_cover_mean":"%"}}
 def test_month_aggregation_and_radiation_sum(self):
  node=self.m["puntos"][0];obj=self.fixture(node)
  metadata={"downloaded_utc":"2026-10-17T00:00:00+00:00"}
  result=m.convert(node,obj,metadata,"2023-01-01","2023-01-31")
  self.assertEqual(len(result),1)
  self.assertEqual(result[0]["radiacion_corta_mj_m2"],310.)
  self.assertEqual(result[0]["viento_10m_m_s"],3.)
  self.assertEqual(result[0]["dias_validos"],31)
  self.assertEqual(result[0]["medicion_instrumental"],"false")
 def test_reject_missing_day(self):
  node=self.m["puntos"][0];obj=self.fixture(node)
  for key,val in obj["daily"].items():val.pop()
  with self.assertRaises(ValueError):
   m.convert(node,obj,{"downloaded_utc":"test"},"2023-01-01","2023-01-30")
 def test_reject_weather_physics(self):
  node=self.m["puntos"][0];obj=self.fixture(node)
  obj["daily"]["relative_humidity_2m_mean"][4]=101.
  with self.assertRaises(ValueError):
   m.convert(node,obj,{"downloaded_utc":"test"},"2023-01-01","2023-01-31")
if __name__=="__main__":unittest.main()
