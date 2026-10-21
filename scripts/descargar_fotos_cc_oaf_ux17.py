#!/usr/bin/env python3
"""Conservar copias autorizadas de fotografías Commons (licencias verificadas).
Mantiene las referencias externas si la descarga está bloqueada. No redistribuye
fotografías comerciales de laboratorios sin permiso expreso.
"""
from __future__ import annotations
import io,json,hashlib
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"fotos_cc"
GALLERY=ROOT/"datos"/"galeria_sanidad_2026.json"
COMMONS={
    "mango-plaga-1":("Ceratitis_capitata_-_adult.jpg","ceratitis_capitata_cc_by_sa.jpg","Daniel Feliciano, CC BY-SA 4.0"),
    "vid-enfermedad-1":("UncinulaNecatorOnGrapes.jpg","oidio_vid_cc_by_sa.jpg","Oliver Macdonald, CC BY-SA 3.0"),
    "banano-plaga-1":("Cosmopolites_sordidus,_banana_weevil_(Mindanao,_Philippines)_01.jpg","picudo_banano_cc0.jpg","Obsidian Soul, CC0"),
}
def run():
    data=json.loads(GALLERY.read_text(encoding="utf-8"))
    count=0;logs=[]
    OUT.mkdir(parents=True,exist_ok=True)
    for id,(filename,outfile,license_text) in COMMONS.items():
        target=OUT/outfile
        if not target.exists():
            url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="") + "?width=960"
            try:
                res=requests.get(url,headers={"User-Agent":"OAF-Lambayeque/1.0 (academic science; Wikimedia Commons attribution retained)"},timeout=(15,45))
                res.raise_for_status()
                if not res.headers.get("Content-Type","").lower().startswith("image/"):
                    raise ValueError("No se devolvió una imagen")
                if len(res.content)>4000000 or len(res.content)<8000:
                    raise ValueError("Tamaño fuera de límites")
                photo=Image.open(io.BytesIO(res.content))
                photo.verify()
                photo=Image.open(io.BytesIO(res.content)).convert("RGB")
                if photo.width<350 or photo.height<200:raise ValueError("Resolución insuficiente")
                photo.thumbnail((1000,1000))
                photo.save(target,"JPEG",quality=88,optimize=True)
            except (requests.RequestException,ValueError,OSError) as exc:
                logs.append(f"{id}: copia fallida: {exc.__class__.__name__}; conservar enlace externo")
                continue
        record=data["organismos"][id]
        record["url"]=f"assets/fotos_cc/{outfile}"
        record["copia_local_licencia"]=license_text
        record["sha256_copia_local"]=hashlib.sha256(target.read_bytes()).hexdigest()
        count+=1
        logs.append(f"{id}: archivo local válido y atribución preservada")
    if count:
        GALLERY.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("\n".join(logs))
    print("fotografias_con_respaldo_local:",count)
if __name__=="__main__":run()
