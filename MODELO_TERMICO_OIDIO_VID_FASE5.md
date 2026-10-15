# Fase 5 · Indicador térmico experimental del oídio de vid

Proyecto: OAF-Lambayeque. El portal público contiene un módulo de análisis prospectivo dentro de Cultivos y riesgo de enfermedades → Predicción.

## Evidencia científica
La [guía UC IPM](https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/) indica que, **después de una infección primaria**, tres días consecutivos con al menos seis horas continuas por día entre 70 y 85 °F (aproximadamente 21,1–29,4 °C) dentro del dosel pueden iniciar la fase conidial del índice. Este algoritmo del OAF evalúa exclusivamente ese patrón térmico y **no** el índice completo de UC IPM.

## Datos y procedimiento
Se utiliza la [API de Open-Meteo](https://open-meteo.com/en/docs), serie horaria pronosticada de temperatura del aire a 2 m, con zona horaria America/Lima. Se solicitan ocho días y se descarta el día actual; se evalúan siete jornadas completas futuras. Se cuenta el mayor tramo de horas consecutivas dentro de la franja térmica. No se suman horas dispersas.

La herramienta presenta días que cumplen el criterio térmico, máxima racha de días y la existencia de una secuencia de tres días consecutivos. Horas faltantes hacen que la jornada no sea evaluable; no se sustituyen datos.

## Limitaciones esenciales
- La temperatura a 2 m no es equivalente a la temperatura en el dosel.
- El modelo original requiere una infección primaria conocida y condiciones del cultivo que aún no se registran.
- La resolución horaria no reproduce los extremos térmicos subhorarios ni el índice completo.
- No mide incidencia, severidad o probabilidad de infección, ni recomienda tratamientos.
- El pronóstico depende del proveedor externo, no ha sido validado prospectivamente en Lambayeque.

## Reproducibilidad
Script: [oidio_vid_indicador_termico.py](modelos/oidio_vid_indicador_termico.py). Se ejecuta con la biblioteca estándar de Python.

Pruebas sin Internet: python modelos/oidio_vid_indicador_termico.py --prueba

Consulta al proveedor: python modelos/oidio_vid_indicador_termico.py --localidad Motupe

La primera instrucción prueba cuatro casos: tres días consecutivos, días separados, un día con hora faltante y días sin condiciones favorables.

## Próximos pasos
1. Validar los datos pronosticados con sensores de temperatura dentro del dosel en parcelas de vid.
2. Recopilar fenología, presencia primaria de oídio, antecedentes y verificaciones de campo.
3. Registrar fecha de emisión de cada pronóstico y resultado observado, para medir sensibilidad, especificidad y calibración.
4. Incorporar Botrytis en arándano cuando exista una estimación confiable de humectación foliar y datos locales de diagnóstico.
