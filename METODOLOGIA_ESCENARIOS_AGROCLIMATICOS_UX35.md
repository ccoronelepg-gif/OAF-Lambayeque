# OAF-Lambayeque · UX35 — Visor multicapa de escenarios agroclimáticos

**Fecha de integración:** 22 de octubre de 2026  
**Pestaña:** Predicciones y anomalías → Escenarios de riesgo agroclimático  
**Propósito:** comparar antecedentes históricos con señales meteorológicas actuales, susceptibilidad a inundaciones/deslizamientos y activos agrícolas/urbanos para orientar vigilancia preventiva. **No genera mapas de inundación futura, pronósticos de caudal ni alertas operativas.**

## 1. Nueva arquitectura de la subpestaña

Únicamente permanece visible el visor central de tres paneles: **Capas**, **Mapa** y **Diagnóstico del territorio y posibles impactos**. Los cuadros anteriores de la subpestaña quedan ocultos; los enlaces y la metodología se conservan en «Metadatos y trazabilidad».

La sección de capas se divide en:
1. **Antecedentes de El Niño:** comparación de lluvia estimada para 1983, 1998, 2017 y 2023; puntos geológicos de inundación fluvial/pluvial y flujos de detritos de 2017; estudio CENEPRED 2023.
2. **Lluvias pronosticadas:** acumulados a tres o siete días y umbral descriptivo ajustable (20, 40, 70 y 100 mm) en Chiclayo, Jayanca, Motupe y Olmos; perspectiva cualitativa de ENFEN a partir de noviembre 2026.
3. **Consecuencias potenciales:** susceptibilidad a inundaciones y movimientos en masa, vigilancia de cauces, sequía y calor. **Los escenarios se construyen visualmente; no se asignan probabilidades ni extensiones de impacto inventadas.**
4. **Agricultura y agroindustrias:** superficie agrícola MINAM 2018; seis puntos referenciales de empresas/oficinas/fundos obtenidos de cartografía abierta, con estatus explícito de fuente.
5. **Capas territoriales compartidas:** todas las categorías del visor «Territorio y riesgos climáticos» —mapa base, divisiones políticas, cuencas, ríos, quebradas, puntos críticos, vías MTC y servicios de emergencias— y selección de provincia, distrito o cuenca usando el mismo estado de filtrado.

## 2. Antecedentes 1983, 1998, 2017 y 2023

**Estudio histórico oficial:** CENEPRED, *Escenario de riesgo por inundaciones y movimientos en masa ante lluvias asociadas al fenómeno El Niño*, actualización del **15 de mayo de 2023**. El estudio considera lluvias de los veranos de 1983, 1998, 2017 y 2023, en un escenario de susceptibilidad y exposición, no un conjunto de huellas cartográficas observadas para cada año.

https://sigrid.cenepred.gob.pe/sigridv3/documento/16310

**Lluvia histórica comparativa:** consultas a Open-Meteo Archive para **enero a marzo**, por separado, de 1983, 1998, 2017 y 2023. Cuatro puntos de referencia de Lambayeque (Chiclayo, Jayanca, Motupe y Olmos), coordenadas publicadas en `assets/oaf-ux35-escenarios-multicapas.js`.

Ejemplo:
`https://archive-api.open-meteo.com/v1/archive?latitude=-6.7714&longitude=-79.8409&start_date=2017-01-01&end_date=2017-03-31&daily=precipitation_sum&timezone=America%2FLima`

Los registros son **estimaciones de reanálisis meteorológico**, no series instrumentales de pluviómetros. No se interpola entre localidades ni se afirma que una de ellas represente a todas las cuencas. Un total trimestral no se compara directamente con el pronóstico de tres o siete días sin normalización por ventana, climatología y fuente.

Para **2017** se incorporan los puntos registrados por INGEMMET en la evaluación geológica del Niño Costero. Los eventos de 1983, 1998 y 2023 no usan esos puntos como si hubieran sucedido en esos años.

Fuente vectorial: https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6010100

## 3. Pronóstico a siete días y perspectiva noviembre 2026–verano 2027

**Pronóstico diario:** Open-Meteo Forecast API `daily=precipitation_sum`, con `forecast_days=7`. Los valores se consultan en línea en el navegador y cambian cuando el proveedor actualiza su modelo. Se puede seleccionar ventana de 3 o 7 días y un umbral meramente **descriptivo**, nunca equivalente a nivel de alerta oficial de SENAMHI.

**Perspectiva estacional (fotografía informativa de octubre de 2026):** ENFEN, Comunicado Oficial **N.º 18-2026 del 16 de octubre de 2026**. Señala:

- Alerta de **El Niño Costero**, con condiciones cálidas previstas hasta otoño de 2027.
- **Lluvias superiores a lo normal** en la costa norte durante el resto de 2026 y en el verano de 2027, posibles episodios localizados de moderada a fuerte intensidad.
- **Caudales superiores a lo normal**, principalmente **desde noviembre** en el **río La Leche**, entre otros ríos del norte.
- Temperaturas costeras del aire muy superiores a lo normal; el comunicado menciona niveles muy bajos del **reservorio Tinajones** para la época.

