"""8X material particulado: pruebas con datos sintéticos, NO mediciones."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'modelos'/'particulas_aire_8x.py'
spec=importlib.util.spec_from_file_location('aire8x',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fabricated(year=2025, missing=False):
    from datetime import datetime,timedelta
    d=datetime(year,1,1);end=datetime(year+1,1,1)
    times=[];p25=[];p10=[]
    while d<end:
        times.append(d.strftime('%Y-%m-%dT%H:%M'))
        p25.append(None if missing and d.month==2 else 12.5)
        p10.append(28.0)
        d+=timedelta(hours=1)
    return dict(timezone='GMT',hourly_units={'pm2_5':'μg/m³','pm10':'μg/m³'},
                hourly=dict(time=times,pm2_5=p25,pm10=p10))

class Aire8XTests(unittest.TestCase):
    def test_api_calendar_complete_and_ugm3(self):
        rows,step=m.response_to_months(fabricated(),'Motupe',2025)
        self.assertEqual(len(rows),12)
        self.assertEqual(step,1)
        self.assertEqual(rows[0]['pm25_media_ug_m3'],12.5)
        self.assertEqual(rows[0]['pm10_media_ug_m3'],28.0)

    def test_low_coverage_does_not_impute_month(self):
        rows,_=m.response_to_months(fabricated(missing=True),'Motupe',2025)
        self.assertFalse(rows[1]['mes_pm_completo_80pct'])
        self.assertEqual(rows[1]['pm25_media_ug_m3'],'')
        self.assertEqual(rows[1]['pm10_media_ug_m3'],28.0)

    def test_units_critical(self):
        r=fabricated()
        r['hourly_units']['pm10']='mg/m³'
        with self.assertRaisesRegex(ValueError,'Unidad'):m.response_to_months(r,'Olmos',2025)

    def test_duplicate_time_rejected(self):
        r=fabricated();r['hourly']['time'][1]=r['hourly']['time'][0]
        with self.assertRaisesRegex(ValueError,'duplicadas'):m.response_to_months(r,'Olmos',2025)

    def test_missing_timestamps_rejected(self):
        r=fabricated()
        for key in ('time','pm2_5','pm10'):r['hourly'][key].pop()
        with self.assertRaises(ValueError):m.response_to_months(r,'Olmos',2025)

    def test_no_source_honest_state(self):
        with tempfile.TemporaryDirectory() as temp:
            state=m.execute(temp)
            self.assertEqual(state['filas_mes_sitio'],0)
            self.assertFalse(state['serie_pm_1996_2025_completa'])
            self.assertFalse(state['comparacion_legal_ECA_habilitada'])
            self.assertFalse(state['csv_publicado'])
            m.execute(temp,check=True)

    def test_not_combine_pm25_and_pm10(self):
        r=fabricated()
        rows,_=m.response_to_months(r,'Chiclayo',2025)
        self.assertNotEqual(rows[3]['pm25_media_ug_m3'],rows[3]['pm10_media_ug_m3'])

if __name__=='__main__':unittest.main()
