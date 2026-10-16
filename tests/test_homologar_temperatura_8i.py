"""Pruebas sintéticas aisladas de 8I; ningún número de prueba se publica como evidencia agrícola."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("homologador8i",REPO/"modelos/homologar_temperatura_senamhi_8i.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Test8I(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        directory=self.root/"datos/temperatura_senamhi_8i"
        (directory/"entradas").mkdir(parents=True)
        shutil.copyfile(REPO/m.HIST,self.root/m.HIST)
        (directory/"manifest.csv").write_text(",".join(m.FIELDS_MANIFEST)+"\n",encoding="utf-8")
        self.input=directory/"entradas/prueba.csv"
        self.manifest=directory/"manifest.csv"

    def make_days(self,n=31,tmean="23",method="promedio_horario_24h"):
        with self.input.open("w",newline="",encoding="utf-8") as f:
            wr=csv.writer(f);wr.writerow(m.FIELDS_DAILY)
            for day in range(1,n+1):
                wr.writerow(["SEN_TEST","1996-01-"+str(day).zfill(2),"25","21",tmean,method,"aprobado"])

    def make_manifest(self,**overrides):
        r={
          "codigo_estacion":"SEN_TEST","nombre_estacion":"Estación sintética (solo pruebas)",
          "archivo_csv":"prueba.csv","sha256_archivo":hashlib.sha256(self.input.read_bytes()).hexdigest(),
          "url_fuente":"https://www.senamhi.gob.pe/","fecha_publicacion_utc":"2026-10-01T12:00:00+00:00",
          "unidad":"°C","zona_horaria":"America/Lima","latitud":"-6.77140","longitud":"-79.84090",
          "altitud_m":"30","codigo_confirmado":"true","coordenadas_confirmadas":"true",
          "metodo_homologado":"true","calidad_confirmada":"true","independencia_confirmada":"false",
          "autorizacion_publicacion_derivados":"true","punto_oaf_objetivo":"Chiclayo",
          "documento_metodo":"https://www.senamhi.gob.pe/"
        }
        r.update(overrides)
        with self.manifest.open("w",newline="",encoding="utf-8") as f:
            wr=csv.DictWriter(f,fieldnames=m.FIELDS_MANIFEST)
            wr.writeheader();wr.writerow(r)

    def test_repository_without_data_remains_pending(self):
        status,rows=m.evaluate(REPO)
        self.assertEqual(status["n_archivos_fuente_autorizados"],0)
        self.assertEqual(status["n_meses_con_pares_estacion_era5"],0)
        self.assertFalse(status["habilidad_prospectiva_8e_demostrada"])
        self.assertEqual(rows,[])

    def test_empty_template_never_fakes_temperature(self):
        status,records=m.evaluate(self.root)
        self.assertEqual(status["estado"],"sin_serie_termica_senamhi_instrumental")
        self.assertIsNone(status["estadisticos_descriptivos"]["mae_c"])
        m.publish(self.root,False);m.publish(self.root,True)

    def test_real_data_schema_synthetic_fixture_yields_descriptive_pair(self):
        self.make_days();self.make_manifest()
        report,rows=m.evaluate(self.root)
        self.assertEqual(report["n_meses_con_pares_estacion_era5"],1)
        self.assertEqual(rows[0]["mes"],"1996-01")
        self.assertEqual(rows[0]["dias_tmedia_validos"],31)
        self.assertEqual(rows[0]["estado_comparacion"],"comparacion_descriptiva_sin_independencia_certificada")
        self.assertAlmostEqual(rows[0]["temperatura_media_observada_c"],23)
        self.assertAlmostEqual(rows[0]["diferencia_era5_menos_estacion_c"],0.44839)
        self.assertFalse(report["estadisticos_descriptivos"]["habilidad_predictiva_8e_demostrada"])
        m.publish(self.root,False);m.publish(self.root,True)

    def test_partial_month_with_only_tmax_tmin_never_becomes_tmean(self):
        self.make_days(tmean="");self.make_manifest()
        report,rows=m.evaluate(self.root)
        self.assertEqual(rows[0]["dias_tmedia_validos"],0)
        self.assertIsNone(rows[0]["temperatura_media_observada_c"])
        self.assertIsNone(rows[0]["era5_land_8d_c"])
        self.assertEqual(report["n_meses_con_pares_estacion_era5"],0)

    def test_one_day_missing_prevents_month_pair(self):
        self.make_days(30);self.make_manifest()
        _,rows=m.evaluate(self.root)
        self.assertEqual(rows[0]["estado_mes"],"incompleto")
        self.assertIsNone(rows[0]["diferencia_era5_menos_estacion_c"])

    def test_geography_blocks_nonrepresentative_pair(self):
        self.make_days();self.make_manifest(latitud="-5.1")
        report,rows=m.evaluate(self.root)
        self.assertEqual(report["n_meses_con_pares_estacion_era5"],0)
        self.assertEqual(rows[0]["estado_comparacion"],"metadatos_o_representatividad_pendientes")

    def test_unconfirmed_code_blocks_pair(self):
        self.make_days();self.make_manifest(codigo_confirmado="false")
        report,_=m.evaluate(self.root)
        self.assertEqual(report["n_meses_con_pares_estacion_era5"],0)

    def test_bad_sha_rejected(self):
        self.make_days();self.make_manifest(sha256_archivo="0"*64)
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            m.evaluate(self.root)

    def test_unsafe_path_rejected(self):
        self.make_days();self.make_manifest(archivo_csv="../evil.csv")
        with self.assertRaisesRegex(ValueError,"no seguro"):
            m.evaluate(self.root)

    def test_no_permission_raises(self):
        self.make_days();self.make_manifest(autorizacion_publicacion_derivados="false")
        with self.assertRaisesRegex(ValueError,"autorización"):
            m.evaluate(self.root)

    def test_duplicate_daily_date_rejected(self):
        self.make_days()
        with self.input.open("a",encoding="utf-8") as f:
            f.write("SEN_TEST,1996-01-01,25,21,23,promedio_horario_24h,aprobado\n")
        self.make_manifest()
        with self.assertRaisesRegex(ValueError,"duplicada"):
            m.evaluate(self.root)

    def test_invalid_temp_bounds_rejected(self):
        self.make_days(tmean="27");self.make_manifest()
        with self.assertRaisesRegex(ValueError,"Tmedia por encima"):
            m.evaluate(self.root)

    def test_unknown_averaging_rejected(self):
        self.make_days(method="max_min_dividido_dos");self.make_manifest()
        with self.assertRaisesRegex(ValueError,"Método Tmedia no reconocido"):
            m.evaluate(self.root)

    def test_observation_after_publication_rejected(self):
        self.make_days();self.make_manifest(fecha_publicacion_utc="1995-12-31T18:00:00+00:00")
        with self.assertRaisesRegex(ValueError,"después de la publicación"):
            m.evaluate(self.root)

if __name__=="__main__":
    unittest.main()
