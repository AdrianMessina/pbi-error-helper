---
id: refresh-003
title: Refresh falla por memoria insuficiente en la capacity
category: refresh
severity: alta
tools: [Service, Gateway]
tags: [memory, capacity, out-of-memory, premium, pro]
related: [refresh-002]
media:
  images: []
  videos: []
---

## Síntoma

El refresh falla en el Power BI Service con alguno de estos mensajes:

> Resource governing: memory. The operation was cancelled because there weren't
> enough resources to complete it.

> Errors in the high-level relational engine. The following exception occurred while
> the managed IDbConnection interface was being used: Insufficient memory to continue
> the execution of the program.

> Memory error: The operation was canceled because there wasn't enough memory to
> complete it. Reduce the size of the model or increase the capacity.

> Failed to execute the command because the server does not have enough memory.

En el Gateway, el log puede mostrar:

> System.OutOfMemoryException: Exception of type 'System.OutOfMemoryException'
> was thrown.

El dataset no se actualiza y los reportes muestran datos desactualizados. En la
app de Premium Capacity Metrics se observa un pico de consumo de memoria cercano
al 100%.

## Causa

Durante el refresh, Power BI necesita mantener en memoria tanto el **modelo actual**
(para que los reportes sigan funcionando) como los **datos nuevos** que se están
procesando. Esto significa que el consumo de memoria puede ser hasta el **doble**
del tamaño del dataset durante el refresh.

Causas específicas:

- **Dataset demasiado grande para la capacity**: un dataset de 5 GB en una capacity
  Premium P1 (25 GB de RAM compartida entre todos los datasets del nodo) puede
  fallar si hay otros datasets activos consumiendo memoria.
- **Licencia Pro/PPU con límite de 1 GB**: el dataset supera el límite de 1 GB
  por dataset (Pro) o 100 GB (PPU). Pro tiene un límite estricto de 1 GB para el
  tamaño del .pbix publicado.
- **Cardinalidad excesiva**: columnas con millones de valores únicos (IDs de
  transacción, timestamps con segundos, GUIDs) consumen mucha más memoria que
  columnas con baja cardinalidad.
- **Columnas innecesarias**: importar todas las columnas de tablas anchas cuando
  solo se usan unas pocas.
- **Tipos de datos ineficientes**: usar `Text` para columnas que deberían ser
  `Number` o `Date`. Los textos largos consumen significativamente más memoria.
- **Tablas desnormalizadas**: una sola tabla plana con datos repetidos en lugar
  de un esquema estrella normalizado.
- **Power Query con operaciones que bufferizan**: `Table.Buffer`, `List.Buffer`,
  o pasos que materializan tablas completas en memoria.
- **Contención en el Gateway**: el servidor del Gateway no tiene suficiente RAM
  para procesar el volumen de datos durante la extracción.

## Solución paso a paso

### Paso 1 — Medir el tamaño real del modelo

1. En Power BI Desktop, ir a `File > Options > Diagnostics` y tomar nota del
   puerto local.
2. Conectar DAX Studio al modelo local.
3. Ejecutar en DAX Studio: `View > Model Metrics` o usar VertiPaq Analyzer.
4. Identificar:
   - Las tablas más grandes (por filas y por tamaño en memoria).
   - Las columnas con mayor cardinalidad.
   - Las columnas que más memoria consumen.

### Paso 2 — Reducir el tamaño del modelo

#### A. Eliminar columnas innecesarias

1. En Power Query, usar `Table.SelectColumns` o `Remove Columns` para quedarse
   solo con las columnas necesarias.
2. Columnas típicamente innecesarias: IDs surrogate no usados en relaciones,
   descripciones largas, campos de auditoría (CreatedBy, ModifiedDate), columnas
   duplicadas.

#### B. Reducir cardinalidad

1. **Timestamps**: redondear a hora o día si no se necesita precisión al segundo:
   ```m
   = Table.TransformColumns(Source, {{"Fecha", DateTime.Date, type date}})
   ```
2. **IDs de transacción**: si solo se usan para conteo, considerar no importarlos
   y usar una medida `COUNTROWS` en lugar de `DISTINCTCOUNT([TransactionID])`.
3. **Textos largos**: truncar o categorizar si es posible.

#### C. Optimizar tipos de datos

1. Cambiar `Text` a `Number` donde corresponda.
2. Cambiar `DateTime` a `Date` si no se necesita la hora.
3. Usar `Int64` en lugar de `Decimal Number` para enteros.

#### D. Normalizar el modelo

1. Separar tablas planas en un esquema estrella:
   - Tabla de hechos con las métricas y claves foráneas.
   - Tablas de dimensiones con los atributos descriptivos.
2. Esto reduce drásticamente la repetición de datos en memoria.

### Paso 3 — Filtrar datos históricos

1. Solo importar los datos necesarios para el análisis. Si el reporte cubre los
   últimos 3 años, no importar 10 años de historia.
2. Implementar **Incremental Refresh** para tablas grandes (ver refresh-002).
3. Para datos históricos que se consultan raramente, considerar un modelo separado
   o DirectQuery.

### Paso 4 — Escalar la capacity

Si el modelo ya está optimizado y sigue sin caber:

| Licencia | Límite por dataset | RAM total |
|----------|-------------------|-----------|
| Pro | 1 GB | Compartida |
| PPU | 100 GB | Compartida |
| Premium P1 | 25 GB | 25 GB |
| Premium P2 | 50 GB | 50 GB |
| Premium P3 | 100 GB | 100 GB |

1. Verificar en `Premium Capacity Metrics` el uso de memoria actual.
2. Si la capacity está saturada:
   - Mover datasets menos críticos a otra capacity.
   - Escalar al siguiente SKU.
   - Habilitar `Large dataset format` en la configuración del dataset (permite
     datasets mayores a 10 GB en Premium).

### Paso 5 — Optimizar el Gateway

Si el error es OutOfMemoryException en el Gateway:

1. Verificar RAM disponible en el servidor (`Task Manager > Performance`).
2. Aumentar la RAM del servidor del Gateway (mínimo 8 GB, recomendado 16+ GB).
3. Escalonar refreshes para que no se ejecuten simultáneamente muchos datasets
   pesados.
4. Configurar `MaxConcurrentRefreshes` en el Gateway para limitar la concurrencia.

## Cómo prevenirlo

- **Monitorear el tamaño del modelo** con DAX Studio / VertiPaq Analyzer en cada
  release. Establecer un presupuesto de memoria (ej. "este modelo no debe superar
  2 GB").
- **Diseñar en esquema estrella** desde el inicio. Evitar tablas planas
  desnormalizadas.
- **Eliminar columnas agresivamente**: si una columna no se usa en una relación,
  un visual, una medida o un filtro, no debería estar en el modelo.
- **Reducir cardinalidad proactivamente**: no importar timestamps con precisión
  innecesaria, GUIDs, o textos largos.
- **Usar Incremental Refresh** para tablas de hechos grandes.
- **Revisar el modelo antes de publicar**: ejecutar VertiPaq Analyzer y verificar
  que no haya columnas sorpresivamente grandes.

## Fuentes

- [Microsoft Docs - Manage your data storage in workspaces](https://learn.microsoft.com/en-us/power-bi/admin/service-admin-manage-your-data-storage-in-power-bi)
- [Microsoft Docs - Large datasets in Power BI Premium](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-large-models)
- [Microsoft Docs - Optimization guide for Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)
- [SQLBI - VertiPaq Analyzer](https://www.sqlbi.com/tools/vertipaq-analyzer/)
