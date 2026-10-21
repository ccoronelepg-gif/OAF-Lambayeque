"""Fase UX-9: imagen, legibilidad, fuentes y visualizadores sin alterar investigación OAF."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"index.html").read_text(encoding="utf-8")
FILES=["assets/oaf-ux9-refinamiento.css",
       "assets/oaf-ux9-estructura.js",
       "assets/oaf-ux9-lectura-clima.js",
       "assets/oaf-ux9-mapa-sectores.js",
       "assets/oaf-ux9-predicciones.js"]

class UX9(unittest.TestCase):
    def test_user_supplied_banner_is_local_and_uncropped(self):
        self.assertIn('src="assets/oaf-portada-proporcionada-2026.jpg?v=ux10-20261021"',PAGE)
        self.assertTrue((ROOT/"assets/oaf-portada-proporcionada-2026.jpg").is_file())
        self.assertGreater((ROOT/"assets/oaf-portada-proporcionada-2026.jpg").stat().st_size, 250_000)
        self.assertIn("Los números de esta imagen son ilustrativos.",PAGE)
        self.assertNotIn('src="assets/oaf-hero-monitoreo-agroclimatico.svg"',PAGE)

    def test_intro_single_centered_paragraph(self):
        agro=(ROOT/"assets/oaf-agroexportacion-2026.js").read_text("utf-8")
        structure=(ROOT/"assets/oaf-ux9-estructura.js").read_text("utf-8")
        css=(ROOT/"assets/oaf-ux9-refinamiento.css").read_text("utf-8")
        self.assertIn('const intro=node("div","oaf-agro-summary"',agro)
        self.assertIn('Ciencia de datos y agricultura de agroexportación',agro)
        self.assertNotIn("const ten=[",agro)
        self.assertNotIn("oaf-intro-columns",structure)
        self.assertNotIn("column-count:2",css)
        self.assertIn("text-align:center!important",css)
        paragraph=agro.split('const intro=node("div","oaf-agro-summary"',1)[1].split(";\n",1)[0]
        self.assertEqual(paragraph.count("<p>"),1)
        self.assertLessEqual(len(paragraph.split()),75)
        self.assertIn('id="oaf-home-summary-static"',PAGE)

    def test_all_ux9_assets_exist_and_loaded(self):
        for f in FILES:
            self.assertTrue((ROOT/f).is_file(),f)
            self.assertIn(f,PAGE)
        css=(ROOT/FILES[0]).read_text("utf-8")
        self.assertIn("text-align:justify",css)
        self.assertIn("oaf-plain-weather",css)

    def test_only_responsible_forecasts_and_enso(self):
        js=(ROOT/FILES[4]).read_text("utf-8")
        for text in ("forecast_days","precipitation_sum","temperature_2m_max",
                     "oaf-ux9-final-lluvia","oaf-ux9-final-enso",
                     "datos/estado_enso_verificado_ux9_2026.json",
                     "datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv"):
            self.assertIn(text,js)
        self.assertNotIn("Math.random(",js)
        doc=json.loads((ROOT/"datos/estado_enso_verificado_ux9_2026.json").read_text("utf-8"))
        self.assertEqual(doc["enfen"]["numero"],"18-2026")
        self.assertEqual(doc["enfen"]["fecha_emision"],"2026-10-16")
        self.assertEqual(doc["noaa"]["fecha_emision"],"2026-10-08")
        self.assertIn("enfen.imarpe.gob.pe/",doc["enfen"]["fuente"])
        self.assertIn("cpc.ncep.noaa.gov/",doc["noaa"]["fuente"])

    def test_independent_geographic_map_from_published_geojson(self):
        js=(ROOT/FILES[3]).read_text("utf-8")
        self.assertIn("sectores_muestreo_9k.geojson",js)
        self.assertIn("data.features.length!==42",js)
        self.assertIn('oaf-ux9-map',js)
        self.assertIn('tabindex:0',js)
        self.assertIn("zona",js.lower())
        doc=json.loads((ROOT/"datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson").read_text("utf-8"))
        self.assertEqual(len(doc["features"]),42)
        self.assertFalse(doc["metadata"]["son_zonas_homogeneas_validadas"])

    def test_original_models_ids_and_router_survive(self):
        for key in ('id="oaf-altitudinal-map"','id="oaf-9k-visor"','id="oaf-research-deep"',
                    'id="oaf-home-analysis"','id="oaf-home-location"',
                    'data-page="clima"','data-page="autor"'):
            self.assertIn(key,PAGE)
        self.assertIn('oaf-agro-archive-autor',(ROOT/"assets/oaf-agroexportacion-2026.js").read_text("utf-8"))
        structure=(ROOT/FILES[1]).read_text("utf-8")
        self.assertIn("archivedHome.append",structure)
        self.assertIn("archivedAutor.append",structure)
        self.assertIn("oaf:ux9-ready",structure)

if __name__=="__main__":
    unittest.main()
