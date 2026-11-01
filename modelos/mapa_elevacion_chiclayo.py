#!/usr/bin/env python3
"""Mapa exploratorio de elevaciones Copernicus GLO-90 para Las Brisas, Chiclayo.

Produce un PNG de divulgación y un JSON de resultados. Es un DSM (superficie),
NO un DTM bare-earth de precisión urbana ni un mapa de inundación.
"""
from pathlib import Path
from datetime import date
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle
from matplotlib import patheffects
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

RASTER = Path("datos/relieve_9l/fuentes/copernicus_glo90_s07_w080.tif")
EXPECTED_SHA = "c4d78e481f80927d72886787e422ed02214ffb0d5739e67a25facd2c874f7532"
OUT = Path("datos/dem_chiclayo_las_brisas")
OUT.mkdir(parents=True, exist_ok=True)

# Reconstrucción geográfica de código corto 64CP+476, relativo a Chiclayo.
LAT, LON = -6.7797125, -79.864359375
WEST, EAST = LON - 0.024, LON + 0.024
SOUTH, NORTH = LAT - 0.021, LAT + 0.021

assert RASTER.exists(), "No se encuentra la fuente Copernicus auditada."
sha = hashlib.sha256(RASTER.read_bytes()).hexdigest()
assert sha == EXPECTED_SHA, "La huella del TIFF no coincide con el original documentado en 9L."

with rasterio.open(RASTER) as src:
    assert src.crs.to_epsg() == 4326, f"CRS inesperado: {src.crs}"
    window = from_bounds(WEST, SOUTH, EAST, NORTH, src.transform)
    window = window.round_offsets().round_lengths()
    data = src.read(1, window=window, masked=True).astype(np.float64)
    b = rasterio.windows.bounds(window, src.transform)
    transform = src.window_transform(window)
    center_row, center_col = rasterio.transform.rowcol(transform, LON, LAT)
    nodata = int(np.ma.count_masked(data))
    a = data.filled(np.nan)
    a[(a < -50) | (a > 1000)] = np.nan
    assert np.isfinite(a).sum() > 100, "DEM incompleto."
    valid = a[np.isfinite(a)]
    q1, q2 = np.quantile(valid, [1/3, 2/3])
    zcenter = float(a[center_row, center_col]) if 0 <= center_row < a.shape[0] and 0 <= center_col < a.shape[1] else None
    classes = np.digitize(a, [q1,q2]).astype(float)
    classes[~np.isfinite(a)] = np.nan

meta = {
    "titulo":"Elevaciones relativas del modelo Copernicus alrededor de Las Brisas, Chiclayo",
    "tipo":"MODELO DIGITAL DE SUPERFICIE (DSM), no DTM bare-earth",
    "fuente":"Copernicus DEM GLO-90 2021; archivo original auditado en OAF 9L",
    "doi":"10.5270/ESA-c5d3d65",
    "sha256_original": sha,
    "codigo_plus_corto":"64CP+476 Chiclayo",
    "ubicacion_reconstruida_lat": LAT,
    "ubicacion_reconstruida_lon": LON,
    "bbox_wgs84":{"west":b[0],"south":b[1],"east":b[2],"north":b[3]},
    "dimension_celdas":[int(data.shape[0]),int(data.shape[1])],
    "n_celdas_validas":int(valid.size),
    "celdas_sin_dato": nodata,
    "min_m":round(float(valid.min()),2),
    "p33_m":round(float(q1),2),
    "p67_m":round(float(q2),2),
    "max_m":round(float(valid.max()),2),
    "ubicacion_celda_m": round(zcenter,2) if zcenter is not None else None,
    "zonas":{
        "rojo":"tercio inferior de altitud en ventana cartográfica",
        "amarillo":"tercio intermedio de altitud",
        "verde":"tercio superior de altitud, NO significa ausencia de riesgo"
    },
    "advertencia":"Los colores son alturas relativas del DSM ~90m, no depresiones medidas ni riesgo hidráulico. Requiere DTM <=1-2m y validación de drenaje."
}
(OUT/"metadatos_elevacion.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n","utf8")

# Celdas reales comprimidas para permitir auditoría/reproducción fuera de GitHub.
import base64, zlib
elev_float = np.where(np.isfinite(a),a,-32768).astype("<f4")
payload = base64.b64encode(zlib.compress(elev_float.tobytes(),9)).decode("ascii")
(OUT/"payload_dem_b64.txt").write_text(payload+"\n","utf8")

# Semáforo de tres clases sin elevar precisión; formato compacto para cartel local.
class_chars = "".join(str(int(v)) for v in classes.reshape(-1))
(OUT/"semaforo_clases_b64.txt").write_text(
    base64.b64encode(zlib.compress(class_chars.encode("ascii"),9)).decode("ascii")+"\n",
    "utf8"
)



