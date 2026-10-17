"""8U NOAA OISST: calidad diaria, coordenadas oceánicas, máscara y periodo."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf_oisst",ROOT/"modelos/sst_costera_8u.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestSST(unittest.TestCase):
 def setUp(self):
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);self.root=Path(d.name)
 def fake(self):
  return (b"time,zlev,latitude,longitude,sst\n"
       b"UTC,m,degrees_north,degrees_east,degree_C\n"
       b"1996-01-01T12:00:00Z,0,-6.625,-80.625,22.1\n"
       b"1996-01-02T12:00:00Z,0,-6.625,-80.625,22.5\n")
 def test_noaa_csv_units_row_and_daily_dates(self):
  with patch.object(m.common,"dates",return_value=["1996-01-01","1996-01-02"]):
   vals=m.validate(self.fake(),m.POINTS[0],m.PERIODS[0])
  self.assertEqual(vals["1996-01-01"],22.1)
 def test_missing_day_is_rejected_not_imputed(self):
  truncated=self.fake().splitlines(keepends=True)
  with patch.object(m.common,"dates",return_value=["1996-01-01","1996-01-02"]):
   with self.assertRaisesRegex(ValueError,"por día"):m.validate(b"".join(truncated[:-1]),m.POINTS[0],m.PERIODS[0])
 def test_land_or_missing_numeric_is_rejected(self):
  bad=self.fake().replace(b"22.5",b"NaN")
  with patch.object(m.common,"dates",return_value=["1996-01-01","1996-01-02"]):
   with self.assertRaisesRegex(ValueError,"máscara terrestre"):m.validate(bad,m.POINTS[0],m.PERIODS[0])
 def test_wrong_ocean_coordinates_rejected(self):
  bad=self.fake().replace(b"-80.625",b"-79.625")
  with patch.object(m.common,"dates",return_value=["1996-01-01","1996-01-02"]):
   with self.assertRaisesRegex(ValueError,"celda distinta"):m.validate(bad,m.POINTS[0],m.PERIODS[0])
 def test_no_source_means_zero_verified_ocean_pixels(self):
  state,rows=m.report(self.root)
  self.assertEqual(rows,[])
  self.assertEqual(state["archivos_sst_verificados"],0)
  self.assertEqual(state["sitios_con_sst_30anios_completa"],0)
  self.assertTrue(state["sst_no_es_velocidad_de_corrientes"])
  m.publish(self.root);m.publish(self.root,check=True)
 def test_site_geometry_and_source_endpoint_fixed(self):
  url=m.request(m.POINTS[0],(1996,2005))
  self.assertIn("ncdcOisst21Agg_LonPM180.csv",url)
  self.assertIn("1996-01-01T12",url)
  self.assertIn("-80.625",url)
  self.assertIn("sst%5B",url)
if __name__=="__main__":unittest.main()
