"""9R QA: separación temporal, trazabilidad de CHIRPS, métricas GCN vs RF."""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import comparacion_gcn_rf_9r as exp

class ValidacionGCNvsRF(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads(exp.RESULT.read_text("utf8"))
  with exp.PRED.open(encoding="utf8",newline="") as f:
   cls.pred=list(csv.DictReader(f))
 def test_ensayo_temporal_no_mira_objetivos_futuros(self):
  j=self.report
  self.assertEqual(j["fase"],"9R")
  self.assertEqual(j["conjuntos"]["train"],"1997-01 a 2015-12")
  self.assertEqual(j["conjuntos"]["validacion"],"2016-01 a 2020-12")
  self.assertEqual(j["conjuntos"]["prueba_fuera_muestra"],"2021-01 a 2025-12")
  self.assertEqual(j["conjuntos"]["n_meses_entrenamiento"],228)
  self.assertEqual(j["conjuntos"]["n_meses_validacion"],60)
  self.assertEqual(j["conjuntos"]["n_meses_prueba"],60)
  self.assertEqual(j["origen_CHIRPS"]["meses_verificados"],360)
  self.assertTrue(j["conjuntos"]["mes_objetivo_desconocido_para_predictor"])
  self.assertTrue(j["conjuntos"]["serie_final_CHIRPS_revisada_a_posteriori"])
  self.assertFalse(j["pronostico_2026_comprobado"])
  self.assertEqual(j["n_modelos_operativamente_validados"],0)
  self.assertFalse(j["alertas_fitosanitarias_emitidas"])
  self.assertGreater(j["grafo"]["n_aristas_no_dirigidas"],0)
 def test_referencia_climatologica_y_errores(self):
  j=self.report
  self.assertEqual(set(j["metricas_prueba"]),set(exp.MODELS))
  self.assertEqual(j["n_predicciones_sector_mes_prueba"],len(self.pred))
  self.assertEqual(j["n_predicciones_sector_mes_prueba"],60*j["grafo"]["n_nodos_con_lluvia_valida"])
  for name,d in j["metricas_prueba"].items():
   self.assertEqual(d["n"],len(self.pred))
   self.assertGreaterEqual(d["mae_mm"],0)
   self.assertGreaterEqual(d["rmse_mm"],d["mae_mm"]-0.0002)
  self.assertIn(j["mejor_modelo_ml_por_mae"],("GCN","Random Forest"))
  self.assertIn(j["mejor_modelo_incluyendo_baseline_por_mae"],exp.MODELS)
 def test_per_sector_and_year_real_test_predictions(self):
  j=self.report
  self.assertEqual(len(j["metricas_por_anio_test"]),5)
  self.assertEqual(len(j["sensibilidad_cinco_anios_test_leave_one_year_out"]),5)
  self.assertEqual(len(j["comparacion_por_grupo_exploratorio_9q"]),7)
  self.assertEqual(sum(v["n_sector"] for v in j["comparacion_por_piso_altitudinal"].values()),
                   j["grafo"]["n_nodos_con_lluvia_valida"])
  for r in self.pred:
   self.assertGreaterEqual(r["mes_objetivo"],"2021-01")
   self.assertLessEqual(r["mes_objetivo"],"2025-12")
   for col in ("lluvia_observada_CHIRPS_mm","climatologia_entrenamiento_mm",
               "random_forest_mm","gcn_mm"):
    self.assertGreaterEqual(float(r[col]),0)
  for name,d in j["anomalia_lluvia_muy_alta_umbral_percentil80_train"].items():
   self.assertTrue(d["train_monthly_p80_threshold"])
   self.assertGreater(d["n_true_anomaly"],0)
 def test_no_leakage_de_anomalias_y_geometria(self):
  j=self.report
  self.assertTrue(j["grafo"]["construccion_sin_series_CHIRPS_de_entrenamiento_o_prueba"])
  self.assertTrue(any("normales ERA5" in x for x in j["variables_EXCLUIDAS_por_fuga_temporal"]))
  self.assertEqual(j["n_zonas_homogeneas_certificadas"],0)
  self.assertLessEqual(j["grafo"]["n_nodos_con_lluvia_valida"],42)
  self.assertEqual(j["modelo_GCN"]["graph_layers"],2)
  self.assertIn("val_mae_mm",j["modelo_RF"])
  self.assertIn("val_mae_mm",j["modelo_GCN"])
 def test_ui_no_elimina_rutas_ni_comparaciones(self):
  html=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(html.count("<section data-page="),5)
  for id in ("oaf-9r-visor","oaf-9r-winner","oaf-9r-chart",
             "oaf-9r-score-table","oaf-9r-floors","oaf-9r-groups",
             "oaf-9r-anomalies","oaf-9r-years","oaf-9r-status"):
   self.assertEqual(html.count('id="'+id+'"'),1,id)
  self.assertIn("visor_comparacion_9r.js",html)
  self.assertIn("FASE_9R_COMPARACION_GCN_RANDOM_FOREST.md",html)

if __name__=="__main__":unittest.main()
