---
id: modelo-003
title: "Valores duplicados impiden crear el lado 'uno' de una relación uno-a-muchos"
category: modelo
severity: alta
tools: [Desktop, Service]
tags: [duplicate-values, relationships, dimension-table, key-column]
related: [modelo-001, modelo-002]
media:
  images: []
  videos: []
---

## Síntoma

Al intentar crear una relación entre una tabla de dimensión (lookup) y una tabla
de hechos, Power BI Desktop muestra el siguiente error:

> This column contains duplicate values and can't be used as the 'one' side of
> a one-to-many relationship.

O su equivalente en español:

> Esta columna contiene valores duplicados y no se puede usar como lado "uno" de
> una relación de uno a varios.

Esto impide crear la relación con cardinalidad `1:N`. Power BI puede ofrecer
como alternativa cambiar a una relación `M:N`, lo cual generalmente no es la
solución correcta y puede causar los problemas descritos en `modelo-002`.

## Causa

Para que una columna participe como el **lado "1"** (lookup/dimensión) de una
relación `1:N`, cada valor en esa columna debe ser **único** — no puede haber
filas duplicadas. Este error aparece cuando la tabla de dimensión tiene **dos o
más filas con el mismo valor** en la columna clave.

Las causas raíz más comunes son:

- **Datos sucios en la fuente:** la tabla de dimensión se cargó sin deduplicar.
  Por ejemplo, la tabla `Clientes` tiene dos registros para el mismo
  `ClienteID` porque uno es la versión actual y otro la histórica (Slowly
  Changing Dimension tipo 2 sin procesar).
- **Combinación incorrecta en Power Query:** un `Merge` o `Append` que
  introdujo filas duplicadas. Por ejemplo, hacer `Append` de dos tablas de
  productos de diferentes regiones que comparten los mismos códigos.
- **Columna clave incorrecta:** se seleccionó una columna que no es realmente
  la clave primaria. Por ejemplo, usar `NombreProducto` en lugar de
  `ProductoID` cuando hay productos con el mismo nombre pero diferente ID.
- **Valores NULL o en blanco:** múltiples filas con valor `null` o vacío en la
  columna clave cuentan como duplicados entre sí.
- **Espacios o caracteres invisibles:** valores que parecen iguales visualmente
  pero difieren por espacios al inicio/final, saltos de línea o caracteres
  Unicode no visibles.
- **Granularidad incorrecta de la tabla:** la tabla contiene datos a un nivel
  de detalle más fino del esperado. Por ejemplo, una tabla `Productos` que en
  realidad tiene una fila por combinación producto-tienda.

## Solución paso a paso

### Paso 1 — Identificar los duplicados

1. Ir a **Power Query Editor** (Transform data).
2. Seleccionar la tabla de dimensión problemática.
3. Seleccionar la columna clave, hacer clic derecho y elegir
   **Remove Other Columns** (en una copia o referencia de la tabla).
4. Ir a **Home > Remove Rows > Remove Duplicates**.
5. Observar cuántas filas se eliminaron. Si se eliminaron filas, hay duplicados.
6. Alternativamente, usar **View > Column Quality** y **Column Distribution**
   en Power Query para ver el porcentaje de valores únicos vs. duplicados.

### Paso 2 — Determinar la causa raíz

1. Antes de la deduplicación, agrupar por la columna clave y contar:
   - En Power Query: seleccionar la columna > **Transform > Group By** >
     contar filas. Filtrar por conteo > 1.
   - En DAX (tabla calculada temporal):
     ```dax
     DupsCheck =
     FILTER(
         ADDCOLUMNS(
             VALUES(Dimension[KeyColumn]),
             "Conteo", CALCULATE(COUNTROWS(Dimension))
         ),
         [Conteo] > 1
     )
     ```
2. Examinar las filas duplicadas para entender por qué existen:
   - Si los valores son idénticos en todas las columnas: duplicado puro.
   - Si difieren en otras columnas: la granularidad de la tabla es incorrecta
     o hay un problema de SCD.

### Paso 3 — Corregir en Power Query

**Si son duplicados puros (filas idénticas):**

1. Seleccionar la columna clave.
2. **Home > Remove Rows > Remove Duplicates.**

**Si la tabla tiene granularidad incorrecta:**

1. Agrupar la tabla por la columna clave usando **Group By**.
2. Elegir la estrategia de agregación correcta para las demás columnas
   (primera fila, máximo, etc.).
3. Verificar que el resultado tiene sentido de negocio.

**Si hay valores NULL:**

1. Filtrar o reemplazar los NULL: **Transform > Replace Values** (reemplazar
   `null` por un valor significativo) o eliminar las filas con NULL si no
   son necesarias.

**Si hay espacios o caracteres invisibles:**

1. Seleccionar la columna clave.
2. **Transform > Format > Trim** (elimina espacios al inicio y final).
3. **Transform > Format > Clean** (elimina caracteres no imprimibles).
4. Si persisten duplicados, aplicar **Transform > Format > Lowercase** para
   normalizar mayúsculas/minúsculas.

### Paso 4 — Verificar y crear la relación

1. Después de aplicar la corrección, verificar con **Column Distribution**
   que la columna clave muestre: **Distinct = Count** (todos los valores son
   únicos).
2. Cerrar Power Query y aplicar los cambios.
3. Crear la relación normalmente en la vista de modelo. El error no debería
   aparecer.

## Cómo prevenirlo

- **Validar la unicidad de las claves en Power Query antes de cerrar y
  aplicar.** Usar *Column Quality* y *Column Distribution* como rutina.
- **Definir la clave primaria conceptual** de cada tabla de dimensión al
  diseñar el modelo. Documentar qué columna debe ser única.
- **Aplicar `Remove Duplicates` como paso estándar** al final de cada
  transformación de tabla de dimensión en Power Query, como red de seguridad.
- **Tratar los NULL antes de crear relaciones.** Una columna clave nunca
  debería tener valores nulos.
- **Usar Trim y Clean** por defecto en columnas de texto que servirán como
  clave de relación.
- **Si la fuente tiene SCD tipo 2**, filtrar para quedarse solo con la versión
  vigente (`WHERE EsFila Actual = 1`) o crear una vista en la base de datos
  que exponga solo las claves únicas.

## Fuentes

- [Microsoft Docs - Create and manage relationships in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships)
- [Microsoft Docs - Troubleshoot relationships in Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/relationships-troubleshoot)
- [Microsoft Docs - Column Quality, Distribution, and Profile in Power Query](https://learn.microsoft.com/en-us/power-query/data-profiling-tools)
- [SQLBI - How to handle duplicate values in dimension tables](https://www.sqlbi.com/articles/handling-duplicate-values-in-dimension-tables/)
