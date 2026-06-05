---
id: modelo-004
title: Tablas automáticas de fecha/hora inflan el modelo y causan confusión
category: modelo
severity: baja
tools: [Desktop, Service]
tags: [auto-date-time, performance, model-size, date-table]
related: [modelo-001]
media:
  images: []
  videos: []
---

## Síntoma

Al trabajar con el modelo de datos en Power BI Desktop se observan uno o más
de estos comportamientos:

- En la vista de **Model** o en el panel de campos, aparecen **jerarquías de
  fecha automáticas** (Year > Quarter > Month > Day) en cada columna de tipo
  `Date` o `DateTime`, incluso cuando ya existe una tabla de calendario
  explícita.
- El archivo `.pbix` es **más grande de lo esperado** para la cantidad de datos
  que contiene. Por ejemplo, un modelo con 100K filas ocupa significativamente
  más que un archivo equivalente sin columnas de fecha.
- Al analizar el modelo con **DAX Studio** o **Vertipaq Analyzer**, aparecen
  múltiples tablas ocultas con nombres como `LocalDateTable_XXXXXXXX-...` o
  `DateTableTemplate_...`, cada una consumiendo memoria.
- Las medidas de **time intelligence** (como `SAMEPERIODLASTYEAR`,
  `TOTALYTD`, `DATEADD`) **no funcionan correctamente** o devuelven `BLANK`
  porque Power BI usa la tabla automática interna en lugar de la tabla de
  calendario explícita del modelo.
- Al crear una relación con una tabla de calendario personalizada, se generan
  **ambiguedades** porque la tabla automática oculta compite con la tabla
  explícita.

## Causa

Power BI Desktop tiene habilitada por defecto la opción **"Auto date/time"**
(fecha y hora automáticas). Cuando esta opción está activa, el motor crea
**una tabla de fechas oculta por cada columna** de tipo `Date` o `DateTime`
en el modelo.

Cada tabla automática:

- Contiene un rango completo de fechas basado en los valores mínimo y máximo
  de la columna asociada.
- Incluye columnas calculadas para `Year`, `Quarter`, `Month`, `Day`, y una
  jerarquía predefinida.
- Se almacena comprimida en el modelo VertiPaq, pero **suma memoria y tamaño
  de archivo** por cada columna de fecha.
- Es **invisible** en la vista de modelo pero **activa** — puede interferir
  con el contexto de filtro de las funciones de time intelligence.

En un modelo con 10 columnas de tipo fecha en diferentes tablas, esto significa
**10 tablas de fecha ocultas adicionales**, cada una con miles de filas. Esto
es especialmente problemático cuando:

- Ya existe una tabla de calendario explícita y bien diseñada.
- El modelo tiene muchas tablas transaccionales con columnas de fecha
  (FechaPedido, FechaEnvio, FechaFactura, etc.).
- Se necesita un comportamiento preciso de time intelligence con una tabla
  de fechas marcada como "Date table".

## Solución paso a paso

### Paso 1 — Desactivar la función Auto date/time

1. Abrir Power BI Desktop.
2. Ir a **File > Options and settings > Options**.
3. En el panel izquierdo, bajo la sección **Current File**, seleccionar
   **Data Load**.
4. Desmarcar la casilla **"Auto date/time for new files"** en la sección
   de inteligencia de tiempo.
5. Repetir el paso bajo **GLOBAL > Data Load** para que aplique a todos los
   archivos nuevos.
6. Hacer clic en **OK**.

> Nota: Desactivar esta opción en un archivo existente elimina las tablas
> automáticas al guardar y recargar el modelo. Verificar que ninguna medida
> o visual dependa de las jerarquías automáticas antes de desactivarlo.

### Paso 2 — Crear una tabla de calendario explícita (si no existe)

1. En Power BI Desktop, ir a **Modeling > New Table** y crear una tabla
   de calendario con DAX:
   ```dax
   Calendario =
   VAR MinDate = MIN(Ventas[Fecha])
   VAR MaxDate = MAX(Ventas[Fecha])
   RETURN
   ADDCOLUMNS(
       CALENDAR(MinDate, MaxDate),
       "Anio", YEAR([Date]),
       "NroMes", MONTH([Date]),
       "NombreMes", FORMAT([Date], "MMMM"),
       "Trimestre", "Q" & FORMAT([Date], "Q"),
       "DiaSemana", WEEKDAY([Date], 2),
       "NombreDia", FORMAT([Date], "dddd"),
       "AnioMes", FORMAT([Date], "YYYY-MM")
   )
   ```
2. Alternativamente, importar una tabla de calendario desde Power Query
   o desde la base de datos de origen.

### Paso 3 — Marcar la tabla como tabla de fechas

1. Seleccionar la tabla `Calendario` en la vista de modelo.
2. Ir a **Table tools > Mark as date table**.
3. Seleccionar la columna de fecha (tipo `Date`, valores contiguos sin
   huecos).
4. Confirmar. Esto le indica a Power BI que use esta tabla para time
   intelligence en lugar de las tablas automáticas.

### Paso 4 — Verificar la reducción de tamaño

1. Guardar el archivo `.pbix`.
2. Abrir **DAX Studio** y conectar al modelo.
3. Ejecutar **View > Vertipaq Analyzer > Analyze Model**.
4. Verificar que ya no existan tablas `LocalDateTable_*` ni
   `DateTableTemplate_*`.
5. Comparar el tamaño del archivo antes y después. En modelos con muchas
   columnas de fecha, la reducción puede ser de un **10-30%** del tamaño
   comprimido.

### Paso 5 — Actualizar medidas y visuales

1. Revisar todas las medidas que usen funciones de time intelligence
   (`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`, etc.) y asegurarse de
   que referencien la tabla `Calendario` explícita.
2. Revisar los visuales que usaban la jerarquía automática (Year > Quarter
   > Month > Day) y reemplazarlos con las columnas de la tabla `Calendario`.
3. Verificar que las relaciones entre la tabla `Calendario` y las tablas
   de hechos estén correctamente configuradas como `1:N`.

## Cómo prevenirlo

- **Desactivar Auto date/time a nivel global** como primer paso al instalar
  Power BI Desktop. Ir a Options > GLOBAL > Data Load y desmarcar la opción.
  Esto asegura que ningún archivo nuevo lo tenga activo.
- **Crear siempre una tabla de calendario explícita** como parte del diseño
  estándar del modelo. Es una best practice universalmente recomendada por
  Microsoft y la comunidad.
- **Marcar la tabla de calendario como "Date table"** inmediatamente después
  de crearla. Esto habilita el time intelligence nativo y evita que Power BI
  intente usar tablas automáticas.
- **Incluir la desactivación de Auto date/time en el checklist de inicio de
  proyecto** de Power BI del equipo.
- **Auditar periódicamente los modelos existentes** con DAX Studio / Vertipaq
  Analyzer para detectar tablas ocultas innecesarias.

## Fuentes

- [Microsoft Docs - Auto date/time guidance in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/auto-date-time)
- [Microsoft Docs - Set and use date tables in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)
- [SQLBI - Removing auto date/time tables in Power BI](https://www.sqlbi.com/articles/disabling-auto-date-time-in-power-bi/)
- [Microsoft Docs - DAX time intelligence functions](https://learn.microsoft.com/en-us/dax/time-intelligence-functions-dax)