Fuente oficial: https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-18-2026/

Referencias SENAMHI enlazadas desde ENFEN:
- Perspectivas climáticas: https://www.senamhi.gob.pe/load/file/02262SENA-76.pdf
- Escenarios del verano: https://www.senamhi.gob.pe/load/file/02261SENA-25.pdf
- Perspectiva hidrológica: https://www.senamhi.gob.pe/load/file/02694SENA-74.pdf

El comunicado ofrece una **señal climática/hidrológica regional**, no una tabla validada de milímetros mensuales por distrito, caudales `m³/s` por estación ni fechas de inundación. La perspectiva ENFEN se rotula explícitamente con fecha y requiere una actualización editorial cuando se publique un comunicado posterior.

## 4. Posibles impactos

Los módulos de consecuencias muestran cómo interpretar en conjunto:
- susceptibilidad regional a inundaciones (INGEMMET/SIGRID `5010502`),
- susceptibilidad a movimientos en masa (`5090022`),
- inventarios geológicos históricos,
- hidrografía y cuencas ANA/IGN,
- zonas agrícolas MINAM 2018,
- carreteras MTC y establecimientos de emergencia IGN/IDEP,
- sequías registradas y cartografía histórica de calor SENAMHI.

**No se calculan ni dibujan futuras huellas de inundación o deslizamiento** sin un modelo hidrológico/hidráulico validado y resultados espaciales con precisión adecuada. La cercanía de un punto de empresa a una zona susceptible no permite deducir daño material, nivel de exposición cuantificado o si una instalación está operativa.

## 5. Capa de empresas agroindustriales y fundos

Archivo geográfico abierto incluido:
`datos/riesgos_ux35/ubicaciones_agroindustriales_referenciales.geojson`

| Nombre | Tipo de geometría observada | Fuente |
|---|---|---|
| Agrovision Perú S.A.C. | Oficina en Olmos | OSM/Mapcarta, nodo 12903547120; BASC WBO certificado julio 2026 |
| Complejo Agroindustrial Beta S.A. | Oficina en Olmos | OSM/Mapcarta, nodo 12903547760 |
| Frusan Agro S.A.C. | Oficina en Olmos | OSM/Mapcarta, nodo 12903418586 |
| Agrícola Chapi | Oficina en Olmos | OSM/Mapcarta, nodo 12903547772 |
| Agrolmos S.A. | Punto referencial de terreno agrícola | OSM/Mapcarta, polígono 1465622784 |
| Fundo C5 AGV / Agrovision | Punto referencial de terreno agrícola | OSM/Mapcarta, polígono 1008256014 |

Estas ubicaciones son **una muestra no exhaustiva**, no equivalen a perímetros de empresas y **no son un padrón de formalidad tributaria**. El certificado BASC documental de Agrovision acredita certificación de la instalación auditada, no formalidad tributaria de las demás entidades. Antes de ampliar el inventario debe cruzarse nombre/RUC y estado de alta con SUNAT y dirección geocodificada verificada.

Fuente de oficina Agrovision: https://mapcarta.com/es/N12903547120  
Fuente de Beta: https://mapcarta.com/es/N12903547760  
Fuente de Frusan: https://mapcarta.com/es/N12903418586  
Fuente de Agrícola Chapi: https://mapcarta.com/es/N12903547772  
Fuente Agrovision BASC: https://sibasc.wbasco.org/mod_consulta_pag_wbo/consulta_empresa.php?capitulo_id=4&empresa_id=1647&session_nomidioma=

## 6. UX, atribución y condiciones de uso

- La interfaz solo se muestra como **visor central**; la demás información de la subpestaña se oculta para evitar redundancia.
- Los filtros territoriales se vinculan a los ya existentes en el visor de «Territorio y riesgos climáticos». Las geometrías se reutilizan mediante interfaces entre módulos, sin duplicar ni fabricar registros.
- Las capas se pueden activar por separado, combinar y consultar con marcadores; el diagnóstico explica cada selección y describe consecuencias potenciales de manera sencilla.
- En móvil los tres paneles se apilan; el árbol de capas mantiene desplazamiento independiente.
- Las solicitudes de reanálisis y pronóstico pueden fallar por CORS, red o políticas del proveedor. Se muestran errores o estados de carga; **no hay datos ficticios de respaldo**.
- El portal no sustituye boletines oficiales de SENAMHI, ENFEN, ANA, INDECI o CENEPRED.

## 7. Pendientes científicos

1. Incorporar series hidrométricas observadas de La Leche, Chancay-Lambayeque y Zaña, con estaciones identificadas.
2. Calibrar un modelo lluvia-escorrentía por cuenca y validar retrospectivamente los picos de caudal.
3. Añadir mapas de profundidad/extensión de inundación **únicamente** a partir de modelos hidráulicos calibrados o escenarios oficiales explícitos.
4. Ampliar el directorio de empresas con fuentes oficiales, RUC y geocodificación precisa de las instalaciones.
5. Verificar en navegadores reales y PWA disponibilidad CORS de cada servicio, responsividad y tiempos de respuesta.
