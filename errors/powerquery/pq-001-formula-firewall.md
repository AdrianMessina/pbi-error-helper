---
id: pq-001
title: Formula.Firewall - Query references other queries
category: powerquery
severity: alta
tools: [Desktop, Service]
tags: [power-query, M, privacy-levels, refresh]
related: [refresh-001]
media:
  images: []
  videos: []
---

## Síntoma

Al actualizar (refresh) o previsualizar una query en Power Query Editor, aparece:

> Formula.Firewall: Query 'X' (step 'Y') references other queries or steps, so it
> may not directly access a data source. Please rebuild this data combination.

El refresh falla o el preview queda en blanco.

## Causa

El "Firewall" de Power Query es un mecanismo de seguridad que evita que datos de
una fuente con un nivel de privacidad (Private/Organizational/Public) se mezclen
inadvertidamente con otra fuente de nivel distinto.

Disparadores típicos:

- Una query lee un **parámetro** o **otra query** que a su vez referencia un origen
  de datos, y los combinás en el mismo paso (merge, append, lookup).
- Dos sources con **privacy levels distintos** mezclados en un solo paso.
- Uso de funciones M dinámicas (`Web.Contents(parameter)`) donde la URL se construye
  a partir de otra query.

## Solución paso a paso

### Opción A — Configurar privacy levels (rápido)

1. `File > Options and settings > Options > Current File > Privacy`
2. Marcar **"Ignore the Privacy Levels and potentially improve performance"**.
3. Aplicar y refrescar.

Limitación: solo afecta a tu archivo local. Si publicás al Service y usás Gateway,
también hay que setearlo allá.

### Opción B — Rediseñar la query (correcto)

1. Identificar las dos queries involucradas: la que hace de "source" y la que
   "referencia".
2. Combinar todo en una **única query** sin referencias cruzadas a steps externos.
   Por ejemplo, si tenés `URL = Param1 & "/api"` y después `Web.Contents(URL)`,
   inlineá el parámetro: `Web.Contents(Param1 & "/api")`.
3. Si necesitás reutilizar lógica, usá **funciones M custom** en lugar de queries
   intermedias.

### Opción C — Igualar privacy levels en el Service

1. En powerbi.com → **Datasets > Settings > Data source credentials**.
2. Para cada source listada, expandir y setear el mismo **Privacy level**
   (típicamente Organizational).
3. Reintenar el refresh.

## Cómo prevenirlo

- **Definir privacy levels temprano** y de forma consistente en todas las fuentes.
- Evitar construir URLs o paths dinámicamente desde queries — usar parámetros
  estáticos cuando sea posible.
- Para fuentes mixtas (SharePoint + SQL + Web), considerar **staging queries**
  separadas que se materialicen y después se combinen sin referencias dinámicas.

## Fuentes

- [Microsoft Docs - Power Query Privacy Levels](https://learn.microsoft.com/en-us/power-query/data-privacy-firewall)
- Chris Webb - The Power Query Firewall
