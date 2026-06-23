---
id: refresh-005
title: One or more upstream operations failed
category: refresh
severity: media
tools: [Service, Gateway]
tags: [refresh, upstream, gateway, dependency, request-id]
search_hints:
  - "One or more upstream operations failed"
  - "una o mas operaciones upstream fallaron"
  - "upstream operations failed Request ID"
  - "error upstream refresh"
  - "one more operation failed"
related: [refresh-001, refresh-002, conn-001]
media:
  images: []
  videos: []
---

## Síntoma

Al refrescar un modelo semántico (manual o programado), el Service muestra:

> Error: One or more upstream operations failed.
> Request ID: ce96a1b3-0af2-7c8d-bac6-b89ccc1980f5.

El refresh aborta. No queda claro *qué* upstream falló — el mensaje es
genérico.

## Causa

Power BI evaluó una o más queries del modelo y al menos una falló por una
operación previa en la cadena. El mensaje "upstream" indica que el problema
está en un paso anterior, no en el último paso visible.

Causas frecuentes:

- Una fuente de datos cayó (Teradata, SAP, SQL) → el paso de extracción
  rompe y todos los pasos que dependen de él fallan en cascada.
- Una credencial de la fuente expiró o fue revocada → ver `refresh-001`.
- Una **dataflow** o **modelo upstream** del que dependen estas queries está
  con error o no refrescó.
- El Gateway está offline → ver `conn-001`.
- La query en Power Query referencia una tabla que cambió de nombre o se
  borró aguas arriba.

## Solución paso a paso

1. **Capturar el Request ID** del mensaje. Es la pista principal para
   debuggear desde el portal admin o pedir soporte a Microsoft.

2. **Identificar qué fuentes usa el modelo:**
   - Workspace → modelo semántico → `Settings` → `Data source credentials`
     y `Parameters`.
   - Anotar cada datasource configurado.

3. **Verificar cada fuente upstream:**
   - **Gateway online?** Workspace → `Manage gateways` → estado.
   - **Credenciales válidas?** Settings → `Data source credentials` →
     `Edit credentials`. Re-autenticar si está expirado.
   - **La query funciona en Desktop?** Abrir el `.pbix` y refrescar tabla
     por tabla — la primera que falla es la culpable.

4. **Si depende de dataflows/modelos upstream:**
   - Confirmar que los dataflows refrescaron OK (Workspace del dataflow →
     `Refresh history`).
   - Si algún dataflow está fallando, ahí está el problema raíz — resolver
     ese refresh primero.

5. **Revisar el Refresh History detallado:**
   - Service → modelo → `Refresh history` → click en la fila fallida →
     `Show details`. El detalle suele indicar la tabla específica.

6. **Re-encolar el refresh** una vez resuelto el upstream y validar que
   completa.

## Cómo prevenirlo

- Documentar el árbol de dependencias del modelo (qué dataflows, qué
  databases, qué credenciales). Saberlo de memoria acelera el debug.
- Configurar **alertas de refresh fallido** sobre los modelos críticos
  (Power Automate o Monitoring Hub).
- Cuando un upstream va a cambiar (renombre de tabla, migración de schema),
  comunicarlo a los dueños de los modelos consumidores antes del cambio.

## Fuentes

- [Microsoft - Troubleshoot refresh scenarios](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios)
- [Power BI Monitoring Hub](https://learn.microsoft.com/en-us/power-bi/admin/service-admin-monitoring-hub)
