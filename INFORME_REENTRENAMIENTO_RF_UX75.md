# OAF Lambayeque · UX75 · Informe de reentrenamiento Random Forest

**Fecha de ejecución:** 7 de noviembre de 2026 (UTC).
**Repositorio:** OAF-Lambayeque.
**Estado:** experimento terminado; nuevo modelo **NO** desplegado como operativo.

## 1. Datos efectivamente incorporados

Se recuperaron **2 130 días por localidad** (Chiclayo, Jayanca, Motupe y Olmos), desde 2021-01-01 hasta **2026-10-31**. Son **8 520 registros diarios** de ERA5 mediante Open-Meteo Historical Weather API, el último día disponible verificado por el flujo. En comparación con la emisión anterior, se incorporó el **2026-10-31**.

Variables: precipitación diaria (mm), temperatura máxima y media (°C), humedad relativa media (%), viento medio (km/h) y radiación de onda corta diaria (MJ/m²). Las seis son de **reanálisis ERA5**, no observaciones instrumentales de campo.

El modelo multivariable final se entrenó con **11 836 ejemplos supervisados** y **55 características**. El binario se conserva únicamente como artefacto de investigación del flujo GitHub Actions, no en la web.

## 2. Métodos y prohibición de filtración temporal

- **Incumbente:** Random Forest autorregresivo, rezagos 1, 2, 3, 7 y 14 de lluvia y Tmax; pronóstico encadenado de 7 días.
- **Candidato UX75:** Random Forest **directo por horizonte 1–7**, con variables de historial meteorológico hasta la fecha del origen (no usa humedad, viento ni radiación de días futuros).
- **Ajuste de hiperparámetros:** train 2021–2023 y validación temporal en 2024. Se eligieron los parámetros **antes** de observar los errores de prueba 2025–2026.
- **Prueba 2025:** entrenar únicamente hasta fin de 2024; 52 orígenes / 364 pares de predicción observación.
- **Prueba 2026:** reentrenar únicamente hasta fin de 2025; 44 orígenes / 308 pares.
- Todos los errores usan ERA5 posterior como referencia. **No** equivalen a validación instrumental SENAMHI ni a evidencia `as-issued` contra Open-Meteo almacenado en tiempo real.

**Parámetros elegidos por MAE 2024**

| Variable | Árboles | Profundidad | Hoja mínima |
|---|---:|---:|---:|
| Precipitación diaria | 120 | 10 | 12 |
| Tmax | 160 | 12 | 9 |

## 3. Resultados comparables: MAE (menor es mejor)

| Año | Variable | RF anterior | RF candidato UX75 | Climatología | Cambio UX75 frente a RF anterior |
|---|---|---:|---:|---:|---|
| 2025 | Lluvia (mm/día) | 2,3568 | 2,4935 | 2,1829 | **Empeora 5,80 %** |
| 2026 | Lluvia (mm/día) | 4,1042 | 4,1142 | 4,3487 | **Empeora 0,24 %** |
| 2025 | Tmax (°C) | 1,0787 | 1,0113 | 0,9528 | **Mejora 6,25 %** respecto al RF, pero no a climatología |
| 2026 | Tmax (°C) | 1,3043 | 1,1088 | 2,8549 | **Mejora 14,99 %** respecto al RF |

**Horizontes 1–7 en los que el candidato consigue menor MAE:**

| Año | Lluvia frente RF anterior | Lluvia frente climatología | Tmax frente RF anterior | Tmax frente climatología |
|---|---:|---:|---:|---:|
| 2025 | 0/7 | 2/7 | 6/7 | 3/7 |
| 2026 | 3/7 | 4/7 | 7/7 | 7/7 |

## 4. Decisión técnica

**Lluvia:** no se observa mejora consistente. Se mantiene el RF anterior como referencia experimental y la climatología como línea base de habilidad retrospectiva. El candidato UX75 **no debe** sustituir al anterior.

**Temperatura máxima:** mejora retrospectiva prometedora, especialmente en 2026. En 2025, aun cuando mejora al RF, no supera a la climatología. Por tanto no supera el criterio robusto **ambos años + climatología + al menos 5/7 horizontes**. Mantener como **candidato de investigación**, sin afirmarlo validado operativamente.

**No se ha comparado el candidato con pronósticos Open-Meteo originalmente emitidos en 2025/2026:** para esa comparación se necesitan emisiones realmente archivadas antes de los eventos. El seguimiento prospectivo UX74 inició el 6 de noviembre de 2026.

## 5. Siguientes ensayos justificados

1. Para lluvia: evaluar un modelo de dos etapas (ocurrencia y cantidad), y métricas de eventos raros; no optimizar por el conjunto de prueba congelado.
2. Para temperatura máxima: realizar prueba prospectiva `as-issued` en las cuatro localidades, comparar con Open-Meteo y medir MAE, sesgo y skill frente a climatología.
3. Incorporar estaciones instrumentales con control de calidad y verificar independencia geográfica antes de declarar aptitud para gestión agrícola.
4. Mantener separados los modelos de ambiente meteorológico de la cartografía de infección o infestación fitosanitaria; no traducir MAE climático en probabilidades de plaga.

## 6. Trazabilidad y artefactos

- Resultado auditable: `datos/rf_experimento_ux75/evaluacion_reentrenamiento.json`.
- Código de entrenamiento: `modelos/experimento_rf_nuevos_datos_ux75.py`.
- Flujo: `.github/workflows/oaf_rf_nuevos_datos_ux75.yml`.
- Artefacto binario: `rf_candidato_multivariable_ux75.joblib`, disponible en la ejecución CI (retención 60 días). **No despliegue automático**.
- SHA-256 del binario: `b16479cdaf4a5daed07c625b3515ac18637d881efd8e0aeb124cb515ea3a934f`.

**Conclusión:** el reentrenamiento experimental UX75 fue exitoso a nivel de ejecución y reproducibilidad. **No se demostró mejora robusta global** para ambos objetivos y períodos. La ganancia de Tmax 2026 no autoriza promover la nueva versión.
