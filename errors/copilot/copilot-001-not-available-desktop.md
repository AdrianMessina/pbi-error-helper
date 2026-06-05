---
id: copilot-001
title: Copilot no disponible o botón deshabilitado en Power BI Desktop
category: copilot
severity: alta
tools: [Desktop]
tags: [Copilot, Desktop, capacity, tenant-settings, preview]
related: [copilot-002, copilot-003]
media:
  images: []
  videos: []
---

## Síntoma

Al abrir Power BI Desktop, el botón de Copilot en la cinta de opciones (Ribbon) aparece
en gris, deshabilitado, o directamente no existe. El usuario no puede abrir el panel de
Copilot ni generar páginas de reporte asistidas por IA. En algunos casos, el ícono aparece
pero al hacer clic no ocurre nada, o muestra un mensaje del tipo:

> "Copilot isn't available. Make sure you have access to a workspace on a supported capacity."

El problema persiste incluso después de reiniciar Desktop o cambiar de archivo .pbix.
En ciertos entornos, el botón aparece para algunos usuarios pero no para otros dentro
de la misma organización.

## Causa

El botón de Copilot en Desktop depende de varias condiciones que deben cumplirse
simultáneamente. Si cualquiera falla, el botón se deshabilita:

1. **Configuración de tenant deshabilitada.** El administrador de Fabric/Power BI no
   activó el switch "Copilot and Azure OpenAI Service" en el portal de administración.
   Esta es la causa más frecuente. La ruta exacta es: **Admin Portal > Tenant settings >
   Copilot and Azure OpenAI Service > "Users can use Copilot and Azure OpenAI Service
   (preview)"**. Si está deshabilitado, ningún usuario del tenant verá Copilot.

2. **Sin acceso a capacidad F2+ o P1+.** Copilot requiere que el usuario tenga acceso
   a al menos un workspace asignado a una capacidad Fabric F2 o superior, o Premium P1
   o superior. Si el usuario solo trabaja con workspaces en capacidad compartida (shared
   capacity) o capacidad inferior a F2, el botón se deshabilita. Importante: **PPU
   (Premium Per User) no es suficiente** para habilitar Copilot en Desktop.

3. **Versión de Desktop obsoleta.** Las versiones de Power BI Desktop anteriores a
   enero de 2025 no incluyen el panel completo de Copilot para reportes. Versiones
   previas pueden tener funcionalidad parcial (solo narrativas inteligentes) o ninguna.
   La versión mínima recomendada es la de **febrero 2025** o posterior para la
   experiencia completa de Copilot.

4. **Consentimiento de preview expirado o no aceptado.** Copilot en Desktop requiere
   que el usuario haya aceptado las condiciones de preview en **File > Options and
   Settings > Options > Preview Features**. Si el consentimiento expiró o nunca fue
   otorgado, el botón puede aparecer pero no funcionar.

5. **Grupo de seguridad no incluido.** Si el administrador configuró Copilot para
   "Specific security groups" en lugar de "The entire organization", el usuario debe
   pertenecer a uno de esos grupos. Si no está incluido, no verá Copilot.

## Solución paso a paso

1. **Verificar la configuración del tenant.** Pedir al administrador de Fabric que
   navegue a **Admin Portal > Tenant settings** y busque la sección "Copilot and Azure
   OpenAI Service". Confirmar que el toggle **"Users can use Copilot and Azure OpenAI
   Service (preview)"** está activado. Si se cambió recientemente, esperar entre 15 y
   30 minutos para que la configuración se propague a todos los usuarios.

2. **Verificar la capacidad del workspace.** Ir a **Power BI Service > Workspace >
   Settings > Premium** y confirmar que el workspace está asignado a una capacidad
   F2, F4, F8, F16, F32, F64, P1, P2, P3, P4 o P5. Si dice "None" o "Shared", el
   workspace no tiene capacidad suficiente. Asignar el workspace a una capacidad
   válida o pedir acceso a un workspace que ya la tenga.

3. **Actualizar Power BI Desktop.** Ir a **File > About** y verificar la versión. Si
   es anterior a enero 2025, descargar la última versión desde
   https://powerbi.microsoft.com/desktop/ o desde Microsoft Store. Desinstalar la
   versión antigua antes de instalar la nueva si se descarga manualmente.

4. **Re-aceptar el consentimiento de preview.** Ir a **File > Options and Settings >
   Options > Preview Features**. Desactivar la casilla de Copilot, hacer clic en
   Aceptar, cerrar Desktop completamente, reabrir Desktop, volver a activar la casilla
   de Copilot y aceptar. Esto renueva el consentimiento de preview.

5. **Verificar pertenencia al grupo de seguridad.** Si el tenant tiene Copilot
   habilitado solo para grupos específicos, verificar en Azure AD (Entra ID) que el
   usuario pertenece a uno de los grupos listados en la configuración del tenant. Si
   no pertenece, solicitar al administrador que lo agregue.

6. **Reiniciar Desktop.** Después de todos los cambios anteriores, cerrar Power BI
   Desktop completamente (verificar en el Task Manager que no queden procesos
   residuales de `PBIDesktop.exe`) y reabrir.

## Cómo prevenirlo

- **Mantener Desktop actualizado.** Configurar actualizaciones automáticas desde
  Microsoft Store o establecer una política organizacional de actualización mensual.
  Las nuevas funcionalidades de Copilot se liberan continuamente y requieren versiones
  recientes.
- **Documentar la configuración del tenant.** Mantener un registro de qué settings
  están habilitados, para qué grupos, y cuándo expiran los previews. Esto evita
  sorpresas cuando un consentimiento expira silenciosamente.
- **Usar un workspace de prueba con capacidad asignada.** Asegurar que los
  desarrolladores de reportes tengan acceso permanente a al menos un workspace con
  capacidad F2+ o P1+ para poder usar Copilot sin depender de asignaciones temporales.
- **Comunicar los requisitos a nuevos usuarios.** Al onboardear nuevos miembros del
  equipo, incluir los pasos de verificación de Copilot como parte del checklist de
  configuración de herramientas.

## Fuentes

- [Microsoft Learn - Copilot in Power BI overview](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)
- [Microsoft Learn - Enable Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi)
- [Microsoft Learn - Copilot requirements and limitations](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-requirements)
- [Microsoft Fabric Blog - Copilot in Power BI](https://blog.fabric.microsoft.com/en-us/blog/copilot-in-power-bi)
