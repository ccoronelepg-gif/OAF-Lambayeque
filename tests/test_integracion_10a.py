#!/usr/bin/env python3
"""Pruebas de integridad y no alertas para auditoría OAF fase 10A."""
import csv,importlib.util,tempfile,unittest
from pathlib import Path
MOD=Path(__file__).resolve().parents[1]/"modelos/auditoria_integrada_10a.py"
spec=importlib.util.spec_from_file_location("oaf10a",MOD);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(name="random_forest",y=3.,p=4.):
 return {"mes":"2021-01","anio":"2021","sector":"S001","piso":"llanura_costa","bloque":"0","modelo":name,"y":y,"p":p}
class Auditoria10ATests(unittest.TestCase):
 def test_mae_rmse(self):
  value=m.metric([row(p=4),row(p=5)])
  self.assertEqual(value["mae_mm"],1.5)
  self.assertEqual(value["rmse_mm"],round((2.5)**.5,4))
 def test_sesgo_con_signo(self):
  self.assertEqual(m.metric([row(p=1)])["sesgo_mm"],-2.0)
 def test_dup_rechazado(self):
  a=row()
  with self.assertRaisesRegex(ValueError,"repetida"):m.evaluate([a,a],{},{"folds":[]})
 def test_target_divergente_rechazado(self):
  with self.assertRaisesRegex(ValueError,"no pareadas"):
   m.evaluate([row("random_forest"),row("gcn",y=10)],{},{"folds":[]})
 def test_matrix_incompleta_rechazada(self):
  with self.assertRaisesRegex(ValueError,"incompleta"):
   m.evaluate([row()],{},{"folds":[]})
 def test_data_negativa_rechazada(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"fake.csv"
   with p.open("w",newline="",encoding="utf8") as f:
    writer=csv.DictWriter(f,fieldnames=sorted(m.COLS));writer.writeheader()
    writer.writerow({"mes":"2021-01","anio":"2021","sector":"S001","piso":"llanura_costa","bloque":"0","modelo":"random_forest","observado_CHIRPS_mm":"-1","predicho_mm":"2"})
   with self.assertRaisesRegex(ValueError,"lluvia inválida"):m.read(p)
if __name__=="__main__":unittest.main()
