# OAF-Lambayeque · Fase 8A: archivo prospectivo y verificación de anomalías oceánicas Niño 1+2

**Responsable:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Primera emisión verificada:** 15 de octubre de 2026, horario de Perú.  
**Estado:** investigación con archivo inmutable de predicciones experimentales. **No es ICEN oficial ni pronóstico operativo validado de El Niño Costero.**

## 1. La línea climática continúa en paralelo

Mientras se consiguen evaluaciones reales de *Botrytis* en arándano (Fase 7C, estado real `sin_datos_campo`), el OAF continuará la **predicción de anomalías climáticas regionales y evolución oceánica relacionada con El Niño Costero**. La validación de condiciones meteorológicas, la de anomalías oceánicas y la de enfermedad son tareas científicas diferentes.

El trabajo 6D detectó NOAA NCEI ERSSTv5 para Niño 1+2 (hasta septiembre 2026), con anomalías originales respecto de 1971–2000, y recalculó una referencia mensual 1991–2020 para comparabilidad. Se conservan la fuente, la transformación y el control cruzado con un archivo NOAA CPC. Esta serie derivada **no se denomina ICEN oficial**.

**Referencias institucionales**:
- [ENFEN/IMARPE: definición del ICEN](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen). Desde la actualización publicada por ENFEN en 2024, el ICEN operacional se basa en promedio móvil de tres meses de ERSSTv5 Niño 1+2 (base 1991–2020). Las categorías y comunicados oficiales corresponden a ENFEN.
- [NOAA NCEI: ERSSTv5 Niño 1+2, archivo original](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat) y [Readme](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/Readme).
- [NOAA CPC: archivos de índices oceánicos y actualizaciones](https://www.cpc.ncep.noaa.gov/data/indices/Readme.index.shtml). La publicación de datos normalmente se realiza hacia el día 10 de cada mes, pero **nunca se presupone que una observación existe solo por transcurrir esa fecha**.

## 2. Problema metodológico resuelto

**Una reconstrucción histórica no demuestra que el modelo podía haber emitido ese resultado antes del evento.** Por eso implementamos una evaluación verdaderamente prospectiva con dos garantías:

1. **Congelación de pronósticos con hora de emisión**. El archivo guarda exactamente qué predecía el OAF en esa fecha y los hash SHA-256 de los datos usados. No se modifica si NOAA revisa meses pasados o si el algoritmo cambia.
2. **Verificación después de disponer de observaciones**. Las predicciones se comparan con las anomalías NOAA disponibles en el archivo mensual **no antes del día 10 del mes siguiente al periodo objetivo**, y solo si el valor realmente existe. Se registran diferencias frente al AR(1) y a la persistencia.

**Distinción crítica**:
- `estimacion_intramensual_nowcast`: se emitió **después de que comenzó** el mes objetivo. No cuenta para calcular habilidad pronosticando meses todavía no iniciados.
- `pronostico_previo_al_mes`: se emitió **antes del día 1** del mes objetivo. Este sí podrá contar en un análisis prospectivo de pronósticos mensuales, una vez disponible la observación posterior.
- Ninguno de estos dos tipos equivale a la clasificación de El Niño Costero ni una predicción probabilística calibrada.

La verificación posterior usa datos **ERSSTv5 revisables**. Los resultados indicarán explícitamente que no son mediciones independientes directas del océano ni equivalencia con el ICEN publicado por ENFEN.

## 3. Primera emisión real, sellada 15/10/2026

**Observación oceanográfica de origen:** anomalía NOAA NCEI Niño 1+2 reajustada por el OAF para septiembre 2026: **+4,38867 °C**, que se redondea a +4,389 °C.

| Mes objetivo | Modelo AR(1) experimental | Persistencia | Estado de emisión | Primera fecha permitida de evaluación |
|---|---:|---:|---|---|
| Octubre de 2026 | **+4,054 °C** | +4,389 °C | **Estimación intramensual** (emitida el 15/oct) | 10/11/2026 |
| Noviembre de 2026 | **+3,744 °C** | +4,389 °C | **Pronóstico anterior al mes** | 10/12/2026 |
| Diciembre de 2026 | **+3,456 °C** | +4,389 °C | **Pronóstico anterior al mes** | 10/01/2027 |

**Resultado de la primera ejecución GitHub Actions:**
- Archivo guardado: [datos/pronosticos_oceanicos_emitidos/2026-09.json](datos/pronosticos_oceanicos_emitidos/2026-09.json), una copia inmutable vinculada al mes de origen 2026-09.
- Hora exacta: **2026-10-15T05:53:43+00:00**, equivalente al 15/10/2026 a las **00:53:43 en Perú**.
- Pronósticos almacenados: **3** (dos anteriores al mes y una estimación intramensual).
- Comparaciones ya realizadas: **0**. Es la situación correcta porque ninguno de los meses objetivo había finalizado con su fecha mínima de control.
- [Estado de verificación JSON](datos/verificacion_oceanica_8a.json): `pendiente_maduracion_oceanica`. [CSV de verificaciones](datos/verificacion_oceanica_8a.csv) únicamente con encabezados.

**Esta fase no ha acertado ni fallado aún frente a los valores futuros: esa información todavía no existe.**

## 4. Integridad y trazabilidad

El motor [modelos/auditoria_oceanica_8a.py](modelos/auditoria_oceanica_8a.py) implementa:
- Esquemas y unidades conocidas; valida origen, últimos registros disponibles, cálculos numéricos y base climática.
- Archivo **append-only** `datos/pronosticos_oceanicos_emitidos/AAAA-MM.json`: un archivo por último mes efectivamente observado, sin sobrescribir la primera emisión.
- Hash SHA-256 del JSON del modelo y CSV histórico utilizados, más hora UTC y hora local.
- Control de vigencia que **solo admite un nuevo pronóstico si el último mes NOAA corresponde al mes inmediatamente anterior al actual**; si la fuente está rezagada, no genera una emisión nueva falsa.
- Tres horizontes de uno, dos y tres meses y dos referencias: AR(1) y persistencia. El AR(1) **todavía no demostró superar consistentemente la persistencia en la evaluación reciente**, como ya se documentó en Fase 6D.
- Verificación con tabla de errores cuando exista mes observado maduro; MAE comparativos calculados **por horizonte y solo sobre emisiones anteriores al inicio del mes**. Resultados con pocas emisiones se mantienen exploratorios.
- `validacion_operativa=false`, `es_icen_oficial=false`, `es_alerta_enfen=false` incluso después de una comparación parcial.

**Pruebas automáticas aprobadas**: cambio diciembre→enero, cómputo de meses objetivo, distinción de octubre emitido a mitad de mes frente a noviembre/diciembre emitidos antes del inicio, rechazo de ICEN etiquetado falsamente y latencia al mes siguiente.

**Actualización:** [flujo GitHub Actions](.github/workflows/oaf_auditoria_oceanica_8a.yml) programado los días 12, 19 y 26 de cada mes y cuando cambia el modelo de origen o sus observaciones; registra nuevas emisiones y verifica únicamente predicciones cuyos datos maduraron.

## 5. Interfaz y buenas prácticas

En el observatorio, [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino), hay un nuevo panel plegable «**Fase 8A · Pronósticos oceánicos archivados antes del evento**» que muestra:
- Mes previsto, valor experimental y persistencia.
- Etiqueta intramensual o realmente prospectiva.
- Estado observado/no observado y primera fecha de evaluación.
- Fuente de los cálculos y enlaces a los registros originales.

El diseño autorizado de Inicio —recuadro verde solo con título y dos fotografías, descripción y firma fuera—, las cinco pestañas y los módulos de arándano/vid permanecen intactos.

## 6. Próxima fase oceánico-atmosférica 8B

El AR(1) es un **punto de comparación**, no una solución definitiva. La Fase 8B debería:
1. Incorporar predictores del Pacífico ecuatorial con serie, metodología y fecha de disponibilidad verificables: **viento zonal, presión / Índice de Oscilación del Sur y contenido de calor subsuperficial**, y evaluar si agregan capacidad de anticipación de Niño 1+2.
2. Comparar modelos contra persistencia, climatología cero y los productos institucionales de ENFEN, manteniendo fija la frontera de información disponible **en la fecha de emisión**.
3. Producir resultados en horizontes de **1–3 meses**, intervalos de incertidumbre evaluados, y verificación en un conjunto no empleado para calibración. No llamar «predicción validada» al modelo por un único buen trimestre.
4. Estudiar la relación temporal Niño 1+2 ↔ temperatura/precipitación/radiación en Lambayeque usando el periodo histórico **1996–2025**, sin inferir causalidad automática ni emitir probabilidades de inundación.
5. Integrar boletines oficiales ENFEN como señal institucional y fuente de contexto, claramente diferenciados de todas las proyecciones exploratorias propias.

La línea fitosanitaria avanzará cuando lleguen datos de campo; el desarrollo de modelos climáticos y vigilancia oficial **no necesita detenerse durante esa recopilación**.
