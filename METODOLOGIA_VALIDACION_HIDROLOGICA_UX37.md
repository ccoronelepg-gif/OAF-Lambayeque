# OAF-Lambayeque · UX37 — auditoría de caudales y validación preliminar de modelos

**Implementación:** 22 de octubre de 2026.  
**Sección:** Predicciones y anomalías → Escenarios de riesgo agroclimático → 7 · Validación de series y modelos hidrológicos.  
**Estado científico:** herramientas de recepción, control de calidad y métricas; **sin observaciones cargadas por defecto y sin modelo lluvia–escorrentía calibrado**.

## 1. Fuentes verificadas y acceso a los datos

**SENAMHI · PHISIS** permite consultar niveles y caudales de la red de monitoreo hidrológico y productos diarios/mensuales, con cobertura dependiente de las estaciones publicadas. No se confirmó una API pública automática, documentada y utilizable directamente desde OAF para descargar una serie diaria íntegra de La Leche, Chancay–Lambayeque y Zaña.

https://www.gob.pe/21712-consultar-la-informacion-hidrologica-peruana-en-la-plataforma-phisis-consultar-el-monitoreo-hidrologico-de-los-rios-peruanos

**Proyecto Especial Olmos Tinajones (PEOT)** publica consultas por mes y año, con valores de descargas y aportes en m³/s, y almacenamiento de Tinajones en millones de m³. No se interpola el registro mensual para fabricar caudales diarios.

https://www.gob.pe/40915-acceder-al-sistema-de-informacion-hidrologica-tinajones

**SENAMHI** también ofrece mecanismos de descarga de datos hidrometeorológicos sujetos a requisitos de acceso; la disponibilidad por estación debe comprobarse antes de incorporarla.

https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos

No se declara en el portal ninguna conexión en tiempo real a PHISIS, ANA o PEOT.

## 2. Formato de importación

Archivo único CSV con cabecera obligatoria:

```csv
fecha,rio,estacion,latitud,longitud,caudal_observado_m3s,caudal_simulado_m3s,fuente,modelo,fecha_descarga
```

Plantilla sin mediciones inventadas: `datos/hidrologia_ux37/plantilla_validacion_caudales.csv`.

- `fecha` y `fecha_descarga`: `AAAA-MM-DD`. Fechas no futuras ni descargas anteriores a la observación.
- `rio`: *La Leche*, *Chancay–Lambayeque* o *Zaña*; grafías sin tildes reconocibles.
- `estacion`: identificador o denominación constante en toda la serie.
- `latitud` y `longitud`: coordenadas WGS84, grados decimales, en territorio peruano. En Lambayeque ambas suelen ser **negativas**.
- `caudal_observado_m3s` y `caudal_simulado_m3s`: caudal diario de **la misma unidad (m³/s), misma estación, mismo día**; valores numéricos no negativos.
- `fuente`: referencia documental legible y constante.
- `modelo`: nombre o versión del modelo externo que produjo el caudal simulado; no se infiere que sea Random Forest de OAF.
- `fecha_descarga`: fecha declarada de obtención del archivo fuente. No sustituye la validación de autenticidad documental.
- Separador coma o punto y coma (para decimales con coma), comillas CSV admitidas.

En el navegador, el archivo se lee mediante la API local de archivos. No se sube al servidor ni a GitHub, no se persiste en almacenamiento local y se descarta tras cerrar o refrescar la página.

## 3. Control de calidad

- Tamaño máximo: 3 MB y 25 000 filas de datos.
- Validación de cabecera y número de columnas.
- Verificación de fechas ISO, años bisiestos, valores de caudal numéricos/no negativos, ubicación en Perú y consistencia de nombre/versión de modelo, estación y fuente.
- Se rechazan coordenadas incongruentes (desplazamiento superior a 0,005° dentro de una estación).
- Duplicados por **río, estación y fecha**: se rechaza la fila duplicada y se contabiliza la incidencia.
- Se informa el número de filas válidas y descartadas, los días faltantes y la cobertura temporal observada.
- Las métricas solo se habilitan con al menos **30 pares válidos** y cobertura diaria de **80 %** o más dentro del intervalo cargado, y una serie no constante. Estos umbrales son **controles exploratorios del OAF**, no criterios normativos del SENAMHI.

