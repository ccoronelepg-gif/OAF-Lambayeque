# OAF-Lambayeque · Reanudación fase 8S · 17/10/2026

## Estado ejecutado y materializado en GitHub

Se implementó fase **8S**: validación de anomalía térmica mensual a un mes vista en una muestra regional más extensa, mediante las fuentes originales ERA5-Land de las fases 8O/8P. Portal: https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones. Repositorio: https://github.com/ccoronelepg-gif/OAF-Lambayeque.

- Al comenzar 8S, **67** testigos con clima multivariable completo en las etapas 8O/8P. Se excluyeron preventivamente **2** puntos con DEM ≤5 m por riesgo costero no revisado cartográficamente. Se analizaron **65 testigos**, que corresponden a **50 centros únicos ERA5-Land**; 15 consultas duplican centros. Estos números son un corte del inventario: 8P sigue descargando hasta 81 cuando el proveedor lo permita; ver `datos/clima_contiguo_8p/estado_clima_8p.json`.
- Evaluación rolling origin con **cinco particiones**, sin superposición entre los años reservados del test: entrenamiento 1997–2008, 1997–2011, 1997–2014, 1997–2017, 1997–2020; validación 2009–2011, 2012–2014, 2015–2017, 2018–2020, 2021–2022; prueba 2012–2014, 2015–2017, 2018–2020, 2021–2022, 2023–2025. Las normales térmicas propias del sitio se recalculan en cada corte con **1996–fin entrenamiento**.
- Se compararon anomalía climática cero, persistencia local t−1, señal regional t−1 excluyendo celda objetivo y ridge jerárquico combinando t−1 local/regional. El modelo se selecciona solo con el periodo de validación anterior al test. En los cinco cortes fue seleccionado **jerárquico**.
- **8.400 resultados temporales** y **8.400 con bloque espacial retenido** = 50 centros únicos × 168 meses de prueba 2012–2025.
- **RMSE test temporal 0,448275 °C**, persistencia 0,468228 °C y normal mensual 0,878651 °C; skill vs persistencia **+4,2614 %**.
- **RMSE test espacial (cuatro franjas latitudinales retenidas en ajustes y selección) 0,448167 °C**, persistencia 0,468228 °C y normal 0,878651 °C; skill vs persistencia **+4,2845 %**.
- Para control geográfico los 50 centros se distribuyen en **cuatro bandas norte-sur equilibradas por cantidad de celdas**, no son cuencas ni polígonos oficiales. Se dejan sin entrenar los coeficientes de la franja retenida, y el predictor regional de los demás excluye las celdas de esa franja. **Sí se permite climatología histórica propia 1996–fin entrenamiento y señal térmica t−1 de la franja retenida**, por lo que NO se prueba capacidad en ubicaciones sin series locales.
- Por estrato altitudinal test espacial, RMSE modelo/persistencia y skill: llanura 0,566437/0,583587 °C +2,94%; valle 0,476122/0,497628 +4,32%; piedemonte 0,413984/0,434353 +4,69%; montaña baja 0,361147/0,381327 +5,29%; montaña media 0,321652/0,348482 +7,70%; montaña alta 0,330746/0,361974 +8,63%. No afirmar significación causal o habilidad operativa por piso sin estaciones y pruebas adicionales.
- **0 estaciones térmicas SENAMHI de validación independiente integradas**, **0 predicciones prospectivas operativas validadas**, **0 zonas agroclimáticas homogéneas cartografiadas y certificadas**. ENSO/ENFEN, radiación, precipitación, fitopatología de arándano/vid no fueron predictores del experimento. Las series objetivos provienen de ERA5-Land, mismo reanálisis de predictores.

## Artefactos
- `modelos/validacion_regional_8s.py`: carga fuentes 8O/8P con SHA, agrupa 1996–2025 en meses, descarta DEM≤5, deduplica centros, cinco cortes, cuatro franjas, valida t−1, calcula predicciones y métricas.
- `tests/test_validacion_regional_8s.py`: 11 pruebas aisladas de ventanas, sin fuga temporal, duplicados, reporte de skill negativo y retención geográfica.
- `.github/workflows/oaf_validacion_regional_8s.yml`: CI, --check, commit de productos de evaluación y verificación HTML y JS.
- `datos/validacion_regional_8s/estado_validacion_8s.json`, `predicciones_temporales_8s.csv`, `predicciones_bloques_8s.csv`: resultados del experimento real.
- `FASE_8S_VALIDACION_REGIONAL.md`: método y tablas completas, cautelas.
- `modelos/visor_regional_8s.js` y `index.html`: panel 8S en #verificaciones, tablas por corte, altura y bloques espaciales.

## Próxima fase 8T

1. Completar muestreo 8P hacia 81 testigos, nueva evaluación 8S sin ocultar cuánto cambian los resultados al ampliar cobertura.
2. **Validación instrumentada SENAMHI** real: hallar/recuperar metadatos de estaciones, fechas y observaciones térmicas; comparar error reanálisis vs instrumento y calibración local, sin inventar códigos.
3. **Ensayos prospectivos archivados antes del mes objetivo** con horizonte de disponibilidad real de ERA5-Land; comparar 1 mes de anticipo frente a persistencia climática.
4. Incorporar modelos más relevantes para Niño Costero, con información oceánica Niño 1+2 y T300, ENFEN boletines oficiales, variables meteorológicas lluvia/radiación/humedad, valores disponibles t−1 o predictores estacionales archivados; sin fuga temporal.
5. Homogeneidad por ambientes requiere cartografía oficial INEI/IGN de tierra/agua, cuencas, exposición de laderas y gradientes; no usar bandas latitudinales como zonas agrícolas oficiales ni emitir riesgo fitosanitario arándano/vid sin incidencia de campo.

**Preferencia de ejecución**: realizar trabajo real en GitHub, comunicar avances y resultados rigurosos, no pedir al usuario cuestionarios ni ejercicios.
