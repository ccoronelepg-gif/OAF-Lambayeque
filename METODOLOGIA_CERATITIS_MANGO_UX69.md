# OAF-Lambayeque · Fase UX69: segundo modelo del módulo C

**Fecha:** 6 de noviembre de 2026  
**Ubicación:** VISOR → Escenarios de riesgo agroclimático → C. Riesgo agroclimático fitosanitario.

## Resultado implementado

Se añade una combinación independiente: **mango – *Ceratitis capitata***. El módulo sigue utilizando el mismo mapa geográfico principal, el selector de localidad/parcela y las modalidades actual, pronóstico a 7 días e histórico ERA5-Land. No se cambia ninguna capa de los módulos A y B.

Se preserva la combinación arándano – *Botrytis cinerea*, cuyo cálculo exploratorio evalúa episodios HR ambiental a 2 m >90 % durante al menos 6 horas continuas. **Ninguno de los dos indicadores es una probabilidad validada de infección o infestación.**

### Fórmula de referencia para *Ceratitis capitata*

Para la población experimental de Petrolina (Brasil), el cuerpo de resultados de Ricalde et al. (2012) reporta **temperatura base 9,1 °C** y **constante térmica de referencia huevo-adulto 341 grados-día**. La aproximación implementada es:

```
GD_día = max(0, Tmedia_2m_día - 9.1 °C)
GD_intervalo = Σ GD_día
```

- **Variables consultadas:** exclusivamente temperatura del aire a 2 m (`temperature_2m`), con zona horaria `America/Lima`; para mango no se solicitan variables ajenas a su cálculo.
- **Fuente meteorológica:** Open-Meteo Forecast (actual y 7 días) y Open-Meteo Archive ERA5-Land (histórico), conservando los servicios externos ya utilizados en OAF.
- **Intervalo aplicable:** como precaución se rechazan jornadas cuya temperatura media esté fuera de 15–30 °C, régimen con desarrollo observado en la publicación; el estudio reportó ausencia de desarrollo inmaduro a 35 °C.
- **Datos faltantes:** se rechazan horas nulas, duplicadas, incompletas o temperaturas extremas físicamente inválidas. No se reemplazan valores por ceros, promedios ni predicciones simuladas.
- **En la visualización:** marcador de la ubicación realmente consultada, temperatura media por día, GD diarios y acumulación del periodo. No se colorean superficies regionales inexistentes.
- **Semáforo:** **no implementado** para este organismo. Sin calibración local, vigilancia de presencia, fenología/hospedantes y fecha de inicio de una cohorte, mostrar un nivel Bajo/Moderado/Alto/Muy alto sería engañoso.

**Advertencia documental relevante:** el *abstract* de Ricalde et al. (2012) menciona **8,47 °C**, mientras el texto de resultados del mismo artículo menciona **9,1 °C** para Petrolina, con 341 GD en ambas ubicaciones. OAF declara esta discrepancia explícitamente y usa 9,1 °C de manera provisional, siguiendo los resultados detallados. No se considera parámetro calibrado para Lambayeque. Una revisión posterior deberá contrastar la tabla original y preferir, en el futuro, fuentes de SENASA y validaciones locales.

La temperatura de aire a 2 m **no representa directamente la temperatura en el suelo** donde se desarrolla la pupa, por lo que esta suma no permite afirmar que se completará una generación. No se ofrece fecha de emergencia, población, mortalidad ni daño. El usuario necesita un biofix confirmado y, preferentemente, sensores de temperatura de suelo y monitoreo de campo para avanzar a un modelo fenológico completo.

### Catálogo de modelos

`datos/fitosanitario_modelos_ux69.json` conserva los siete cultivos, los dos indicadores exploratorios y el estado pendiente de organismos de café, vid, palto, banano, maracuyá y mango. Está versionado y puede ampliarse sin reutilizar una ecuación genérica para enfermedades de distinta biología.

### Archivos creados o modificados

- `modelos/ceratitis_mango_termico_ux69.js`: núcleo numérico de cálculos GDD.
- `assets/oaf-ux35c-fitosanitario.js`: selección dinámica de cultivo y organismo, consulta específica de variables, cálculo y resultados.
- `datos/fitosanitario_modelos_ux69.json`: catálogo taxonómico y científico versionado.
- `index.html`: carga el núcleo antes del módulo C, sin crear otro visor.
- `sw.js`: precarga obligatoria del núcleo en la versión UX69.
- `tests/oaf-smoke.mjs`: pruebas de intervalos de siete días, histórico, datos faltantes, rango experimental y ausencia de riesgo ficticio.

### Validación antes de declarar producción

Las pruebas automatizadas comprueban lógica y sintaxis; no sustituyen ensayos de aceptación en navegador ni validación de campo. Deben ejecutarse sobre el despliegue real: elección de mango, selección de *Ceratitis*, cambio de ubicación, los tres periodos, errores de APIs, marcador de la ubicación y estabilidad de la versión móvil. Verificar también que las cuatro capas del módulo A y dos del módulo B permanezcan sin modificaciones.

## Fuentes consultadas

- Ricalde, M. P., Nava, D. E., Loeck, A. E., & Donatti, M. G. (2012). *Temperature-dependent development and survival of Brazilian populations of the Mediterranean fruit fly, Ceratitis capitata, from tropical, subtropical and temperate regions*. Journal of Insect Science, 12, 33. DOI: https://doi.org/10.1673/031.012.3301
- Open-Meteo Forecast API: https://open-meteo.com/en/docs
- Open-Meteo Historical Weather API y ERA5-Land: https://open-meteo.com/en/docs/historical-weather-api
- Catálogo científico de la fase: `datos/fitosanitario_modelos_ux69.json`.

**Siguiente fase de investigación:** conseguir parámetros y observaciones reales para la roya del café (*Hemileia vastatrix*) y modelos específicos de antracnosis en mango, mildiu de vid y pudrición de raíces de palto. No activar sus ecuaciones sin mediciones y fuentes apropiadas, especialmente mojado foliar o humedad del suelo.
