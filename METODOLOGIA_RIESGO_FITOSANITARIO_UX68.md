# Módulo C · Riesgo agroclimático fitosanitario — UX68

**Fecha de implementación:** 6 de noviembre de 2026  
**Estado:** primera integración operativa de consulta puntual; no equivale al despliegue completo de un sistema regional de riesgo.

## 1. Alcance que está activo

El catálogo muestra siete cultivos solicitados. Solo habilita el par **arándano – *Botrytis cinerea*** porque el repositorio ya contiene una metodología experimental específica (Fase 7A). Los pares mango–*Colletotrichum* spp., mango–*Ceratitis capitata*, palto–*Phytophthora cinnamomi*, vid–*Plasmopara viticola*, vid–*Botrytis cinerea*, banano–*Pseudocercospora fijiensis*, café–*Hemileia vastatrix*, café–*Leucoptera coffeella* y los de maracuyá permanecen sin modelo habilitado en esta versión. No se les asignan parámetros genéricos.

## 2. Modelo habilitado: arándano – *Botrytis cinerea*

- **Tipo:** indicador exploratorio de favorabilidad meteorológica.
- **Regla:** identificar humedad relativa del aire a 2 m superior al 90 % durante seis o más horas consecutivas.
- **Fundamento:** UC IPM indica que la infección de tejidos puede ocurrir después de seis o más horas de humectación continua o cuando la humedad relativa supera aproximadamente el 90 % durante seis o más horas. Es una condición descrita para Botrytis, no un umbral calibrado para arándano de Lambayeque.
- **Variables descargadas:** temperatura del aire a 2 m, humedad relativa a 2 m, precipitación, radiación solar de onda corta, déficit de presión de vapor y velocidad del viento a 10 m.
- **Variable que activa el criterio actual:** humedad relativa horaria a 2 m. Las otras variables se presentan como contexto; no se suman con ponderaciones inventadas.
- **Cálculo:** recorrer la serie horaria ordenada; incrementar una racha cuando HR >90%; reiniciarla cuando HR ≤90%; contabilizar un episodio cuando la racha alcanza la sexta hora. Las horas adicionales no crean episodios nuevos mientras la racha continúe.
- **Salidas:** número de episodios, mayor racha continua, horas totales HR >90%, agregados diarios de HR, temperatura, precipitación y viento.
- **Clasificación:** no se asignan las categorías Bajo, Moderado, Alto o Muy alto porque no hay umbrales de severidad local validados. La salida es “favorabilidad meteorológica detectada” o “no se detectó el criterio”; la segunda frase no descarta infección.
- **Fenología:** se recoge como dato contextual declarado por el usuario. No se infiere fenología a partir del clima.
- **Limitaciones:** HR a 2 m no equivale a humedad foliar; el sistema no detecta esporas, inóculo, infección, síntomas ni incidencia; no produce probabilidad de enfermedad ni recomendación de plaguicidas.

### Modalidades

1. **Condiciones actuales:** examina las últimas 24 horas horarias disponibles del producto Open-Meteo Forecast. Son datos de modelo meteorológico, no observaciones de una estación en la parcela.
2. **Pronóstico a 7 días:** exige 24 registros horarios completos por cada uno de los siete días siguientes. No rellena horas ausentes.
3. **Análisis histórico:** consulta Open-Meteo Archive con ERA5-Land y fechas elegidas; requiere días completos. La salida es retrospectiva y no representa observaciones instrumentales de parcela.

## 3. Fuentes

- UC IPM, *Botrytis Blight, or Gray Mold*: https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/
- Open-Meteo Forecast API: https://open-meteo.com/en/docs
- Open-Meteo Historical Weather API / ERA5-Land: https://open-meteo.com/en/docs/historical-weather-api
- Modelo experimental previo OAF: `modelos/botrytis_arandano_humedad_7a.js` y `modelos/botrytis_arandano_humedad_7a.py`.

## 4. Selección geográfica y escala

La consulta permite Chiclayo, Jayanca, Motupe y Olmos, o un punto WGS84 digitado/seleccionado sobre el mapa. El marcador identifica la coordenada solicitada; la respuesta registra también la coordenada de la celda meteorológica devuelta por el proveedor. No se interpolan superficies ni se asignan categorías a lugares sin datos. La provincia y distrito se muestran para las cuatro localidades configuradas; para un punto manual se indican como no determinados.

## 5. Tratamiento de datos y control de errores

- Rechaza respuestas HTTP fallidas, errores del proveedor, series desalineadas, valores nulos, horas duplicadas y datos fuera de rango.
- No sustituye faltantes con ceros, promedios ni valores simulados.
- El análisis histórico se limita a 366 días por consulta para evitar descargas excesivas.
- La salida identifica proveedor, fecha/hora de consulta, coordenada solicitada y coordenada modelada.
- La ejecución automatizada de regresión comprueba sintaxis, inclusión de activos PWA, episodio sintético de ocho horas y rechazo de valores nulos.

## 6. Estado de arquitectura y pendientes para la versión regional

OAF se publica como sitio estático en GitHub Pages. En ese alojamiento el navegador puede consultar APIs públicas, pero no puede ejecutar un servicio Python persistente ni alojar PostgreSQL/PostGIS. Los scripts Python que existen en el repositorio se ejecutan mediante flujos de GitHub Actions; no constituyen por sí solos una API interactiva para la consulta por parcela.

Por eso esta entrega no declara implementados un backend Python, una base PostgreSQL/PostGIS, una malla regional, una superficie raster de riesgo ni una calibración epidemiológica. Para esas capacidades se necesita desplegar un servicio de procesamiento y almacenamiento con API segura, o una plataforma equivalente, y validarlo con registros de vigilancia y campo.

Pendientes científicos y de ingeniería:
1. Curar modelos independientes por combinación cultivo–organismo y documentar parámetros/ecuaciones con fuentes específicas.
2. Conseguir series de humedad foliar medida o validar un estimador local; no sustituirla por HR a 2 m.
3. Obtener datos de vigilancia/presencia por localidad y parcela para pasar de favorabilidad a riesgo.
4. Calibrar categorías por modelo con validación temporal y espacial independiente.
5. Incorporar un backend geoespacial, malla con resolución coherente con el producto climático y almacenamiento versionado de modelos/resultados.
6. Contrastar resultados con técnicos y registros de campo de Lambayeque.

## 7. Restricción de cambios

La implementación UX68 se limita al módulo C, sus archivos de estilo, su carga en `index.html`, precaché PWA y pruebas. No se cambian los módulos A ni B, sus capas, ni el diseño de las demás secciones.
