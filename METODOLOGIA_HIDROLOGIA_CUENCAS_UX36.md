# OAF-Lambayeque · UX36 — Vigilancia hidrológica cuantitativa y validación de datos

**Fecha:** 22 de octubre de 2026  
**Subpestaña:** Predicciones y anomalías → Escenarios de riesgo agroclimático  
**Objetivo:** pasar de superposición de peligros a una línea base **cuantitativa, trazable y por cuenca**, priorizando La Leche, Chancay–Lambayeque, Zaña y el sistema Tinajones.

## 1. Estado real de la fase

UX36 aporta:
1. **Tabla reproducible de masas históricas anuales** (hm³/año), comparando volumen medio de referencia contra El Niño de **1998**, con factores calculados a partir de datos publicados por Gobierno Regional/PEOT.
2. **Selector de río** (La Leche, Chancay–Lambayeque, Zaña o comparación conjunta), con diagnóstico científico contextual.
3. **Resaltado cartográfico de cauces oficiales** únicamente si la red hidrográfica IGN/SIGRID entrega líneas **con nombre coincidente**. No se dibujan cauces sintéticos, no se asignan coordenadas inventadas y se informa cuando la geometría no se recupera.
4. **Ficha de Tinajones** que distingue un antecedente documentado de 2024–2025 de los valores operativos que deben consultarse en el sistema PEOT.
5. **Acceso verificable a fuentes oficiales PHISIS y PEOT** para consultar niveles, caudales y almacenamiento actuales. **No hay una API pública verificable y conectada** en esta fase; por ello, el OAF no muestra números «en vivo».
6. **Importación local de series hidrométricas CSV**, sin envío a servidor ni almacenamiento persistente. Los valores están rotulados «aportados por el usuario, no auditados» y no generan alertas automáticas.

**No se ha calibrado un modelo de escorrentía, hidrología, hidráulica, HEC-HMS, HEC-RAS ni un modelo de predicción de inundaciones.** No se calcularon periodos de retorno, probabilidades, umbrales rojos ni alturas de inundación.

## 2. Comparación histórica reproducible

Fuente oficial: Gobierno Regional de Lambayeque / Proyecto Especial Olmos Tinajones, *Plan de Desarrollo Hidráulico de la Región Lambayeque*, versión difundida en 2018. Tabla «Oferta hídrica superficial — Región Lambayeque».

https://siga.regionlambayeque.gob.pe/mysiganew/content/sisadportPublicaTema_mostrar.php?pass=MTA1Nw%3D%3D&poco_id=12546

| Río | Masa media histórica (hm³/año) | Masa del FEN 1998 (hm³/año) | Relación FEN/Media |
|---|---:|---:|---:|
| Chancay–Lambayeque | 850 | 3 000 | 3,53 |
| La Leche | 203 | 1 800 | 8,87 |
| Zaña | 224 | 1 200 | 5,36 |

La comparación se calcula como `fen1998_annual_hm3 / normal_annual_hm3`. El **período estadístico concreto** de la media histórica no aparece claramente precisado en la tabla original, por lo que no se presenta como un promedio OMM 1991–2020, ni como normal climatológica de la actualidad. El documento es de planificación y no representa valores medidos durante 2026.

`1 hm³ = 1 MMC = 1 millón de m³`.

**No confundir:**
- El **volumen anual** es la integral temporal de los caudales durante un año; **no equivale** al caudal pico en `m³/s`.
- Un cociente elevado de volúmenes anuales no es por sí mismo un período de retorno, una probabilidad o nivel de riesgo.
- Las masas de agua de 1998 no se extrapolan al próximo verano sin modelado calibrado.

Archivo de procedencia del observatorio:
`datos/hidrologia_ux36/referencias_cuencas_lambayeque.json`.

## 3. Tinajones: fuentes de operación y antecedente histórico

El portal oficial PEOT, *Sistema de Información Hidrológica Tinajones*, permite consultar **mes y año** y expone campos como Río Chancay (m³/s), aportes de túneles Conchano y Chotano, canal alimentador, compuertas, **Reservorio Tinajones (MMC)**, canal de descarga, circulante, aportes de quebradas y otros caudales de operación.

https://www.gob.pe/40915-acceder-al-sistema-de-informacion-hidrologica-tinajones

