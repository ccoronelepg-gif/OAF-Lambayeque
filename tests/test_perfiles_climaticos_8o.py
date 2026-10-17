"""Pruebas de 8O clima: perfiles sintéticos privados; ninguna zona real inventada."""
import csv,gzip,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("clima8o",REPO/"modelos/perfiles_climaticos_8o.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FIELDS=("id","latitud","longitud","altitud_dem_m","estrato_fisico_preliminar",
        "candidato_testigo_climatico","homogeneidad_validada")
class TestClimate8O(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        p=self.root/m.TESTIGOS;p.parent.mkdir(parents=True,exist_ok=True)
        self.testigos=[{"id":f"M{i+1:04d}","latitud":-6.9+i*.06,
             "longitud":-79.9+i*.018,"altitud_dem_m":float(i*160),
             "estrato_fisico_preliminar":"pilot","candidato_testigo_climatico":"true",
             "homogeneidad_validada":"false"} for i in range(12)]
        with p.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(self.testigos)
        (self.root/m.DEM_STATE).write_text(json.dumps({
           "fase":"8O","nodos_dem_verificados":420,"nodos_diseno":420}))
    def block(self,model,start,end,tamper=False):
        days=m.dates(start,end)
        responses=[]
        for i,p in enumerate(self.testigos):
            cluster=(i//6)
            tmean=[20+cluster*6+(int(d[5:7])-1)*0.15 for d in days]
            if model=="era5_land":
                daily={"temperature_2m_mean":tmean,
                   "temperature_2m_max":[v+4 for v in tmean],
                   "temperature_2m_min":[v-4 for v in tmean]}
            else:
                daily={"precipitation_sum":[2+cluster*4 for _ in days],
                   "relative_humidity_2m_mean":[67+cluster*17 for _ in days],
                   "shortwave_radiation_sum":[19-cluster*3 for _ in days]}
            daily["time"]=days
            responses.append({"timezone":"America/Lima","utc_offset_seconds":-18000,
                "latitude":p["latitud"],"longitude":p["longitud"],"elevation":p["altitud_dem_m"],
                "daily":daily})
        blob=json.dumps(responses,separators=(",",":")).encode()
        p,q=m.raw_paths(self.root,model,start,end);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(gzip.compress(blob,mtime=0))
        meta={"fase":"8O","modelo":model,"periodo":[start,end],
             "ids":[r["id"] for r in self.testigos],
             "url":m.query(model,start,end,self.testigos),
             "sha256_original":hashlib.sha256(blob).hexdigest()}
        if tamper:meta["sha256_original"]="0"*64
        q.write_text(json.dumps(meta))
    def test_incomplete_inventory_wont_make_groups(self):
        st,groups,norms=m.build(self.root)
        self.assertEqual(st["n_grupos_similitud_exploratorios"],0)
        self.assertEqual(st["n_testigos_con_perfil_30anios"],0)
        self.assertFalse(st["homogeneidad_espacial_certificada"])
        m.publish(self.root);m.publish(self.root,True)
    def test_partial_decade_never_claims_homogeneity(self):
        self.block("era5_land",1996,2005)
        s,p,n=m.build(self.root)
        self.assertEqual(s["n_fuentes_archivadas"],1)
        self.assertEqual(len(p),0)
        self.assertFalse(s["capacidad_predictiva_zonal_demostrada"])
    def test_six_synthetic_sources_generate_only_exploratory_groups(self):
        for model in m.VARS:
            for start,end in m.BLOCKS:self.block(model,start,end)
        s,p,n=m.build(self.root)
        self.assertEqual(s["n_testigos_con_perfil_30anios"],12)
        self.assertEqual(len(p),12)
        self.assertEqual(len(n),144)
        self.assertGreaterEqual(s["n_grupos_similitud_exploratorios"],2)
        self.assertFalse(s["homogeneidad_espacial_certificada"])
        self.assertEqual(s["zonas_agroclimaticas_operativas"],0)
        self.assertTrue(all(v["zona_climatica_validada"]=="false" for v in p))
        m.publish(self.root);m.publish(self.root,True)
    def test_hash_rejects_fake_provenance(self):
        self.block("era5_land",1996,2005,tamper=True)
        with self.assertRaisesRegex(ValueError,"Integridad"):
            m.build(self.root)
    def test_humidity_bounds_are_enforced(self):
        model,start,end="era5",1996,2005
        self.block(model,start,end)
        p,meta=m.raw_paths(self.root,model,start,end)
        raw=json.loads(gzip.decompress(p.read_bytes()))
        raw[0]["daily"]["relative_humidity_2m_mean"][0]=103
        blob=json.dumps(raw).encode();p.write_bytes(gzip.compress(blob))
        j=json.loads(meta.read_text());j["sha256_original"]=hashlib.sha256(blob).hexdigest()
        meta.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError,"Humedad"):
            m.build(self.root)
    def test_incomplete_dates_rejected(self):
        data=[{"timezone":"America/Lima","utc_offset_seconds":-18000,
          "latitude":p["latitud"],"longitude":p["longitud"],"elevation":30,
          "daily":{"time":[]}} for p in self.testigos]
        with self.assertRaisesRegex(ValueError,"Serie incompleta"):
            m.validate_blob(json.dumps(data).encode(),"era5_land",1996,2005,self.testigos)
    def test_groups_with_singletons_not_scored_as_homogeneous(self):
        vec=[[0.0]*5,[10.0]*5,[20.0]*5]
        parts=m.agglomerate(vec,2)
        self.assertIsNone(m.silhouette(vec,parts))

if __name__=="__main__":unittest.main()
