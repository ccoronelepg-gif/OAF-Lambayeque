# OAF-Lambayeque — Reanudación fase 8P (octubre 2026)

## Proyecto y meta

Proyecto activo real: https://github.com/ccoronelepg-gif/OAF-Lambayeque y sitio https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones. Objetivo regional: **identificar áreas agroclimáticas homogéneas de Lambayeque**, integrando altitud, valles, relieve, costa y series 1996–2025 de temperatura (Tmean/Tmax/Tmin), precipitación, humedad y radiación; posteriormente validar y predecir anomalías y desarrollar vigilancia fitosanitaria de arándano/vid y monitoreo El Niño Costero con ENFEN.

**No afirmar** que un estrato altitudinal, un conglomerado no contiguo, un par de centros de rejilla ni los 420 puntos DEM conforman zonas climáticas certificadas o que OAF demostró habilidad predictiva regional.

## Fase 8P desarrollada en rama main

### Diseño y cifras verificadas
- **420 nodos DEM de 8O** en polígono simplificado secundario de Lambayeque (no capa INEI/IGN oficialmente validada).
- **62 nuevos testigos 8P**, diferentes de los 19 anteriores: planicie 10, valle 10, piedemonte 12, ladera baja 10, ladera media 8, alta montaña 12. Se excluyeron nuevos testigos con DEM <=5 m por precaución costa/tierra, no porque se haya comprobado que sean agua.
- **1.244 aristas de cercanía geométrica <=8,5 km** entre los 420 nodos, SOLO proximidad; no equivale a homogeneidad/clúster validado.
- 19 testigos previos de 8O con clima 1996–2025 completo. 62 nuevos ordenados en cuatro grupos de 16,16,16,14, cada uno con dos modelos (ERA5-Land temperaturas; ERA5 humedad, lluvia, radiación) × tres décadas, **24 fuentes climáticas nuevas** con QA diaria y SHA originales.
- GitHub Actions descarga máximo dos fuentes por ciclo, proceso **diario** y en actualizaciones. Las respuestas parciales se archivan con SHA, pero solo se publican perfiles nuevos cuando se reúnen seis archivos históricos completos por grupo.
- Hito exitoso **12/24 fuentes**, 2 grupos completos, **32 nuevos perfiles + 19 antiguos = 51 testigos con 30 años**. Los archivos adicionales siguen incorporándose automáticamente; consultar `datos/clima_contiguo_8p/estado_clima_8p.json` para estado en vivo, sin asumir siempre exactamente 12 fuentes.
- Con 51 puntos: **61 pares** de testigos distanciados <=20 km; **13 parejas** superan el cribado exploratorio (distancia climática estandarizada <=0,6; DEM delta <=300 m; |ΔT anual|<=1,5°C; |Δ lluvia anual|<=150 mm).
- **AUDITORÍA CIENTÍFICA CRUCIAL:** de los 13 pares, **10 comparten alguna celda de ERA5 o ERA5-Land** (en los 10, la misma celda ERA5 podría inducir similitud artificial de lluvia/humedad/radiación); **solo tres pares tienen coordenadas de centro de celda diferentes en ambos modelos**. Celdas diferentes tampoco demuestran independencia estadística o exactitud frente a estaciones.
- Esos tres pares definen **DOS NÚCLEOS DE VECINDAD EXPLORATORIOS, NO POLÍGONOS**: V1 (M0163, M0184, M0224), altitudes 212–521 m (dos enlaces), coords aproximadamente -6,469 a -6,313, -79,562 a -79,531; V2 (M0234, M0308), alta montaña 2978–3236 m (un enlace), coords -6,281 a -6,125, ~-79,36. V2 tiene dist 17,714 km, diferencia T anual -1,046°C, diferencia de precip media anual -53,237 mm y distancia climática 0,24979. **No extrapolar condiciones entre los puntos ni llamar áreas agrícolas confirmadas.**
- **Zonas homogéneas acreditadas = 0; predicciones zonales con habilidad prospectiva comprobada = 0; validación instrumental SENAMHI no realizada**. Riesgo fitosanitario no es función directa de anomalías sin evaluaciones reales de campo.

### Archivos
- `modelos/muestreo_zonas_contiguas_8p.py` y `tests/test_muestreo_zonas_8p.py`: diseña 62 + 1244 aristas, ~7 pruebas.
- `modelos/clima_vecindades_8p.py` y `tests/test_clima_vecindades_8p.py`: adquisición 30 años y SHA de 24 fuentes, control de centros de celda ERA5/ERA5-Land comparados, cribado local, agrupación en núcleos a partir de aristas independientes de *identidad de celda*, ~10 pruebas.
- `.github/workflows/oaf_zonas_8p.yml` y `.github/workflows/oaf_clima_8p.yml`: CI test y descarga automática en main.
- `datos/zonas_contiguas_8p/estado_muestreo_8p.json`, `nuevos_testigos_8p.csv`, `aristas_cercania_8p.csv`.
- `datos/clima_contiguo_8p/estado_clima_8p.json`, `testigos_perfil_completo_8p.csv`, `pares_climaticos_cercanos_8p.csv`, `pares_similares_exploratorios_8p.csv`, `fuentes/` con blobs comprimidos y metadatos.
- `modelos/visor_clima_8p.js` + `index.html`: mapa de los 420 nodos y 62 nuevos testigos, resultados reales de clima completo, pares con indicación de celdas compartidas y los dos núcleos piloto.
- `FASE_8P_VECINDADES_AGROCLIMATICAS.md`: metodología científica, límites y hallazgos.

### Siguiente fase propuesta 8Q
1. Completar últimas fuentes 8P sin forzar la API (HTTP429 se respeta), recalcular testigos 81/81 y núcleos en la climatología.
2. Obtener y verificar **límite departamental oficial INEI/IGN, máscara tierra/mar, cuencas y uso de suelo agrícola**. C2 costero inicial de 8O incluía nodos DEM 0 y -1 m, no aceptar como agrícola sin cartografía.
3. Densificar climatologías alrededor de **V1 piedemonte y V2 alta montaña**, donde existe evidencia de semejanza local con centros diferentes; incluir nodos intermedios, laderas enfrentadas, transiciones de cuenca y gradient físico, verificar centro de ERA5/ERA5-Land.
4. Estudiar continuidad y estabilidad espacial/temporal de los microambientes, construir **polígonos candidatos solo si la evidencia multivariable realmente respalda continuidad**; zonas de transición explícitas y contrastes frente a estación SENAMHI y campo. Evitar interpretar grafos de simple proximidad como polígonos.
5. Solo después contrastar modelos de anomalías de El Niño Costero y fitopatología arándano/vid con validación independiente, emisiones congeladas y referencias oficiales ENFEN/SENAMHI.

Usuario quiere ejecución directa sin preguntas, y mantener el proyecto guardado en GitHub. Mantener referencia OAF 1996–2025; comparativa OMM 1991–2020 cuando corresponda.
