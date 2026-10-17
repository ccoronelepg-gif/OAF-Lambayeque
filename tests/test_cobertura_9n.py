"""Fase 9N: controles de fuentes multipieza, cobertura y distinción científica."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from shapely.geometry import shape
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import cobertura_multitesela_9n as m

class CopernicusMultitesela9N(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=m.load_json(m.STATE)
  cls.mani=m.load_json(m.MANIFEST)
  cls.rows=m.load_json(m.ROW_FILE)
  cls.geo=m.load_json(m.GEO)

 def test_fuentes_geo_y_huellas_originales(self):
  a=self.mani
  self.assertEqual(a["fase"],"9N")
  self.assertEqual(len(a["teselas_requeridas"]),self.report["teselas_necesarias"])
  self.assertEqual(len(a["teselas_que_pudieron_abrirse"]),self.report["teselas_archivadas_validas"])
  for src in a["teselas_que_pudieron_abrirse"]:
   path=ROOT/src["path"]
   self.assertTrue(path.is_file())
   self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),src["sha256"])
   self.assertEqual(src["crs"],"EPSG:4326")
  for item in a["teselas_que_no_pudieron_comprobarse"]:
   self.assertTrue(item["no_inferir_elevacion_cero"])

 def test_42_sectores_contados_sin_inventar_cobertura(self):
  r=self.report
  self.assertEqual(r["n_sectores_9k"],42)
  self.assertEqual(len(self.rows),42)
  self.assertEqual(len({x["id_sector"] for x in self.rows}),42)
  self.assertEqual(r["n_sectores_cobertura_completa"]+
                   r["n_sectores_cobertura_parcial"]+
                   r["n_sectores_sin_dem"],42)
  self.assertEqual(r["n_geometrias_filtro"],len(self.geo["features"]))
  self.assertGreaterEqual(r["n_sectores_evaluables"],35)
  self.assertEqual(r["n_zonas_agroclimaticas_homogeneas_validadas"],0)
  self.assertEqual(r["cuencas_ana_oficialmente_ratificadas"],0)
  self.assertFalse(r["ajuste_altitudinal_nmme_validado"])
  self.assertFalse(r["alertas_fitosanitarias_derivadas"])

 def test_coherencia_de_pendiente_y_cambios_entre_resoluciones(self):
  for row in self.rows:
   self.assertFalse(row["zona_homogenea_instrumental_validada"])
   if row["cobertura"]=="sin_dem":
    self.assertIsNone(row["compatible_270m_30"])
    self.assertIsNone(row["diferencia_abs_30_270_vs_450"])
    continue
   self.assertTrue(0<row["fraccion_geometrica_teselas_leidas"]<=1)
   for resolution in (270,450):
    values=[row[f"compatible_{resolution}m_{t}"] for t in (20,30,40)]
    self.assertTrue(all(isinstance(v,(float,int)) and 0<=v<=1 for v in values))
    self.assertLessEqual(values[0],values[1])
    self.assertLessEqual(values[1],values[2])
   self.assertLessEqual(row["diferencia_abs_30_270_vs_450"],1)

 def test_geometria_contenida_en_sector_9k(self):
  prev=m.load_json(m.PREV)["features"]
  origin={x["properties"]["id_sector"]:shape(x["geometry"]) for x in prev}
  for feat in self.geo["features"]:
   p=feat["properties"];geom=shape(feat["geometry"])
   self.assertTrue(geom.is_valid)
   self.assertIn(p["sector_9k"],origin)
   self.assertFalse(p["zona_homogenea_validada"])
   self.assertFalse(p["riesgo_fitosanitario_validado"])
   self.assertLess(geom.difference(origin[p["sector_9k"]].buffer(.00001)).area,1e-8)

 def test_reproducibilidad_offline_y_navegacion(self):
  m.run(check=True)
  html=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(html.count("<section data-page="),5)
  for name in ("oaf-9n-visor","oaf-9n-summary","oaf-9n-map",
               "oaf-9n-table","oaf-9n-status","oaf-9n-tile-status"):
   self.assertEqual(html.count('id="'+name+'"'),1,name)
  self.assertIn("modelos/visor_multitesela_9n.js",html)
  self.assertIn("FASE_9N_COBERTURA_MULTITESELA.md",html)

if __name__=="__main__":
 unittest.main()
