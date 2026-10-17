"""Fase 8T: índices NOAA autenticados, fuga temporal y selección pre-test."""
import importlib.util,math,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ocean8t",REPO/"modelos/contraste_oceanico_8t.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def artificial_index():
    return {f"{y:04d}-{mo:02d}":{"nino12_anom_c":math.sin((y-1996)*.3+mo*.1),
            "nino34_anom_c":math.cos((y-1996)*.2+mo*.1)}
            for y in range(1996,2026) for mo in range(1,13)}

def dummy_record(d):
    return {"date":d,"prev":None,"local":.2,"regional":.4,"y":.8,
      "cell":(-6.8,-79.6),"pid":"M0001","year":int(d[:4])}

class TestOceanIndex8T(unittest.TestCase):
    def test_parse_whitespace_original_format_and_noaaposition(self):
        header=b"YR MON  NINO1+2   ANOM   NINO3    ANOM   NINO4    ANOM NINO3.4    ANOM\n"
        samples=b"".join(
            f"{y} {mo} 25.00 -0.24 26.0 0.3 28.0 -0.1 27.1 0.34\n".encode()
            for y in range(1996,2026) for mo in range(1,13))
        rows=m.parse_noaa(header+samples)
        self.assertEqual(len(rows),360)
        self.assertEqual(rows["1996-01"]["nino12_anom_c"],-.24)
        self.assertEqual(rows["2025-12"]["nino34_anom_c"],.34)
        with self.assertRaisesRegex(ValueError,"360 meses"):
            m.parse_noaa(header+samples.replace(b"1996 1 25.00 -0.24 26.0 0.3 28.0 -0.1 27.1 0.34\n",b""))
    def test_noaa_invalid_or_duplicate_must_fail(self):
        header=b"YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM\n"
        samples=b"".join(f"{y} {mo} 25 -0.2 26 0.2 28 -0.1 27 0.4\n".encode()
            for y in range(1996,2026) for mo in range(1,13))
        with self.assertRaisesRegex(ValueError,"duplicado"):
            m.parse_noaa(header+samples+b"1996 1 25 -0.2 26 0.2 28 -0.1 27 0.4\n")
    def test_ocean_predates_even_previous_target_month(self):
        idx=artificial_index()
        rows=[{"date":"2012-03","prev":"2012-02","local":.2,"regional":.1,"y":.3,
               "year":2012,"cell":(-6.1,-79.9),"pid":"M1"}]
        joined=m.add_ocean(rows,idx)
        self.assertEqual(joined[0]["ocean_month"],"2012-01")
        self.assertLess(joined[0]["ocean_month"],joined[0]["prev"])
        self.assertEqual(joined[0]["ocean12"],idx["2012-01"]["nino12_anom_c"])
    def test_no_target_month_predictor_in_ridge(self):
        data=[{"local":math.sin(j/2),"regional":math.cos(j/2),
               "ocean12":math.sin(j/3),"y":math.sin(j/2)+math.cos(j/2)+math.sin(j/3)}
               for j in range(300)]
        coeff=m.fit_enriched(data)
        self.assertEqual(len(coeff),4)
        p=m.predict(data[1],[0,.5,.5],coeff)
        self.assertTrue(math.isfinite(p["jerarquico_nino12"]))
        self.assertEqual(p["persistencia"],data[1]["local"])
    def test_negative_skill_not_hidden(self):
        rows=[{"anomalia_tmedia_objetivo_c":0,"prediccion_seleccionada_c":1,
          "prediccion_jerarquica_c":.6,"prediccion_persistencia_c":.2}]
        score=m.stats(rows)
        self.assertLess(score["mejora_RMSE_vs_8S"],0)
        self.assertLess(score["mejora_RMSE_vs_persistencia"],0)
    def test_timestamps_validated_by_explicit_index_shift(self):
        idx=artificial_index()
        rows=[{"date":"1996-02","prev":"1996-01","local":0,"regional":0,"y":0,
                "year":1996,"cell":(-6.8,-79.3),"pid":"A"},
              {"date":"1996-03","prev":"1996-02","local":0,"regional":0,"y":0,
                "year":1996,"cell":(-6.8,-79.3),"pid":"A"}]
        result=m.add_ocean(rows,idx)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["ocean_month"],"1996-01")
    def test_spatial_band_id_is_fixed_by_existing_8s(self):
        centers={f"p{i}":(-6.9+i*.04,-79.2+i*.03) for i in range(16)}
        bands=m.regional.geographic_groups(centers)
        self.assertEqual(len(set(bands.values())),4)
        self.assertTrue(all(sum(x==b for x in bands.values())>=2 for b in set(bands.values())))
if __name__=="__main__":unittest.main()
