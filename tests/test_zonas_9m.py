"""9M — regresiones físicas, hidrológicas y publicación honesta."""
import csv,hashlib,json,sys,unittest
from pathlib import Path
from shapely.geometry import shape,box
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"modelos"))
import sensibilidad_relieve_9m as top
import zonas_hidrograficas_9m as ana

class Agrozonas9M(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.geo,cls.status,cls.rows=top.measure()

 def test_relieve_real_y_todos_los_sectores_evaluados_o_excluidos(self):
  s=self.status
  self.assertEqual(s["fase"],"9M")
  self.assertEqual(s["n_sectores_9k"],42)
  self.assertEqual(len(self.rows),42)
  self.assertEqual(s["comparacion_resoluciones_m"],[270,450])
  self.assertEqual(s["umbrales_pendiente_grados"],[20,30,40])
  self.assertEqual(hashlib.sha256(top.SOURCE.read_bytes()).hexdigest(),
                   s["dem_original_9l_sha256"])
  self.assertEqual(sum(s["estado_cobertura"].values()),42)
  self.assertEqual(len(self.geo["features"]),s["n_geometrias_refinadas"])
  self.assertFalse(s["downscaling_nmme_entrenado"])
  self.assertFalse(s["alerta_fitosanitaria_generada"])
  self.assertEqual(s["n_zonas_homogeneas_certificadas"],0)

 def test_umbrales_ordenados_y_estabilidad_no_inventada(self):
  ok=[r for r in self.rows if r["tipo_cobertura"] in ("parcial","completa")]
  self.assertEqual(len(ok),self.status["n_sector_evaluados_con_dos_escalas"])
  self.assertTrue(len(ok)>=5)
  for p in ok:
   for scale in (270,450):
    vals=[p[f"compatible_{scale}m_{t}"] for t in (20,30,40)]
    self.assertTrue(all(isinstance(x,float) and 0<=x<=1 for x in vals))
    self.assertLessEqual(vals[0],vals[1]);self.assertLessEqual(vals[1],vals[2])
   self.assertLessEqual(p["sensibilidad_30grados_abs_270_vs_450"],1)
   self.assertIn(p["aspecto_dominante_270m"],("N","E","S","O",None))
   self.assertFalse(p["zona_homogenea_validada"])
   self.assertFalse(p["riesgo_fitosanitario_validado"])

 def test_geometria_en_poligono_original_y_tesela(self):
  original=json.loads(top.SECTORS.read_text("utf8"))["features"]
  byid={f["properties"]["id_sector"]:shape(f["geometry"]) for f in original}
  with __import__("rasterio").open(top.SOURCE) as ds:
   tile=box(*ds.bounds)
  for f in self.geo["features"]:
   p=f["properties"];geom=shape(f["geometry"])
   self.assertTrue(geom.is_valid)
   self.assertFalse(p["prediccion_zonal_validada"])
   self.assertFalse(p["cuenca_certificada"])
   self.assertLess(geom.difference(byid[p["id_sector_9k"]].buffer(.00001)).area,1e-8)
   self.assertLess(geom.difference(tile.buffer(.00001)).area,1e-8)

 def test_hidrografia_no_se_certifica_por_superposicion(self):
  self.assertTrue(ana.ENDPOINT.endswith("FeatureServer/7/query"))
  self.assertIn("www.idep.gob.pe",ana.ENDPOINT)
  if not ana.STATE.exists():return
  a=json.loads(ana.STATE.read_text("utf8"))
  g=json.loads(ana.OVERLAY.read_text("utf8"))
  self.assertEqual(a["fase"],"9M")
  self.assertEqual(a["n_intersecciones_referenciales"],len(g["features"]))
  self.assertEqual(a["n_cuencas_certificadas_por_oaf"],0)
  self.assertFalse(a["alertas_fitosanitarias_habilitadas"])
  self.assertFalse(g["metadata"]["capas_hidrograficas_certificadas"])
  if a["cobertura_institucional_capa_descargada"]:
   self.assertTrue(ana.RAW.exists())
   raw=__import__("gzip").decompress(ana.RAW.read_bytes())
   self.assertEqual(hashlib.sha256(raw).hexdigest(),a["sha256_original"])
   self.assertGreater(a["n_unidades_devueltas"],0)

 def test_archivos_y_frontend_sin_perder_cinco_rutas(self):
  h=(ROOT/"index.html").read_text("utf8")
  self.assertEqual(h.count('<section data-page='),5)
  i=h.indexOf('<section data-page="clima"')
  j=h.indexOf('<section data-page="nino"',i)
  part=h[i:j]
  for key in ("oaf-9m-visor","oaf-9m-map","oaf-9m-floor","oaf-9m-table",
              "oaf-9m-catchments","oaf-9m-detail","oaf-9m-status"):
   self.assertEqual(part.count('id="'+key+'"'),1,key)
  self.assertIn("modelos/visor_zonas_9m.js",h)
  self.assertIn("assets/oaf-zonas-9m.css",h)
  self.assertIn("FASE_9M_SENSIBILIDAD_CUENCAS.md",h)

 def test_salidas_deterministas(self):
  if top.STATE.exists() and top.GEO.exists() and top.CSV.exists():
   top.run(check=True)

if __name__=="__main__":unittest.main()
