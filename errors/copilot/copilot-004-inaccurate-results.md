---
id: copilot-004
title: Copilot genera respuestas incorrectas o DAX inexacto
category: copilot
severity: media
tools: [Desktop, Service]
tags: [Copilot, semantic-model, DAX, inaccurate, metadata, descriptions]
related: [copilot-005]
media:
  images: []
  videos: []
---

## Síntoma

Copilot responde a preguntas del usuario con datos incorrectos, genera DAX que produce
resultados erróneos, o malinterpreta la intención de la pregunta. Los síntomas típicos
incluyen:

- **Números incorrectos.** El usuario pregunta "ventas totales del mes pasado" y Copilot
  devuelve un número que no coincide con lo que muestran los visuales existentes del
  reporte.
- **Campos equivocados.** Copilot usa la columna `Amount` de la tabla de presupuesto
  en lugar de la tabla de ventas, porque ambas se llaman igual.
- **DAX incorrecto.** La medida generada por Copilot usa funciones inapropiadas, omite
  filtros necesarios, o aplica lógica de negocio incorrecta. Por ejemplo, suma valores
  que deberían promediarse, o no excluye registros cancelados.
- **Interpretación errónea.** El usuario pregunta por "clientes activos" y Copilot
  interpreta "activos" como un campo financiero (assets) en lugar del estado del cliente.
- **Respuestas vagas o genéricas.** Copilot responde con información general en lugar
  de datos específicos del modelo, indicando que no pudo interpretar la estructura.

Estos problemas NO son bugs de Copilot. En la gran mayoría de los casos, la causa raíz
está en el modelo semántico.

## Causa

Copilot interpreta las preguntas del usuario usando los metadatos del modelo semántico:
nombres de tablas, nombres de columnas, nombres de medidas, descripciones, relaciones y
la estructura general del schema. Si estos metadatos son ambiguos, incompletos o confusos,
Copilot no tiene suficiente contexto para generar respuestas precisas.

1. **Nombres de campo ambiguos o genéricos.** Columnas llamadas "Amount", "Value", "ID",
   "Status", "Name", "Date" o "Type" sin contexto adicional son la causa principal de
   errores. Si hay una columna `Amount` en la tabla de ventas y otra en la tabla de
   presupuesto, Copilot no sabe cuál usar. Si hay columnas `Date` en tres tablas
   diferentes, Copilot puede elegir la incorrecta para filtrar por tiempo.

2. **Ausencia de descripciones en tablas, columnas y medidas.** Las descripciones son
   el mecanismo principal que tiene Copilot para entender la semántica de cada objeto.
   Sin descripciones, Copilot solo tiene el nombre del campo, que frecuentemente es
   insuficiente. Una medida llamada `Total Revenue` sin descripción no le dice a Copilot
   si incluye impuestos, si excluye devoluciones, o cuál es su moneda.

3. **Nombres duplicados entre tablas.** Cuando múltiples tablas tienen columnas con
   nombres idénticos (`CustomerID` en 4 tablas, `Date` en 3 tablas), Copilot puede
   seleccionar la tabla incorrecta. Esto es especialmente problemático en modelos que
   no siguen un star schema limpio.

4. **Objetos no utilizados que agregan ruido.** Columnas importadas pero nunca usadas
   en reportes, medidas obsoletas que ya no aplican, tablas de staging que quedaron
   visibles -- todo esto genera ruido que confunde a Copilot. Mientras más objetos
   tenga que evaluar, mayor la probabilidad de seleccionar el incorrecto.

5. **Sin AI Instructions configuradas.** Power BI permite configurar "AI Instructions"
   a nivel del modelo semántico, que son instrucciones en lenguaje natural que guían a
   Copilot sobre cómo interpretar el modelo. Sin estas instrucciones, Copilot no conoce
   las reglas de negocio específicas (por ejemplo, que "ventas" siempre debe excluir
   devoluciones, o que "mes actual" se define como el mes calendario completo más
   reciente).

6. **Sin sinónimos definidos.** Los usuarios pueden referirse a un campo de formas
   diferentes a como está nombrado en el modelo. Si la columna se llama
   `TransactionAmount` pero el usuario dice "ingresos" o "facturación", Copilot puede
   no hacer la conexión. Los sinónimos resuelven este gap.

7. **Sin verified answers para KPIs clave.** Verified answers son respuestas
   predefinidas y validadas para preguntas de negocio frecuentes. Sin ellas, Copilot
   genera la respuesta dinámicamente, lo que introduce riesgo de error para preguntas
   de alta importancia (como "¿cuál fue la facturación del trimestre?").

## Solución paso a paso

1. **Renombrar campos a nombres descriptivos de negocio.** Cambiar nombres genéricos
   a nombres que reflejen el contexto de negocio:
   - `Amount` en la tabla Sales --> `SalesAmount`
   - `Amount` en la tabla Budget --> `BudgetAmount`
   - `Date` en la tabla Calendar --> `CalendarDate`
   - `ID` en la tabla Customer --> `CustomerID`
   - `Status` en la tabla Orders --> `OrderStatus`
   Usar PascalCase o espacios según la convención del equipo, pero siempre incluyendo
   el contexto de la tabla.

