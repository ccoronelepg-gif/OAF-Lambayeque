# OAF-Lambayeque · Punto de continuidad (22 de octubre de 2026)

**Estado:** pausa voluntaria solicitada por el usuario. **Fase última integrada: UX36.** Próxima fase prevista: **UX37**. No se debe iniciar ninguna fase automáticamente; continuar cuando el usuario lo solicite.

## Entorno del proyecto

- Repositorio: https://github.com/ccoronelepg-gif/OAF-Lambayeque
- Sitio web y aplicación móvil PWA: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
- Autor visible: Ing. Agro. Carlos Enrique Coronel García
- Enfoque: observatorio científico agroclimático y fitosanitario de Lambayeque, con cartografía de riesgos, predicción de lluvia, territorio agrícola y soporte a la agroexportación.

## Fases recientes ya integradas

- **UX29:** visores de territorio/escenarios con árbol de capas, mapa y diagnóstico por selección.
- **UX30:** simplificación de la subpestaña Territorio y riesgos climáticos a un visor único con filtros provinciales/distritales; fuentes a Metadatos y trazabilidad.
- **UX31:** puntos históricos de inundación fluvial, pluvial, erosión y flujos de detritos (INGEMMET); capa de sequía INDECI y calor histórico SENAMHI.
- **UX32–UX34:** correcciones de consultas IGN/SIGRID para ríos, quebradas y límites, visualización de respaldo, etiquetas, color agrícola más visible y mejor navegación.
- **UX35:** visor multicapa de escenarios con años históricos 1983/1998/2017/2023; pronósticos a 3/7 días; perspectiva ENFEN de noviembre 2026–verano 2027; susceptibilidad; capas territoriales compartidas; seis ubicaciones agroindustriales referenciales de Olmos.
- **UX36:** vigilancia hidrológica con La Leche, Chancay-Lambayeque, Zaña y sistema Tinajones; comparación de masas históricas de agua (hm³/año), referencia FEN 1998, ficha de Tinajones, enlaces PHISIS y PEOT, resaltado cartográfico de cauces cuando se dispone de línea nominada, e importación local de CSV hidrométrico.

## Archivos y versión UX36

- `assets/oaf-ux36-vigilancia-hidrologica.js`
- `assets/oaf-ux36-vigilancia-hidrologica.css`
- `datos/hidrologia_ux36/referencias_cuencas_lambayeque.json`
- `datos/hidrologia_ux36/plantilla_observaciones_hidrometricas.csv`
- `METODOLOGIA_HIDROLOGIA_CUENCAS_UX36.md`
- Integración en `index.html`; caché de aplicación `sw.js` versión **v26** (verificada en repositorio a fecha de creación de este registro).

## Base histórica documentada

| Cuenca | Volumen anual medio referencial (hm³/año) | Evento 1998 (hm³/año) | Relación |
|---|---:|---:|---:|
| La Leche | 203 | 1800 | 8.87 |
| Chancay–Lambayeque | 850 | 3000 | 3.53 |
| Zaña | 224 | 1200 | 5.36 |

Fuente de la tabla: Plan de Desarrollo Hidráulico de Lambayeque, fuente Gobierno Regional/PEOT, descrita y enlazada en metodología UX36.

**Advertencia:** las cifras son volúmenes históricos anuales, no caudales actuales ni probabilidades de desborde; tampoco están calibrados modelos hidráulicos o lluvia-escorrentía. El incremento histórico de almacenamiento de Tinajones en agosto 2024–julio 2025 fue de 40 MMC según ANA, **no es el volumen vigente**.

## Próxima fase: UX37

1. **Inventariar estaciones y series hidrométricas reales** de La Leche, Chancay-Lambayeque, Zaña y Tinajones: organismo, identificador, coordenadas, altura, fechas, resolución temporal, unidades, cobertura, actualizaciones y términos de uso.
2. Integrar datos de ANA, SENAMHI PHISIS y PEOT **solamente si se verifica acceso, fuente y esquema**. Si un portal no permite acceso automático, documentar la restricción y habilitar importación reproducible de datos oficiales; no fabricar caudales.
3. **Control de calidad temporal**: ausencias, duplicados, valores extremos, cambios de estación o unidades; indicadores de cobertura.
4. Con series suficientes, desarrollar análisis descriptivos por cuenca y comparación de crecidas históricas; iniciar calibración lluvia–escorrentía (con validación temporal independiente, NSE, KGE, RMSE, sesgo y errores en máximos) **solo cuando existan observaciones suficientes**.
5. Integrar al visor y al Diagnóstico del territorio con lenguaje para usuarios no técnicos, diferencia clara entre *observado / histórico / pronosticado / escenario orientativo*, filtros y trazabilidad.
6. Mantener coherencia **web + PWA + service worker**, versionar recursos para evitar caché desactualizada, y verificar la presentación real con datos y servicios en navegador.

## Limitaciones pendientes de verificar

- No se confirmó mediante prueba visual real que **todos** los geoservicios de SIGRID/IGN, SENAMHI, OSINERGMIN, PEOT o PHISIS respondan desde GitHub Pages o la PWA. El chequeo de sintaxis y archivos en GitHub **no prueba** un servicio cartográfico funcional.
- No se cuenta en el sistema OAF con una API pública verificada para datos operativos de caudal y nivel de PHISIS ni para almacenamiento actual de Tinajones.
- Empresas agroindustriales: las seis ubicaciones UX35 son **referenciales**, no un registro oficial exhaustivo ni comprobación de formalidad tributaria.
- Áreas de inundación futura, alturas de desborde, probabilidades y daños agrícolas **requieren un modelo hidrológico-hidráulico validado**. No deben representarse como hechos.

## Cómo retomar

Cuando el usuario diga «continuemos con la siguiente fase», recuperar este documento y el archivo `METODOLOGIA_HIDROLOGIA_CUENCAS_UX36.md`, verificar la rama actual antes de editar y comenzar UX37. Evitar repetir preguntas ya respondidas y conservar todas las capas y el diseño existente del OAF.
