#!/usr/bin/env python3
"""Pruebas sintéticas AISLADAS para el evaluador OAF 8G (no son resultados del OAF)."""
import csv
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "modelos" / "evaluador_prospectivo_8g.py"
spec = importlib.util.spec_from_file_location("evaluador_8g", SCRIPT)
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
ORIGINAL_ISSUE = ROOT / "datos/pronosticos_temperatura_regional_8e/2026-09.json"
ORIGINAL_LEDGER = ROOT / "datos/verificacion_temperatura_regional_8e.json"


class Evaluador8GTest(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        folder = self.root / "datos/pronosticos_temperatura_regional_8e"
        folder.mkdir(parents=True)
        shutil.copyfile(ORIGINAL_ISSUE, folder / ORIGINAL_ISSUE.name)
        self.issue = json.loads(ORIGINAL_ISSUE.read_text(encoding="utf-8"))
        self.report = json.loads(ORIGINAL_LEDGER.read_text(encoding="utf-8"))
        self.ledgerpath = self.root / "datos/verificacion_temperatura_regional_8e.json"
        self.csvpath = self.root / "datos/verificacion_temperatura_regional_8e.csv"
        self.write_report("2026-10-16T12:00:00+00:00", 0)
        self.write_csv([])

    def write_report(self, cut, observed):
        self.report["generado_utc"] = cut
        self.report["pronosticos_comparados"] = observed
        self.report["comparados_realmente_previos_al_mes"] = max(0, observed - 4)
        self.ledgerpath.write_text(json.dumps(self.report), encoding="utf-8")

    def row_for(self, forecast):
        actual = forecast["pronostico_local_c"] - 1.5  # dato sintético SOLO en TemporaryDirectory
        return {
            "emision_utc": self.issue["emision_utc"],
            "mes_origen": self.issue["mes_origen"],
            "mes_objetivo": forecast["mes_objetivo"],
            "localidad": forecast["localidad"],
            "horizonte_meses": forecast["horizonte_meses"],
            "tipo_emision": forecast["tipo_emision"],
            "pronostico_local_c": forecast["pronostico_local_c"],
            "pronostico_nino_t300_c": forecast["pronostico_nino_t300_c"],
            "observacion_era5_land_c": actual,
            "error_local_c": 1.5,
            "error_nino_t300_c": forecast["pronostico_nino_t300_c"] - actual
        }

    def write_csv(self, rows):
        with self.csvpath.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ev.DETAIL_FIELDS[:0] + (
                "emision_utc", "mes_origen", "mes_objetivo", "localidad",
                "horizonte_meses", "tipo_emision", "pronostico_local_c",
                "pronostico_nino_t300_c", "observacion_era5_land_c",
                "error_local_c", "error_nino_t300_c"))
            writer.writeheader()
            writer.writerows(rows)

    def test_all_metrics_pending_without_observation(self):
        report, rows = ev.build(self.root)
        self.assertEqual(len(rows), 12)
        self.assertEqual(report["n_premes_archivados"], 8)
        self.assertEqual(report["n_intramensuales_archivados"], 4)
        self.assertEqual(report["n_verificados_total"], 0)
        self.assertIsNone(report["metricas"]["premes"]["total"]["modelos"]["local"]["mae_c"])
        self.assertIsNone(report["metricas"]["premes"]["total"]["modelos"]["nino_t300"]["intervalo_90_cobertura"])
        self.assertFalse(report["habilidad_prospectiva_demostrada"])
        self.assertEqual(len(report["trazabilidad"]["emisiones_inmutables"]), 1)
        ev.publish(self.root, check=False)
        ev.publish(self.root, check=True)

    def test_premature_observation_is_rejected(self):
        self.write_csv([self.row_for(self.issue["pronosticos"][0])])
        self.write_report("2026-10-16T12:00:00+00:00", 1)
        with self.assertRaisesRegex(ValueError, "ventana permitida"):
            ev.build(self.root)

    def test_detect_modified_forecast(self):
        row = self.row_for(self.issue["pronosticos"][0])
        row["pronostico_local_c"] += 2
        self.write_csv([row])
        self.write_report("2026-11-12T12:00:00+00:00", 1)
        with self.assertRaisesRegex(ValueError, "modificada"):
            ev.build(self.root)

    def test_intramonth_cannot_be_used_to_claim_premonth_skill(self):
        nowcasts = [p for p in self.issue["pronosticos"] if not p["emitido_antes_inicio_mes"]]
        self.write_csv([self.row_for(x) for x in nowcasts])
        self.write_report("2026-11-12T12:00:00+00:00", 4)
        out, rows = ev.build(self.root)
        self.assertEqual(out["n_verificados_total"], 4)
        self.assertEqual(out["n_verificados_premes"], 0)
        self.assertEqual(out["n_verificados_intramensuales"], 4)
        self.assertIsNone(out["metricas"]["premes"]["total"]["modelos"]["local"]["mae_c"])
        self.assertEqual(out["metricas"]["intramensual"]["total"]["modelos"]["local"]["mae_c"], 1.5)
        self.assertEqual(sum(r["observacion_era5_land_c"] is not None for r in rows), 4)

    def test_full_future_synthetic_score_but_never_validated(self):
        self.write_csv([self.row_for(x) for x in self.issue["pronosticos"]])
        self.write_report("2027-01-12T12:00:00+00:00", 12)
        out, _ = ev.build(self.root)
        self.assertEqual(out["n_verificados_premes"], 8)
        self.assertEqual(out["n_verificados_intramensuales"], 4)
        self.assertEqual(out["metricas"]["premes"]["total"]["modelos"]["local"]["mae_c"], 1.5)
        self.assertEqual(out["metricas"]["premes"]["total"]["modelos"]["local"]["rmse_c"], 1.5)
        self.assertEqual(out["metricas"]["premes"]["total"]["modelos"]["local"]["sesgo_c"], 1.5)
        self.assertFalse(out["habilidad_prospectiva_demostrada"])
        self.assertFalse(out["cobertura_intervalos_90_evaluable"])

    def test_duplicate_comparison_rejected(self):
        row = self.row_for(self.issue["pronosticos"][0])
        self.write_csv([row, row])
        self.write_report("2026-11-12T12:00:00+00:00", 2)
        with self.assertRaisesRegex(ValueError, "duplicada"):
            ev.build(self.root)

    def test_real_repository_does_not_claim_prospective_skill(self):
        out, rows = ev.build(ROOT)
        self.assertFalse(out["habilidad_prospectiva_demostrada"])
        self.assertEqual(out["n_registros_archivados"], len(rows))
        self.assertEqual(out["n_premes_archivados"] + out["n_intramensuales_archivados"], len(rows))


if __name__ == "__main__":
    unittest.main()