2. **Agregar descripciones a todos los objetos.** En Power BI Desktop, seleccionar cada
   tabla, columna y medida en el panel de Modelo y agregar una descripción en el panel
   de Propiedades. Las descripciones deben ser concisas pero informativas:
   - Tabla: "Tabla de hechos con todas las transacciones de venta desde 2020. Cada fila
     es una línea de factura."
   - Columna: "Monto neto de la venta en USD, después de descuentos pero antes de
     impuestos."
   - Medida: "Suma de SalesAmount filtrada para excluir devoluciones (OrderStatus <>
     'Returned'). Moneda: USD."

3. **Configurar AI Instructions.** En Power BI Service, ir al semantic model >
   **Settings > AI Instructions** y agregar instrucciones que definan reglas de negocio:
   - "Cuando el usuario pregunte por 'ventas', usar siempre la medida [Total Net Sales]
     que excluye devoluciones."
   - "El año fiscal de la empresa empieza en abril. 'Year' se refiere al año fiscal."
   - "Todos los montos monetarios están en USD salvo que se indique lo contrario."
   - "La tabla Calendar es la tabla de fechas maestra para todo filtro temporal."

4. **Definir sinónimos.** En Power BI Desktop, en la vista de Modelo, seleccionar una
   columna o medida y agregar sinónimos en el panel de Propiedades:
   - `SalesAmount` --> sinónimos: "ingresos", "facturación", "revenue"
   - `CustomerName` --> sinónimos: "cliente", "razón social", "nombre del cliente"
   Limitar a 1-2 sinónimos por campo para evitar ambigüedad.

5. **Configurar verified answers.** En Power BI Service, ir al semantic model >
   **Settings > Q&A settings > Suggest questions** y definir respuestas verificadas
   para preguntas clave del negocio. Por ejemplo:
   - "¿Cuál es la facturación total?" --> medida `[Total Net Sales]` con el filtro
     de fecha apropiado.
   - "¿Cuántos clientes activos tenemos?" --> medida `[Active Customer Count]`.

6. **Eliminar objetos no utilizados.** Usar la herramienta **Measure Killer**
   (disponible como External Tool) o revisar manualmente el modelo para identificar
   columnas y medidas que no se usan en ningún visual ni cálculo. Ocultarlas o
   eliminarlas para reducir el ruido. Como mínimo, ocultar las columnas de claves
   foráneas que solo sirven para relaciones.

7. **Simplificar el schema.** Si el modelo tiene tablas de staging, tablas auxiliares
   de ETL, o tablas duplicadas, reorganizarlo hacia un star schema limpio. Copilot
   funciona mejor con modelos que tienen tablas de hechos claramente identificables
   y dimensiones bien definidas.

8. **Probar con "Ask data questions".** Antes de usar Copilot en producción, probar
   las preguntas más comunes en la experiencia de Q&A ("Ask a question about your data")
   para verificar que el modelo responde correctamente. Q&A usa una lógica similar a
   Copilot para interpretar el modelo.

## Cómo prevenirlo

- **Tratar los metadatos como parte del desarrollo del modelo.** Incluir la definición
  de descripciones, sinónimos y AI Instructions como parte del Definition of Done de
  cada iteración del modelo semántico. No es un paso opcional -- es fundamental para
  que Copilot funcione correctamente.
- **Establecer convenciones de nombrado.** Definir un estándar organizacional para
  nombres de tablas, columnas y medidas. Tablas de hechos con nombres de acción
  (`SalesTransactions`, `OrderLines`), dimensiones con nombres de entidad (`Customer`,
  `Product`, `Calendar`), medidas con prefijo de operación (`Total`, `Avg`, `Count`,
  `Pct`).
- **Revisar el modelo periódicamente.** Cada trimestre, revisar el modelo para
  identificar objetos obsoletos, descripciones desactualizadas y sinónimos faltantes.
  Usar la documentación del modelo (exportada con pbi-cli o Tabular Editor) como base.
- **Capacitar a los usuarios.** Comunicar al equipo que las preguntas a Copilot
  funcionan mejor cuando usan el vocabulario del modelo. Compartir una lista de los
  campos y medidas principales con sus nombres exactos.
- **Usar Copilot como test del modelo.** Si Copilot no puede responder correctamente
  una pregunta simple, es un indicador de que el modelo necesita mejoras en metadatos.

## Fuentes

- [Microsoft Learn - Optimize your semantic model for Copilot](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)
- [Microsoft Learn - AI Instructions for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-ai-instructions)
- [Microsoft Learn - Q&A best practices for Power BI](https://learn.microsoft.com/en-us/power-bi/natural-language/q-and-a-best-practices)
- [Microsoft Learn - Copilot for Power BI report pages](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-report)
- SQLBI - Best practices for naming conventions in Power BI models
