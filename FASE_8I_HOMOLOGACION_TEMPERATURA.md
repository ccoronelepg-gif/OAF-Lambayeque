# Fase 8I — Homologación de observaciones instrumentales de temperatura

**OAF-Lambayeque · 16 de octubre de 2026 · Ing. Agrónomo Carlos Enrique Coronel García**

## Resultado técnico y límite de la evidencia

Se implementaron el importador Python, un inventario de fuentes con huellas SHA-256, controles diarios, agregación mensual estricta y un evaluador descriptivo **estación SENAMHI – ERA5-Land (8D)**. El primer informe real arroja:

- **0 archivos instrumentales térmicos autorizados incorporados**.
- **0 estaciones con fuente Tmedia ingresada; 0 meses homologados; 0 pares temperatura estación–ERA5-Land**.
- **MAE, RMSE y sesgo = no evaluables (null)**.
- `validacion_instrumental_independiente_certificada=false`; `habilidad_prospectiva_8e_demostrada=false`; `intervalos_predictivos_90_calibrados=false`.

**Ninguna cifra sintética de los tests se ha incorporado al observatorio.** Los cinco archivos históricos de estaciones que sí se conservan de SENAMHI son **precipitación mensual 1996–2015**, no temperaturas. La fase 8H sigue siendo su auditoría de procedencia.

## Fuentes científicas e institucionales

