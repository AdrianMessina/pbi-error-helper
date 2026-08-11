---
id: conn-002
title: DataSource.Error - ODBC connection failure (acceso denegado)
category: conexion
severity: alta
tools: [Desktop, Service]
tags: [ODBC, SQL, permisos, credenciales, base-datos, dataflow]
related: [pq-002, conn-001]
media:
  images: ["DataSource.Error ODBC error connection failure.png"]
  videos: []
---

## Síntoma

Al intentar conectarse a una base de datos SQL Server (u otro origen ODBC) en Power Query, aparece:

> DataSource.Error: ODBC: ERROR [08001] [SAP AG][LIBODBCHDB DLL][HDBODBC] Communication link failure;-10709 Connect failed
> Details:
>   DataSourceKind=SapHana
>   DataSourcePath=slpsrusjp001:30015
>   Message=ODBC: ERROR [08001] Communication link failure;-10709 Connect failed (connect timeout expired)

El preview de la tabla queda vacío y el refresh falla.

## Causa

El error se debe a que tu usuario **no tiene permisos** para leer la base de datos especificada.

Causas específicas:

- Tu cuenta de Active Directory (o SQL Login) no fue agregada a la base de datos.
- Tenés permisos solo en ciertas tablas, pero la query intenta leer otras.
- La base de datos usa **autenticación de Windows** y estás usando credenciales SQL incorrectas (o viceversa).
- El origen requiere VPN o acceso desde red corporativa, y estás trabajando desde fuera.
- El timeout se produce porque el servidor espera credenciales que nunca llegan.

## Solución paso a paso

### Opción A — Reutilizar un flujo de datos existente

Si alguien más del equipo ya tiene acceso:

1. Verificar si existe un **Dataflow** (flujo de datos) en el Power BI Service que ya se conecte a esta base de datos.
2. En Power BI Desktop:
   - `Get Data > Power Platform > Dataflows`
   - Seleccionar el workspace donde está el dataflow.
   - Elegir las tablas necesarias.
3. Guardar y refrescar. Esto evita que tu usuario necesite permisos directos en la base.

### Opción B — Solicitar acceso a la base de datos

Si necesitás acceso directo:

1. Identificar el servidor y base de datos del error:
   - En el ejemplo: servidor `slpsrusjp001:30015`, base de datos (verificar en connection string).
2. Contactar al **DBA** (administrador de bases de datos) o al equipo de IT.
3. Solicitar:
   - **Permisos de lectura** (`db_datareader` para SQL Server, o equivalente en SAP HANA/Oracle).
   - Especificar las tablas concretas si es posible (principio de mínimo privilegio).
4. Una vez otorgados los permisos:
   - En Power Query: `Data source settings > Edit Permissions`
   - Actualizar o reingresar las credenciales (Windows o Database).
5. Reintentar la conexión.

### Opción C — Cambiar el origen de datos en Power Query

Si el origen original no es accesible y no hay flujo de datos:

1. `Power Query Editor > Home > Data source settings`
2. Seleccionar el origen problemático → `Change Source`
3. Reemplazar por:
   - Una fuente alternativa con los mismos datos (ej: archivo Excel exportado, SharePoint List).
   - Un **flujo de datos** (dataflow) que actúe como intermediario.
   - Una vista o tabla materializada en otra base de datos a la que sí tengas acceso.
4. Aplicar cambios y guardar.

### Opción D — Verificar credenciales y método de autenticación

1. En Power BI Desktop: `File > Options and settings > Data source settings`
2. Localizar el servidor en la lista → `Edit Permissions`
3. Verificar:
   - **Credentials**: ¿estás usando Windows, Database, o OAuth?
   - Si dice "Windows": asegurarte de que tu cuenta AD tiene permisos.
   - Si dice "Database": verificar usuario/contraseña SQL.
4. Cambiar el tipo de credencial si es necesario y reintentar.

## Cómo prevenirlo

- **Planificar permisos temprano**: al iniciar un proyecto, listar todas las fuentes de datos y solicitar acceso antes de empezar.
- **Usar cuentas de servicio** para conexiones productivas en el Service (evita problemas cuando usuarios individuales cambian de rol o se van).
- **Centralizar acceso vía Dataflows**: crear flujos de datos administrados por un equipo central con permisos ya establecidos, y que el resto del equipo consuma desde ahí.
- **Documentar fuentes**: mantener un catálogo de qué bases de datos existen, quién tiene acceso, y cómo solicitarlo.

## Fuentes

- [Microsoft Docs - Power BI data sources](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-sources)
- [SAP HANA connector documentation](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-sap-hana)
- [Troubleshoot ODBC errors in Power Query](https://learn.microsoft.com/en-us/power-query/odbc-troubleshoot)
