---
id: modelo-005
title: No se ha podido publicar el reporte en Power BI Service
category: modelo
severity: alta
tools: [Desktop, Service]
tags: [publish, semantic-model, column-error, validation]
search_hints:
  - "No se ha podido publicar el archivo en Power BI"
  - "We couldn't publish to Power BI"
  - "no se pudo publicar el reporte"
  - "error al publicar power bi"
  - "publish failed power bi"
  - "couldn't publish to power bi"
  - "no se ha podido publicar"
related: []
media:
  images: [modelo-005-fig1.png]
  videos: []
---

## Síntoma

Al intentar publicar un `.pbix` desde Power BI Desktop al Service, aparece:

> No se ha podido publicar el archivo en Power BI
>
> (o en inglés: "We couldn't publish to Power BI")

El upload no se completa. El reporte queda solo localmente.

## Causa

Casi siempre indica que el **modelo semántico tiene un error de validación**
que Desktop no bloquea al guardar pero el Service rechaza al validar.

Causas frecuentes:

- Una **columna calculada** o **medida** quedó con expresión inválida
  (referencia a columna borrada, sintaxis rota, tipo incompatible).
- Una columna tiene un tipo de dato declarado distinto del que devuelve
  la consulta (ej. `Decimal Number` pero llegan strings).
- Una relación quedó inconsistente tras renombrar columnas.
- Roles de RLS con expresiones DAX que no compilan.
- Modelo demasiado grande para la capacidad destino (ver `servicio-002`).

## Solución paso a paso

1. **Abrir `View > Performance analyzer` o `Model view`** y refrescar las
   tablas una por una. La primera que falle es la que tiene el problema.

2. **Revisar el panel de "Errores":**
   - En Desktop, `View > Issues` o el ícono de campana arriba a la derecha
     suele mostrar columnas/medidas con error.
   - Las tablas afectadas aparecen con un signo de exclamación.

3. **Inspeccionar medidas y columnas calculadas recientes.** Hacer click en
   cada una para ver el panel de expresión — Desktop subraya las que tienen
   error sintáctico.

4. **Tipos de columna en Power Query:**
   - `Transform data` → cada tabla → revisar el paso `Changed Type`.
   - Si una columna tiene valores nulos o textos donde se espera número,
     forzar el tipo correcto o limpiar antes.

5. **Probar guardar el `.pbix` con un nombre nuevo** y re-publicar. A veces
   el archivo queda corrupto y reabrirlo limpio resuelve.

6. **Si el modelo es muy grande**, validar el tamaño contra la capacidad del
   workspace destino (ver `servicio-002`).

## Cómo prevenirlo

- Hacer `File > Save` y luego cerrar/abrir el .pbix antes de publicar — fuerza
  una revalidación completa del modelo.
- Mantener un changelog corto de qué medidas/columnas se modificaron en cada
  versión para acotar el debug si rompe la publicación.
- Para reportes críticos, validar la publicación en un workspace de DEV antes
  de subir al de PROD.

## Fuentes

- [Microsoft Docs - Publish from Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-upload-desktop-files)
- [Troubleshooting publish issues](https://learn.microsoft.com/en-us/power-bi/troubleshoot/)
