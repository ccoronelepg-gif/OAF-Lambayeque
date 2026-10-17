# Fase 9G — Sensibilidad territorial de Virrey, Puchaca y El Espinal

**Fecha:** 17 de octubre de 2026. **Alcance:** tres comparaciones entre posiciones geográficas y cotas publicadas por diferentes informes para las mismas estaciones documentales. **No** se extrajeron celdas ERA5-Land/CHIRPS ni se calcularon MAE/RMSE o habilidad predictiva.

## Por qué es necesaria esta comprobación

La fase 9F corroboró documentalmente los nombres mediante tres máximos de lluvia y fechas exactas de SENAMHI. Sin embargo, los boletines históricos no ofrecen una historia armonizada de movimientos del instrumental y citan distintas ubicaciones y altitudes. Si se usara solo una coordenada «porque coincide mejor con la grilla», la comparación contra ERA5/CHIRPS sufriría sesgo de selección. Por ello se preparó esta sensibilidad antes de calcular los errores.

## Resultados reproducibles

| Estación | Separación entre **dos referencias documentales** | Altitudes publicadas en distintas fuentes | Amplitud | Posibles franjas OAF entre referencias |
|---|---:|---|---:|---|
| El Espinal | **1,860 km** | 371; 408,6; 409 m | **38 m** | 300–799 m |
| Puchaca | **2,647 km** | 355; 500; 800 m | **445 m** | 300–799 y 800–1599 m |
| Virrey | **1,531 km** | 214; 264; 275 m | **61 m** | 100–299 m |

Los desplazamientos se estimaron con la fórmula de Haversine entre **dos coordenadas documentales**, no entre puntos de medición contemporáneamente certificados. Son distancias de escenario: no una medida comprobada de que la estación haya sido trasladada esos kilómetros. Si la segunda fuente expresa minutos enteros, la precisión real es inferior a la de los decimales de la tabla.

La diferencia altitudinal de **Puchaca (445 m)** cruza el límite entre dos franjas altitudinales exploratorias del OAF. Es una razón suficiente para **no utilizar una sola cota** de esa estación en la calibración de gradientes regionales o en la asignación de su piso altitudinal histórico sin resolver primero los metadatos.

### Fuentes de cada escenario

Los extremos, posiciones base y altitudes se documentaron en [fase 9F](FASE_9F_IDENTIDAD_TERRITORIAL.md). Se cotejan: [boletín SENAMHI de extremos](https://www.senamhi.gob.pe/load/file/02245SENA-4.pdf) frente a documentación [SENAMHI 2015/CHIRPS](https://sigrid.cenepred.gob.pe/docs/PARA%20PUBLICAR/SENAMHI/Validacion%20de%20datos%20CHIRPS%20de%20Precipitacion%20para%20Monitoreo%20de%20Periodos%20Secos%20y%20Humedos%20en%20el%20Peru.pdf), [normales SENAMHI](https://www.senamhi.gob.pe/load/file/01401SENA-77.pdf) y [documento MINAG/ANA de El Espinal](https://www.ana.gob.pe/sites/default/files/normatividad/files/condiciones_agroclimaticas_arroz_0_2.pdf). Las coordenadas alternativas proceden de las fuentes **específicamente documentadas en la ficha 9F**, no se adivinaron mediante parecido con lluvia o satélites.

## Procedimiento

1. Leer la matriz 9F sin modificarla.
2. Confirmar el nombre/código de cada referencia alternativa y su literal exacto en la fuente archivada.
3. Calcular la distancia Haversine entre coordenada de la primera fuente y segunda fuente; expresar resultado redondeado a 0,001 km, pero advertir sobre la precisión documental original.
4. Identificar mínimos, máximos y amplitud entre altitudes publicadas. Comparar con las seis **franjas físicas exploratorias** del OAF: 0–99, 100–299, 300–799, 800–1599, 1600–2499, >=2500 m. Ninguna franja constituye por sí misma una «zona homogénea validada».
5. Guardar el resultado en `datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json`, generado por `modelos/sensibilidad_ubicacion_9g.py`; test `--check` exige reproducción bit a bit. `.github/workflows/oaf_sensibilidad_ubicacion_9g.yml` verifica la matriz y mantiene bloqueadas comparaciones todavía no realizadas.

## Lo que NO se ha realizado

- **Cero** parejas estación–CHIRPS y **cero** estación–ERA5-Land: no se han extraído valores de grilla para estos candidatos históricos.
- **Ningún** MAE, RMSE, sesgo, habilidad de pronóstico o anomalía predictiva calculado a partir de la fase 9G.
- No hay validación de hora local/día pluviométrico, cambios instrumentales, traslado de estación o independencia CHIRPS respecto de las propias estaciones asimiladas.
- Las diferentes altitudes publicadas podrían representar errores de catálogo o emplazamientos distintos; el motivo exacto sigue desconocido.

## Próxima etapa 9H

Obtener información original de emplazamiento e historia de instrumentos; extraer valores por **todos los candidatos documentados** de cada producto externo, sin elegir retrospectivamente la coordenada que «mejor ajusta»; armonizar fechas y unidades; verificar si CHIRPS incorpora el mismo pluviómetro. **Solo después** calcular diferencias y métricas con cobertura y resolución espacial declaradas. Mantener los indicadores públicos con leyenda «resultado experimental» mientras no se disponga de evidencia de validación independiente.
