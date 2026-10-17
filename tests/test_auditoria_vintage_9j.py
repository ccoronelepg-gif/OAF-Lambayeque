"""9J: pruebas offline de trazabilidad original y fechas de emisión."""
import json
import sys
import unittest
from datetime import date,datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import auditoria_vintage_9j as q

class Vintage9J(unittest.TestCase):
    def test_fuentes_commit_no_modificados(self):
        manifest=q.jread(q.SOURCES)
        self.assertEqual(len(manifest["archivos_diarios"]),4)
        for item in manifest["archivos_diarios"]:
            fingerprint=q.archive_proof(item["path"],item["primer_commit"])
            self.assertEqual(len(fingerprint),64)

    def test_tiempos_comparaciones(self):
        x=q.build()
        daily=x["diarios_externos"]
        self.assertEqual(x["corte_local"],"2026-10-17")
        self.assertEqual(daily["n_emisiones"],4)
        self.assertEqual(daily["n_localidad_dia_pronosticados"],112)
        self.assertEqual(daily["n_emisiones_con_commit_y_bytes_comprobados"],4)
        self.assertEqual(daily["fecha_primer_contraste_posible"],"2026-10-22")
        self.assertEqual(daily["n_comparables_temporalmente_al_corte"],0)
        self.assertLess(daily["n_localidad_dia_valido_unicos"],112)
        self.assertEqual(x["verificacion_externa_6g"]["n_dias_verificados"],0)

    def test_temperatura_8e_no_se_confunde_con_nowcast(self):
        x=q.build()
        monthly=x["temperatura_mensual_propia"]
        self.assertEqual(monthly["n_emisiones"],1)
        self.assertEqual(monthly["n_predicciones_premes"],8)
        self.assertEqual(monthly["n_nowcasts_intramensuales"],4)
        self.assertEqual(monthly["n_temporalmente_elegibles"],0)
        self.assertEqual(monthly["n_contrastes_en_libro_8e"],0)
        self.assertEqual(x["verificacion_temperatura_8g"]["n_pronosticos_verificados"],0)
        self.assertEqual(x["sst_mensual_propia"]["n_predicciones_premes"],2)
        self.assertEqual(x["sst_mensual_propia"]["n_nowcasts_intramensuales"],1)

    def test_cero_habilidad_y_fuentes_externas(self):
        x=q.build()
        for k in ("oaf_habilidad_prospectiva_demostrada",
                  "enso_nino_costero_predictivo_validado",
                  "alertas_fitosanitarias_derivadas",
                  "normal_1996_2025_validada_instrumentalmente"):
            self.assertIs(x[k],False)
        self.assertTrue(all(v is None for v in x["metricas_predictivas_observadas"].values()))
        self.assertEqual(x["predicciones_estacionales_NOAA_descargadas_y_verificadas_n"],0)
        self.assertTrue(any("NMME" in z["nombre"] for z in x["inventario_estacional_NOAA_C3S"]))

    def test_seccion_web_y_no_regresiones(self):
        h=(ROOT/"index.html").read_text("utf8")
        self.assertEqual(h.count('<section data-page='),5)
        # El portal conserva registros técnicos y ofrece verificación en el nivel experto.
        self.assertIn('id="oaf-9j-visor"',h)
        self.assertIn('id="oaf-9j-status"',h)
        self.assertIn('id="oaf-9j-ledger"',h)
        self.assertIn("FASE_9J_AUDITORIA_VINTAGE.md",h)
        self.assertIn("modelos/visor_auditoria_9j.js",h)
        self.assertIn("assets/oaf-auditoria-9j.css",h)

    def test_reproduccion_del_json_final(self):
        if q.REPORT.exists():
            self.assertEqual(q.jread(q.REPORT),q.build())

if __name__=="__main__":unittest.main()
