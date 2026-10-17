# OAF-Lambayeque — Fase 8X: resiliencia ante extremos y material particulado PM₂.₅ / PM₁₀

**Fecha:** octubre 2026. **Ámbito:** Lambayeque; referencias Chiclayo, Jayanca, Motupe y Olmos. **Criterio:** datos trazables y límites científicos explícitos.

## 1. Nuevas variables ambientales

El OAF incorpora dos concentraciones de **material particulado en suspensión**: **PM₂.₅** (partículas con diámetro aerodinámico de hasta 2,5 µm) y **PM₁₀** (hasta 10 µm), ambas en **µg/m³**. No se suman entre sí, porque PM₁₀ incluye la fracción fina. Las partículas pueden relacionarse con resuspensión de polvo por viento, quemas, tránsito, actividades humanas, transporte regional, altura de la capa de mezcla y deposición por lluvia.

La primera fuente descargada realmente es la **salida de composición atmosférica CAMS Global de Open-Meteo Air Quality API**. Son **predicciones/reconstrucciones modeladas de una rejilla atmosférica**, **NO** observaciones de estación certificada SENAMHI, laboratorio ni sensores instalados en campos agrícolas. El servicio CAMS Global Forecast da información global desde 2022, pero la fase 8X limita su primera ingestión a **2023–2025** para evaluar procedencia, calidad y cobertura; **no atribuir cobertura PM a 1996–2025**.

- Motor Python: [`modelos/particulas_aire_8x.py`](modelos/particulas_aire_8x.py).
- Originales gzip y metadatos SHA-256 por sitio-año: [`datos/aire_8x/fuentes/`](datos/aire_8x/fuentes/).
- Matriz mensual, únicamente para meses con cobertura válida: [`datos/aire_8x/particulas_mensuales_8x.csv`](datos/aire_8x/particulas_mensuales_8x.csv).
- Estado real de cobertura, centros de celda y control de series idénticas: [`datos/aire_8x/estado_aire_8x.json`](datos/aire_8x/estado_aire_8x.json).
- Pruebas unitarias: [`tests/test_particulas_aire_8x.py`](tests/test_particulas_aire_8x.py).
- Workflow: [`.github/workflows/oaf_particulas_aire_8x.yml`](.github/workflows/oaf_particulas_aire_8x.yml).

**Controles**: tiempo UTC sin fechas duplicadas, frecuencia horaria/3h, calendario anual, unidades µg/m³ auditadas, concentraciones numéricas finitas no negativas, archivo crudo reproducible con SHA-256, y mes publicable solo si **ambas concentraciones cubren al menos 80 %** de intervalos esperados. No se imputan los meses incompletos.

**Advertencia importante de independencia espacial:** el centro geográfico que devuelve un servicio no siempre significa resolución efectiva distinta. El primer año 2025 mostró series PM₂.₅ y PM₁₀ idénticas para Motupe y Olmos. Se añadió una prueba programática para reportar pares completos de series idénticas y prohibir tratarlas como muestras independientes de partículas.

El módulo de aire es **de vigilancia ambiental exploratoria**. No se usa aún en pronósticos históricos de anomalías 1996–2025: ello exigiría una serie conjunta válida, versionada y con periodos de entrenamiento anteriores a la prueba.