La interfaz puede calcular las métricas aunque existan filas descartadas, pero muestra explícitamente las incidencias. Para decisiones científicas es recomendable revisar todos los descartes y realizar auditoría documental.

## 4. Indicadores y sus fórmulas

Para el conjunto de pares `obsᵢ`, `simᵢ`, n observaciones:

- `NSE = 1 − Σ(simᵢ−obsᵢ)² / Σ(obsᵢ−media(obs))²`.
- `KGE-2009 = 1 − sqrt[(r−1)²+(σsim/σobs−1)²+(media(sim)/media(obs)−1)²]`. La componente de variabilidad corresponde a la relación de desviaciones estándar; **no** es KGE 2012.
- `RMSE = sqrt[Σ(simᵢ−obsᵢ)²/n]`, m³/s.
- `MAE = Σ|simᵢ−obsᵢ|/n`, m³/s.
- `PBIAS = 100 × Σ(simᵢ−obsᵢ)/Σobsᵢ`. Aquí **positivo significa sobreestimación**. Esta convención de signo se indica expresamente.
- Se informa el desfase en días entre la fecha del máximo observado y la fecha del máximo simulado de todo el período; no implica atribución causal ni fiabilidad de predicción.

Referencia metodológica de métricas: documentación HEC-HMS (USACE):
https://www.hec.usace.army.mil/confluence/hmsdocs/hmstrm/calibration/calibration-summary-statistics

Definición KGE 2009:
https://search.r-project.org/CRAN/refmans/hydroGOF/help/KGE.html

**No se aplican umbrales universalmente aprobatorios.** NSE y KGE son medidas de concordancia sujetas a la dinámica de la cuenca, la escala temporal y la representación de extremos.

## 5. Bloque cronológico final

Además de la evaluación de la serie completa, el OAF calcula métricas en el **30 % final de la serie** como diagnóstico temporal complementario.

**Advertencia esencial:** este bloque no constituye prueba de independencia si los mismos días o sus resultados se usaron previamente para entrenar, calibrar, seleccionar hiperparámetros o elegir la estructura del modelo. Solo con historia de entrenamiento documentada y separación temporal o por evento podría hablarse de validación fuera de muestra.

Para calibrar un modelo lluvia–escorrentía aún faltan lluvias observadas por cuenca, evapotranspiración/temperatura, parámetros hidrológicos, condiciones iniciales, topografía, caudales de estación con control de calidad y series de evaluación externa.

## 6. Por qué no se estiman inundaciones futuras

La concordancia entre una serie modelada y observada de caudales **no** determina por sí sola calados, velocidades de flujo ni áreas inundadas. Es imprescindible integrar geometría fluvial, modelos hidráulicos, cotas, rugosidad, obras, niveles, condiciones de borde y evaluación independiente por evento.

Los visores de peligro de CENEPRED/INGEMMET conservan su propia metodología y NO se actualizan con los valores importados por el usuario.

## 7. Próxima fase metodológica

1. Obtener series oficiales verificadas por estación, incluyendo cobertura, calidad, frecuencia y permisos de reutilización.
2. Construir por cuenca la línea base completa con caudales medios, máximos y percentiles usando periodos explícitos.
3. Definir ensayos de calibración y validación temporal/espacial/por evento con observaciones independientes, registrando configuración del modelo y supuestos.
4. Evaluar NSE, KGE, RMSE, PBIAS y habilidad para máximos separadamente para cada cuenca.
5. Investigar modelación hidráulica de inundaciones solo tras verificar la capacidad predictiva de caudales y la geometría de cauces.

**Archivos:** `assets/oaf-ux37-validacion-hidrologica.js`, `assets/oaf-ux37-validacion-hidrologica.css`, `datos/hidrologia_ux37/plantilla_validacion_caudales.csv`.
