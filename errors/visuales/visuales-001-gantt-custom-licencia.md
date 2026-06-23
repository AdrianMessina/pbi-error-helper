---
id: visuales-001
title: Visual custom no carga (licencia faltante o caducada)
category: visuales
severity: media
tools: [Desktop, Service]
tags: [custom-visual, gantt, license, appsource, marketplace]
search_hints:
  - "El visual requiere una licencia"
  - "the visual requires a license"
  - "trial expired visual custom"
  - "falla en la carga visualización custom licencia"
  - "error grafico de gantt"
  - "visual custom no carga"
  - "visual personalizado licencia caducada"
related: []
media:
  images: [visuales-001-fig1.png]
  videos: []
---

## Síntoma

Una visualización del reporte (típicamente un Gantt, KPI avanzado, mapa
específico u otro visual no nativo) muestra en lugar del gráfico:

> El visual requiere una licencia.
>
> O bien: ícono de error / cuadro en blanco / mensaje de "trial expired".

El resto del reporte funciona normal. Solo ese visual está roto.

## Causa

Es un **visual custom** importado desde AppSource o un archivo `.pbiviz`
externo, y:

- La **licencia comercial nunca se compró** y terminó el período trial.
- La licencia expiró y no se renovó.
- El visual fue removido de AppSource o el publisher lo discontinuó.
- En el tenant están bloqueados los visuales no certificados y este es uno.

Los visuales custom más comunes que caen en esto en YPF: **Gantt by MAQ
Software**, **Drill Down Donut**, **Hierarchy Slicer Pro**, **Power KPI**,
y similares de marketplace.

## Solución paso a paso

1. **Identificar el visual exacto:**
   - Desktop → click en el visual → panel `Visualizations` → ver el nombre y
     el ícono → suele decir el publisher al hover.
   - Si solo tenés el `.pbix` publicado, abrir el reporte en Desktop con un
     usuario con licencia válida (si existe) para confirmar el nombre.

2. **Validar el estado de la licencia:**
   - El publisher del visual suele tener un portal donde se renueva.
   - Pedir al área de compras si la licencia corporativa sigue vigente.

3. **Elegir entre estas opciones:**

   **A — Renovar la licencia** (si el visual sigue siendo útil y se usa en
   varios reportes).

   **B — Reemplazar el visual por uno nativo o por un visual certificado
   gratuito:**
   - Gantt → existen alternativas nativas usando matriz + barras condicionales
     o usando "Gantt by Microsoft" si está disponible.
   - KPI → usar las cards/multi-row cards nativas.
   - Custom slicers → casi siempre hay un slicer nativo equivalente.

   **C — Reemplazar por un visual custom certificado por Microsoft**
   (gratuito, sin riesgo de discontinuación).

4. **Si el tenant bloquea visuales no certificados** (tenant setting), pedir
   al admin que lo agregue a la lista permitida — pero solo si el visual está
   certificado o auditado.

5. **Aplicar el cambio en el `.pbix`**, validar que el visual reemplazado
   muestra los mismos datos, y publicar.

## Cómo prevenirlo

- **Preferir siempre visuales certificados por Microsoft**. La marca de
  "Certified" garantiza que el publisher cumple con seguridad y que no se va
  a desaparecer del marketplace sin aviso.
- Mantener un inventario de qué reportes usan qué visuales custom + estado
  de licencia.
- En lo posible, evitar visuales custom para reportes de uso amplio. Si un
  visual nativo sirve, usá el nativo: cero riesgo de licencias.

## Fuentes

- [Microsoft - Certified Power BI visuals](https://learn.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals-certified)
- [AppSource - Power BI visuals](https://appsource.microsoft.com/en-us/marketplace/apps?product=power-bi-visuals)
