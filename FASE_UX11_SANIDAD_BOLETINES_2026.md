# Fase UX-11 — Cultivos y Sanidad + Boletines oficiales
**Actualización:** 21 de octubre de 2026.
**Objetivo editorial:** dos bloques por pestaña, control científico de las fuentes y conservación integral del archivo técnico.

## Cultivos y Sanidad: dos bloques
### 1. Modelo Agroclimático Predictivo
- Filtros dependientes: localidad (Chiclayo, Jayanca, Motupe, Olmos), cultivo (mango, vid, arándano, palto, maracuyá, banano), tipo (plaga/enfermedad) y organismo.
- 23 fichas: 12 registros de plagas y 11 de enfermedades.
- API Open-Meteo: 7 días de precipitación prevista, máximas térmicas y series horarias de temperatura y humedad agregadas por día. Filtrado explícito de datos incompletos.
- Diagrama interactivo de lluvia diaria y humedad; resumen, daño, agente causal y enlaces científicos.
- Conclusiones cualitativas sobre *condiciones que ameritan vigilancia* según temperatura, humedad, lluvia o drenaje; no se pronostican presencia, infección, incidencia ni fluctuación poblacional observada a partir del clima.
- Para Fusarium R4T: no se estima una probabilidad por lluvia/temperatura; se destaca bioseguridad y reporte al SENASA.
- La metodología y los experimentos previos permanecen en Metadatos.

### 2. Manejo Sanitario
- Filtros de cultivo, tipo de organismo y enfermedad/plaga.
- Explicación del daño, pérdida productiva y medidas culturales o de monitoreo.
- Cinco casos con ejemplo documentado en Perú:
  - Mango, mosca de la fruta: spinosad formulado en cebo, resolución SENASA 141-2025.
  - Vid, oídio: Luna Experience, fluopyram + tebuconazol, PQUA 684-SENASA, fuente Bayer Perú.
  - Arándano, moho gris: Switch 62.5 WG, ciprodinil + fludioxonil, ficha 2024, PQUA 262-SENASA y uso indicado para arándano/moho gris por fabricante.
  - Palto, pudrición radicular: antagonista *Trichoderma viride*, ejemplo de control biológico expuesto por SENASA; el agente no constituye por sí mismo un plaguicida habilitado para cualquier formulación.
  - Banano, picudo negro: *Beauveria bassiana*, experiencia técnica SENASA 2020.
- Se evita extrapolar biofungicidas a cultivos que no tienen la combinación exacta sustentada en etiqueta: no se asignan marcas/dosis a los demás organismos.
- Verificar siempre SIGIA: https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_cultivo.html
- Para productos de exportación, comprobar límites máximos de residuos en destino, etiqueta, carencia, reingreso y gestión de resistencia.
- Diagramas botánicos y patológicos son esquemas explicativos, no imágenes de diagnóstico.

## Boletines oficiales: dos bloques
### 1. Información del Niño
Tarjetas con las publicaciones primarias:
- ENFEN N.º 18-2026, 16/10/2026, estado **Alerta de El Niño Costero**.
- Informe Técnico ENFEN 18, publicado 18/10/2026.
- NOAA CPC, 08/10/2026, fortalecimiento de El Niño global y posible fase fuerte/muy fuerte hasta inicios de 2027.
- SENAMHI, consulta de avisos vigentes en Lambayeque.
- CENEPRED/SENAMHI: estudio de escenarios de lluvias de octubre–diciembre de 2026.

### 2. Evolución de los boletines
- Tres tarjetas de lectura rápida: ENFEN, NOAA y consulta territorial SENAMHI.
- Gráfico mensual coloreado de anomalía oceánica Niño 1+2 según archivos NOAA NCEI ERSSTv5 del repositorio, base 1991–2020.
- Resumen para productores: el seguimiento de El Niño obliga a prepararse, pero la alerta oceánica no define fechas ni acumulados locales de lluvia.
- Enlaces a fuente original, predicciones a siete días y trazabilidad.

## Garantías técnicas
Los módulos anteriores de la pestaña Cultivos y de la pestaña Boletines se mueven como nodos DOM existentes —sin clonarlos ni perder sus IDs— a dos desplegables dentro de **Metadatos y trazabilidad**. Los demás contenidos de Metadatos, la portada y los paneles de Clima regional y Predicciones y anomalías no se modifican.

**Archivos añadidos**
- `datos/sanidad_agroexportadora_2026.json`
- `datos/boletines_institucionales_2026.json`
- `assets/oaf-sanidad-boletines-ux11.css`
- `assets/oaf-ux11-estructura.js`
- `assets/oaf-ux11-sanidad.js`
- `assets/oaf-ux11-boletines.js`
- `tests/test_ux11_sanidad_boletines_2026.py`

## Referencias clave
- SENASA SIGIA: https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_cultivo.html
- SENASA control biológico picudo banano (2020): https://www.senasa.gob.pe/senasacontigo/productores-emplean-control-biologico-para-combatir-plagas-en-el-cultivo-de-banano/
- SENASA spinosad (2025): https://www.gob.pe/institucion/senasa/normas-legales/7660481-141-2025-midagri-senasa-jn
- Bayer Perú Luna Experience: https://www.agro.bayer.pe/content/cropscience/latin-america/pe/es-pe/productos/product-details.html/fungicide/luna_experience
- Syngenta Switch: https://www.syngenta.com.pe/product/crop-protection/fungicida/switchr-625-wg
- SENASA tristeza palto: https://www.senasa.gob.pe/senasacontigo/senasa-la-tristeza-del-palto-y-recomendaciones-para-su-control/
- UC IPM uva oídio: https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/
- Revisión maracuyá 2023: https://www.scielo.org.pe/scielo.php?pid=S2077-99172023000400011&script=sci_arttext
- ENFEN 18-2026: https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-18-2026/
- NOAA CPC 08/10/2026: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc_Sp.shtml
- SENAMHI avisos: https://www.senamhi.gob.pe/main.php?dp=lambayeque&p=aviso-meteorologico-vigente

**Límites:** Los insumos modelados de Open-Meteo no certifican datos instrumentales de campo; las relaciones meteorológicas son solo orientativas. El catálogo no representa el registro vigente de productos; consultar SENASA al momento de decidir una aplicación. Los boletines están fechados; verificar versiones posteriores en cada institución.
