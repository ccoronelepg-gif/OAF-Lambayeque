"""OAF UX · contrato no regresivo de datos y navegación, octubre 2026."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"index.html").read_text(encoding="utf8")
BASE=json.loads((ROOT/"datos/ux_2026/auditoria_base_2026.json").read_text(encoding="utf8"))
ROUTES=("inicio","clima","nino","cultivos","verificaciones")

class Tracker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.ids={}
        self.pages=[]
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs)
        if tag=="section" and attr.get("data-page"):self.pages.append(attr["data-page"])
        if attr.get("id"):
            value=attr["id"]
            assert value not in self.ids, "ID duplicado: "+value
            page=next((a["data-page"] for t,a in reversed(self.stack) if "data-page" in a),None)
            self.ids[value]=page
        if tag not in {"link","meta","input","img","br","hr","source","area","wbr","embed","param"}:
            self.stack.append((tag,attr))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                self.stack=self.stack[:i]
                return

class UXContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom=Tracker();cls.dom.feed(HTML)

    def test_preserves_all_463_public_ids(self):
        self.assertEqual(len(BASE["ids_conservar"]),463)
        old=set(BASE["ids_conservar"])
        self.assertEqual(old-set(self.dom.ids),set(),"Nunca eliminar IDs de scripts científicos")

    def test_all_previous_45_scripts_preserved_in_order(self):
        names=re.findall(r'<script\b[^>]*src="([^"]+)"',HTML)
        before=BASE["scripts_orden_de_carga"]
        self.assertEqual(len(before),45)
        indices=[names.index(x) for x in before]
        self.assertEqual(indices,sorted(indices))
        for url in names:
            self.assertTrue((ROOT/url.split("?")[0]).is_file(),url)

    def test_five_routes_and_deep_categorization(self):
        self.assertEqual(tuple(self.dom.pages),ROUTES)
        for id in ("oaf-ux-view-quick","oaf-ux-view-technical","oaf-mobile-menu",
                   "oaf-current-city","oaf-trust-legend"):
            self.assertIn(id,self.dom.ids)
        for id in ("oaf-research-categories","oaf-research-deep"):
            self.assertEqual(self.dom.ids[id],"verificaciones")
        for term in ("Clima regional","Océano y El Niño","Sanidad vegetal","Validación científica"):
            self.assertIn(term,HTML)

    def test_home_modules_location_and_six_contracts(self):
        for id in ("oaf-zone-primary","oaf-home-location","oaf-home-phytosanitary",
                   "oaf-home-nino","oaf-regional-map-heading","oaf-altitudinal-map",
                   "oaf-home-news-title","oaf-home-data-source","oaf-home-technology",
                   "oaf-forecast-grid"):
            self.assertEqual(self.dom.ids[id],"inicio",id)
        self.assertEqual(HTML.count('id="oaf-altitudinal-map"'),1)
        for id in ("temp","prec","hum","vpd","wind","rad","air"):
            self.assertEqual(self.dom.ids["oaf-live-"+id],"inicio")
            self.assertEqual(self.dom.ids["oaf-meta-"+id],"inicio")
        for id in ("temp","rain","humidity","radiation"):
            self.assertEqual(self.dom.ids["oaf-forecast-"+id],"inicio")
            self.assertEqual(self.dom.ids["oaf-forecast-"+id+"-meta"],"inicio")
        home=HTML.split('<section data-page="inicio" id="inicio">')[1].split('<section data-page="clima"')[0]
        self.assertLess(home.index('id="oaf-zone-primary"'),home.index('id="oaf-main-indicators"'))
        self.assertLess(home.index('id="oaf-home-nino"'),home.index('id="oaf-regional-map-heading"'))
        self.assertIn("Blueberry_close_up.jpg",home)
        self.assertIn("Bunch_Of_Grapes_On_Vine.jpg",home)

    def test_no_pseudo_evidence_or_false_alert(self):
        src=(ROOT/"assets/oaf-ux-data-2026.js").read_text(encoding="utf8")
        curr=(ROOT/"assets/oaf-inicio-climatico-2026.js").read_text(encoding="utf8")
        self.assertIn('j.verificacion==="verificada"',src)
        self.assertIn("j.url_comunicado",src)
        self.assertIn('forecast_days:"7"',src)
        for key in ("temperature_2m_max","precipitation_sum","relative_humidity_2m_mean","shortwave_radiation_sum"):
            self.assertIn(key,src)
        for w in ("oaf:weather",'"oaf-meta-"+id',"oaf-meta-air"):
            self.assertIn(w,curr)
        self.assertNotIn("t>=33",curr)
        self.assertNotIn("h>=80",curr)
        self.assertIn("condiciones meteorológicas favorables no significan presencia confirmada",HTML)
        self.assertIn("Zonificación exploratoria — no oficial",HTML)
        self.assertIn("no emite alertas oficiales",HTML)
        self.assertNotIn("IA predictiva validada",HTML)

    def test_data_sources_and_no_duplicate_map(self):
        assert "420" in HTML and "datos/muestreo_8o/nodos_dem_8o.csv" in HTML
        for org in ("SENAMHI","ENFEN","NOAA","Copernicus","CHIRPS","Open-Meteo","CAMS"):
            self.assertIn(org,HTML)
        self.assertIn("Fuente",HTML)
        self.assertIn("MAE",HTML)
        self.assertIn("RMSE",HTML)
        self.assertIn("Machine Learning",HTML)

if __name__=="__main__":unittest.main()
