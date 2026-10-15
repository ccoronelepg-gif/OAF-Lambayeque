# Punto de reanudación del OAF-Lambayeque — 14 de octubre de 2026

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/
**Repositorio:** https://github.com/ccoronelepg-gif/OAF-Lambayeque

## Objetivo del proyecto
Desarrollar el Observatorio Agroclimático y Fitosanitario de Lambayeque como un **sistema predictivo con dos objetivos científicos principales**: **(1) anticipar posibles anomalías climáticas en Lambayeque, especialmente eventos y evolución de El Niño Costero, además de anomalías de lluvia, temperatura y humedad**, y **(2) predecir condiciones de riesgo de enfermedades agrícolas en arándano y vid**, integrando información climática, variables agronómicas y registros sanitarios de campo. El propósito es ofrecer predicciones anticipadas, probabilísticas, fechadas y verificables para mejorar la prevención y las decisiones de productores y profesionales. La vigilancia y el análisis histórico son la base, **no el resultado final**.


## Precisión estratégica final del autor (14/10/2026)

**Meta principal de todo el proyecto: PREDICCIÓN, no únicamente vigilancia o visualización.** El OAF deberá evolucionar hacia dos sistemas predictivos diferenciados pero relacionados:

1. **Predicción agroclimática:** estimar con anticipación la ocurrencia, intensificación o persistencia de anomalías de lluvia, temperatura y humedad en Lambayeque, prestando especial atención a **posibles episodios de El Niño Costero**. Para este fenómeno no basta procesar lluvia local: se necesitarán observaciones y predicciones oceánicas/atmosféricas, anomalía de TSM en Niño 1+2, índices y escenarios ENFEN, además de modelos de referencia. Distinguir pronósticos externos de predicciones originales del OAF. Empezar con modelos sencillos y avanzar a modelado probabilístico solo cuando existan datos adecuados.
2. **Predicción fitosanitaria:** estimar anticipadamente las condiciones favorables o, posteriormente, probabilidades calibradas de ocurrencia de enfermedades de **arándano y vid** con variables climáticas, fenología, datos de campo y modelos epidemiológicos validados localmente. Los primeros focos son Botrytis/antracnosis en arándano y oídio/mildiu en vid.

**Cadena de valor:** datos y monitoreo → pronóstico de anomalías climáticas → estimación de condiciones favorables para patógenos → predicción fitosanitaria calibrada → comunicación preventiva, con sello temporal y niveles explícitos de incertidumbre.

**Requisitos obligatorios antes de declarar éxito:** pronósticos emitidos antes del evento, comparación contra una referencia ingenua/institucional, evaluación temporal fuera de muestra, seguimiento de falsas alarmas, incertidumbre, verificación independiente y evidencia de campo cuando aplique. Los comunicados ENFEN continúan siendo el estado **oficial**, mientras que cualquier pronóstico propio sobre El Niño Costero debe identificarse como experimental hasta demostrar habilidad predictiva. No presentar el OAF como capaz de predecir El Niño o enfermedades antes de completar esta validación.

## Estado del portal
- Cinco secciones principales en este orden: **Inicio**, **Datos climatológicos**, **Cultivos y riesgo de enfermedades**, **Boletín de El Niño**, **Verificación de datos**.
- Portada: dentro del recuadro verde, **solo** «Observatorio Agroclimático y Fitosanitario» y las fotografías de arándano y vid. Debajo y fuera del recuadro, descripción del proyecto **en primera persona por el autor**, seguida de **Carlos E. Coronel García — Ingeniero Agrónomo**. No introducir más texto en el recuadro verde.
- La sección «Cultivos y riesgo de enfermedades» conserva una tabla compacta con **enfermedad, condiciones climáticas y cultivo**, respaldada por fuentes, y una subpestaña diferenciada de **Predicción del riesgo**.
- En el «Boletín de El Niño» se enlazan documentos oficiales ENFEN y SENAMHI, sin inferir automáticamente la alerta vigente. Si la consulta institucional falla, se señala que el estado no está verificado.
- En «Datos climatológicos» se ofrecen consultas meteorológicas externas y su evolución pronosticada; las predicciones propias se señalan como «en desarrollo».
- En «Verificación de datos» permanecen fuentes, trazabilidad, calidad y acceso al portal histórico archivado en `archivo-analisis-historico.html`.
- Evitar sobrecargar la portada y preservar sus cinco pestañas, fotografías y navegación.

