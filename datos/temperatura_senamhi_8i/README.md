# Datos térmicos instrumentales — Fase 8I

Este directorio es una **entrada controlada**, no una colección de datos oficiales descargados. El manifiesto y la plantilla contienen exclusivamente encabezados: **no existen observaciones de temperatura SENAMHI verificadas cargadas aquí todavía**.

## Ingreso autorizado

Colocar archivos diarios originales en `datos/temperatura_senamhi_8i/entradas/`, solo si la licencia y la autorización de SENAMHI permiten alojarlos públicamente en GitHub. De otro modo, utilizar una ejecución local y conservar los archivos fuera del repositorio, publicando solo resultados autorizados. Registrar en `manifest.csv` código oficial inequívoco, nombre, archivo, SHA-256 exacto, URL documental, fecha de disponibilidad con zona, coordenadas/altitud, método y flags de corroboración **documental**, control de calidad, posible independencia respecto de ERA5-Land y permiso de divulgación de resultados derivados.

Formato diario: `codigo_estacion,fecha,tmax_c,tmin_c,tmedia_c,metodo_tmedia,control_calidad`. `fecha` ISO `AAAA-MM-DD`; temperaturas Celsius; `control_calidad=aprobado` o `rechazado`. `metodo_tmedia=promedio_horario_24h` (media de observaciones efectivas horarias) o `media_diaria_metodo_documentado` solo cuando la documentación demuestra comparabilidad. Si solo se dispone de Tmax/Tmin, **no convertir automáticamente** `(Tmax+Tmin)/2` en la Tmedia del reanálisis.

No imputar días. No extrapolar coordenadas, altitud ni códigos instrumentales. Cada estación/mes requiere cobertura íntegra del calendario para participar en el contraste. La disponibilidad real requiere documentos SENAMHI; las marcas de manifiesto son declaraciones sometidas a auditoría, no garantía de independencia científica.

Fuentes: [SENAMHI datos](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos), [solicitud por estación, variable y periodo](https://www.senamhi.gob.pe/index.php?p=solicitud-servicio), [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
