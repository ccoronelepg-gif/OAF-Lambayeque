# Diagnóstico complementario de ERA5-Land, fase 3P

Prueba puntual de 10 días (1–10 de febrero de 1998), estaciones Jayanca y Cueva Blanca.
Se contrastó disponibilidad de precipitación diaria y horaria en Open-Meteo, no exactitud climática.

| Estación | Modelo | Estado | Nulos diarios/total | Nulos horarios/total |
|---|---|---|---:|---:|
| Jayanca (La Viña) | era5_land | OK | 10/10 | 240/240 |
| Jayanca (La Viña) | era5 | OK | 0/10 | 0/240 |
| Jayanca (La Viña) | era5_seamless | OK | 0/10 | 0/240 |
| Cueva Blanca | era5_land | OK | 10/10 | 240/240 |
| Cueva Blanca | era5 | OK | 0/10 | 0/240 |
| Cueva Blanca | era5_seamless | OK | 0/10 | 0/240 |

Si hay valores nulos o negativos, NO se deben interpretar como 0 mm. Si la serie de ERA5-Land no es aprovechable, su limitación debe consignarse y consultar fuentes oficiales alternativas.

Documentación API: https://open-meteo.com/en/docs/historical-weather-api
