"""9O — auditoría de climatologías CHIRPS y ERA5 con ausencias explícitas."""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import chirps_homogeneidad_9o as ch
import diagnostico_homogeneidad_9o as dx

class Homogeneidad9O(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads(ch.DAYS.read_text("utf8"))
  cls.summary=json.loads(dx.SUMMARY.read_text("utf8"))
 def test_fuentes_y_cantidad_no_inventada(self):
  j=self.source
  self.assertEqual(j["fase"],"9O")
  self.assertEqual(j["n_sectores"],42)
  self.assertEqual(j["n_testigos_reanalisis"],81)
  self.assertEqual(j["n_meses_reales"]+j["n_meses_faltantes"],j["n_meses_solicitados"])
  self.assertLessEqual(j["n_meses_reales"],360)
  self.assertEqual(len({f["mes"] for f in j["fuentes"]}),j["n_meses_reales"])
  self.assertFalse(j["calibracion_de_pronosticos_zonales"])
  self.assertFalse(j["estaciones_meteorologicas_independientes"])
  for f in j["fuentes"]:
   self.assertEqual(len(f["sha256"]),64)
   self.assertIn("/CHIRPS/v3.0/monthly/latam/tifs/",f["url"])
   self.assertEqual(f["epsg"],4326)
 def test_30_anios_reanalisis_y_no_confundirlo_con_estacion(self):
  j=self.summary
  self.assertEqual(j["periodo_objetivo"],"1996-2025")
  self.assertEqual(j["n_testigos_reanalisis_30anios"],81)
  self.assertEqual(j["n_normales_mes_testigo_reanalisis"],972)
  self.assertEqual(j["n_normales_mes_sector"],504)
  self.assertEqual(j["n_sectores"],42)
  self.assertEqual(j["zonas_climaticas_homogeneas_certificadas"],0)
  self.assertFalse(j["validacion_externa_instrumental_independiente"])
  self.assertFalse(j["modelo_predictivo_validado_por_sectores"])
  self.assertTrue(j["contraste_CHIRPS_vs_ERA5_no_es_prueba_independiente"])
  self.assertEqual(j["numero_anios_completos_para_normales_chirps"],
     len(j["anios_chirps_con_12_meses"]))
 def test_normal_anual_solo_con_anios_completos(self):
  for x in self.summary["resumen_sectores"]:
   self.assertFalse(x["homogeneidad_climatica_certificada"])
   self.assertFalse(x["prediccion_fitosanitaria_validada"])
   self.assertLessEqual(x["n_anios_completos"],
      self.summary["numero_anios_completos_para_normales_chirps"])
   if not x["n_anios_completos"]:
    self.assertIsNone(x["precipitacion_anual_media_mm"])
   elif x["precipitacion_anual_media_mm"] is not None:
    self.assertGreaterEqual(x["precipitacion_anual_media_mm"],0)
  self.assertEqual(self.summary["n_sectores_sin_pixel_chirps_valido"],
    len(self.summary["sectores_sin_pixel_chirps_valido"]))
 def test_pares_hidrologicos_y_testigos_no_equivalen_a_clima_certificado(self):
  j=self.summary
  self.assertEqual(j["n_familias_comparadas"],3)
  self.assertEqual(j["n_pares_sector_misma_unidad_hidrografica"],
     len(j["candidatos_hidro_climaticos"]))
  for c in j["candidatos_hidro_climaticos"]:
   self.assertFalse(c["fusion_climatica_validada"])
   self.assertTrue(c["mismo_piso"])
  for r in j["comparaciones_testigos_nucleos"]:
   self.assertFalse(r["reanálisis_independencia_validada"])
 def test_ux_conserva_cinco_rutas(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count("<section data-page="),5)
  for id in ("oaf-9o-visor","oaf-9o-plot","oaf-9o-sector",
     "oaf-9o-status","oaf-9o-validation","oaf-9o-pairs"):
   self.assertEqual(h.count('id="'+id+'"'),1,id)
  self.assertIn("modelos/visor_homogeneidad_9o.js",h)
  self.assertIn("FASE_9O_HOMOGENEIDAD_CLIMATICA.md",h)
 def test_series_reproducibles_sin_redescargar_tiff(self):
  ch.check()
  dx.save(check=True)

if __name__=="__main__":
 unittest.main()
