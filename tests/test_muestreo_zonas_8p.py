"""8P: verificación de testigos nuevos y grafo de cercanía (datos DEM reales)."""
import importlib.util,tempfile,shutil,json,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf8p",REPO/"modelos/muestreo_zonas_contiguas_8p.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Test8PSampling(unittest.TestCase):
 def setUp(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
  self.root=Path(tmp.name)
  for path in (m.NODES,m.PILOTS):
   q=self.root/path;q.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(REPO/path,q)
 def test_new_nodes_are_unique_and_not_8o_pilots(self):
  new,edges,nodes,old=m.select(self.root)
  self.assertEqual(len(new),62)
  self.assertEqual(len(set(x["id"] for x in new)),62)
  self.assertFalse(set(x["id"] for x in new)&set(x["id"] for x in old))
 def test_sample_reinforces_high_altitude_and_not_coastal_dem_negative(self):
  new,edges,_,_=m.select(self.root)
  self.assertGreaterEqual(sum(x["altitud_dem_m"]>=800 for x in new),30)
  self.assertTrue(all(x["altitud_dem_m"]>5 for x in new))
  self.assertTrue(all(x["apto_para_zona_operativa"]=="false" for x in new))
 def test_quotas_are_respected_even_with_sparse_middle_mountains(self):
  new,_,_,_=m.select(self.root)
  for k,quota in m.QUOTAS.items():
   self.assertEqual(sum(x["estrato_fisico_preliminar"]==k for x in new),quota)
 def test_edges_are_finite_local_symmetric_undirected_not_homogeneity(self):
  _,edges,allnodes,_=m.select(self.root)
  self.assertGreater(len(edges),500)
  ids={x["id"] for x in allnodes}
  self.assertTrue(all(e["origen_id"] in ids and e["destino_id"] in ids
    and e["origen_id"]!=e["destino_id"] and e["distancia_km"]<=8.5
    and e["homogeneidad_climatica_comprobada"]=="false" for e in edges))
 def test_8p_creates_deterministic_outputs_and_flags_no_operational_zones(self):
  m.publish(self.root);m.publish(self.root,check=True)
  report=json.loads((self.root/m.OUT/"estado_muestreo_8p.json").read_text())
  self.assertFalse(report["zona_climatica_homogenea_demostrada"])
  self.assertEqual(report["n_poligonos_agricolas_certificados"],0)
  self.assertFalse(report["predicciones_zonales_verificadas"])
  self.assertEqual(report["n_testigos_totales_propuestos"],81)
 def test_dem_metadata_altered_is_not_accepted(self):
  p=self.root/m.NODES;txt=p.read_text()
  p.write_text(txt.replace(",false\n",",true\n",1))
  with self.assertRaisesRegex(ValueError,"falsamente"):
   m.select(self.root)
 def test_geo_distance_and_no_coincidence_rules(self):
  self.assertAlmostEqual(m.haversine(-6.5,-79.5,-6.5,-79.5),0)
  self.assertTrue(6<m.haversine(-6.5,-79.5,-6.5,-79.4375)<8)

if __name__=="__main__":unittest.main()
