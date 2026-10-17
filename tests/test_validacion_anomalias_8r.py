"""8R: no fuga temporal, selección previa al test y deduplicación de celdas."""
import importlib.util,math,statistics,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oaf8r",ROOT/"modelos/validacion_anomalias_8r.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    ids=[f"S{i:02d}" for i in range(10)]
    centers={pid:(-6.45+(i//2)*.1,-79.65+(i//2)*.09) for i,pid in enumerate(ids)}
    dates=[f"{year}-{month:02d}" for year in range(1996,2026) for month in range(1,13)]
    seq={}
    for i,pid in enumerate(ids):
        x=0.;monthly={}
        for j,day in enumerate(dates):
            year=int(day[:4]);mon=int(day[-2:])
            x=.6*x + .3*math.sin(j*.23+.2*i)+.05*math.cos(i*1.2+j*.08)
            monthly[day]=20+0.7*i+3*math.sin(2*math.pi*(mon-1)/12)+x
        seq[pid]=monthly
    transects={pid:("V1" if i<6 else "V2") for i,pid in enumerate(ids)}
    return seq,centers,transects

class TestChronology8R(unittest.TestCase):
    def test_unique_cells_are_not_inflated_by_duplicate_api_queries(self):
        monthly,centers,tr=fixture()
        rows,groups,normals=m.features(monthly,centers)
        self.assertEqual(len(groups),5)
        self.assertEqual(len(rows),10*359)
        self.assertEqual(len(m.representative_rows(rows,groups)),5*359)
    def test_calibration_excludes_validation_and_test_years(self):
        monthly,centers,tr=fixture()
        norms=m.normal_monthly(monthly["S00"])
        for mon in range(1,13):
            desired=statistics.mean(monthly["S00"][f"{y}-{mon:02d}"]
                                    for y in range(1996,2011))
            self.assertAlmostEqual(norms[mon],desired)
        before=m.exercise(monthly,centers,tr)[0]
        copied={pid:dict(data) for pid,data in monthly.items()}
        for pid in copied:
            for year in range(2016,2026):
                for mon in range(1,13):
                    copied[pid][f"{year}-{mon:02d}"]+=5+(year-2016)*.7
        after=m.exercise(copied,centers,tr)[0]
        self.assertEqual(before["coeficientes_ridge_congelados"],
                         after["coeficientes_ridge_congelados"])
        self.assertEqual(before["evaluacion_validacion_rmse_por_celda"],
                         after["evaluacion_validacion_rmse_por_celda"])
        self.assertEqual(before["estrategia_seleccionada_por_validacion"],
                         after["estrategia_seleccionada_por_validacion"])
        self.assertNotEqual(before["evaluacion_prueba_por_celda"],
                            after["evaluacion_prueba_por_celda"])
    def test_forecast_2016_jan_only_uses_2015_dec_data(self):
        monthly,centers,tr=fixture()
        report,rows=m.exercise(monthly,centers,tr)
        j=next(r for r in rows if r["mes_objetivo"]=="2016-01" and r["testigo_id"]=="S00")
        self.assertEqual(j["ultimo_mes_observado"],"2015-12")
        self.assertEqual(report["fecha_corte_validacion"],"2015-12")
        self.assertEqual(len(rows),10*120)
        self.assertTrue(report["variables_explicativas_disponibles_t_menos_1"])
    def test_leave_cell_out_regional_predictor_never_uses_same_pixel(self):
        monthly,centers,tr=fixture()
        rows,grp,normals=m.features(monthly,centers)
        a=next(r for r in rows if r["pid"]=="S00" and r["date"]=="2020-04")
        b=next(r for r in rows if r["pid"]=="S01" and r["date"]=="2020-04")
        self.assertAlmostEqual(a["regional"],b["regional"])
        prev="2020-03"
        others=[monthly[f"S{i:02d}"][prev]-normals[f"S{i:02d}"][3]
                for i in (2,4,6,8)]
        self.assertAlmostEqual(a["regional"],statistics.mean(others))
    def test_validation_selection_and_frozen_test_are_reported(self):
        report,rows=m.exercise(*fixture())
        selected=report["estrategia_seleccionada_por_validacion"]
        others=report["evaluacion_validacion_rmse_por_celda"]
        self.assertEqual(selected,min(m.MODELS,key=lambda n:(others[n]["rmse_c"],m.MODELS.index(n))))
        self.assertEqual(report["n_centros_celda_era5land_distintos"],5)
        self.assertEqual(report["n_sitios_pseudoreplicados"],5)
        self.assertEqual(report["evaluacion_prueba_por_celda"][selected]["n"],5*120)
        self.assertEqual(report["zonas_agroclimaticas_homogeneas_certificadas"],0)
        self.assertFalse(report["evaluacion_prospectiva_real"])
        self.assertFalse(report["validacion_instrumental_independiente"])
    def test_nan_or_missing_months_are_not_imputed(self):
        monthly,centers,tr=fixture()
        del monthly["S00"]["2008-05"]
        with self.assertRaises(ValueError):m.exercise(monthly,centers,tr)
    def test_same_data_fits_identically(self):
        obj=fixture()
        a,_=m.exercise(*obj);b,_=m.exercise(*obj)
        self.assertEqual(a,b)
    def test_gaussian_solver_handles_simple_system(self):
        solution=m.solve3([[4.,1.,0.],[1.,3.,1.],[0.,1.,2.]],[5.,5.,3.])
        self.assertAlmostEqual(sum((4,1,0)[j]*solution[j] for j in range(3)),5,places=8)

if __name__=="__main__":unittest.main()
