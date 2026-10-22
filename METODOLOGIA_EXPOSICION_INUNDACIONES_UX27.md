# OAF-Lambayeque · UX27 — inundaciones y cuantificación de exposición agrícola

**Fecha de integración:** 22 de octubre de 2026.  
**Alcance:** Análisis de la región → Territorio y riesgos climáticos.  
**Estado:** visor regional y reproducción de indicadores publicados. La intersección espacial por provincia/distrito está implementada como procedimiento SIG reproducible, pero **NO se ha ejecutado sobre ambas capas completas y verificadas** debido a que no se ha podido descargar el raster de clases originales (solo su representación web). Por tanto, el portal no debe mostrar hectáreas sintéticas por filtro.

## 1. Capa para cubrir Lambayeque

- **CENEPRED / SIGRID / MapServer S05CP / ID 5090024**: *Susceptibilidad a inundaciones por lluvias fuertes*. Cobertura cartográfica nacional, aplicable a la región Lambayeque por recorte geográfico. Cuatro clases: muy alto, alto, medio y bajo. **Referencia temática: CENEPRED, 2021**.
- **INGEMMET / SIGRID / MapServer S05CP / ID 5010502**: *Susceptibilidad regional a inundaciones*, compilación cartográfica por región.
- **CENEPRED / SIGRID / MapServer S05CP / ID 5090023**: susceptibilidad ante lluvias vinculadas a eventos El Niño, disponible en el selector existente.

Metadatos oficiales:

https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024  
https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5010502  
https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090023  
https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend

**Interpretación:** la susceptibilidad clasifica predisposición física, no probabilidad calibrada de ocurrencia ni hectáreas que necesariamente se inundarán en un evento futuro.

## 2. Cuantificación oficial implementada en el portal

Fuente: **CENEPRED, Escenarios de riesgo por inundaciones y movimientos en masa en el marco del Plan Multisectorial ante lluvias intensas y peligros asociados 2025–2027**, cuadro de nivel de riesgo *Muy alto*, publicado en el reporte semanal de **5 al 11 de enero de 2026**, página impresa 4 (índice PDF 3).

| Indicador | Valor | Universo |
|---|---:|---|
| Distritos clasificados en escenario de riesgo muy alto por inundaciones | **9** | Subconjunto de Lambayeque |
| Superficie agrícola considerada en el escenario | **1 380 ha** | 9 distritos |
| Superficie agrícola ubicada en zonas de mayor susceptibilidad | **1 234 ha** | 9 distritos |
| Relación mayor susceptibilidad/superficie considerada | **89,4203 %** (redondeado 89,4 %) | 1 234 / 1 380 |
| Diferencia aritmética, sin equivalencia con riesgo nulo | **146 ha** | 1 380 − 1 234 |
| Viviendas en zona de mayor susceptibilidad | **50 299** | 9 distritos |
| Vías de mayor susceptibilidad | **374 km** | 9 distritos |

La clase *riesgo muy alto* se aplica a los distritos incluidos en el escenario; el dato de **superficie de mayor susceptibilidad** es el subgrupo de hectáreas agrícolas según el cuadro oficial. No se afirma que 1 234 ha correspondan a todo Lambayeque o a un inventario anual de hectáreas afectadas.

Fuente principal:
https://sigrid.cenepred.gob.pe/sigridv3/documento/17791

Reporte con la tabla reproducida:
https://sigrid.cenepred.gob.pe/sigridv3/storage/reporte_semanal/REPORTE_SEMANAL_202601_2.pdf

Capas y formatos adicionales para el análisis:
https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_climatico_llu/10_shape.zip

Este ZIP corresponde al escenario del Plan Multisectorial, que puede expresar **riesgo**, y no necesariamente los mismos polígonos/códigos del raster de **susceptibilidad** 5090024. Debe inspeccionarse su contenido, CRS, clases, año y procedencia antes de usarlo para intersección.

