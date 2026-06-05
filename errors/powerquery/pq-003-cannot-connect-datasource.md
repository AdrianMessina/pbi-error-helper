---
id: pq-003
title: DataSource.Error - No se puede conectar al origen de datos
category: powerquery
severity: alta
tools: [Desktop, Service, Gateway]
tags: [data-source, connection, credentials, path]
related: [conn-001, refresh-001]
media:
  images: []
  videos: []
---

## Síntoma

Al refrescar o previsualizar una query en Power Query Editor, aparece alguno de estos
mensajes:

> DataSource.Error: Unable to connect. Details: "We encountered an error while trying
> to connect."

> DataSource.Error: The data source path could not be found.

> DataSource.Error: Could not find file 'C:\Datos\archivo.xlsx'.

> DataSource.Error: An error occurred in the 'X' query. Expression.Error: The key
> didn't match any rows in the table.

En el Service, el refresh programado falla con:

> Data source error: The data source path could not be found. Please check the path
> and try again.

La tabla afectada queda vacía o con datos desactualizados.

## Causa

Power Query no puede alcanzar el origen de datos configurado. Las causas más comunes:

- **Archivo movido o renombrado**: la query apunta a una ruta local
  (`C:\Users\juan\Desktop\datos.xlsx`) y el archivo fue movido, renombrado o eliminado.
- **Ruta de red inaccesible**: la carpeta compartida (`\\servidor\share\`) está caída,
  fue reconfigurada, o el usuario actual no tiene permisos.
- **Credenciales inválidas o expiradas**: la contraseña del data source cambió. Esto
  es especialmente frecuente con tokens OAuth (SharePoint, Dynamics, Salesforce).
- **Servidor de base de datos inalcanzable**: el SQL Server o la base de datos cambió
  de nombre, IP, puerto, o el firewall bloquea la conexión.
- **Cambio de entorno**: el .pbix fue desarrollado en un entorno (dev) con una ruta
  o servidor y publicado en otro (prod) sin actualizar los parámetros.
- **Gateway no configurado**: el dataset en el Service necesita un Gateway para acceder
  a fuentes on-premises y no tiene uno asignado.

## Solución paso a paso

### Escenario 1 — Archivo local no encontrado

1. Verificar que el archivo exista en la ruta esperada.
2. Si fue movido, actualizar la ruta en Power Query:
   - `Home > Data Source Settings > Change Source...`
   - Actualizar el path al archivo.
3. **Recomendación**: parametrizar la ruta usando un parámetro de Power Query:
   ```m
   let
       RutaBase = #"Param_Ruta",
       Source = Excel.Workbook(File.Contents(RutaBase & "\datos.xlsx"))
   in
       Source
   ```

### Escenario 2 — Ruta de red / carpeta compartida

1. Desde el equipo donde corre el refresh (tu PC para Desktop, el servidor del
   Gateway para el Service), abrir Explorer y navegar a la ruta manualmente.
2. Si no se puede acceder:
   - Verificar que el share existe (`\\servidor\share`).
   - Verificar permisos NTFS y de share para la cuenta que ejecuta el refresh.
   - Verificar conectividad de red (`ping servidor`).
3. Si la ruta cambió, actualizar en `Data Source Settings`.

### Escenario 3 — Base de datos / servidor

1. Verificar conectividad al servidor:
   ```powershell
   Test-NetConnection -ComputerName miservidor.dominio.com -Port 1433
   ```
2. Verificar que la base de datos existe y la cuenta tiene acceso (probar con
   SSMS o Azure Data Studio).
3. Actualizar credenciales en `Data Source Settings > Edit Permissions`.

### Escenario 4 — En el Service (refresh programado)

1. Ir al dataset en el workspace: `Settings > Data source credentials`.
2. Para cada fuente listada, verificar que:
   - Las credenciales estén configuradas y vigentes.
   - El privacy level esté seteado (Organizational típicamente).
3. Si la fuente es on-premises, verificar que el Gateway esté asignado y online:
   - `Settings > Gateway and cloud connections > Maps to: [seleccionar gateway]`.
4. Probar un refresh manual para confirmar.

### Escenario 5 — Parametrizar para múltiples entornos

1. Crear parámetros en Power Query:
   - `Home > Manage Parameters > New Parameter`
   - Ejemplo: `Param_Servidor` = "sql-dev.empresa.com"
2. Referenciar en las queries:
   ```m
   Source = Sql.Database(Param_Servidor, "MiBaseDatos")
   ```
3. Al mover entre entornos, solo cambiar el valor del parámetro.

## Cómo prevenirlo

- **Nunca usar rutas absolutas locales** (`C:\Users\...`). Usar rutas de red UNC
  (`\\server\share\`) o parametrizar.
- **Usar parámetros de Power Query** para servidores, rutas y bases de datos. Facilita
  el cambio entre entornos dev/test/prod.
- **Documentar qué cuenta/credencial autentica cada fuente** y tener un proceso
  de rotación que incluya actualizar Power BI.
- **Configurar el Gateway correctamente** antes de publicar datasets que usen fuentes
  on-premises.
- **Probar el refresh en el Service** inmediatamente después de publicar, no esperar
  al schedule.

## Fuentes

- [Microsoft Docs - Data source settings in Power Query](https://learn.microsoft.com/en-us/power-query/data-source-settings)
- [Microsoft Docs - Configure scheduled refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh)
- [Microsoft Docs - Using parameters in Power Query](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters)
