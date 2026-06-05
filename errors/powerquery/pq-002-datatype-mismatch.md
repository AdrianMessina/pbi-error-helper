---
id: pq-002
title: Data type mismatch en merge, append u operaciones de columna
category: powerquery
severity: media
tools: [Desktop, Service, Gateway]
tags: [data-type, merge, append, conversion, Expression.Error]
related: [pq-001]
media:
  images: []
  videos: []
---

## Síntoma

Al ejecutar un merge, append o una transformación sobre una columna en Power Query
Editor, aparece alguno de estos mensajes:

> Expression.Error: We cannot convert the value "ABC" to type Number.

> Expression.Error: We cannot convert the value null to type Text.

> Expression.Error: We cannot apply operator + to types Text and Number.

> DataFormat.Error: We couldn't convert to Number.

En un Merge (Join), el error se muestra al intentar vincular dos columnas cuyo tipo
no coincide:

> Expression.Error: We cannot convert the value 12345 to type Text.

El paso fallido queda marcado en rojo y la preview de la tabla desaparece o muestra
"Error" en las celdas afectadas.

## Causa

Power Query utiliza tipado fuerte: cada columna tiene un tipo definido (text, number,
date, datetime, etc.) y las operaciones entre tipos incompatibles generan error.

Disparadores frecuentes:

- **Merge con claves de distinto tipo**: una tabla tiene la columna clave como `Text`
  (ej. "00123") y la otra como `Number` (ej. 123). Aunque visualmente parezcan iguales,
  el merge falla o devuelve cero coincidencias.
- **Append de tablas con la misma columna en tipos distintos**: la tabla A tiene
  "Monto" como `Number` y la tabla B como `Text` (porque contiene valores como "N/A").
  Al hacer Append, Power Query intenta convertir y falla.
- **Cambio de tipo implícito por "Changed Type" automático**: Power Query inserta un
  paso `Changed Type` al cargar datos. Si la primera fila de una columna parece número
  pero filas posteriores contienen texto, la conversión falla en esas filas.
- **Valores null en columnas tipadas**: operaciones aritméticas o de comparación sobre
  null generan error dependiendo del contexto.
- **Fuentes dinámicas**: un archivo CSV que un mes tiene "123.45" y el siguiente tiene
  "123,45" (diferente separador decimal) provoca falla de conversión.

## Solución paso a paso

### Opción A — Alinear tipos antes del Merge

1. Identificar las columnas clave del Merge y verificar su tipo en cada tabla:
   - En Power Query, seleccionar la columna → mirar el ícono del encabezado
     (ABC = Text, 123 = Number, calendario = Date).
2. Si una es `Number` y la otra `Text`, convertir ambas al mismo tipo **antes**
   del paso Merge:
   ```m
   = Table.TransformColumnTypes(Source, {{"ID_Cliente", type text}})
   ```
3. Para IDs numéricos con ceros a la izquierda (ej. "00123"), convertir siempre
   a `Text` en ambas tablas para preservar los ceros.

### Opción B — Limpiar datos antes del Append

1. Antes de hacer Append, verificar que las columnas homólogas tengan el mismo tipo.
2. Si una columna tiene valores no convertibles (ej. "N/A", "-", "NULL"), reemplazarlos
   primero:
   ```m
   = Table.ReplaceValue(Source, "N/A", null, Replacer.ReplaceValue, {"Monto"})
   ```
3. Luego aplicar el tipo:
   ```m
   = Table.TransformColumnTypes(Cleaned, {{"Monto", type number}})
   ```

### Opción C — Usar try/otherwise para conversiones seguras

Para columnas donde algunos valores pueden fallar la conversión:

```m
= Table.AddColumn(Source, "Monto_Safe", each
    try Number.From([Monto]) otherwise null,
    type number
)
```

Esto convierte lo posible y pone `null` donde falla, sin romper la query completa.

### Opción D — Eliminar el paso "Changed Type" automático

1. En `Applied Steps`, buscar el paso `Changed Type` que Power Query genera al
   conectar la fuente.
2. Eliminarlo y agregar manualmente un paso de tipado solo sobre las columnas que
   realmente necesitan conversión.
3. Para columnas problemáticas, aplicar primero una limpieza y después el tipo.

## Cómo prevenirlo

- **Definir tipos explícitamente** en cada query en lugar de depender del auto-detect
  de Power Query.
- En Merges, **siempre verificar que las claves tengan el mismo tipo** antes de unir.
- Para fuentes externas (CSV, Excel), establecer un **contrato de datos**: definir
  qué tipo espera cada columna y validar al inicio de la query.
- Usar `Table.Schema(tabla)` para inspeccionar tipos programáticamente y detectar
  inconsistencias antes de combinar.
- Si los datos vienen con valores "basura" ("N/A", "-", "Error"), limpiarlos en un
  paso dedicado antes de tipar.

## Fuentes

- [Microsoft Docs - Data types in Power Query](https://learn.microsoft.com/en-us/power-query/data-types)
- [Microsoft Docs - Merge queries overview](https://learn.microsoft.com/en-us/power-query/merge-queries-overview)
- [Microsoft Docs - Handling errors in Power Query](https://learn.microsoft.com/en-us/power-query/dealing-with-errors)
