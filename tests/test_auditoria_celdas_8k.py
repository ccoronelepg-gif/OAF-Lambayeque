"""Tests 8K: geometría auditable y respuestas de proveedor sintéticas SOLO aisladas."""
import csv
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("audit8k",ROOT/"modelos/auditoria_celdas_estaciones_8k.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FILES=(m.SOURCE_SCRIPT,m.STATIONS,m.CANDIDATES,m.AUDIT,m.CELLS,m.TEMP8I,m.TEMP8J)

class TestSpatial8K(unittest.TestCase):
    def setUp(self):
        box=tempfile.TemporaryDirectory()
        self.addCleanup(box.cleanup)
        self.root=Path(box.name)
        for file in FILES:
            target=self.root/file
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/file,target)
        # La prueba de ausencia es aislada incluso si CI ya archivó 4 celdas reales.
        self.write_cells([])

    def write_cells(self,rows):
        with (self.root/m.CELLS).open("w",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=m.CELL_FIELDS)
            writer.writeheader();writer.writerows(rows)

    def fake_cells(self):
        out=[]
        for loc,(lat,lon) in m.sites_from_8d(self.root).items():
            q={"latitude":str(lat),"longitude":str(lon),
               "models":"era5_land","cell_selection":"land",
               "timezone":"America/Lima","start_date":"2020-07-01",
               "end_date":"2020-07-01","daily":"temperature_2m_mean"}
            out.append(dict(localidad_oaf=loc,latitud_solicitada=str(lat),longitud_solicitada=str(lon),
                latitud_respuesta=str(round(lat,1)),longitud_respuesta=str(round(lon,1)),
                elevacion_respuesta_m="41",tipo_elevacion="altura_reportada_api_no_orografia_era5_verificada",
                modelo_solicitado="era5_land",seleccion_celda="land",
                fecha_muestra="2020-07-01",fecha_consulta_utc="2026-10-16T12:00:00+00:00",
                url_consulta="https://archive-api.open-meteo.com/v1/archive?"+urlencode(q),
                fuente_documentacion=m.DOC_URL,sha256_respuesta="a"*64,
                metadatos_celda_8d_originales_verificados="false"))
        return out

    def test_absence_of_model_grid_response_remains_explicit(self):
        report,atlas,ranking=m.build(self.root)
        self.assertEqual(report["estaciones_documentales_historicas_lluvia"],5)
        self.assertEqual(report["variantes_de_coordenadas_estacion"],9)
        self.assertEqual(report["respuestas_geograficas_proveedor_8k"],0)
        self.assertEqual(report["estaciones_con_tmax_tmin_en_boletin_senamhi"],8)
        self.assertEqual(report["coordenadas_celda_8d_originales_verificadas"],0)
        self.assertEqual(len(atlas),4)
        self.assertEqual(len(ranking),36)
        self.assertTrue(all(z["apta_validacion_temperatura"] is False for z in ranking))
        self.assertTrue(all(z["celda_devuelta_por_openmeteo_lat"] is None for z in atlas))
        m.publish(self.root)
        m.publish(self.root,check=True)
        view=json.loads((self.root/m.OUT/"vista_8k.json").read_text(encoding="utf-8"))
        self.assertEqual(len(view["candidatas_termometricas_documentadas"]),8)
        self.assertEqual(len(view["estaciones_historicas_lluvia_cercanas"]),8)

    def test_response_is_not_original_8d_cell(self):
        self.write_cells(self.fake_cells())
        report,atlas,ranking=m.build(self.root)
        self.assertEqual(report["respuestas_geograficas_proveedor_8k"],4)
        self.assertEqual(report["coordenadas_celda_8d_originales_verificadas"],0)
        self.assertTrue(all(z["celda_devuelta_por_openmeteo_lat"] is not None for z in atlas))
        self.assertTrue(all(z["distancia_a_celda_openmeteo_8k_km"] is not None for z in ranking))
        self.assertTrue(all(not z["apta_validacion_temperatura"] for z in ranking))

    def test_official_temperature_bulletin_is_not_an_authorised_daily_series(self):
        path=self.root/m.CANDIDATES
        altered=path.read_text(encoding="utf-8").replace(",false,false,false,false,false,",",true,false,false,false,false,",1)
        path.write_text(altered,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"mención en un boletín"):
            m.build(self.root)

    def test_changed_provider_coordinate_requested_rejected(self):
        x=self.fake_cells()
        x[0]["latitud_solicitada"]="-15.0"
        self.write_cells(x)
        with self.assertRaisesRegex(ValueError,"solicitud no reproducen"):
            m.build(self.root)

    def test_invented_8d_archival_certification_rejected(self):
        x=self.fake_cells()
        x[0]["metadatos_celda_8d_originales_verificados"]="true"
        self.write_cells(x)
        with self.assertRaisesRegex(ValueError,"consulta nueva 8K"):
            m.build(self.root)

    def test_incorrect_model_or_selection_rejected(self):
        x=self.fake_cells()
        x[0]["modelo_solicitado"]="era5"
        self.write_cells(x)
        with self.assertRaisesRegex(ValueError,"modelo 8D"):
            m.build(self.root)

    def test_8d_coord_drift_prevents_reporting(self):
        target=self.root/m.SOURCE_SCRIPT
        s=target.read_text(encoding="utf-8")
        s=s.replace('"Chiclayo":(-6.77140,-79.84090)','"Chiclayo":(-5.00000,-70.00000)')
        target.write_text(s,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"coordenadas originales 8D"):
            m.sites_from_8d(self.root)

    def test_thermal_file_requires_8i_8j_reaudit(self):
        path=self.root/m.TEMP8I
        payload=json.loads(path.read_text(encoding="utf-8"))
        payload["n_estaciones_con_fuente"]=1
        path.write_text(json.dumps(payload),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"reauditar catálogo"):
            m.build(self.root)

    def test_station_variable_cannot_masquerade_as_temperature(self):
        path=self.root/m.STATIONS
        s=path.read_text(encoding="utf-8").replace("precipitacion_mm","temperatura_c",1)
        path.write_text(s,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"historial térmico"):
            m.build(self.root)

    def test_distances_honour_geometry(self):
        self.assertAlmostEqual(m.haversine(-6.7714,-79.8409,-6.7714,-79.8409),0.0)
        self.assertGreater(m.haversine(-6.7714,-79.8409,-6.39278,-79.8228),40)
        with self.assertRaisesRegex(ValueError,"fuera del globo"):
            m.haversine(-99,0,0,0)

    def test_nearest_lattice_is_not_provider_result(self):
        self.assertEqual(m.lattice_nearest(-6.7714),-6.8)
        self.assertEqual(m.lattice_nearest(-79.8409),-79.8)

if __name__=="__main__":
    unittest.main()
