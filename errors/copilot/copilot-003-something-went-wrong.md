---
id: copilot-003
title: "Copilot - \"Something went wrong\" al generar narrativa o reporte"
category: copilot
severity: alta
tools: [Desktop, Service]
tags: [Copilot, something-went-wrong, Smart-Narrative, capacity, preview-consent]
related: [copilot-001, copilot-002]
media:
  images: []
  videos: []
---

## Síntoma

Al intentar usar Copilot para generar páginas de reporte, crear Smart Narratives, o hacer
preguntas en el panel de Copilot, aparece un error genérico con variantes como:

> "Something went wrong and we couldn't load the narrative. Try again later."

> "Something went wrong. Please try again."

> "We weren't able to generate a response. Try rephrasing your question."

> "Copilot couldn't complete your request. Something went wrong on our end."

Este es el error más frecuente de Copilot y el más frustrante porque el mensaje no indica
la causa raíz. Puede aparecer de forma intermitente (funciona a veces, falla otras) o de
forma consistente. En algunos casos, Copilot funciona para un reporte pero falla en otro
dentro del mismo workspace. También puede funcionar para un usuario pero no para un
colega que tiene acceso al mismo reporte y workspace.

## Causa

El mensaje "Something went wrong" es un error genérico que encapsula múltiples causas
posibles. Debugging requiere descartar cada una sistemáticamente:

1. **Workspace sin capacidad válida.** Aunque el botón de Copilot aparezca habilitado
   (especialmente en Desktop), la operación falla en el backend porque el workspace
   donde se publicará o donde reside el reporte no tiene capacidad F2+/P1+. Desktop
   permite abrir el panel de Copilot, pero cuando intenta ejecutar la operación contra
   el servicio, falla si la capacidad no es suficiente. Este es el caso más común.

2. **Grupo de seguridad no autorizado para Copilot.** El usuario ve el botón porque el
   tenant tiene Copilot habilitado, pero su grupo de seguridad no está en la lista de
   permitidos. La UI no siempre refleja esta restricción correctamente y muestra el
   error genérico en lugar de un mensaje de permisos.

3. **Consentimiento de preview expirado o corrupto.** El consentimiento de preview de
   Copilot tiene una vigencia limitada. Si expiró o se corrompió (por ejemplo, tras una
   actualización de Desktop que resetea configuraciones), las llamadas al backend fallan
   con error genérico. Esto es más común en Desktop que en Service.

4. **Restricciones de región.** Si el tenant está en una región sin soporte de Azure
   OpenAI y el toggle de procesamiento cross-geo está desactivado, el backend no puede
   enrutar la solicitud a un datacenter con capacidad de IA. El error resultante es
   genérico.

5. **Cache o tokens de sesión corruptos.** Sessions cookies, tokens de autenticación
   vencidos, o cache del navegador corrupta pueden causar que las llamadas al backend
   de Copilot fallen. Esto es más frecuente en Service que en Desktop y suele
   manifestarse como un error intermitente.

6. **Workspace picker descartado sin selección.** En Desktop, cuando Copilot pide
   seleccionar un workspace para ejecutar la operación (porque necesita capacidad del
   servicio), si el usuario cierra el diálogo sin seleccionar un workspace, Copilot
   muestra "Something went wrong" en lugar de un mensaje más descriptivo.

7. **Modelo semántico demasiado complejo para el tier de capacidad.** Modelos con
   muchas tablas, relaciones, o medidas complejas pueden exceder los límites de
   procesamiento de la capacidad asignada. Las capacidades F2 (la más pequeña que
   soporta Copilot) tienen límites más estrictos. Si el análisis del modelo por parte
   de Copilot excede el timeout o la memoria, se produce el error genérico.

8. **Interrupción temporal del servicio de Azure OpenAI.** Menos frecuente, pero
   posible. Si el backend de Azure OpenAI que atiende a Copilot está experimentando
   problemas, todas las solicitudes de Copilot fallan con este error. Esto afecta a
   todos los usuarios del tenant simultáneamente.

## Solución paso a paso

