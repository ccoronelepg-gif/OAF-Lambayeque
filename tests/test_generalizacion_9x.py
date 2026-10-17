"""9X: reconstrucción espacial, trazabilidad y cero habilidad operativa atribuida."""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import generalizacion_espacial_9x as s

class GeoHoldout9X(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads(s.REPORT.read_text("utf8"))
  cls.folds=json.loads(s.FOLDS.read_text("utf8"))
  with s.PRED.open(encoding="utf8",newline="") as f:
   cls.pred=list(csv.DictReader(f))
 def test_five_geographic_blocks_distinct_and_no_shared_chirps_cell(self):
  r,f=self.report,self.folds
  self.assertEqual(r["fase"],"9X")
  self.assertEqual(f["fase"],"9X")
  self.assertEqual(r["n_sectores"],39)
  self.assertEqual(f["n_folds"],5)
  self.assertEqual(f["n_pixeles_compartidos_entre_bloques"],0)
  self.assertEqual(f["n_datos_de_lluvia_de_sectores_holdout_usados_para_fit"],0)
  self.assertEqual(r["n_predicciones_totales"],39*60*5)
  self.assertEqual(len(self.pred),39*60*5)
  allhold=[]
  for fold in f["folds"]:
   a=fold["sectores_holdout"];b=fold["sectores_train"]
   self.assertFalse(set(a)&set(b))
   self.assertEqual(len(a)+len(b),39)
   self.assertGreaterEqual(len(a),3)
   self.assertTrue(fold["holdout_excluded_from_train_and_validation_targets"])
   allhold.extend(a)
  self.assertEqual(len(allhold),len(set(allhold)))
  self.assertEqual(len(allhold),39)
 def test_months_and_sample_identical_for_each_model(self):
  models=set(s.MODELS);self.assertEqual(set(self.report["modelos"]),models)
  by={m:set() for m in models}
  observed={}
  for row in self.pred:
   model=row["modelo"];key=(row["mes"],row["sector"])
   self.assertIn(model,models)
   self.assertGreaterEqual(row["mes"],"2021-01")
   self.assertLessEqual(row["mes"],"2025-12")
   self.assertNotIn(key,by[model])
   by[model].add(key)
   true=float(row["observado_CHIRPS_mm"])
   self.assertGreaterEqual(true,0)
   self.assertGreaterEqual(float(row["predicho_mm"]),0)
   if key in observed:self.assertAlmostEqual(observed[key],true,places=5)
   else:observed[key]=true
  self.assertEqual(len(set(map(frozenset,by.values()))),1)
  self.assertEqual(len(observed),39*60)
 def test_stats_and_uncertainty(self):
  r=self.report
  self.assertEqual(set(r["metricas_globales"]),set(s.MODELS))
  for m,item in r["metricas_globales"].items():
   self.assertEqual(item["n"],39*60)
   self.assertGreaterEqual(item["mae_mm"],0)
   self.assertGreaterEqual(item["rmse_mm"],item["mae_mm"])
  for cmp in r["bootstrap_espacial_bloques"].values():
   self.assertEqual(cmp["n_bloques_geograficos"],5)
   self.assertEqual(cmp["remuestras_exactas"],3125)
   self.assertLessEqual(*cmp["rango_bootstrap_espacial_exploratorio_95_pct_mm"])
  self.assertEqual(len(r["metricas_por_anio"]),5*5)
  self.assertEqual(len(r["metricas_por_piso"]),7*5)
 def test_no_operational_approval(self):
  r=self.report
  self.assertFalse(r["validacion_SENAMHI_externa"])
  self.assertFalse(r["alertas_fitosanitarias_activadas"])
  self.assertFalse(r["comparable_directamente_con_9R_por_metricas"])
  self.assertEqual(r["n_modelos_operativos_autorizados"],0)
  self.assertFalse(r["climatologia_entrenada_solo_en_otros_sectores"] is False)
  self.assertTrue(r["version_original_as_issued_CHIRPS_no_conservada"])
  self.assertTrue(r["GCN_grafos_no_CNN_2D"])
  s.run(check=True)
 def test_portal_keeps_five_tabs_and_honest_labels(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count("<section data-page="),5)
  for id in ("oaf-9x-visor","oaf-9x-status","oaf-9x-winner",
             "oaf-9x-map","oaf-9x-legend","oaf-9x-map-caption",
             "oaf-9x-grid","oaf-9x-floor-table","oaf-9x-comparisons"):
   self.assertEqual(h.count('id="'+id+'"'),1,id)
  self.assertIn("modelos/visor_generalizacion_9x.js",h)
  self.assertIn("FASE_9X_GENERALIZACION_ESPACIAL.md",h)

if __name__=="__main__":
 unittest.main()
