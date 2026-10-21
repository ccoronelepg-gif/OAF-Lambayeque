"""UX-11: sólo dos bloques visibles de Cultivos y Boletines, catálogo fiable."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"index.html").read_text("utf-8")
SCHEMA=json.loads((ROOT/"datos/sanidad_agroexportadora_2026.json").read_text("utf-8"))
BUL=json.loads((ROOT/"datos/boletines_institucionales_2026.json").read_text("utf-8"))
LAYOUT=(ROOT/"assets/oaf-ux11-estructura.js").read_text("utf-8")
SAN=(ROOT/"assets/oaf-ux11-sanidad.js").read_text("utf-8")
NEWS=(ROOT/"assets/oaf-ux11-boletines.js").read_text("utf-8")

class SanidadBoletinesUX11(unittest.TestCase):
    def test_six_crops_and_twenty_three_organisms(self):
        self.assertEqual(len(SCHEMA["cultivos"]),6)
        self.assertEqual({x["id"] for x in SCHEMA["cultivos"]},
                         {"mango","vid","arandano","palto","maracuya","banano"})
        self.assertEqual(len(SCHEMA["organismos"]),23)
        self.assertEqual(len({x["id"] for x in SCHEMA["organismos"]}),23)
        self.assertEqual(len([o for o in SCHEMA["organismos"] if o["tipo"]=="plaga"]),12)
        self.assertEqual(len([o for o in SCHEMA["organismos"] if o["tipo"]=="enfermedad"]),11)
        for o in SCHEMA["organismos"]:
            for attr in ("dano","modelo_nota","manejo_cultural","vigilancia","agentes","fuente","clasificacion"):
                self.assertTrue(o.get(attr), (o["id"],attr))
            self.assertIn(o["clasificacion"],{"temperatura","humedad","suelo","estres","bioseguridad"})
            self.assertTrue(o["referencias"])
            self.assertTrue(all(urlparse(x).scheme=="https" for x in o["referencias"]))
            for p in o["productos"]:
                for key in ("nombre","ingrediente","registro","fuente","nota","tipo"):
                    self.assertTrue(p.get(key),(o["id"],key))
                self.assertEqual(urlparse(p["fuente"]).scheme,"https")

    def test_product_examples_are_checked_not_generic_doses(self):
        examples=[p["nombre"] for o in SCHEMA["organismos"] for p in o["productos"]]
        self.assertTrue(any("Luna Experience" in p for p in examples))
        self.assertTrue(any("Switch" in p for p in examples))
        self.assertTrue(any("Beauveria" in p for p in examples))
        self.assertTrue(any("Spinosad" in p for p in examples))
        self.assertIn("SIGIA",SCHEMA["aviso"])
        self.assertIn("R4T",SAN)
        self.assertIn("No se debe recomendar",SAN)
        self.assertNotIn("Math.random(",SAN)

    def test_two_blocks_each_metadata_preserved(self):
        ids=["oaf-sanidad-modelo","oaf-sanidad-manejo","oaf-boletines-informacion","oaf-boletines-evolucion"]
        for x in ids:self.assertEqual(LAYOUT.count('block("'+x+'"'),1)
        for x in ("oaf-archivo-cultivos-ux11","oaf-archivo-boletines-ux11","oaf-meta-legacy"):
            self.assertIn(x,LAYOUT)
        self.assertIn("ac.append(child)",LAYOUT)
        self.assertIn("an.append(child)",LAYOUT)
        self.assertIn("oaf:agro-ready",LAYOUT)
        self.assertIn("oaf:ux11-ready",LAYOUT)

    def test_weather_is_data_driven_no_false_disease_probabilities(self):
        for word in ("relative_humidity_2m","temperature_2m","precipitation_sum",
                     "forecast_days","oaf-sm-chart","oaf-sm-conclusion",
                     "No se puede estimar a partir de clima"):
            if word=="No se puede estimar a partir de clima":
                self.assertIn("NO puede predecirse por temperatura o lluvia",SAN)
            else:self.assertIn(word,SAN)
        self.assertIn("NaN" if "NaN" in SAN else "Number.isFinite",SAN)

    def test_official_bulletins_evidence(self):
        self.assertEqual(len(BUL["boletines"]),5)
        self.assertEqual(BUL["boletines"][0]["fecha"],"2026-10-16")
        self.assertEqual(BUL["boletines"][0]["institucion"],"ENFEN")
        self.assertEqual(BUL["boletines"][2]["institucion"],"NOAA CPC")
        for b in BUL["boletines"]:
            self.assertTrue(b["resumen"] and b["implicacion"])
            self.assertEqual(urlparse(b["url"]).scheme,"https")
        self.assertIn("datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv",NEWS)
        self.assertIn("no puede indicar por sí solo en qué día lloverá",LAYOUT)

    def test_integration_and_original_dom_ids(self):
        for p in ["assets/oaf-ux11-estructura.js","assets/oaf-ux11-sanidad.js",
                  "assets/oaf-ux11-boletines.js","assets/oaf-sanidad-boletines-ux11.css"]:
            self.assertIn(p,HTML)
            self.assertTrue((ROOT/p).exists())
        for id_ in ("oaf-nino-pred-data","oaf-control-cards","modelos-fitosanitarios",
                    "oaf-nino-predictive","oaf-8v-chart"):
            self.assertIn('id="'+id_+'"',HTML)
        self.assertEqual(HTML.count('<section data-page='),6)

if __name__=="__main__":unittest.main()
