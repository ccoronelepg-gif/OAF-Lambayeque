# OAF-Lambayeque 2.0
### Observatorio Agroclimático y Fitosanitario de Lambayeque, Perú

**Autor:** ING. AGRÓNOMO CARLOS ENRIQUE CORONEL GARCÍA  
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/


## Actualización del portal · 14/10/2026

La página pública [OAF-Lambayeque 2.2](https://ccoronelepg-gif.github.io/OAF-Lambayeque/) incorpora:

- Biblioteca consultable para **arándano y vid**, con nueve enfermedades, variables meteorológicas, rangos publicados, nivel de respaldo y enlaces directos a estudios y guías técnicas.
- Módulo visible de **boletines ENFEN** con comunicado N.º 17-2026 (verificado al 14/10/2026), acceso a archivos institucionales y al registro de monitoreo automatizado con sus limitaciones.
- Consulta horaria experimental para **Jayanca, Motupe, Olmos y Chiclayo**, con años completos 2023–2025, usando ERA5-Land (temperatura/HR) y ERA5 (precipitación) a través de Open-Meteo, exportación CSV y tratamiento explícito de fallos y datos faltantes.
- Conservación de todas las secciones de validación, CHIRPS, SENAMHI y datos históricos existentes.

Los índices no son alertas operativas ni permiten diagnosticar enfermedades. El navegador necesita acceso a la API de terceros para obtener datos horarios.

## Interfaz pública simplificada · 14/10/2026

**Sitio:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/

La portada se reorganizó en cinco pestañas exclusivas:
1. Cultivos y condiciones de riesgo de patologías: tabla de tres columnas (enfermedad, condiciones climáticas y cultivo), con nueve patologías y fuentes.
2. Boletines de El Niño: enlaces ENFEN/SENAMHI, consulta al registro institucional y estado de verificación sin suponer alerta vigente.
3. Datos climáticos: consulta modelada de tiempo reciente y pronóstico externo a siete días para cuatro localidades, más última disponibilidad CHIRPS.
4. Riesgo de presencia de enfermedades: estado de los modelos, requisitos y advertencia de que no existen alertas OAF operativas.
5. Verificaciones de datos: resumen de calidad, cobertura histórica y enlace al portal anterior conservado en [archivo-analisis-historico.html](archivo-analisis-historico.html).

El nuevo diseño reduce información redundante; la página histórica de 2026 se mantiene íntegra. Las imágenes públicas proceden de Wikimedia Commons (Scott Bauer/USDA y Panelxf, CC0/dominio público). Las cifras de estado de fuente se cargan desde los JSON mantenidos en este repositorio. El pronóstico de Open-Meteo **no es un modelo predictivo propio del OAF**.

## Interfaz OAF actualizada · 14/10/2026

La navegación pública se ordena de izquierda a derecha en cinco secciones:

1. **Inicio:** propósito del proyecto, fuentes utilizadas, evaluación de calidad, modelos científicos y validación futura.
2. **Datos climatológicos:** meteorología modelada reciente, perspectiva a siete días de Open-Meteo, disponibilidad de precipitación CHIRPS y distinción de predicciones propias en desarrollo.
3. **Cultivos y riesgo de enfermedades:** tabla compacta de tres columnas con las nueve enfermedades de arándano y vid, bibliografía científica y resumen de modelos experimentales sin alertas operativas.
4. **Boletín de El Niño:** comunicados de ENFEN y avisos SENAMHI; el estado se publica únicamente si es verificable.
5. **Verificación de datos:** cobertura y control de calidad, archivo original íntegro en [archivo-analisis-historico.html](archivo-analisis-historico.html).

La web preserva los enlaces directos anteriores a `#cultivos` y redirige la pestaña antigua `#riesgos` a esa sección, sin duplicación de información.

## Misión

Desarrollar un sistema regional de **vigilancia agroclimática actualizada, pronóstico probabilístico y alerta temprana experimental** de eventos anómalos —en especial condiciones vinculadas con **El Niño Costero**— y de riesgos fitosanitarios agrícolas. La primera línea de sanidad vegetal se centra en **arándano**, comenzando con condiciones favorables para *Botrytis cinerea*.

**Estado actual:** la nueva arquitectura está **planificada**, no constituye aún un sistema de predicción propio validado, ni emite alertas climáticas o fitosanitarias operativas.

## Cuatro fases prioritarias

| Fase | Objetivo | Estado |
|---|---|---|
| **3Z** | Modernizar fuentes oficiales, monitoreo reciente y trazabilidad ENFEN/SENAMHI/satélites | **En progreso · CHIRPS v3 integrado** |
| **4A** | Modelos de anomalías y pronósticos probabilísticos meteorológicos | Pendiente |
| **4B** | Riesgo fitosanitario de arándano basado en condiciones y observaciones de campo | Pendiente |
| **4C** | Evaluación prospectiva, validación independiente y comunicación de alertas | Pendiente |

Plan detallado: [PLAN_MAESTRO_OAF_2_0.md](PLAN_MAESTRO_OAF_2_0.md).  
Protocolo de estados y alertas: [PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md](PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md).  
Catálogo de fuentes priorizadas: [datos/catalogo_fuentes_operativas_3z.csv](datos/catalogo_fuentes_operativas_3z.csv).  
Plan de fases legible por máquinas: [datos/plan_operativo_oaf_2_0.json](datos/plan_operativo_oaf_2_0.json).

## Fase 3Z — primera fuente reciente en producción de datos (14/10/2026)

**CHIRPS v3:** se descargaron y verificaron archivos GeoTIFF mensuales de octubre de 2025 a agosto de 2026 (11 meses, 55 estimaciones de píxel para cinco puntos referenciales del OAF). **Septiembre de 2026 todavía no estaba publicado** en la URL de consulta y quedó como faltante. Se preservaron el SHA-256 de los rasters, la fecha UTC de consulta, ubicación exacta de la celda, resoluciones y URLs. CHIRPS es una **estimación espacial mezclada satélite/pluviómetros**, no una observación SENAMHI ni un pronóstico.

**ENFEN:** está preparado el sistema semanal de verificación de comunicados, pero el servidor ENFEN no resolvió DNS durante la primera ejecución en GitHub Actions. La aplicación muestra `no_verificado` y enlaza directamente a [comunicados ENFEN](https://enfen.imarpe.gob.pe/comunicados/); **no inventa** un estado actual ni emite alertas propias.

**Automatización:** dos GitHub Actions los lunes para CHIRPS y ENFEN; el resultado del último monitoreo se expone en el [panel 3Z del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#monitoreo3z). La actualización depende de la disponibilidad de las fuentes y los despliegues de GitHub Pages, no es un servicio garantizado en tiempo real.

Archivos: [monitoreo CHIRPS](MONITOREO_CHIRPS_RECIENTE_3Z.md), [CSV reciente](datos/chirps_v3_reciente_3z.csv), [auditoría](datos/auditoria_rasters_chirps_3z.json), [estado CHIRPS](datos/estado_monitoreo_3z.json), [informe ENFEN](MONITOREO_ENFEN_3Z.md) y [estado ENFEN](datos/estado_enfen_3z.json).

## Datos y transparencia científica

- El observatorio conserva las fases históricas **3N–3Y** y todos sus datos originales y cálculos reproducibles.
- Base SENAMHI aportada: **1 109 meses-estación observados completos, 1996–2015**; 79 combinaciones estación-año completas y último año completo común **2012**. Se requieren fichas instrumentales adicionales para confirmar códigos y emplazamientos históricos.
- Se analizaron retrospectivamente PISCOp v3, CHIRPS v3 y ERA5-Seamless sobre meses completos históricos; no está demostrada independencia externa en los 15 pares estación-producto.
- Los valores mensuales publicados en boletines DZ2 de 2024–2025 se conservan por separado como evidencia documental preliminar, sin transformarlos en series diarias completas.
- **No se imputan días/meses faltantes ni se publica un acumulado anual observado de años incompletos.** La vigilancia de un día o semana recientes **sí puede realizarse** con datos realmente disponibles y de calidad verificada, sin esperar que termine el año.
- CHIRPS, IMERG y otros gridded son **estimaciones**, los modelos pronosticados son **pronósticos** y los pluviómetros son **observaciones instrumentales**: nunca se confunden.
- Las alertas oficiales sobre El Niño Costero corresponden a **ENFEN** y los avisos meteorológicos oficiales a **SENAMHI**. El OAF enlazará esas fuentes fechadas y evitará emitir alertas propias hasta demostrar validez.

Política histórica: [CRITERIO_COBERTURA_OFICIAL.md](CRITERIO_COBERTURA_OFICIAL.md).  
Resultados de cobertura: [RESULTADO_COBERTURA_OFICIAL.md](RESULTADO_COBERTURA_OFICIAL.md).  
Bitácora técnica completa: [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md).

## Fuentes institucionales a integrar en Fase 3Z

- **ENFEN** — https://enfen.imarpe.gob.pe/comunicados/
- **SENAMHI** — https://www.senamhi.gob.pe/
- **CHIRPS v3 (Climate Hazards Center)** — https://www.chc.ucsb.edu/data/chirps3
- **NASA GPM / IMERG** — https://gpm.nasa.gov/data/imerg
- **ECMWF** — https://www.ecmwf.int/en/forecasts

Estas fuentes tienen estados distintos: **CHIRPS v3 mensual ya está conectado**, con una actualización semanal programada y extracción real comprobada hasta agosto de 2026. La consulta ENFEN está implementada, pero su última ejecución **no pudo resolver el servidor institucional**, de modo que se muestra como no verificada y requiere revisar directamente el comunicado oficial. Las demás fuentes recientes aún no están integradas; no se deben anunciar como activas.

## Herramientas

Python, análisis estadístico, GitHub Actions, sensores remotos y SIG, con énfasis en **bajo presupuesto**, control de calidad, accesibilidad pública y aplicaciones en sanidad vegetal. La precisión dependerá de la calidad de los datos, no de presentar un modelo complejo.

---
*Proyecto científico en desarrollo. Ninguna visualización experimental sustituye los comunicados ENFEN, avisos SENAMHI ni el diagnóstico agronómico en campo.*
