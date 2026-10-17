"""9M: agrupación hidrofísica sin mezclar niveles, pisos o certificaciones."""
import json,sys,unittest
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import agrupar_hidrofisicos_9m as g

class Zonificacion9M(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.geo,cls.state,cls.tab=g.compute()
 def test_invariantes(self):
  m=self.state
  self.assertEqual(m["fase"],"9M")
  self.assertEqual(m["n_sectores_9k_originales"],42)
  self.assertEqual(m["n_agrupaciones_hidrofisicas"],len(self.geo["features"]))
  self.assertEqual(m["n_agrupaciones_hidrofisicas"],len(self.tab))
  self.assertGreater(m["n_agrupaciones_hidrofisicas"],0)
  self.assertEqual(m["n_cuencas_operativas_certificadas"],0)
  self.assertEqual(m["n_zonas_homogeneas_validadas"],0)
  self.assertFalse(m["modelo_zonal_con_habilidad_demostrado"] if
                   "modelo_zonal_con_habilidad_demostrado" in m else m["modelo_zonal_con_habilidad_demostrada"])
  self.assertFalse(self.geo["metadata"]["zonas_climaticas_homogeneas_validadas"])
 def test_contencion_y_piso_y_familia(self):
  src=json.loads(g.IN_Z.read_text("utf8"))["features"]
  originals={p["properties"]["id_sector"]:p for p in src}
  for feat in self.geo["features"]:
   p=feat["properties"];part=shape(feat["geometry"])
   self.assertTrue(part.is_valid)
   self.assertFalse(p["agrupacion_operativa"])
   self.assertFalse(p["clima_homogeneo_validado"])
   self.assertFalse(p["cuenca_certificada"])
   self.assertGreaterEqual(p["area_aprox_km2"],.01)
   bases=[originals[x] for x in p["nodos_sectores_origen"]]
   self.assertEqual(len(bases),p["n_sectores_origen"])
   self.assertTrue(all(b["properties"]["estrato"]==p["piso"] for b in bases))
   self.assertTrue(all((b["properties"]["familia_similitud"] or None)==p["familia_climatica"] for b in bases))
   union=unary_union([shape(x["geometry"]) for x in bases])
   self.assertLess(part.difference(union.buffer(.00005)).area,1e-6)
 def test_determinismo(self):
  if g.GEO.exists() and g.STATE.exists():
   g.run(check=True)

if __name__=="__main__":unittest.main()
