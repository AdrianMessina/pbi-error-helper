---
id: dax-003
title: Transición de contexto inesperada con CALCULATE en columnas calculadas
category: dax
severity: alta
tools: [Desktop, Service]
tags: [CALCULATE, context-transition, row-context, filter-context]
related: [dax-001, dax-004]
media:
  images: []
  videos: []
---

## Síntoma

Al usar `CALCULATE` dentro de una columna calculada, los valores devueltos son
inesperadamente iguales para todas las filas, o devuelven el total general de la tabla
en lugar del valor correspondiente a cada fila. Por ejemplo:

```dax
-- Columna calculada en la tabla Ventas
Ranking Producto =
CALCULATE(
    COUNTROWS(Ventas),
    Ventas[Producto] = EARLIER(Ventas[Producto])
)
```

Devuelve el mismo número para todas las filas, o un número que no coincide con el
conteo esperado por producto.

En otros casos, una medida que funciona perfectamente en un visual produce resultados
incorrectos cuando se invoca dentro de una columna calculada con `CALCULATE`, porque
la transición de contexto convierte TODAS las columnas de la fila actual en filtros,
no solo la columna que el usuario tenía en mente.

## Causa

DAX opera con dos tipos de contexto:
- **Row context (contexto de fila):** existe en columnas calculadas e iteradores (`SUMX`,
  `FILTER`, etc.). Permite acceder al valor de cada columna de la fila actual.
- **Filter context (contexto de filtro):** existe en medidas y dentro de `CALCULATE`.
  Filtra la tabla completa antes de evaluar la expresión.

**La transición de contexto** ocurre cuando `CALCULATE` encuentra un row context activo:
automáticamente convierte cada columna de la fila actual en un filtro equivalente. Esto
significa que si la tabla tiene 20 columnas, `CALCULATE` genera internamente 20 filtros
— uno por cada columna — no solo el filtro que el usuario escribió explícitamente.

Consecuencias problemáticas:

- **Filtrado excesivo:** Si dos filas tienen el mismo producto pero distinta fecha,
  la transición filtra por producto Y fecha Y todas las demás columnas, devolviendo
  típicamente 1 fila (la fila actual) en lugar del grupo esperado.
- **Rendimiento:** La transición de contexto en una tabla con millones de filas genera
  millones de evaluaciones individuales de `CALCULATE`, cada una con N filtros internos.
- **Interacción con medidas:** Llamar una medida (que internamente usa `CALCULATE`) dentro
  de un iterador activa la transición de contexto aunque el usuario no haya escrito
  `CALCULATE` explícitamente, porque las medidas se envuelven implícitamente en CALCULATE.

## Solución paso a paso

1. **Confirmar que hay transición de contexto.** Crear una columna calculada de prueba:
   ```dax
   _Debug CantFilas = CALCULATE(COUNTROWS(Ventas))
   ```
   Si devuelve `1` para todas las filas, la transición de contexto está filtrando hasta
   la fila individual — confirmando el problema.

2. **Si se necesita agregar por un grupo (ej: producto), usar `CALCULATE` con
   `REMOVEFILTERS` para eliminar los filtros no deseados** y luego agregar solo el filtro
   necesario:
   ```dax
   Ventas Producto =
   CALCULATE(
       SUM(Ventas[Monto]),
       REMOVEFILTERS(Ventas),
       Ventas[Producto] = Ventas[Producto]
   )
   ```
   `REMOVEFILTERS(Ventas)` elimina todos los filtros generados por la transición, y
   luego `Ventas[Producto] = Ventas[Producto]` re-aplica solo el filtro deseado.

3. **Evaluar si realmente se necesita una columna calculada.** En la mayoría de los
   casos, el resultado deseado se logra mejor con una **medida**:
   ```dax
   Total Ventas Producto =
   SUM(Ventas[Monto])
   ```
   Una medida responde automáticamente al contexto de filtro del visual (slicers, filas
   de la matriz) sin necesidad de gestionar la transición de contexto manualmente.

4. **Si se necesita un ranking, usar funciones nativas de ranking** en lugar de
   `CALCULATE` + `COUNTROWS`:
   ```dax
   -- Como medida:
   Ranking =
   RANKX(
       ALLSELECTED(Productos[Producto]),
       [Total Ventas]
   )
   ```

5. **Si se invoca una medida dentro de `SUMX`/`FILTER`/otro iterador**, tener en cuenta
   que la medida activa la transición implícitamente. Usar `ALLEXCEPT` o `REMOVEFILTERS`
   dentro de la medida si es necesario controlar qué filtros se aplican:
   ```dax
   Total Ventas Sin Transición =
   CALCULATE(
       SUM(Ventas[Monto]),
       REMOVEFILTERS(Ventas[Fecha]),
       REMOVEFILTERS(Ventas[Region])
   )
   ```

## Cómo prevenirlo

- **Regla de oro:** evitar `CALCULATE` en columnas calculadas salvo que se entienda
  perfectamente la transición de contexto. Para la gran mayoría de escenarios, una
  **medida** es la respuesta correcta.
- **Cuando se necesite una columna calculada con agregación**, usar `RELATED` para traer
  valores de tablas relacionadas, o pre-calcular el valor en Power Query / la fuente de
  datos.
- **Estudiar el artículo de SQLBI sobre context transition** — es uno de los conceptos
  más difíciles de DAX y la fuente de la mayoría de los bugs sutiles.
- **Usar variables (`VAR`)** para aislar evaluaciones y hacer el código más legible y
  depurable.

## Fuentes

- [Microsoft Docs - CALCULATE function](https://learn.microsoft.com/en-us/dax/calculate-function-dax)
- [SQLBI - Context Transition in DAX](https://www.sqlbi.com/articles/understanding-context-transition/)
- [SQLBI - Row Context and Filter Context in DAX](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/)
- [The Definitive Guide to DAX, 2nd Edition - Marco Russo & Alberto Ferrari, Chapter 5](https://www.sqlbi.com/books/the-definitive-guide-to-dax/)
