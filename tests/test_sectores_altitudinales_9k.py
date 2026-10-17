"""Regresión 9K: polígonos de soporte, franjas excluyentes y centros climáticos reales."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import sectores_altitudinales_9k as z

class Poligonos9K(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo,cls.rep,cls.assign=z.build()

    def test_inventario_y_pisos_fisicos(self):
        r=self.rep
        self.assertEqual(r["n_nodos_dem"],420)
        self.assertEqual(r["n_testigos_con_360_meses"],81)
        self.assertEqual(len(self.assign),420)
        self.assertEqual(len({q["id"] for q in self.assign}),420)
        self.assertEqual(sum(r["nodos_por_piso"].values()),420)
        self.assertTrue(all(q["estrato_fisico_preliminar"] in z.CLASSES for q in self.assign))

    def test_ningun_grupo_une_pisos_o_inventa_certificacion(self):
        r=self.rep
        self.assertEqual(r["n_zonas_homogeneas_certificadas"],0)
        self.assertEqual(r["n_sectores_agricolas_certificados"],0)
        self.assertFalse(r["validacion_espacial_de_pronosticos"])
        self.assertFalse(r["prediccion_elnino_costero_zonal_validada"])
        self.assertTrue(r["geometria_referencial_no_oficial"])
        self.assertEqual(len(self.geo["features"]),r["n_poligonos_graficos_exploratorios"])
        self.assertGreater(len(self.geo["features"]),7)
        for f in self.geo["features"]:
            p=f["properties"]
            self.assertFalse(p["zona_homogenea_validada"])
            self.assertFalse(p["pronostico_zonal_validado"])
            self.assertFalse(p["sector_agricola_certificado"])
            self.assertIn(p["estrato"],z.CLASSES)
            self.assertTrue(p["n_nodos_dem"]>=1)
            self.assertTrue(p["area_dibujo_km2"]>0)

    def test_geojson_valido_y_contenido_en_limite_referencial(self):
        from shapely.geometry import shape
        from shapely.ops import transform
        _,_,_,region=z.read()
        for f in self.geo["features"]:
            g=transform(z.PROJ,shape(f["geometry"]))
            self.assertTrue(g.is_valid)
            self.assertGreater(g.area,0)
            self.assertLess(g.difference(region.buffer(5)).area,100)

    def test_testigos_no_extrapolados_a_otro_piso(self):
        d,w,_,_=z.read()
        for x in self.assign:
            c=x["testigo_climatico_asociado"]
            if not c:continue
            self.assertIn(c,w)
            self.assertEqual(x["estrato_fisico_preliminar"],w[c]["estrato"])
            self.assertLessEqual(abs(float(x["altitud_dem_m"])-w[c]["alt"]),180.00001)
            self.assertLessEqual(float(x["distancia_testigo_km"]),12.001)

    def test_reproduccion_si_se_publico(self):
        if z.GEO.exists() and z.OUT.exists() and z.TABLE.exists():
            z.check()

if __name__=="__main__":unittest.main()
