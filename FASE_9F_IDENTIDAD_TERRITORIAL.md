# Fase 9F — Identificación documental y análisis territorial de Virrey, Puchaca y El Espinal

**Corte de trabajo:** 17 de octubre de 2026. **Estado:** relación documental de los tres archivos con nombres, códigos y máximos diarios de SENAMHI, comprobada contra los originales mediante una rutina reproducible; referencias cartográficas institucionales con discrepancias de posición y altitud **no resueltas**. Esta fase no acredita el emplazamiento exacto histórico ni verifica predicciones OAF contra ERA5 o CHIRPS.

## 1. Confirmación positiva de la identidad nominal

Los nombres aportados por el usuario fueron **Virrey, Pucha y Espinal**. La nomenclatura publicada por SENAMHI usa **VIRREY, PUCHACA y EL ESPINAL**. En contra de una asociación de códigos por orden de envío, se verificó el máximo diario original de cada archivo, cotejándolo con [Tabla 3 de «Monitoreo diario de precipitaciones en la región norte» (SENAMHI)](https://www.senamhi.gob.pe/load/file/02245SENA-4.pdf):

| Archivo original (sin modificar) | Nombre publicado | Código institucional usado en documentación | Valor diario original exacto | Registro en informe SENAMHI |
|---|---|---|---|---|
| `qc00152107.txt` | Virrey | 152107 | **330,0 mm, 10/02/2012** | Virrey, 330,0 mm, 10/02/2012 |
| `qc00153114.txt` | Puchaca («Pucha») | 153114 | **150,2 mm, 06/01/1998** | Puchaca, 150,2 mm, 06/01/1998 |
| `qc00000340.txt` | El Espinal («Espinal») | 000340 | **107,0 mm, 20/02/1998** | El Espinal, 107,0 mm, 20/02/1998 |

Son **tres coincidencias exactas y específicas** en fecha, lluvia y nombre, además de la correspondencia entre el código de seis dígitos y el nombre de archivo con ceros iniciales. El código de Virrey y su existencia en Lambayeque también figuran en [un estudio SENAMHI de validación de CHIRPS (2015), Tabla 3.2, página 15](https://sigrid.cenepred.gob.pe/docs/PARA%20PUBLICAR/SENAMHI/Validacion%20de%20datos%20CHIRPS%20de%20Precipitacion%20para%20Monitoreo%20de%20Periodos%20Secos%20y%20Humedos%20en%20el%20Peru.pdf); el código 153114 se publica en [Normales 1981–2010 de SENAMHI](https://www.senamhi.gob.pe/load/file/01401SENA-77.pdf) y el código 000340 en [documentación MINAG de El Espinal](https://www.ana.gob.pe/sites/default/files/normatividad/files/condiciones_agroclimaticas_arroz_0_2.pdf).

**Nivel de confianza:** alto para nombre y código como unidad documental. No supone certificación plena del instrumental, del control de calidad de todos los días, de la licencia de redistribución o del emplazamiento histórico.

## 2. Referencias cartográficas publicadas y discrepancias

La Tabla 3 de SENAMHI ofrece coordenadas y altitudes de referencia, pero documentos diferentes registran ubicaciones o alturas diferentes. **La tabla siguiente no debe presentarse como posición exacta del pluviómetro en 1964–2014.**

| Estación | Sector geográfico según informe | Latitud de referencia | Longitud de referencia | Altitud informe (m) | Otras altitudes publicadas (m) |
|---|---|---:|---:|---:|---:|
| Virrey | Olmos, Lambayeque | −5,580833 | −79,969889 | 264 | **275** (SENAMHI 2015), **214** (estudio ANA) |
| Puchaca | Incahuasi, Ferreñafe | −6,373639 | −79,469500 | 355 | **500** (otro informe SENAMHI), **800** (normales SENAMHI) |
| El Espinal | Oyotún, Chiclayo | −6,817528 | −79,201611 | 409 | **371** (atlas SENAMHI), **408,6** (boletín anterior) |

**IMPORTANTE:** en Puchaca la diferencia de 445 metros entre valores publicados de altitud (355 vs 800) es científica y operativamente significativa. No debe «promediarse» para crear una estación ficticia a 577,5 m ni debe utilizarse para calibrar gradientes térmicos. Podría reflejar diferencias de estación, registros históricos o ubicación; el motivo exacto sigue pendiente de establecer documentalmente. Para El Espinal y Virrey también hay diferencias de coordenadas entre fuentes.

La separación geográfica aproximada entre *referencias publicadas* es: El Espinal–Puchaca **57,5 km**; Puchaca–Virrey **104,1 km**; El Espinal–Virrey **161,6 km**. Estas cifras se basan en la fórmula de distancia ortodrómica y sirven para apreciar dispersión espacial general; no certifican la ubicación real del sensor o su pertenencia a una zona homogénea.

## 3. Intensidad histórica de 1998 con referencia independiente del año analizado

Con las tres series originales auditadas y las series mensuales de 9D, se comparó 1998 con años completos de 1996–2013 **excluyendo del cálculo de referencia 1997 y 1998**. Se exige 100 % de días de cada mes; los años incompletos quedan fuera sin interpolación.

| Estación | Lluvia observada 1998 (mm) | Años completos de comparación (excluye 1997 y 1998) | Factor 1998 / media anual disponible |
|---|---:|---:|---:|
| El Espinal | 1 847,10 | 15 | **5,34×** |
| Puchaca | 2 258,00 | 9 | **10,36×** |
| Virrey | 3 367,40 | 16 | **10,34×** |

**Advertencia:** estas referencias no son la normal climatológica oficial 1996–2025 (30 años), tampoco una climatología OMM 1991–2020. Los factores expresan contraste exploratorio de 1998; no demuestran capacidad de pronóstico ni permiten comparar «intensidad» entre dos climas si la distribución de años disponibles es distinta. Sobre todo, la muestra de Puchaca de **solo 9 años completos** puede ser poco estable y no debe mezclarse sin ajuste con 15 y 16 años.

El archivo `datos/validacion_estaciones_9f/identificacion_territorial_9f.json` guarda cada fecha y magnitud máxima cotejada, hash SHA-256 de los tres originales, nombre/código, referencias geográficas, altitudes incompatibles, altimetría y la comparación anual y enero–abril. El motor `modelos/identificacion_instrumental_9f.py` reproduce estas cifras sin fuentes adicionales inventadas, y el workflow `.github/workflows/oaf_identificacion_9f.yml` verifica que el cálculo siga coherente con todos los originales.

## 4. Consecuencias para el observatorio predictivo

Esta integración **sí permite** asignar un nombre documentado a cada serie histórica, reconocer que corresponden a sectores diferentes del territorio y detectar un histórico de lluvias intensas asociado a 1983 y 1998, siempre separando observación de interpretación. También permite plantear una verificación real y georreferenciada con análisis de sensibilidad a las ubicaciones publicadas.

Esta integración **todavía NO permite**:
- declarar calibrado un modelo de El Niño o predicción de anomalías 1, 2, 3 meses;
- atribuir una capacidad de pronóstico a OAF basada en registros posteriores a la fecha hipotética;
- estimar diferencias por «pisos altitudinales» usando como cierta la altitud conflictiva de Puchaca;
- establecer de manera unívoca qué píxel CHIRPS o ERA5-Land es el correcto a nivel del instrumento histórico;
- considerar independientes los datos CHIRPS en caso de que una de estas series de pluviómetro haya sido asimilada por CHIRPS;
- generar alertas de inundación, sanidad vegetal o salud para parcelas específicas.

**Estado del motor de emparejamiento ERA5/CHIRPS:** se mantiene bloqueado hasta resolver la ubicación histórica y equivalencia instrumental; las coordenadas provisionales se conservan en un objeto *separado* del inventario aprobado, impidiendo su uso accidental como geocodificación certificada.

## 5. Qué cambió en la web

En **Análisis de clima regional**, los paneles «Observaciones meteorológicas históricas» y «Comparación histórica de lluvias entre estaciones» incluyen ahora los nombres Virrey, Puchaca y El Espinal en filtros y leyendas. Se añadió un tercer panel plegable «Virrey, Puchaca y El Espinal: estaciones y territorio»: se elige estación, se consulta el máximo diario cotejado, las referencias de altitud, el análisis histórico de 1998 y un **esquema orientativo** de la posición según la publicación. Cada gráfico tiene una nota aclaratoria.

Se corrigió además un problema de estructura HTML anterior: los paneles de estaciones se situaban fuera de la sección navegable de clima. Ahora residen **dentro de «Análisis de clima regional»**, para que solo aparezcan al visitar esa pestaña.

## 6. Próximo trabajo técnico

Acreditar historia de posición e instrumentos de las tres estaciones con fichas/senamhi y aclarar diferencias entre cotas publicadas. Después realizar sensibilidad de comparación CHIRPS/ERA5-Land extrayendo valores para **todas las coordenadas documentadas alternativas**, contrastando error estación–grilla con periodos coincidentes, ventanas horarias equivalentes y una nota explícita sobre independencia CHIRPS. Calcular sesgo MAE/RMSE y extremos, sin confundir productos históricos con predicción validada.
