"""Integridad y honestidad científica OAF 9H (sin requerir Internet)."""
import csv
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"datos/validacion_estaciones_9h"
GEO=json.loads((ROOT/"datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json").read_text("utf8"))
GRID=json.loads((F/"comparacion_observacional_9h.json").read_text("utf8"))
ERA=json.loads((F/"contraste_era5_complementario_9h.json").read_text("utf8"))

def csv_read(path):
    with path.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))

class Contraste9H(unittest.TestCase):
    def test_origins_and_external_data(self):
        self.assertEqual(GRID["fase"],"9H")
        self.assertEqual(ERA["fase"],"9H")
        self.assertEqual(len(GEO["estaciones"]),3)
        self.assertFalse(GRID["emplazamiento_historico_9g_certificado"])
        self.assertFalse(ERA["emplazamientos_historicos_9g_resueltos"])
        self.assertFalse(GRID["habilidad_predictiva_operativa_certificada"])
        self.assertFalse(ERA["validacion_predictiva_operativa"])
        self.assertFalse(GRID["comparacion_chirps_independiente"])
        self.assertFalse(ERA["normal_1996_2025_completa"])

    def test_chirps_1998_exact_period(self):
        pairs=csv_read(F/"pares_mensuales_9h.csv")
        chirps=[p for p in pairs if p["producto"]=="CHIRPS-v3 mensual LATAM"]
        self.assertEqual(len(chirps),GRID["n_pares_chirps"])
        self.assertEqual(len(chirps),72)
        self.assertEqual(len({(r["codigo_archivo"],r["mes"]) for r in chirps}),36)
        self.assertTrue(all(r["mes"].startswith("1998-") for r in chirps))
        src={x["sha256"] for x in GRID["fuentes_descargadas"]}
        self.assertEqual(len([x for x in GRID["fuentes_descargadas"] if x["producto"].startswith("CHIRPS")]),12)
        self.assertTrue(all(r["sha256_respuesta"] in src and len(r["sha256_respuesta"])==64 for r in chirps))
        self.assertEqual(GRID["n_pares_era5"],0)
        self.assertFalse(GRID["emisiones_historicas_pronostico_con_vintage"])

    def test_era5_not_renamed_to_era5_land(self):
        pairs=csv_read(F/"pares_era5_complementarios_9h.csv")
        rain=[r for r in pairs if r["variable"]=="precipitation_sum"]
        self.assertEqual(len(rain),ERA["n_pares_era5_precipitacion"])
        self.assertEqual(len(rain),1276)
        self.assertEqual(len({(r["codigo_archivo"],r["mes"]) for r in rain}),638)
        self.assertTrue(all(r["producto"]=="ERA5_atmosferico" for r in rain))
        self.assertIn("No soportada directamente",ERA["era5_land_precipitacion"])
        self.assertEqual(len(ERA["fuentes_sha256"]),2)
        shas={x["sha256"] for x in ERA["fuentes_sha256"]}
        self.assertTrue(all(r["sha256_respuesta"] in shas for r in rain))
        temp=ERA["n_pares_era5_land_temperatura"]
        if temp==0:
            self.assertIn("ERA5-Land_temperatura",ERA["errores_descarga"])
        self.assertEqual(sum(r["variable"]!="precipitation_sum" for r in pairs),temp)

    def test_spatial_sensitivity_puchaca(self):
        rows=[s for s in GRID["sensibilidad_de_celdas"] if s["nombre"]=="Puchaca"]
        self.assertEqual(len(rows),2)
        self.assertTrue(all(s["mismo_centro_celda_entre_escenarios"] is False for s in rows))
        self.assertEqual(next(s for s in rows if s["producto"].startswith("CHIRPS"))["n_meses_1998_escenario_1"],12)
        q=next(s for s in rows if s["producto"].startswith("CHIRPS"))
        self.assertAlmostEqual(q["centros_separados_km"],5.56,places=2)
        era=[a for a in ERA["sintesis"] if a["nombre"]=="Puchaca" and a["producto"]=="ERA5_atmosferico"]
        self.assertEqual(len(era),2)
        self.assertNotEqual(era[0]["centro_celda"],era[1]["centro_celda"])
        self.assertNotEqual(era[0]["metricas_periodo"]["mae"],era[1]["metricas_periodo"]["mae"])

    def test_symmetric_statistics_and_complete_months(self):
        observed={}
        with (ROOT/"datos/estaciones_9d/series_mensuales_9d.csv").open(newline="",encoding="utf8") as f:
            for r in csv.DictReader(f):
                observed[(r["codigo"],r["mes"])]=r
        for fp in ("pares_mensuales_9h.csv","pares_era5_complementarios_9h.csv"):
            rows=csv_read(F/fp)
            self.assertEqual(len(rows),len({(r["codigo_archivo"],r["escenario"],r["producto"],r.get("variable","precipitation"),r["mes"]) for r in rows}))
            for r in rows:
                station=observed[(r["codigo_archivo"],r["mes"])]
                self.assertEqual(int(station["precip_dias_validos"]) if "precipitation_sum" in r.get("variable","precipitation_sum") or r.get("variable")=="" else int(station["tmax_dias_validos"] if "max" in r["variable"] else station["tmin_dias_validos"]),int(station["dias_calendario"]))
                if "precipitacion_producto_mm" in r:
                    v=float(r["precipitacion_producto_mm"]);o=float(r["precipitacion_estacion_mm"]);diff=float(r["diferencia_producto_menos_estacion_mm"])
                else:
                    v=float(r["reanálisis"]);o=float(r["observado"]);diff=float(r["diferencia_reanalisis_menos_observado"])
                self.assertTrue(math.isfinite(o) and math.isfinite(v))
                self.assertAlmostEqual(v-o,diff,delta=0.0002)

    def test_website_and_sources_visible(self):
        h=(ROOT/"index.html").read_text(encoding="utf8")
        a=h.index('<section data-page="clima"')
        b=h.index('<section data-page="nino"',a)
        within=h[a:b]
        for fragment in (
            'id="oaf-9h-visor"','id="oaf-9h-site"','id="oaf-9h-scenario"',
            'id="oaf-9h-plot"','id="oaf-9h-state"',
            "FASE_9H_CONTRASTE_INSTRUMENTAL.md",
            "datos/validacion_estaciones_9h/contraste_era5_complementario_9h.json"):
            self.assertIn(fragment,within)
        self.assertIn('src="modelos/visor_contraste_estaciones_9h.js"',h)
        self.assertIn('href="assets/oaf-contraste-estaciones-9h.css?v=1"',h)
        self.assertEqual(h.count('id="oaf-9h-visor"'),1)
        self.assertEqual(h.count('id="oaf-altitudinal-map"'),1)
        self.assertEqual(h.count('<section data-page='),5)

if __name__=="__main__":unittest.main()
