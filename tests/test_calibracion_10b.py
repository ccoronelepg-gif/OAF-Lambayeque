"""Pruebas unitarias para el motor 10B, sin generar supuestas predicciones operativas."""
import unittest,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'modelos/calibracion_temporal_10b.py'
spec=importlib.util.spec_from_file_location('calib10b',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Criterios10B(unittest.TestCase):
 def test_cuantil(self):self.assertEqual(m.quantile(range(1,25)),23)
 def test_calibracion_incompleta(self):
  with self.assertRaises(ValueError):m.quantile([1]*23)
 def test_metrica_cobertura(self):
  sample=[{'ok':True,'err':-2,'width':4},{'ok':False,'err':4,'width':6}]
  self.assertEqual(m.summarize(sample),{'n':2,'cobertura_pct':50.,'mae_mm':3.,'ancho_medio_mm':5.,'sesgo_mm':1.})
 def test_extremo_no_detectado(self):
  sample=[{'modelo':'gcn','obs':110.,'pred':80.}]
  r=next(x for x in m.events(sample) if x['modelo']=='gcn' and x['umbral_mm']==100)
  self.assertEqual((r['detectados'],r['omitidos']),(0,1))
if __name__=='__main__':unittest.main()