## Cultivos, enfermedades y enfoque
- Cultivos prioritarios: **arándano y vid**.
- Biblioteca científica inicial: 5 enfermedades de arándano (Botrytis, antracnosis, mancha diana, oídio y Phytophthora) y 4 de vid (oídio, mildiu, podredumbre gris y podredumbre negra).
- Distinguir condiciones climáticas favorables, riesgo estimado y presencia confirmada. Los umbrales publicados fuera de Lambayeque **no son reglas operativas validadas localmente**.
- Mantener referencia climática principal 1996–2025 cuando haya cobertura completa, y 1991–2020 para comparabilidad con la normal OMM. No interpolar faltantes sin documentarlo.
- Fuentes: SENAMHI (observaciones), CHIRPS (estimaciones satelitales), ERA5/ERA5-Land (reanálisis), NASA POWER cuando resulte útil, ENFEN (comunicados oficiales); identificar siempre el producto y la fecha.

## Último avance técnico: fase 5
- Se incorporó en la subpestaña Predicción un **indicador térmico experimental** para oídio de la vid (`Erysiphe necator`) con pronóstico horario externo Open-Meteo para Motupe, Jayanca, Olmos y Chiclayo.
- Referencia UC IPM: **después de infección primaria**, tres días consecutivos con al menos seis horas continuas por día entre 70–85 °F (aprox. 21,1–29,4 °C) en el dosel. El portal calcula **solo el patrón térmico**, usando temperatura pronosticada a 2 m; **no reproduce el índice completo**, no estima probabilidad de enfermedad ni diagnostica infecciones.
- Se probaron 4 escenarios sintéticos: tres días favorables consecutivos, días separados, hora faltante y ausencia de condiciones favorables. Las pruebas lógicas pasaron. La disponibilidad real de la API no ha sido verificada en este entorno.
- Código: `modelos/oidio_vid_indicador_termico.py`.
- Documentación: `MODELO_TERMICO_OIDIO_VID_FASE5.md`.
- Mantener avisos de que los resultados experimentales no recomiendan fungicidas ni sustituyen monitoreo del cultivo.

## Próximos trabajos acordados
1. **Abrir la línea predictiva agroclimática**: definir anomalías objetivo (lluvia, temperatura, humedad y evolución de El Niño Costero), escalas temporales y métricas; catalogar TSM Niño 1+2, escenarios ENFEN y pronósticos oceánico-atmosféricos fechados.
2. Verificar la consulta horaria de la web y conservar instantáneas de pronósticos por fecha de emisión, plazo y localidad para futura evaluación sin fuga temporal.
3. **Continuar la línea predictiva fitosanitaria**: validar el indicador térmico de oídio en vid y trabajar en Botrytis de arándano con datos fiables de humectación foliar y registros de campo.
4. Implementar evaluación retrospectiva y prospectiva frente a referencias simples u oficiales, cuantificar habilidad, falsos avisos e incertidumbre, y registrar datos faltantes.
5. Evolucionar ambas líneas hacia predicciones útiles **solo si alcanzan validación independiente**; mantener diferenciados comunicados oficiales ENFEN, pronósticos externos, modelos propios experimentales y enfermedades diagnosticadas.

**Criterio permanente:** no inventar mediciones, cifras de riesgo, predicciones o validaciones. Presentar resultados confirmados y las incertidumbres.
