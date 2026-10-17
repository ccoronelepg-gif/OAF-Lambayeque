#!/usr/bin/env python3
"""9V: discovery and scientific provenance gate for polygon monthly data.
No fabrication, no use of 5 recent monitoring points as sectoral panels.
Standard library only. Run: python scripts/auditar_insumos_sectoriales_9v.py
"""
import csv, hashlib, json, re, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"resultados"/"9v"
REQUIRED={"sector_id","mes","lluvia_mm"}
EXPECTED={f"{year:04d}-{month:02d}" for year in range(1996,2026) for month in range(1,13)}
CANDIDATE_PATTERNS=("sector","polig","homogene","9q","9r")
def hash_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
def analyze(p):
    item={"archivo":str(p.relative_to(ROOT)),"sha256":hash_file(p),"bytes":p.stat().st_size,"valido":False}
    try:
        with p.open(encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            fields=set(reader.fieldnames or [])
            item["columnas"]=sorted(fields)
            if not REQUIRED.issubset(fields):
                item["causa"]="columnas_incompatibles"
                return item
            counts={}
            for idx,row in enumerate(reader,2):
                sector=(row.get("sector_id") or "").strip()
                month=(row.get("mes") or "").strip()
                if not sector or not re.fullmatch(r"\\d{4}-(0[1-9]|1[0-2])",month):
                    raise ValueError(f"identificador/fecha inválidos, línea {idx}")
                value=float(row["lluvia_mm"])
                if not (value>=0 and value<float("inf")):
                    raise ValueError(f"lluvia inválida, línea {idx}")
                counts.setdefault(sector,[]).append(month)
            if not counts: raise ValueError("sin filas")
            summary={}
            for sector,dates in counts.items():
                duplicated=len(dates)!=len(set(dates))
                missing=sorted(EXPECTED-set(dates))
                extras=sorted(set(dates)-EXPECTED)
                summary[sector]={"meses":len(dates),"duplicados":duplicated,"faltantes":len(missing),
                                 "primeros_faltantes":missing[:5],"extras":extras[:5]}
            item["sectores"]=summary
            item["valido"]=all(v["meses"]==360 and not v["duplicados"] and
                               v["faltantes"]==0 and not v["extras"] for v in summary.values())
            item["causa"]="completo_en_formato" if item["valido"] else "cobertura_incompleta"
    except (OSError,ValueError,UnicodeError) as e:
        item["causa"]="error_lectura_validacion"
        item["detalle"]=str(e)
    return item

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in ROOT.rglob("*.csv") if
                 ".git" not in p.parts and "resultados" not in p.parts and
                 any(s in p.name.lower() for s in CANDIDATE_PATTERNS))
    inventory=[analyze(p) for p in files]
    valid=[r for r in inventory if r["valido"]]
    geo=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".geojson",".gpkg",".shp",".parquet"}
        and any(s in p.name.lower() for s in CANDIDATE_PATTERNS))
    status={"fase":"9V","generado_utc":datetime.now(timezone.utc).isoformat(),
       "estado":"CANDIDATOS_COMPLETOS_AUN_NO_VERIFICADOS" if valid else "BLOQUEADO_SIN_MATRIZ_SECTORIAL",
       "archivos_revisados":inventory,"candidatos_formato_completo":[r["archivo"] for r in valid],
       "geometrias_candidatas":geo,"habilitado_entrenamiento":False,
       "razon":"Requiere proveniencia CHIRPS, polígono y verificación de fecha de publicación antes de entrenar",
       "advertencia":"La integridad tabular NO equivale a validación de fuente ni habilidad predictiva."}
    (OUT/"auditoria_insumos.json").write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding="utf-8")
    with (OUT/"inventario.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["archivo","sha256","bytes","valido","causa"])
        writer.writeheader()
        for item in inventory:writer.writerow({k:item.get(k,"") for k in writer.fieldnames})
    print(json.dumps({"estado":status["estado"],"candidatos":len(files),
                       "completos_formato":len(valid),"geometrias":len(geo)},ensure_ascii=False))
    return 0

if __name__=="__main__":sys.exit(main())
