"""Pruebas de 8J: datos sintéticos exclusivamente en directorios temporales."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("horaria8j",ROOT/"modelos/homologar_temperatura_horaria_8j.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Test8J(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        shutil.copytree(ROOT/"datos/temperatura_horaria_8j",self.root/"datos/temperatura_horaria_8j")
        (self.root/"datos/temperatura_horaria_8j/entradas").mkdir()
        (self.root/"datos").mkdir(exist_ok=True)
        shutil.copyfile(ROOT/mod.HIST,self.root/mod.HIST)
        self.csv=self.root/"datos/temperatura_horaria_8j/entradas/demo.csv"
        self.manifest=self.root/mod.MANIFEST

    def hourly(self,missing=None,bad=False,temp="23",timestamp_override=None):
        # Enero 1996 en Perú (UTC-05:00): 744 instantes exactos locales.
        first=datetime(1996,1,1,5,0,tzinfo=timezone.utc)
        with self.csv.open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f);w.writerow(mod.HOUR_FIELDS)
            for i in range(31*24):
                if i==missing:continue
                t=first+timedelta(hours=i)
                if i==0 and timestamp_override:t=timestamp_override
                w.writerow(["EST01",t.isoformat(),temp,"rechazado" if bad and i==0 else "aprobado"])

    def registration(self,**patch):
        vals=dict(
            codigo_estacion="EST01",archivo_csv="demo.csv",
            sha256_archivo=hashlib.sha256(self.csv.read_bytes()).hexdigest(),
            url_fuente="https://www.senamhi.gob.pe/",
            publicado_utc="2026-10-16T12:00:00+00:00",
            latitud="-6.77140",longitud="-79.84090",altitud_estacion_m="30",
            altitud_celda_era5_m="35",fuente_altitud_celda="https://cds.climate.copernicus.eu/",
            localidad_oaf="Chiclayo",codigo_verificado="true",
            coordenadas_verificadas="true",metodo_temporal_verificado="true",
            control_calidad_documentado="true",representatividad_espacial_evaluada="true",
            publicacion_derivados_autorizada="true",documento_metodologico="https://www.senamhi.gob.pe/"
        )
        vals.update(patch)
        with self.manifest.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=mod.METADATA_FIELDS);w.writeheader();w.writerow(vals)

    def test_empty_real_inventory_and_metrics(self):
        result,rows=mod.calculate(self.root)
        self.assertEqual(result["estaciones_fuente_autorizada"],0)
        self.assertEqual(result["pares_descriptivos_estacion_era5"],0)
        self.assertIsNone(result["estadisticas_por_localidad"]["Chiclayo"]["mae_c"])
        self.assertFalse(result["habilidad_predictiva_8e_demostrada"])
        mod.publish(self.root)
        mod.publish(self.root,check=True)

    def test_true_month_complete_with_utc_local_shift(self):
        self.hourly();self.registration()
        result,rows=mod.calculate(self.root)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["mes"],"1996-01")
        self.assertEqual(rows[0]["horas_calendario"],744)
        self.assertEqual(rows[0]["horas_validas"],744)
        self.assertEqual(rows[0]["dias_con_24_horas"],31)
        self.assertEqual(rows[0]["temperatura_instrumental_horaria_c"],23.0)
        self.assertAlmostEqual(rows[0]["diferencia_era5_menos_estacion_c"],0.44839)
        self.assertEqual(result["pares_descriptivos_estacion_era5"],1)
        self.assertFalse(result["validacion_independiente_demostrada"])
        mod.publish(self.root);mod.publish(self.root,check=True)

    def test_missing_hour_excludes_entire_month(self):
        self.hourly(missing=123);self.registration()
        result,rows=mod.calculate(self.root)
        self.assertEqual(rows[0]["dias_con_24_horas"],30)
        self.assertEqual(rows[0]["horas_validas"],743)
        self.assertIsNone(rows[0]["temperatura_instrumental_horaria_c"])
        self.assertEqual(result["pares_descriptivos_estacion_era5"],0)

    def test_rejected_quality_excludes_entire_month(self):
        self.hourly(bad=True);self.registration()
        _,rows=mod.calculate(self.root)
        self.assertIsNone(rows[0]["temperatura_instrumental_horaria_c"])

    def test_provisional_coordinates_exclude_pair(self):
        self.hourly();self.registration(coordenadas_verificadas="false")
        _,rows=mod.calculate(self.root)
        self.assertIsNone(rows[0]["era5_land_8d_c"])
        self.assertEqual(rows[0]["estado_espacial"],"requiere_revision_geografica")

    def test_elevation_difference_excludes_pair(self):
        self.hourly();self.registration(altitud_celda_era5_m="600")
        _,rows=mod.calculate(self.root)
        self.assertIsNone(rows[0]["diferencia_era5_menos_estacion_c"])
        self.assertGreater(abs(rows[0]["desnivel_celda_estacion_m"]),200)

    def test_distance_excludes_pair(self):
        self.hourly();self.registration(latitud="-5.1")
        _,rows=mod.calculate(self.root)
        self.assertIsNone(rows[0]["era5_land_8d_c"])

    def test_sha_modified_rejected(self):
        self.hourly();self.registration(sha256_archivo="0"*64)
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            mod.calculate(self.root)

    def test_no_publication_permission(self):
        self.hourly();self.registration(publicacion_derivados_autorizada="false")
        with self.assertRaisesRegex(ValueError,"no autorizada"):
            mod.calculate(self.root)

    def test_duplicate_utc_instant_rejected(self):
        self.hourly()
        with self.csv.open("a",encoding="utf-8") as f:
            f.write("EST01,1996-01-01T05:00:00+00:00,23,aprobado\n")
        self.registration()
        with self.assertRaisesRegex(ValueError,"Duplicado horario UTC"):
            mod.calculate(self.root)

    def test_wrong_utc_offset_rejected(self):
        self.hourly(timestamp_override=datetime(1996,1,1,5,tzinfo=timezone(timedelta(hours=-5))))
        self.registration()
        with self.assertRaisesRegex(ValueError,"explícitamente UTC"):
            mod.calculate(self.root)

    def test_non_exact_hour_rejected(self):
        self.hourly(timestamp_override=datetime(1996,1,1,5,30,tzinfo=timezone.utc))
        self.registration()
        with self.assertRaisesRegex(ValueError,"hora UTC"):
            mod.calculate(self.root)

    def test_qa_unknown_rejected(self):
        self.hourly()
        p=self.csv
        p.write_text(p.read_text(encoding="utf-8").replace("23,aprobado","23,sospechoso",1),encoding="utf-8")
        self.registration()
        with self.assertRaisesRegex(ValueError,"QA no reconocida"):
            mod.calculate(self.root)

    def test_no_imputed_temperature_outlier(self):
        self.hourly(temp="999");self.registration()
        with self.assertRaisesRegex(ValueError,"inverosímil"):
            mod.calculate(self.root)

    def test_future_release_rejected(self):
        self.hourly();self.registration(publicado_utc="2099-01-01T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError,"futura"):
            mod.calculate(self.root)

if __name__=="__main__":
    unittest.main()