### Referencias y normativa

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api): CAMS Global, variables `pm2_5` y `pm10`, unidades y descripción de resolución/modelos.
- [Copernicus CAMS global reanalysis EAC4](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=overview): posible historia desde 2003, requiere descargar y auditar; **NO se considera integrada**.
- [SENAMHI calidad del aire](https://www.senamhi.gob.pe/main.php?dp=lambayeque&p=calidad-del-aire): se requiere confirmar estación/instrumento/cobertura real de Lambayeque, no reutilizar series de Lima como si fueran de la región.
- [MINAM D. S. 003-2017-MINAM](https://www.gob.pe/institucion/minam/normas-legales/3670-003-2017-minam): normativa peruana de estándares de aire (ECA). **Una media mensual CAMS global no demuestra cumplimiento ni infracción de estándares definidos para periodos/metodologías regulados.**
- [EPA: conceptos básicos de PM](https://espanol.epa.gov/espanol/conceptos-basicos-sobre-el-material-particulado-pm-por-sus-siglas-en-ingles).

### Relación agrícola que queda por contrastar

El material particulado podría utilizarse para caracterizar deposición superficial y polvo, pérdida de radiación incidente, condiciones de trabajo e interacciones con viento y precipitación. La presencia de partículas **no implica enfermedad vegetal**, ni equivale a conidios o esporas fúngicas ni al diagnóstico de *Botrytis*, oídio u otros patógenos. El muestreo de aerosoles, deposición en hojas, fenología y evaluaciones fitosanitarias sigue pendiente. La TSM, las corrientes y los vientos del OAF permanecen separados por fuente y resolución.

## 2. Evaluación de extremos 2017 y 2023

En paralelo, el motor [`modelos/auditoria_extremos_8x.py`](modelos/auditoria_extremos_8x.py) analiza los errores que YA emitió el experimento retrospectivo 8W en los años **2017 y 2023**, separando la temporada enero–abril de mayo–diciembre. No se reentrenan modelos mirando sus errores; se mantienen exactamente los pronósticos y fechas originales del backtest. Se auditan 4 localidades, 2 objetivos, 5 modelos, 3 horizontes, 2 años y 2 periodos = **480 grupos de error MAE**, con meses completos.

**Comparación exploratoria de MAE de lluvia enero–abril a horizonte 1 mes (mm, ERA5 reanálisis, solo 4 meses por año):**

| Sitio | Año | Ridge local | Ridge local + viento + SST | Resultado |
|---|---:|---:|---:|---|
| Chiclayo | 2017 | 96,37 | 89,25 | Mejora |
| Chiclayo | 2023 | 88,32 | 85,72 | Mejora |
| Jayanca | 2017 | 210,25 | 205,82 | Mejora |
| Jayanca | 2023 | 194,92 | 159,85 | Mejora |
| Motupe | 2017 | 260,06 | 283,09 | Empeora |
| Motupe | 2023 | 209,89 | 181,11 | Mejora |
| Olmos | 2017 | 231,83 | 234,75 | Empeora |
| Olmos | 2023 | 146,14 | 135,36 | Mejora |

La aparente mejora con SST y viento en algunos sectores **no valida pronóstico de lluvias extraordinarias**: solo cuatro meses por periodo y valores de precipitación del reanálisis, NO estaciones. En Motupe y Olmos **empeora en 2017**, demostrando que no hay regla regional universal.

**El Niño de 1997–1998 NO es un evento validado fuera de muestra en el diseño 8W**, porque aparece en entrenamiento. Los registros ERA5 elevados detectados en Motupe en marzo de 1998 requieren cotejo instrumental, no descarte arbitrario.

- Reporte ejecutado: [`datos/extremos_8x/estado_extremos_8x.json`](datos/extremos_8x/estado_extremos_8x.json).
- Serie auditada por año, época, objetivo, localidad y modelo: [`datos/extremos_8x/error_extremos_2017_2023_8x.csv`](datos/extremos_8x/error_extremos_2017_2023_8x.csv).
- Tests: [`tests/test_auditoria_extremos_8x.py`](tests/test_auditoria_extremos_8x.py).
- Automatización: [`.github/workflows/oaf_auditoria_extremos_8x.yml`](.github/workflows/oaf_auditoria_extremos_8x.yml).

## 3. Portal e interpretación

[Verificaciones OAF](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones) incluye el panel **Fase 8X · Material particulado PM₂.₅ y PM₁₀**. Permite elegir localidad, contaminante, año climático de comparación y horizontes con gráficos y errores. Fuentes y banderas de calidad quedan a disposición pública. **Ningún valor modelado es alerta sanitaria, declaración de calidad normativa o recomendación de fitosanitarios.**

## 4. Próximo paso 8Y

1. Probar una historia aerosol **más extensa (2003–2025 CAMS EAC4 o MERRA-2)**, con conversión física/unidades y máscara topoclimática, no asumir acceso libre a miles de valores sin descargar.
2. Controlar similitudes o independencia espacial efectiva de PM entre Motupe/Olmos y otras zonas; contrastar con estaciones PM reales de Lambayeque si existen datos abiertos verificables.
3. Calcular correlaciones de PM con viento, lluvia, humedad y radiación solo en meses coincidentes, sin aseveraciones causales.
4. Comparar objetivos de extremos por cinco cortes, separado por época del año, e incorporar variables PM a modelos predictivos **solo si se demuestra cobertura histórica adecuada y mejora fuera de muestra**.
5. Ampliar muestreo de zonas homogéneas diferenciando costa, valles intermedios, piedemonte y sierra; contrastar con SENAMHI, ENFEN, IMARPE, SENASA y datos de campo.

**Dictamen:** fase 8X produce vigilancia experimental de material particulado y auditoría de residuos climáticos, sin habilitar alarmas operativas.
