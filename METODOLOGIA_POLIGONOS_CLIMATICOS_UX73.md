# OAF Lambayeque · UX73 · Polígonos climáticos indicativos (C) y reparación de capas A

**Corte técnico:** 6 de noviembre de 2026.  
**Alcance modificado:** únicamente las capas geográficas del visor A y C, y sus pruebas, hoja de estilos y caché. Se conserva el número de capas temáticas: cuatro en A y dos en B; una sola capa C. B no se modifica.

## 1. Qué significa realmente un polígono

Los polígonos UX73 se basan en indicadores meteorológicos procedentes de Open-Meteo, **no** en ocurrencia observada de plagas o enfermedades. Para construir una superficie cartográfica ilustrativa sin inventar interpolación epidemiológica:

1. Se seleccionan 30 puntos de un muestreo determinista dentro del límite referencial de Lambayeque (`datos/zonificacion_8n/limite_lambayeque_referencial.geojson`). El contorno está simplificado y su fuente secundaria no se ha validado como límite oficial.
2. Se consulta la respuesta meteorológica en cada coordenada.
3. Se construye una retícula rectangular de paso **0,055°** (aproximadamente 6 km norte-sur; la anchura real depende de la latitud).
4. Se conserva solo cada celda con **cuatro vértices y centro completamente interiores al contorno referencial**. Las celdas de borde, islas o áreas no cubiertas quedan deliberadamente sin clasificación.
5. Cada celda se asigna a la muestra meteorológica más cercana por distancia esférica, si esta dista **28 km o menos**. Se unen horizontalmente celdas vecinas con una misma muestra para formar bandas poligonales de menor peso SVG.
6. El polígono **hereda el indicador puntual de su muestra más cercana**, mediante extensión de vecino más cercano; no se evalúan datos nuevos en cada metro del polígono. Esta aproximación NO es una interpolación espacial validada ni un mapa de superficie cultivada.
7. Los polígonos muestran magnitudes climáticas descriptivas. Los colores no representan riesgo Bajo/Moderado/Alto/Muy alto de infección, infestación, daños o pérdidas. No se atribuyen probabilidades.

**Limitación:** los polígonos adyacentes pueden tener límites en escalones, no siguen límites de parcelas ni gradientes topográficos. Áreas del borde pueden carecer de polígono. Las celdas vecinas incluso pueden representar la misma celda meteorológica subyacente de Open-Meteo.

## 2. C · Riesgo agroclimático fitosanitario

La única capa C incorpora dos organismos con indicadores teóricos documentados:

| Cultivo | Patógeno/plaga | Indicador espacial 7 días | Forma de clasificación |
|---|---|---|---|
| Arándano | *Botrytis cinerea* | Número de episodios de HR a 2 m >90 % durante seis horas consecutivas | 0 episodios; 1; dos o más; sin datos. **No** infección |
| Mango | *Ceratitis capitata* | Acumulación de grados-día calculada con 8,47 °C y 9,1 °C, dos bases presentes en Ricalde 2012 | Gradiente descriptivo relativo entre puntos, **no** generaciones ni infestación |

Las series meteorológicas pronosticadas corresponden a **siete días completos siguientes al día local**, no a 7 días parciales. Los datos incompletos se excluyen, sin imputación; las temperaturas fuera del régimen experimental 15–30 °C se identifican como no aplicables para el modelo de *C. capitata*.

