# OAF-Lambayeque · Punto de reanudación 17/10/2026 · Fase 8O

## Estado ejecutado y verificado

Se implementó **fase 8O — muestreo geográfico regional minucioso y primera comparación climática multivariable** para evitar extrapolar cuatro localidades a toda Lambayeque y comenzar la búsqueda de zonas regionales climáticamente semejantes.

**Muestreo del relieve COMPLETO**:
- Polígono secundario simplificado, referencial de Lambayeque; no homologado todavía con capa INEI/IGN, posible error de línea de costa.
- 420 puntos dentro del polígono: **293 puntos regulares de malla 0,0625° + 127 puntos adicionales de malla 0,03125°** alrededor de 33 referencias de gradiente/relieve obtenidas del DEM 8N.
- **420 de 420 elevaciones DEM reales** GLO-90/Open-Meteo archivadas con URL/SHA/fecha en 9 lotes `datos/muestreo_8o/fuentes_dem/`; no son sensores meteorológicos ni prueba de homogeneidad.
- Distribución de puntos físicos: planicie <100 m=161; valle 100–299=121; piedemonte 300–799=64; ladera 800–1599=30; montaña 1600–2499=11; montaña ≥2500=23; cotas DEM negativas=10. Conteos de puntos, NO porcentajes de superficie ni hectáreas.
- **19 testigos** distribuidos entre seis estratos de elevación y un control de cotas DEM negativas por selección maximin de distancia dentro de cada estrato; no son parcelas.

**Climatología regional PILOTO COMPLETA**:
- 19 testigos × 360 meses del periodo **1996–2025** (30 años).
- Se archivaron **seis fuentes de reanálisis**: tres décadas por ERA5-Land (Tmean/Tmax/Tmin) y tres por ERA5 (precipitación, RH y radiación), manteniendo modelos/metadatos/URL/SHA separados, sin rellenar lagunas.
- Perfiles de 12 normales mensuales para cinco familias variables (Tmean, amplitud diaria Tmax−Tmin, lluvia, humedad, radiación), normalizadas en escala multivariable.
- Clúster aglomerativo media con k=2–6 y selección por silueta eligió **k=2** y silueta **0,34389**. ARI por décadas contra agrupación completa **1,0** para 1996–2005, 2006–2015 y 2016–2025: clasificación temporalmente estable para **estos 19** puntos, no validación independiente ni estabilidad espacial.
- **C2**: 2 testigos costeros (M0208, M0189), separados 21,856 km, DEM de 0 y −1 m, distancia climática interna estandarizada 0,6235. **MUCHA CAUTELA:** posible selección cerca de costa/mar/área no agrícola en polígono simplificado; la precipitación modelada difiere ~167 vs ~299 mm/año. No habilita zona agroclimática agrícola.
- **C1**: 17 testigos, diámetro espacial **174,131 km**, diferencia de elevación **3.164 m**, distancia climática media 0,9997: NO una sola zona homogénea de uso agrario pese a pertenencia al grupo estadístico.
- **Resultado operativo: 0 polígonos de zonas homogéneas validadas y 0 pronósticos zonales certificados.** NO presentar dos grupos estadísticos como dos pisos ecológicos ni dos zonas de predicción para agricultores. La clasificación es exploratoria y sugiere que 19 testigos aún son demasiado pocos para delinear transiciones espaciales.
- No se modificaron emisiones experimentales 8E/8G ni se atribuyeron alertas a OAF sobre ENFEN, fitopatología arándano/vid.

## Archivos y automatización

- `modelos/muestreo_homogeneidad_8o.py`; `tests/test_muestreo_homogeneidad_8o.py` (9 pruebas sintéticas aisladas).
- `modelos/perfiles_climaticos_8o.py`; `tests/test_perfiles_climaticos_8o.py` (7 pruebas sintéticas aisladas).
- `datos/muestreo_8o/estado_muestreo_8o.json`, `diseno_malla_8o.csv`, `nodos_dem_8o.csv`, `testigos_climaticos_8o.csv`, fuentes DEM.
- `datos/perfiles_climaticos_8o/estado_climatico_8o.json`, `grupos_testigos_8o.csv`, `normales_mensuales_testigos_8o.csv`, fuentes seis bloques.
- `.github/workflows/oaf_muestreo_8o.yml` y `oaf_perfiles_climaticos_8o.yml`; acciones ejecutadas con tests, SHA y archivos climáticos reales; latest climate successful run 38994088827 and later updates.
- `modelos/visor_homogeneidad_8o.js` + `index.html`: mapa/filtro de 420 nodos y testigos, resumen de grupos, advertencia de no certificación en Verificación de datos.
- `FASE_8O_MUESTREO_HOMOGENEIDAD.md`: informe científico y hallazgo crítico de no identificar aún polígonos confiables.

## Siguiente fase sugerida: 8P

1. Conseguir/validar límite regional oficial **INEI/IGN** actualizado y máscara tierra/agua o uso agrícola; revisar puntos C2 en la franja costera occidental (DEM 0 y −1 m) antes de recomendar núcleos de zona.
2. Extender extracción climática multivariable y **contigua** más allá de 19 testigos, hacia los 420 nodos DEM con adquisición por lotes periódicos y límite de API; representar transiciones de lluvia, humedad, radiación y amplitud térmica, además de altitud. Evitar tratar celdas reanalizadas repetidas como observaciones independientes.
3. Delimitar **polígonos candidatos contiguos** por gradientes/climatología 1996–2025, cuencas y altitud, con incertidumbre, contraste por décadas/bloques espaciales y zonificación explícitamente provisional.
4. Verificar zona a zona frente a estaciones térmicas y pluviométricas SENAMHI (metadatos/códigos/periodos, sin afirmar datos disponibles), ENFEN para El Niño Costero, cultivos/fitosanidad arándano y vid. Después comparar habilidad predictiva independiente de modelos regionales y zonales, sin publicidad operativa prematura.

**Preferencias:** continuar ejecutando sin formular cuestionarios ni tareas al usuario; resultados de campo siempre auténticos y rigurosos. Referencia climática 1996–2025, OMM 1991–2020 como comparabilidad.
