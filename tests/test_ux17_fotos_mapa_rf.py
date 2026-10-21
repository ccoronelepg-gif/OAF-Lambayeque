"""Auditoría de integridad estática de imágenes y datos RF OAF UX17."""
from pathlib import Path
import json,unittest,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
def load(name):return (ROOT/name).read_text(encoding="utf-8")
class IntegrityTest(unittest.TestCase):
 def test_local_fallback_svg_is_renderable(self):
  for name in ("assets/oaf-sin-foto-patogeno.svg","assets/oaf-sin-foto-envase.svg"):
   tree=ET.parse(ROOT/name)
   self.assertTrue(tree.getroot().tag.endswith("svg"))
   self.assertIn("viewBox",tree.getroot().attrib)
 def test_gallery_images_refer_to_existing_local_assets(self):
  d=json.loads(load("datos/galeria_sanidad_2026.json"))
  self.assertEqual(len(d["organismos"]),23)
  for id,entry in d["organismos"].items():
   self.assertTrue(entry["url"],id)
   self.assertTrue(entry.get("source"),id)
   if entry["url"].startswith("assets/"):
    p=ROOT/entry["url"]
    self.assertTrue(p.is_file(),entry["url"])
    self.assertTrue(p.read_bytes().startswith(b"\xff\xd8"),entry["url"])
    self.assertTrue(entry.get("copia_local_licencia"),id)
 def test_photo_and_map_controls_installed(self):
  html=load("index.html")
  for name in ("oaf-ux17-imagenes-mapas.js","oaf-ux17-fotos-mapas.css"):
   self.assertIn(name,html)
  css=load("assets/oaf-ux17-fotos-mapas.css")
  self.assertIn("object-fit:contain",css.replace(" ",""))
  chart=load("ecorregiones-clima-10k.html")
  for name in ("oaf-ux17-opacity","oaf-ux17-borders","oaf-ux17-reset-view"):
   self.assertIn(name,chart)
 def test_rf_backtest_keeps_honest_provenance(self):
  data=json.loads(load("datos/rf_experimental_ux15.json"))
  self.assertFalse(data["operativo_certificado"])
  self.assertFalse(data["alertas_automaticas"])
  if data["estado"]=="candidato_experimental_generado":
   score=data["metrica_mensual"]
   self.assertIn("mae_climatologia_local_mm",score)
   self.assertEqual(score["seleccion_solo_validacion"].split(";")[0],"2019-2020")
   back=score.get("evaluacion_multihorizonte")
   self.assertIsNotNone(back)
   self.assertEqual([x["meses_adelante"] for x in back["por_horizonte"]],list(range(1,7)))
   self.assertEqual(set(data["escenarios_mensuales_rf_experimentales"]),{"Chiclayo","Jayanca","Motupe","Olmos"})
   for rows in data["escenarios_mensuales_rf_experimentales"].values():
    self.assertEqual(len(rows),6)
    self.assertTrue(all(x["requiere_validacion_prospectiva"] is True for x in rows))
if __name__=="__main__":unittest.main()
