# OAF Lambayeque · Validación teórica y capa cartográfica de potencial agroclimático UX72

**Fecha de corte:** 6 de noviembre de 2026.  
**Ubicación:** VISOR → Escenarios de riesgo agroclimático → C. Riesgo agroclimático fitosanitario.

## Propósito

Mostrar en un mapa regional la **distribución espacial de condiciones meteorológicas potencialmente favorables** para los dos indicadores teóricos disponibles (arándano–*Botrytis cinerea* y mango–*Ceratitis capitata*), con datos reales pronosticados y **sin afirmar riesgo epidemiológico calibrado, presencia de la plaga, incidencia, probabilidad de infección, generaciones ni necesidad de aplicar fitosanitarios**. No existen datos locales de campo suficientes para esa interpretación.

Esta implementación no es una evaluación de susceptibilidad de un predio, ni un modelo estadístico de incidencia, ni una interpolación validada sobre la región. Es una consulta georreferenciada de indicadores agroclimáticos potenciales.

## 1. Niveles de validación

| Validación | Arándano / *B. cinerea* | Mango / *C. capitata* |
|---|---|---|
| Relación cultivo–organismo | Respaldada (INIA y literatura fitopatológica) | Respaldada (SENASA y literatura entomológica) |
| Variable meteorológica vinculada | HR ambiente; **no** humedad foliar medida | Temperatura del aire; no temperatura de pupa en suelo |
| Parámetro teórico bibliográfico | HR del aire >90 % durante ≥6 h (proxy de un ambiente propicio) | Umbral inferior reportado 8,47/9,1 °C; constante 341 GD de laboratorio (Petrolina) |
| Fórmula implementada | Contar episodios de HR >90 % de ≥6 h consecutivas | GD = max(Tmedia diaria − Tbase,0), sumados en 7 días |
| Control matemático | Test racha que cruza medianoche, datos nulos y faltantes | Test 25 °C, 7 días y sensibilidad de bases |
| Prueba meteorológica | 30 series reales de Open-Meteo, horarias | 30 series reales de Open-Meteo, horarias |
| Verificación epidemiológica Lambayeque | **No** | **No** |
| Riesgo de campo/semáforo autorizado | **No** | **No** |

### 1A. *Botrytis cinerea* en arándano

La guía oficial de berries **NSW DPI 2025–2026** explica que infección de *Botrytis* en frutos y flores se relaciona con períodos de humedad alta, lluvia y **humectación del tejido**; por ejemplo, cita seis horas de humectación foliar a 20 °C como suficientes en ciertas condiciones. Se trata de un fenómeno fisiopatológico asociado a superficies mojadas, temperatura y fenología. Fuente: [Berry plant protection guide 2025–2026](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0006/566349/Berry-plant-protection-guide-2025.pdf).

La guía general [UC IPM — Botrytis blight](https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/) asocia humedad relativa alta y periodos húmedos con la enfermedad. Como OAF **no mide la humectación de flores/frutos** para los 30 puntos, el mapa solo cuenta episodios de **HR del aire a 2 m mayor a 90 % por seis horas continuas**: eso es un *indicador del ambiente*, no una condición de infección comprobada ni una probabilidad.

- Una secuencia continua de 8 horas con HR >90 % se cuenta como **un episodio**, no tres.
- Un intervalo que atraviese medianoche se cuenta como **un solo episodio**.
- Leyenda: **0 episodios detectados**; **1 episodio**; **≥2 episodios**; **datos faltantes**. Son categorías de *frecuencia de episodios meteorológicos*, **NO niveles Bajo/Moderado/Alto** de una enfermedad.
- Un valor 0 no implica ausencia de inóculo ni sanidad del cultivo.

### 1B. *Ceratitis capitata* en mango

