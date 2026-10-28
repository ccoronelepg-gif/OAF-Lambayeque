# AgroCiencia Aplicada · v1.3 — Atlas fotográfico y rigor científico

Actualización de la plataforma consultiva: se retiran fotografías genéricas de las fichas y portadas, el mapa simulado de la vista de inicio y la cabecera creada mediante IA, sustituyéndolos por fotos auténticas de organismos y síntomas con identificación y fuente documentada.

## Evidencia fotográfica
Se incorporan 10 imágenes acreditadas mediante fichas de Wikimedia Commons, con nombre científico del organismo o enfermedad, autor, licencia, URL a la obra original y advertencia de ámbito. El atlas se filtra junto a las 21 fichas sanitarias. Para organismos sin fotografía específica revisada no se publica ninguna imagen. No se usa material generado para representar especies o sintomatología.

Las fotos se cargan de Wikimedia Commons en línea; para licencia y descripción exacta de cada fotografía véase `atlas_fotografico.json`, o «Fuentes y metodología» en la web. Una fotografía no implica identificación de una muestra aportada por el usuario, presencia regional ni prueba epidemiológica. Los síntomas pueden requerir confirmación microscópica o de laboratorio.

## Funcionamiento
Abrir `index.html` desde un servidor web estático o publicar en GitHub Pages; `AgroCiencia_Aplicada_v1_3_autonomo.html` incluye el CSS y JavaScript de la web, pero las fotografías, los mapas y los datos externos requieren internet. Se conservan funciones de Open-Meteo, localización geográfica y UTM, búsqueda, favoritos y exportación CSV. Los datos meteorológicos siguen siendo modelados y requieren verificación en el navegador con conexión.

## Licencias
Código del proyecto: pendiente de elección de licencia por el titular. Las imágenes de terceros **no** se relicencian con el código: respetar las licencias específicas enlazadas en el manifiesto. En el frontend se usa recorte visual CSS sin modificar los originales remotos.

## Revisión
La revisión de las fichas originales y condiciones de Commons se realizó el 28/10/2026. Las URL de fotografías dependen de Wikimedia Commons y pueden variar; si la imagen no carga, se informa y se enlaza la fuente. Antes de un uso científico formal, validar la taxonomía con fuentes especializadas y, si procede, especialistas locales.