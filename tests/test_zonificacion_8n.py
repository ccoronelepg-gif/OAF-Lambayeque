"""Pruebas 8N: cartografía regional, puntos interiores y DEM sintético aislado."""
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
spec=importlib.util.spec_from_file_location("zones8n",REPO/"modelos/zonificacion_preliminar_8n.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestZonificacion8N(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup)
        self.root=Path(d.name)
        path=self.root/m.BOUNDARY
        path.parent.mkdir(parents=True)
        shutil.copyfile(REPO/m.BOUNDARY,path)

    def group(self,i,values=None):
        points=m.batches(self.root)[i-1]
        if values is None:
            bins=[65,160,420,920,1900,2900]
            values=[bins[(i+j)%len(bins)] for j in range(len(points))]
        raw=json.dumps({"elevation":values},separators=(",",":")).encode("utf-8")
        path=m.raw_path(self.root,i);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(gzip.compress(raw,mtime=0))
        meta={"fase":"8N","api":m.ELEV_API,
              "url":m.request_url(points),
              "fuente_de_elevacion":"Open-Meteo Elevation API; DEM, no instrumento",
              "puntos":[p["id"] for p in points],
              "sha256_json_original":hashlib.sha256(raw).hexdigest()}
        m.meta_path(self.root,i).write_text(json.dumps(meta),encoding="utf-8")
        return path

    def test_no_data_no_homogeneity_claim(self):
        summary,rows,centers=m.calculate(self.root)
        self.assertGreater(len(centers),30)
        self.assertEqual(len(rows),0)
        self.assertFalse(summary["homogeneidad_climatica_estadistica_demostrada"])
        self.assertFalse(summary["cobertura_puntual_completa"])
        self.assertEqual(summary["zonas_operativas_aprobadas"],0)
        m.publish(self.root)
        m.publish(self.root,check=True)

    def test_geometry_encloses_study_sites_and_grid_excludes_outside(self):
        geometry,_=m.geom(self.root)
        for point in ((-79.84090,-6.77140),(-79.82280,-6.39278),
                      (-79.71420,-6.15083),(-79.74723,-5.98825)):
            self.assertTrue(m.inside(*point,geometry),point)
        self.assertFalse(m.inside(-80.8,-6.8,geometry))
        self.assertFalse(m.inside(-78.9,-6.8,geometry))
        pts=m.grid(self.root)
        self.assertEqual(len({p["id"] for p in pts}),len(pts))
        self.assertTrue(all(m.inside(p["longitud"],p["latitud"],geometry) for p in pts))

    def test_thresholds_are_candidate_altitude_not_climate(self):
        self.assertEqual(m.band(35),"planicie_muy_baja")
        self.assertEqual(m.band(100),"planicie_valle_interior")
        self.assertEqual(m.band(300),"piedemonte")
        self.assertEqual(m.band(800),"ladera_baja")
        self.assertEqual(m.band(1600),"ladera_media")
        self.assertEqual(m.band(2500),"zona_alta_andina")
        self.assertEqual(m.band(-5),"cota_negativa_dem_verificar")
        self.assertFalse(m.calculate(self.root)[0]["homogeneidad_climatica_estadistica_demostrada"])

    def test_incomplete_batches_do_not_count_as_regional_coverage(self):
        self.group(1)
        summary,rows,centers=m.calculate(self.root)
        self.assertEqual(len(rows),len(m.batches(self.root)[0]))
        self.assertEqual(summary["n_lotes_dem_archivados"],1)
        self.assertEqual(summary["cobertura_puntual_completa"],len(m.batches(self.root))==1)
        self.assertTrue(all(r["clima_homogeneo_validado"]=="false" for r in rows))
        m.publish(self.root)
        m.publish(self.root,check=True)

    def test_all_batches_complete_only_elevational_classes(self):
        for index in range(1,len(m.batches(self.root))+1):self.group(index)
        summary,rows,pts=m.calculate(self.root)
        self.assertEqual(len(rows),len(pts))
        self.assertTrue(summary["cobertura_puntual_completa"])
        self.assertEqual(summary["zonas_operativas_aprobadas"],0)
        self.assertEqual(summary["estado"],"malla_dem_completa_solo_estratificacion_fisica")
        self.assertTrue(all(not d["apto_para_pronostico_por_zona"] for d in summary["estratos"].values()))
        m.publish(self.root)
        m.publish(self.root,check=True)

    def test_tampered_hash_fails_closed(self):
        self.group(1)
        p=m.meta_path(self.root,1);obj=json.loads(p.read_text())
        obj["sha256_json_original"]="0"*64;p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError,"Integridad"):
            m.calculate(self.root)

    def test_missing_or_bad_elevation_not_replaced(self):
        points=m.batches(self.root)[0]
        self.group(1,[None]*len(points))
        with self.assertRaisesRegex(ValueError,"altitud"):
            m.calculate(self.root)

    def test_boundary_source_must_identify_department(self):
        file=self.root/m.BOUNDARY
        obj=json.loads(file.read_text())
        obj["features"][0]["properties"]["codigo_ubigeo"]="06"
        file.write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError,"Límite no identifica"):
            m.calculate(self.root)

if __name__=="__main__":
    unittest.main()
