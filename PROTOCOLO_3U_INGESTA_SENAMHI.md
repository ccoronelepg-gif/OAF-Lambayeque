# OAF-Lambayeque — Fase 3U: incorporación controlada de nuevas observaciones SENAMHI

**Fecha de preparación:** 14 de octubre de 2026 (Perú)  
**Alcance:** preparar una ingesta científicamente auditable de las series **2016–2025**.  
**Estado:** software de importación y pruebas completados. **No se han recibido ni importado archivos SENAMHI nuevos de 2016–2025**, ni se ha certificado un instrumento nuevo.

## Fuente original y acceso

La información oficial de SENAMHI permite descargar TXT diarios, con seis campos: año, mes, día, precipitación, temperatura máxima y temperatura mínima. La ficha institucional indica **registro y contraseña** para acceder a la descarga:
https://www.gob.pe/es/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos

La Plataforma Nacional de Datos Abiertos del Perú también cataloga un conjunto de variables de **estaciones automáticas de intercambio internacional**:
https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio

La segunda fuente es **complementaria**: aún no se ha demostrado que incluya las cinco series históricas precisas del OAF, ni que tenga la continuidad ni independencia apropiadas. No se importó ningún dato de allí.

## Lo que está implementado

- Importador de seis columnas: `scripts/importar_senamhi_3u.py`.
- Pruebas sintéticas de fechas, datos ausentes y ceros: `tests/test_importar_senamhi_3u.py`.
- Ejecución automática de pruebas en `.github/workflows/pruebas_3u.yml`.
- Directorio **local privado por defecto**: `datos/_privados/3u/`; protegido en `.gitignore`.
- Estado público verificable, sin atribuir nuevas mediciones: `datos/estado_3u.json`.

El importador realiza control de fecha válida y ausencia de duplicados, identifica valores ausentes como `-99.9`, números no válidos y lluvia negativa, y registra episodios de precipitación diaria superiores a 500 mm **como incidencia que requiere revisión**, sin corregirlos ni borrarlos arbitrariamente. Calcula **120 meses por estación** para 2016–2025, solo declara acumulado mensual si están los días completos y deja el campo vacío en los otros casos. **0 mm medido sí se conserva como 0**.

Se crea una huella SHA-256 del archivo original para rastrear versiones. Las marcas de metadatos no se convierten en certificación oficial automática.

## Uso futuro del importador — cuando los TXT estén disponibles legalmente

Ejemplo de sintaxis en la terminal de VS Code (solo documentación del procedimiento; no requiere ejecutar nada mientras no existan archivos nuevos):

```powershell
python scripts/importar_senamhi_3u.py --archivo "datos/_privados/senamhi_originales/cayalti_2016_2025.txt" --estacion "Cayaltí"
```

La salida local será `datos/_privados/3u/cayalti_mensual_3u.csv` y `datos/_privados/3u/cayalti_auditoria_3u.json`. **Estos archivos no deben incluirse en el historial público** sin evaluar autorización y procedencia. Git ignora la ruta, pero `git add -f` puede forzar una inclusión; verificar siempre antes de subir cambios.

El programa solo acepta el formato de seis columnas indicado. Si un TXT oficial tiene encabezados extra, separadores decimales u otras convenciones, se debe documentar y adaptar el lector tras inspeccionarlo; nunca modificar los originales para conseguir una ejecución artificialmente exitosa. Temperaturas se leen como columnas pero esta fase **solo valida precipitación**, no temperatura.

## Criterios científicos y de publicación

1. Confirmar **nombre, código y localidad del instrumento real** del archivo recibido, incluyendo traslados o cambios de estación. No asumir que EMA La Viña equivale a Jayanca histórica ni que todos los códigos de Cueva Blanca son intercambiables.
2. Conservar el TXT original sin alteraciones y registrar fuente, fecha, código y licencia.
3. Agregar diariamente a totales mensuales solo si se cubre todo el mes con datos válidos.
4. Solo tras cotejo instrumental y espacial, comparar con PISCOp v3.0, CHIRPS v3 y ERA5-Seamless. La independencia estadística requiere documentar si los instrumentos participaron en cada producto.
5. Para difusión científica pública, separar **observación instrumental**, **estimación** y **pronóstico**.

**Actualmente:** 1 109 meses-estación originales completos 1996–2015 ya contrastados y 3 327 pares de estimaciones; **0 archivos nuevos 2016–2025** incorporados. Es un **estado de recepción**, no significa lluvia cero ni estaciones inactivas.

## Próximas tareas científicas

Gestionar el acceso autorizado a SENAMHI y las fichas instrumentales; verificar si la información abierta adicional puede aportar pluviómetros independientes; incorporar datos observados realmente recibidos y autorizados; ampliar la validación con los meses completos de 2016–2025 disponibles; revisar gradientes costa–valle–sierra antes del primer módulo de enfermedades del arándano.

**Solicitud ya redactada, todavía no enviada:** `SOLICITUD_DATOS_SENAMHI_3R.md`.
