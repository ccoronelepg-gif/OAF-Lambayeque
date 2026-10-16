# OAF-Lambayeque — Punto de reanudación: 16 de octubre de 2026 (Parte 8G)

## Última etapa completada
**8G: Evaluador automatizado de pronósticos agroclimáticos en Python**, posterior al rediseño 8F-Web.

La implementación está en la rama `main` del repositorio
https://github.com/ccoronelepg-gif/OAF-Lambayeque

### Archivos de la fase
- `modelos/evaluador_prospectivo_8g.py`: auditor temporal que lee 8E y nunca reescribe pronósticos originales.
- `tests/test_evaluador_prospectivo_8g.py`: siete pruebas, incluidas fechas prematuras, duplicados, modificación de valores, contraste intramensual y fixtures sintéticas **aisladas**.
- `.github/workflows/oaf_evaluador_8g.yml`: automatización 13/20/27 de cada mes posterior a 8E, que ejecuta pruebas y publica datos derivados.
- `datos/evaluacion_prospectiva_8g/metricas_8g.json` y `datos/evaluacion_prospectiva_8g/detalle_8g.csv`: resultados sin imputación.
- `modelos/visor_evaluacion_prospectiva_8g.js`: gráficos y tabla filtrable, solo si hay contrastes reales.
- `index.html`: nuevo acordeón «Fase 8G» en pestaña **Verificación de datos**.
- `FASE_8G_EVALUADOR_PROSPECTIVO.md`: documentación científica con referencias OMM, Copernicus, NOAA y fórmulas.

### Estado de los datos en la primera ejecución real
- 1 emisión original (15/10/2026) y **12 predicciones archivadas** de temperatura para cuatro localidades.
- 8 pronósticos premes y 4 estimaciones intramensuales, separados.
- **0 verificaciones elegibles**, por lo que MAE, RMSE, sesgo y cobertura permanecen nulos.
- Primera verificación posible de octubre **10/11/2026** (ERA5-Land disponible y mes completo); primeras mediciones evaluables de los pronósticos *premes* desde diciembre.
- La habilidad prospectiva **NO ESTÁ DEMOSTRADA**; no atribuir alertas ENFEN, SENAMHI ni riesgos fitosanitarios a la señal térmica.

### Control de calidad
- El primer flujo de CI de 8G finalizó **success**: https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38970388810
- Comprobados el archivo de salida JSON (12 archivados, 0 verificados, métricas null) y CSV (12 filas).
- Flujos institucionales de consistencia 2.0 y 3Z siguieron aprobando tras insertar el panel en Verificación de datos.
- Comprobar eventualmente que GitHub Pages haya concluido el despliegue de la documentación y el panel.

## Próximo paso sugerido
**Parte 8H**: evaluación ampliada de calidad e incertidumbre; contraste independiente del reanálisis con estaciones SENAMHI, diferencias de coordenadas/altitud y cobertura, diseño prospectivo de intervalos sin fuga temporal, indicadores de habilidad con muestra adecuada y controles de actualización de ERA5-Land. Continuar en paralelo la obtención de registros reales de campo sobre Botrytis en arándano y enfermedades de la vid.

**Reglas permanentes**: 1996–2025 referencia histórica principal, 1991–2020 OMM para comparabilidad, sin inventar observaciones, sin atribuir capacidad predictiva no validada, mantener acceso público simple y toda la investigación histórica en Verificación de datos. No exigir al usuario que ejecute scripts como tarea.
