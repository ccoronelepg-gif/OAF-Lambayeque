# Fase UX-7 · Reorganización temática por pestañas
**Fecha:** 21 de octubre de 2026

## Objetivo
Mejorar la navegación del portal OAF-Lambayeque sin eliminar información científica ni redistribuir arbitrariamente datasets, gráficos, modelos o scripts entre pestañas. Mantener la navegación pública y los identificadores existentes.

## Implementación
Se añadieron 36 accesos temáticos organizados en los seis módulos principales:
- **Inicio (7):** elección de localidad, indicadores, mapa, pronóstico externo, agricultura, Niño, novedades.
- **Clima regional (9):** estaciones, paisajes ecoclimáticos, perspectiva meteorológica, series históricas, pisos, sectores, validación instrumental, aire modelado y semejanza climática.
- **Boletines oficiales (5):** instituciones, Niño 1+2, contraste oceánico, forzantes marinas e integración océano-atmósfera.
- **Cultivos y sanidad (3):** enfermedades, MIP y seguridad, y evaluaciones meteorológicas experimentales.
- **Predicciones y anomalías (7):** contraste instrumental, montaña, RF, probabilidades, RF frente a GCN, ENSO y condiciones húmedas.
- **Metadatos y trazabilidad (5):** catálogo, buscador, índice por áreas, auditoría de emisión y archivo íntegro.

## Archivos creados
- `assets/oaf-estructura-pestanas-2026.css`: tarjetas responsivas, navegación accesible y botón de regreso al índice.
- `assets/oaf-estructura-pestanas-2026.js`: navegación contextual, enlace al índice activo y apertura de detalles sin mover ni eliminar contenidos.
- `tests/test_estructura_pestanas_2026.py`: pruebas de rutas, 36 enlaces, IDs originales, orden de scripts, recursos JS/CSS y evidencia científica.

## Archivos modificados
- `index.html`: inserción de los índices dentro de cada pestaña y carga de CSS/JS nuevos, manteniendo íntegros los bloques y sus IDs anteriores.
- `.github/workflows/oaf_ux_integrity_2026.yml`: pruebas adicionales en la auditoría automática.

## Integridad y limitaciones
- No se han modificado los datos meteorológicos, CSV, JSON, modelos predictivos ni métricas científicas.
- Los índices enlazan a los identificadores originales: no reemplazan gráficos ni tablas.
- La información externa permanece identificada como externa, la producción del OAF como investigación cuando corresponda y los avisos oficiales se atribuyen a sus emisores.
- La «Vista rápida» y «Vista técnica» preexistentes siguen disponibles.
- Los deep links y la nueva interfaz requieren verificación manual adicional con navegador físico (especialmente accesibilidad/visualización móvil); las pruebas automáticas no sustituyen esa comprobación.

## Próxima mejora técnica recomendable
Medir rendimiento de los módulos extensos en móvil, optimizar cargas diferidas de visores y normalizar en un catálogo reutilizable los metadatos de cada dashboard. No publicar alertas predictivas sin validación real.
