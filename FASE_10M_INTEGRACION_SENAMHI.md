# OAF-Lambayeque · Integración de observaciones SENAMHI — Fase 10M

**Fecha de corte: 17 de octubre de 2026.**

## ¿Qué se incorporó efectivamente?

Se auditaron **50 archivos nuevos** suministrados por el usuario: 32 archivos de **Cueva Blanca, código SENAMHI 153102, altitud 3300 m**; y 18 de **Incahuasi, código 000307, altitud 3052 m**. Se han conciliado con la auditoría anterior de **13 estaciones** (11 costeras o de valle y las dos montañosas ya parcialmente incorporadas).

| Indicador | Resultado |
|---|---:|
| Estaciones distintas en el consolidado | 13 |
| Registros originales de la auditoría anterior | 1441 |
| Filas provenientes de los 50 archivos nuevos | 1515 |
| Filas totales examinadas | 2956 |
| Claves estación+resolución+fecha/hora repetidas | 303 |
| Copias idénticas extra retiradas del consolidado | 362 |
| Contradicciones de precipitación para la misma clave | **0** |
| Observaciones diarias únicas resultantes | **1386** |
| Observaciones horarias únicas resultantes | **1208** |
| Registros temporales únicos consolidados | **2594** |
| Cueva Blanca: meses completos recibidos | **26** |
| Incahuasi: meses completos recibidos | **14** |
| Total meses-estación en tabla pública | 48 |
| Meses-estación completos con lluvia numérica | 43 |

Las filas horarias se mantienen separadas de las diarias y no se imputan como valores diarios sin contar con horas completas y zona horaria contrastada. La fecha de una estación diferente **no constituye un duplicado** aunque registre también cero milímetros. Las trazas `T` y datos `S/D` no se convierten en cero.

**Atención:** un archivo fuente puede repetir parte o todo un mes; la auditoría usa un identificador de observación real, no un conteo de archivos como si fueran meses independientes. Se han encontrado 303 claves repetidas, con 362 copias adicionales idénticas y **sin cambios contradictorios en los valores de precipitación**.

## Cobertura montañosa nueva para la fase 10L

| Estación | Altitud | Meses distintos completos | Periodos disponibles |
|---|---:|---:|---|
| Cueva Blanca (153102) | 3300 m | **26** | Oct 2021 a sep 2026, **con meses intermedios faltantes** |
| Incahuasi (000307) | 3052 m | **14** | Feb 2024 a may 2026, **con meses intermedios faltantes** |

**Precaución:** los 40 meses-estación completos son **no consecutivos**. No equivalen a una serie continua 2021–2026, ni a 40 meses calendario comunes a ambas estaciones. Los acumulados de esos meses completos contienen observaciones puntuales SENAMHI sin control de calidad; no constituyen todavía una validación de sector CHIRPS.

## ¿Dónde están los datos?

- [Tabla mensual de 48 meses-estación](datos/senamhi_estaciones_10m/resumen_mensual_senamhi_observado.csv). Contiene estación, código original de 6 dígitos, altitud, año-mes, número de días, completitud, suma mensual SOLO si el mes tiene todos sus días numéricos, estatus QC y bloqueo de uso en RF.
- [Manifiesto SHA-256 de 50 archivos originales y resumen de deduplicación](datos/senamhi_estaciones_10m/manifest_fuentes_10m.json).
- [Script de verificación automática](modelos/auditar_integracion_senamhi_10m.py) y [su workflow](.github/workflows/oaf_10m_senamhi_fuentes.yml).

**Archivos completos (incluidos 1386 registros diarios, 1208 horarios, 50 CSV originales, informes Excel, historial y hashes):** en la **biblioteca personal persistente** del usuario, carpeta `/OAF-Lambayeque/SENAMHI/`, subarchivo `OAF_SENAMHI_10M_integracion_2026-10-17.zip`. La biblioteca personal no se publica como parte de GitHub Pages; el portal dispone del **resumen mensual y metadatos** para evaluación/consulta. La base diaria en la biblioteca conserva originales y trazabilidad.

## Reglas científicas de importación a RF

1. Identificación real por `codigo_estacion` + `resolucion` + `fecha_hora`. No utilizar el nombre de archivo como identificador de estación.
2. Datos de fuente: **«SENAMHI / DRD — Datos sin control de calidad»**. La cabecera indica procedencia declarada, pero **no comprueba autenticidad externa**, calidad instrumental, correcciones retrospectivas ni independencia de los pluviómetros usados por CHIRPS.
3. Los totales mensuales completos son **provisionales hasta QC**. Las lagunas no se convierten en precipitación cero y no se interpolan silenciosamente.
4. Validación geográfica pendiente: convertir DMS a WGS84, comprobar orientación y altitud, ubicar estaciones frente a polígonos 9K y comparar su pluviómetro puntual con CHIRPS areal con incertidumbre representativa.
5. Antes de medir un acierto «independiente», identificar si estas estaciones entraron al producto CHIRPS; sus registros pueden estar asimilados por este producto satelital-pluviométrico.
6. **El entrenamiento Random Forest 10K/10L/10J NO se actualiza automáticamente con estos archivos**. Se habilitará solo tras QC, conciliación espacial, control de vintages y particiones de entrenamiento/validación.
7. El modelo de lluvias se mantiene separado de cualquier futuro algoritmo de enfermedades que use observaciones de campo.

**Estado técnico:** incorporado como base de observaciones para análisis de montaña, **pendiente de validación formal y sin alertas meteorológicas habilitadas**.
