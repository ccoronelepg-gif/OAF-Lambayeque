# OAF 8J — Entrada para series instrumentales HORARIAS

Este directorio solo incluye **plantillas sin datos**: ninguna temperatura horaria SENAMHI ha sido incorporada.

El manifiesto requiere fuente oficial y fecha de publicación UTC, huella SHA-256 de archivo original, identidad de estación y coordenadas, altitud de estación y **de celda** obtenida de metadatos documentados, localidad OAF, método temporal y criterios documentales de calidad, representatividad y autorización de publicación de derivados. No convertir proximidad geográfica en identidad instrumental ni atribuir independencia.

Los archivos originales permitidos se colocarían en `entradas/` si la licencia lo permite. El script no descarga SENAMHI, ni transforma las series históricas de lluvia de fases previas. La columna `instante_utc` exige un ISO 8601 con offset UTC `+00:00` o `Z`, en la **hora exacta (HH:00:00)** para representar una temperatura puntual de 2 m, y el motor agrupa en días civiles de Perú (UTC−05:00). `calidad`: `aprobado` o `rechazado`. Sin datos aprobados en las 24 horas de un día no existe un promedio diario completo; solo con todos los días completos se computa el promedio mensual.

Las coordenadas OAF son referenciales. Se aplica un límite administrativo de distancia de 20 km y desnivel de 200 m, **sin convertirlos en criterios físicos suficientes**. No se corrige temperatura por gradiente térmico adiabático estimado arbitrariamente. Aunque existan comparaciones estación–reanálisis, son **descriptivas**, no verificación prospectiva del modelo 8E ni certificación independiente.

Fuentes: [SENAMHI](https://www.gob.pe/institucion/senamhi/pages/9313-conocer-los-datos-hidrometeorologicos-del-peru); [ERA5-Land/Copernicus](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land); [OMM WMO-No. 8](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/instruments-and-methods-of-observation-programme-imop/guide-instruments-and-methods-of-observation-wmo-no-8).
