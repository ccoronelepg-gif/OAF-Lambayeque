"""OAF-Lambayeque | Fase 3U: ingesta LOCAL de archivos TXT diarios SENAMHI.

No descarga datos ni certifica identidad instrumental. No publica datos en GitHub.
Formato de seis columnas: año,mes,día,precipitación,Tmáx,Tmín.
El ejemplo es el formato de la página oficial SENAMHI; comprobar ficha y unidades.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

START_YEAR, END_YEAR = 2016, 2025
MISSING = {"", "NA", "NAN", "NULL", "S/D", "-99.9"}
STATIONS = {
    "Jayanca (La Viña)", "Cayaltí", "Reque", "Lambayeque", "Cueva Blanca"
}

def read_csv_senamhi(path: Path):
    """Devuelve (date -> float|None, informe) y rechaza duplicados/fechas inválidas."""
    binary = path.read_bytes()
    digest = hashlib.sha256(binary).hexdigest()
    decoded = None
    encoding = None
    for codec in ("utf-8-sig", "cp1252"):
        try:
            decoded = binary.decode(codec)
            encoding = codec
            break
        except UnicodeDecodeError:
            continue
    if decoded is None:
        raise ValueError("Codificación TXT no reconocida")
    separator = ";" if decoded.splitlines()[0].count(";") >= 5 else ","
    reader = csv.reader(decoded.splitlines(), delimiter=separator)
    seen = {}
    invalid_values = Counter()
    outside = 0
    skipped_header = 0
    for lineno, parts in enumerate(reader, 1):
        if not parts or all(not x.strip() for x in parts):
            continue
        cells = [x.strip() for x in parts]
        if len(cells) != 6:
            raise ValueError(f"Línea {lineno}: se esperaban 6 columnas; hay {len(cells)}")
        if lineno == 1 and (re.search(r"a[ñn]o|year|precip|mes", " ".join(cells[:4]), re.I)):
            skipped_header += 1
            continue
        try:
            y, m, d = (int(x) for x in cells[:3])
            day = date(y, m, d)
        except (ValueError, TypeError) as err:
            raise ValueError(f"Línea {lineno}: fecha inválida o formato desconocido") from err
        if not START_YEAR <= y <= END_YEAR:
            outside += 1
            continue
        if day in seen:
            raise ValueError(f"Fecha duplicada: {day.isoformat()} (línea {lineno})")
        original = cells[3].replace(" ", "")
        if original.upper() in MISSING:
            rain = None
            invalid_values["codigo_ausente"] += 1
        else:
            try:
                rain = float(original)
            except ValueError:
                rain = None
                invalid_values["no_numerico"] += 1
            else:
                if not math.isfinite(rain):
                    rain = None
                    invalid_values["no_finito"] += 1
                elif rain < 0:
                    rain = None
                    invalid_values["negativo_no_sentinel"] += 1
                elif rain > 500:
                    invalid_values["extremo_superior_500_mm_dia_revisar"] += 1
        seen[day] = rain
    if not seen:
        raise ValueError("El archivo no contiene fechas 2016–2025: no hay observaciones nuevas")
    info = {
        "sha256_original": digest,
        "formato_decodificado": encoding,
        "filas_registros_periodo": len(seen),
        "filas_fuera_de_periodo": outside,
        "cabeceras_omitidas": skipped_header,
        "incidencias_valor": dict(invalid_values),
        "primera_fecha": min(seen).isoformat(),
        "ultima_fecha": max(seen).isoformat(),
    }
    return seen, info

def compile_monthly(records: dict[date, float | None]):
    result = []
    for y in range(START_YEAR, END_YEAR + 1):
        for m in range(1, 13):
            total_days = calendar.monthrange(y, m)[1]
            values = [records.get(date(y, m, d)) for d in range(1, total_days + 1)]
            present = sum(date(y, m, d) in records for d in range(1, total_days + 1))
            valid = sum(v is not None for v in values)
            complete = valid == total_days
            result.append({
                "mes": f"{y}-{m:02d}",
                "observado_mm": round(sum(values), 3) if complete else "",
                "dias_mes": total_days,
                "dias_archivo": present,
                "dias_validos": valid,
                "dias_faltantes_o_invalidos": total_days - valid,
                "estado": "completo" if complete else "incompleto",
            })
    return result

def metadata_status(metadata: Path | None):
    if metadata is None:
        return {"codigo_instrumental": "pendiente", "ficha_oficial": "pendiente",
                "identidad_historica": "no_certificada", "licencia_publicacion": "no_verificada"}
    values = json.loads(metadata.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise ValueError("Metadatos deben ser un objeto JSON")
    allowed = {"codigo_instrumental", "ficha_oficial", "identidad_historica", "licencia_publicacion"}
    if set(values) - allowed:
        raise ValueError("Campos de metadatos desconocidos: " + repr(sorted(set(values)-allowed)))
    return {name: values.get(name, "pendiente") for name in allowed}

def ingest(input_path: Path, station: str, output_dir: Path, metadata: Path | None = None):
    if station not in STATIONS:
        raise ValueError("Nombre de estación no reconocido. Debe coincidir con el catálogo del OAF")
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    rows, info = read_csv_senamhi(input_path)
    month = compile_monthly(rows)
    complete = sum(x["estado"] == "completo" for x in month)
    summary = {
        "fase": "3U", "estacion_declarada": station,
        "periodo_solicitado": "2016-01 a 2025-12", "meses_en_ventana": 120,
        "meses_completos": complete, "meses_incompletos": 120-complete,
        "dias_validos": sum(x["dias_validos"] for x in month),
        "metadatos_declarados_no_certificados_automaticamente": metadata_status(metadata),
        "verificacion_independencia_productos": "pendiente",
        "apto_para_validacion_externa": False,
        "publicacion_automatica": False,
        **info,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = {"Jayanca (La Viña)":"jayanca","Cayaltí":"cayalti","Reque":"reque",
            "Lambayeque":"lambayeque","Cueva Blanca":"cueva_blanca"}[station]
    out_csv = output_dir / f"{slug}_mensual_3u.csv"
    out_json = output_dir / f"{slug}_auditoria_3u.json"
    with out_csv.open("w", newline="", encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(month[0]))
        writer.writeheader()
        writer.writerows(month)
    out_json.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary

def main():
    p=argparse.ArgumentParser(description="Importar TXT diario SENAMHI 2016–2025 LOCALMENTE sin publicar datos")
    p.add_argument("--archivo",type=Path,required=True,help="Archivo diario TXT recibido por el investigador")
    p.add_argument("--estacion",required=True,choices=sorted(STATIONS))
    p.add_argument("--metadatos",type=Path,help="JSON opcional con código, ficha y licencias")
    p.add_argument("--salida",type=Path,default=Path("datos/_privados/3u"))
    args=p.parse_args()
    summary=ingest(args.archivo,args.estacion,args.salida,args.metadatos)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Archivos guardados SOLO localmente en:",args.salida)
    if summary["meses_completos"]==0:
        print("AVISO: cero meses completos, ninguna validación posible.")

if __name__=="__main__":
    main()
