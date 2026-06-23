---
id: conn-006
title: 3802 Database does not exist (Teradata)
category: conexion
severity: alta
tools: [Desktop, Service, Gateway]
tags: [teradata, permissions, view, sql, 3802, 42S02]
search_hints:
  - "Failed [3802 : 42S02] Database does not exist"
  - "Database does not exist Teradata"
  - "no existe vista en sql"
  - "no existe la base de datos teradata"
  - "la tabla no existe en teradata"
  - "Select Statement failed 3802"
  - "me sacaron los permisos teradata"
related: [conn-005]
media:
  images: [conn-006-fig1.png]
  videos: []
---

## Síntoma

Al ejecutar una consulta o al refrescar una tabla que viene de Teradata, aparece:

> Executed as Single statement. Failed [3802 : 42S02] Database 'F_DIM_V' does
> not exist.
>
> Elapsed time = 00:00:00.009
> STATEMENT 1: Select Statement failed.

La query funcionaba ayer pero hoy ya no devuelve datos.

## Causa

El código de error `3802` de Teradata es engañoso: dice "Database does not
exist", pero en la práctica también se dispara cuando la base/vista **existe
pero el usuario no tiene permiso de lectura** sobre ella.

Causas frecuentes:

- Permiso revocado a nivel de usuario sobre la vista o database.
- Cambió la pertenencia del usuario a un rol/grupo de Teradata.
- Se hizo un refactor del modelo de datos y la vista cambió de schema.
- Conexión apuntando a otro environment (dev/prod) donde la vista no existe.

## Solución paso a paso

1. **Confirmar que la vista existe** desde una herramienta administrativa
   (Teradata Studio, dbeaver) con un usuario admin:
   ```sql
   SELECT * FROM DBC.TablesV WHERE DatabaseName = 'F_DIM_V';
   ```

2. **Verificar permisos del usuario sobre la base/vista:**
   ```sql
   SELECT * FROM DBC.AllRights
   WHERE UserName = 'RY22146' AND DatabaseName = 'F_DIM_V';
   ```

3. **Pedir el alta de permisos al facilitador del dato.**
   - Identificar al dueño del schema `F_DIM_V`.
   - Solicitar `SELECT` sobre la vista o sobre el rol que la incluye.

4. **Validar el ambiente** al que apunta la conexión. Confirmar que el server
   en la conexión de Power Query es el correcto (DEV vs PROD).

5. Refrescar la consulta. Si el error persiste, hacer un `Test connection`
   desde Power BI Desktop con las credenciales del usuario actual.

## Cómo prevenirlo

- Manejar accesos a Teradata vía roles/grupos, no permisos directos por
  usuario — facilita auditoría y alta de nuevos miembros.
- Documentar qué vistas usa cada reporte clave, así cuando alguien pierde
  acceso se identifica el impacto rápido.
- Para reportes críticos, usar **Service Principal** o cuenta técnica con
  permisos estables en lugar de credenciales personales.

## Fuentes

- [Teradata error 3802 reference](https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/SQL-Messages/Messages/3700-3899)
- [Power BI - Connect to Teradata](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-connect-teradata)
