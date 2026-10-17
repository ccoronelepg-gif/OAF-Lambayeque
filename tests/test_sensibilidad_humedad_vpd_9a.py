"""Fase 9A: tests de temporalidad, normalización y comparación pareada.
Fixtures inventados SOLO para tests; la corrida real usa ERA5 1996-2025.
"""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"modelos"))
import sensibilidad_humedad_vpd_9a as m

class Test9A(unittest.TestCase):
    def setUp(self):
        self.tr=[{'mes':f'{yr}-{mo:02d}'}
                 for yr in range(1996,2011) for mo in range(1,13)]
        self.h={r['mes']:{
            'rh_2m_media_pct':str(60+int(r['mes'][:4])-1996),
            'vpd_max_diario_media_mes_kpa':'2'} for r in self.tr}
        for mo in range(1,13):
            self.h[f'2011-{mo:02d}']={
              'rh_2m_media_pct':'90','vpd_max_diario_media_mes_kpa':'5'}

    def test_train_only_monthly_normals(self):
        base=m.means(self.tr,self.h)
        self.assertAlmostEqual(base['vpd_max_diario_media_mes_kpa'][6],2)
        self.assertAlmostEqual(base['rh_2m_media_pct'][1],67)
        self.h['2011-01']['rh_2m_media_pct']='500'
        self.assertAlmostEqual(m.means(self.tr,self.h)['rh_2m_media_pct'][1],67)

    def test_origin_without_future(self):
        normals=m.means(self.tr,self.h)
        origin='2010-12'
        a=m.features([1,2,3],origin,self.h,normals,'base_mas_rh_vpd')
        self.h['2011-01']['rh_2m_media_pct']='987'
        b=m.features([1,2,3],origin,self.h,normals,'base_mas_rh_vpd')
        self.assertEqual(a,b)
        self.assertEqual(len(a),5)

    def test_variants_nested(self):
        norm=m.means(self.tr,self.h)
        x=m.features([1,2],'2010-12',self.h,norm,m.BASE)
        a=m.features([1,2],'2010-12',self.h,norm,'base_mas_rh')
        b=m.features([1,2],'2010-12',self.h,norm,'base_mas_vpd')
        c=m.features([1,2],'2010-12',self.h,norm,'base_mas_rh_vpd')
        self.assertEqual(x,[1,2])
        self.assertEqual(len(a),3)
        self.assertEqual(len(b),3)
        self.assertEqual(c,[1,2,a[-1],b[-1]])

    def test_unknown_model_rejected(self):
        with self.assertRaisesRegex(ValueError,'desconocido'):
            m.features([0],'2010-12',self.h,m.means(self.tr,self.h),'magico')

    def test_missing_origin_not_imputed(self):
        with self.assertRaisesRegex(ValueError,'ausente'):
            m.features([0],'1995-12',self.h,m.means(self.tr,self.h),'base_mas_rh')

    def test_continuous_gain_direction(self):
        rows=[dict(localidad='Olmos',horizonte_meses=1,
                  objetivo='temperatura_aire_c',periodo='agregado_2011_2025',
                  modelo=name,mae=mae) for name,mae in
                  [(m.BASE,2),('base_mas_rh',1)]]
        result=m.gains(rows,'mae')
        self.assertEqual(result[0]['mejoria_pct'],50)

    def test_expected_periods(self):
        self.assertEqual(len(m.b.FOLDS),5)
        self.assertEqual(m.b.HORIZONS,(1,2,3))
        self.assertEqual(m.b.shift('2023-01',-3),'2022-10')

    def test_extremes_exactly_four_test_months(self):
        data=[]
        for yr in (2017,2023):
            for mo in range(1,5):
                for site in m.b.SITES:
                    for h in m.b.HORIZONS:
                        for target in m.b.TARGETS:
                            for model in m.MODELS:
                                data.append(dict(localidad=site,objetivo=target,
                                  horizonte_meses=h,modelo=model,
                                  mes_objetivo=f'{yr}-{mo:02d}',
                                  prediccion=4.0,observado=5.0))
        out=m.extreme_diagnostics(data)
        self.assertEqual(len(out),4*2*3*2*4)
        self.assertTrue(all(q['mae']==1 for q in out))

if __name__=='__main__':unittest.main()
