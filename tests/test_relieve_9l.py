"""9L: pruebas de relieve DEM contínuo y prudencia causal."""
import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import refinar_relieve_9l as m
from shapely.geometry import shape

class Relieve9L(unittest.TestCase):
 def test_geometria_y_altitud(self):
  self.assertTrue(m.F_SOURCE.exists(),"Copernicus COG original requerido")
  ge,state=m.check()
  self.assertEqual(state["n_familias"],3)
  self.assertEqual(state["n_sectores_9k_auditados"],5)
  self.assertEqual(len(ge["features"]),5)
  self.assertEqual(len({f["properties"]["familia"] for f in ge["features"]}),3)
  prev={f["properties"]["id_sector"]:shape(f["geometry"])
   for f in json.loads(m.F_BASE.read_text("utf8"))["features"]}
  for f in ge["features"]:
   p=f["properties"];origin=prev[p["sector_9k"]]
   self.assertTrue(p["altitud_cog_min_m"]<=p["altitud_cog_p50_m"]<=p["altitud_cog_max_m"])
   self.assertGreater(p["n_pixeles_cog_en_poligono"],10)
   self.assertGreaterEqual(p["n_pixeles_relieve_piso_y_pendiente_compatible"],0)
   self.assertLessEqual(p["n_pixeles_relieve_piso_y_pendiente_compatible"],
                        p["n_pixeles_cog_en_poligono"])
   self.assertFalse(p["continuidad_climatica_validada"])
   self.assertFalse(p["prediccion_zonal_validada"])
   if f["geometry"]:
    g=shape(f["geometry"])
    self.assertTrue(g.is_valid)
    self.assertLess(g.difference(origin.buffer(.00001)).area,1e-7)
 def test_certificacion_y_modelo(self):
  s=json.loads(m.F_STATE.read_text("utf8"))
  self.assertEqual(s["zonas_homogeneas_instrumentales_certificadas"],0)
  self.assertEqual(s["cuencas_hidrograficas_confirmadas"],0)
  self.assertFalse(s["comparacion_nmme"]["ajuste_altitudinal_entrenado"])
  self.assertFalse(s["comparacion_nmme"]["prediccion_por_sector_generada"])
  self.assertFalse(s["comparacion_nmme"]["habilidad_prospectiva_demostrada"])
  self.assertEqual(s["comparacion_nmme"]["n_celdas_noaa_para_4_localidades"],2)
  self.assertEqual(hashlib.sha256(m.F_SOURCE.read_bytes()).hexdigest(),
                   s["sha256_tiff_original"])
 def test_portal_y_legibilidad(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count('<section data-page='),5)
  for label in ("oaf-9l-visor","oaf-9l-map","oaf-9l-list","oaf-9l-state"):
   self.assertEqual(h.count('id="'+label+'"'),1)
  self.assertIn("modelos/visor_relieve_9l.js",h)
  self.assertIn("FASE_9L_RELIEVE_Y_TRANSFERENCIA.md",h)

if __name__=="__main__":unittest.main()
