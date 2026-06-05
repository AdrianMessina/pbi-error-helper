---
id: copilot-005
title: Cómo preparar el modelo semántico para Copilot
category: copilot
severity: baja
tools: [Desktop, Service]
tags: [Copilot, semantic-model, optimization, AI-Instructions, verified-answers, synonyms]
related: [copilot-004]
media:
  images: []
  videos: []
---

## Síntoma

No es un error propiamente dicho. Esta entrada aplica cuando Copilot funciona
técnicamente (el botón está habilitado, no da errores), pero las respuestas son
imprecisas, irrelevantes, o no reflejan la realidad del negocio. El usuario siente que
Copilot "no entiende" el modelo o que "inventa" datos. También aplica como guía
preventiva antes de habilitar Copilot por primera vez en un modelo semántico nuevo.

Los indicadores de que el modelo necesita optimización para Copilot incluyen:
- Copilot confunde columnas con nombres similares entre tablas.
- Las respuestas numéricas no coinciden con los visuales del reporte.
- Copilot no puede responder preguntas que parecen simples.
- El usuario tiene que reformular la misma pregunta varias veces para obtener
  una respuesta razonable.
- Copilot genera DAX que usa funciones innecesariamente complejas o incorrectas.

## Causa

Copilot depende exclusivamente de los metadatos del modelo semántico para interpretar
preguntas y generar respuestas. A diferencia de un analista humano que conoce el contexto
de negocio, Copilot solo tiene acceso a:

- Nombres de tablas, columnas y medidas.
- Descripciones de objetos (si existen).
- Relaciones entre tablas.
- AI Instructions (si están configuradas).
- Sinónimos (si están definidos).
- Verified answers (si están configuradas).

Si estos metadatos son insuficientes, ambiguos o están ausentes, Copilot tiene que
"adivinar" la intención del usuario basándose solo en los nombres de los campos, lo que
frecuentemente produce resultados incorrectos. Un modelo optimizado para Copilot no solo
mejora las respuestas de IA, sino que también mejora la experiencia de Q&A, la navegación
del modelo por parte de otros desarrolladores, y la documentación general del asset.

## Solución paso a paso

Las siguientes prácticas deben implementarse como parte del ciclo de desarrollo del modelo
semántico, no como una tarea reactiva después de que Copilot falla.

### 1. Nomenclatura clara y consistente

Aplicar convenciones de nombrado que comuniquen la función de cada objeto sin ambigüedad:

- **Tablas de hechos:** usar nombres de acción en plural que describan el evento de
  negocio. Ejemplos: `SalesTransactions`, `OrderLines`, `InventoryMovements`,
  `SupportTickets`. Evitar nombres genéricos como `Data`, `Table1`, `Fact`.
- **Tablas de dimensiones:** usar nombres de entidad en singular. Ejemplos: `Customer`,
  `Product`, `Store`, `Calendar`. Evitar prefijos técnicos como `Dim_` o `d_` que no
  aportan contexto de negocio a Copilot.
- **Columnas:** incluir el contexto de la tabla si el nombre es genérico. `Amount` pasa
  a ser `SalesAmountUSD`. `Date` pasa a ser `OrderDate`. `Status` pasa a ser
  `OrderFulfillmentStatus`. Usar espacios o PascalCase según la convención del equipo.
- **Medidas:** usar un prefijo que indique la operación. `Total Net Sales`,
  `Avg Order Value`, `Count Active Customers`, `Pct Margin YoY`. Esto ayuda tanto a
  Copilot como a los usuarios humanos a entender qué hace cada medida.

### 2. Relaciones explícitas y jerarquías bien definidas

- Verificar que todas las relaciones entre tablas estén correctamente configuradas con
  la cardinalidad adecuada (1:N desde la dimensión al hecho).
- Crear jerarquías explícitas para las dimensiones más usadas. Por ejemplo, en la tabla
  `Calendar`: Año > Trimestre > Mes > Día. En `Geography`: País > Región > Ciudad.
  Las jerarquías ayudan a Copilot a entender niveles de drill-down.
- Marcar la tabla de fechas con "Mark as Date Table" para que Copilot pueda usar time
  intelligence correctamente.
