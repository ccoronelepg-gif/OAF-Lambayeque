# Parte 8M — Sensibilidad geográfica de la temperatura de ERA5-Land en Lambayeque

**Observatorio Agroclimático y Fitosanitario OAF-Lambayeque**  
**Fecha de diseño del ensayo:** 16 de octubre de 2026.  
**Líneas vinculadas:** predicción de anomalías agroclimáticas, Niño Costero y bases para futuras evaluaciones fitosanitarias en arándano y vid.

## 1. Hipótesis y alcance

La fase 8L estableció que **dos preferencias de selección de celda de Open-Meteo (`land` y `nearest`) daban las mismas temperaturas** para las cuatro coordenadas fijas analizadas.

La fase 8M aborda una pregunta diferente: **¿cuánto cambian las temperaturas históricas y sus anomalías al desplazar sistemáticamente las coordenadas de consulta unos kilómetros alrededor de cada localidad?**

La evaluación es histórica y espacial, nunca validación instrumental. No representa predios agrarios, termómetros SENAMHI, infecciones vegetales ni estimaciones de habilidad prospectiva de los modelos OAF 8E.

## 2. Diseño espacial previo a los resultados

Se fijan **nueve puntos por localidad**, con el centro original de los datos 8D/8L y ocho desplazamientos:

| Rumbo | ΔLatitud (°) | ΔLongitud (°) |
|---|---:|---:|
| Centro (C) | 0 | 0 |
| Norte (N) | +0,05 | 0 |
| Sur (S) | −0,05 | 0 |
| Este (E) | 0 | +0,05 |
| Oeste (W) | 0 | −0,05 |
| Noreste (NE) | +0,05 | +0,05 |
| Noroeste (NW) | +0,05 | −0,05 |
| Sureste (SE) | −0,05 | +0,05 |
| Suroeste (SW) | −0,05 | −0,05 |

La distancia métrica real de 0,05° depende de la dirección y la latitud. Se calcula y archiva mediante la fórmula geodésica de Haversine. **No se asume que cada rumbo sea exactamente igual en kilómetros.**

Ámbito original: Chiclayo (-6,77140; -79,84090), Jayanca (-6,39278; -79,82280), Motupe (-6,15083; -79,71420) y Olmos (-5,98825; -79,74723). Son referencias urbanas/regionales, no parcelas de producción.

**Diseño previsto:** 4 localidades × 9 posiciones = **36 puntos**. Para cada posición se requieren 360 meses completos de 1996–2025. La comparación vecino–centro produce, si todas las fuentes están disponibles, **11.520 pares mensuales** (4 × 8 × 360), además de 1.440 meses base de los centros.

## Resultados instrumentados al primer corte (16/10/2026)

La API limitó temporalmente nuevas consultas con HTTP 429. Por ello, la adquisición se reparte en **un máximo de dos bloques decenales por ejecución programada** y el resumen regional se mantiene pendiente hasta contar con los 12 bloques de las cuatro localidades.

Ya se obtuvieron seis bloques íntegros, equivalentes a **360 meses completos en Chiclayo y Jayanca**. La comparación produce **18 puntos y 5.760 pares mensuales vecino–centro**; **Motupe y Olmos siguen pendientes**.

| Indicador descriptivo de reanálisis | Chiclayo | Jayanca |
|---|---:|---:|
| Vecinos con otro píxel de Open-Meteo | 5/8 | 5/8 |
| Mayor MAE de Tmedia vecino–centro por rumbo | 0,59889 °C | 0,63055 °C |
| Máxima diferencia absoluta mensual | 1,12333 °C | 1,47500 °C |
| Mayor MAE de diferencias de anomalía por rumbo | 0,11058 °C | 0,11376 °C |

En Chiclayo, al desplazar el punto **al oeste**, el píxel cambió y la diferencia media fue aproximadamente **−0,563 °C**; al desplazarlo al norte, el píxel también cambió y la diferencia media fue aproximadamente **+0,596 °C**. En Jayanca, el desplazamiento **al noroeste** presentó un MAE de **0,63055 °C**.

**Hallazgo metodológico adicional:** algunos puntos que mantuvieron **la misma celda informada** también presentaron diferencias térmicas menores, congruentes con que la API utiliza un ajuste espacial/elevacional adicional. No atribuir estas diferencias exclusivamente a la selección de celda ni a un gradiente térmico físico sin un nuevo ensayo con downscaling desactivado.

Todos estos indicadores son **sensibilidad espacial del reanálisis**, no errores de temperatura respecto a SENAMHI ni medición fitosanitaria. El estado actualizable debe consultarse en [`estado_8m.json`](datos/sensibilidad_vecindad_8m/estado_8m.json), pues el número de localidades completas aumentará con los nuevos bloques verificables.

## 3. Datos, proveedores y precaución sobre elevación

La fuente elegida es el conjunto **ERA5-Land** a través de **Open-Meteo Historical Weather API**. Para conservar compatibilidad con la etapa anterior 8L se mantienen:

- `models=era5_land`, **sin mezclar ERA5 ni otros modelos**.
- `daily=temperature_2m_mean`, temperatura media diaria del aire a 2 m en °C.
- `timezone=America/Lima`.
- `cell_selection=land`, valor predeterminado del proveedor.
- Ajuste de elevación **predeterminado del proveedor**, sin modificar `elevation`.
- Periodo fijo 1996–2025 en bloques 1996–2005, 2006–2015 y 2016–2025.

