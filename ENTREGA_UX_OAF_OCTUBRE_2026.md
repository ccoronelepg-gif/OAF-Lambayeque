# Entrega UX/UI — OAF-Lambayeque · 17 de octubre de 2026

Se implementaron las etapas UX-1 a UX-5 sobre la rama `main` existente, con commits incrementales de interfaz, CSS, JS y auditoría. No se reescribieron los modelos Python ni las series históricas para adaptar la estética. El inventario previo contiene **799 archivos, 463 IDs HTML y 45 scripts previamente cargados**, todos protegidos con pruebas automatizadas.

## Cambios de UX publicados

**UX-1 — Navegación y confianza.** Menú compacto en Android, «Vista rápida | Vista técnica», localidad seleccionada visible en barra de contexto y leyenda de confiabilidad en cinco categorías: observado/verificado; reanálisis/modelo; experimental; investigación; pendiente. Los datos no se reclasifican sin cambiar su procedencia real.

**UX-2 — Inicio del productor.** Portada agrícola original intacta; selector Chiclayo/Jayanca/Motupe/Olmos inmediatamente debajo; siete métricas (temperatura, lluvia, RH, VPD calculado, viento, radiación, AQI CAMS) con **fuente y fecha de validez por tarjeta**; lectura breve sin umbrales arbitrarios para diagnosticar enfermedades. Tarjetas de arándano/Botrytis y vid/oídio en evaluación; el primer cultivo no dispone todavía de verificación biológica local.

**UX-3 — Mapa, pronóstico y fuentes.** El mismo mapa interactivo auditado de **420 puntos DEM** se trasladó a Inicio **sin duplicar su ID ni crear georreferenciación ficticia**; leyenda de altitud exploratoria. Gráficos independientes de siete días para temperatura máxima (°C), precipitación (mm), HR (%), radiación de onda corta (MJ/m²) usando un solo endpoint de pronóstico de Open-Meteo. Tarjetas ENFEN condicionadas a un comunicado realmente verificado; actualmente el archivo ENFEN 3Z registra **consulta fallida**, por tanto se presenta «pendiente de comprobación». Novedades consultan exclusivamente resúmenes archivados OAF, evitando simular noticias en tiempo real. Fuentes principales y flujo `datos abiertos → APIs → calidad → Python/SIG → modelos estadísticos experimentales → interpretación → productor`.

**UX-4 — Archivo de investigación.** Un catálogo de cuatro grupos expandibles conserva las 5 rutas originales y los cientos de bloques técnicos existentes. Los detalles extensos de la pestaña de investigación se muestran con «Vista técnica»; los enlaces directos a un ID técnico activan automáticamente esa vista. Los archivos y nombres de fases se mantienen para trazabilidad técnica.

**UX-5 — Respuesta móvil y no regresión.** CSS verde petróleo / agrícola con fondos claros, controles táctiles, tarjetas responsive, navegación por hash intacta, modo reducido de animaciones. La prueba `.github/workflows/oaf_ux_integrity_2026.yml` comprueba todos los IDs, scripts anteriores, fuentes, mapa único, semántica de clases y sintaxis JS. El workflow histórico de interfaz se adaptó para reconocer que el **único mapa** ahora vive en Inicio.

## Alcance real de la validación

- Se han ejecutado pruebas de código y verificado el éxito de las publicaciones GitHub Pages; **no** se ha completado una validación manual de pantallas Android con un navegador físico en esta sesión.
- La carga de Open-Meteo/CAMS sigue sujeta a red, cuota/latencia y disponibilidad del proveedor. La UI declara los valores ausentes; los tests utilizan *mocks solamente en QA*, nunca como datos reales del sitio.
- La situación ENFEN no se extrapola desde NOAA/OAF. Modelos OAF: análisis estadístico y predictivo **experimental**, no alertas.
- Los códigos Virrey, Puchaca y El Espinal están corroborados documentalmente; altitudes y emplazamientos históricos siguen sin certificar. El mapa físico de 420 nodos no supone seis zonas agroclimáticas científicamente validadas.
- **La ejecución de la fase 9G** posteriormente añadió comparaciones entre ubicaciones documentales, pero no MAE/RMSE frente a ERA5/CHIRPS.

## Evidencia verificable

- [Plan UX, dependencias y criterios de aceptación](PLAN_UX_OAF_2026.md)
- [Inventario antes de cambios](datos/ux_2026/auditoria_base_2026.json)
- [Pruebas de no regresión](tests/test_ux_oaf_2026.py), [script de datos y ENFEN](assets/oaf-ux-data-2026.js), [estilos de inicio](assets/oaf-ux-home-2026.css), [navegación](assets/oaf-ux-shell-2026.js)
- [GitHub Actions UX](.github/workflows/oaf_ux_integrity_2026.yml)
- [Fase 9G: sensibilidad geográfica](FASE_9G_SENSIBILIDAD_GEOGRAFICA.md)
