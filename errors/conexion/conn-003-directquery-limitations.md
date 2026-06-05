---
id: conn-003
title: DirectQuery - Visual excede los recursos disponibles o rendimiento muy lento
category: conexion
severity: media
tools: [Desktop, Service]
tags: [DirectQuery, performance, visual-limit, live-connection]
related: []
media:
  images: []
  videos: []
---

## Síntoma

Al interactuar con un reporte en modo DirectQuery, los usuarios experimentan:

> This visual has exceeded the available resources. Try filtering to decrease the
> amount of data displayed.

> Couldn't load the data for this visual.

> Query was cancelled by the data source because it exceeded the allowed resource
> limits.

> The query was canceled because the estimated cost of this query exceeds the
> configured threshold.

Otros síntomas sin mensaje de error explícito:

- Los visuals tardan **10-30+ segundos** en renderizar después de cada interacción
  (click en un slicer, hover, drill-down).
- Slicers con listas largas tardan mucho en cargar las opciones.
- El reporte se siente "trabado" comparado con reportes en Import mode.
- En el Service, los usuarios abandonan el reporte porque la experiencia es
  inaceptable.
- El equipo de DBA reporta queries pesadas y constantes viniendo de Power BI.

## Causa

En modo **DirectQuery**, Power BI no almacena datos. Cada interacción del usuario
(cambiar un filtro, hacer drill-down, pasar el mouse sobre un visual) genera una
o más queries SQL que se envían al servidor de origen en tiempo real.

Causas del mal rendimiento o errores de recursos:

- **Visuals con demasiadas filas/cardinalidad**: un visual tipo tabla mostrando
  miles de filas, o un gráfico de barras con cientos de categorías, genera queries
  masivas.
- **Muchos visuals en una sola página**: cada visual genera su propia query. Una
  página con 15+ visuals genera 15+ queries simultáneas al origen cada vez que
  cambia un filtro.
- **Medidas DAX complejas**: DAX se traduce a SQL. Medidas con muchos CALCULATE,
  FILTER, iteradores (SUMX, AVERAGEX), o funciones de time intelligence generan
  SQL subóptimo o no traducible.
- **Modelo mal diseñado para DirectQuery**: tablas con muchas columnas, relaciones
  many-to-many, o bidirectional filtering generan JOINs costosos.
- **Servidor de origen lento**: el SQL Server / Azure SQL / Synapse no tiene los
  índices, estadísticas o recursos necesarios para responder rápidamente.
- **Límites del conector**: Power BI impone un timeout de **225 segundos** por
  query DirectQuery y un límite de **1 millón de filas** por query.
- **Sin aggregations ni caching**: cada interacción va al origen sin caché
  intermedio (salvo que se configuren aggregations o automatic page refresh con
  caché).

## Solución paso a paso

### Paso 1 — Diagnosticar las queries generadas

1. Abrir **DAX Studio** y conectar al modelo.
2. Activar `All Queries` trace.
3. Interactuar con el reporte en Power BI Desktop.
4. Revisar en DAX Studio:
   - Las queries DAX generadas por cada visual.
   - El SQL generado (expandir la query para ver el "DirectQuery" statement).
   - La duración de cada query.
5. Identificar los visuals y medidas que generan las queries más lentas.

### Paso 2 — Reducir el número de visuals por página

1. **Limitar a 8-10 visuals** por página como máximo. Cada visual es una query al
   origen.
2. Mover visuals de detalle a páginas de drill-through:
   - El usuario hace click en un valor → navega a una página con detalle.
   - La página de drill-through solo genera queries cuando se accede.
3. Usar **bookmarks** para alternar entre conjuntos de visuals en la misma página
   (solo los visibles generan queries).

### Paso 3 — Optimizar los visuals

1. **Limitar la cardinalidad visible**:
   - Usar filtros TopN para mostrar solo los Top 10/20 en gráficos.
   - Evitar tablas/matrices sin filtros que intenten cargar miles de filas.
