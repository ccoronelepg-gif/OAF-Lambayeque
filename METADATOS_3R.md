# OAF-Lambayeque — Fase 3R: identidad y procedencia de estaciones

**Corte documental:** octubre de 2026 · **Estado:** auditoría preliminar de fuentes, sin certificación definitiva de emplazamientos durante 1996–2015.

## Principio de trazabilidad

Una coordenada publicada para una estación con el mismo nombre NO prueba identidad instrumental, ausencia de traslados o continuidad exacta durante toda la serie descargada. El inventario registra **coordenada de análisis**, **coordenada candidata**, **fuente**, **tipo de estación** cuando se conoce y **nivel de verificación pendiente**.

| Estación | Posición utilizada en 3Q (lat, lon) | Alternativa auditada (lat, lon) | Evidencia y observaciones |
|---|---|---|---|
| Jayanca (La Viña) | -6.322, -79.779 | -6.33306, -79.76861 | Tabla de SENAMHI de estación histórica de nombre exacto y elevación 103 m. La EMA La Viña de la ficha oficial es una estación automática distinta en nomenclatura y altitud (75 m); equivalencia no comprobada. |
| Cayaltí | -6.88079444, -79.54701389 | -6.89853, -79.55964 | SENAMHI publica puntos distintos: estación convencional código **000320**, 6°52'50.86 S, 79°32'49.25 O y 90 m; tabla histórica de SENAMHI -6.89853, -79.55964 y 102 m. No está documentada la causa de la discrepancia ni las fechas de uso de cada ubicación. |
| Reque | -6.88613, -79.83550 | -6.88644, -79.83572 | Tabla histórica SENAMHI, 21 m. Separación mínima; comprobar código y ficha de la serie original. |
| Lambayeque | -6.73152778, -79.90983611 | -6.70361, -79.92139 | Alternativa de inventario preliminar sin ficha de instrumento exacta. Un reporte de monitoreo agrometeorológico SENAMHI consigna aprox. 6°42'15 S, 79°55'37 O, 38 m, pero NO prueba equivalencia con los datos diarios. |
| Cueva Blanca | -6.13130, -79.40450 | -6.149, -79.350 | Un reporte de INGEMMET recogido por CENEPRED describe estación PLU Cueva Blanca con código **106060**, 6°7'52.68 S, 79°24'16.2 O, 3300 m; una tabla histórica reproducida de ANA señala Cueva Blanca **153102** en -6.149,-79.350. **Identidad conflictiva: no sustituir sin documento que demuestre equivalencia.** |

## Conclusiones de sensibilidad de la precipitación estimada CHIRPS

La prueba `scripts/sensibilidad_geografica_3r.py` extrajo CHIRPS v3 mensual en 1998 y 2000 para ambos pares de coordenadas. Comprueba los 24 meses de cada estación respecto a `datos/comparacion_3q_1996_2015.csv`, sin modificar observaciones SENAMHI.

**24/24 mapas mensuales procesados; 240 píxeles extraídos; 10 comparaciones anuales; 0 incidencias.**

- **Jayanca:** 1,683 km entre puntos; ambos dentro del mismo píxel de 0,05°. Cambio de acumulado anual 1998 y 2000: **0 mm**.
- **Cayaltí:** 2,415 km; diferentes píxeles en 24/24 meses. Cambio en CHIRPS anual **−47,855 mm (1998)** y **−3,961 mm (2000)**.
- **Reque:** 0,042 km; mismo píxel en 24/24. Cambio anual **0 mm**.
- **Lambayeque:** 3,356 km; mismo píxel en 24/24. Cambio anual **0 mm**.
- **Cueva Blanca:** 6,339 km; píxeles distintos en 24/24. Cambio anual **+139,802 mm (1998)** y **+138,397 mm (2000)**.

Los cambios entre candidatos miden sensibilidad **del producto espacial**, NO evidencia de reubicación física ni corrección de las posiciones. El desempeño frente a la lluvia observada puede mejorar o empeorar por coincidencia; no debe decidirse la localización según qué punto arroje menor MAE.

## Información aún necesaria

1. Correspondencia entre el **código registrado en la descarga TXT** y el catálogo SENAMHI; verificar fuente de medición y estación, nombre histórico, latitud, longitud, elevación, fechas de operación, cambio de instrumentos/emplazamientos.
2. Si no se acredita continuidad geográfica, reportar un rango de resultados o sensibilidad en lugar de una sola «ubicación corregida».
3. Ampliar estaciones instrumentales y acceso a datos posteriores a 2015. El sistema público de descarga SENAMHI permite solicitar series diarias, pero su trámite **requiere usuario registrado y contraseña**. Que los TXT recibidos terminen en 2014/2015 no significa que todas las estaciones hayan dejado de operar esos años.
4. Prueba de independencia: identificar registros que no intervinieron en la construcción de PISCOp y CHIRPS, o utilizar separación espacial robusta en validación.

## Fuentes documentales consultadas

- SENAMHI, tabla de estaciones históricas (incluye Jayanca, Cayaltí y Reque): https://www.senamhi.gob.pe/load/file/01404SENA-1.pdf
- SENAMHI, ficha de EMA La Viña (no equiparar sin pruebas): https://www.senamhi.gob.pe/load/file/00701SENA-313.pdf
- SENAMHI, ficha de estación convencional Cayaltí código 000320: https://web2.senamhi.gob.pe/include_mapas/_dat_esta_tipo.php?estaciones=000320
- SENAMHI, reporte de monitoreo agrometeorológico con estación Lambayeque: https://www.senamhi.gob.pe/load/file/02951SENA-53.pdf
- INGEMMET/CENEPRED, informe técnico A7022, Cueva Blanca 106060 y 3300 m: https://sigrid.cenepred.gob.pe/sigridv3/storage/biblioteca/14262_informe-tecnico-n0-a7022-evaluacion-de-peligros-geologicos-de-la-institucion-educativa-10061-colaya-centro-poblado-colaya-distrito-salas-provincia-lam.pdf
- Extracto secundario de tabla ANA (Cueva Blanca 153102; requiere cotejo con PDF original): https://es.slideshare.net/slideshow/ana00031271pdf/251920437
- SENAMHI, servicio oficial para acceder a datos diarios y registro: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos

**Archivos de evidencia**: `datos/catalogo_coordenadas_3r.csv`, `datos/sensibilidad_3r_mensual.csv`, `datos/sensibilidad_3r_resumen.csv`, `datos/coordenadas_pixeles_3r_1998_2000.csv`, `datos/estado_3r.json`, `SENSIBILIDAD_3R.md`.

**Próximo paso 3R:** ampliar el análisis de sensibilidad para el periodo de validación 1996–2015 si es justificable, y obtener correspondencia oficial entre fichas de estación e históricos; no sustituir las series ya evaluadas por otros puntos sin documentar su procedencia.
