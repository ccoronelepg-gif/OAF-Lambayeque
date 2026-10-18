"""Tests 10K — geometrias ecoexperimentales, métricas e independencia temporal."""
import sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import rf_ecopaisajes_10k as mod
class Tests10K(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.geo,cls.lookup,cls.floor=mod.catalog()
 def test_ecopaisajes_no_son_ecorregiones_oficiales(self):
  self.assertFalse(self.geo["metadata"]["es_mapa_oficial_MINAM"])
  self.assertFalse(self.geo["metadata"]["n_sectores_con_CHIRPS"]!=39)
  self.assertTrue(all(x["properties"]["categoria_ecologica_oficial"] is False for x in self.geo["features"]))
 def test_poligonos_39_tres_faltantes(self):
  self.assertEqual(len(self.geo["features"]),39)
  self.assertEqual(set(self.geo["metadata"]["poligonos_descartados_sin_CHIRPS"]),{"S028","S032","S034"})
  self.assertEqual(len(set(self.lookup)),39)
 def test_cinco_paisajes_y_siete_pisos(self):
  self.assertEqual(len(mod.CATEGORIES),5)
  self.assertEqual(len({z for g in mod.CATEGORIES.values() for z in g["pisos"]}),7)
  self.assertEqual(set(self.lookup.values()),set(mod.CATEGORIES))
 def test_no_altitud_negativa_ocultada(self):
  target=[f for f in self.geo["features"] if f["properties"]["sector"]=="S001"][0]
  self.assertTrue(target["properties"]["cota_negativa_pendiente"])
 def test_ecofeatures_sin_imputar_limpieza(self):
  nodes,A,edges,fixed,floors,polygon,data,audit=mod.base.previous.inputs()
  arr=mod.ones(nodes,self.lookup)
  self.assertEqual(arr.shape,(39,5))
  self.assertTrue(np.all(arr.sum(axis=1)==1))
  x=np.zeros((4,39,11),dtype=np.float32)
  joined=mod.append_eco(x,nodes,self.lookup)
  self.assertEqual(joined.shape,(4,39,16))
 def test_no_enfermedad_ni_horas_foliar(self):
  self.assertFalse(any("enfermedad" in c or "foliar" in c for c in mod.FIELD_NAMES))
  self.assertIn("estimado_rf_mm",mod.FIELD_NAMES)
  self.assertIn("prob_rf_p95",mod.FIELD_NAMES)
 def test_stats_evitan_repartir_incertidumbre_como_poblacion(self):
  self.assertIsNone(mod.stats([]))
  rows=[{"observado_mm":100,"estimado_rf_mm":80,"climatologia_mm":10,
    "prob_rf_p90":.8,"prob_ref_p90":.2,"prob_rf_p95":.6,"prob_ref_p95":.1,
    "evento_p90":1,"evento_p95":1,"limite_inf_90_mm":75,"limite_sup_90_mm":95,"sector":"S001"}]
  s=mod.stats(rows)
  self.assertEqual(s["mae_rf_mm"],20.)
  self.assertEqual(s["n_eventos_p95"],1)
  self.assertEqual(s["cobertura_intervalo_90_pct"],0.)
 def test_ventanas_sin_futuro(self):
  nodes,A,edges,fixed,floors,polygon,data,audit=mod.base.previous.inputs()
  x0,x1,y,raw,thr,dates,tr,va,ca,te=mod.base.matrix(nodes,fixed,data)
  self.assertEqual([int(mask.sum()) for mask in (tr,va,ca,te)],[228,36,24,60])
  self.assertEqual(dates[0],"1997-01")
  self.assertEqual(dates[-1],"2025-12")
if __name__=="__main__":unittest.main()
