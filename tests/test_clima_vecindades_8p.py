"""8P: pruebas isoladas del criterio de cercanía y de cobertura temporal."""
import importlib.util,tempfile,shutil,json,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("neighbor8p",REPO/"modelos/clima_vecindades_8p.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FILES=(m.SAMPLE,m.SAMPLE_STATE,m.OLD_NORMALS,m.OLD_NODES,m.OLD_STATE)

class TestClimate8P(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
  self.root=Path(temp.name)
  for path in FILES:
   source=REPO/path;dest=self.root/path;dest.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(source,dest)
 def test_original_19_only_without_false_new_profiles(self):
  status,sites,near,similar=m.evaluate(self.root)
  self.assertEqual(status["testigos_total_con_30_anios"],19)
  self.assertEqual(status["testigos_nuevos_con_30_anios"],0)
  self.assertEqual(status["lotes_climaticos_esperados"],24)
  self.assertEqual(status["lotes_climaticos_verificados"],0)
  self.assertEqual(status["zonas_homogeneas_geograficas_certificadas"],0)
  self.assertFalse(status["precision_predictiva_zonal_demostrada"])
  self.assertTrue(all(x["apto_para_zona_operativa"]=="false" for x in sites))
  m.publish(self.root);m.publish(self.root,check=True)
 def test_new_groups_are_all_expected_without_duplicate_nodes(self):
  pts=m.nodes(self.root)
  batches=m.chunked(pts)
  self.assertEqual(len(pts),62)
  self.assertEqual([len(x) for x in batches],[16,16,16,14])
  self.assertEqual(len({p["id"] for p in pts}),62)
 def test_temporal_8o_reference_is_19x12(self):
  pts,normals=m.old(self.root)
  self.assertEqual(len(pts),19)
  self.assertEqual(len(normals),228)
 def test_near_candidate_returns_descriptive_values_no_operational_zone(self):
  a={"id":"a","latitud":-6.5,"longitud":-79.5,"altitud_dem_m":145}
  b={"id":"b","latitud":-6.53,"longitud":-79.52,"altitud_dem_m":158}
  normals={(node,m):{"tmedia_c":21., "amplitud_termica_c":8.,"precipitacion_mm":30.,
    "humedad_relativa_pct":75.,"radiacion_mj_m2":550.} for node in ("a","b") for m in range(1,13)}
  scale={x:(20.,1.) for x in m.FEATS}
  result=m.candidate(a,b,normals,scale)
  self.assertLess(result["distancia_geografica_km"],20)
  self.assertEqual(result["distancia_climatica_estandarizada"],0)
  self.assertEqual(result["zona_homogenea_verificada"],"false")
 def test_shared_era5_cell_is_explicitly_flagged_not_declared_independent(self):
  a={"id":"a","latitud":-6.5,"longitud":-79.5,"altitud_dem_m":170}
  b={"id":"b","latitud":-6.53,"longitud":-79.52,"altitud_dem_m":220}
  normals={(node,m):{"tmedia_c":21.,"amplitud_termica_c":8.,
   "precipitacion_mm":30.,"humedad_relativa_pct":75.,"radiacion_mj_m2":550.}
    for node in ("a","b") for m in range(1,13)}
  scale={f:(0.,1.) for f in m.FEATS}
  centers={("era5","a"):{(-6.5,-79.5)},("era5","b"):{(-6.5,-79.5)},
           ("era5_land","a"):{(-6.5,-79.5)},("era5_land","b"):{(-6.52,-79.5)}}
  pair=m.candidate(a,b,normals,scale,centers=centers)
  self.assertEqual(pair["igual_celda_era5"],"si")
  self.assertEqual(pair["igual_celda_era5land"],"no")
  self.assertEqual(pair["centros_de_ambos_modelos_diferentes"],"false")
  self.assertEqual(pair["zona_homogenea_verificada"],"false")
  centers[("era5","b")]={(-6.53,-79.52)}
  pair2=m.candidate(a,b,normals,scale,centers=centers)
  self.assertEqual(pair2["centros_de_ambos_modelos_diferentes"],"true")
  self.assertEqual(pair2["zona_homogenea_verificada"],"false")

 def test_far_locations_cannot_be_called_neighbor(self):
  a={"id":"a","latitud":-6.5,"longitud":-79.5,"altitud_dem_m":100}
  b={"id":"b","latitud":-5.0,"longitud":-79.0,"altitud_dem_m":100}
  self.assertIsNone(m.candidate(a,b,{},{}))
 def test_corrupted_8o_provenance_rejected(self):
  path=self.root/m.OLD_STATE;content=json.loads(path.read_text())
  content["n_fuentes_archivadas"]=0
  path.write_text(json.dumps(content))
  with self.assertRaisesRegex(ValueError,"8O no tiene"):
   m.evaluate(self.root)
 def test_tampered_spatial_design_rejected(self):
  path=self.root/m.SAMPLE_STATE
  content=json.loads(path.read_text());content["n_testigos_climaticos_nuevos_8p"]=77
  path.write_text(json.dumps(content))
  with self.assertRaisesRegex(ValueError,"Diseño 8P"):
   m.evaluate(self.root)
 def test_monthly_climate_models_remain_separate(self):
  self.assertEqual(set(m.METHODS),{"era5","era5_land"})
  self.assertIn("relative_humidity_2m_mean",m.METHODS["era5"])
  self.assertIn("temperature_2m_max",m.METHODS["era5_land"])

if __name__=="__main__":unittest.main()
