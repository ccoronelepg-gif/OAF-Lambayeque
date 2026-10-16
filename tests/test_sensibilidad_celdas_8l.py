"""Fase 8L: pruebas aisladas sintéticas; no publican resultados ficticios."""
from __future__ import annotations
import csv
import gzip
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("spatial8l",ROOT/"modelos/sensibilidad_celdas_8l.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestSensitivity8L(unittest.TestCase):
    def setUp(self):
        obj=tempfile.TemporaryDirectory()
        self.addCleanup(obj.cleanup)
        self.root=Path(obj.name)
        (self.root/"datos").mkdir(parents=True)
        shutil.copyfile(ROOT/m.HIST,self.root/m.HIST)

    def payload(self,method,start,end):
        days=list(m.expected_dates(start,end))
        out=[]
        for i,(city,(lat,lon)) in enumerate(m.SITES.items()):
            vals=[]
            for d in days:
                y,month=int(d[:4]),int(d[5:7])
                base=17.0+i+(month-1)*0.25+(y-1996)*0.01
                dlt=(0.5 if city=="Chiclayo" else 0.0) if method=="nearest" else 0.0
                vals.append(round(base+dlt,5))
            out.append({
              "latitude":round(lat,3),"longitude":round(lon,3),
              "timezone":"America/Lima","utc_offset_seconds":-18000,
              "elevation":100+i*3,
              "daily":{"time":days,"temperature_2m_mean":vals}
            })
        return out

    def source(self,method,start,end,invalid=False):
        data=self.payload(method,start,end)
        if invalid:data[0]["daily"]["temperature_2m_mean"][-1]=None
        raw=json.dumps(data,separators=(",",":")).encode("utf-8")
        path=m.path_for(self.root,method,start,end)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(gzip.compress(raw,mtime=0))
        metadata={
          "fase":"8L","selection":method,"start":start,"end":end,
          "url":m.build_url(method,start,end),
          "sha256_json_original":hashlib.sha256(raw).hexdigest(),
          "fecha_consulta_utc":"2026-10-16T12:00:00+00:00",
          "unidad":"°C","agregacion":"media_aritmetica_de_medias_diarias",
          "dataset":"ERA5-Land vía Open-Meteo Historical Weather API",
          "documentacion":m.DOCS,"metadata_version":1,
          "no_certifica_celda_original_8d":True
        }
        m.sha_for(self.root,method,start,end).write_text(json.dumps(metadata),encoding="utf-8")

    def all_sources(self):
        for method in m.SELECTIONS:
            for start,end in m.BLOCKS:self.source(method,start,end)

    def test_no_sources_means_no_invented_means_or_skill(self):
        rep,rows=m.evaluate(self.root)
        self.assertEqual(rep["n_pares_mensuales"],0)
        self.assertFalse(rep["habilidad_prospectiva_8e_demostrada"])
        self.assertFalse(rep["resultado_disponible"])
        self.assertIsNone(rep["por_localidad"]["Chiclayo"]["mae_entre_selecciones_c"])
        self.assertEqual(rows,[])
        m.outputs(self.root)
        m.outputs(self.root,check=True)

    def test_synthetic_complete_30_year_window(self):
        self.all_sources()
        rep,rows=m.evaluate(self.root)
        self.assertTrue(rep["resultado_disponible"])
        self.assertEqual(rep["n_pares_mensuales"],1440)
        self.assertEqual(rep["n_consultas_por_bloques"],6)
        self.assertEqual(rep["por_localidad"]["Chiclayo"]["n"],360)
        self.assertEqual(rep["por_localidad"]["Chiclayo"]["mae_entre_selecciones_c"],0.5)
        self.assertEqual(rep["por_localidad"]["Jayanca"]["mae_entre_selecciones_c"],0.0)
        self.assertEqual(rep["por_localidad"]["Chiclayo"]["mae_diferencia_anomalias_c"],0.0)
        self.assertEqual(rep["por_localidad"]["Chiclayo"]["n_meses_abs_diferencia_ge_0_5_c"],360)
        self.assertFalse(rep["habilidad_prospectiva_8e_demostrada"])
        self.assertFalse(rep["celdas_8d_originales_inequivocamente_identificadas"])
        m.outputs(self.root)
        m.outputs(self.root,check=True)

    def test_partial_inputs_refused_instead_of_zero_or_imputation(self):
        self.source("land",1996,2005)
        with self.assertRaisesRegex(ValueError,"Archivo incompleto"):
            m.evaluate(self.root)

    def test_tampered_hash_is_rejected(self):
        self.source("land",1996,2005)
        meta_path=m.sha_for(self.root,"land",1996,2005)
        meta=json.loads(meta_path.read_text())
        meta["sha256_json_original"]="f"*64
        meta_path.write_text(json.dumps(meta),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            m.evaluate(self.root)

    def test_a_missing_day_is_rejected(self):
        values=self.payload("land",1996,2005)
        values[0]["daily"]["time"].pop()
        with self.assertRaisesRegex(ValueError,"Cobertura diaria"):
            m.check_payload(values,"land",1996,2005)

    def test_non_finite_value_rejected(self):
        self.source("land",1996,2005,invalid=True)
        with self.assertRaisesRegex(ValueError,"Valor térmico"):
            m.evaluate(self.root)

    def test_wrong_model_url_refused(self):
        self.source("nearest",1996,2005)
        path=m.sha_for(self.root,"nearest",1996,2005)
        meta=json.loads(path.read_text())
        meta["url"]=meta["url"].replace("era5_land","era5")
        path.write_text(json.dumps(meta),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"URL no reproduce"):
            m.evaluate(self.root)

    def test_expected_daily_range_leap_year_and_month(self):
        self.assertEqual(len(list(m.expected_dates(1996,1996))),366)
        self.assertEqual(len(list(m.expected_dates(1997,1997))),365)
        self.assertEqual(len(list(m.expected_dates(1996,2005))),3653)
        self.assertEqual(len(list(m.expected_dates(2006,2015))),3652)
        self.assertEqual(len(list(m.expected_dates(2016,2025))),3653)

if __name__=="__main__":
    unittest.main()
