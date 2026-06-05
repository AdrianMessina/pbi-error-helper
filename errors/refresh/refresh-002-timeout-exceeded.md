---
id: refresh-002
title: Refresh falla por timeout - Se excede el límite de tiempo de procesamiento
category: refresh
severity: alta
tools: [Service, Gateway]
tags: [timeout, scheduled-refresh, performance, premium, pro]
related: [refresh-001, pq-004]
media:
  images: []
  videos: []
---

## Síntoma

El refresh programado o manual en el Power BI Service falla con alguno de estos
mensajes:

> Data source error - Processing timeout.

> The operation was canceled because the refresh exceeded the allowed time limit.

> Refresh timed out. The dataset refresh could not be completed within the allotted
> time.

> [Microsoft][ODBC Driver] Query timeout expired.

En el historial de refreshes (`Refresh history`), la operación aparece como `Failed`
con duración cercana al límite:
- **2 horas** para workspaces con licencia Pro / PPU.
- **5 horas** para workspaces en Premium capacity.
- **24 horas** para Premium con XMLA endpoint (refresh vía TMSL/TOM).

El reporte en el Service muestra datos desactualizados.

## Causa

El refresh tarda más del tiempo máximo permitido por la licencia/capacity. Esto ocurre
por:

- **Tablas muy grandes sin query folding**: Power Query descarga millones de filas
  a memoria para luego filtrar/transformar localmente. Ver error pq-004.
- **Múltiples fuentes lentas**: cada tabla se refresca secuencialmente y la suma
  supera el límite.
- **Full refresh en lugar de incremental**: se refresca toda la tabla histórica en
  cada ciclo en lugar de solo las particiones nuevas/modificadas.
- **Fuente de datos lenta**: el servidor SQL está sobrecargado, la API tiene rate
  limiting, o la red tiene alta latencia.
- **Transformaciones pesadas en Power Query**: pasos que consumen mucho tiempo
  (merges complejos, expansión de listas, llamadas a APIs fila por fila).
- **Gateway saturado**: demasiados datasets refrescando simultáneamente a través
  del mismo Gateway, generando contención.

## Solución paso a paso

### Paso 1 — Identificar qué tabla tarda más

1. En Power BI Desktop, activar Query Diagnostics:
   - `Power Query Editor > Tools > Start Diagnostics`
   - Refrescar el dataset.
   - `Tools > Stop Diagnostics`
2. Analizar la tabla `Diagnostics_DetailedLog`: ordenar por `Duration` para
   encontrar las tablas/pasos más lentos.
3. Alternativamente, refrescar tabla por tabla manualmente y medir tiempos.

### Paso 2 — Optimizar las queries lentas

1. **Verificar query folding** (ver pq-004):
   - Click derecho en cada paso → "View Native Query".
   - Si está grisado, el folding se rompió y la tabla se descarga completa.
2. **Reducir el volumen de datos**:
   - Filtrar por fecha: solo cargar los últimos N meses/años relevantes.
   - Eliminar columnas innecesarias lo antes posible en la query.
   - Agregar datos en el origen (vista SQL con GROUP BY) en lugar de traer el
     detalle.
3. **Mover lógica al servidor**:
   - Crear vistas SQL que hagan los joins y filtros pesados.
   - Usar `Value.NativeQuery` para pasar SQL nativo.

### Paso 3 — Configurar Incremental Refresh

Para tablas históricas que crecen continuamente:

1. En Power BI Desktop, crear dos parámetros obligatorios:
   - `RangeStart` (tipo DateTime)
   - `RangeEnd` (tipo DateTime)
2. Filtrar la tabla por estos parámetros:
   ```m
   = Table.SelectRows(Source, each [FechaTransaccion] >= RangeStart
       and [FechaTransaccion] < RangeEnd)
   ```
3. Configurar la política de incremental refresh:
   - Click derecho en la tabla en el panel de campos → `Incremental refresh`.
   - Definir período de almacenamiento (ej. 3 años) y período de refresh (ej.
     últimos 10 días).
4. Publicar al Service. A partir de ahora, solo se refrescan las particiones
   recientes.

### Paso 4 — Paralelizar el refresh (Premium)

En capacidades Premium:

1. Ir al dataset en el Service → `Settings > Scheduled refresh`.
2. Expandir `Advanced` → habilitar **"Allow parallel loading of tables"** si no
   está activo.
3. Esto permite que múltiples tablas se refresquen simultáneamente en lugar de
   secuencialmente.

### Paso 5 — Optimizar el Gateway

1. Verificar que no haya demasiados datasets refrescando al mismo tiempo:
   - En la app del Gateway → `Diagnostics > Performance Monitor`.
2. Escalonar los horarios de refresh para evitar picos de concurrencia.
3. Considerar agregar más nodos al cluster del Gateway si la carga es alta.
4. Asegurar que el servidor del Gateway tiene suficiente RAM y CPU.

### Paso 6 — Escalar la licencia si es necesario

Si después de optimizar el refresh sigue necesitando más de 2 horas:

- **Pro → Premium Per User (PPU)**: extiende el límite a 5 horas y da más
  recursos.
- **PPU → Premium capacity**: misma ventaja con recursos dedicados.
- **Premium con XMLA**: permite refreshes de hasta 24 horas usando TMSL vía
  SQL Server Management Studio o scripts.

## Cómo prevenirlo

- **Implementar Incremental Refresh** desde el inicio para cualquier tabla que
  supere las 100.000 filas y crezca con el tiempo.
- **Monitorear tiempos de refresh** regularmente. Si un refresh que tardaba 20 min
  ahora tarda 1h, investigar antes de que llegue al límite.
- **Diseñar el modelo con volúmenes de datos realistas** durante el desarrollo,
  no con muestras pequeñas.
- **Escalonar refreshes**: no programar todos los datasets a la misma hora.
- **Verificar query folding** cada vez que se modifica una query sobre una tabla
  grande.
- **Documentar el SLA de refresh**: definir cuánto tiempo debería tardar cada
  dataset y alertar si se desvía.

## Fuentes

- [Microsoft Docs - Data refresh in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data)
- [Microsoft Docs - Incremental refresh for datasets](https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview)
- [Microsoft Docs - Troubleshoot refresh scenarios](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios)
- [Microsoft Docs - On-premises data gateway performance](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-performance)
