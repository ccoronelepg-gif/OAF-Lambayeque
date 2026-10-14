# OAF-Lambayeque | Fase 3Y — Ampliación del registro documental de lluvia DZ2

> **Solo evidencia documental preliminar**, NO serie diaria y NO independencia demostrada.
> Valores recuperados de tablas PP observada indexadas de boletines SENAMHI; cotejo visual PDF pendiente.
> Las estaciones con el mismo nombre no se presumen instrumentos históricos idénticos.

## Avance de cobertura

- 7 meses documentales (2024–2025), 35 registros estación-mes.
- 33 valores numéricos, 2 anotaciones Traza y 10 ceros observados reales.
- Año 2025: 4 meses con tabla transcrita de 12 boletines oficiales publicados.
- **0 meses diarios nuevos certificados**; ningún valor se ha incorporado a los 1 109 meses 1996–2015.

## Acumulados observados (mm/mes) según boletines publicados

| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca | Fuente oficial |
|---|---:|---:|---:|---:|---:|---|
| 2024-07 | 0 | 0 | 0 | 0 | 3.3 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-144.pdf) |
| 2024-09 | 2.3 | Traza | 0 | 0 | 30.1 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-146.pdf) |
| 2024-10 | 0 | Traza | 4.4 | 0 | 54.1 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-147.pdf) |
| 2025-01 | 12.4 | 19 | 9.5 | 4.5 | 117.2 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-150.pdf) |
| 2025-02 | 35.6 | 19.62 | 10.91 | 21.5 | 282.3 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-151.pdf) |
| 2025-03 | 33.5 | 6.55 | 3.9 | 11.2 | 205.1 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-152.pdf) |
| 2025-06 | 0 | 1.4 | 0.31 | 0 | 48.7 | [PDF](https://www.senamhi.gob.pe/load/file/03601SENA-155.pdf) |

## Cobertura de la colección 2025

La página institucional enumera los doce boletines mensuales de 2025:
https://www.gob.pe/institucion/senamhi/informes-publicaciones/6490504-boletin-climatico-regional-dz2-2025
Los meses no transcritos no se completaron por interpolación, comparación con modelos ni suposición de cero.
El hecho de figurar el PDF no garantiza por sí solo que la tabla específica esté completa o contenga estas mismas estaciones.

## Limitaciones técnicas

- «Traza» es texto, no 0 mm; se conservaron dos casos.
- Estas observaciones no permiten probar la continuidad de estación entre 1996–2015 y 2024–2025.
- La extracción indexada del PDF no reemplaza la revisión de imagen/tabla por página; esa verificación se registra como pendiente.
- No se calculó precipitación anual 2025, ni error frente a CHIRPS/PISCOp/ERA5 en 2025.
- Para crear una serie mensual apta para validación se requieren los registros diarios autorizados, sus códigos y controles SENAMHI, o un protocolo independiente específico para acumulados oficiales.
- Las 15 filas previas de la Fase 3X permanecen idénticas.

## Reproducibilidad

Datos: datos/observaciones_documentales_dz2_3y.csv
Matriz de boletines: datos/matriz_boletines_2025_3y.csv
Estado: datos/estado_3y.json
Código y criterios de preservación: scripts/actualizar_boletines_3y.py
Fuentes originales: datos/observaciones_publicadas_dz2_3x.csv y portal oficial SENAMHI DZ2.