Ricalde et al. (2012), [*Journal of Insect Science* 12:33, DOI 10.1673/031.012.3301](https://doi.org/10.1673/031.012.3301), estudiaron desarrollo de inmaduros de poblaciones brasileñas, incluida Petrolina. Existe una discrepancia dentro de su propio artículo: **el resumen indica 8,47 °C** y el texto de resultados **9,1 °C**, ambos con un requerimiento total de **341 grados-día**. Es insuficiente para afirmar que cualquiera de las dos bases corresponde a las condiciones de Lambayeque.

La cartografía **no selecciona arbitrariamente un parámetro como definitivo**: calcula un intervalo de sensibilidad:

```
GD_base_9.1  = Σ_{7 días} max(0, Tmedia_día(2 m) - 9.1 °C)
GD_base_8.47 = Σ_{7 días} max(0, Tmedia_día(2 m) - 8.47 °C)
```

Un ejemplo de prueba, **no pronóstico real**: siete días con temperatura media constante de 25 °C dan **111,30 GD** (base 9,1) y **115,71 GD** (base 8,47). El motor rechaza cualquier jornada con media fuera del intervalo experimental de 15–30 °C; las demás celdas siguen procesándose. La temperatura de aire a 2 m no representa necesariamente el microambiente del suelo donde pupa el insecto.

Los grados-día no son población, infestación, densidad MTD, ni probabilidad de daño. No se calcula cuántas generaciones ocurren sin una fecha biológica confirmada de inicio de cohorte (biofix) y monitoreo local, y **341 GD no se utiliza para asignar un semáforo**.

Fuente contextual nacional: [SENASA — mosca de la fruta en Lambayeque](https://www.senasa.gob.pe/senasacontigo/senasa-lambayeque-se-mantiene-en-etapa-de-erradicacion-de-mosca-de-la-fruta/). El MTD antiguo de ese comunicado **no es la tasa actual de 2026** ni se incorpora a los mapas.

## 2. Método cartográfico

- **Contorno:** `datos/zonificacion_8n/limite_lambayeque_referencial.geojson`, que indica expresamente «límite simplificado, fuente secundaria histórica, no validado oficialmente para 2026».
- **Sistema de coordenadas:** WGS84 (CRS84 / EPSG:4326) para la consulta de latitud y longitud.
- **Malla de muestras:** determinista, 10 columnas × 8 filas de centros candidatos dentro de la envolvente, excluyendo los puntos fuera del polígono mediante ray casting; se seleccionan como máximo **30 puntos**. Cada marcador se ubica en la **coordenada consultada**, no necesariamente en el centro de la celda seleccionada por el proveedor.
- **Resolución meteorológica:** la del producto de Open-Meteo de elección automática; los 30 puntos consultados **no garantizan 30 celdas meteorológicas independientes**. La interfaz muestra cuántas celdas devuelto el proveedor se distinguen por su centro aproximado.
- **Horizon temporal:** los siete días **completos siguientes al día local** de la consulta; se exigen 24 registros por día (168 h por punto).
- **Proveedor:** [Open-Meteo Forecast API](https://open-meteo.com/en/docs), consulta múltiple real con parámetro `latitude` y `longitude` como listas, `timezone=America/Lima`, `forecast_days=8`, `cell_selection=land`.
- **No hay interpolación:** no se generan celdas coloreadas, polígonos de riesgo ni gradientes sobre zonas no muestreadas. Solo hay círculos de puntos con valores derivados de sus series meteorológicas respectivas.
- **No hay mapa de distribución de cultivo:** que un punto tenga condiciones teóricas para mango o arándano no demuestra que exista ese hospedante allí. Evitar usarlo para inferir superficie susceptible.
- **GeoJSON:** puede exportarse como `FeatureCollection` de puntos con variables derivadas, fuente y advertencia explícita `es_riesgo_calibrado: false`; **no** contiene polígonos de riesgo.

## 3. Integridad del procesamiento

1. Cada respuesta se verifica contra el número exacto de coordenadas enviadas (30).
2. Cada serie se comprueba por longitud y por fecha/hora, falta de hora, duplicados y nulos.
3. Si falla la información de un punto, este se representa sin dato verificable, **no se imputan números, se extrapolan zonas ni se colorean áreas ficticias**.
4. Si falla completamente Open-Meteo, se muestra el error y se elimina el mapa anterior para impedir la presentación de datos caducados como actuales.
5. Al cambiar el organismo se recalculan variables y se reemplaza toda la capa.
6. Activar/desactivar C dibuja/retira los puntos sin alterar A ni B; el redibujado del contorno notifica la reconstrucción del overlay.
7. Se permite inspeccionar cada punto mediante click/teclado y exportar sus coordenadas y datos a GeoJSON.

## 4. Estado de los otros organismos priorizados

Los 23 registros de los seis cultivos principales continúan en revisión bibliográfica (UX70–UX71); aún no hay parámetros regionales validados para clasificarlos automáticamente. Café (*Hemileia vastatrix* y *Leucoptera coffeella*) aparece en el catálogo experimental, no en las 23 fichas principales. No se activan modelos genéricos de antracnosis, mildiu, sigatoka, roya, phytophthora, fusariosis o plagas sin diagnóstico. **Foc R4T** exige bioseguridad y supervisión SENASA, no una predicción de presencia por clima.

## 5. Limitaciones y requisitos para un verdadero mapa de riesgo

Para pasar de mapa de clima a riesgo agroclimático **epidemiológicamente validado** se necesita:
1. Mapa oficial vigente de cultivos/parcelas y fenología.
2. Vigilancia SENASA/estaciones y presencia/abundancia identificada por especie.
3. Medición de humectación foliar y temperatura de dosel para *Botrytis*; temperatura del suelo y MTD/biofix para *Ceratitis*.
4. Validación espacial y temporal independiente por localidad, año y sistema de cultivo, incluyendo métricas de discriminación, calibración e incertidumbre.
5. Actualización de los parámetros de laboratorio y de las fuentes meteorológicas cuando haya mejores ensayos locales.
6. Solo después, clasificación de riesgo definida por una variable objetivo, categoría y umbral calibrado; revisión de daños, sensibilidad/especificidad y falsos positivos/negativos.

### Archivos de implementación

- `modelos/mapa_potencial_fitosanitario_ux72.js`: muestreo de contorno y cálculos científicos.
- `assets/oaf-ux35d-mapa-potencial.js`: gestión de fuentes, mapa de puntos y exportación.
- `assets/oaf-ux35d-mapa-potencial.css`: estilos, leyendas y móviles.
- `assets/oaf-ux35-escenarios-multicapas.js`: notificación de redibujado y textos científicos.
- `tests/mapa_potencial_ux72.cjs`: pruebas de matemáticas, georreferencia, faltantes, y proveedor.
- `.github/workflows/mapa_potencial_ux72.yml`: prueba automatizada e integración de API.

**Comprobación:** la prueba de servicio Open-Meteo de GitHub Actions fue satisfactoria para 30/30 ubicaciones, con 30/30 series completas de humedad y 30/30 series completas y aplicables de temperatura en la fecha de ensayo. Esta verificación no representa validación de campo ni garantiza disponibilidad permanente de la API.