- Evitar relaciones bidireccionales a menos que sean estrictamente necesarias. Las
  relaciones bidireccionales agregan complejidad que Copilot puede malinterpretar.

### 3. Descripciones completas en todos los objetos

Agregar descripciones a cada tabla, columna y medida del modelo. Las descripciones deben
responder las preguntas que un usuario nuevo haría:

- **Tabla:** "¿Qué contiene esta tabla? ¿Qué representa cada fila? ¿Desde cuándo tiene
  datos?" Ejemplo: "Tabla de hechos con todas las transacciones de venta minorista desde
  enero 2020. Cada fila representa una línea de factura. Incluye ventas online y en
  tienda física. No incluye devoluciones (ver tabla Returns)."
- **Columna:** "¿Qué significa este valor? ¿Cuál es la unidad? ¿Hay valores especiales?"
  Ejemplo: "Monto neto de la venta en USD después de descuentos aplicados. No incluye
  impuestos. Valores negativos indican ajustes de precio post-venta."
- **Medida:** "¿Qué calcula? ¿Qué filtros aplica? ¿Cuál es la unidad?" Ejemplo:
  "Suma de SalesAmountUSD para transacciones con OrderStatus = 'Completed'. Excluye
  devoluciones y cancelaciones. Resultado en USD. Usar con filtro de fecha del Calendar."

En Power BI Desktop, las descripciones se agregan seleccionando el objeto en la vista
de Modelo y editando la propiedad "Description" en el panel de Propiedades. En Tabular
Editor o con TMDL, se edita directamente en la definición del objeto.

### 4. Esquema simplificado y sin ruido

- **Eliminar columnas no utilizadas.** Cada columna importada pero no usada es ruido
  para Copilot. Usar la herramienta **Measure Killer** o **Model Analyzer** (External
  Tools) para identificar columnas sin referencia. Eliminarlas del modelo o, como
  mínimo, ocultarlas.
- **Eliminar medidas obsoletas.** Medidas de pruebas, medidas duplicadas, medidas que
  ya no reflejan el negocio actual -- eliminarlas o moverlas a un grupo de visualización
  "Deprecated" y ocultarlas.
- **Ocultar columnas técnicas.** Claves foráneas (CustomerKey, ProductID), columnas de
  auditoría (CreatedDate, ModifiedBy), y columnas de ETL (BatchID, LoadTimestamp) deben
  estar ocultas. Copilot no las necesita y su presencia agrega ruido.
- **Consolidar tablas auxiliares.** Si hay múltiples tablas pequeñas que podrían ser
  una sola dimensión, considerar consolidarlas para simplificar el grafo de relaciones.

### 5. AI Instructions para controlar la interpretación

Configurar AI Instructions en Power BI Service (semantic model > Settings > AI
Instructions) con reglas de negocio específicas:

```
- "Ventas" siempre se refiere a la medida [Total Net Sales], no a [Gross Sales].
- El año fiscal empieza en abril. Cuando el usuario dice "este año", usar el año fiscal.
- Todos los montos están en USD salvo que se indique lo contrario.
- "Clientes activos" significa clientes con al menos una compra en los últimos 12 meses.
- La tabla Calendar es la tabla de fechas principal. Usar siempre Calendar[Date] para
  filtros temporales, nunca SalesTransactions[OrderDate].
- Ignorar la tabla _Staging_Products, es una tabla auxiliar de ETL.
```

Las AI Instructions se evalúan en cada solicitud de Copilot y actúan como un "prompt de
sistema" que contextualiza todas las respuestas.

### 6. Verified Answers para KPIs de alto valor

Para las preguntas de negocio más importantes (las que los ejecutivos hacen
frecuentemente), configurar verified answers que garanticen respuestas correctas:

- En Power BI Service, ir al semantic model > **Settings > Q&A settings**.
- En la sección "Suggest questions", agregar preguntas frecuentes con sus respuestas
  verificadas. Por ejemplo:
  - "¿Cuál es la facturación del mes?" --> medida `[Total Net Sales]` + filtro
    `Calendar[Month] = MONTH(TODAY())`.
  - "¿Cuántos clientes activos tenemos?" --> medida `[Active Customer Count]`.
  - "¿Cuál es el margen promedio?" --> medida `[Avg Margin Pct]`.

