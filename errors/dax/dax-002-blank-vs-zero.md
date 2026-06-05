---
id: dax-002
title: La medida devuelve BLANK en lugar de 0 (o viceversa)
category: dax
severity: media
tools: [Desktop, Service]
tags: [measure, BLANK, aggregation, IF, COALESCE]
related: [dax-001, dax-005]
media:
  images: []
  videos: []
---

## Síntoma

Una medida muestra celdas vacías en una tabla o matriz donde se esperaba ver `0`. En
tarjetas (cards), el visual desaparece o muestra "(Blank)" en vez del valor numérico.
En gráficos de barras o líneas, los puntos de datos faltantes rompen la continuidad de
la serie o directamente no se renderizan.

Alternativamente, una medida que debería devolver BLANK (para ocultar filas sin datos)
devuelve `0`, causando que la tabla muestre filas innecesarias con valores en cero que
inflan el conteo y confunden al usuario.

## Causa

En DAX, `BLANK()` no es lo mismo que `0`. Las funciones de agregación estándar como
`SUM`, `COUNT`, `AVERAGE` ignoran los BLANK en su cálculo, y muchos visuals de Power BI
ocultan automáticamente las filas/columnas donde todas las medidas devuelven BLANK.

Las causas más frecuentes:

- **`IF` sin rama ELSE:** La expresión `IF([Ventas] > 100, [Ventas])` devuelve BLANK
  cuando la condición es falsa, porque DAX usa BLANK como valor por defecto del tercer
  argumento. Esto hace que filas válidas desaparezcan de la tabla.
- **`DIVIDE` sin alternateResult:** `DIVIDE([Ventas], [Cantidad])` devuelve BLANK cuando
  el denominador es 0, no devuelve 0 ni error.
- **No hay filas en el contexto de filtro:** Si un filtro elimina todas las filas de una
  tabla, `SUM(Tabla[Columna])` devuelve BLANK, no 0.
- **Uso de `ISBLANK` cuando se necesita comprobar 0 también:** `ISBLANK(0)` devuelve
  FALSE, por lo que valores explícitamente cero pasan inadvertidos.

## Solución paso a paso

1. **Identificar si el problema es BLANK→0 o 0→BLANK.** Crear una medida de diagnóstico:
   ```dax
   _Debug Ventas =
   IF(
       ISBLANK([Total Ventas]),
       "ES BLANK",
       FORMAT([Total Ventas], "0.00")
   )
   ```
   Ponerla en una tabla para ver exactamente qué filas devuelven BLANK.

2. **Para convertir BLANK a 0**, envolver la medida con `COALESCE` o sumarle cero:
   ```dax
   Total Ventas Safe =
   COALESCE([Total Ventas], 0)
   ```
   O alternativamente:
   ```dax
   Total Ventas Safe = [Total Ventas] + 0
   ```
   `COALESCE` es más legible y explícito; el `+ 0` es un truco rápido pero menos claro.

3. **Para que una medida devuelva BLANK deliberadamente** (para ocultar filas sin datos),
   agregar una guarda al inicio:
   ```dax
   Total Ventas =
   VAR _resultado = SUM(Tabla[Ventas])
   RETURN
       IF(ISBLANK(_resultado), BLANK(), _resultado)
   ```

4. **Si el problema es un `IF` sin ELSE**, agregar siempre el tercer argumento:
   ```dax
   -- Antes (devuelve BLANK si falso):
   Ventas Filtradas = IF([Ventas] > 100, [Ventas])

   -- Después (devuelve 0 si falso):
   Ventas Filtradas = IF([Ventas] > 100, [Ventas], 0)
   ```

5. **Verificar en los visuals** que el comportamiento sea el esperado. En tablas/matrices,
   ir a Format → Values → Show items with no data para controlar si las filas BLANK se
   muestran o no.

## Cómo prevenirlo

- **Siempre escribir las tres ramas de `IF`** — nunca depender del BLANK implícito como
  rama ELSE, salvo que sea la intención explícita.
- **Usar `COALESCE` como wrapper estándar** en medidas que alimentan tarjetas o KPIs
  donde un BLANK rompe el visual.
- **Documentar la intención:** si una medida debe devolver BLANK para ocultar filas,
  dejar un comentario `-- Devuelve BLANK intencionalmente para ocultar filas sin datos`.
- **Testear medidas con y sin filtros** para verificar el comportamiento en contextos
  donde no hay filas (ej: seleccionar un año futuro sin ventas).

## Fuentes

- [Microsoft Docs - BLANK function](https://learn.microsoft.com/en-us/dax/blank-function-dax)
- [Microsoft Docs - COALESCE function](https://learn.microsoft.com/en-us/dax/coalesce-function-dax)
- [SQLBI - Handling BLANK in DAX](https://www.sqlbi.com/articles/blank-handling-in-dax/)
- [SQLBI - The definitive guide to BLANK in DAX](https://www.sqlbi.com/articles/blank-row-in-dax/)
