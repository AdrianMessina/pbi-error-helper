---
id: copilot-002
title: Copilot no disponible en Power BI Service
category: copilot
severity: alta
tools: [Service]
tags: [Copilot, Service, capacity, F2, P1, Premium, workspace]
related: [copilot-001, copilot-003]
media:
  images: []
  videos: []
---

## Síntoma

Al editar un reporte en Power BI Service (app.powerbi.com), el botón de Copilot no
aparece en la barra de herramientas del modo de edición, o aparece pero está en gris y
no se puede hacer clic. En algunos casos, al intentar abrir el panel de Copilot, aparece
un mensaje genérico indicando que Copilot no está disponible para este workspace. El
problema puede manifestarse de distintas formas:

- El ícono de Copilot no existe en la barra de edición del reporte.
- El ícono existe pero muestra un tooltip: "Copilot is not available for this workspace."
- Al abrir el panel lateral de Copilot, aparece un mensaje pidiendo seleccionar un
  workspace con capacidad compatible, pero ningún workspace de la lista aplica.
- Copilot funciona en un workspace pero no en otro dentro del mismo tenant.

El problema no se resuelve refrescando el navegador ni cambiando de explorador.

## Causa

Copilot en Power BI Service tiene requisitos más estrictos que Desktop porque depende
directamente del workspace donde reside el reporte. Las causas principales son:

1. **Workspace en capacidad compartida (shared capacity).** Esta es la causa número uno.
   Copilot solo funciona en workspaces asignados a capacidades **Fabric F2 o superior**
   o **Premium P1 o superior**. Si el workspace está en capacidad compartida, Copilot
   se deshabilita automáticamente. Es crítico entender que **PPU (Premium Per User) NO
   es suficiente** para Copilot — se requiere capacidad organizacional dedicada. Este
   es el error más común porque muchas organizaciones usan PPU pensando que es
   equivalente a Premium, pero Copilot no lo reconoce como capacidad válida.

2. **Configuración de tenant desactivada.** El administrador no habilitó el switch
   "Copilot and Azure OpenAI Service" en el portal de administración. La ruta es:
   **Admin Portal > Tenant settings > Copilot and Azure OpenAI Service**. Hay dos
   toggles relevantes: el principal para habilitar Copilot, y uno adicional para
   permitir que los datos se procesen fuera de la región geográfica del tenant
   (necesario en regiones donde Azure OpenAI no está disponible localmente).

3. **Usuario no incluido en el grupo de seguridad permitido.** Si el administrador
   configuró Copilot para grupos de seguridad específicos en lugar de toda la
   organización, el usuario debe ser miembro de uno de esos grupos. Esto se configura
   en la misma sección del tenant settings donde se activa Copilot.

4. **Región geográfica no soportada.** Copilot requiere acceso a Azure OpenAI Service,
   que no está disponible en todas las regiones de Azure. Si el tenant está en una región
   sin soporte (por ejemplo, algunas regiones de Sudamérica, Asia o gobierno), Copilot
   no funcionará a menos que se habilite el procesamiento cross-geo. Las regiones
   soportadas incluyen US East, US West, West Europe, UK South, Australia East, entre
   otras. La lista se actualiza periódicamente.

5. **Procesamiento cross-geo no habilitado.** Incluso si la región principal del tenant
   no soporta Azure OpenAI, es posible habilitar el envío de datos a una región que sí
   lo soporte. Esto se controla con el toggle **"Data sent to Azure OpenAI can be
   processed outside your tenant's geographic region, compliance boundary, or national
   cloud instance"** en Admin Portal. Si el tenant está en una región sin soporte y este
   toggle está desactivado, Copilot no funcionará.

6. **Capacidad pausada o sobrecargada.** Si la capacidad Fabric o Premium está pausada
   (en el caso de capacidades de prueba o dev/test), o si está al límite de su SKU,
   Copilot puede no estar disponible temporalmente. Esto es más común con capacidades
   F2 (la más pequeña que soporta Copilot) bajo carga alta.

## Solución paso a paso

