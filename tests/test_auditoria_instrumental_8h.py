"""OAF 8H: pruebas documentales reales y errores sintéticos AISLADOS."""
from __future__ import annotations
import csv
import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf_audit8h",ROOT/"modelos/auditoria_instrumental_8h.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class TestOAF8H(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/"datos/evaluacion_prospectiva_8g").mkdir(parents=True)
        for path in (audit.FILE_STATIONS,audit.FILE_RAIN,audit.FILE_COVER,audit.FILE_8G):
            dest=self.root/path
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,dest)

    def test_historical_inventory_never_certifies_temperature(self):
        result,rows=audit.assess(self.root)
        self.assertEqual(result["meses_estacion_precipitacion"],1109)
        self.assertEqual(result["estaciones_historicas_precipitacion"],5)
        self.assertEqual(result["estacion_anio_completos"],79)
        self.assertEqual(result["ultimo_anio_comun_completo"],2012)
        self.assertEqual(result["estaciones_aptas_validacion_temperatura_8e"],0)
        self.assertFalse(result["intervalos_prediccion_90_publicables"])
        self.assertIsNone(result["radio_90_por_localidad_horizonte"])
        self.assertEqual(len(rows),5)
        self.assertTrue(all(not row["apto_contraste_8e_temperatura"] for row in rows))
        self.assertTrue(all(row["distancia_referencial_km"]>=0 for row in rows))
        audit.run(self.root)
        audit.run(self.root,check=True)

    def test_rainfall_is_not_a_temperature_series(self):
        target=self.root/audit.FILE_RAIN
        s=target.read_text(encoding="utf-8")
        s=s.replace("estacion,mes,observado_mm,dias_validos,dias_mes",
                    "estacion,mes,temperatura_c,dias_validos,dias_mes",1)
        target.write_text(s,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"no es una serie de temperatura"):
            audit.assess(self.root)

    def test_missing_monthly_day_rejected(self):
        path=self.root/audit.FILE_RAIN
        original=path.read_text(encoding="utf-8")
        path.write_text(original.replace("Cayaltí,1996-01,3.250,31,31",
                                          "Cayaltí,1996-01,3.250,30,31",1),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"todos los días"):
            audit.assess(self.root)

    def test_metadata_location_never_passes_without_instrumental_evidence(self):
        path=self.root/audit.FILE_STATIONS
        s=path.read_text(encoding="utf-8")
        s=s.replace(",false,false,false,",",true,true,true,")
        path.write_text(s,encoding="utf-8")
        result, rows=audit.assess(self.root)
        self.assertEqual(result["estaciones_aptas_validacion_temperatura_8e"],0)

    def test_malformed_coordinates_rejected(self):
        path=self.root/audit.FILE_STATIONS
        s=path.read_text(encoding="utf-8").replace("-6.322,-79.779","-106.322,-79.779")
        path.write_text(s,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"fuera de rango"):
            audit.assess(self.root)

    def test_quantile_with_too_few_samples_remains_none(self):
        self.assertIsNone(audit.conformal_radius([], "2026-10-16T12:00:00+00:00"))

    @staticmethod
    def synthetic_calibration(n=40):
        rows=[]
        year,month=2019,1
        for i in range(n):
            target=f"{year:04d}-{month:02d}"
            issue=f"{year:04d}-{month-1:02d}-15T12:00:00+00:00" if month>1 else f"{year-1:04d}-12-15T12:00:00+00:00"
            after_year,after_month=(year+1,1) if month==12 else (year,month+1)
            released=f"{after_year:04d}-{after_month:02d}-12T12:00:00+00:00"
            rows.append({"fecha_objetivo":target,"prediccion_emitida_utc":issue,
                         "observado_disponible_utc":released,"error_c":str(i+1)})
            month+=1
            if month>12:month=1;year+=1
        return rows

    def test_calibration_is_preparatory_not_published_as_operational(self):
        samples=self.synthetic_calibration()
        result=audit.conformal_radius(samples,"2026-10-16T12:00:00+00:00")
        self.assertEqual(result,37.0) # ceil((40+1)*0.9) = 37
        result_real,_=audit.assess(self.root)
        self.assertIsNone(result_real["cobertura_intervalos_90"])
        self.assertFalse(result_real["calibracion_temporal_realizada"])

    def test_future_release_leak_is_rejected(self):
        rows=self.synthetic_calibration()
        rows[-1]["observado_disponible_utc"]="2027-02-12T12:00:00+00:00"
        with self.assertRaisesRegex(ValueError,"Fuga temporal"):
            audit.conformal_radius(rows,"2026-10-16T12:00:00+00:00")

    def test_duplicate_target_for_calibration_is_rejected(self):
        rows=self.synthetic_calibration()
        rows[-1]["fecha_objetivo"]=rows[0]["fecha_objetivo"]
        with self.assertRaisesRegex(ValueError,"duplicado"):
            audit.conformal_radius(rows,"2026-10-16T12:00:00+00:00")

    def test_intra_month_forecast_for_calibration_is_rejected(self):
        rows=self.synthetic_calibration()
        rows[1]["prediccion_emitida_utc"]="2019-02-10T12:00:00+00:00"
        with self.assertRaisesRegex(ValueError,"intramensual"):
            audit.conformal_radius(rows,"2026-10-16T12:00:00+00:00")

if __name__=="__main__":
    unittest.main()
