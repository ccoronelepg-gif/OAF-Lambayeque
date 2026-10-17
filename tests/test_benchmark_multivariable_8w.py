"""OAF 8W: pruebas sintéticas; no confundir con validación instrumental."""
import importlib.util
import math
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'modelos'/'benchmark_multivariable_8w.py'
spec=importlib.util.spec_from_file_location('oaf_8w',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def data():
    out=[]
    for year in range(1996,2026):
        for month in range(1,13):
            date=f'{year}-{month:02d}'
            out.append({
              'mes':date,'localidad':'Motupe',
              'temperatura_aire_c':str(23+month*.1+(year-1996)*.02),
              'precipitacion_mes_mm':str(month*2+(year-1996)%5),
              'viento_10m_m_s':'3','viento_u_aprox_m_s':'-.2','viento_v_aprox_m_s':'.8',
              'anomalia_nino12_c':'0.8','anomalia_nino34_c':'0.4',
              'lluvia_modelada_ge_1000_mm_revisar':'False',
            })
    return out

class Benchmark8W(unittest.TestCase):
    def test_shift_cross_year_leap(self):
        self.assertEqual(m.shift('2016-01',-1),'2015-12')
        self.assertEqual(m.shift('2016-12',2),'2017-02')

    def test_p90_train_only(self):
        self.assertAlmostEqual(m.quantile([0,10,20,30,40],.9),36)
        self.assertEqual(m.quantile([0,0,0],.9),0)

    def test_ridge_intercept_unpenalized(self):
        pred=m.ridge([[1],[2],[3],[4]],[5,5,5,5],[[99]])
        self.assertAlmostEqual(pred[0],5,places=7)

    def test_ridge_response(self):
        pred=m.ridge([[0],[1],[2],[3],[4]],[0,1,2,3,4],[[2],[4]])
        self.assertTrue(all(math.isfinite(v) for v in pred))
        self.assertGreater(pred[1],pred[0])

    def test_logistic_probabilities(self):
        p=m.logistic([[i] for i in range(24)],[int(i>12) for i in range(24)],[[1],[22]])
        self.assertGreater(p[1],p[0])
        self.assertTrue(all(0<pv<1 for pv in p))

    def test_hindcast_target_is_not_predictor_for_same_target(self):
        rows=data()
        sea={}
        p1=m.predictions(rows,(2011,2013),1,'temperatura_aire_c',sea)
        val=p1['local_viento_sst']['2011-02']
        # Alter y(t+1) after the cut; it cannot influence forecast for that same target.
        for row in rows:
            if row['mes']=='2011-02':
                row['temperatura_aire_c']='1000'
        p2=m.predictions(rows,(2011,2013),1,'temperatura_aire_c',sea)
        self.assertEqual(val,p2['local_viento_sst']['2011-02'])

    def test_extreme_train_threshold_ignores_test_year(self):
        rows=data()
        es=m.events(rows,(2011,2013),1,{},'Motupe')
        cutoff=es['climatologia_evento']['2011-02'][2]
        for r in rows:
            if r['mes']=='2013-02':r['precipitacion_mes_mm']='20000'
        e2=m.events(rows,(2011,2013),1,{},'Motupe')
        self.assertEqual(cutoff,e2['climatologia_evento']['2011-02'][2])

    def test_missing_current_blocks_extra_variant(self):
        d=data();by={r['mes']:r for r in d}
        clim=m.normal_features([r for r in d if r['mes']<'2011-01'],by,'Motupe','temperatura_aire_c')
        sea={('Mar_frente_Pimentel','2010-12'):{'corriente_2017_2025_disponible':'False'},
             ('Mar_norte_Lambayeque','2010-12'):{'corriente_2017_2025_disponible':'False'}}
        self.assertIsNone(m.candidate(by,'2010-12',clim,'con_corrientes',sea))

if __name__=='__main__':unittest.main()
