---
id: dax-005
title: División por cero muestra error en visuals o DIVIDE devuelve BLANK inesperado
category: dax
severity: baja
tools: [Desktop, Service]
tags: [DIVIDE, division-by-zero, error-handling]
related: [dax-002, dax-001]
media:
  images: []
  videos: []
---

## Síntoma

Al usar una medida que involucra división, se observa uno de estos problemas:

- Un visual (tabla, tarjeta, gráfico) muestra **"Error"** o **"NaN"** en lugar de un
  valor numérico, porque el denominador es cero en algún contexto de filtro.
- La medida usa `DIVIDE` pero devuelve **BLANK** en filas donde el usuario esperaba ver
  `0` o un mensaje personalizado, causando que esas filas desaparezcan del visual.
- Al usar el operador `/` directamente, Power BI muestra el error:
  > "Cannot perform the operation because of an arithmetic overflow or division by zero."

Esto es especialmente visible en matrices con muchas combinaciones de filtros, donde
algunas celdas tienen denominador cero (ej: un producto sin ventas en cierto mes).

## Causa

En DAX existen dos formas de dividir, con comportamiento muy diferente ante el cero:

1. **Operador `/`:** `[Numerador] / [Denominador]` — si el denominador es `0` o `BLANK`,
   DAX genera un error de infinito. Ese error se propaga al visual y se muestra como
   "Error" o "Infinity".

2. **Función `DIVIDE`:** `DIVIDE([Numerador], [Denominador])` — si el denominador es `0`
   o `BLANK`, devuelve `BLANK` por defecto (tercer argumento). Esto es seguro pero
   puede causar que filas "desaparezcan" del visual porque Power BI oculta filas con
   BLANK (ver dax-002).

Causas frecuentes de denominador cero:

- **Filtro que elimina todas las filas:** un slicer selecciona un producto que no tiene
  ventas en cierto período, haciendo que `SUM(Ventas[Cantidad])` devuelva BLANK (que
  DAX trata como 0 en contexto aritmético).
- **Datos incompletos:** filas con cantidad = 0 en la fuente de datos.
- **Medida de ratio sin protección:** `[Ventas] / [Presupuesto]` donde no todos los
  productos tienen presupuesto cargado.

## Solución paso a paso

1. **Reemplazar el operador `/` por la función `DIVIDE`** en todas las medidas que
   puedan tener denominador cero:
   ```dax
   -- INCORRECTO: puede generar error
   Margen % = [Ganancia] / [Ventas]

   -- CORRECTO: devuelve BLANK si Ventas = 0
   Margen % = DIVIDE([Ganancia], [Ventas])
   ```

2. **Si BLANK no es el resultado deseado**, especificar un valor alternativo como tercer
   argumento de `DIVIDE`:
   ```dax
   -- Devuelve 0 en lugar de BLANK cuando no hay ventas
   Margen % = DIVIDE([Ganancia], [Ventas], 0)
   ```

3. **Para mostrar un mensaje personalizado** en lugar de un número, combinar con `IF`:
   ```dax
   Margen % Display =
   VAR _denominador = [Total Ventas]
   VAR _resultado = DIVIDE([Ganancia], _denominador)
   RETURN
       IF(
           _denominador = 0,
           "Sin ventas",
           FORMAT(_resultado, "0.0%")
       )
   ```
   Nota: esta medida devuelve texto, por lo que no se puede usar en gráficos numéricos.

4. **Si se necesita que las filas con denominador cero sigan visibles** con valor `0` en
   el visual (en lugar de desaparecer), usar el tercer argumento:
   ```dax
   Precio Promedio = DIVIDE([Total Ventas], [Cantidad Vendida], 0)
   ```

5. **Para medidas de porcentaje que alimentan formato condicional**, asegurarse de que
   el valor alternativo sea numérico y consistente:
   ```dax
   Cumplimiento % =
   VAR _meta = [Meta Ventas]
   VAR _real = [Ventas Reales]
   RETURN
       DIVIDE(_real, _meta, 0)
   ```
   Esto garantiza que las reglas de formato condicional (ej: rojo < 80%, verde > 100%)
   funcionen correctamente incluso cuando no hay meta definida.

## Cómo prevenirlo

- **Estándar del proyecto:** usar `DIVIDE()` en lugar del operador `/` como regla por
  defecto en todas las medidas. El operador `/` solo debería usarse cuando se tiene
  certeza absoluta de que el denominador nunca será cero.
- **Definir el tercer argumento conscientemente.** No depender del BLANK por defecto si
  la medida alimenta tarjetas, KPIs o gráficos donde BLANK causa problemas de
  visualización (ver dax-002).
- **Validar datos en la fuente:** agregar controles en Power Query o en el ETL para
  detectar y tratar valores cero en columnas que se usan frecuentemente como
  denominadores (ej: cantidades, presupuestos, metas).
- **Usar variables (`VAR`)** para calcular el denominador una sola vez y reutilizarlo
  tanto en el `DIVIDE` como en lógica condicional, mejorando legibilidad y rendimiento.

## Fuentes

- [Microsoft Docs - DIVIDE function](https://learn.microsoft.com/en-us/dax/divide-function-dax)
- [SQLBI - Use DIVIDE instead of /](https://www.sqlbi.com/articles/use-divide-instead-of-dividing/)
- [Microsoft Docs - DAX Best Practices](https://learn.microsoft.com/en-us/power-bi/guidance/dax-divide-function-operator)
- [SQLBI - Handling errors in DAX](https://www.sqlbi.com/articles/handling-errors-in-dax/)