Como antecedente verificable separado, la ANA informó el **9 de septiembre de 2025** que, en el período **agosto 2024 – julio 2025**, el almacenamiento del reservorio Tinajones aumentó **40 millones de m³** (MMC). Es un **cambio histórico de almacenamiento**, no el volumen que contiene el reservorio hoy.

https://www.gob.pe/institucion/ana/noticias/1244576-grupo-de-trabajo-padh-presenta-informe-de-evaluacion-2024-2025-en-la-cuenca-chancay-lambayeque

En UX36, `current_storage_mmc: null` y `current_as_of: null` porque no se verificó una consulta automática fiable para dar el último volumen real.

## 4. Monitoreo actual PHISIS / SENAMHI

SENAMHI publica monitoreo y análisis de niveles y caudales mediante PHISIS. La plataforma incluye estaciones hidrométricas y presenta indicadores institucionales de peligrosidad y tendencias. La disponibilidad para cada río depende de la red y fecha del proveedor.

https://www.gob.pe/21712-consultar-la-informacion-hidrologica-peruana-en-la-plataforma-phisis-consultar-el-monitoreo-hidrologico-de-los-rios-peruanos

El OAF **no está suscrito a un API operativo de PHISIS**, por tanto no reutiliza valores ni semáforos oficiales como si dispusiera de ellos en tiempo real.

## 5. Importación de mediciones locales (sin sincronización con servidores)

Archivo de plantilla: `datos/hidrologia_ux36/plantilla_observaciones_hidrometricas.csv`

Columnas:

`fecha,rio,estacion,caudal_m3s,nivel_m,volumen_mmc,fuente`

Ejemplo conceptual sin valores reales: una fila tendría `fecha` en formato `YYYY-MM-DD`, río o embalse, nombre de estación, al menos una magnitud numérica no negativa y una fuente documental identificable.

Reglas:
- Máximo 2 MB por archivo local; se examinan hasta 25 000 líneas.
- Fecha ISO válida y no futura; el río debe identificarse como La Leche, Chancay–Lambayeque, Zaña o Tinajones.
- Al menos una variable presente entre `caudal_m3s`, `nivel_m`, `volumen_mmc`; campos faltantes permanecen sin valor.
- Datos importados **no verificados por el observatorio**; se exhiben en una sección distinta de los valores históricos oficiales.
- No se guardan en GitHub ni se envían a servicios externos. Desaparecen al cerrar o recargar la página.
- Se informa el número de filas aceptadas y descartadas; una estación y fecha se conserva una sola vez.
- Sin serie y parámetros calibrados, no se calculan probabilidades de crecida ni se emiten alertas.

## 6. Diagnóstico y visualización

- La selección de una cuenca modifica la comparación histórica, la explicación y, **cuando se dispone de geometría nominada IGN**, resalta su cauce.
- Para La Leche se distingue la **perspectiva cualitativa de ENFEN de octubre 2026** (caudales posiblemente superiores a lo normal desde noviembre) de un caudal medido o predicho numéricamente.
- Chancay–Lambayeque se interpreta junto con la regulación y operación de Tinajones.
- Zaña requiere su propia red de observaciones hidrológicas y validación local.
- La línea de una fuente cartográfica puede no corresponder a un cauce a escala catastral y no informa la sección hidráulica, diques ni capacidad del drenaje.
- En dispositivos móviles se conservan filtros, controles, tabla y enlaces a fuentes oficiales.

## 7. Próxima fase recomendada (UX37)

1. Obtener series observadas oficiales **con estación, coordenadas, fecha, unidades, frecuencia, metadatos y criterio de calidad** de PEOT, SENAMHI y ANA para cada cuenca.
2. Procesar huecos, cambios de estación, incertidumbre y regionalización hidrométrica; construir una línea base de frecuencia y duración de caudales.
3. Calibrar un modelo lluvia–escorrentía por cuenca y validarlo con eventos independientes; registrar NSE, KGE, RMSE, sesgo y métricas de picos, así como intervalos de incertidumbre.
4. Acoplar niveles y caudales a levantamientos topográficos e hidráulicos antes de elaborar **polígonos de inundación futuros**, cuantificaciones de exposición agrícola y umbrales operativos.
5. Validar visual y funcionalmente el navegador web, el móvil y las políticas CORS de los geoservicios remotos.

Este informe documenta **lo que la fase UX36 sí integra** y las tareas científicas que permanecen pendientes; no sustituye una calibración hidrológica.
