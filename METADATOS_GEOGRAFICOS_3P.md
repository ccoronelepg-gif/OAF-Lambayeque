# Fase 3P — Auditoría de procedencia geográfica SENAMHI
**14 de octubre de 2026 · OAF-Lambayeque**. Esta tabla es de trazabilidad: **no** prueba reubicaciones; podrían existir diferencias de nombres, fechas, digitalización o tipos de estación.

| Estación | Punto utilizado en fases 3N/3O/3P (lat, lon) | Otro punto publicado o catalogado (lat, lon) | Separación (km) | Interpretación |
|---|---|---|---:|---|
| Jayanca (La Viña) | -6.322; -79.779 | -6.33306; -79.76861 | 1.68 | El segundo aparece en documentación de SENAMHI; confirmar identidad/código del instrumento y periodo |
| Cayaltí | -6.88079444; -79.54701389 | -6.89853; -79.55964 | 2.41 | Contrastar con ficha oficial y verificar cambios de ubicación |
| Reque | -6.88613; -79.83550 | -6.88644; -79.83572 | 0.04 | Diferencia pequeña de geocodificación |
| Lambayeque | -6.73152778; -79.90983611 | -6.70361; -79.92139 | 3.36 | Segundo par registrado en catálogo preliminar anterior; pendiente de soporte documental original |

**Cueva Blanca:** el punto antiguo de la primera maqueta (-5.84; -79.51) difiere **34.43 km** de (-6.13130; -79.40450) y fue **descartado** por error de ubicación. El segundo corresponde aproximadamente a la estación descrita por SENAMHI en un boletín de mayo de 2024, con **3 300 m s. n. m.** y código de estación sujeto a cotejo con serie histórica. Este dato actual **no demuestra continuidad del emplazamiento en 1998**.

## Prioridades

1. Buscar la ficha/código original de las cinco series descargadas y los periodos de traslado o cambio de instrumento.
2. Mantener dos campos separados: «coordenada consultada» y «coordenada instrumental corroborada».
3. Reextraer PISCOp y ERA5 en posiciones corroboradas antes de cerrar recomendaciones regionales.
4. La posible diferencia de ubicación puede cambiar la celda meteorológica utilizada (especialmente cerca de gradientes altitudinales o litorales). No adjudicarle la totalidad del sesgo sin prueba cuantitativa.
5. **EMA La Viña** y **Jayanca (La Viña)** podrían ser denominaciones relacionadas, pero su equivalencia instrumental exacta **no está comprobada**.

## Fuentes contrastadas
- SENAMHI, documento de red pluviométrica e indicadores con coordenadas de Cayaltí, Reque y Jayanca: https://www.senamhi.gob.pe/load/file/01404SENA-1.pdf
- SENAMHI, ficha de estación automática EMA La Viña: https://www.senamhi.gob.pe/load/file/00701SENA-313.pdf
- SENAMHI, informe de mayo de 2024 que indica Cueva Blanca -6.131; -79.405; 3300 m: https://www.senamhi.gob.pe/load/file/03619SENA-31.pdf
- Cuadro de coordenadas empleadas en Fase 3N: https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/VALIDACION_3N.md

La **separación** se calculó geodésicamente (gran círculo) entre pares publicados/codificados y se redondeó a 0.01 km. Son distancias entre metadatos, no medidas de error de GPS ni evidencia de traslado.