1. **Descartar el problema de capacidad (causa #1).** Verificar que el workspace
   destino tiene capacidad F2+ o P1+ activa. En Service: **Workspace > Settings >
   Premium > License mode**. Si es Desktop, verificar el workspace seleccionado en el
   diálogo de Copilot. Esta verificación debe ser siempre el primer paso.

2. **Renovar el consentimiento de preview (causa #3).** En Power BI Desktop:
   - Ir a **File > Options and Settings > Options > Preview Features**.
   - Desactivar todas las casillas relacionadas con Copilot.
   - Hacer clic en **OK** y cerrar Desktop completamente.
   - Reabrir Desktop, volver a **Options > Preview Features**.
   - Reactivar las casillas de Copilot y aceptar los términos.
   - Reiniciar Desktop una vez más.
   Este proceso fuerza una renovación del consentimiento y es la solución más
   efectiva para errores intermitentes en Desktop.

3. **Limpiar cache y sesión (causa #5).** En Service:
   - Cerrar sesión de Power BI Service completamente.
   - Limpiar cache y cookies del navegador para `*.powerbi.com` y `*.fabric.microsoft.com`.
   - Alternativamente, abrir una ventana de incógnito/privada.
   - Iniciar sesión nuevamente y probar Copilot.
   En Desktop: cerrar Desktop, eliminar la carpeta de cache en
   `%LOCALAPPDATA%\Microsoft\Power BI Desktop\`, reabrir.

4. **Verificar el workspace picker (causa #6).** Si el error ocurre en Desktop
   inmediatamente después de que aparece un diálogo pidiendo seleccionar un workspace,
   asegurar que se selecciona un workspace con capacidad válida y se confirma con OK.
   No cerrar el diálogo con X ni presionar Cancelar.

5. **Verificar grupo de seguridad y tenant settings (causas #2 y #4).** Solicitar al
   administrador que confirme:
   - Que el usuario está en el grupo de seguridad autorizado para Copilot.
   - Que el toggle de cross-geo está activado si aplica.
   Los cambios en tenant settings tardan **15 a 30 minutos** en propagarse.

6. **Simplificar el modelo si es complejo (causa #7).** Si el error ocurre
   consistentemente con un reporte específico pero Copilot funciona en otros reportes
   del mismo workspace:
   - Verificar el número de tablas, columnas y medidas del modelo.
   - Intentar con una versión simplificada del modelo (menos tablas/medidas).
   - Si la capacidad es F2, considerar escalar a F4 o superior.

7. **Verificar el estado del servicio (causa #8).** Consultar
   https://status.fabric.microsoft.com/ para verificar si hay incidentes activos
   afectando a Copilot o Azure OpenAI. Si hay un incidente, esperar a que se resuelva.

8. **Reintentar después de esperar.** Si ninguno de los pasos anteriores resuelve el
   problema, esperar 30 minutos y reintentar. Algunos errores transitorios del backend
   se resuelven solos.

## Cómo prevenirlo

- **Verificar los requisitos antes de usar Copilot.** Antes de depender de Copilot
  para una presentación o entrega, verificar que el workspace tiene capacidad, que
  el consentimiento de preview está activo y que la conexión funciona. Hacer una
  prueba simple (preguntar "summarize this page") para confirmar.
- **Mantener el consentimiento de preview renovado.** Después de cada actualización
  mayor de Desktop, verificar que las opciones de preview siguen activas. Las
  actualizaciones pueden resetear estas configuraciones.
- **Tener un workspace de fallback.** Si el workspace principal tiene problemas de
  capacidad, tener un segundo workspace con capacidad asignada donde se pueda
  publicar temporalmente para usar Copilot.
- **Monitorear la salud de la capacidad.** Usar la app "Microsoft Fabric Capacity
  Metrics" para detectar sobrecarga antes de que afecte a Copilot. Configurar alertas
  para uso de capacidad superior al 80%.
- **No depender de Copilot para entregas críticas sin plan B.** Copilot sigue en
  preview y puede fallar. Tener un plan alternativo (crear la narrativa manualmente,
  tener un template de reporte preparado) para entregas con deadline fijo.

## Fuentes

- [Microsoft Learn - Copilot in Power BI overview](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)
- [Microsoft Learn - Copilot troubleshooting](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-troubleshoot)
- [Microsoft Learn - Enable Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi)
- [Microsoft Fabric Status Page](https://status.fabric.microsoft.com/)
- [Microsoft Community - Copilot Something Went Wrong](https://community.fabric.microsoft.com/t5/Power-BI-forums/ct-p/power_bi)
