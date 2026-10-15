# Punto de reanudación del OAF-Lambayeque — 14 de octubre de 2026

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/
**Repositorio:** https://github.com/ccoronelepg-gif/OAF-Lambayeque

## Objetivo del proyecto
Desarrollar el Observatorio Agroclimático y Fitosanitario de Lambayeque para integrar series meteorológicas, vigilancia oficial de El Niño, evidencia epidemiológica y modelos predictivos progresivamente validados con observaciones de campo. El propósito es anticipar condiciones de riesgo, facilitar decisiones preventivas y reducir pérdidas agrícolas.

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
1. Verificar funcionamiento de la interfaz y la consulta horaria externa en el sitio publicado; corregir eventuales fallos sin alterar el diseño aprobado.
2. Validar sesgos y calidad de pronósticos horarios frente a estaciones o sensores de temperatura en el dosel.
3. Implementar un indicador experimental para Botrytis en arándano, desarrollando o validando previamente una estimación confiable de humectación foliar.
4. Registrar predicciones por fecha de emisión, horizonte y localidad; compararlas con observaciones fitosanitarias y métricas reproducibles.
5. Evolucionar hacia modelos calibrados localmente para arándano y vid; mantener separados los boletines oficiales ENFEN y las alertas OAF aún no operativas.

**Criterio permanente:** no inventar mediciones, cifras de riesgo, predicciones o validaciones. Presentar resultados confirmados y las incertidumbres.