Archivos de datos abiertos de los indicadores publicados: `datos/riesgos_ux27/indicadores_cenepred_2025.csv` y `datos/riesgos_ux27/indicadores_cenepred_2025.json`. Los valores calculados (porcentaje y diferencia aritmética) se distinguen explícitamente de los datos oficiales originales.

## 3. Capa de exposición agrícola

**MINAM, ServicioGeoINEA / MapServer / capa 1, Superficie Agrícola Nacional**.

https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer/1

El servicio indica tipo **Feature Layer**, geometría **polígono**, referencias administrativas `IDDPTO`, `NOMBDEP`, `IDPROV`, `NOMBPROV`, `IDDIST`, `NOMBDIST` y campos `AG_2018`/`FECHA_ACT`. El atributo AG_2018 requiere validación de unidades, definición y duplicación de polígonos; no se le asigna una unidad por inferencia.

El informe oficial de 2025 y los polígonos agrícolas con referencia 2018 son **productos de fechas y metodologías diferentes**. Su superposición posterior constituye un análisis nuevo, no la reproducción directa del indicador del CENEPRED.

## 4. Procedimiento SIG reproducible

Archivo: `analisis/cuanti_exposicion_agricola_ux27.py` (Python 3, GeoPandas 1+, Shapely 2+, Pandas 2+). Requiere descargar **archivos vectoriales originales**, no imágenes exportadas por MapServer.

Ejemplo para una geocapa de susceptibilidad convertida oficialmente a polígonos con clases descriptivas:

```bash
python analisis/cuanti_exposicion_agricola_ux27.py \
  --agricultura insumos/superficie_agricola_minam.gpkg \
  --peligro insumos/susceptibilidad_inundacion_cenepred.gpkg \
  --clase n_peligro \
  --departamento NOMBDEP \
  --provincia NOMBPROV \
  --distrito NOMBDIST \
  --salida resultados/ux27_agricultura_susceptibilidad.csv
```

El procedimiento realiza: identificación explícita de clases, reproyección de las geometrías al CRS métrico EPSG:32717, validación topológica, unión de polígonos agrícolas por ámbito para evitar doble conteo, jerarquización de niveles de susceptibilidad cuando se solapen polígonos, intersección vectorial, suma de área real en m² / 10 000 y consolidación por provincia y distrito.

El script **detiene** la operación si faltan geometrías, CRS o clases reconocibles; no estima coordenadas ni valores faltantes.

Requisitos científicos antes de publicar hectáreas nuevas:
1. Comprobar que la capa de inundación cubra todas las áreas pertinentes del departamento y registrar áreas sin clasificación.
2. Comprobar la precisión real, escala, sistema de referencia y fecha de los mapas originales.
3. Verificar que los polígonos del MINAM sean **superficie efectivamente agrícola** y no distritos enteros simbolizados por estadística.
4. Validar solapamientos, incertidumbre, unidades, categorías y restricciones del proveedor.
5. Para cuencas: incorporar polígonos ANA completos y calcular una intersección adicional; **la versión actual del script consolida por provincia y distrito, no por cuenca**.
6. Contrastar con muestras de campo y cartografía base de calidad suficiente.
7. Distinguir hectáreas de *susceptibilidad* de hectáreas *efectivamente inundadas* y de *pérdidas económicas*.

## 5. Límites de la fase UX27

El mapa web renderiza el raster institucional mediante ArcGIS REST. Esta imagen **no es** un GeoTIFF categórico bruto; clasificar sus colores para obtener hectáreas crearía riesgo de error por simbología, transparencia, antialiasing y distinta resolución de pantalla. Por ello, la interfaz presenta exclusivamente cifras publicadas y dispone de un método SIG de cálculo que se ejecutará solo cuando existan los insumos geográficos verificables.

**Resultado UX27:** capa regional identificada y enlazada, panel cuantitativo documental, porcentaje reproducido, procedimiento SIG publicable, PWA sincronizada. Queda pendiente realizar y validar la intersección regional completa y los desgloses por ámbito geográfico.