- Fuente Botrytis: [UC IPM, Botrytis blight](https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/); HR a 2 m NO equivale a humectación foliar.
- Fuente mosca de fruta: [Ricalde et al. 2012, DOI 10.1673/031.012.3301](https://doi.org/10.1673/031.012.3301); temperaturas base 8,47 (abstract) y 9,1 (resultados) son discrepantes en esa publicación; no son calibraciones Lambayeque.
- El archivo GeoJSON de polígonos incluye `es_riesgo_calibrado:false`, `incidencia:null` y `probabilidad_infeccion:null`. El archivo GeoJSON de puntos continúa disponible.

Los restantes cultivos/organismos no reciben polígonos de riesgo fitosanitario ficticios.

## 3. A · Peligros climáticos e hidrometeorológicos

### 3A. Inundaciones — producto oficial y complemento distinto

- **Producto oficial requerido:** CENEPRED SIGRID, ID **5090024**, susceptibilidad a inundación por lluvias fuertes, referencia 2021. [Ficha oficial del servicio](https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024).
- **Revisión:** el identificador está documentado y es de tipo **raster**, no vector. Su representación depende del geoservicio ArcGIS REST. Durante el ensayo remoto UX73 el servicio **no respondió** (`fetch failed` desde runner), por lo que no se puede afirmar que la capa oficial haya sido visualmente verificada ni sustituirla por formas inventadas.
- **Alternativa visual honesta:** cuando el usuario marca inundaciones, la interfaz muestra **lluvia máxima diaria pronosticada** como *contexto meteorológico* en polígonos aproximados, con advertencia de que no es susceptibilidad, mapa hidráulico, delimitación de inundación ni peligro validado. El raster CENEPRED se sigue solicitando separadamente. El contexto se dibuja con menor opacidad para no tapar totalmente una eventual respuesta oficial.
- **Datos publicados de exposición agrícola**, no raster ni predicción: [CENEPRED documento 17791](https://sigrid.cenepred.gob.pe/sigridv3/documento/17791) indica nueve distritos en escenario 2025–2027, con 1 234 ha de superficie agrícola de mayor susceptibilidad en ese subconjunto. No se generan polígonos de nueve distritos sin límites administrativos completos.

### 3B. Lluvias intensas

- **Variable:** máxima precipitación diaria modelada entre los próximos siete días (mm/24 h).
- **Fuente:** Open-Meteo Forecast API, campos `daily.precipitation_sum`. Las categorías `<1`, `1–10`, `10–30`, `≥30 mm/24h` representan **intervalos descriptivos de precipitación** y no son umbrales normativos de aviso de SENAMHI ni peligros geotécnicos oficiales. Se requieren corroboración con estaciones y umbrales locales para declarar peligro.

### 3C. Sequía y déficit hídrico

- **Variable:** lluvia total modelada de los **30 días anteriores**, mediante `past_days=30` y `daily.precipitation_sum`.
- **Fuente:** Open-Meteo Forecast (serie retrospectiva modelada); **no** SPI, SPEI, humedad de suelo, déficit del cultivo ni sequía oficial. Los intervalos visuales de `<10`, `10–30`, `30–75`, `≥75 mm/30d` solo muestran magnitud de lluvia acumulada, no cuantifican anormalidad respecto de una climatología.
- **Para validar sequía:** disponer de serie histórica 1991–2020 con un método SPI/SPEI documentado, análisis de balance hídrico, ET0 y reserva de agua del suelo, y validación local.

### 3D. Temperaturas extremas

- **Variable disponible funcionalmente:** máxima temperatura diaria pronosticada a 2 m durante los próximos siete días, a partir de Open-Meteo. Las bandas `<25`, `25–30`, `30–35` y `≥35 °C` son rangos descriptivos; **no** identifican olas de calor sin percentiles y duración local.
- **Fuente oficial histórica adicional:** SENAMHI IDESEP [Frecuencia de olas de calor](https://idesep.senamhi.gob.pe/portalidesep/wms.do), grupo `g_01_06`. Se corrigió la ausencia de `heatWmsUrl` y se generó la petición `GetMap`. El servicio **tampoco respondió** desde el runner en la verificación UX73; la capa Open-Meteo proporciona un mapa climático legible aunque la WMS histórica falle.
- **Limitación:** la representación de Tmáx solo trata calor; un mapa completo de extremos también necesita temperaturas mínimas y percentiles históricos.

## 4. Estado técnico y validación

- Los tests matemáticos verifican que los polígonos sean interiores al contorno, referidos a alguno de los 30 puntos, dentro de ≤28 km y con geometría Polygon válida.
- Las pruebas unitarias controlan fechas, 30 días anteriores, siete días posteriores, lluvia y temperatura, y rechazan nulos.
- Se validó la conexión diaria de Open-Meteo en Motupe y Olmos: 38 días (30 anteriores, día actual, siete futuros) completos por punto.
- Las pruebas de navegador usan respuestas meteorológicas sintéticas **solo para comprobar renderizado y acciones**, nunca se almacenan ni publican en la web como pronósticos.
- El portal publicado consulta servicios externos en tiempo de uso; si un servicio falla, no debe mostrar datos sintéticos.

**Estado de esta fase:** cartografía de potencial climático y funcionalidad frontend, no validación científica de riesgo de campo ni garantía de disponibilidad de fuentes externas.

## 5. Próximos requisitos para polígonos verdaderos de riesgo

No usar estas zonas estimadas para recomendar aplicaciones de plaguicidas o evacuar un sector. Antes de elaborar polígonos de riesgo reales, conseguir coberturas verificadas de los cultivos, incidencia/monitoreo georreferenciado SENASA, estaciones locales y un modelo epidemiológico con validación temporal y espacial; para inundación, raster/vector oficial descargado con su leyenda y clasificación, no una imagen convertida de colores.

## Archivos

- `modelos/poligonos_potenciales_ux73.js`
- `assets/oaf-ux35d-mapa-potencial.js`
- `assets/oaf-ux73-peligros-poligonos.js`
- `assets/oaf-ux30-territorio-unificado.js`
- `assets/oaf-ux73-poligonos.css`
- `tests/poligonos_ux73.cjs`
- `tests/ux73_navegador.cjs`
- `tests/verificar_fuentes_peligros_a_ux73.cjs`
