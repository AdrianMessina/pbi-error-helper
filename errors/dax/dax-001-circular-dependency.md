---
id: dax-001
title: Circular dependency detected
category: dax
severity: alta
tools: [Desktop, Service]
tags: [calculated-column, measure, CALCULATE, dependency]
related: [dax-002]
media:
  images: []
  videos: []
---

## Síntoma

Al crear o editar una medida o columna calculada, Power BI muestra el error:

> A circular dependency was detected: Table[ColumnA], Table[ColumnB], Table[ColumnA].

La medida no se guarda, o queda guardada pero rompe el refresh / la evaluación del modelo.

## Causa

Power BI necesita resolver el orden de evaluación de cada expresión DAX. Si dos o más
columnas calculadas o medidas se referencian entre sí — directa o indirectamente — no
hay un orden válido y el motor aborta.

Causas frecuentes:

- Una **columna calculada** que usa `CALCULATE()` con un filtro que toca otra columna
  calculada de la misma tabla.
- Dos columnas calculadas que se referencian mutuamente: `A = B + 1` y `B = A * 2`.
- Una medida que usa `EARLIER()` o variables en un contexto que reintroduce la propia
  medida en la evaluación.
- Relaciones bidireccionales que generan dependencias circulares ocultas entre tablas.

## Solución paso a paso

1. **Identificar la cadena de dependencias.** Power BI te dice las primeras dos columnas
   en el mensaje. Buscá ambas en el panel de Campos.

2. **Decidir cuál ruptura aplica:**
   - Si una de las dos puede ser **medida** en lugar de columna calculada → moverla a
     medida elimina la dependencia (las medidas se evalúan en contexto de query, no de
     fila).
   - Si ambas deben ser columnas calculadas, eliminá la dependencia transitiva: hacé
     que una se calcule a partir de columnas base, no derivadas.

3. **Si interviene `CALCULATE` en una columna calculada**, reemplazá los filtros
   internos por expresiones que no toquen columnas calculadas. Idealmente:
   - Usá columnas físicas (de la fuente) como base.
   - Movelo a medida si el resultado se agrega.

4. **Si hay relaciones bidireccionales**, revisá si son necesarias. Una relación
   bidireccional entre dos tablas con columnas calculadas que cruzan ambas direcciones
   genera circularidad en el grafo de dependencias.

5. Guardar y verificar que el error desaparezca. Si el modelo es complejo, exportar
   TMDL y revisar la sección de columnas y medidas para entender la cadena.

## Cómo prevenirlo

- **Regla práctica:** las columnas calculadas se calculan en tiempo de refresh y en
  contexto de fila — usalas solo cuando necesitás materializar el valor. Para casi
  todo lo agregado, preferí **medidas**.
- Evitar `CALCULATE` dentro de columnas calculadas — es una de las causas #1 de este
  error.
- Documentar la cadena de dependencias críticas del modelo para que futuros cambios
  no la rompan silenciosamente.

## Fuentes

- [Documentación oficial Microsoft - Circular Dependencies](https://learn.microsoft.com/en-us/dax/best-practices/dax-formula-error-detected)
- SQLBI - Understanding circular dependencies in DAX
