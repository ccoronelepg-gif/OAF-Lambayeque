"""Pruebas offline 9I: no corrige a posteriori años, píxeles ni saldos faltantes."""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import analisis_multianual_9i as mod

class Evaluacion9I(unittest.TestCase):
    def test_preregistro_y_reporte_sin_habilidad_falsa(self):
        j=mod.generate()
        self.assertEqual(j["fase"],"9I")
        self.assertEqual(j["anios_prespecificados"],[1996,1998,2002,2007,2011,2013])
        self.assertEqual(j["estaciones_n"],3)
        self.assertEqual(j["escenarios_documentales_por_estacion"],2)
        for name in ("independencia_CHIRPS_validada","horario_pluviometrico_validado",
                     "emplazamiento_historico_certificado",
                     "pronosticos_archivados_con_vintage",
                     "modelo_predictivo_calibrado_en_esta_fase",
                     "cobertura_1996_2025_de_estaciones"):
            self.assertIs(j[name],False)
        self.assertGreaterEqual(j["pares_chirps_era5_mes_escenario"],72)
        self.assertGreaterEqual(j["meses_estacion_unicos_emparejados"],36)

    def test_base_1998_no_duplicada(self):
        j=mod.generate()
        selected=[a for a in j["resultados_estacion_escenario_anio"] if a["anio"]==1998]
        self.assertEqual(len(selected),6)
        self.assertTrue(all(x["n_meses_comunes"]==12 for x in selected))
        self.assertEqual(next(q for q in j["anios_resumen"] if q["anio"]==1998)
                         ["meses_estacion_distintos_emparejados"],36)
        self.assertTrue(all(q["chirps"] and q["era5"] for q in selected))

    def test_metricas_consistentes(self):
        j=mod.generate()
        for a in j["resultados_estacion_escenario_anio"]:
            n=a["n_meses_comunes"]
            self.assertLessEqual(n,12)
            self.assertEqual(n,a["chirps"]["n_meses"] if a["chirps"] else 0)
            self.assertEqual(n,a["era5"]["n_meses"] if a["era5"] else 0)
            self.assertEqual(a["anio_completo_12_meses"],n==12)
            if n:
                self.assertAlmostEqual(a["chirps"]["lluvia_estacion_mm"],
                                       a["era5"]["lluvia_estacion_mm"],delta=0.001)
                for p in ("chirps","era5"):
                    score=a[p]
                    self.assertTrue(math.isfinite(score["mae_mm_mes"]))
                    self.assertGreaterEqual(score["mae_mm_mes"],0)
                    self.assertGreaterEqual(score["rmse_mm_mes"]+0.002,score["mae_mm_mes"])

    def test_salida_reproducible_si_publicada(self):
        if mod.FILE.exists():
            self.assertEqual(json.loads(mod.FILE.read_text("utf8")),mod.generate())

if __name__=="__main__":unittest.main()
