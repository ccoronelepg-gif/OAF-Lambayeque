"""8Y: unit tests purely synthetic, never claim independent aerosol observations."""
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"modelos"/"diagnostico_particulas_8y.py"
spec=importlib.util.spec_from_file_location("pm_8y",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Test8Y(unittest.TestCase):
    def test_perfect_linear_pearson(self):
        self.assertAlmostEqual(m.pearson([1,2,3,4],[2,4,6,8]),1.0)

    def test_insufficient_overlap_writes_null(self):
        xs=[(f"2025-{i:02d}",i,float(i)) for i in range(1,13)]
        res=m.statistics(xs)
        self.assertIsNone(res["pearson_bruto"])
        self.assertEqual(res["coincidencias"],12)

    def test_seasonal_signal_disappears_after_demeaning(self):
        values=[(f"{yr}-{month:02d}",float(month),float(month)*3)
            for yr in (2023,2024,2025) for month in range(1,13)]
        stat=m.statistics(values)
        self.assertAlmostEqual(stat["pearson_bruto"],1.0)
        self.assertIsNone(stat["pearson_sin_ciclo_mensual"])

    def test_sufficient_36_months_exclusion_year(self):
        values=[(f"{yr}-{mo:02d}",float(mo)+(yr-2023)*.4,
                 float(mo)*.3+float((yr-2023)*(mo%3)))
                 for yr in m.YEARS for mo in range(1,13)]
        d=m.statistics(values)
        self.assertEqual(d["coincidencias"],36)
        self.assertEqual(d["cortes_exclusion_anual_disponibles"],3)
        self.assertTrue(-1<=d["pearson_bruto"]<=1)

    def test_minimum_two_years_and_no_future(self):
        self.assertEqual(m.MIN_MONTHS,24)
        self.assertEqual(m.YEARS,(2023,2024,2025))
        self.assertNotIn(2026,m.YEARS)

    def test_zero_variance_no_fake_effect(self):
        self.assertIsNone(m.pearson([4,4,4],[4,6,8]))

if __name__=="__main__":unittest.main()
