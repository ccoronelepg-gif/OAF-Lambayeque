# OAF-Lambayeque — Reanudación fase 8W, octubre 2026

## Estado real

Fase **8W implementada en repositorio público**, no solo diseñada. Motor:
`modelos/benchmark_multivariable_8w.py`. Tests:
`tests/test_benchmark_multivariable_8w.py` (8 pruebas sintéticas). Workflow:
`.github/workflows/oaf_benchmark_multivariable_8w.yml`.
Resultados reales archivados en `datos/benchmark_8w/`:
`predicciones_mensuales_8w.csv`,
`probabilidades_lluvia_p90_8w.csv`,
`sensibilidad_corrientes_8w.csv`,
`estado_benchmark_8w.json`.
Reporte `FASE_8W_BENCHMARK_MULTIVARIABLE.md`.
Panel visible `index.html`, id `oaf-benchmark-8w`, JS `modelos/visor_benchmark_8w.js`, dentro de [Verificación de datos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones). El panel compara MAE, RMSE y Brier, con filtros e incluye gráfico de ganancia/pérdida a través de cinco cortes.

Última corrida validada antes de la gráfica nueva:
https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39004443117
con todas las etapas exitosas. Posteriormente se añadió un gráfico SVG de cinco cortes y la prueba de existencia DOM; verificar la última corrida de CI tras commit correspondiente.

## Diseño y datos

Matiz de **1.440 meses-localidad** ERA5, ERA5-Land, ERA5 viento y SST Niño1+2/Niño3.4 NOAA revisadas, 1996–2025, Chiclayo/Jayanca/Motupe/Olmos. Cinco cortes forward 2011–2013, 2014–2016, 2017–2019, 2020–2022, 2023–2025 con entrenamiento anterior. Horizonte h=1/2/3 meses. Cada fold reconstruye climatologías, transformación log1p de lluvias, escalados y P90 solo con datos de entrenamiento.

Comparadores: climatología mensual, persistencia, Ridge local, Ridge local + viento ERA5, Ridge local + viento + SST Niño1+2/Niño3.4. Para lluvia P90 enero–abril, logística regularizada con evaluación Brier y climatología de eventos aprendida en train. Solo investigación: NOAA no son vintages fecha-emisión, reanálisis no es estación SENAMHI. Corrientes NOAA/AOML GEOSTRÓFICAS no corrientes totales; su reanálisis desde 2017 se evalúa por separado con entrenamiento 2017–2022, prueba 2023–2025 y sitios marinos no colocalizados.

## Resultados validados

- **21.600 predicciones continuas** combinaciones modelo × fecha × objetivo × horizonte × localidad; **2.880 estimaciones probabilísticas** combinaciones modelo × fecha evento; **1.728** predicciones del subexperimento de corrientes, sin independencia estadística.
- En comparación agrupada 2011–2025, SST+viento mejora MAE local en **11/12** combinaciones de temperatura y **11/12** de precipitación.
- Mejora en al menos 3/5 cortes: 9/12 temperatura, 11/12 precipitación. Mejora en ≥4/5 cortes: 4/12 temp, 6/12 precipitación. Esto NO demuestra robustez universal ni causalidad.
- A un mes: Motupe T local 0,341520°C / con viento+SST 0,336764°C; Olmos T local 0,331983°C / océano+viento 0,333740°C (empeora); Motupe lluvia 47,548796 / 45,689133 mm; Jayanca lluvia 39,534967 / 36,796392 mm; Chiclayo lluvia 10,444918 / 10,018625 mm.
- Brier de evento lluvia P90, SST+viento mejora climatología en **8/12** combinaciones; Motupe 1 mes Brier climatología 0,07965204 / océano 0,06547514, 5 eventos/60 meses test.
- Corrientes: variante con u/v geostróficas mejora MAE en **8/24** comparaciones y RMSE en **4/24**; no activar operacionalmente.
- 1998 extremo ENSO se incorpora al training de todos los cortes, NO hay prueba independiente de capacidad ante repetición 1997–1998. Hay 11 meses-sitio de ERA5 ≥1000 mm sin verificación SENAMHI; Motupe marzo 1998 2913,8 mm MODELADOS.
- Modelo evalúa 4 centros de cuadrícula, no todos los pisos ecológicos de Lambayeque; zonas físicas homogéneas SIG certificadas siguen cero.

## Siguiente fase 8X

Priorizar diagnóstico de residuos en 2017 y 2023, sensibilidad a exclusión de 1997–1998 del entrenamiento, métricas en años de evento, intervalos temporales emparejados por bloques para comparar modelos, consistencia por estación y reducción de falsas señales; ampliar muestreo a 79 referencias/55 celdas regiones 8P/8S y estaciones reales SENAMHI antes de delimitar zonas homogéneas. Explorar productos oceanográficos satelitales/grillados colocalizados más largos NASA OSCAR o Copernicus Marine para corrientes, sin mezclar físicamente viento en tierra y mar. Reservar alertas fitosanitarias hasta observaciones verificadas de arándano/vid (Botrytis, oídio, etc.).

**Regla:** No pedir cuestionarios al usuario. Continuar desarrollando código real, citando fuentes científicas, no declarar pronósticos operativos, El Niño Costero anticipado, ni enfermedad sin verificación.