1. **Verificar la capacidad del workspace.** Ir al workspace en Power BI Service, hacer
   clic en **Settings** (ícono de engranaje) > **Premium**. En la sección "License mode",
   debe mostrar una capacidad Fabric (F2+) o Premium (P1+). Si muestra "None", "Shared",
   "Embedded" o "Premium Per User", el workspace no tiene capacidad válida para Copilot.
   Solicitar al administrador de capacidad que asigne el workspace a un nodo F2+ o P1+.

2. **Verificar la configuración del tenant.** Solicitar al administrador de Fabric que
   navegue a **Admin Portal > Tenant settings** y busque "Copilot and Azure OpenAI
   Service". Verificar que ambos toggles estén activados:
   - "Users can use Copilot and Azure OpenAI Service (preview)" -- **Enabled**.
   - "Data sent to Azure OpenAI can be processed outside your tenant's geographic
     region..." -- **Enabled** (especialmente si el tenant está en Latinoamérica, Asia
     u otra región sin Azure OpenAI local).

3. **Verificar pertenencia al grupo de seguridad.** En el mismo panel de tenant settings,
   verificar si Copilot está habilitado para "The entire organization" o para "Specific
   security groups". Si es para grupos específicos, confirmar que el usuario está en uno
   de esos grupos. Verificar en **Azure AD (Entra ID) > Groups** buscando el nombre del
   grupo y confirmando la membresía del usuario.

4. **Verificar el estado de la capacidad.** Ir a **Admin Portal > Capacity settings** y
   confirmar que la capacidad asignada al workspace está activa (no pausada). Si es una
   capacidad de trial, verificar que no haya expirado. Si la capacidad está
   sobrecargada, considerar escalar temporalmente o mover el workspace a otra capacidad
   con más headroom.

5. **Verificar la región.** Si todos los pasos anteriores están correctos pero Copilot
   sigue sin funcionar, verificar la región del tenant en **Admin Portal > Help + support
   > About Power BI**. Comparar con la lista de regiones soportadas en la documentación
   de Microsoft. Si la región no está soportada, habilitar el procesamiento cross-geo
   (paso 2, segundo toggle).

6. **Esperar la propagación de cambios.** Si se realizaron cambios en tenant settings o
   en la asignación de capacidad, esperar **15 a 30 minutos** antes de verificar. Los
   cambios de tenant settings no son instantáneos. Cerrar sesión y volver a iniciarla
   después del período de espera.

7. **Probar en modo incógnito.** Abrir una ventana de incógnito/privada en el navegador,
   iniciar sesión en Power BI Service e intentar usar Copilot. Esto descarta problemas
   de cache o extensiones del navegador que puedan interferir.

## Cómo prevenirlo

- **Mapear workspaces y capacidades.** Mantener un inventario actualizado de qué
  workspaces tienen capacidad F2+/P1+ y cuáles están en shared/PPU. Comunicar a los
  equipos de reporte cuáles son los workspaces habilitados para Copilot.
- **No confundir PPU con Premium.** Documentar internamente que PPU (Premium Per User)
  no habilita Copilot. Muchas organizaciones migran a PPU pensando que es equivalente
  a P1, pero para Copilot no lo es. Si Copilot es una prioridad, considerar al menos
  una capacidad F2 dedicada.
- **Habilitar cross-geo proactivamente.** Si el tenant está en una región donde Azure
  OpenAI no tiene presencia local, habilitar el procesamiento cross-geo desde el inicio.
  Consultar con el equipo de compliance antes de hacerlo si hay restricciones de
  residencia de datos.
- **Monitorear la capacidad.** Usar la app "Microsoft Fabric Capacity Metrics" para
  monitorear el uso de la capacidad. Si la capacidad se satura frecuentemente, Copilot
  puede fallar intermitentemente.
- **Incluir Copilot en el governance plan.** Definir en el plan de gobernanza de Power
  BI quiénes tienen acceso a Copilot, en qué workspaces, y bajo qué condiciones. Esto
  evita tickets de soporte recurrentes.

## Fuentes

- [Microsoft Learn - Copilot in Power BI overview](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)
- [Microsoft Learn - Enable Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi)
- [Microsoft Learn - Copilot requirements and limitations](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-requirements)
- [Microsoft Learn - Power BI Premium Per User FAQ](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-per-user-faq)
- [Microsoft Fabric Blog - Copilot availability by region](https://blog.fabric.microsoft.com/en-us/blog/copilot-in-microsoft-fabric-and-power-bi)
