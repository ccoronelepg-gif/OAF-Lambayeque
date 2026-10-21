# Fase UX-8 — Portada agroexportadora, clima regional y predicciones
**Fecha de ejecución:** 21 de octubre de 2026
**Proyecto:** OAF-Lambayeque
**Principio:** reorganizar información sin eliminar resultados científicos, fuentes ni IDs.

## Cultivos priorizados
Mango, vid, arándano, palto, maracuyá y banano. Se interpretó «bet» de la instrucción como **vid**, continuidad del cultivo ya analizado anteriormente por OAF. La denominación puede ajustarse si el autor confirma otro cultivo. Los registros se encuentran en `datos/catalogo_cultivos_agroexportacion_2026.json`, con 12 registros de grupos de plagas y 11 de enfermedades, cada uno con organismo o grupo asociado, orientación de monitoreo y fuente identificable.

## Inicio
Se mantienen el encabezado y el acceso a la guía de lectura para productores. Después figura una síntesis científica de diez párrafos, sin enlace «Explorar fuentes y metadatos» ni tarjetas redundantes de terceros/modelos.
Se crean exclusivamente tres bloques temáticos:
1. **¿Cómo está el clima?** Lugar, indicadores existentes y mapa DEM dinámico reutilizados con sus ID originales.
2. **Predicciones y anomalías.** Dashboard de lluvia prevista para siete días desde Open-Meteo, segundo dashboard con series anuales ERA5 1996–2025 elaboradas por OAF, resumen de investigación RF y un reporte con resultados reales de MAE 10I y validez del comunicado ENFEN archivado.
3. **Cultivos de agroexportación.** Seis accesos al catálogo fitosanitario por cultivo.

## Clima regional
Tres bloques visibles:
1. Serie histórica anual de lluvia/temperatura por localidad y cartografía DEM por franjas altitudinales, con leyendas y fuente.
2. Panel con mapas de agrupación territorial y modelos OAF, enlaces a dashboard 10K y comparación de RF con GCN; indicadores experimentales claramente rotulados.
3. Mapa interactivo de estaciones por altitud usando fichas 9F y manifiesto 10M, con incertidumbre geográfica y filtros.

No se extrapola automáticamente una serie histórica a valores futuros 2027–2030: el modelo multianual operativo, si se desea, requiere metodología, calibración y pruebas independientes.

## Predicciones y anomalías
Resumen de Python, estadística, SIG y Random Forest; visualización del pronóstico externo de siete días con origen y vigencia; resultados propios de lluvia mensual y probabilidad experimental P90; lectura del índice histórico Niño 1+2 desde archivo NOAA. Las probabilidades de enfermedad no se extrapolan a partir de lluvia mensual sin mediciones fitosanitarias y validación de campo.

## Datos conservados
El código `assets/oaf-agroexportacion-2026.js` reutiliza los contenedores existentes (sin clonarlos ni cambiar sus IDs) y desplaza los complementarios desde Inicio, Clima regional y Predicciones hacia `Metadatos y trazabilidad → Archivo técnico consolidado`. El archivo anterior se conserva para la vista técnica y enlaces profundos. Los productos originales del repositorio (modelos, CSV, JSON, figuras, auditorías y scripts) no se alteran.

## Fuentes verificables para el catálogo
- SENASA, moscas de la fruta en mango de Lambayeque: https://www.senasa.gob.pe/senasacontigo/lambayeque-acciones-de-control-integrado-de-moscas-de-la-fruta-contribuye-con-la-sanidad-en-la-cosecha-de-mango/
- SENASA, antracnosis y cochinillas en mango: https://www.senasa.gob.pe/senasacontigo/amazonas-senasa-capacito-a-productores-de-mango-para-la-ejecucion-de-labores-de-control-integrado-de-moscas-de-la-fruta/
- UC IPM, oídio, Botrytis y cochinillas de vid: https://ipm.ucanr.edu/agriculture/grape/
- INIA, sanidad integral del arándano: https://repositorio.inia.gob.pe/items/70ccf99b-a81b-4782-b2c6-07c4c7dabb25
- SENASA, tristeza y plagas del palto: https://www.senasa.gob.pe/senasacontigo/senasa-la-tristeza-del-palto-y-recomendaciones-para-su-control/
- INIA, manual de maracuyá: https://repositorio.inia.gob.pe/bitstreams/c335afc1-2062-4ee4-8e84-4d958539d7c6/download
- SENASA, Fusarium R4T y banano: https://www.gob.pe/institucion/senasa/noticias/967156-senasa-trabaja-en-la-contencion-de-plaga-que-afecta-a-bananos-y-platanos

Las fuentes identifican organismos de interés en Perú u otras regiones estudiadas y no implican que existan en una parcela particular de Lambayeque a la fecha de consulta.

## Archivos nuevos
- `datos/catalogo_cultivos_agroexportacion_2026.json`
- `assets/oaf-agroexportacion-2026.css`
- `assets/oaf-agroexportacion-2026.js`
- `assets/oaf-agro-charts-2026.js`
- `assets/oaf-agro-crops-2026.js`
- `assets/oaf-agro-evidencia-2026.js`
- `tests/test_agroexportacion_2026.py`

## Integridad y condiciones
El workflow UX comprueba la conservación de los scripts, IDs y rutas originales, los documentos de plagas/enfermedades, fuentes de referencia y el acceso a gráficos. Los mapas y estaciones exponen explícitamente la naturaleza exploratoria y la incertidumbre espacial. Todos los valores mostrados en gráficos temporales deben proceder de archivos históricos o de la API meteorológica y llevar unidad y fecha; cualquier fallo presenta «no disponible» y no un dato fabricado.

**La publicación de GitHub Pages no acredita por sí sola la corrección visual en todos los navegadores**; conviene validar adicionalmente en dispositivos móviles y con revisión científica del catálogo.
