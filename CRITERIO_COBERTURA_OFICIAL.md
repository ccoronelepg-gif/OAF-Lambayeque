# OAF-Lambayeque | Política transversal de cobertura, calidad y año de corte

**Vigente desde:** 14 de octubre de 2026.  
**Decisión del titular del proyecto:** trabajar hasta **el año más reciente para el que se disponga de datos completos, confiables y de fuentes oficiales**. Nunca llenar, inventar ni interpolar observaciones faltantes para presentar un año como completo.

## Regla metodológica obligatoria

1. **Dato observado:** debe tener fuente institucional identificada, fecha, variable, unidad y estación rastreable. Se distingue del dato de reanálisis o interpolación (PISCOp, CHIRPS, ERA5); estos últimos **no reemplazan** una observación ausente.
2. **Mes completo:** debe tener todos los días calendario del mes con observación válida en la fuente diaria. Si falta al menos un día, el total mensual observado se marca **incompleto / no calculable**, nunca se sustituye con lluvia 0 mm, medias históricas, CHIRPS u otros modelos. Un 0 mm realmente observado sí se conserva como cero.
3. **Año completo de una estación:** exige los **12 meses completos** del mismo año y estación, con 365 o 366 días válidos según calendario, sin duplicados y con unidades e identificación correctas. Solo entonces puede calcularse el acumulado anual observado de esa estación.
4. **Año completo compartido:** para comparaciones regionales entre varias estaciones, cada estación incluida debe disponer de esos 12 meses. El **año límite compartido** será el último año calendario donde todas las estaciones seleccionadas cumplen la condición; puede ser anterior al último año completo de cada estación por separado.
5. **Año de corte dinámico, no 2025 por decreto:** incorporar años más recientes solo cuando existan series oficiales completas y validadas. **La fecha más reciente publicada no equivale al último año completo.** El objetivo puede extenderse más allá de 2025 si hay información nueva y confiable, sin inventar cobertura.
6. **Integridad instrumental:** además de la cobertura matemática, se debe cotejar código de la estación, coordenadas históricas, fechas de operación, control de calidad, horarios de acumulación y cambios de instrumento. El simple hecho de tener 12 meses no acredita por sí mismo continuidad ni independencia frente a productos estimados.
7. **Boletines mensuales:** son evidencia oficial **documental** de los meses que realmente publican, pero no deben transformarse en una serie diaria inexistente. Una colección con 12 PDFs tampoco garantiza 12 acumulados verificables por estación. Mantener las marcas «Traza» sin convertirlas en cero.
8. **Series parciales:** se pueden conservar y mostrar como cobertura pendiente con su fuente, pero **no** utilizar para elaborar acumulados, medias o balances anuales supuestamente completos. En validaciones mensuales exploratorias, solo emplear meses completos realmente observados, declarar el número de meses y prohibir afirmaciones de cobertura anual completa.
9. **Comparación con grillas:** se realiza exclusivamente sobre meses/años observados válidos y coincidentes; los años recientes que solo tengan modelos pero no referencia oficial se identifican como **estimaciones sin validación instrumental externa**.
10. **Sin inventar datos:** ningún script, gráfico, tablero o informe podrá sustituir nulos con cero, promedios, interpolaciones o modelos para aprobar controles de completitud. Las exclusiones siempre quedan registradas.

## Situación comprobada con los archivos diarios SENAMHI originales de 1996–2015

El programa `scripts/control_anios_completos.py` examina el archivo de meses completos `datos/senamhi_mensual_completo_1996_2015.csv`, cuya generación original descarta meses con faltantes diarios.

| Estación | Último año con 12 meses completos de los TXT disponibles |
|---|---:|
| Jayanca (La Viña) | **2012** |
| Cayaltí | **2013** |
| Reque | **2013** |
| Lambayeque | **2013** |
| Cueva Blanca | **2013** |

El **último año completo compartido por las cinco estaciones es 2012**. Hay 11 años calendario completos comunes entre 1996 y 2015: 1996–2003, 2009, 2010 y 2012.

Las fechas posteriores en los TXT pueden contener meses completos aislados, pero **no se deben reportar como años completos**. Los boletines de 2024 y 2025 documentados en las fases 3X–3Y no amplían todavía el último año instrumental completo: falta reconstrucción/cotejo de todas las fechas y continuidad de estación.

**Precisión sobre certificación:** la evaluación anterior verifica cobertura diaria/mensual **de los archivos históricos recibidos de SENAMHI**; la correspondencia exacta de los códigos y los posibles traslados instrumentales aún necesitan fichas oficiales. Por eso se distingue «cobertura temporal completa» de «identidad instrumental oficialmente certificada».

## Implementación técnica

- `scripts/control_anios_completos.py`: control automático, reproducible, sin consultar servicios externos ni modificar la serie base.
- `datos/cobertura_anual_oficial.csv`: año, estación, meses completos y situación de cobertura.
- `datos/acumulados_anuales_completos.csv`: **únicamente** años que reúnen los 12 meses completos de la estación.
- `datos/estado_cobertura_oficial.json`: último año completo por estación, último año completo compartido y limitaciones.
- `.github/workflows/control_cobertura_oficial.yml`: verifica que ningún acumulado anual se calcule con menos de 12 meses.

## Para fases siguientes

En adelante, la página pública, los informes y los modelos utilizarán como **corte instrumental comprobado** el último año completo según el alcance de cada análisis. Cuando exista información confiable posterior, se volverá a calcular automáticamente el corte. **No se completarán observaciones con métodos estadísticos para aparentar cobertura oficial.**
