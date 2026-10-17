"""QA público OAF 2026, diseño sin pérdida de modelos/datos existentes."""
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
ROUTES={
    'inicio':'Inicio',
    'clima':'Análisis de clima regional',
    'nino':'Monitoreo del Niño y anomalías climáticas',
    'cultivos':'Sanidad vegetal',
    'verificaciones':'Investigación y datos'
}
TARGETS={
    'oaf-home-location':'inicio',
    'oaf-live-temp':'inicio',
    'oaf-live-prec':'inicio',
    'oaf-live-hum':'inicio',
    'oaf-live-vpd':'inicio',
    'oaf-live-wind':'inicio',
    'oaf-live-rad':'inicio',
    'oaf-strengths-summary':'inicio',
    'oaf-news-chirps':'inicio',
    'oaf-news-enfen':'inicio',
    'oaf-news-air':'inicio',
    'oaf-news-model':'inicio',
    'wx-data':'clima',
    'oaf-dash-place':'clima',
    'oaf-hist-plot':'clima',
    'oaf-altitudinal-map':'clima',
    'oaf-map-stats':'clima',
    'oaf-zones-8n':'clima',
    'oaf-homogeneity-8o':'clima',
    'oaf-neighbors-8p':'clima',
    'oaf-regional-8s':'clima',
    'oaf-aire-extremos-8x':'clima',
    'oaf-diagnostico-8y':'clima',
    'oaf-8z-humedad':'clima',
    'oaf-nino-pred-data':'nino',
    'oaf-ocean-8t':'nino',
    'oaf-factors-8u':'nino',
    'oaf-integracion-8v':'nino',
    'patologias':'cultivos',
    'oaf-control-cards':'cultivos',
    'modelos-fitosanitarios':'cultivos',
    'cultivos-tab-condiciones':'cultivos',
    'cultivos-tab-prediccion':'cultivos',
    'oaf-benchmark-8w':'verificaciones',
    'oaf-benchmark-9a':'verificaciones',
}

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.ids={}
        self.route=[]
        self.navigation=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and 'data-tab' in a:
            self.navigation.append((a['data-tab'],a.get('href')))
        if tag=='section' and a.get('data-page'):
            self.route.append(a['data-page'])
        if a.get('id'):
            page=next((p[1].get('data-page') for p in reversed(self.stack)
                       if p[1].get('data-page')),None)
            if a['id'] in self.ids:
                raise AssertionError('Duplicate ID '+a['id'])
            self.ids[a['id']]=page
        if tag not in {'meta','link','img','br','hr','input','source','area','wbr','embed','param'}:
            self.stack.append((tag,a))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]
                return

class Redisenio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom=Inventory();cls.dom.feed(HTML)
    def test_five_top_level_pages_only(self):
        self.assertEqual(self.dom.route,list(ROUTES))
        self.assertEqual(self.dom.navigation,[(k,'#'+k) for k in ROUTES])
        for name in ('dashboard','control'):
            self.assertNotIn(name,self.dom.route)
    def test_every_important_module_belongs_to_correct_page(self):
        for element,page in TARGETS.items():
            with self.subTest(element=element):
                self.assertEqual(self.dom.ids.get(element),page)
    def test_all_evidence_and_descriptive_legends_present(self):
        self.assertGreaterEqual(HTML.count('class="oaf-figure-caption"'),15)
        for link in ('https://enfen.imarpe.gob.pe/comunicados/',
          'https://open-meteo.com/en/docs','https://www.cpc.ncep.noaa.gov/',
          'https://www.chc.ucsb.edu/data/chirps','https://atmosphere.copernicus.eu/'):
            self.assertIn(link,HTML)
        self.assertIn('todavía requieren validación instrumental',HTML)
        self.assertIn('no son mediciones de estación',HTML)
        self.assertIn('No es un',HTML)
    def test_subtabs_and_navigation_compatibility(self):
        self.assertEqual(HTML.count('role="tab"'),2)
        self.assertIn("raw==='dashboard'",HTML)
        self.assertIn("raw==='control'",HTML)
        self.assertIn("raw==='riesgos'",HTML)
        self.assertIn("closest('[data-page]')",HTML)
    def test_dynamic_sources_and_js_exist(self):
        for path in ("assets/oaf-arquitectura-2026.js",
                     "assets/oaf-redesign-8f.js",
                     "modelos/visor_benchmark_9a.js"):
            self.assertTrue((ROOT/path).exists(),path)
        self.assertIn('src="assets/oaf-arquitectura-2026.js?v=1"',HTML)
        src=(ROOT/'assets/oaf-arquitectura-2026.js').read_text()
        self.assertIn('datos/muestreo_8o/nodos_dem_8o.csv',src)
        self.assertIn('datos/estado_enfen_3z.json',src)
        self.assertIn('datos/benchmark_9a/estado_benchmark_9a.json',src)
        self.assertNotIn('Datos simulados',src)
    def test_altitude_map_uses_real_verified_points(self):
        data=(ROOT/'datos/muestreo_8o/nodos_dem_8o.csv').read_text().splitlines()
        self.assertEqual(len(data)-1,420)
        self.assertIn('altitud_dem_m',data[0])
        self.assertIn('estrato_fisico_preliminar',data[0])
        self.assertEqual(HTML.count('id="oaf-altitudinal-map"'),1)
        self.assertIn('no son zonas climáticas homogéneas certificadas',HTML)
    def test_home_indicators_and_current_source(self):
        src=(ROOT/'assets/oaf-redesign-8f.js').read_text()
        self.assertIn("shortwave_radiation,wind_speed_10m",src)
        self.assertIn("vpdEstimate",src)
        self.assertNotIn("wind_speed_10m,vapour_pressure_deficit",src)
        self.assertIn("$('#oaf-home-location')",src)
        self.assertIn("'#oaf-live-vpd'",src)
        self.assertIn("'#oaf-live-wind'",src)
    def test_inline_navigation_javascript_syntax(self):
        scripts=re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',HTML)
        source='\n'.join(script for script in scripts if script.strip())
        self.assertIn('function nav()',source)
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'inline-oaf.js'
            dest.write_text(source,encoding='utf-8')
            output=subprocess.run(['node','--check',str(dest)],
                    capture_output=True,text=True,check=False)
            self.assertEqual(output.returncode,0,output.stderr)

    def test_no_orphaned_old_sections(self):
        for match in re.finditer(r'<section data-page="([^"]+)"',HTML):
            self.assertIn(match.group(1),ROUTES)

if __name__=='__main__':unittest.main()
