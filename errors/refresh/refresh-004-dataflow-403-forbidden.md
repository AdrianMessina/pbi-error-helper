---
id: refresh-004
title: Refresh falla con 403 Forbidden al consumir Dataflow
category: refresh
severity: alta
tools: [Service, Gateway]
tags: [Dataflow, "403", Forbidden, credentials, OAuth, workspace-permissions, DataFormat.Error]
related: [refresh-001, pq-003]
media:
  images: []
  videos: []
---

## Síntoma

El refresh del modelo semántico falla con un error similar a:

> PowerPlatformDataflows018
> Downstream service call .../clusterdetails failed with status code 403
> DataFormat.Error: We reached the end of the buffer.

En el historial de refresh se ven detalles como `status code 403` (Forbidden) y un
error secundario `DataFormat.Error: We reached the end of the buffer` que aparece
porque el conector intenta procesar una respuesta vacía o inesperada después del
rechazo de acceso.

El modelo semántico consume un Dataflow (Gen1 o Gen2) como origen de datos, y el
refresh funcionaba anteriormente pero dejó de funcionar.

## Causa

El código `403 Forbidden` indica que el servicio no tiene autorización válida para
acceder al Dataflow o a su workspace. Las causas más probables:

1. **Credenciales OAuth vencidas o rotas** en la configuración del modelo semántico.
   Los tokens de acceso expiran periódicamente y si no se renuevan, el refresh falla.

2. **El usuario dueño del refresh ya no tiene permisos** sobre el workspace donde
   está el Dataflow. Si lo cambiaron de área, le revocaron acceso, o se fue de la
   empresa, el refresh hereda su (ahora inválida) identidad.

3. **Permisos insuficientes sobre el Dataflow.** Para consumir un Dataflow Gen2 con
   el conector Power Platform Dataflows se requiere rol **Admin, Member o
   Contributor** en el workspace del Dataflow. El rol **Viewer no alcanza**.

4. **El Dataflow fue movido, eliminado o recreado.** Si el Dataflow se borró y se
   volvió a crear, el ID interno cambia y la conexión del modelo apunta a un recurso
   que ya no existe o tiene otro propietario.

5. **El Dataflow no está actualizado.** Microsoft requiere que un Dataflow se
   refresque exitosamente antes de que un modelo semántico pueda consumirlo. Si el
   refresh del Dataflow falla, el modelo que lo consume también falla.

6. **Cambio en políticas del tenant o Conditional Access** que bloquea el token del
   service principal o del usuario.

## Solución paso a paso

### 1. Re-autenticar las credenciales del Dataflow

1. En Power BI Service, ir al **modelo semántico** que falla.
2. Click en **Settings** (ícono de engranaje) → **Data source credentials** o
   **Gateway and cloud connections**.
3. Buscar la conexión de tipo **Power Platform Dataflows / Dataflows**.
4. Click en **Edit credentials** → iniciar sesión con cuenta organizacional.
5. Confirmar **Privacy level** = Organizational.
6. Click **Sign in** y guardar.

### 2. Verificar o tomar control del dataset

Si el dueño original del dataset ya no tiene acceso:

1. En el workspace, buscar el modelo semántico.
2. Click en **...** → **Settings** → **Take over** (Tomar control).
3. Esto reasigna la propiedad al usuario actual.
4. Después de tomar control, volver a configurar **todas** las credenciales de
   las fuentes de datos.

### 3. Verificar permisos en el workspace del Dataflow

1. Ir al workspace donde está el Dataflow.
2. Click en **Access** (panel de permisos).
3. Confirmar que la cuenta que autentica el refresh tiene rol **Admin, Member o
   Contributor** — **no** Viewer.
4. Si es Viewer, solicitar upgrade de permisos al admin del workspace.

### 4. Verificar que el Dataflow esté actualizado

1. Ir al workspace del Dataflow.
2. Abrir el Dataflow y verificar que el último refresh fue exitoso.
3. Si el Dataflow tiene refresh programado, confirmar que esté activo y no falle.
4. Refrescar el Dataflow manualmente primero.
5. **Después** de que el Dataflow refresque OK, refrescar el modelo semántico.

### 5. Si el Dataflow fue recreado

1. Abrir el modelo semántico en Power BI Desktop.
2. En Power Query Editor, ir al paso de Source del query que conecta al Dataflow.
3. Re-seleccionar el Dataflow correcto desde el nuevo workspace/ID.
4. Publicar de nuevo al Service.
5. Reconfigurar credenciales.

### 6. Si usa Gateway

1. Ir a **Manage gateways** → seleccionar el gateway.
2. Verificar que las data sources del gateway incluyan la conexión al Dataflow.
3. Verificar que las credenciales del gateway sean válidas.

## Cómo prevenirlo

- **Usar cuentas de servicio** para el ownership de datasets que consumen Dataflows,
  no cuentas personales que pueden perder acceso.
- **Monitorear el refresh del Dataflow** antes que el del dataset. Si el Dataflow
  falla, el dataset va a fallar después.
- **Documentar la cadena de dependencias**: qué modelo consume qué Dataflow, en qué
  workspace, con qué cuenta. Cuando alguien se va del equipo, hay que transferir.
- **Configurar alertas de refresh failure** tanto en el Dataflow como en el dataset.
- Revisar permisos periódicamente, especialmente después de reorganizaciones de
  workspaces o cambios de personal.

## Fuentes

- [Microsoft Docs - Configure and consume a dataflow](https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-configure-consume)
- [Microsoft Docs - Power Platform Dataflows connector](https://learn.microsoft.com/en-us/power-query/connectors/dataflows)
- [Microsoft Docs - Troubleshooting dataflow connection issues](https://learn.microsoft.com/en-us/power-query/dataflows/troubleshooting-dataflow-issues-connection-to-the-data-source)
