# OAF-Lambayeque | Fase 3V: estaciones NOAA GHCN-Daily próximas al área de estudio

> **Inventario exploratorio, NO red SENAMHI validada**. Radio de 160 km alrededor de cualquiera de cinco puntos del OAF.
> La pertenencia departamental NO se conoce aquí; una estación de Cajamarca o Piura NO debe presentarse como ubicada en Lambayeque.
> NOAA combina datos de redes nacionales y resúmenes GSOD; fuentes pueden no ser independientes de SENAMHI ni de productos interpolados.

## Conteos comprobados

- Candidatos en el radio geográfico: **4**.
- Con periodo PRCP en inventario que se solapa con 2016–2025: **4**.
- Archivos diarios descargados y revisados: **4**.
- Meses completos 2016–2025 en archivos diarios de candidatos consultados: **2**.
- Nuevas series SENAMHI originales incorporadas al OAF: **0**.

## Candidatos geográficos (solo inventario)

| Código NOAA | Nombre | Distancia mínima a un punto OAF (km) | PRCP primer año | PRCP último año | Meses completos 2016–2025 | Estado descarga |
|---|---|---:|---:|---:|---:|---|
| PEM00084452 | CAPT JOSE A  QUINONES GONZALE | 10.94 | 1973 | 2025 | No comprobado | ok |
| PEM00084472 | GEN FAP ARMANDO REVOREDO IGLE | 120.24 | 1973 | 2025 | 1 | ok |
| PEM00084501 | CAPITAN CARLOS MARTINEZ DE PI | 141.92 | 1973 | 2025 | No comprobado | ok |
| PEM00084401 | CAPITAN FAP GUILLERMO CONCHA | 154.83 | 1973 | 2025 | 1 | ok |

## Interpretación técnica

- El inventario contiene rangos de años por elemento, que NO implican continuidad diaria ni meses completos.
- Para cada candidato descargado se leyeron registros de precipitación PRCP, cuyos valores en GHCN-Daily están en décimas de mm; valores -9999 y Q_FLAG no vacío no se aceptaron.
- Se consideran meses completos solo cuando los días calendario contienen valores diarios válidos.
- Los datos NOAA pueden derivar de intercambio meteorológico o redes nacionales; antes de usarlos hay que identificar códigos, fuente (S_FLAG), zona horaria/día de medición y posibles coincidencias con las cinco estaciones históricas SENAMHI.
- No se ha añadido ningún registro de NOAA a los totales SENAMHI 1996–2015 ni a una validación instrumental de 2016–2025.
- No se ha evaluado pertenencia al territorio administrativo de Lambayeque, ni equivalencia de emplazamientos.

## Fuentes

- Inventario NOAA: https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt y https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt
- GHCN-Daily: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily
- Descripción de archivos: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
- SENAMHI GBON/RBON: https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio
- Código: scripts/inventario_3v_noaa.py
- Inventario: datos/candidatos_3v_noaa.csv; estado: datos/estado_3v_noaa.json.

**Próximo paso:** cotejar identidad y localización oficial con SENAMHI, y comprobar fuentes originales y series diarias más recientes antes de una prueba realmente independiente.
