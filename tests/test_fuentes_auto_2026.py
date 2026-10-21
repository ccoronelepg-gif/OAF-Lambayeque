"""Pruebas offline: nunca inventar un comunicado desde texto suelto."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from actualizar_fuentes_oaf_2026 import latest_enfen

class AutoFuentesTest(unittest.TestCase):
    def test_latest_verified_issued_link(self):
        html='''<a href="https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-17-2026/">Comunicado Oficial ENFEN N° 17-2026</a>
        <a href="https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-18-2026/">Comunicado Oficial ENFEN N° 18-2026</a>'''
        data=latest_enfen(html)
        self.assertEqual((data['anio'],data['numero']),(2026,18))
        self.assertTrue(data['url'].startswith('https://enfen.imarpe.gob.pe/'))
    def test_domain_must_be_institutional(self):
        html='<a href="https://noticias-privadas.example/comunicado">Comunicado Oficial ENFEN N° 19-2026</a>'
        with self.assertRaises(ValueError):latest_enfen(html)
    def test_unstructured_article_is_not_official_index(self):
        with self.assertRaises(ValueError):latest_enfen('<p>Comunicado Oficial ENFEN N° 30-2026</p>')
if __name__=='__main__':unittest.main()
