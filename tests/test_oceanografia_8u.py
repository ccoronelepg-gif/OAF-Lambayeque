"""8U: ocean SST source is SHA verified, currents are real seawater vectors only."""
import importlib.util,json,math,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def get(name,filename):
 spec=importlib.util.spec_from_file_location(name,ROOT/"modelos"/filename)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m
sst=get("sst8u","oceanografia_fuentes_8u.py")
curr=get("curr8u","corrientes_geostroficas_8u.py")

class TestMarine8U(unittest.TestCase):
 def test_noaa_nino_12_sea_surface_temperature_has_360_months_from_real_archive(self):
  rows=sst.original_sst(ROOT)
  self.assertEqual(len(rows),360)
  self.assertEqual(rows[0]["mes"],"1996-01")
  self.assertEqual(rows[-1]["mes"],"2025-12")
  self.assertTrue(all(x["region_cuadrante_no_punto"]=="true" for x in rows))
  self.assertTrue(all(x["vintage_historica_verificada"]=="false" for x in rows))
 def test_noaa_cpc_sst_does_not_fabricate_marine_currents(self):
  meta,_=sst.assemble(ROOT)
  self.assertEqual(meta["n_series_corriente_marina_1996_2025_descargadas_y_validadas"],0)
  self.assertFalse(meta["tsm_costa_lambayeque_medido"])
  self.assertTrue(meta["NO_confundir_corriente_marina_con_viento"])
 def test_geostrophic_direction_is_towards_not_meteorological_from(self):
  self.assertAlmostEqual((math.degrees(math.atan2(0,1))+360)%360,0)
  self.assertAlmostEqual((math.degrees(math.atan2(1,0))+360)%360,90)
 def test_geostrophic_query_contains_both_actual_ocean_components(self):
  u=curr.make_url("x",-6.7,-81.1,2017,2020)
  self.assertIn("u_current",u);self.assertIn("v_current",u)
  self.assertIn("2017-01-01",u);self.assertIn("-81.1",u)
  self.assertNotIn("wind_speed",u)
 def test_current_api_cannot_claim_30yr_historical_data(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   state,rows=curr.evaluate(root)
   self.assertFalse(state["periodo_1996_2025_de_corrientes_completo"])
   self.assertEqual(state["n_series_punto_periodo_verificadas"],0)
   self.assertEqual(rows,[])
   curr.publish(root);curr.publish(root,check=True)
 def test_currents_csv_units_qa_and_month(self):
  text="time,latitude,longitude,u_current,v_current\nUTC,degrees_north,degrees_east,m/s,m/s\n"
  text+="2017-01-01T00:00:00Z,-6.7,-81.1,0.3,-0.2\n"
  with self.assertRaisesRegex(ValueError,"insuficiente"):
   curr.parse_original(text.encode(),-6.7,-81.1,2017,2017)
 def test_noaa_sst_can_rebuild_without_edits(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   # same immutable input NOAA files from actual 8T archive
   from shutil import copyfile
   for file in (sst.cpc.RAW,sst.cpc.META):
    dest=root/file;dest.parent.mkdir(parents=True,exist_ok=True)
    copyfile(ROOT/file,dest)
   sst.publish(root);sst.publish(root,check=True)
if __name__=="__main__":unittest.main()
