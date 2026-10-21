# OAF-Lambayeque · Activación de avisos por correo y contador

## Correo por actualización

El flujo .github/workflows/oaf_notificaciones_correo.yml se ejecuta cuando se actualiza la rama main. El envío requiere configurar secretos privados; hasta entonces el código está listo, pero NO envía correos. Ninguna contraseña ni dirección privada se publica en el repositorio.

En el repositorio, abre Settings > Secrets and variables > Actions > New repository secret y crea:
1. OAF_EMAIL_TO — dirección destinataria especificada por el propietario.
2. OAF_GMAIL_USER — cuenta de Gmail remitente.
3. OAF_GMAIL_APP_PASSWORD — contraseña de aplicación de Google (con verificación en dos pasos activada). No usar la contraseña normal de Gmail.

Para probar, entra en Actions > OAF - Aviso de cambios del portal > Run workflow. El correo indica que hubo cambios de archivos, NO certifica que GitHub Pages haya acabado de publicarlos.

## Contador público

El pie de la web integra un widget de visualizaciones de CounterAPI (counterapi.com). No se precisa una API key para este widget público. Cuenta visualizaciones estimadas, NO visitantes únicos; pueden influir recargas, bots y bloqueadores. Es un servicio externo y puede fallar. Un sistema de analítica certificada requiere integrar analítica propia y una política de privacidad.

## Pestañas reorganizadas

Clima Regional contiene las series históricas, mapa de relieve, pronóstico externo de siete días, anomalías oceánicas y, al final, trazabilidad instrumental con estaciones diferenciadas por colores.

Predicciones y Anomalías reúne Python, Machine Learning, Random Forest, paisajes agroclimáticos y evaluación histórica. La ventana de siete días exhibe el pronóstico externo como referencia y declara que RF diario aún carece de emisión validada. La evaluación mensual muestra pruebas retrospectivas 2021–2025 de cinco paisajes, NO pronósticos numéricos futuros.

La portada tiene imagen más compacta, pronóstico semanal resumido para Chiclayo y probabilidades oceánicas oficiales ENFEN (N.º 18-2026, 16/10/2026, figura 2a). Octubre 2026: 98 % cálida extraordinaria y 2 % cálida fuerte; son probabilidades de magnitud del mar Niño 1+2, NO de lluvias o daños agrícolas.

## Comprobación pendiente

Confirmar visualmente desde navegador real tras el despliegue: orden de los módulos, filtros, colores de estaciones, carga de gráficos, estado de imágenes y contador; y ejecutar prueba de correo tras configurar los secretos. El commit en GitHub no demuestra entrega de email ni despliegue concluido.
