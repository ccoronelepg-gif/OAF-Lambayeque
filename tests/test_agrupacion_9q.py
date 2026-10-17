"""OAF 9Q: fuentes observadas, 360 meses reales y agrupación provisional."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import recuperar_chirps_9q as downloader
import agrupar_pisos_9q as zonal

class Fase9Q(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src=json.loads(downloader.MANIFEST.read_text("utf8"))
  cls.geo=json.loads(zonal.GROUPS.read_text("utf8"))
  cls.report=json.loads(zonal.REPORT.read_text("utf8"))
 def test_360_mes_fijos_y_sin_meses_duplicados(self):
  s=self.src
  self.assertEqual(s["fase"],"9Q")
  self.assertEqual(s["n_meses_preexistentes_9o_9p"],120)
  self.assertEqual(s["n_meses_objetivo"],360)
  self.assertEqual(s["n_meses_chirps_verificados"]+s["n_meses_no_comprobados"],360)
  self.assertEqual(s["n_meses_nuevos_9q"],len(s["nuevos"]))
  self.assertEqual(len({x["mes"] for x in s["nuevos"]}),s["n_meses_nuevos_9q"])
  self.assertTrue(s["producto_final_no_preliminar"])
  self.assertEqual(s["zonas_climaticas_homogeneas_certificadas"],0)
  self.assertFalse(s["pronostico_zonal_validado"])
  self.assertFalse(s["alertas_fitosanitarias_emitidas"])
  self.assertEqual(s["todas_las_fechas_1996_2025_verificadas"],s["n_meses_chirps_verificados"]==360)
  self.assertEqual(downloader.check(),s["n_meses_nuevos_9q"])
 def test_evidencia_por_registro_y_fuente(self):
  j=self.report
  self.assertEqual(j["fase"],"9Q")
  self.assertEqual(j["meses_chirps_360"],self.src["n_meses_chirps_verificados"])
  self.assertEqual(j["n_meses_faltantes"],self.src["n_meses_no_comprobados"])
  self.assertEqual(j["n_sectores"],42)
  self.assertEqual(j["n_pisos_exploratorios"],7)
  self.assertEqual(sum(x["n_sectores"] for x in j["comparacion_de_pisos"]),42)
  self.assertEqual(j["n_zonas_homogeneas_instrumentalmente_certificadas"],0)
  self.assertEqual(j["n_estaciones_instrumentales_independientes_30anios"],0)
  self.assertFalse(j["habilidad_pronostico_exante_validada"])
  self.assertFalse(j["aptitud_agricola_aranadano_vid_validada"])
 def test_filtrado_climatico_y_procedencia_grupos(self):
  j=self.report
  self.assertEqual(self.geo["metadata"]["agrupaciones_certificadas"],0)
  self.assertEqual(j["n_grupos_propuestos"],len(self.geo["features"]))
  self.assertGreaterEqual(j["n_pares_mismo_piso_cuenca_cercanos_evaluados"],j["n_pares_lluvia_y_testigos_multivariable_satisfacen_criterios"])
  for x in self.geo["features"]:
   p=x["properties"]
   self.assertFalse(p["zona_homogenea_validada"])
   self.assertFalse(p["limite_oficial"])
   self.assertFalse(p["pronostico_zonal_validado"])
   self.assertEqual(p["puntos_campo_independientes"],0)
   self.assertGreaterEqual(len(p["sectores"]),2)
 def test_determinismo_y_navegacion_del_portal(self):
  zonal.run(check=True)
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count("<section data-page="),5)
  for id in ("oaf-9q-visor","oaf-9q-months","oaf-9q-annual","oaf-9q-groups",
     "oaf-9q-status","oaf-9q-plot-type","oaf-9q-graphic","oaf-9q-floor-table",
     "oaf-9q-group-table","oaf-9q-science","oaf-9q-map","oaf-9q-map-detail"):
   self.assertEqual(h.count('id="'+id+'"'),1,id)
  self.assertIn("visor_pisos_9q.js",h)
  self.assertIn("FASE_9Q_PISOS_Y_AGRUPACIONES.md",h)

if __name__=="__main__":unittest.main()
