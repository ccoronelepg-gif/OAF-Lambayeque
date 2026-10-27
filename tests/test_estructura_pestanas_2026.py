"""UX-7 · Estructura temática de seis pestañas sin regresión científica."""
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
BASE = json.loads((ROOT / "datos/ux_2026/auditoria_base_2026.json").read_text(encoding="utf-8"))
PAGES = ("inicio", "clima", "nino", "cultivos", "autor", "verificaciones")
COUNT_PER_PAGE = {"inicio": 6, "clima": 9, "nino": 5, "cultivos": 3, "autor": 7, "verificaciones": 5}

class CatalogParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.pages = []
        self.groups = {}
        self.targets = {}
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "section" and a.get("data-page"):
            self.pages.append(a["data-page"])
        if tag == "aside" and a.get("data-oaf-outline"):
            key = a["data-oaf-outline"]
            self.groups[key] = []
        if tag == "a" and "oaf-outline-item" in a.get("class", "").split():
            group = next((v.get("data-oaf-outline") for t, v in reversed(self.stack) if v.get("data-oaf-outline")), None)
            assert group is not None, "Acceso temático fuera de su índice"
            self.groups[group].append(a.get("href"))
            self.targets[a.get("href")] = group
        if tag not in {"meta", "link", "img", "br", "hr", "input", "source", "area", "wbr", "embed", "param"}:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                return

class EstructuraPestanas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = CatalogParser()
        cls.dom.feed(HTML)

    def test_six_existing_routes_preserved(self):
        self.assertEqual(tuple(self.dom.pages), ("inicio", "clima", "nino", "cultivos", "autor", "verificaciones"))
        self.assertEqual(set(self.dom.groups), set(PAGES))
        self.assertEqual(dict((k, len(v)) for k, v in self.dom.groups.items()), COUNT_PER_PAGE)

    def test_all_prior_public_ids_and_scripts_preserved(self):
        old_ids = set(BASE["ids_conservar"])
        self.assertFalse(old_ids - set(self.dom.ids))
        self.assertEqual(len(self.dom.ids), len(set(self.dom.ids)))
        scripts = re.findall(r'<script\b[^>]*src="([^"]+)"', HTML)
        expected = BASE["scripts_orden_de_carga"]
        # Respetar rutas y orden, pero no imponer la versión antigua ?v del caché.
        script_paths = [src.split("?", 1)[0] for src in scripts]
        expected_paths = [src.split("?", 1)[0] for src in expected]
        idx = [script_paths.index(name) for name in expected_paths]
        self.assertEqual(idx, sorted(idx))
        self.assertEqual(HTML.count('id="oaf-altitudinal-map"'), 1)
        self.assertIn('id="oaf-research-deep"', HTML)

    def test_all_navigation_targets_exist(self):
        ids = set(self.dom.ids)
        # La sección de coordenadas de clima es un componente DOM creado por JavaScript.
        area_js = (ROOT / "assets/oaf-territorio-compartido.js").read_text(encoding="utf-8")
        self.assertIn('wrap.id="oaf-area-"+k', area_js)
        self.assertIn('clima:()=>$("oaf-history")', area_js)
        allowed_aliases = {"cultivos", "prediccion", "oaf-area-clima"}
        for page, targets in self.dom.groups.items():
            for href in targets:
                with self.subTest(page=page, href=href):
                    self.assertTrue(href and href.startswith("#"))
                    self.assertTrue(href[1:] in ids or href[1:] in allowed_aliases)
        self.assertEqual(sum(map(len, self.dom.groups.values())), 35)

    def test_all_new_assets_are_used_and_present(self):
        for name in ("assets/oaf-estructura-pestanas-2026.css",
                     "assets/oaf-estructura-pestanas-2026.js"):
            self.assertTrue((ROOT / name).is_file())
            self.assertIn(name, HTML)
        js = (ROOT / "assets/oaf-estructura-pestanas-2026.js").read_text(encoding="utf-8")
        self.assertIn("requestAnimationFrame", js)
        self.assertNotIn("replaceChildren()", js)
        self.assertNotIn("remove()", js)

    def test_index_is_not_a_replacement_for_scientific_content(self):
        for anchor in ("oaf-senamhi-estaciones-10m", "oaf-9k-visor",
                       "oaf-9q-visor", "oaf-nino-pred-data",
                       "oaf-control-cards", "oaf-rf-unico-lluvias-10i",
                       "oaf-meta-hub", "oaf-9j-visor"):
            self.assertIn('id="' + anchor + '"', HTML)
        for notice in ("NO pronóstico", "en validación", "Fuente", "incertidumbre"):
            self.assertIn(notice.lower(), HTML.lower())

if __name__ == "__main__":
    unittest.main()
