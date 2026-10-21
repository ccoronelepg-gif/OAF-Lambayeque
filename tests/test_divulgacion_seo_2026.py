"""Control de calidad de la guía pública, enlaces e indexación OAF, octubre de 2026."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://ccoronelepg-gif.github.io/OAF-Lambayeque/"
GUIDE = ROOT / "guia-lectura-agroclimatica.html"
HOME = ROOT / "index.html"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

class DivulgacionSEO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = HOME.read_text(encoding="utf-8")
        cls.guide = GUIDE.read_text(encoding="utf-8")
        cls.dom = Links()
        cls.dom.feed(cls.guide)

    def test_human_readable_content_and_provenance(self):
        for text in ("Precipitación", "Humedad relativa",
                     "Déficit de presión de vapor", "Radiación solar",
                     "CHIRPS", "SENAMHI", "modelo", "El Niño",
                     "datos en tiempo real"):
            self.assertIn(text.casefold(), self.guide.casefold())
        self.assertIn('role="status"', self.guide)
        self.assertIn('name="description"', self.guide)
        self.assertIn('type="application/ld+json"', self.guide)

    def test_homepage_has_searchable_link(self):
        self.assertIn('href="guia-lectura-agroclimatica.html"', self.home)
        self.assertIn('rel="canonical"', self.home)
        self.assertIn('name="robots" content="index,follow', self.home)

    def test_guide_has_semantic_navigation_and_no_broken_local_hashes(self):
        self.assertIn('href="./#inicio"', self.guide)
        for href in self.dom.links:
            if href.startswith(("https:", "http:", "mailto:", "./#")):
                continue
            if href.startswith("#"):
                self.assertIn(href[1:], self.dom.ids)
                continue
            target = href.split("#")[0].split("?")[0]
            if target:
                self.assertTrue((GUIDE.parent / unquote(target)).is_file(), href)

    def test_sitemap_points_to_existing_files(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [i.text for i in tree.findall(".//s:loc", namespaces=ns)]
        self.assertGreaterEqual(len(urls), 5)
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn(SITE, urls)
        self.assertIn(SITE + GUIDE.name, urls)
        for url in urls:
            self.assertTrue(url.startswith(SITE), url)
            path = url[len(SITE):]
            self.assertTrue((ROOT / (path or "index.html")).is_file(), url)

if __name__ == "__main__":
    unittest.main()
