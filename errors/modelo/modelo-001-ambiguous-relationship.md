---
id: modelo-001
title: Relación ambigua entre tablas (ambiguous path)
category: modelo
severity: alta
tools: [Desktop]
tags: [model, relationships, bidirectional, star-schema]
related: [dax-001]
media:
  images: []
  videos: []
---

## Síntoma

Al crear una relación en el modelo, Power BI Desktop la marca como **inactiva** (línea
punteada) y muestra:

> You can't create a direct active relationship between [TableA] and [TableB] because
> there is already an active relationship path between these tables.

O al evaluar una medida aparece resultado incorrecto / `BLANK` sin causa obvia.

## Causa

Power BI requiere que entre cualquier par de tablas exista **un único camino activo
de relaciones**. Cuando hay dos o más caminos posibles, el motor no sabe cuál usar
y la ambigüedad se debe romper.

Escenarios típicos:

- Una tabla de hechos relacionada con la misma dimensión por dos columnas (ej:
  `Ventas` con `Fechas` por `FechaPedido` y `FechaEntrega`).
- Relaciones bidireccionales (`<->`) que crean ciclos en el grafo.
- Snowflake con múltiples saltos desde una dimensión hacia otra vía tabla puente.

## Solución paso a paso

### Caso A — Dos relaciones a la misma dimensión

1. Dejar **una sola activa** (la más usada) y la otra como **inactiva**.
2. En las medidas que necesitan la inactiva, usar `USERELATIONSHIP`:
   ```dax
   Ventas por FechaEntrega =
   CALCULATE(
       SUM(Ventas[Monto]),
       USERELATIONSHIP(Ventas[FechaEntrega], Fechas[Fecha])
   )
   ```

### Caso B — Relaciones bidireccionales causan ambigüedad

1. Identificar la(s) relación(es) `<->` involucrada(s) en el ciclo.
2. Cambiar a **single direction** (`>`) — del lado del 1 hacia el N.
3. Si necesitabas filtrado cruzado, replicarlo con `CROSSFILTER` en medidas
   específicas en lugar de globalmente.

### Caso C — Snowflake con caminos múltiples

1. Considerar **aplanar** las dimensiones en una sola (estrella en lugar de
   snowflake) — es la práctica recomendada.
2. Si no se puede aplanar, marcar como inactivas las relaciones que generan caminos
   alternativos y usar `USERELATIONSHIP` puntualmente.

## Cómo prevenirlo

- **Modelar en estrella** desde el inicio — una tabla de hechos central + dimensiones
  conectadas con una sola relación cada una.
- **Evitar bidireccionales por defecto.** Habilitarlas solo cuando el caso de uso
  específico lo justifica (típicamente: tablas puente many-to-many controladas).
- Para fechas múltiples, usar **role-playing dimensions** (varias tablas de fechas)
  o `USERELATIONSHIP`, no dos relaciones activas.

## Fuentes

- [Microsoft Docs - Model relationships in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand)
- SQLBI - Relationships in Power BI and Tabular models
