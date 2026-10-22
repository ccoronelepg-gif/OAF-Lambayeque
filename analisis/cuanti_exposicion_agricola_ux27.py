#!/usr/bin/env python3
"""UX27: intersección vectorial reproducible de agricultura y susceptibilidad.
Uso: python analisis/cuanti_exposicion_agricola_ux27.py --agricultura ... --peligro ... \
        --clase n_peligro --departamento NOMBDEP --provincia NOMBPROV --distrito NOMBDIST \
        --salida resultados/ux27_exposicion.csv

Requisitos: geopandas>=1.0, shapely>=2.0, pandas>=2.0.
IMPORTANTE: usar capas VECTORIALES verificadas; una captura o un raster coloreado
del visor ArcGIS no contiene clases geográficas suficientes para esta operación.
"""
import argparse
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

METRIC_CRS = "EPSG:32717"  # UTM 17S, adecuado al ámbito de Lambayeque
LEVELS = ("muy alto", "alto", "medio", "bajo")


def norm(value):
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def level(value):
    s = norm(value)
    if "muy alto" in s or "muy alta" in s:
        return "muy alto"
    for k in ("alto", "alta", "medio", "media", "bajo", "baja"):
        if k in s:
            return {"alta": "alto", "media": "medio", "baja": "bajo"}.get(k, k)
    return None


def load_polygons(path, description):
    result = gpd.read_file(path)
    if result.empty:
        raise ValueError(f"{description}: el archivo está vacío")
    if result.crs is None:
        raise ValueError(f"{description}: el archivo carece de CRS")
    result = result[result.geometry.notna() & ~result.geometry.is_empty].copy()
    if not result.geom_type.isin(("Polygon", "MultiPolygon")).all():
        raise ValueError(f"{description}: solo se admiten polígonos reales")
    result.geometry = result.geometry.make_valid()
    result = result.to_crs(METRIC_CRS)
    if result.empty:
        raise ValueError(f"{description}: sin geometrías válidas")
    return result


def union(series):
    return series.union_all()


def measure(agricultura, peligro, clase, dept, prov, dist):
    if clase not in peligro:
        raise ValueError(f"No existe campo {clase!r} en la capa de peligros")
    if dept:
        if dept not in agricultura:
            raise ValueError(f"Campo de departamento {dept!r} no presente en agricultura")
        agricultura = agricultura[agricultura[dept].map(norm) == "lambayeque"].copy()
        if agricultura.empty:
            raise ValueError("No hay polígonos agrícolas etiquetados LAMBAYEQUE")
    fields = [f for f in (prov, dist) if f]
    for field in fields:
        if field not in agricultura:
            raise ValueError(f"Campo {field!r} ausente de la capa agrícola")
    peligro["_nivel"] = peligro[clase].map(level)
    if peligro["_nivel"].isna().any():
        classes = list(map(str, peligro.loc[peligro["_nivel"].isna(), clase].unique()[:10]))
        raise ValueError("Existen clases de peligro desconocidas: " + ", ".join(classes))
    # Disolver cada nivel y retirar geometría ya cubierta por un nivel mayor
    # para evitar contabilizar dos veces una misma área por solapamiento.
    disjoint = {}
    higher = None
    for category in LEVELS:
        subset = peligro.loc[peligro["_nivel"] == category, "geometry"]
        if subset.empty:
            continue
        geom = union(subset)
        if higher is not None:
            geom = geom.difference(higher)
        if not geom.is_empty:
            disjoint[category] = geom
            higher = geom if higher is None else higher.union(geom)
    if not disjoint:
        raise ValueError("Ninguna clase territorial reconocida")
    if not fields:
        groups = [(("Lambayeque",), agricultura)]
        output_fields = ["ambito"]
    else:
        output_fields = fields
        groups = agricultura.groupby(fields, dropna=False)
    records = []
    for raw_key, group in groups:
        key = raw_key if isinstance(raw_key, tuple) else (raw_key,)
        agri_geom = union(group.geometry)
        total_ha = agri_geom.area / 10000
        row = dict(zip(output_fields, map(str, key)))
        row["agricola_cartografiada_ha"] = round(total_ha, 3)
        for cat in LEVELS:
            mask = disjoint.get(cat)
            name = cat.replace(" ", "_") + "_ha"
            row[name] = round(agri_geom.intersection(mask).area / 10000, 3) if mask is not None else 0.0
        affected = sum(row[k.replace(" ", "_") + "_ha"] for k in LEVELS)
        if affected > total_ha * 1.001 + 0.002:
            raise RuntimeError("Intersección inconsistente: superposición de clases no resuelta")
        row["sin_clasificacion_ha"] = round(max(0, total_ha - affected), 3)
        row["mayor_susceptibilidad_pct_de_area"] = (
            round(100 * (row["muy_alto_ha"] + row["alto_ha"]) / total_ha, 2)
            if total_ha > 0 else None
        )
        records.append(row)
    return pd.DataFrame(records).sort_values(output_fields)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agricultura", required=True, help="Polígonos agrícolas oficiales, SHP/GPKG/GeoJSON")
    p.add_argument("--peligro", required=True, help="Polígonos oficiales de susceptibilidad, no imágenes")
    p.add_argument("--clase", required=True, help="Campo que contiene Muy Alto/Alto/Medio/Bajo")
    p.add_argument("--departamento", default="NOMBDEP", help="Campo de nombre del departamento en agricultura; vacío para omitir")
    p.add_argument("--provincia", default="NOMBPROV", help="Campo de provincia; vacío para total regional")
    p.add_argument("--distrito", default="NOMBDIST", help="Campo de distrito; vacío para total provincial")
    p.add_argument("--salida", required=True, help="Ruta del CSV de salida")
    args = p.parse_args()
    ag = load_polygons(args.agricultura, "agricultura")
    hz = load_polygons(args.peligro, "peligro")
    result = measure(ag, hz, args.clase, args.departamento or None,
                     args.provincia or None, args.distrito or None)
    dest = Path(args.salida)
    dest.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(dest, index=False, encoding="utf-8-sig")
    print(f"Resultados SIG guardados en {dest} ({len(result)} ámbitos).")
    print("Verifica escala y fecha de fuentes antes de publicar estas hectáreas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
