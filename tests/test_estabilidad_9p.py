"""9P: regresiones de fuente CHIRPS, años y no-certificación."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import estabilidad_climatica_9p as s
import mirror_chirps_9p as mirror

class Continuidad9P(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads(s.DIAG.read_text("utf8"))
  cls.source=json.loads(mirror.META.read_text("utf8"))
 def test_30_anios_no_imputados(self):
  j=self.report
  self.assertEqual(j["fase"],"9P")
  self.assertEqual(j["n_meses_historicos_objetivo"],360)
  self.assertEqual(j["n_meses_chirps_comprobados_total"]+
                   j["n_meses_no_comprobados"],360)
  self.assertEqual(j["n_meses_chirps_existentes_9o"],108)
  self.assertEqual(j["n_meses_chirps_agregados_9p"],self.source["n_meses_9p_nuevos"])
  self.assertEqual(sum(j["anios_por_decada_fuentes"].values()),j["n_anios_fuente_completos"])
  self.assertEqual(j["n_anios_fuente_completos"],len(j["anios_fuente_completos"]))
  self.assertEqual(j["periodo_chirps_30_anios_completo"],
                   j["n_meses_chirps_comprobados_total"]==360)
  self.assertEqual(j["sectores_9k_totales"],42)
  self.assertEqual(j["n_zonas_climaticamente_homogeneas_certificadas"],0)
  self.assertEqual(j["n_estaciones_independientes_1996_2025_por_sector"],0)
  self.assertFalse(j["precision_predictiva_de_alertas_validada"])
 def test_fuente_espejo_sin_mezcla_ilegitima(self):
  r=self.source
  self.assertEqual(r["fase"],"9P")
  self.assertEqual(r["n_meses_referencia_9o"],108)
  self.assertEqual(r["n_meses_objetivo"],360)
  self.assertEqual(r["n_meses_9p_nuevos"]+r["n_meses_referencia_9o"]+
                   r["n_meses_pendientes"],360)
  self.assertEqual(r["n_meses_9p_nuevos"],len(r["nuevos"]))
  self.assertTrue(r["ninguna_equivalencia_asumida_sin_prueba"])
  self.assertTrue(r["no_mezcla_productos_CHIRPS_v2_prelim"])
  if r["n_meses_9p_nuevos"]:
   self.assertTrue(r["mirroring_verificado"])
   self.assertEqual(len(r["comparaciones_equivalencia"]),2)
   self.assertTrue(all(v["producto_equivalente_en_celdas_lambayeque"]
                       for v in r["comparaciones_equivalencia"]))
  mirror.check()
 def test_pares_separados_de_certificacion(self):
  for pair in self.report["resumen_pares"]:
   self.assertIn(pair["par"],("S002_S003","S003_S004"))
   self.assertEqual(pair["estabilidad_climatica_certificada"],"false")
   self.assertLessEqual(pair["n_anios_comunes"],self.report["n_anios_fuente_completos"])
   for col in ("r_todos_meses","r_loyo_min","r_loyo_mediana","r_loyo_max"):
    val=pair[col]
    if val is not None:self.assertTrue(-1<=val<=1,(col,val))
   if pair["r_loyo_min"] is not None:
    self.assertLessEqual(pair["r_loyo_min"],pair["r_loyo_max"])
 def test_series_anuales_y_reproduccion(self):
  summary=s.save(check=True)
  self.assertEqual(summary["n_meses_chirps_comprobados_total"],self.report["n_meses_chirps_comprobados_total"])
  self.assertEqual(len(s.rows(s.ANNUAL)),42*30)
  self.assertEqual(len(s.rows(s.PAIRS)),2)
 def test_interfaz_cientifica_y_navegacion(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count("<section data-page="),5)
  for ident in ("oaf-9p-visor","oaf-9p-months","oaf-9p-years",
                "oaf-9p-source","oaf-9p-decades","oaf-9p-pairs","oaf-9p-conclusion"):
   self.assertEqual(h.count('id="'+ident+'"'),1,ident)
  self.assertIn("visor_estabilidad_9p.js",h)
  self.assertIn("FASE_9P_ESTABILIDAD_CLIMATICA.md",h)

if __name__=="__main__":unittest.main()
