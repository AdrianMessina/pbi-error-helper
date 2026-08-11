---
id: version-001
title: Can't resolve schema - Please update version
category: version
severity: alta
tools: [Desktop]
tags: [version, schema, report.json, actualización, compatibilidad]
related: []
media:
  images: ["Cant resolve schema please update version.png"]
  videos: []
---

## Síntoma

Al intentar abrir un archivo `.pbix` o un proyecto `.pbip` en Power BI Desktop, aparece:

> Se produjo un error.
> Can't resolve schema '3.3.0' in 'report.json'. Please update to the latest version of Power BI Desktop and retry.

El archivo no se abre y puede quedar bloqueado.

## Causa

El archivo de reporte fue creado o guardado con una **versión más reciente** de Power BI Desktop que la que tenés instalada actualmente.

Power BI Desktop actualiza el schema del archivo `report.json` (que define la estructura del reporte, páginas, visuales, etc.) con cada release. Versiones anteriores no pueden interpretar schemas más nuevos y rechazan el archivo.

Escenarios comunes:

- Alguien del equipo tiene auto-update habilitado y guardó el archivo con la versión del mes.
- El archivo vino de un tenant corporativo con versión enterprise (Report Server) diferente a Desktop público.
- Se bajó un template o ejemplo de la web creado con una versión preview.

## Solución paso a paso

### Paso 1 — Actualizar Power BI Desktop

1. Descargar la última versión desde:
   - [https://powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop)
2. **Cerrar completamente** Power BI Desktop (verificar en Task Manager que no quede ningún proceso `PBIDesktop.exe`).
3. Ejecutar el instalador descargado.
4. Reiniciar Power BI Desktop e intentar abrir el archivo nuevamente.

### Paso 2 — Verificar la versión instalada

1. Abrir Power BI Desktop.
2. `Help > About` → verificar el número de versión (ej: `Version: 2.134.xxx.0 (August 2026)`).
3. Comparar con la versión requerida en el mensaje de error (schema `3.3.0` = versión reciente de 2026).

### Paso 3 — Si el problema persiste

- **Si estás en un entorno corporativo gestionado**: verificar con IT si hay políticas de grupo o restricciones que impidan actualizar. Puede ser necesario abrir un ticket interno.
- **Si el archivo es `.pbip` (proyecto)**: verificar en el archivo `definition/report.json` dentro de la carpeta del proyecto la línea `"$schema"` y confirmar qué versión requiere.

## Cómo prevenirlo

- **Habilitar auto-update** en todo el equipo:
  - `File > Options and settings > Options > Global > Updates`
  - Marcar **"Automatically download and install updates"**.
- **Acordar una política de versión**: si trabajás en equipo, definir que todos usen la misma versión (ej: siempre la del mes en curso, o una versión fija por 3 meses).
- **Guardar copia de compatibilidad**: si necesitás compartir con usuarios que no pueden actualizar, considerar usar **Power BI Service** como punto intermedio (publicar y que descarguen desde allí).
- **Documentar la versión mínima** en el README o wiki del proyecto.

## Fuentes

- [Microsoft Docs - Power BI Desktop release notes](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update)
- [Power BI Desktop download page](https://powerbi.microsoft.com/desktop)
