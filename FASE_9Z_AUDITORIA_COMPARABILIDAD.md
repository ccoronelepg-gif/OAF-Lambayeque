# Fase 9Z — Auditoría de comparabilidad predictiva territorial (17/10/2026)

Se preparó un evaluador ejecutable, con plantilla CSV y tres pruebas unitarias aprobadas, disponible como paquete entregado en la conversación.

## Alcance implementado
El programa exige fecha objetivo y fecha de emisión anterior, sector, piso ecológico, nombre del modelo (GCN, Random Forest o climatología), horizonte, fuente de observación, precipitación observada/predicha y declaración explícita de pronóstico fuera de muestra. Calcula MAE, RMSE y sesgo por sector/piso/horizonte/fuente/modelo para periodos 2021–2025; ofrece desglose anual. Rechaza duplicados, registros sin evidencia de pronóstico fuera de muestra y fechas de emisión no anteriores al objetivo. Solo habilita comparación exploratoria entre modelos que compartan fechas y valor observado, con al menos doce pares.

## Resultado de control
Tres pruebas locales pasaron: sin datos no se declara ganador ni se activan alertas; un único modelo no se declara comparación; los pronósticos emitidos el mismo día objetivo son rechazados. Sobre la plantilla vacía se generó correctamente **n_validos=0** y ninguna comparación.

## Advertencias
No se dispone en esta integración de la matriz transformada completa de 9X con fechas originales de emisión, objetivos y procedencia acreditada. Por tanto, no se declara un vencedor predictivo ni se atribuyen métricas ficticias a GCN o Random Forest. Tampoco se ha conectado aún esta implementación al portal público.

La declaración CSV `fuera_muestra=si` es un requisito mínimo, no una prueba autosuficiente de exclusión del futuro: hace falta auditar entrenamiento, fecha de corte y producto objetivo. CHIRPS/ERA5 no acreditan automáticamente independencia instrumental.

## Puerta de la fase 10A
Reconstruir a partir de los artefactos retrospectivos de 9X la matriz comparable sin fugas, enlazar con 9Y para intervalos por combinación sector/piso/horizonte y contrastar con estaciones independientes. Mantener bloqueadas las alertas automáticas hasta evaluación instrumental prospectiva.
