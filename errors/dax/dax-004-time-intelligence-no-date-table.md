---
id: dax-004
title: Funciones de time intelligence fallan por tabla de fechas incorrecta o no marcada
category: dax
severity: alta
tools: [Desktop, Service]
tags: [time-intelligence, date-table, SAMEPERIODLASTYEAR, DATESYTD]
related: [dax-001, dax-003]
media:
  images: []
  videos: []
---

## Síntoma

Al usar funciones de time intelligence como `SAMEPERIODLASTYEAR`, `DATESYTD`,
`TOTALYTD`, `DATEADD`, o `PARALLELPERIOD`, se obtiene uno de estos errores:

> "The '[Fecha]' column of the 'Calendario' table cannot be used in a date or time
> intelligence calculation because it has duplicate values."

> "A date column in the table 'Ventas' has been specified for the function
> SAMEPERIODLASTYEAR. This is not supported."

> "The function DATESYTD expects a reference to a date/time column as the first
> parameter."

O bien, la medida no da error pero devuelve BLANK o resultados incorrectos: por ejemplo,
`SAMEPERIODLASTYEAR` devuelve el mismo valor que el período actual, o `DATESYTD`
devuelve acumulados que no coinciden con la suma manual.

## Causa

Las funciones de time intelligence de DAX tienen requisitos estrictos sobre la tabla de
fechas que se les pasa como argumento:

1. **La tabla de fechas debe estar marcada como "Date Table"** en el modelo. Sin esta
   marca, DAX no puede optimizar las operaciones de time intelligence y algunas funciones
   fallan directamente.

2. **La columna de fecha debe tener tipo Date o DateTime**, no texto ni entero. Si la
   fecha llegó como texto ("2024-01-15") y no se convirtió, las funciones no la
   reconocen.

3. **No puede haber fechas duplicadas** en la columna de fecha de la tabla calendario.
   Si hay duplicados (ej: por un join mal hecho o por incluir la hora), la marca como
   Date Table falla.

4. **No puede haber huecos (gaps) en el rango de fechas.** La tabla debe cubrir cada
   día consecutivo desde el 1 de enero del primer año hasta el 31 de diciembre del
   último año. Si faltan días (ej: se excluyeron fines de semana), funciones como
   `DATESYTD` y `SAMEPERIODLASTYEAR` devuelven resultados parciales o incorrectos.

5. **Se usa la columna de fecha de la tabla de hechos** en lugar de la tabla calendario.
   Las funciones de time intelligence esperan la columna de la tabla de fechas dedicada,
   no la fecha de la tabla transaccional.

## Solución paso a paso

1. **Verificar si existe una tabla de fechas dedicada.** En el panel de Campos, buscar
   una tabla llamada "Calendario", "DimFecha", "DateTable" o similar. Si no existe,
   crearla:
   ```dax
   Calendario =
   ADDCOLUMNS(
       CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31)),
       "Año", YEAR([Date]),
       "Mes", MONTH([Date]),
       "NombreMes", FORMAT([Date], "MMMM"),
       "Trimestre", "Q" & FORMAT([Date], "Q"),
       "AñoMes", FORMAT([Date], "YYYY-MM")
   )
   ```

2. **Marcar la tabla como Date Table.** En Power BI Desktop:
   - Seleccionar la tabla Calendario en la vista de Modelo.
   - Ir a Table Tools → Mark as date table → Mark as date table.
   - Seleccionar la columna `Date` como columna de fecha.
   - Si aparece un error de validación, ir al paso 3.

3. **Verificar que no hay duplicados ni huecos.** Crear una medida de diagnóstico:
   ```dax
   _Debug Fechas Duplicadas =
   COUNTROWS(Calendario) - DISTINCTCOUNT(Calendario[Date])
   ```
   Si devuelve > 0, hay duplicados. Para verificar huecos:
   ```dax
   _Debug Dias Esperados =
   DATEDIFF(MIN(Calendario[Date]), MAX(Calendario[Date]), DAY) + 1
       - COUNTROWS(Calendario)
   ```
   Si devuelve > 0, hay días faltantes en el rango.

4. **Crear la relación entre la tabla calendario y la tabla de hechos:**
   - Relación: `Calendario[Date]` → `Ventas[Fecha]` (uno a muchos).
   - Dirección de filtro: Single (de Calendario a Ventas).

5. **Reescribir las medidas para usar la columna de la tabla calendario**, no la de la
   tabla de hechos:
   ```dax
   -- INCORRECTO: usa la fecha de la tabla de hechos
   Ventas Año Anterior =
   CALCULATE([Total Ventas], SAMEPERIODLASTYEAR(Ventas[Fecha]))

   -- CORRECTO: usa la fecha de la tabla calendario
   Ventas Año Anterior =
   CALCULATE([Total Ventas], SAMEPERIODLASTYEAR(Calendario[Date]))
   ```

6. **Verificar el resultado** comparando manualmente: filtrar el visual por enero 2024 y
   verificar que `Ventas Año Anterior` muestre el valor de enero 2023.

## Cómo prevenirlo

- **Siempre crear una tabla calendario dedicada** como primer paso al construir un modelo.
  Nunca depender de las fechas de las tablas transaccionales para time intelligence.
- **Marcarla como Date Table** inmediatamente después de crearla. Esto activa las
  validaciones automáticas de Power BI.
- **Asegurar cobertura completa de años:** la tabla calendario debe empezar el 1 de enero
  y terminar el 31 de diciembre, cubriendo todos los años presentes en los datos más
  al menos un año extra para proyecciones.
- **Nunca filtrar la tabla calendario** para excluir fines de semana o feriados. Si se
  necesita esa lógica, agregar una columna `EsDiaLaborable` y filtrar por ella en las
  medidas, no en la tabla misma.
- **Usar `CALENDAR` o `CALENDARAUTO`** en DAX, o generar la tabla en Power Query con
  `List.Dates`, para garantizar continuidad.

## Fuentes

- [Microsoft Docs - Time Intelligence in DAX](https://learn.microsoft.com/en-us/dax/time-intelligence-functions-dax)
- [Microsoft Docs - Mark as Date Table](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)
- [SQLBI - Creating a Date Table in DAX](https://www.sqlbi.com/articles/creating-a-simple-date-table-in-dax/)
- [SQLBI - Time Intelligence Best Practices](https://www.sqlbi.com/articles/time-intelligence-in-power-bi-desktop/)
