"""8O: 9 comprobaciones independientes del muestreo, DEM y selección piloto."""
import gzip,hashlib,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("sampling8o",REPO/"modelos/muestreo_homogeneidad_8o.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Test8O(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        for path in (m.ORIGIN,m.BOUNDARY):
            dest=self.root/path;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(REPO/path,dest)
    def sample(self,i):
        group=m.batches(self.root)[i-1]
        heights=[float((i+j)*37%3300) for j in range(len(group))]
        raw=json.dumps({"elevation":heights}).encode()
        path,meta=m.paths(self.root,i);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(gzip.compress(raw,mtime=0))
        meta.write_text(json.dumps({"fase":"8O","url":m.url(group),
             "ids":[p["id"] for p in group],"sha256_original":hashlib.sha256(raw).hexdigest(),
             "tipo":"Elevación DEM Open-Meteo (GLO-90); no estación"}))
        return path,meta
    def test_grid_is_genuinely_finer_than_8n(self):
        pts,anchors=m.definition(self.root)
        self.assertGreater(len(pts),350)
        self.assertLess(len(pts),800)
        self.assertGreater(len(anchors),10)
        self.assertEqual(len({(p["latitud"],p["longitud"]) for p in pts}),len(pts))
        self.assertTrue(any(p["tipo_muestreo"]=="refuerzo_003125" for p in pts))
    def test_only_inside_reference_boundary(self):
        geom=m.geometry(self.root)
        pts,_=m.definition(self.root)
        self.assertTrue(all(m.inside(p["longitud"],p["latitud"],geom) for p in pts))
        self.assertFalse(m.inside(-80.9,-6.8,geom))
    def test_no_dem_produces_no_zones_or_testigos(self):
        state,plan,pts,chosen=m.compute(self.root)
        self.assertEqual(len(pts),0)
        self.assertEqual(len(chosen),0)
        self.assertEqual(state["zonas_homogeneas_demostradas"],0)
        m.publish(self.root);m.publish(self.root,True)
    def test_partial_dem_not_certified_as_complete(self):
        self.sample(1)
        state,plan,pts,chosen=m.compute(self.root)
        self.assertEqual(len(pts),len(m.batches(self.root)[0]))
        self.assertEqual(len(chosen),0)
        self.assertEqual(state["zonas_homogeneas_demostradas"],0)
    def test_full_synthetic_dem_selects_multiple_bands_only_as_pilot(self):
        for i in range(1,len(m.batches(self.root))+1):self.sample(i)
        state,plan,pts,chosen=m.compute(self.root)
        self.assertEqual(len(pts),len(plan))
        self.assertTrue(12<=len(chosen)<=19)
        self.assertTrue(all(p["homogeneidad_validada"]=="false" for p in pts))
        self.assertEqual(state["zonas_homogeneas_demostradas"],0)
        self.assertEqual(len(set(p["id"] for p in chosen)),len(chosen))
        m.publish(self.root);m.publish(self.root,True)
    def test_sha_tamper_is_never_accepted(self):
        _,metadata=self.sample(1)
        x=json.loads(metadata.read_text())
        x["sha256_original"]="0"*64;metadata.write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError,"integridad"):
            m.compute(self.root)
    def test_missing_dem_elevation_fails(self):
        path,metadata=self.sample(1)
        payload={"elevation":[None]*len(m.batches(self.root)[0])}
        raw=json.dumps(payload).encode();path.write_bytes(gzip.compress(raw))
        meta=json.loads(metadata.read_text());meta["sha256_original"]=hashlib.sha256(raw).hexdigest()
        metadata.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError,"Altitud DEM"):
            m.compute(self.root)
    def test_negative_dem_stays_review_not_synthetic_zero(self):
        self.assertEqual(m.band(-2),"cota_negativa_revisar")
        self.assertEqual(m.band(0),"llanura_costa")
        self.assertEqual(m.band(1600),"montana_media")
    def test_missing_original_8n_refused(self):
        target=self.root/m.ORIGIN
        target.write_text("no es csv")
        with self.assertRaises(ValueError):
            m.definition(self.root)

if __name__=="__main__":unittest.main()
