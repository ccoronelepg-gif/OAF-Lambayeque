# OAF-Lambayeque | Fase 3W: auditoría horaria SENAMHI GBON/RBON

> Inventario y cobertura temporal observada: NO es validación independiente ni equivalencia con las cinco estaciones históricas.
> Para series horarias, el número de horas presentes NO certifica automáticamente totales mensuales de lluvia.
## Estado de la descarga y cobertura

- Ejecución: completo_con_limitaciones.
- CSV origen: https://www.datosabiertos.gob.pe/sites/default/files/Variables%20Meteorologicas%20de%20las%20Estaciones%20autom%C3%A1ticas%20de%20intercambio%20internacional%20-%20%5BServicio%20Nacional%20de%20Meteorolog%C3%ADa%20e%20Hidrolog%C3%ADa%20del%20Per%C3%BA%20-%20SENAMHI%5D.csv
- Filas analizadas: 408960.
- Primer registro fechado: 2015-01-01.
- Último registro fechado: 2024-04-30.
- Estaciones candidatas por departamento declarado o radio 160 km: 0.
- Meses con conteo de horas completo (preliminares): 0.
- Nuevos meses de lluvia SENAMHI certificados e incorporados: **0**.

## Estaciones candidatas (metadatos del archivo, no identidad instrumental certificada)

| ID del archivo | Estación | Departamento declarado | Red | Horas válidas 2016–2025 | Meses de 24 horas/día completos (provisionales) |
|---|---|---|---|---:|---:|

## Verificación nacional del inventario (segunda auditoría)

La comprobación adicional `scripts/inventario_nacional_gbon_3w.py` procesó las mismas **408 960 filas** y agrupó los registros por **nombre, latitud, longitud, departamento y red**, porque el campo `ID` enumera **filas**, no códigos de estación. Se identificaron exactamente **cinco estaciones**, cada una con 81 792 filas:

| Estación del CSV | Departamento | Red | Distancia mínima aproximada a puntos OAF |
|---|---|---|---:|
| Matucana | Lima | GBON | 651,75 km |
| Carania | Lima | GBON | 728,88 km |
| Imata | Arequipa | RBON | 1 356,80 km |
| San José de Uzuna | Arequipa | RBON | 1 400,65 km |
| Candarave | Tacna | RBON | 1 533,56 km |

**No hay estaciones declaradas en Lambayeque ni a 160 km de los cinco puntos de referencia del OAF** en este archivo. Este resultado NO indica ausencia de estaciones operativas SENAMHI en el departamento: solo delimita la cobertura del CSV concreto.

El archivo comienza el **1 de enero de 2015** y termina el **30 de abril de 2024**. La fecha de última modificación de la ficha en 2025 no debe interpretarse como disponibilidad de observaciones de ese año.

**Archivos complementarios auditables:** `datos/inventario_nacional_gbon_3w.csv`, `datos/estado_geografia_3w.json`, `scripts/inventario_nacional_gbon_3w.py`.

## Límites y próximos pasos

- La fecha de actualización de la ficha del dataset no garantiza que el CSV incluya el año 2025.
- La cobertura en el archivo puede ser de pocos meses o años aunque aparezca un inventario nacional.
- El archivo utiliza FECHA, HORA, PP; se requiere consultar el diccionario para definir el periodo al que corresponde PP, huso horario y horario de acumulación.
- Se ha contado un día como completo solo con 24 horas distintas y 24 filas con precipitación válida; un mes, solo con todos los días completos. Las fechas con horas duplicadas/ausentes no pasan el control.
- El campo ID de este CSV enumera registros/filas y NO es el código instrumental; se agruparon estaciones por nombre, coordenadas, red y departamento.
- Que una estación tenga el mismo nombre que otra no demuestra identidad de serie, continuidad histórica, ni independencia de PISCOp o CHIRPS.
- No se sumó precipitación ni se alteró la validación instrumental 1996–2015; solo se publican conteos y metadatos agregados.
- La pertenencia administrativa se transcribe del campo DEPARTAMENTO, y la búsqueda por 160 km también puede incluir Cajamarca, Piura y La Libertad.
- Fuente: https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio
- Código reproducible: scripts/auditar_gbon_rbon_3w.py

