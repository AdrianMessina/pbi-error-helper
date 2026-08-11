---
id: pq-002
title: No se puede guardar el flujo de datos - Error desconocido
category: powerquery
severity: media
tools: [Service, Dataflows]
tags: [dataflow, power-query, API, permisos, origen-datos]
related: [pq-001, conn-001]
media:
  images: ["Error desconocido la API no devolvio un mensaje de error.png"]
  videos: []
---

## Síntoma

Al intentar guardar un flujo de datos en el Power BI Service, aparece:

> No se puede guardar el flujo de datos
> Error desconocido: la API no devolvió un mensaje de error

El flujo de datos no se crea y no hay detalles adicionales en el mensaje de error.

## Causa

Este error genérico puede tener varias causas subyacentes:

- **Falta de permisos** en el workspace para crear o modificar flujos de datos.
- **Falta de permisos** en el origen de datos al que intenta conectarse el flujo.
- **Capacidad insuficiente** o límites alcanzados en Premium/PPU.
- **Timeout** en la validación de la query por queries muy complejas o lentas.
- Problemas temporales de conectividad entre el Service y el origen de datos.

## Solución paso a paso

### Opción A — Verificar permisos en el workspace

1. En el workspace donde intentás crear el flujo de datos:
   - `Settings > Access`
   - Verificar que tu rol sea **Admin**, **Member** o **Contributor** (Viewer no puede crear dataflows).
2. Si no tenés permisos, solicitar el rol adecuado al admin del workspace.

### Opción B — Reutilizar un flujo de datos existente

Si el problema es de permisos en el origen de datos:

1. Verificar si ya existe un **flujo de datos** con acceso a la misma fuente.
2. En lugar de crear uno nuevo:
   - Usar **Get Data > Dataflows** en Power BI Desktop o en otra query del Service.
   - Conectarse al flujo existente y consumir las tablas necesarias.
3. Esto evita tener que pedir credenciales nuevas en el origen.

### Opción C — Cambiar el origen de datos en Power Query

Si la fuente original no es accesible:

1. Abrir el dataflow draft o el query en **Power Query Editor**.
2. `Home > Data source settings` → seleccionar el origen problemático.
3. **Change Source** y reemplazar por:
   - Una fuente a la que sí tengas acceso (ej: SharePoint List, Excel en OneDrive).
   - Un flujo de datos intermediario que ya tenga los datos.
4. Aplicar cambios y reintentar guardar el flujo de datos.

### Opción D — Solicitar acceso a la base de datos

Si necesitás acceso directo a la fuente (SQL Server, Oracle, etc.):

1. Identificar el servidor y base de datos en el connection string.
2. Contactar al DBA o administrador de la base de datos.
3. Solicitar:
   - **Permisos de lectura** (`db_datareader`) en las tablas necesarias.
   - Agregarte al **Gateway** (si es on-premises) con las credenciales correctas.
4. Una vez otorgados los permisos, reintentar crear el dataflow.

## Cómo prevenirlo

- **Centralizar flujos de datos**: crear un workspace dedicado a dataflows corporativos donde se mantengan las conexiones a fuentes críticas con permisos ya establecidos.
- **Documentar fuentes de datos**: mantener un registro de qué flujos de datos acceden a qué fuentes, para reutilizar en lugar de duplicar.
- **Solicitar permisos temprano**: al iniciar un proyecto, identificar las fuentes necesarias y pedir acceso antes de empezar a diseñar.
- **Usar roles de servicio**: para conexiones a bases de datos, usar cuentas de servicio dedicadas en lugar de cuentas individuales.

## Fuentes

- [Microsoft Docs - Dataflows best practices](https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-best-practices)
- [Power BI Community - Dataflow error troubleshooting](https://community.powerbi.com)
