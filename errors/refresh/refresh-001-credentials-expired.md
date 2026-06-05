---
id: refresh-001
title: Refresh falla - credenciales del data source inválidas o expiradas
category: refresh
severity: alta
tools: [Service, Gateway]
tags: [refresh, gateway, credentials, scheduled-refresh]
related: [conn-001]
media:
  images: []
  videos: []
---

## Síntoma

El refresh programado o manual en el Service falla con uno de estos mensajes:

> The credentials provided for the [Source] source are invalid.
>
> Failed to update data source credentials.
>
> The user name or password is incorrect.

En el panel del dataset se ve un ícono de error rojo. Los usuarios reportan que los
reportes muestran datos viejos.

## Causa

- **Contraseña vencida** del usuario que autenticó la fuente (típico cuando es una
  cuenta personal del autor que vence cada 90 días por política corporativa).
- **Cuenta de servicio rotada** sin actualizar el dataset.
- **Token OAuth expirado** (sources tipo SharePoint Online, Dynamics, Salesforce).
- **Permisos revocados** sobre el origen (el DBA quitó acceso a la base, por ejemplo).
- **Cambio en el endpoint** del source (DNS, puerto, instancia) que invalida la
  cadena de conexión cacheada.

## Solución paso a paso

1. **Identificar la fuente fallida.**
   - En el Service: `Workspace > Dataset > Settings > Data source credentials`.
   - La fuente con error muestra "Edit credentials" y un ícono de warning.

2. **Re-autenticar la fuente.**
   - Click en "Edit credentials".
   - Para SQL: elegir `Basic` con user/password actualizados o `Windows` si usa
     gateway con cuenta de servicio.
   - Para OAuth (SharePoint, etc.): hacer "Sign in" — abre popup para reautenticar.
   - Confirmar **Privacy level** acorde (Organizational en la mayoría de casos
     corporativos).

3. **Si usa Gateway on-premises**, repetir el proceso en la configuración del
   Gateway:
   - `Manage gateways > [gateway name] > Data sources > [source] > Edit credentials`.
   - Importante: las credenciales del Service y del Gateway son independientes.

4. **Probar el refresh manual** desde el dataset antes de esperar al programado.

5. **Si el error persiste**, verificar:
   - El usuario/cuenta tiene permisos vigentes sobre el origen (probar con SSMS
     u otro cliente).
   - El Gateway está online (`Manage gateways > Status: Online`).
   - No hay cambios de red/firewall que bloqueen al Gateway.

## Cómo prevenirlo

- **Usar cuentas de servicio** con contraseñas que no expiran o con rotación
  controlada, no cuentas personales del autor del reporte.
- **Documentar qué cuenta autentica cada dataset** — cuando rote, todos los datasets
  afectados son conocidos.
- **Habilitar notificaciones de failure** del refresh para enterarse antes que los
  usuarios.
- Considerar **SSO con Azure AD** para fuentes que lo soporten (elimina contraseñas
  almacenadas).

## Fuentes

- [Microsoft Docs - Troubleshooting refresh scenarios](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios)
