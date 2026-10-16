# OAF-Lambayeque — Punto de continuidad 16/10/2026 · Fase 8K

## Fase desarrollada

**8K — Inventario de estaciones candidatas y correspondencia espacial entre puntos OAF y celdas reportadas por Open-Meteo/ERA5-Land**, realizada sobre el proyecto existente y publicada en `main`.

### Hallazgo real: proveedor Open-Meteo, nueva consulta de 16/10/2026

Se consultó para el **1 de julio de 2020** `models=era5_land`, `cell_selection=land`, `daily=temperature_2m_mean`, `timezone=America/Lima`, registrando 4 respuestas de latitud/longitud de centros de celda y elevación reportada API, con URLs, fechas UTC y SHA256:
- Chiclayo solicitada (-6.77140,-79.84090) → API (-6.7999954,-79.799995), distancia 5.524 km.
- Jayanca solicitada (-6.39278,-79.82280) → API (-6.4000015,-79.799995), distancia 2.645 km.
- Motupe solicitada (-6.15083,-79.71420) → API (-6.1999970,-79.700000), distancia 5.688 km.
- Olmos solicitada (-5.98825,-79.74723) → API (-6.0000000,-79.700000), distancia 5.384 km.

**Precisión clave:** las extracciones de temperaturas 8D fueron realizadas anteriormente y no archivaron los centros de celda devueltos originalmente; las coordenadas recuperadas mediante una consulta nueva de 8K son **METADATOS DEL PROVEEDOR EN 8K**, no certificación del píxel exacto usado al crear 8D. La elevación devuelta tampoco equivale necesariamente a la altitud física de un píxel ERA5-Land ni a la cota del instrumento SENAMHI.

### Inventario termométrico documental

- Se conservaron **5 estaciones de la base histórica de lluvia**: Jayanca (La Viña), Cayaltí, Reque, Lambayeque, Cueva Blanca (1.109 meses históricos de precipitación completos, NO temperatura).
- Se añadieron como **ocho candidatas documentales mencionadas en boletín SENAMHI DZ2 con Tmax/Tmin**: Jayanca, Olmos, Reque, Lambayeque, Cayaltí, Tongorrape, Sipán y Puchaca. Solo se acredita mención en boletín, NO datos diarios, continuidad instrumental, disponibilidad ni código histórico. Fuente: https://www.senamhi.gob.pe/load/file/03601SENA-102.pdf
- Resultado del control: **0 estaciones termométricas de Tmedia homologadas, 0 comparaciones estación–reanálisis confirmadas, 0 celdas 8D originales certificadas, ninguna habilidad prospectiva 8E demostrada**.

## Archivos técnicos fase 8K
- `modelos/consultar_metadatos_openmeteo_8k.py`: captura geográfica reproducible API (nueva consulta 8K), evita recolecciones redundantes, conserva hora/URL/hash.
- `datos/metadatos_celdas_openmeteo_8k.csv`: cuatro coordenadas realmente devueltas.
- `datos/candidatas_termometricas_documentales_8k.csv`: ocho candidatos térmicos de boletín, TODOS no certificados.
- `datos/SOLICITUD_SENAMHI_TEMPERATURA_8K.md`: requisitos de adquisición documental e instrumental.
- `modelos/auditoria_celdas_estaciones_8k.py`: auditoría de coordenadas originales 8D, fuentes 8H/8I/8J, distancias, controles y trazabilidad.
- `tests/test_auditoria_celdas_8k.py`: 11 pruebas, todas con datos sintéticos exclusivamente en directorios temporales cuando corresponda.
- `datos/seleccion_espacial_8k/estado_8k.json`, `localidades_celdas_8k.csv`, `proximidad_estaciones_8k.csv`, `vista_8k.json`: informes científicos y visor web.
- `modelos/visor_geografia_8k.js` e `index.html`: pestaña **Verificación de datos**, acordeón 8K.
- `.github/workflows/oaf_geografia_8k.yml`: GitHub Actions valida fuentes, cobertura geográfica y panel, y publica automáticamente solo datos derivados.
- `FASE_8K_INVENTARIO_ESPACIAL.md`: informe científico SENAMHI/Open-Meteo/Copernicus.

La auditoría 8K, después de corregir las pruebas de integración, finalizó con **success**, incluida sintaxis JavaScript y consistencia del panel:
https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38980283304

## Continuidad: Parte 8L

Trabajar sobre el **efecto de la selección de celda y topografía sobre temperatura y riesgo agroclimático**:
1. Recuperar/registrar coordenadas devueltas por Open-Meteo comparando explícitamente `cell_selection=land` y `cell_selection=nearest`, con sus diferencias de distancia y Tmedia sin asumir que alguna versión reproduce exactamente la extracción 8D.
2. Evaluar sensibilidad de la referencia climática 1996–2025 para temperaturas por celda únicamente con datos ERA5-Land documentados y con el mismo periodo/proveedor, siempre manteniendo 1991–2020 OMM como comparabilidad estándar.
3. No afirmar corrección altitudinal ni temperatura instrumental SENAMHI sin código oficial, ubicación/periodo y series térmicas reales.
4. Mantener vigilancia de El Niño Costero por ENFEN y desarrollo del módulo fitosanitario de arándano y vid.
5. Mantener capas profundas de método en Verificación de datos; portada concisa y científica.

**El usuario desea continuación ejecutiva, sin cuestionarios ni tareas manuales.** Nunca generar métricas inventadas, y no anunciar alertas OAF validadas mientras sus modelos prospectivos no estén verificados.
