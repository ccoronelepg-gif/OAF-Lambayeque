"""8Q tests: study corridors over authentic DEM; synthetic climate in temporary files."""
import csv,gzip,hashlib,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf8q",REPO/"modelos/transectos_continuidad_8q.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestCorridors8Q(unittest.TestCase):
 def setUp(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
  self.root=Path(tmp.name)
  for path in (m.NODES,m.OLD_CLIMATE,
               "datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv"):
   source=REPO/path;out=self.root/path;out.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(source,out)
 def test_all_three_premapped_segments_and_8_to_12_midpoints(self):
  points,routes=m.samples(self.root)
  self.assertEqual(len(routes),3)
  self.assertTrue(8<=len(points)<=12)
  self.assertEqual(len({x["testigo_id"] for x in points}),len(points))
  self.assertTrue(all(x["distancia_al_objetivo_km"]<=5 for x in points))
  self.assertTrue(all(x["homogeneidad_espacial_acreditada"]=="false" for x in points))
  self.assertTrue(all(x["altitud_dem_m"]>5 for x in points))
 def test_documented_elevation_excursions_on_both_segments(self):
  pts,layout=m.samples(self.root)
  v1=[x for x in pts if x["transecto"].startswith("V1")]
  v2=[x for x in pts if x["transecto"]=="V2"]
  self.assertGreater(max(p["altitud_dem_m"] for p in v1),521)
  self.assertTrue(any(abs(p["salto_altitudinal_lineal_m"])>150 for p in v1))
  self.assertGreater(max(p["altitud_dem_m"] for p in v2),3236)
  self.assertLess(min(p["altitud_dem_m"] for p in v2),2978)
 def test_no_incomplete_meteorology_claims_climate_continuity(self):
  status,positions,comparison,cellrows=m.evaluate(self.root)
  self.assertEqual(status["fuentes_climaticas_verificadas"],0)
  self.assertEqual(status["n_testigos_intermedios_30_anios_completos"],0)
  self.assertEqual(comparison,[])
  self.assertEqual(cellrows,[])
  self.assertEqual(status["zonas_contiguas_homogeneas_demostradas"],0)
  m.publish(self.root);m.publish(self.root,check=True)
 def test_missing_climate_sources_are_not_substituted(self):
  p=m.points(m.samples(self.root)[0])
  self.assertIsNone(m.inspect(self.root,"era5_land",1996,2005,p))
  state,*rest=m.evaluate(self.root)
  self.assertFalse(state["modelo_predictivo_zonal_validado"])
 def test_metadata_sha_mismatch_rejected(self):
  pts=m.points(m.samples(self.root)[0])
  file,meta=m.source_paths(self.root,"era5_land",1996,2005)
  file.parent.mkdir(parents=True,exist_ok=True)
  raw=json.dumps([{"day":"not_real"}]).encode()
  file.write_bytes(gzip.compress(raw))
  meta.write_text(json.dumps({"fase":"8Q","modelo":"era5_land","periodo":[1996,2005],
     "url":m.climate.query("era5_land",1996,2005,pts),
     "ids":[p["id"] for p in pts],"sha256_original":"0"*64}))
  with self.assertRaisesRegex(ValueError,"SHA"):
   m.evaluate(self.root)
 def test_dem_tampering_rejected(self):
  p=self.root/m.NODES
  contents=p.read_text(encoding="utf-8")
  p.write_text(contents.replace(",false\n",",true\n",1),encoding="utf-8")
  with self.assertRaisesRegex(ValueError,"no declara zonas"):
   m.evaluate(self.root)
 def test_reference_graph_selection_is_repeatable(self):
  a,route=m.samples(self.root)
  b,route2=m.samples(self.root)
  self.assertEqual(a,b)
  self.assertEqual(route,route2)
 def test_report_is_only_sampling_not_instrument_validation(self):
  state,p,_,cellrows=m.evaluate(self.root)
  self.assertEqual(state["poligonos_agroclimaticos_certificados"],0)
  self.assertEqual(state["instrumentos_SENAMHI_confirmados"],0)
  self.assertTrue(state["interpolacion_de_coordenadas_no_es_ruta_topografica"])
  self.assertTrue(state["diferencias_fisicas_no_prueban_diferencias_climaticas"])

if __name__=="__main__":unittest.main()
