#!/usr/bin/env python3
"""Mantiene una única fuente de contenido (index.html) y genera app/index.html.
La web no muestra el instalador; la PWA conserva las seis pestañas y los módulos.
El <base> comparte scripts, estilos y JSON de la web, sin duplicar datasets.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"index.html"
APP=ROOT/"app"/"index.html"

BASE='<base href="../">'
MANIFEST='<link rel="manifest" href="app/manifest.webmanifest?v=20261021-app-separada">'
IOS='<link rel="apple-touch-icon" sizes="180x180" href="assets/oaf-apple-touch-icon-180.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="OAF Lambayeque"><meta name="apple-mobile-web-app-status-bar-style" content="default">'
CSS='<link rel="stylesheet" href="assets/oaf-pwa.css?v=20261021-app-separada">'
JS='<script src="assets/oaf-pwa.js?v=20261021-app-separada" defer></script>'
HASH_NAV=r"""<script>
/* El elemento <base> sirve archivos compartidos desde la web,
   pero las anclas de la aplicación deben permanecer en /app/. */
document.addEventListener("click",function(event){
 var a=event.target.closest&&event.target.closest('a[href^="#"]');
 if(!a)return;
 var h=a.getAttribute("href");
 if(!h||h==="#")return;
 event.preventDefault();
 if(location.hash===h){window.dispatchEvent(new Event("hashchange"));}
 else{location.hash=h;}
},true);
</script>"""
def make(index:str)->str:
    # Legacy PWA tags may still be present in an older source; remove before generating.
    index=re.sub(r'<link rel="manifest" href="[^"]*">',"",index)
    index=re.sub(r'<link rel="apple-touch-icon"[^>]*>',"",index)
    index=re.sub(r'<meta name="apple-mobile-web-app-[^"]+"[^>]*>',"",index)
    index=re.sub(r'<link rel="stylesheet" href="assets/oaf-pwa\.css[^"]*">',"",index)
    index=re.sub(r'<script src="assets/oaf-pwa\.js[^"]*" defer></script>',"",index)
    if '<head>' not in index or '</body>' not in index:raise ValueError("HTML incompatible")
    index=index.replace('<head>','<head>'+BASE+MANIFEST+IOS,1)
    anchor=re.search(r'<link rel="stylesheet" href="assets/oaf-responsive-celulares-ux19\.css[^"]*">',index)
    if not anchor:raise ValueError("Falta estilo responsivo")
    index=index[:anchor.end()]+CSS+index[anchor.end():]
    anchor=re.search(r'<script src="assets/oaf-responsive-celulares-ux19\.js[^"]*" defer></script>',index)
    if not anchor:raise ValueError("Falta script responsivo")
    index=index[:anchor.end()]+JS+index[anchor.end():]
    index=re.sub(r'href=["\'](?:\./)?index\.html#([^"\']+)["\']',r'href="#\1"',index)
    index=index.replace('</body>',HASH_NAV+'</body>',1)
    return index
def main():
    content=make(INDEX.read_text(encoding="utf-8"))
    APP.parent.mkdir(parents=True,exist_ok=True)
    APP.write_text(content,encoding="utf-8")
    print("OAF App sincronizada con index.html: seis pestañas, modelos y fuentes originales.",len(content),"caracteres")
if __name__=="__main__":main()
