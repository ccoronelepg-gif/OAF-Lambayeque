"""9W: origen de 39 sectores, validación temporal y derechos de los resultados."""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import puente_validacion_9w as bridge

class Evidence9W(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=bridge.obj(bridge.MANIFEST)
  cls.evidence=bridge.obj(bridge.EVIDENCE)
 def test_controles_fuentes_y_particiones(self):
  s=self.source
  self.assertEqual(s["meses_CHIRPS_final_verificados"],360)
  self.assertEqual(s["n_poligonos_9k"],42)
  self.assertEqual(s["n_sectores_aptos_historia_CHIRPS"],39)
  self.assertEqual(s["filas_matriz_auditada"],39*360)
  self.assertEqual(s["sectores_sin_celda_CHIRPS"],["S028","S032","S034"])
  self.assertEqual(s["conteo_por_fase"],{"9O":108,"9P":12,"9Q":240})
  self.assertEqual(s["auditoria_de_objetivos_9R"]["n_comparaciones"],2340)
  self.assertEqual(s["auditoria_de_objetivos_9R"]["incongruencias"],0)
  self.assertTrue(s["modelo_9R_ya_ejecutado"])
  self.assertTrue(s["notas_9S_9V_anteriores_desactualizadas"])
 def test_comparacion_bloques_y_modelos(self):
  a=self.evidence
  self.assertEqual(a["fase"],"9W")
  by={p["protocolo"]:p for p in a["modelos_y_pruebas"]}
  self.assertEqual(set(by),{"9R","9R_2022_2025","9T"})
  self.assertEqual(by["9R"]["anios_prueba"],[2021,2022,2023,2024,2025])
  self.assertEqual(by["9R"]["casos_sector_mes_por_modelo"],2340)
  self.assertEqual(by["9R_2022_2025"]["casos_sector_mes_por_modelo"],1872)
  self.assertEqual(by["9T"]["casos_sector_mes_por_modelo"],1872)
  self.assertEqual(set(by["9R"]["metrica_modelos"]),{"climatologia","random_forest","gcn"})
  self.assertEqual(set(by["9T"]["metrica_modelos"]),{"climatologia","random_forest","persistencia"})
  for p in a["modelos_y_pruebas"]:
   for m in p["metrica_modelos"].values():
    self.assertEqual(m["n"],p["casos_sector_mes_por_modelo"])
    self.assertGreaterEqual(m["mae_mm"],0)
    self.assertGreaterEqual(m["rmse_mm"],m["mae_mm"])
   for cmp in p["comparacion_errores_emparejados"].values():
    self.assertEqual(cmp["n_bloques_anio"],len(p["anios_prueba"]))
    self.assertEqual(cmp["n_remuestras_exactas"],len(p["anios_prueba"])**len(p["anios_prueba"]))
    self.assertLessEqual(cmp["intervalo_bootstrap_anual_95_pct_mm"][0],
                         cmp["intervalo_bootstrap_anual_95_pct_mm"][1])
 def test_limites_operativos(self):
  a=self.evidence
  self.assertFalse(a["modelo_operativo_habilitado"])
  self.assertFalse(a["validacion_espacial_con_sectores_ausentes_en_entrenamiento"])
  self.assertFalse(a["verificacion_as_issued_de_variables_rezagadas"])
  self.assertFalse(a["alertas_fitosanitarias_emitidas"])
  self.assertTrue(a["GCN_de_9R_arquitectura_de_grafos_no_CNN_convolucion_2D"])
  self.assertFalse(a["comparar_mae_9R_vs_9T_para_elegir_modelo"])
 def test_csv_y_procedencia(self):
  with bridge.BRIDGE.open(newline="",encoding="utf8") as f:
   reader=csv.DictReader(f)
   self.assertEqual(reader.fieldnames,["sector_id","mes","lluvia_mm"])
   self.assertEqual(sum(1 for _ in reader),39*360)
  self.assertEqual(bridge.hashfile(bridge.BRIDGE),self.source["sha256_matriz_nueva"])
  self.assertEqual(bridge.hashfile(bridge.GEOMS),self.source["sha256_poligonos"])
  with bridge.FLOOR.open(newline="",encoding="utf8") as f:
   self.assertEqual(len(list(csv.DictReader(f))),3*7*3)
  with bridge.YEAR.open(newline="",encoding="utf8") as f:
   self.assertEqual(len(list(csv.DictReader(f))),5*3+4*3+4*3)
 def test_web_y_metodo(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count("<section data-page="),5)
  for s in ("oaf-9w-visor","oaf-9w-grid","oaf-9w-status",
            "oaf-9w-comparison","oaf-9w-details"):
   self.assertEqual(h.count('id="'+s+'"'),1,s)
  self.assertIn("visor_evidencia_9w.js",h)
  self.assertIn("FASE_9W_RECONCILIACION_PREDICTIVA.md",h)
if __name__=="__main__":unittest.main()
