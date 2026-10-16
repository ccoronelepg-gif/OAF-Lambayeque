"""OAF 8M: pruebas sintéticas aisladas, nunca publicadas como observaciones."""
from __future__ import annotations
import csv
import gzip
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf8m",REPO/"modelos/sensibilidad_vecindad_8m.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestVecindad8M(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root=Path(d.name)
        p=self.root/m.REFERENCE
        p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(REPO/m.REFERENCE,p)
        self.ref=m.load_reference(self.root)

    def write_one(self,city,start,end,modified=False,bad=False):
        dates=m.calendar_dates(start,end)
        allresponses=[]
        for direction,requested in m.locations(city):
            shifted=direction!="C"
            temps=[]
            for day in dates:
                v=self.ref[(city,day[:7])]
                if shifted:v+=0.5
                temps.append(round(v,5))
            if bad and direction=="NE":temps[0]=None
            lat,lon=requested
            allresponses.append({
                "timezone":"America/Lima",
                "utc_offset_seconds":-18000,
                "latitude":round(lat+(0.03 if shifted else 0),6),
                "longitude":round(lon+(0.02 if shifted else 0),6),
                "elevation":100+(10 if shifted else 0),
                "daily":{"time":dates,"temperature_2m_mean":temps}
            })
        if modified:
            allresponses[0]["daily"]["temperature_2m_mean"][0]+=1.0
        blob=json.dumps(allresponses,ensure_ascii=False,separators=(",",":")).encode("utf-8")
        data=m.source_path(self.root,city,start,end)
        data.parent.mkdir(parents=True,exist_ok=True)
        data.write_bytes(gzip.compress(blob,mtime=0))
        meta={
          "fase":"8M","ciudad":city,"periodo":[start,end],
          "url":m.build_url(city,start,end),
          "sha256_respuesta_original":hashlib.sha256(blob).hexdigest(),
          "consulta_utc":"2026-10-16T12:00:00+00:00",
          "variable":"temperature_2m_mean","modelo":"era5_land",
          "seleccion":"land",
          "ajuste_elevacion":"valor_predeterminado_openmeteo_90m",
          "sin_validacion_instrumental":True,
          "documentacion":m.DOCS
        }
        m.meta_path(self.root,city,start,end).write_text(
            json.dumps(meta,ensure_ascii=False),encoding="utf-8")

    def create_all(self):
        for city in m.SITES:
            for start,end in m.BLOCKS:self.write_one(city,start,end)

    def test_no_input_means_empty_metrics_and_no_false_alerts(self):
        rep,points,pairs=m.evaluate(self.root)
        self.assertFalse(rep["resultados_disponibles"])
        self.assertEqual(rep["n_pares_mensuales_comparados"],0)
        self.assertIsNone(rep["por_localidad"]["Chiclayo"]["max_mae_tmedia_c"])
        self.assertFalse(rep["habilidad_prospectiva_8e_demostrada"])
        self.assertFalse(rep["validacion_instrumental"])
        self.assertEqual(points,[])
        self.assertEqual(pairs,[])
        m.publish(self.root)
        m.publish(self.root,check=True)

    def test_design_is_declared_in_advance_and_geographically_consistent(self):
        self.assertEqual(len(m.SITES),4)
        self.assertEqual(len(m.OFFSETS),9)
        self.assertEqual(m.locations("Chiclayo")[0],("C",m.SITES["Chiclayo"]))
        self.assertEqual(len(m.calendar_dates(1996,2005)),3653)
        self.assertEqual(len(m.calendar_dates(2006,2015)),3652)
        self.assertEqual(len(m.calendar_dates(2016,2025)),3653)
        self.assertEqual(round(m.haversine(*m.SITES["Chiclayo"],*m.locations("Chiclayo")[1][1]),1),5.6)

    def test_partial_sources_do_not_publish_any_pair(self):
        self.write_one("Chiclayo",1996,2005)
        rep,points,pairs=m.evaluate(self.root)
        self.assertEqual(rep["estado"],"fuentes_parciales_no_se_publican_resultados")
        self.assertEqual(rep["bloques_presentes"],1)
        self.assertEqual(points,[])
        self.assertEqual(pairs,[])

    def test_one_city_with_three_complete_decades_is_publishable_as_local_only(self):
        for start,end in m.BLOCKS:
            self.write_one("Chiclayo",start,end)
        report,points,pairs=m.evaluate(self.root)
        self.assertFalse(report["resultados_disponibles"])
        self.assertEqual(report["estado"],"localidades_completas_regional_pendiente")
        self.assertEqual(report["localidades_con_periodo_completo"],["Chiclayo"])
        self.assertEqual(report["n_pares_mensuales_comparados"],2880)
        self.assertEqual(len(points),9)
        self.assertEqual(len(pairs),2880)
        self.assertEqual(report["por_localidad"]["Chiclayo"]["n_puntos"],9)
        self.assertEqual(report["por_localidad"]["Olmos"]["n_puntos"],0)
        self.assertFalse(report["validacion_instrumental"])
        m.publish(self.root)
        m.publish(self.root,check=True)

    def test_full_synthetic_set_has_exact_months_and_zero_anomaly_delta_for_constant_offset(self):
        self.create_all()
        rep,points,pairs=m.evaluate(self.root)
        self.assertTrue(rep["resultados_disponibles"])
        self.assertEqual(rep["n_pares_mensuales_comparados"],11520)
        self.assertEqual(len(points),36)
        self.assertEqual(len(pairs),11520)
        self.assertEqual(rep["por_localidad"]["Olmos"]["n_vecinos_con_celda_distinta"],8)
        self.assertEqual(rep["por_localidad"]["Olmos"]["max_mae_tmedia_c"],0.5)
        self.assertEqual(rep["por_localidad"]["Chiclayo"]["max_mae_diferencia_anomalias_c"],0.0)
        self.assertEqual(rep["por_localidad"]["Motupe"]["max_diferencia_mensual_absoluta_c"],0.5)
        self.assertEqual({r["direccion"] for r in pairs},set(m.OFFSETS)-{"C"})
        self.assertTrue(all(r["centro_celda_distinto"] for r in pairs))
        self.assertFalse(rep["habilidad_prospectiva_8e_demostrada"])
        m.publish(self.root)
        m.publish(self.root,check=True)
        view=json.loads((self.root/m.OUTPUT/"vista_8m.json").read_text(encoding="utf-8"))
        self.assertEqual(view["n_pares_mensuales"],11520)

    def test_response_hash_cannot_be_changed(self):
        self.write_one("Olmos",1996,2005)
        path=m.meta_path(self.root,"Olmos",1996,2005)
        meta=json.loads(path.read_text())
        meta["sha256_respuesta_original"]="f"*64
        path.write_text(json.dumps(meta),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"SHA/URL"):
            m.evaluate(self.root)

    def test_missing_day_is_not_imputed(self):
        self.write_one("Olmos",1996,2005,bad=True)
        with self.assertRaisesRegex(ValueError,"fuera de rango físico"):
            m.evaluate(self.root)

    def test_changed_center_cannot_pass_reference_8l(self):
        self.create_all()
        self.write_one("Chiclayo",1996,2005,modified=True)
        with self.assertRaisesRegex(ValueError,"no reproduce archivo 8L"):
            m.evaluate(self.root)

    def test_wrong_model_url_is_rejected(self):
        self.write_one("Olmos",1996,2005)
        path=m.meta_path(self.root,"Olmos",1996,2005)
        meta=json.loads(path.read_text())
        meta["modelo"]="era5"
        path.write_text(json.dumps(meta),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"SHA/URL"):
            m.evaluate(self.root)

if __name__=="__main__":
    unittest.main()
