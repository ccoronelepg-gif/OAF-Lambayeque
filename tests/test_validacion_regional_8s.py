"""8S: 11 tests of regional rolling-window forecasting and spatial holdout."""
import importlib.util,math,statistics,tempfile,unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("stage8s",REPO/"modelos/validacion_regional_8s.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture(n=16):
    months=[f"{y}-{mon:02d}" for y in range(1996,2026) for mon in range(1,13)]
    monthly={};cell={};meta={}
    for i in range(n):
        pid=f"TEST{i:02d}"
        # Five latitude bands with spatially distinct temperature centers.
        lat=-7.3+.11*(i//2)
        lon=-80.1+.05*(i//2)
        cell[pid]=(lat,lon)
        seasonal=2.0*math.sin(i*.1)
        series={}
        for k,key in enumerate(months):
            month=int(key[-2:]);yr=int(key[:4])
            fluct=.4*math.sin(k*.2)+.3*math.cos(k*.05+i*.03)
            series[key]=20.+seasonal+3*math.sin(month*math.pi/6)+.012*(yr-1996)+fluct
        monthly[pid]=series
        meta[pid]={"estrato_fisico_preliminar":m.ALT[i%6]}
    return monthly,cell,meta

class TestStage8S(unittest.TestCase):
    def test_latitude_blocks_hold_out_distinct_grid_cells(self):
        monthly,centers,meta=fixture(32)
        g=m.geographic_groups(centers)
        self.assertEqual(len(set(g.values())),4)
        self.assertTrue(all(sum(z==k for z in g.values())>=2 for k in set(g.values())))
    def test_original_reanalysis_duplicate_requests_one_vote(self):
        monthly,centers,meta=fixture(16)
        rows,unique,norm=m.monthly_folds(monthly,centers,2008)
        self.assertEqual(len(unique),8)
        self.assertEqual(len(rows),8*359)
        self.assertEqual(set(unique.keys()),set(centers.values()))
    def test_no_validation_or_test_information_in_2008_normals(self):
        monthly,centers,meta=fixture()
        _,_,norm=m.monthly_folds(monthly,centers,2008)
        expected=statistics.mean(monthly["TEST00"][f"{y}-01"] for y in range(1996,2009))
        self.assertAlmostEqual(norm["TEST00"][1],expected)
        for site in monthly:
            for year in range(2012,2026):
                monthly[site][f"{year}-01"]+=200
        _,_,norm2=m.monthly_folds(monthly,centers,2008)
        self.assertEqual(norm,norm2)
    def test_training_validation_unchanged_by_mutating_future_test(self):
        monthly,centers,meta=fixture(16)
        old,_,_=m.monthly_folds(monthly,centers,2008)
        for pid in monthly:
            for year in range(2012,2026):
                for mon in range(1,13):
                    monthly[pid][f"{year}-{mon:02d}"]+=50
        new,_,_=m.monthly_folds(monthly,centers,2008)
        a=[r for r in old if 1997<=r["year"]<=2011]
        b=[r for r in new if 1997<=r["year"]<=2011]
        self.assertEqual(a,b)
    def test_geographic_holdout_excludes_region_from_peer_regional_lags(self):
        monthly,centers,meta=fixture(32)
        groups=m.geographic_groups(centers)
        held=groups[centers["TEST00"]]
        a,unique,norm=m.monthly_folds(monthly,centers,2008,held,groups)
        first=next(r for r in a if r["pid"]=="TEST04" and r["date"]=="2011-04")
        included=[pid[0] for c,pid in unique.items() if c!=first["cell"] and groups[c]!=held]
        expected=statistics.mean(monthly[p]["2011-03"]-norm[p][3] for p in included)
        self.assertAlmostEqual(first["regional"],expected)
    def test_rolling_test_ranges_do_not_overlap_validation(self):
        for end,startval,endval,starttest,endtest in m.YEARS:
            self.assertLess(end,startval)
            self.assertLess(endval,starttest)
            self.assertLessEqual(endtest,2025)
        self.assertEqual((m.YEARS[0][-2],m.YEARS[-1][-1]),(2012,2025))
    def test_five_rolls_spatial_splits_and_no_operational_skill(self):
        monthly,centers,meta=fixture(32)
        roll,temporal,spatial,diag,groups=m.evaluate_region(monthly,centers,meta)
        self.assertEqual(len(roll),5)
        self.assertEqual(len(diag),20)
        self.assertEqual(len(temporal),len(spatial))
        self.assertEqual({r["mes_objetivo"][:4] for r in temporal},
          {str(y) for y in range(2012,2026)})
        self.assertEqual(len(set((r["centro_celda_era5land"],r["mes_objetivo"]) for r in spatial)),
          len(spatial))
        self.assertTrue(all(r["mes_dato_mas_reciente"]<r["mes_objetivo"] for r in spatial))
    def test_validated_models_are_chosen_prior_to_test(self):
        monthly,centers,meta=fixture(32)
        rolls,*rest=m.evaluate_region(monthly,centers,meta)
        for row in rolls:
            names=row["rmse_validacion_por_modelo"]
            self.assertEqual(row["modelo_elegido"],
              min(m.MODELS,key=lambda key:(names[key],m.MODELS.index(key))))
    def test_guard_missing_year_and_nans(self):
        monthly,centers,meta=fixture(32)
        del monthly["TEST00"]["2006-01"]
        with self.assertRaises(ValueError):
            m.evaluate_region(monthly,centers,meta)
    def test_report_skill_not_clipped_when_model_underperforms(self):
        fake=[{"prediccion_c":10,"persistencia_c":0,"anomalía_observada_c":1,
             "estrato_altitudinal":"montana_media","climatologia_c":0}]
        x=m.series_report(fake)
        self.assertFalse(x["mejora_persistencia"])
        self.assertLess(x["skill_rmse_vs_persistencia"],0)
    def test_source_is_not_pseudo_ground_truth(self):
        monthly,centers,meta=fixture(32)
        groups=m.geographic_groups(centers)
        self.assertEqual(len(set(groups.values())),4)
        self.assertGreater(len(centers),len(set(centers.values())))

if __name__=="__main__":unittest.main()