plt.rcParams["font.family"] = "DejaVu Sans"
fig=plt.figure(figsize=(9,11.25),dpi=160,facecolor="#eff6fb")
fig.text(.07,.963,"OAF  Lambayeque",fontsize=29,weight="bold",color="#073b60")
fig.text(.072,.934,"Observatorio Agroclimático y Fitosanitario",fontsize=11.8,color="#166a70")
fig.text(.07,.897,"ELEVACIÓN DEL TERRENO · CHICLAYO",fontsize=18.7,weight="bold",color="#0b2942")
fig.text(.07,.871,"Entorno Las Brisas / 9 de Octubre  ·  Código Plus: 64CP+476",fontsize=10.5,color="#27475d")
ax=fig.add_axes([.075,.295,.85,.535])
cmap=ListedColormap(["#e24038","#ffd24a","#36a879"])
cmap.set_bad("#e1e7ef")
ax.imshow(classes,cmap=cmap,vmin=-.5,vmax=2.5,origin="upper",extent=b,interpolation="nearest",alpha=.96,aspect="auto")
# Contornos suavizados solo como guía visual y sin marcadores de depresiones locales.
try:
    from scipy.ndimage import gaussian_filter
    v=np.nanmedian(a)
    smooth=gaussian_filter(np.where(np.isfinite(a),a,v),sigma=1.0)
    xx=np.linspace(b[0],b[2],a.shape[1])
    yy=np.linspace(b[3],b[1],a.shape[0])
    lo=np.floor(np.nanmin(smooth)/2)*2
    hi=np.ceil(np.nanmax(smooth)/2)*2
    if hi-lo>2:
        levels=np.arange(lo+2,hi,2)
        if len(levels)>15: levels=np.linspace(lo,hi,12)
        cs=ax.contour(xx,yy,smooth,levels=levels,colors="#1b3e50",linewidths=.42,alpha=.55)
        ax.clabel(cs,fontsize=6,fmt="%.0f m",inline=1)
except ImportError:
    pass
ax.scatter([LON],[LAT],s=390,c="white",edgecolor="#0849c1",linewidth=3,zorder=5)
ax.scatter([LON],[LAT],s=125,c="#166cff",edgecolor="white",linewidth=1,zorder=6)
ax.annotate("Punto de referencia\n64CP+476",xy=(LON,LAT),xytext=(LON+0.0028,LAT+0.0038),
    fontsize=10,weight="bold",color="#062c53",
    bbox=dict(boxstyle="round,pad=.5",fc="white",ec="#0c76bf",alpha=.93),
    arrowprops=dict(arrowstyle="->",color="#0b62a6",lw=2),zorder=8)
ax.grid(alpha=.19,color="white",linewidth=1)
ax.tick_params(axis="both",labelsize=7,colors="#2b4351")
ax.set_xlabel("Longitud (° O) · WGS84",fontsize=9,color="#203f52")
ax.set_ylabel("Latitud (° S) · WGS84",fontsize=9,color="#203f52")
ax.set_xlim(WEST,EAST)
ax.set_ylim(SOUTH,NORTH)
ax.text(.982,.98,"N ↑",transform=ax.transAxes,ha="right",va="top",fontsize=14,weight="bold",color="#0b2942",
    bbox=dict(boxstyle="round,pad=.25",fc="white",ec="none",alpha=.8))
for spine in ax.spines.values():spine.set_edgecolor("#6e95ab")
fig.text(.076,.836,f"Fuente: Copernicus GLO-90 (≈90 m) · DSM con edificios/vegetación · {data.shape[0]} × {data.shape[1]} celdas",fontsize=8.6,color="#4c6272")
fig.text(.077,.256,"SEMÁFORO DE ELEVACIÓN RELATIVA",fontsize=12,weight="bold",color="#0b2942")
legend_y=.232
for x,color,label in [(0.08,"#e24038",f"ROJO  < {q1:.1f} m"),(.39,"#ffd24a",f"AMARILLO  {q1:.1f}–{q2:.1f} m"),(.73,"#36a879",f"VERDE  > {q2:.1f} m")]:
    fig.patches.append(Rectangle((x,legend_y-.006),.025,.018,transform=fig.transFigure,
                                 facecolor=color,edgecolor="#71828a",linewidth=.5))
    fig.text(x+.032,legend_y,label,fontsize=9.3,color="#183e51",va="center",weight="bold")
fig.text(.077,.188,f"Rango observado dentro del recorte: {valid.min():.1f}–{valid.max():.1f} m · Punto azul: {zcenter:.1f} m",fontsize=10,color="#23425a")
fig.text(.077,.151,"ATENCIÓN: Rojo = menor ALTURA relativa, no necesariamente zona inundable.",fontsize=10.2,
    color="#913622",weight="bold")
fig.text(.077,.122,"Verde = cota mayor en este recorte, pero NO asegura protección ante anegamientos.",fontsize=9.4,color="#294a60")
fig.text(.077,.089,"Para identificar pozas por calle se requiere DTM urbano de 1–2 m, drenaje y control de campo.",fontsize=9,color="#294a60")
fig.text(.077,.052,"Mapa de reconocimiento topográfico · No sustituye estudios hidráulicos ni alertas oficiales.",fontsize=9,color="#35617a",style="italic")
fig.text(.077,.025,"Fuente técnica: Copernicus DEM / ESA–Airbus · Datos OAF 9L · 31 oct 2026",fontsize=8.6,color="#41687d")
png=OUT/"mapa_elevacion_relativa_chiclayo_whatsapp.png"
fig.savefig(png,dpi=160,facecolor=fig.get_facecolor())
plt.close(fig)
print(json.dumps({"png":str(png),"metadata":str(OUT/"metadatos_elevacion.json"),"meta":meta},ensure_ascii=False))
