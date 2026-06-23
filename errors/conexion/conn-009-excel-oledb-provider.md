---
id: conn-009
title: DataSource.NotFound - Microsoft.ACE.OLEDB provider not registered
category: conexion
severity: alta
tools: [Desktop, Service, Gateway]
tags: [excel, oledb, access-database-engine, datatype, office, 64-bit]
search_hints:
  - "DataSource.NotFound Excel Workbook Microsoft.ACE.OLEDB"
  - "Microsoft.ACE.OLEDB.12.0 provider is not registered"
  - "Access Database Engine OLEDB provider may be required"
  - "64-bit version of the Access Database Engine"
  - "error del origen de datos excel"
  - "proveedor OLEDB no registrado"
  - "hace falta volver todos los archivos a xlsx"
  - "Microsoft.Data.Mashup.ErrorCode = 10478"
related: [conn-003]
media:
  images: []
  videos: []
---

## Síntoma

Al intentar refrescar un modelo que consume archivos Excel, aparece:

> Error del origen de datos: DataSource.NotFound: Excel Workbook: The
> 'Microsoft.ACE.OLEDB.12.0' provider is not registered on the local machine.
> The 64-bit version of the Access Database Engine OLEDB provider may be
> required to read this type of file. To download the client software, visit
> the following site: https://go.microsoft.com/fwlink/?LinkID=285987
>
> Microsoft.Data.Mashup.ErrorCode = 10478. The exception was raised by the
> IDbCommand interface.

El modelo no refresca ni en Desktop ni en el Gateway. Los archivos Excel no se
pueden leer.

## Causa

Power BI Desktop o el Gateway intentan conectarse a un archivo Excel (`.xls`,
`.xlsb` o `.xlsx` antiguo) usando el proveedor **Microsoft Access Database
Engine (ACE) OLEDB**, pero ese driver no está instalado en la máquina.

Causas frecuentes:

- El archivo Excel es formato **`.xls`** (Office 2003) en lugar de `.xlsx`
  (Office 2007+) y requiere el driver ACE OLEDB para leerlo.
- El Gateway o Desktop instalado es de **64 bits**, pero el driver ACE OLEDB
  instalado es de **32 bits** (o viceversa).
- Nunca se instaló el **Microsoft Access Database Engine** en la máquina del
  Gateway.
- Se instaló Office 32-bit en una máquina con Power BI 64-bit — hay conflicto
  de arquitecturas.

## Solución paso a paso

### **Opción A — Convertir los archivos a formato moderno (recomendado)**

Si tenés control sobre las fuentes Excel:

1. Abrir cada archivo `.xls` o `.xlsb` con Excel
2. **Guardar como** → formato **`.xlsx`** (Excel Workbook)
3. Actualizar la conexión en Power Query para apuntar al nuevo archivo
4. Refrescar el modelo → ya no debería pedir OLEDB

**Ventaja:** no depende de drivers externos, funciona en cualquier ambiente.

### **Opción B — Instalar el driver ACE OLEDB correcto**

Si NO podés cambiar el formato del archivo:

1. **Identificar la arquitectura de Power BI / Gateway:**
   - Desktop: `Help > About > Version info` → indica 64-bit o 32-bit
   - Gateway: típicamente es 64-bit

2. **Descargar el Access Database Engine** que coincida:
   - **64-bit:** https://go.microsoft.com/fwlink/?LinkID=285987
   - **32-bit:** https://www.microsoft.com/en-us/download/details.aspx?id=13255

3. **Instalar con el parámetro `/passive`** si ya tenés Office instalado (para
   evitar conflictos):
   ```cmd
   AccessDatabaseEngine_X64.exe /passive
Reiniciar Power BI Desktop o el Gateway service (si es en el Gateway)

Refrescar el modelo → ahora debería leer el archivo Excel

Opción C — Cambiar el conector en Power Query
Si el problema es solo en el Service/Gateway y funciona en Desktop:

En Power BI Desktop: Transform data → Data source settings
Cambiar el conector de "Excel Workbook" (OLEDB) a "Folder" → leer el archivo con Excel.Workbook() en M (no usa OLEDB)
Publicar al Service
Ejemplo M code:


let
    Source = Folder.Files("C:\Datos\"),
    Filter = Table.SelectRows(Source, each [Name] = "datos.xls"),
    Content = Filter{0}[Content],
    Import = Excel.Workbook(Content)
in
    Import
Cómo prevenirlo
Estandarizar el formato de archivos de origen a .xlsx — es el formato moderno, no requiere drivers OLEDB especiales, y es más rápido de leer.
Si usás Gateway, documentar qué drivers externos están instalados (ACE OLEDB, Oracle, Teradata) y validar que coincidan con la arquitectura del Gateway (64-bit).
Para modelos críticos en producción, evitar fuentes Excel cuando sea posible — SQL, SharePoint, OneDrive o Azure Blob son más estables y escalables.
Si agregás un Gateway nuevo al cluster, instalar el driver ACE OLEDB 64-bit de entrada para evitar este error al rotar.
Fuentes
Microsoft - Access Database Engine download
Power BI - Excel connector
Troubleshooting Power BI Gateway connectivity