Son **12 solicitudes** (4 localidades × 3 décadas), cada una con 9 posiciones. Se conservan las 12 respuestas JSON completas comprimidas, sus URL, instante de consulta UTC y huellas SHA-256. Las series solo se publican cuando son completas y pasan las comprobaciones.

**Limitación crucial:** cuando se solicita una ubicación distinta, Open-Meteo puede modificar tanto la celda seleccionada como el ajuste estadístico asociado a la elevación calculada a partir de un modelo digital de 90 metros. Por consiguiente, la diferencia de temperatura obtenida mide **sensibilidad conjunta del procedimiento completo de consulta** y no puede atribuirse causalmente solo al relieve ni al cambio de celda. Tampoco equivale al valor bruto de una celda sin downscaling de CDS.

Fuentes institucionales:
- [Open-Meteo, Historical Weather API y parámetros de celda/elevación](https://open-meteo.com/en/docs/historical-weather-api).
- [Copernicus/ECMWF, ERA5-Land hourly](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land), resolución en la grilla CDS de 0,1° × 0,1°, sobre datos modelados de reanálisis.
- Muñoz-Sabater et al. (2021), *ERA5-Land: a state-of-the-art global reanalysis dataset for land applications*, Earth System Science Data 13, 4349–4383, DOI [10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021).

## 4. Indicadores de calidad y sensibilidad

Para cada punto desplazado `p` y el centro `C`, en el mismo mes `t`:

`ΔT(p,t) = T(p,t) − T(C,t)`.

Se calculan por posición: diferencia media, MAE entre series, RMSE entre series, máximo absoluto de ΔT, número de meses con `|ΔT| ≥ 0,5 °C` y `|ΔT| ≥ 1 °C`. Los umbrales son **descriptivos y exploratorios**, no son umbrales fitosanitarios, ENFEN ni de emisión de alertas.

Para las anomalías se calcula una **normal distinta para cada posición y mes calendario** utilizando 30 años completos (1996–2025), después:

`Anomalía(p,t) = T(p,t) − Normal(p,mes(t))`.

La sensibilidad de anomalías es:

`ΔA(p,t) = Anomalía(p,t) − Anomalía(C,t)`.

Esto permite distinguir diferencia media sistemática del sitio respecto de diferencia en comportamiento anómalo. También se guardan latitud/longitud solicitadas, coordenadas de celda devueltas, distancia entre centros de celda, elevación **reportada por la API** y sus diferencias con el centro.

**Regla de calidad esencial:** el centro descargado nuevamente debe reproducir los 360 valores mensuales reales archivados en la fase 8L por localidad (tolerancia de redondeo 0,00003 °C). Si no ocurre, la nueva comparación se rechaza y se solicita auditoría del proveedor.

## 5. Código, controles y datos publicados

- [Motor de adquisición, auditoría y comparación](modelos/sensibilidad_vecindad_8m.py).
- [Pruebas sintéticas aisladas](tests/test_sensibilidad_vecindad_8m.py). Los datos artificiales solo se emplean en carpetas temporales de validación; nunca se presentan como temperaturas observadas.
- [Workflow de GitHub Actions](.github/workflows/oaf_sensibilidad_vecindad_8m.yml).
- [Reporte de estado y trazabilidad](datos/sensibilidad_vecindad_8m/estado_8m.json).
- [CSV por punto y rumbo](datos/sensibilidad_vecindad_8m/puntos_8m.csv).
- [CSV vecino–centro por mes](datos/sensibilidad_vecindad_8m/pares_mensuales_8m.csv).
- [JSON ligero para visualización](datos/sensibilidad_vecindad_8m/vista_8m.json).
- [Fuentes originales comprimidas y metadatos](datos/fuentes_vecindad_8m/), sujeto a disponibilidad y respuesta de la API.
- [Visor público de la fase 8M](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones), pestaña **Verificación de datos**.

La acción automatizada se activa ante cambios de código y mensualmente. Si faltan fuentes, se muestran **únicamente localidades que cuentan individualmente con los tres bloques completos y 360 meses**; nunca se presenta la región como finalizada hasta reunir las cuatro localidades. No se mezclan fuentes sintéticas ni se imputan meses.

## 6. Interpretación científica y continuidad

El resultado determina **sensibilidad espacial del producto de reanálisis/procedimiento de consulta**, no precisión respecto de termómetros ni capacidad predictiva del OAF para anticipar anomalías o enfermedades.

El siguiente trabajo depende del hallazgo: estudiar dónde se producen cambios de celda o contrastes sustanciales entre centro y vecinos, y verificar con datos externos cualquier interpretación sobre costa, altitud y agricultura real. Una etapa adicional puede usar `elevation=nan` para aislar el remuestreo de píxel del ajuste por elevación, con un diseño comparable. Ello requerirá nuevas fuentes históricas completas, sin asumir que las medidas de SENAMHI ya están disponibles.

Se mantienen vigentes el proyecto climatológico 1996–2025, la normal OMM 1991–2020 para comparabilidad cuando exista cobertura, la vigilancia oficial ENFEN y las líneas fitosanitarias de arándano y vid.
