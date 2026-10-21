"""Fase UX-9: imagen, legibilidad, fuentes y visualizadores sin alterar investigación OAF."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"index.html").read_text(encoding="utf-8")
FILES=["assets/oaf-hero-monitoreo-agroclimatico.svg",
       "assets/oaf-ux9-refinamiento.css",
       "assets/oaf-ux9-estructura.js",
       "assets/oaf-ux9-lectura-clima.js",
       "assets/oaf-ux9-mapa-sectores.js",
       "assets/oaf-ux9-predicciones.js"]

class UX9(unittest.TestCase):
    def test_hero_replaced_by_scientific_illustration(self):
        self.assertIn('src="assets/oaf-hero-monitoreo-agroclimatico.svg"',PAGE)
        self.assertNotIn('src="https://commons.wikimedia.org/wiki/Special:FilePath/Blueberry_close_up.jpg?width=700"',PAGE)
        svg=(ROOT/FILES[0]).read_text("utf-8")
        for text in ("MONITOREO AGROCLIMÁTICO","Territorio y estaciones","Análisis y predicción"):
            self.assertIn(text,svg)
        self.assertIn("<svg",svg)

    def test_all_ux9_assets_exist_and_loaded(self):
        for f in FILES:
            self.assertTrue((ROOT/f).is_file(),f)
            self.assertIn(f,PAGE)
        css=(ROOT/FILES[1]).read_text("utf-8")
        self.assertIn("text-align:justify",css)
        self.assertIn("oaf-plain-weather",css)

    def test_only_responsible_forecasts_and_enso(self):
        js=(ROOT/FILES[5]).read_text("utf-8")
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
        js=(ROOT/FILES[4]).read_text("utf-8")
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
        structure=(ROOT/FILES[2]).read_text("utf-8")
        self.assertIn("archivedHome.append",structure)
        self.assertIn("archivedAutor.append",structure)
        self.assertIn("oaf:ux9-ready",structure)

if __name__=="__main__":
    unittest.main()
