# Auditoría integral OAF-Lambayeque · 21 de octubre de 2026

## Alcance y límites

Revisión estructural del portal `index.html` (6 secciones principales y 77 referencias a scripts de visualización) y examen de los módulos de Cultivos y Sanidad, Boletines, vigilancia externa, metadatos y flujos reproducibles. **No equivale a una certificación exhaustiva de cada valor de todos los CSV/JSON históricos**, una auditoría instrumental presencial ni verificación HTTP individual de todas las fotografías remotas. La calidad o actualidad de un proveedor externo no garantiza automáticamente la validez de los modelos locales.

## Comprobaciones documentales

| Elemento | Estado constatado | Límite / acción |
|---|---|---|
| Open-Meteo (semanal, 4 localidades) | El navegador consulta la API al abrir los módulos y al cambiar localidad; presenta 7 días | Pronóstico externo, no modelo OAF entrenado; depende de disponibilidad del proveedor y recarga |
| CHIRPS 3Z | Existe script semanal de descarga, SHA y control de raster; estado archivado hasta septiembre 2026 | Estimación satélite/pluviómetro, no medición de estación; el cron no garantiza nueva edición |
| NOAA NCEI ERSSTv5 6D | Workflow programado días 12 y 19 de cada mes, conserva rebase 1991-2020 | Serie de anomalía oceánica; no predicción de lluvia para parcelas |
| ENFEN 3Z | Monitor anterior tenía URL `/downloads/comunicados/` y consulta archivada fallida | Se corrigió a `/comunicados/`; verificar primera ejecución y lectura de PDFs |
| ENFEN, NOAA CPC, SENAMHI, CENEPRED | Nuevo monitor diario 13:27 UTC y bitácora JSON `estado_fuentes_oficiales_auto.json` | Se distingue web accesible de fecha/aviso realmente verificados; cambios de HTML requieren lectura humana |
| Comunicados y resúmenes del Niño | Cinco documentos en catálogo; cronología de 4 comunicados ENFEN, último N.° 18 (16/10/2026) | El resumen interpretativo es editorial y NO se reescribe automáticamente al cambiar un boletín |
| Modelo Random Forest 10J | Workflow mensual de **candidato** condicionado a incorporar nuevos meses CHIRPS completos | `modelo_desplegado_automaticamente=False`; no hay promoción ni alertas operativas automáticas |
| Modelo 10N estaciones de montaña | Publica una prueba y comparador histórico | En prueba 2026 no mejoró a climatología; no se presenta como pronóstico operativo |
| RF/GCN/CNN otras fases | Existen archivos, experimentos, pruebas por cambios y visores reproducibles | La existencia del workflow no implica reentrenamiento periódico ni precisión prospectiva validada |
| SENAMHI terrestre | La integración 10M y 10N conserva CSV aportados, meses completos y auditoría | Sin flujo abierto continuo confirmado; algunas fuentes carecen de QC instrumental |
| Sanidad | 6 cultivos, 23 problemas y **31 fichas** de productos/agentes en 16 problemas | Cada combinación cultivo–organismo–formulación requiere contrastarse con SIGIA/SENASA; no se publican dosis |
| Fotografía | 23 referencias por organismo y 12 envases referenciales | Se repararon referencias de oídio y picudo, se añadió Score y retiró un logotipo erróneo de Engeo; otras URL externas pueden caducar o bloquearse |
| Visualización | Niño 1+2 con 12/24/36 meses, barras seleccionables, e indicadores de vigencia | Gráfico histórico, no escala de riesgo ni predicción local |

## Matriz de acción y trazabilidad

- **Acceso a fuentes oficiales**: `datos/estado_fuentes_oficiales_auto.json`, `scripts/actualizar_fuentes_oaf_2026.py`, `.github/workflows/oaf_fuentes_oficiales_2026.yml`. La bitácora inicial se publicó como **pendiente de primera ejecución**; el cron constituye programación, no certificación de éxito.
- **Estados y limitaciones del reentrenamiento**: `.github/workflows/oaf_10j_automejora.yml`, `.github/workflows/oaf_10c_reentrenamiento.yml`, `.github/workflows/oaf_ncei_ersstv5_fase6d.yml`, `datos/estado_monitoreo_3z.json` y documentos científicos de cada fase.
- **Manejo sanitario**: `datos/sanidad_agroexportadora_2026.json`; fuentes de fabricantes identificadas, modo celular FRAC/IRAC, nota antiresistencia y obligatoriedad de etiqueta y verificación del estado regulatorio ante SENASA.
- **Imágenes**: `datos/galeria_sanidad_2026.json` y `assets/oaf-galeria-mecanismos-2026.js`. Se mantiene atribución y se muestra un recuadro explicativo si falla una imagen.
- **Navegación**: se conservaron 6 pestañas y los módulos de metadatos; Cultivos y Sanidad y Boletines conservan dos bloques principales.


## Primera ejecución real del monitor diario

La bitácora pública `datos/estado_fuentes_oficiales_auto.json` registró una primera comprobación el **21/10/2026 a las 19:35:24 UTC**. Resultado observado: **NOAA CPC HTTP 200**, **CENEPRED HTTP 200**, **ENFEN error de resolución DNS**, y **SENAMHI tiempo de conexión agotado**. HTTP 200 solo acredita acceso a la página, no novedad ni fecha de un pronóstico. La automatización queda operativa como **monitor de intentos**, no como garantía de consultas exitosas.

Para ENFEN se conserva el vínculo oficial al archivo de comunicados; para SENAMHI se añade un enlace alternativo al compendio estatal DZ2. Si el servidor institucional falla, el panel muestra incidencia y no presenta nuevas afirmaciones de actualidad.

## Pendientes que no deben ocultarse

1. Confirmar una **ejecución exitosa real** del nuevo workflow y los anteriores; una programación GitHub Actions podría fallar por DNS, cambios de HTML, cuotas o permisos.
2. Validar el día de emisión y texto íntegro de todo nuevo comunicado ENFEN; revisar interpretación editorial por profesional antes de sustituir la síntesis antigua.
3. Obtener flujos SENAMHI instrumentales controlados y mediciones biológicas locales para validación independiente de modelos.
4. No promover automáticamente un candidato RF a alertas de campo sin comparaciones prospectivas, calibración y revisión responsable.
5. Auditar periodicidad, integridad y fechas de los CSV/JSON archivados de todas las fases, con pruebas de origen, licencia y exactitud.
6. Verificar uno a uno accesibilidad, licencia y taxonomía de todas las fotografías externas desde un navegador real, y reemplazar las que cambien de ruta.
7. Confirmar en **SIGIA** registro y etiqueta vigentes de cada producto comercial antes de presentarlo como tratamiento autorizado; fabricante o vendedor no bastan para acreditar habilitación.

## Fuentes públicas principales

- ENFEN comunicados: https://enfen.imarpe.gob.pe/comunicados/
- NOAA CPC ENSO: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc_Sp.shtml
- SENAMHI: https://www.senamhi.gob.pe/
- CENEPRED SIGRID: https://sigrid.cenepred.gob.pe/sigridv3/
- SENASA SIGIA: https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_cultivo.html
- CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3
- Open-Meteo: https://open-meteo.com/

**Política científica:** la automatización transporta y comprueba datos, no crea evidencia de presencia de plagas ni valida automáticamente un modelo. Estado de las fuentes e informes técnicos separados de productos experimentales.
