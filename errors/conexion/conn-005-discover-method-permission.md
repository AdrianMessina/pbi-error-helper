---
id: conn-005
title: User does not have permission to call the Discover method
category: conexion
severity: media
tools: [Desktop, Service]
tags: [permissions, analysis-services, discover, dataset-linked, mashup]
search_hints:
  - "does not have permission to call the Discover method"
  - "no tiene permiso para llamar al método Discover"
  - "Microsoft.Data.Mashup.ErrorCode = 10478"
  - "DataSource.Error AnalysisServices"
  - "error al cargar metricas de uso"
  - "error mashup discover"
  - "el usuario no tiene permisos en analysis services"
related: [conn-008]
media:
  images: [conn-005-fig1.png, conn-005-fig2.png]
  videos: []
---

## Síntoma

Al cargar las métricas de uso de un reporte o al refrescar un modelo que se
conecta a otro modelo semántico, aparece:

> DataSource.Error: AnalysisServices: The 'RY22146@grupo.ypf.com' user does not
> have permission to call the Discover method.
>
> Microsoft.Data.Mashup.ErrorCode = 10478.
> Microsoft.Data.Mashup.ValueError.DataSourceKind = AnalysisServices.
> DataSourcePath = powerbi://api.powerbi.com/v1.0/myorg/...

El usuario que abrió el reporte no puede ver los datos aunque tenga acceso al
reporte en sí.

## Causa

El reporte (o las métricas de uso) está consumiendo datos desde **otro modelo
semántico** alojado en otra área de trabajo. El usuario tiene acceso al reporte
de origen, pero **no al modelo semántico subyacente**, así que el servicio
rechaza la llamada `Discover` que necesita para leer la metadata del modelo.

Es habitual cuando:

- El reporte usa **conexión en vivo** a un modelo central compartido (golden
  dataset).
- Las **métricas de uso** intentan agregarse usando otro reporte como fuente.
- Se publicó un reporte basado en un modelo de un workspace al que el usuario
  consumidor no fue agregado.

## Solución paso a paso

1. **Identificar el modelo semántico subyacente** desde el mensaje:
   - El campo `DataSourcePath` muestra el nombre del workspace y del modelo
     (ej. `bi vpc;PAI NETO [USD]`).

2. **Pedir acceso al workspace o al modelo:**
   - Identificar al *facilitador del dato* / dueño del modelo.
   - Solicitar el permiso **Build** (Compilar) sobre el modelo semántico.
     Sin `Build`, no se puede consumir desde otro reporte.

3. **Verificar el acceso desde el Service:**
   - Workspace del modelo → modelo semántico → `Manage permissions` → el
     usuario debe figurar con `Build` o ser miembro del workspace con rol
     Contributor o superior.

4. **Refrescar la página del reporte.** Si era un cache antiguo, puede tardar
   unos minutos en propagarse.

5. Si el reporte es de métricas de uso de Power BI, repetir la solicitud
   también sobre el modelo de **Usage Metrics Report** generado por la app.

## Cómo prevenirlo

- Documentar qué modelos son "centrales/golden" y mantener un grupo de
  seguridad con permiso `Build` sobre ellos.
- Antes de compartir un reporte que usa conexión en vivo, validar que el
  destinatario tenga acceso al modelo subyacente.
- Para modelos sensibles, configurar **Row-Level Security (RLS)** en lugar de
  bloquear el acceso al modelo entero.

## Fuentes

- [Microsoft Docs - Build permission](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-build-permissions)
- [Troubleshoot Power BI permissions](https://learn.microsoft.com/en-us/power-bi/admin/service-admin-troubleshoot-power-bi)
