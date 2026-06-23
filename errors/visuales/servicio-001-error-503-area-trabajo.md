---
id: servicio-001
title: Error 503 al acceder al área de trabajo
category: servicio
severity: alta
tools: [Service]
tags: [503, service-outage, workspace, availability]
search_hints:
  - "503 Service Unavailable"
  - "HTTP 503"
  - "error 503 area de trabajo"
  - "caída general de servicio"
  - "el servicio no está disponible"
  - "service unavailable power bi"
  - "no se puede abrir el area de trabajo"
related: []
media:
  images: []
  videos: []
---

## Síntoma

Al intentar abrir el área de trabajo en Power BI Service, la página devuelve:

> HTTP 503 — Service Unavailable

Tableros y modelos semánticos del workspace no abren. Otros usuarios reportan el
mismo error simultáneamente. Reintentar no resuelve.

## Causa

Caída general del servicio de Power BI o de la región de Azure donde está
hospedada la capacidad. No es un problema del modelo, del reporte ni de
permisos del usuario.

Causas frecuentes:

- Incidente regional de Microsoft (Azure / Power BI).
- Mantenimiento no anunciado en la capacidad Premium/Fabric.
- Saturación temporal del nodo de la capacidad.

## Solución paso a paso

1. **Confirmar que es un problema general** y no del propio cliente:
   - Probar abrir [app.powerbi.com](https://app.powerbi.com) desde otra red
     (datos del celular).
   - Pedir a un compañero que intente abrir el mismo workspace.

2. **Revisar el estado del servicio de Microsoft:**
   - [Microsoft 365 Service Health](https://admin.microsoft.com/servicestatus)
   - [Azure status](https://status.azure.com)
   - Filtrar por "Power BI" y por la región (Brazil South / East US, según la
     capacidad de YPF).

3. **Esperar la resolución del incidente.** No hay workaround local: si el
   Service está caído, no se puede acceder al workspace.

4. **Comunicar al equipo y a stakeholders** que es una caída de Microsoft, no
   un problema de los reportes propios. Evita escalations innecesarias.

5. Reintentar cuando Microsoft marque el incidente como resuelto.

## Cómo prevenirlo

- No depender de Power BI Service para procesos críticos en tiempo real sin un
  plan B (export a archivo, dashboard secundario).
- Suscribirse a las alertas de Service Health del tenant para enterarse del
  incidente antes que los usuarios.
- Documentar los incidentes históricos para tener referencia del MTTR típico.

## Fuentes

- [Power BI Service health and incidents](https://learn.microsoft.com/en-us/power-bi/admin/service-admin-health-incidents)
- [Azure status history](https://status.azure.com/en-us/status/history/)
