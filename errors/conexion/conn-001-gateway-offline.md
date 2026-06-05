---
id: conn-001
title: On-premises data gateway offline
category: conexion
severity: alta
tools: [Service, Gateway]
tags: [gateway, on-premises, connectivity, refresh]
related: [refresh-001]
media:
  images: []
  videos: []
---

## Síntoma

En el Service:

> The gateway you are using is offline. Please check the gateway status and try
> again.

Cualquier dataset que dependa de ese Gateway no refresca. En `Manage gateways` el
estado aparece como **Offline** o **Unable to contact**.

## Causa

- El servicio Windows del Gateway está detenido en el servidor host.
- El servidor host está apagado / reiniciado / sin red.
- El proxy o firewall corporativo bloquea el outbound del Gateway hacia los
  endpoints de Azure.
- La cuenta bajo la que corre el servicio del Gateway perdió permisos.
- Versión del Gateway muy antigua y rechazada por el Service.

## Solución paso a paso

1. **Verificar el servicio en el servidor del Gateway.**
   - Conectarse al servidor.
   - `services.msc` → buscar `On-premises data gateway service`.
   - Si está `Stopped` → click derecho → `Start`.

2. **Si el servicio no arranca**, revisar el event log:
   - `Event Viewer > Applications and Services > Power BI Gateway`.
   - Errores comunes: cuenta de servicio bloqueada, puerto en uso, certificados.

3. **Verificar conectividad outbound** del servidor a:
   - `*.servicebus.windows.net` (puerto 443 y 5671-5672)
   - `*.powerbi.com`, `*.azure.com`
   - Test desde el servidor:
     ```powershell
     Test-NetConnection -ComputerName servicebus.windows.net -Port 443
     ```

4. **Reiniciar el Gateway** desde la app de configuración:
   - Abrir `On-premises data gateway` (app de escritorio en el servidor).
   - `Service Settings` → `Restart now`.

5. **Si la versión es vieja**, descargar la última desde
   [powerbi.microsoft.com/gateway](https://powerbi.microsoft.com/gateway/) e
   instalar sobre la existente.

6. Confirmar en el Service que el estado pasó a **Online**.

## Cómo prevenirlo

- **Monitor del servidor host** (uptime, recursos, disco).
- **Alertas de estado del Gateway** (PowerShell `Get-DataGatewayStatus` + scheduled
  task que avisa por mail).
- **Actualizar el Gateway mensualmente** — Microsoft saca releases con frecuencia
  y eventualmente fuerza upgrade.
- **Cuenta de servicio dedicada** para el Gateway, no la cuenta de un usuario
  individual que se puede ir de la empresa.

## Fuentes

- [Microsoft Docs - Troubleshoot the on-premises data gateway](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-tshoot)
