"""Regresión científica de la fase agroexportadora OAF — octubre 2026."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"index.html").read_text("utf-8")
CATALOG=json.loads((ROOT/"datos/catalogo_cultivos_agroexportacion_2026.json").read_text("utf-8"))
ORIGINAL=json.loads((ROOT/"datos/ux_2026/auditoria_base_2026.json").read_text("utf-8"))

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.scripts=[]
        self.styles=[]
        self.pages=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get("id"):self.ids.append(attrs["id"])
        if tag=="script" and attrs.get("src"):self.scripts.append(attrs["src"])
        if tag=="link" and attrs.get("rel")=="stylesheet":self.styles.append(attrs.get("href",""))
        if tag=="section" and attrs.get("data-page"):self.pages.append(attrs["data-page"])

class AgroExportacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=Elements()
        cls.page.feed(HTML)

    def test_six_crops_with_plagues_diseases_and_scientific_links(self):
        expected={"mango","vid","arandano","palto","maracuya","banano"}
        self.assertEqual({x["id"] for x in CATALOG["cultivos"]},expected)
        self.assertEqual(len(CATALOG["cultivos"]),6)
        for crop in CATALOG["cultivos"]:
            self.assertGreaterEqual(len(crop["plagas"]),2,crop["id"])
            self.assertGreaterEqual(len(crop["enfermedades"]),1,crop["id"])
            self.assertTrue(crop["lectura"])
            for finding in crop["plagas"]+crop["enfermedades"]:
                for field in ("nombre","agentes","vigilancia","fuente"):
                    self.assertTrue(finding.get(field), (crop["id"],field))
                domain=urlparse(finding["fuente"])
                self.assertEqual(domain.scheme,"https")
                self.assertIn(domain.hostname, {"www.senasa.gob.pe","repositorio.inia.gob.pe","www.scielo.org.pe","ipm.ucanr.edu","www.gob.pe"})

    def test_all_original_scientific_ids_and_scripts_remain(self):
        self.assertEqual(len(self.page.ids),len(set(self.page.ids)),"Duplicate DOM IDs")
        self.assertFalse(set(ORIGINAL["ids_conservar"])-set(self.page.ids))
        for path in ORIGINAL["scripts_orden_de_carga"]:
            self.assertIn(path,self.page.scripts)
        old=[self.page.scripts.index(path) for path in ORIGINAL["scripts_orden_de_carga"]]
        self.assertEqual(old,sorted(old))
        self.assertEqual(tuple(self.page.pages),("inicio","clima","nino","cultivos","autor","verificaciones"))

    def test_new_js_and_styles_registered_and_content_contained(self):
        for path in ("assets/oaf-agroexportacion-2026.css",
                     "assets/oaf-agroexportacion-2026.js",
                     "assets/oaf-agro-charts-2026.js",
                     "assets/oaf-agro-crops-2026.js"):
            self.assertTrue((ROOT/path).is_file(),path)
            self.assertIn(path,HTML)
        core=(ROOT/"assets/oaf-agroexportacion-2026.js").read_text("utf-8")
        for marker in ("oaf-bloque-clima-actual","oaf-bloque-prediccion-inicio",
                       "oaf-bloque-cultivos-inicio","oaf-clima-bloque-historico",
                       "oaf-clima-bloque-modelo","oaf-clima-bloque-estaciones",
                       "oaf-agro-technical-archive","oaf-autor-pronosticos"):
            self.assertIn(marker,core)
        self.assertIn("guia-lectura-agroclimatica.html",HTML)
        self.assertIn("oaf-guide-link",HTML)

    def test_no_fake_model_outputs(self):
        charts=(ROOT/"assets/oaf-agro-charts-2026.js").read_text("utf-8")
        for expected in ("datos/lambayeque_mensual_era5_8d.csv",
                         "datos/muestreo_8o/nodos_dem_8o.csv",
                         "datos/validacion_estaciones_9f/identificacion_territorial_9f.json",
                         "datos/noaa_ersstv5_nino12_mensual.csv",
                         "precipitation_sum",
                         "cache"):
            self.assertIn(expected,charts)
        self.assertIn("NaN",charts)
        self.assertNotIn("Math.random",charts)
        self.assertNotIn("datos simulados",charts.lower())

if __name__=="__main__":unittest.main()
