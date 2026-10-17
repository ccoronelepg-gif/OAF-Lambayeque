# Fase 9V — Recuperación y auditoría de insumos sectoriales
Fecha: 17/10/2026

## Hallazgo y decisión
Se consultó el repositorio asociado y no se encontró la matriz 9Q/9R bajo las rutas verificadas; la búsqueda de `sector_id` no devolvió archivos indexados. Los datos `datos/chirps_v3_reciente_3z.csv` existentes representan **cinco puntos referenciales de seguimiento reciente**, NO los polígonos S001–S042 ni 360 meses por sector. No se usarán como si fueran los datos sectoriales.

**No se ha demostrado superioridad de RF sobre GCN.** Se mantiene RF como modelo técnico provisional solo para implementar una primera referencia. Ningún resultado de precisión se ha calculado ahora.

## Componentes agregados
- `scripts/auditar_insumos_sectoriales_9v.py`: inspecciona CSV con nombres asociados a sectores, polígonos, homogeneidad y 9Q/9R; verifica columnas sector_id/mes/lluvia_mm, unicidad, valores finitos no negativos y 360 meses de 1996–2025 por sector; registra hashes SHA-256, faltantes y fuentes de geometría candidatas.
- `.github/workflows/oaf_auditoria_sectorial_9v.yml`: ejecuta auditoría en GitHub Actions y adjunta los reportes como artefactos descargables, sin pretender habilitar entrenamiento.
- Salidas al ejecutar: `resultados/9v/auditoria_insumos.json` e `inventario.csv`.

## Reglas estrictas
La auditoría solo verifica estructura. Si aparecen 360 meses, la capacitación del modelo sigue bloqueada hasta acreditar origen CHIRPS, versión, polígonos y disponibilidad temporal de predictores. Los faltantes NO se convierten en cero. La base instrumental SENAMHI necesita verificación independiente. No se fabrican GCN, ventajas en porcentajes ni alertas.

## Próxima fase 9W
Cuando la matriz y geometrías originales estén en el repositorio: asignar archivos verificados y hashes, ejecutar 9T, evaluar resultados con 9U, expandir RF espacial y construir GCN temporal sobre adyacencia documentada; evaluar fuera de muestra con intervalos por bloques y reportes por altitud/piso ecológico. Hasta entonces el estado científico es **insumos sectoriales sin acreditar**, no «modelo ganador».
