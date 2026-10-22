# OAF-Lambayeque · UX28 — Vías de acceso y respuesta ante emergencias

**Fecha:** 22 de octubre de 2026  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos  
**Alcance:** cartografía referencial para planificación preventiva. **No es una herramienta operativa de despacho de emergencias o navegación.**

## 1. Cartografía oficial de carreteras y caminos

Geoservicio del **Ministerio de Transportes y Comunicaciones (MTC)** publicado mediante la Infraestructura de Datos Espaciales del Perú (IDEP), en el servicio:
https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer

| Categoría | ID de capa | Geometría / uso |
|---|---:|---|
| Red vial nacional | 10 | Polilíneas de rutas nacionales |
| Red vial departamental / regional | 9 | Polilíneas de carreteras departamentales |
| Red vial vecinal / caminos rurales | 8 | Polilíneas vecinales |

Las capas se representan con ArcGIS REST `MapServer/export`, mediante `layers=show:8,9,10`, `bboxSR=4326`, `imageSR=4326` y fondo transparente sobre el contorno regional del OAF. Los colores y símbolos originales pertenecen al servidor MTC. El usuario puede activar o desactivar individualmente cada categoría.

Los catálogos históricos IDEP citan redes viales **hasta 2018** en antiguos servicios WMS; comprobar el campo `FECHA_ACT` o `FECHA_ACTU` de la capa utilizada antes de afirmar que una carretera existe o está operativa en 2026. Un trazo de red vial **no garantiza transitabilidad, ausencia de cortes ni capacidad de paso de vehículos de emergencia**.

## 2. Infraestructura de respuesta

Fuente cartográfica del **IGN / IDEP**, servicio `INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer`:

https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer

| Tipo | ID del servicio | Clasificación |
|---|---:|---|
| Comisarías | 0 | Policía / infraestructura |
| Establecimientos de salud | 2 | Categoría II–IV o nombre hospital → hospital; demás → establecimiento de primer nivel / posta / centro |
| Compañías de bomberos | 3 | Bomberos / infraestructura |

Los puntos provienen de consultas `/query?f=geojson` con ventana regional EPSG:4326 y paginación de hasta seis páginas de 500 registros por capa (máximo 3 000 por categoría original). Los registros se filtran a la extensión del visor y al departamento Lambayeque, cuando el campo departamento está presente. La capa sanitaria no es idéntica a RENIPRESS en tiempo real: categorías, direcciones y la disponibilidad de atenciones deben comprobarse en las entidades propietarias.

La clasificación automática de hospitales por `CATEGORIA` (II/III/IV) y el nombre del establecimiento es orientativa. Puede haber excepciones de clasificación; consulte la ficha original de cada centro.

Los puntos dibujados usan **exactamente las coordenadas del geoservicio**. Si la consulta no responde o está incompleta, el visor informa que la carga es parcial o no está disponible, sin inventar establecimientos.

Cuando el usuario selecciona provincia, distrito o unidad hidrográfica en el módulo UX26, los puntos de esta capa se filtran por la geometría cargada; el conteo refleja **registros recibidos**, nunca capacidad de respuesta ni cobertura total. No se estiman kilómetros de red vial por filtro ni tiempos de traslado.

## 3. Defensa Civil

Se incorporan fichas documentales de dos oficinas con direcciones publicadas oficialmente:

- **Dirección Desconcentrada del INDECI Lambayeque**: Calle Los Zapotes N.° 173, Urbanización Santa Victoria, Chiclayo. Fuente: https://www.gob.pe/institucion/indeci/sedes?sheet=3
- **Defensa Civil, Municipalidad Provincial de Chiclayo**: Avenida Grau N.° 152, Biblioteca Municipal, Chiclayo. Fuente: https://www.gob.pe/institucion/munichiclayo/sedes

Estas oficinas aparecen en un directorio con vínculo a su fuente, **sin marcadores en el mapa**: no se ha verificado un catálogo de coordenadas oficiales precisas para las sedes. Las distintas páginas oficiales de INDECI han publicado direcciones distintas en diferentes fechas; se privilegia la plataforma nacional `gob.pe` y debe comprobarse la sede antes de acudir.

La lista de dos oficinas **no es un inventario exhaustivo** de las oficinas provinciales y distritales de Defensa Civil de Lambayeque.

## 4. Qué NO es la capa UX28

- No confirma que un hospital tenga atención de emergencia, medicamentos, ambulancia o camas disponibles.
- No sustituye números telefónicos oficiales, el SAMU, la PNP ni el Cuerpo General de Bomberos.
- No confirma que una carretera sea transitable durante inundaciones, deslizamientos o bloqueos.
- No debe emplearse para rutear ambulancias ni decidir evacuaciones; no se calcularon rutas, accesibilidad temporal ni tiempos de viaje.
- Los símbolos de organismos distintos pueden corresponder a **periodos de levantamiento y precisiones cartográficas diferentes**.
- Si el proveedor no habilita CORS, limita registros o no responde, se debe consultar su visor institucional original.
- **No se incorpora ninguna capa SENASA**, por instrucción expresa del usuario. Los puestos fitosanitarios y los puntos forestales SERFOR no se mezclan con la capa de emergencias.

## 5. Pendientes de comprobación

- Abrir la web pública en Chrome y Firefox de escritorio y en móvil para confirmar acceso a servidores IDEP, respuesta CORS, paginación y tiempos de carga.
- Corroborar en terreno o directorios institucionales la precisión de puntos de salud, bomberos y comisarías.
- Incorporar actualizaciones oficiales de cortes de carreteras, inundaciones y eventos de emergencia con fecha y licencia.
- Añadir futuras capas oficiales completas y georreferenciadas de oficinas de Defensa Civil si el organismo competente las publica.
- Validar criterios de tratamiento de rutas que atraviesan límites provinciales y distritales.

**Arquitectura:** `assets/oaf-ux28-vias-emergencias.js` y `assets/oaf-ux28-vias-emergencias.css`. El visor UX26 sigue administrando la proyección y los filtros; UX28 usa una notificación de redibujado y no modifica el cálculo UX27.
