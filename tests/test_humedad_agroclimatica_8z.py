"""QA sintético: humedad relativa y VPD historicos. No observaciones."""
import importlib.util
import json
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'humedad_agroclimatica_8z.py'
spec=importlib.util.spec_from_file_location('h8z',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    day=date(1996,1,1);time=[];rh=[];vpd=[]
    while day<=date(2025,12,31):
        time.append(day.isoformat());rh.append(70.0);vpd.append(.8)
        day+=timedelta(days=1)
    return {'latitude':-6.75,'longitude':-79.75,'timezone':'America/Lima',
        'daily_units':{'relative_humidity_2m_mean':'%','vapour_pressure_deficit_max':'kPa'},
        'daily':{'time':time,'relative_humidity_2m_mean':rh,'vapour_pressure_deficit_max':vpd}}
class Humedad8Z(unittest.TestCase):
    def test_360_months_and_leap(self):
        rows=m.aggregate(json.dumps(fixture()).encode(),'Chiclayo')
        self.assertEqual(len(rows),360)
        self.assertEqual(rows[1]['dias_validos'],29)
        self.assertEqual(rows[0]['rh_2m_media_pct'],70)
    def test_missing_day_rejected(self):
        q=fixture()
        for k in q['daily']:q['daily'][k].pop()
        with self.assertRaises(ValueError):m.aggregate(json.dumps(q).encode(),'Chiclayo')
    def test_rh_not_beyond_100(self):
        q=fixture();q['daily']['relative_humidity_2m_mean'][0]=101
        with self.assertRaises(ValueError):m.aggregate(json.dumps(q).encode(),'Chiclayo')
    def test_units_exact(self):
        q=fixture();q['daily_units']['vapour_pressure_deficit_max']='Pa'
        with self.assertRaisesRegex(ValueError,'Unidad VPD'):m.aggregate(json.dumps(q).encode(),'Chiclayo')
    def test_no_source_honest(self):
        with tempfile.TemporaryDirectory() as d:
            s=m.run(d)
            self.assertFalse(s['cobertura_regional_cuatro_sitios_completa'])
            self.assertEqual(s['registros_mes_sitio'],0)
            self.assertTrue(s['no_alertas_fitosanitarias'])
            m.run(d,check=True)
if __name__=='__main__':unittest.main()
