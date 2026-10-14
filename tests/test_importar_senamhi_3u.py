"""Pruebas de importación SENAMHI 3U con datos SINTÉTICOS (no observados)."""
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from importar_senamhi_3u import ingest, read_csv_senamhi

class TestIngesta(unittest.TestCase):
    def test_cero_valido_y_ausencia_no_es_cero(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            text="año,mes,día,precipitacion,tmax,tmin\n"
            for day in range(1,32):
                value="10" if day==1 else "0"
                text+=f"2016,1,{day},{value},30,18\n"
            text+="2016,2,1,-99.9,31,18\n2016,2,2,5,30,18\n"
            original=folder/"original.txt"
            original.write_text(text,encoding="utf-8")
            summary=ingest(original,"Cayaltí",folder/"salida")
            self.assertEqual(summary["meses_completos"],1)
            self.assertEqual(summary["meses_incompletos"],119)
            self.assertEqual(summary["incidencias_valor"],{"codigo_ausente":1})
            report=(folder/"salida"/"cayalti_mensual_3u.csv").read_text(encoding="utf-8")
            self.assertIn("2016-01,10.0,31,31,31,0,completo",report)
            self.assertIn("2016-02,,29,2,1,28,incompleto",report)
            self.assertFalse(summary["apto_para_validacion_externa"])
            self.assertFalse(summary["publicacion_automatica"])

    def test_rechaza_fechas_duplicadas(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"
            p.write_text("2016,1,1,1,20,10\n2016,1,1,2,20,10\n")
            with self.assertRaisesRegex(ValueError,"duplicada"):
                read_csv_senamhi(p)

    def test_rechaza_fechas_invalidas(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"
            p.write_text("2016,2,30,1,20,10\n")
            with self.assertRaisesRegex(ValueError,"fecha inválida"):
                read_csv_senamhi(p)

    def test_registra_negativo_no_sentinel(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"
            p.write_text("2016,1,1,-3,30,18\n")
            rows,info=read_csv_senamhi(p)
            self.assertIsNone(rows[date(2016,1,1)])
            self.assertEqual(info["incidencias_valor"]["negativo_no_sentinel"],1)

    def test_no_acepta_numeros_no_finitos(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"
            p.write_text("2016,1,1,NaN,20,11\n2016,1,2,inf,22,12\n")
            rows,info=read_csv_senamhi(p)
            self.assertIsNone(rows[date(2016,1,1)])
            self.assertIsNone(rows[date(2016,1,2)])
            self.assertGreaterEqual(sum(info["incidencias_valor"].values()),2)

    def test_no_inventa_datos_del_periodo(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"historico.txt"
            p.write_text("2015,12,31,1,20,11\n")
            with self.assertRaisesRegex(ValueError,"no hay observaciones nuevas"):
                read_csv_senamhi(p)

    def test_exige_seis_columnas(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"
            p.write_text("2016,1,1,0\n")
            with self.assertRaisesRegex(ValueError,"6 columnas"):
                read_csv_senamhi(p)

if __name__=="__main__":
    unittest.main()
