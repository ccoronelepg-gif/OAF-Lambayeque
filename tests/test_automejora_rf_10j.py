"""10J safe candidate update: no fake post-2025 data, strict provenance and chronology."""
import csv,datetime as dt,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"modelos"))
import actualizacion_automatica_rf_10j as mod

class Tests10JAuto(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory()
  self.path=Path(self.t.name)
  self.now=dt.datetime(2027,3,2,tzinfo=dt.timezone.utc)
  self.sectors={f"S{k:03d}" for k in range(1,40)}
 def tearDown(self):self.t.cleanup()
 def write(self,year=2026,mo=1,missing=0,source="CHIRPS3_FINAL",publication="2026-02-20T10:00:00Z"):
  f=self.path/f"lluvia_CHIRPS3_FINAL_{year}_{mo:02d}.csv"
  with f.open("w",newline="",encoding="utf8") as target:
   writer=csv.DictWriter(target,fieldnames=mod.FIELDS)
   writer.writeheader()
   for sid in sorted(self.sectors)[:-missing or None]:
    writer.writerow({"mes":f"{year}-{mo:02d}","sector":sid,
       "lluvia_mm":"5.1","producto":source,
       "url_fuente":"https://data.chc.ucsb.edu/products/CHIRPS/v3.0/",
       "fecha_publicacion_utc":publication,"sha256_fuente_original":"a"*64})
 def test_empty_no_new_rain_data(self):
  rec,logs,state=mod.parse_staged(self.path,self.sectors,self.now)
  self.assertEqual(state["estado"],"SIN_MESES_NUEVOS")
  self.assertEqual(rec,{})
 def test_accepts_complete_month_with_origin(self):
  self.write()
  records,logs,state=mod.parse_staged(self.path,self.sectors,self.now)
  self.assertEqual(state["n_sectores"],39)
  self.assertEqual(len(records["2026-01"]),39)
  self.assertEqual(len(logs[0]["sha256_archivo_subido"]),64)
 def test_rejects_partial_month(self):
  self.write(missing=1)
  with self.assertRaises(ValueError):mod.parse_staged(self.path,self.sectors,self.now)
 def test_rejects_false_final_date(self):
  self.write(publication="2026-02-02T00:00:00Z")
  with self.assertRaises(ValueError):mod.parse_staged(self.path,self.sectors,self.now)
 def test_rejects_wrong_product(self):
  self.write(source="CHIRPS3_PRELIM")
  with self.assertRaises(ValueError):mod.parse_staged(self.path,self.sectors,self.now)
 def test_rejects_new_month_gap(self):
  self.write(mo=2,publication="2026-03-20T00:00:00Z")
  with self.assertRaises(ValueError):mod.parse_staged(self.path,self.sectors,self.now)
 def test_rejects_missing_source_sha(self):
  self.write()
  path=next(self.path.glob("*.csv"))
  text=path.read_text("utf8").replace("a"*64,"bad")
  path.write_text(text,encoding="utf8")
  with self.assertRaises(ValueError):mod.parse_staged(self.path,self.sectors,self.now)
 def test_calendar_is_bounded(self):
  from itertools import islice
  seq=list(islice(mod.months_between(2025,11),4))
  self.assertEqual(seq,["2025-11","2025-12","2026-01","2026-02"])
if __name__=="__main__":unittest.main()