Las verified answers tienen prioridad sobre las respuestas generadas dinámicamente,
eliminando el riesgo de error para estas preguntas clave.

### 7. Sinónimos en lenguaje de negocio

Agregar sinónimos a columnas y medidas para que Copilot entienda la terminología que
usan los usuarios del negocio, que puede diferir de los nombres técnicos del modelo:

- `SalesAmountUSD` --> sinónimos: "ingresos", "facturación"
- `CustomerName` --> sinónimos: "cliente", "razón social"
- `ProductCategory` --> sinónimos: "categoría", "línea de producto", "familia"
- `OrderFulfillmentStatus` --> sinónimos: "estado del pedido", "estado de entrega"

Limitar a 1-2 sinónimos por campo para evitar ambigüedad entre sinónimos de campos
diferentes. Los sinónimos se configuran en Power BI Desktop en la vista de Modelo,
en la propiedad "Synonyms" de cada objeto.

### 8. Marcar el modelo como aprobado para Copilot

En Power BI Service, ir al semantic model > **Settings** y activar la opción
**"Approved for Copilot"** (también llamada "Endorsed for Copilot" en algunas versiones).
Esto indica a Power BI que el modelo ha sido revisado y optimizado para su uso con
Copilot, y permite que los usuarios confíen en las respuestas generadas. Solo los
propietarios del dataset pueden activar esta opción.

### 9. Testing continuo con "Ask data questions"

Antes y después de cada cambio significativo en el modelo, probar las preguntas más
comunes usando la experiencia de Q&A:

- En Power BI Service, abrir el reporte y usar "Ask a question about your data".
- Probar al menos 10-15 preguntas representativas del negocio.
- Verificar que los resultados coincidan con los visuales existentes.
- Si Q&A falla, Copilot también fallará -- ambos usan lógica similar para interpretar
  el modelo.
- Documentar las preguntas que fallan y ajustar metadatos hasta que funcionen.

## Cómo prevenirlo

- **Incluir optimización para Copilot en el Definition of Done.** Cada sprint o
  iteración del modelo debe incluir la revisión de descripciones, sinónimos y AI
  Instructions como criterio de aceptación. No es un paso adicional -- es parte
  integral del desarrollo del modelo.
- **Crear un checklist de calidad de metadatos.** Antes de publicar un modelo en
  producción, verificar:
  - [ ] Todas las tablas visibles tienen descripción.
  - [ ] Todas las columnas visibles tienen descripción.
  - [ ] Todas las medidas tienen descripción.
  - [ ] Los nombres son descriptivos y no ambiguos.
  - [ ] Las columnas técnicas están ocultas.
  - [ ] AI Instructions configuradas con reglas de negocio clave.
  - [ ] Al menos 5 verified answers configuradas para KPIs principales.
  - [ ] Sinónimos definidos para campos de uso frecuente.
  - [ ] Testing con Q&A completado sin errores mayores.
- **Designar un "Copilot champion" en cada equipo.** Una persona responsable de
  mantener los metadatos actualizados, configurar AI Instructions, y testear
  periódicamente que Copilot responde correctamente.
- **Automatizar la verificación de metadatos.** Usar scripts (pbi-cli, Tabular Editor
  CLI, o análisis de TMDL) para detectar automáticamente objetos sin descripción,
  columnas visibles que no se usan en reportes, o medidas sin sinónimos.

## Fuentes

- [Microsoft Learn - Optimize your semantic model for Copilot](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)
- [Microsoft Learn - AI Instructions for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-ai-instructions)
- [Microsoft Learn - Q&A best practices](https://learn.microsoft.com/en-us/power-bi/natural-language/q-and-a-best-practices)
- [Microsoft Learn - Verified answers in Q&A](https://learn.microsoft.com/en-us/power-bi/natural-language/q-and-a-tooling-teach-q-and-a)
- [Microsoft Learn - Endorsement for datasets](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-endorse-content)
- [SQLBI - Best practices for Power BI model documentation](https://www.sqlbi.com/articles/)