1. **SENAMHI**, [Descarga de datos meteorológicos](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos), para consultar series disponibles por estación y variable.
2. **SENAMHI**, [Solicitud oficial de información procesada por estación/variable/periodo](https://www.senamhi.gob.pe/index.php?p=solicitud-servicio). Algunas solicitudes están sujetas a condiciones de acceso y tarifas; **este módulo no presenta servicios de pago como datos gratuitos**.
3. **Copernicus Climate Change Service / ECMWF**, [ERA5-Land hourly](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land), variable temperatura del aire a 2 m.
4. **Muñoz-Sabater et al. (2021)**, «ERA5-Land: a state-of-the-art global reanalysis dataset for land applications», *Earth System Science Data*, 13, 4349–4383, [https://doi.org/10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021).
5. **OMM/WMO**, [WIGOS y metadatos de estaciones](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-integrated-global-observing-system-wigos/key-wigos-publications), criterios de identidad de instrumentos y emplazamientos.

El producto del modelo 8D para Lambayeque es una selección geográfica de celdas del reanálisis. **Una celda es diferente de un termómetro físico en el punto**, especialmente con elevación, costa, uso del suelo o instrumentación distinta. Distancias inferiores a 20 km solo sirven de **criba técnica preliminar**; nunca certifican equivalencia de exposición ni independencia.

## Datos a solicitar e incorporar cuando existan

Para cada estación cercana a Chiclayo, Jayanca, Motupe u Olmos se requieren:

- Código oficial de estación, nombre histórico, tipo de estación (automática/convencional), longitud, latitud, altitud, código WIGOS si existe y fecha efectiva de los metadatos.
- Temperatura máxima y mínima diaria y **temperatura media realmente observada** (mejor: registros horarios con horas y zona), método de cálculo, instrumentación, unidades en °C, banderas de calidad y códigos de ausencia.
- Periodo histórico 1996–2025 si existe y periodo reciente 2026; conservar fechas exactas sin exigir artificialmente continuidad a estaciones que no disponen de ella.
- Fecha de disponibilidad/publicación, procedencia institucional, integridad criptográfica SHA-256, historial de traslados, mantenimiento/cambios del sensor y autorización de tratamiento de los archivos.
- Determinar si una estación participó en la construcción/corrección/forzamiento del producto de reanálisis que se desea evaluar. Sin evidencia no afirmar «validación independiente».

## Pipeline construido

**Archivos de entrada:**

- [Especificaciones y política de publicación](datos/temperatura_senamhi_8i/README.md).
- [Manifiesto de archivos fuente — solo encabezados hasta obtener datos](datos/temperatura_senamhi_8i/manifest.csv).
- [Plantilla CSV diario — solo encabezados](datos/temperatura_senamhi_8i/PLANTILLA_DATOS_DIARIOS.csv).
- Los documentos autorizados se alojarán bajo `datos/temperatura_senamhi_8i/entradas/` o en copias de trabajo privadas autorizadas, nunca se subirán al GitHub público archivos cuya licencia lo prohíba.

**Procesamiento:** [`modelos/homologar_temperatura_senamhi_8i.py`](modelos/homologar_temperatura_senamhi_8i.py).

El código rechaza rutas inseguras, datos sin autorización de publicación de resultados derivados, enlaces institucionales sin HTTPS, SHA-256 modificado, código de estación duplicado/no concordante, tiempos futuros respecto de la publicación del archivo, números faltantes no autorizados y datos geográficos físicamente imposibles. La columna diaria `control_calidad` es `aprobado` o `rechazado` y las ausencias de Tmedia no se reemplazan por cero.

La media diaria debe proceder de un **promedio horario de 24 horas o un método diario documentado y homologado**. Si se dispone solo de Tmax/Tmin, no se inventará Tmedia mediante `(Tmax+Tmin)/2` como si fuese el promedio horario equivalente. Un mes es completo solo con **todos los días calendario** con Tmedia válida y control de calidad aceptado. Meses incompletos no pueden calcular pares, aunque tengan precipitaciones u otras variables.

Para cada mes completo y método uniforme, con metadatos corroborados, el programa revisa la distancia orientativa al punto OAF previamente declarado y, si están los datos correspondientes del modelo 8D, estima:

```
Diferencia (°C) = Tmedia mensual ERA5-Land (celda) − Tmedia mensual SENAMHI (estación)
MAE (°C) = media de |diferencia|
RMSE (°C) = raíz de la media de las diferencias al cuadrado
Sesgo (°C) = media de diferencias con signo
```

Siempre se indican conteos. **Estas métricas evalúan correspondencia reanálisis–estación; no evalúan capacidad predictiva 8E.** El programa nunca cambia las predicciones inmutables 8E ni recalibra el sistema 8G. Un indicador documental del manifiesto no sustituye auditoría independiente; las tablas resultan descriptivas/preliminares.

**Salidas verificadas tras la primera ejecución:**

- [Estado, metadatos y conteos](datos/homologacion_temperatura_8i/estado_8i.json).
- [Pares mensuales y motivos de exclusión](datos/homologacion_temperatura_8i/comparacion_mensual_8i.csv).
- [Panel 8I en Verificación de datos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

## Automatización y controles

Las pruebas de [`tests/test_homologar_temperatura_8i.py`](tests/test_homologar_temperatura_8i.py) utilizan exclusivamente datos **sintéticos en directorios temporales**. Prueban, entre otros, casos completos, fechas duplicadas, días ausentes, ausencia de Tmedia, distancias excesivas, metadatos insuficientes, modificaciones de archivos, fechas de disponibilidad falsas y permisos de publicación.

La acción [`.github/workflows/oaf_temperatura_instrumental_8i.yml`](.github/workflows/oaf_temperatura_instrumental_8i.yml) ejecuta la validación al cambiar las fuentes/código y mensualmente el día 21. Solo guarda los productos de calidad derivados si cambian.

## Próximo desarrollo 8J

**Parte 8J — Homologación de datos horarios y temperatura media según método de estación**, más desarrollo de matrices espaciales por estación–celda/altitud y comparación de sesgos por estación/época; diseño de verificación independiente cuando se disponga de datos autorizados. En paralelo continuar el seguimiento oceánico del Niño Costero y la recolección de datos fitosanitarios reales de arándano y vid, con fuentes científicas e instituciones acreditadas.

Hasta que existan temperaturas instrumentales en la misma ventana temporal que 8E, no se declarará ninguna habilidad prospectiva ni se activarán alertas agronómicas automáticas.
