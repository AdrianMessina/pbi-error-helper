---
id: modelo-002
title: Relaciones many-to-many causan valores duplicados/inflados en agregaciones
category: modelo
severity: alta
tools: [Desktop, Service]
tags: [many-to-many, bridge-table, relationships, duplicated-values]
related: [modelo-001, modelo-003]
media:
  images: []
  videos: []
---

## Síntoma

Las medidas de agregación como `SUM`, `COUNT` o `AVERAGE` devuelven valores
**inflados o duplicados** que no coinciden con los datos reales de la tabla de origen.
Por ejemplo:

- El total de ventas en un visual muestra el doble o triple del valor esperado.
- Al filtrar por una dimensión que participa en una relación many-to-many, los
  totales cambian de forma inconsistente o no cuadran con los subtotales.
- En una matriz o tabla, la fila de **Total** muestra un número mayor que la suma
  individual de las filas visibles.
- Power BI Desktop muestra una advertencia al crear la relación:
  > This relationship has a many-many cardinality. This means that one or both of
  > the tables will contain multiple rows with the same key value.

## Causa

Cuando dos tablas tienen una relación **many-to-many** (M:N) — ya sea directa
(configurada como *many-to-many* en el diálogo de relaciones) o indirecta (a través
de una **tabla puente / bridge table**) — el motor de VertipAQ realiza un
**cross-join parcial** entre las filas coincidentes de ambos lados.

Esto significa que si una clave aparece 3 veces en la tabla A y 2 veces en la
tabla B, se generan 6 combinaciones en el contexto de filtro. Cualquier columna
numérica que se agregue con `SUM` se cuenta una vez por cada combinación, lo que
produce la **inflación de valores** (a menudo llamada "double-counting" o
"fan-out").

Escenarios típicos donde ocurre:

- **Tabla puente mal diseñada:** una tabla intermedia que relaciona, por ejemplo,
  `Productos` con `Proveedores` donde un producto puede tener múltiples proveedores
  y viceversa. Al sumar `Ventas[Monto]`, cada venta se multiplica por la cantidad
  de proveedores asociados al producto.
- **Relación directa M:N entre dos tablas de hechos:** por ejemplo, `Ventas` y
  `Presupuestos` relacionadas por `[Fecha]` y `[Producto]` sin dimensiones
  intermedias.
- **Dimensiones degeneradas con granularidad incorrecta:** una dimensión que no
  tiene claves únicas actúa como lado "many" en ambos extremos de la relación.

## Solución paso a paso

### Caso A — Relación M:N directa entre tablas de hechos

1. **No relacionar las tablas de hechos directamente.** En su lugar, conectar
   ambas tablas de hechos a **dimensiones compartidas** (fecha, producto, cliente,
   etc.) con relaciones 1:N.
2. Verificar que cada tabla de dimensión tenga **claves únicas** en la columna
   de relación. Usar *Column Quality* y *Column Distribution* en Power Query para
   confirmarlo.
3. En las medidas, usar `SUMMARIZECOLUMNS` o `CALCULATE` sobre cada tabla de
   hechos por separado y combinar resultados en una medida final:
   ```dax
   Variación =
   [Total Ventas Real] - [Total Presupuesto]
   ```

### Caso B — Tabla puente (bridge table) necesaria

1. Crear una tabla puente que contenga solo las **claves de relación** (sin
   columnas numéricas). Por ejemplo: `PuenteProductoProveedor` con columnas
   `[ProductoID]` y `[ProveedorID]`.
2. Relacionar la tabla puente con cada dimensión usando relaciones **1:N**
   (la dimensión en el lado "1", la tabla puente en el lado "N").
3. **Habilitar filtro bidireccional** en ambas relaciones de la tabla puente
   para que el contexto de filtro fluya correctamente.
4. Mover las medidas de agregación a una tabla que **no** participe en el
   fan-out. Si la medida es `SUM(Ventas[Monto])`, asegurarse de que `Ventas`
   está en el lado N de una relación 1:N con la dimensión, no con la tabla puente.
5. Para evitar el conteo múltiple, usar `DISTINCTCOUNT` o envolver la medida
   con `SUMX` + `DISTINCT`:
   ```dax
   Ventas sin duplicar =
   SUMX(
       DISTINCT(Ventas[VentaID]),
       CALCULATE(SUM(Ventas[Monto]))
   )
   ```

### Caso C — Verificar y corregir la inflación

1. Crear una medida de control que cuente filas de la tabla de hechos:
   ```dax
   Filas Ventas = COUNTROWS(Ventas)
   ```
2. Comparar el resultado en un visual filtrado vs. sin filtro. Si el número
   de filas cambia inesperadamente al aplicar un filtro de la dimensión M:N,
   hay fan-out.
3. Revisar el modelo en la vista de **Model view** en Desktop y verificar que
   cada relación muestre la cardinalidad correcta (`1:*` vs `*:*`).

## Cómo prevenirlo

- **Modelar siempre en esquema estrella** con dimensiones de claves únicas y
  tablas de hechos en el centro. Esto elimina la necesidad de relaciones M:N
  en la mayoría de los casos.
- **Nunca colocar columnas numéricas que se agregan (montos, cantidades) en
  tablas puente.** Las tablas puente deben contener solo claves.
- **Usar `DISTINCTCOUNT` o `SUMX(DISTINCT(...))` en medidas** que operan sobre
  dimensiones con relaciones M:N para evitar inflación.
- **Validar cardinalidades al crear relaciones.** Si Power BI advierte sobre
  M:N, detenerse y evaluar si la estructura del modelo es correcta antes de
  continuar.
- **Probar cada medida con datos conocidos** antes de publicar. Comparar los
  totales del visual con una consulta directa a la fuente de datos.

## Fuentes

- [Microsoft Docs - Many-to-many relationships in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-many-to-many-relationships)
- [Microsoft Docs - Apply many-to-many relationships guidance](https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many)
- [SQLBI - Many-to-many relationships in Power BI](https://www.sqlbi.com/articles/many-to-many-relationships-in-power-bi-and-excel-2016/)
- [SQLBI - The expanded table in DAX](https://www.sqlbi.com/articles/the-expanded-table-in-dax/)
