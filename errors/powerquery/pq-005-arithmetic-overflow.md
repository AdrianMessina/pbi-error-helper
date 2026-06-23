---
id: pq-005
title: Arithmetic overflow al cargar columna numérica
category: powerquery
severity: media
tools: [Desktop, Service]
tags: [overflow, datatype, conversion, decimal, integer, m]
search_hints:
  - "Arithmetic overflow error converting"
  - "error de desbordamiento aritmetico"
  - "arithmetic overflow"
  - "overflow al convertir tipo de dato"
  - "error en conversion numerica del dato"
  - "error de conversion de tipo numerico"
  - "aritmetic overflow"
related: []
media:
  images: [pq-005-fig1.png]
  videos: []
---

## Síntoma

Al refrescar una tabla en Power Query o al cargar al modelo, aparece:

> Arithmetic overflow error converting [tipo] to data type [otro tipo].

La columna afectada queda con error en cada fila. Si está marcada como tipo
`Whole Number` o `Decimal Number`, la carga aborta o queda con valores nulos.

## Causa

El tipo de dato declarado en Power Query no puede contener el valor que llega
de la fuente.

Ejemplos típicos:

- Columna declarada como `Int64.Type` (entero) pero llegan valores con
  decimales o magnitudes mayores a 9.2 × 10¹⁸.
- Columna declarada como `Currency` (Decimal fijo de 4 dígitos) pero llegan
  números con más precisión.
- Cast implícito a `Number` cuando hay strings con caracteres no numéricos
  (comas, puntos, espacios, símbolos de moneda).
- Resultado de una operación (`a * b`) que excede el rango del tipo destino.

## Solución paso a paso

1. **Identificar la columna culpable.** En Power Query, expandir el ícono de
   error de la columna → muestra el valor exacto que no se pudo convertir.

2. **Inspeccionar los datos crudos** antes del paso `Changed Type`:
   - Quitar temporalmente el paso de conversión y ver los valores reales.
   - Buscar outliers, nulls, strings con formato distinto.

3. **Elegir el tipo correcto:**
   - Si hay decimales → `Decimal Number` (no `Whole Number`).
   - Si hay magnitudes muy grandes → `Decimal Number` (no `Whole Number`).
   - Si hay strings con texto → primero limpiar (`Replace Values`, `Trim`,
     remover símbolos) y después convertir.

4. **Convertir explícitamente con manejo de errores:**
   ```m
   = Table.TransformColumns(Source, {{"Importe", each
       try Number.From(_) otherwise null, type nullable number}})
   ```

5. **Refrescar la query y validar** que la columna no muestra el ícono de
   error y que el modelo carga.

## Cómo prevenirlo

- Nunca usar `Detect Data Types` automático en columnas con datos heterogéneos
  — fuerza tipos sin entender el contenido y rompe en producción.
- Para columnas numéricas críticas, declarar explícitamente el tipo en M
  documentando por qué (rango esperado, precisión).
- Validar que la fuente upstream (SQL, Excel, API) no cambió el formato de
  la columna antes de promover el reporte.

## Fuentes

- [Power Query M - Number types](https://learn.microsoft.com/en-us/powerquery-m/number-type)
- [Data types in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types)