2. **Deshabilitar interacciones innecesarias**:
   - `Format > Edit Interactions` → desactivar el cross-filtering entre visuals
     que no necesitan interactuar.
   - Cada interacción que se desactiva es una query menos al hacer click.
3. **Evitar visuals que generan muchas queries**:
   - Scatter plots con miles de puntos.
   - Matrices muy expandidas.
   - Cards con medidas complejas de time intelligence.

### Paso 4 — Simplificar las medidas DAX

1. Evitar iteradores sobre tablas grandes:
   ```dax
   // EVITAR en DirectQuery
   TotalPonderado = SUMX(Ventas, Ventas[Cantidad] * Ventas[PrecioUnitario])

   // PREFERIR: crear columna calculada en el origen
   TotalPonderado = SUM(Ventas[MontoTotal])
   ```
2. Minimizar el uso de `CALCULATE` con múltiples filtros anidados.
3. Mover cálculos complejos al servidor de origen (columnas calculadas en SQL,
   vistas).

### Paso 5 — Optimizar el servidor de origen

1. **Crear índices** sobre las columnas usadas en filtros, relaciones y GROUP BY:
   ```sql
   CREATE NONCLUSTERED INDEX IX_Ventas_Fecha
   ON dbo.Ventas (FechaVenta)
   INCLUDE (MontoTotal, CategoriaID);
   ```
2. **Actualizar estadísticas**:
   ```sql
   UPDATE STATISTICS dbo.Ventas;
   ```
3. **Crear vistas materializadas o indexed views** para consultas frecuentes.
4. **Monitorear las queries de Power BI** con SQL Profiler o Extended Events
   para identificar queries lentas y optimizar con índices.

### Paso 6 — Implementar Aggregations (modelo híbrido)

Para tener lo mejor de ambos mundos (velocidad de Import + frescura de DirectQuery):

1. Crear una tabla de agregación en Import mode con los datos resumidos:
   - Ej: ventas diarias por categoría en lugar de cada transacción.
2. Configurar `Manage Aggregations` en la tabla de agregación para que Power BI
   la use automáticamente cuando sea posible.
3. Las queries de alto nivel (cards, gráficos de tendencia) usan la agregación
   importada (rápido).
4. Los drill-downs a detalle van a DirectQuery (datos frescos).

### Paso 7 — Considerar cambiar a Import mode o Composite

Si el rendimiento sigue siendo inaceptable:

- **Composite model**: tablas de hechos principales en Import, tablas de referencia
  o tiempo real en DirectQuery.
- **Import mode completo**: si los datos no necesitan ser real-time y el volumen
  es manejable, Import mode siempre será más rápido.

## Cómo prevenirlo

- **Evaluar si DirectQuery es realmente necesario** antes de elegirlo. Solo usar
  DirectQuery cuando se necesita datos en tiempo real o el volumen es demasiado
  grande para Import.
- **Diseñar el reporte pensando en DirectQuery**: menos visuals, menos
  interacciones, medidas simples.
- **Preparar el servidor de origen**: índices, estadísticas, recursos adecuados.
  Involucrar al DBA desde el inicio del proyecto.
- **Usar Performance Analyzer** en Power BI Desktop (`View > Performance Analyzer`)
  para medir tiempos de render y query de cada visual durante el desarrollo.
- **Establecer un SLA de rendimiento**: cada visual debería renderizar en menos de
  3 segundos. Si no, optimizar o rediseñar.

## Fuentes

- [Microsoft Docs - DirectQuery model guidance](https://learn.microsoft.com/en-us/power-bi/guidance/directquery-model-guidance)
- [Microsoft Docs - DirectQuery in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-directquery-about)
- [Microsoft Docs - Use composite models](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-composite-models)
- [Microsoft Docs - Aggregations in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-aggregations)
