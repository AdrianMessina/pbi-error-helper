---
id: conn-002
title: Error de conexión a SQL Server - Network-related or instance-specific error
category: conexion
severity: alta
tools: [Desktop, Service, Gateway]
tags: [SQL-Server, network, firewall, port-1433, instance]
related: [conn-001]
media:
  images: []
  videos: []
---

## Síntoma

Al intentar conectar a SQL Server desde Power BI Desktop, el Gateway o al configurar
una fuente de datos, aparece:

> Microsoft SQL: A network-related or instance-specific error occurred while
> establishing a connection to SQL Server. The server was not found or was not
> accessible. Verify that the instance name is correct and that SQL Server is
> configured to allow remote connections. (provider: Named Pipes Provider, error: 40
> - Could not open a connection to SQL Server)

> Microsoft SQL: A network-related or instance-specific error occurred while
> establishing a connection to SQL Server. (provider: TCP Provider, error: 0 - No
> such host is known.)

> Login failed for user 'DOMAIN\user'. (Microsoft SQL Server, Error: 18456)

> Cannot open database "MiBase" requested by the login. The login failed.

En el Service, el refresh falla con un mensaje similar y el dataset queda sin
actualizar.

## Causa

Power BI no puede establecer una conexión TCP/IP con la instancia de SQL Server.
Las causas más frecuentes:

- **Nombre del servidor incorrecto**: typo en el server name, falta el nombre de
  la instancia (`servidor\instancia`), o se usa un alias DNS que no resuelve.
- **SQL Server no escucha en TCP/IP**: por defecto, algunas instalaciones de SQL
  Server (especialmente Express) solo habilitan Shared Memory y Named Pipes, no
  TCP/IP.
- **Puerto bloqueado por firewall**: el puerto 1433 (default) o el puerto dinámico
  de una named instance está bloqueado por el firewall del servidor, del cliente o
  de la red.
- **SQL Server Browser no está corriendo**: para named instances con puertos
  dinámicos, el servicio SQL Server Browser (UDP 1434) es necesario para resolver
  el puerto.
- **Credenciales inválidas**: usuario/contraseña incorrectos, cuenta bloqueada,
  o el usuario no tiene permiso sobre la base de datos.
- **Base de datos offline o inexistente**: la base fue eliminada, renombrada o
  está en estado offline/restoring.
- **Gateway no configurado o caído**: en el Service, si la fuente es on-premises
  y el Gateway no está online o no tiene la fuente configurada.

## Solución paso a paso

### Paso 1 — Verificar el nombre del servidor

1. Confirmar el nombre exacto del servidor:
   - Default instance: `miservidor.dominio.com` o `miservidor`
   - Named instance: `miservidor\SQLEXPRESS` o `miservidor\MI_INSTANCIA`
   - Con puerto custom: `miservidor,1450` (coma, no dos puntos)
2. Verificar resolución DNS desde el equipo que se conecta:
   ```powershell
   nslookup miservidor.dominio.com
   ```
3. Si usa un alias SQL, verificar que esté configurado en `SQL Server Configuration
   Manager > SQL Native Client > Aliases`.

### Paso 2 — Verificar conectividad de red

1. Hacer ping al servidor:
   ```powershell
   ping miservidor.dominio.com
   ```
2. Probar conexión TCP al puerto de SQL:
   ```powershell
   Test-NetConnection -ComputerName miservidor.dominio.com -Port 1433
   ```
3. Si falla, el firewall está bloqueando. Abrir el puerto en:
   - **Windows Firewall del servidor SQL**:
     ```powershell
     New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
     ```
   - **Firewall de red/corporativo**: solicitar al equipo de networking la apertura
     del puerto entre la IP del cliente/Gateway y la IP del servidor SQL.

### Paso 3 — Verificar configuración de SQL Server

1. Abrir **SQL Server Configuration Manager** en el servidor.
2. `SQL Server Network Configuration > Protocols for [INSTANCIA]`:
   - Verificar que **TCP/IP** esté **Enabled**.
   - Doble click en TCP/IP → pestaña `IP Addresses` → verificar que `TCP Port`
     sea 1433 (o el puerto configurado) y `Enabled = Yes`.
3. Si la instancia es named (ej. SQLEXPRESS):
   - Verificar que el servicio **SQL Server Browser** esté **Running**
     (`services.msc` → `SQL Server Browser`).
   - Abrir el puerto UDP 1434 en el firewall para el Browser.
4. Reiniciar el servicio de SQL Server si se hicieron cambios en la configuración
   de red.

### Paso 4 — Verificar autenticación

1. Probar la conexión con SSMS (SQL Server Management Studio) o Azure Data Studio
   usando las mismas credenciales.
2. Si falla con error 18456:
   - **Login incorrecto**: verificar usuario y contraseña.
   - **Authentication mode**: si se usa SQL Authentication, verificar que SQL Server
     esté configurado en **Mixed Mode** (`Server Properties > Security > SQL Server
     and Windows Authentication mode`).
   - **Cuenta bloqueada**: verificar en `Security > Logins > [usuario] > Status`
     que no esté `Denied` o `Disabled`.
   - **Permiso sobre la base**: verificar que el login tenga un **user mapping** a
     la base de datos objetivo (`Login Properties > User Mapping`).

### Paso 5 — Configurar en el Service con Gateway

1. Verificar que el Gateway esté **online** (ver conn-001).
2. En el Gateway, agregar la fuente de datos:
   - `Manage gateways > [gateway] > Add data source`
   - Tipo: SQL Server
   - Server: el nombre exacto (como se conecta desde el servidor del Gateway, no
     desde tu PC).
   - Database: nombre de la base.
   - Credenciales: las que tiene permiso de lectura.
3. **Importante**: el nombre del servidor en el dataset debe coincidir exactamente
   con el nombre configurado en el data source del Gateway. Si en Desktop pusiste
   `miservidor` y en el Gateway `miservidor.dominio.com`, no se mapea.
4. En el dataset del Service: `Settings > Gateway and cloud connections` → mapear
   cada fuente al data source correspondiente del Gateway.

### Paso 6 — Probar la conexión

1. Desde Power BI Desktop: `Get Data > SQL Server` → ingresar el server name
   y database → `OK`.
2. Si funciona localmente pero falla en el Service, el problema está en el Gateway
   o en la red entre el Gateway y el SQL Server.

## Cómo prevenirlo

- **Documentar las cadenas de conexión exactas** (server name, instance, puerto)
  para cada entorno.
- **Usar un puerto estático** para named instances en lugar de puertos dinámicos.
  Esto simplifica la configuración del firewall.
- **Crear cuentas de servicio dedicadas** para Power BI con permisos de solo
  lectura (db_datareader) sobre las bases necesarias.
- **Monitorear el estado del SQL Server** con alertas automáticas.
- **Probar la conexión desde el servidor del Gateway**, no solo desde tu PC de
  desarrollo. La red puede ser diferente.
- **Parametrizar el server name** en Power Query para facilitar el cambio entre
  entornos (dev/test/prod).

## Fuentes

- [Microsoft Docs - SQL Server connection troubleshooting](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/troubleshoot-connecting-to-the-sql-server-database-engine)
- [Microsoft Docs - Configure the Windows Firewall for SQL Server](https://learn.microsoft.com/en-us/sql/sql-server/install/configure-the-windows-firewall-to-allow-sql-server-access)
- [Microsoft Docs - Manage your data source - SQL Server](https://learn.microsoft.com/en-us/power-bi/connect-data/service-gateway-enterprise-manage-sql)
