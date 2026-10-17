"""Test sintético de diagnóstico condicionado a eventos 2017/2023."""
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'auditoria_extremos_8x.py'
spec=importlib.util.spec_from_file_location('ext8x',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def rows():
    out=[]
    for y in (2017,2023):
        for month in range(1,13):
            for site in m.SITES:
                for target in m.TARGETS:
                    for model in m.MODELS:
                        for h in (1,2,3):
                            out.append(dict(localidad=site,objetivo=target,
                                horizonte_meses=str(h),modelo=model,
                                mes_objetivo=f'{y}-{month:02d}',
                                observado='20',prediccion='21'))
    return out
class E8X(unittest.TestCase):
    def test_complete(self):
        out=m.compute(rows())
        self.assertEqual(len(out),4*2*5*3*2*2)
        self.assertTrue(all(x['mae']==1 for x in out))
    def test_missing_month_rejected(self):
        a=rows();a.pop(0)
        with self.assertRaises(ValueError):m.compute(a)
    def test_duplicate_model_year_rejected(self):
        a=rows();a.append(a[0].copy())
        with self.assertRaisesRegex(ValueError,'Duplicate'):m.compute(a)
    def test_never_calls_1998_a_holdout(self):
        self.assertNotIn(1998,m.YEARS)
        self.assertEqual(set(m.YEARS),{2017,2023})
if __name__=='__main__':unittest.main()
