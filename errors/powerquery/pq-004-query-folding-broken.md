---
id: pq-004
title: Query folding interrumpido - Carga completa de tabla en memoria
category: powerquery
severity: media
tools: [Desktop, Service, Gateway]
tags: [query-folding, performance, native-query, SQL]
related: []
media:
  images: []
  videos: []
---

## Síntoma

No hay un mensaje de error explícito en la mayoría de los casos. En cambio, los
síntomas son:

- El refresh es **extremadamente lento** (minutos u horas) para tablas que deberían
  tardar segundos.
- El preview en Power Query tarda mucho y consume toda la RAM disponible.
- Al hacer click derecho sobre un paso y seleccionar **"View Native Query"**, la
  opción está **grisada** (no disponible), indicando que el folding se rompió.
- En el Service, el refresh falla por **timeout** o **out of memory** en tablas
  grandes que antes funcionaban.

En casos extremos, Power BI Desktop se congela o muestra:

> [DataSource.Error] The operation has been timed out.

> Processing timeout. The operation was canceled because the refresh exceeded the
> allowed time limit.

## Causa

**Query folding** es el mecanismo por el cual Power Query traduce los pasos de
transformación a una consulta nativa (SQL, OData, etc.) que se ejecuta en el servidor
de origen. Cuando el folding se interrumpe, Power Query descarga **toda la tabla
a memoria** y aplica las transformaciones localmente.

Causas de ruptura del folding:

- **Pasos no traducibles a SQL**: operaciones M que no tienen equivalente en la fuente,
  como `Table.AddColumn` con funciones M complejas, `Text.Proper`, `List.Generate`,
  `Table.Buffer`, `Table.Combine` con tablas de distinta fuente.
- **Ordenación (Sort)**: `Table.Sort` rompe el folding en muchas fuentes SQL porque
  se aplica después de un paso que ya rompió el folding.
- **Merge entre distintas fuentes**: un Merge entre una tabla SQL y un archivo Excel
  no puede ejecutarse en el servidor SQL.
- **Columnas calculadas complejas**: usar funciones M personalizadas en `Table.AddColumn`
  que no tienen equivalente SQL.
- **Cambio de tipos después de un paso no foldable**: una vez roto, los pasos
  posteriores tampoco se foldan.
- **Uso de `Table.Buffer`**: fuerza la materialización en memoria, rompiendo el
  folding para todos los pasos subsiguientes.
- **Filtros basados en otra query**: `Table.SelectRows` con referencia a otra query
  de Power Query en lugar de un valor literal.

## Solución paso a paso

### Paso 1 — Diagnosticar dónde se rompe el folding

1. Abrir Power Query Editor y seleccionar la query problemática.
2. Hacer click derecho en **cada paso** del panel `Applied Steps`, empezando desde
   arriba.
3. Si la opción **"View Native Query"** está disponible (no grisada), el folding
   sigue activo hasta ese paso.
4. El **primer paso donde "View Native Query" se grisa** es donde se rompe el folding.
5. Anotar qué transformación causa la ruptura.

### Paso 2 — Reorganizar pasos para maximizar el folding

1. **Mover los filtros y selecciones de columnas lo más arriba posible** (antes de
   los pasos que rompen el folding):
   ```m
   // BIEN: filtrar antes de transformar
   let
       Source = Sql.Database("servidor", "base"),
       Ventas = Source{[Schema="dbo",Item="Ventas"]}[Data],
       Filtrado = Table.SelectRows(Ventas, each [Año] >= 2024),  // se foldea
       Columnas = Table.SelectColumns(Filtrado, {"ID", "Monto", "Fecha"}),  // se foldea
       Calculada = Table.AddColumn(Columnas, "MontoIVA", each [Monto] * 1.21)  // puede no foldearse, pero la tabla ya está filtrada
   in
       Calculada
   ```
2. **Eliminar pasos innecesarios** que rompen el folding (sorts, buffers, tipos
   intermedios).

### Paso 3 — Usar Value.NativeQuery para forzar SQL

Si las transformaciones necesarias no son foldables, mover la lógica al servidor:

```m
let
    Source = Sql.Database("servidor", "base"),
    Resultado = Value.NativeQuery(Source,
        "SELECT ID, Monto, Monto * 1.21 AS MontoIVA
         FROM dbo.Ventas
         WHERE Año >= 2024",
        null,
        [EnableFolding = true]
    )
in
    Resultado
```

### Paso 4 — Crear una vista o stored procedure en el servidor

1. Mover la lógica pesada (filtros, joins, cálculos) a una **vista SQL** en el
   servidor.
2. En Power Query, conectar directamente a la vista:
   ```m
   Source = Sql.Database("servidor", "base"){[Schema="dbo",Item="v_Ventas_Resumen"]}[Data]
   ```
3. Así Power Query recibe datos ya procesados y filtrados.

### Paso 5 — Verificar que el folding se restauró

1. Después de reorganizar, hacer click derecho en el **último paso** de la query.
2. Verificar que "View Native Query" esté disponible.
3. Revisar la query SQL generada para confirmar que incluye los filtros WHERE, las
   columnas SELECT y los JOINs esperados.

## Cómo prevenirlo

- **Verificar el folding en cada paso nuevo** que se agrega a una query crítica.
  Acostumbrarse a revisar "View Native Query" regularmente.
- **Filtrar y seleccionar columnas lo antes posible** en la secuencia de pasos.
- **Evitar `Table.Buffer`** a menos que sea estrictamente necesario.
- **Preferir operaciones foldables**: `Table.SelectRows`, `Table.SelectColumns`,
  `Table.Sort` (si está inmediatamente después de Source), `Table.Group`,
  `Table.Join` (misma fuente).
- **Para tablas grandes (millones de filas)**, mover lógica al servidor con vistas
  o procedimientos almacenados.
- **Habilitar Query Diagnostics** (`Tools > Start Diagnostics`) para ver qué queries
  se envían realmente al servidor y detectar cargas completas de tabla.
- Documentar en el equipo qué operaciones M son foldables y cuáles no para la fuente
  específica que usan.

## Fuentes

- [Microsoft Docs - Query folding in Power Query](https://learn.microsoft.com/en-us/power-query/query-folding-basics)
- [Microsoft Docs - Query folding indicators](https://learn.microsoft.com/en-us/power-query/step-folding-indicators)
- [Microsoft Docs - Query diagnostics](https://learn.microsoft.com/en-us/power-query/query-diagnostics)
- [Microsoft Docs - Value.NativeQuery](https://learn.microsoft.com/en-us/powerquery-m/value-nativequery)
