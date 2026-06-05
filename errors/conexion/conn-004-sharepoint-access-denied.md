---
id: conn-004
title: Access Denied / 401 Unauthorized al conectar a SharePoint Online
category: conexion
severity: media
tools: [Desktop, Service, Gateway]
tags: [SharePoint, OAuth, permissions, "401", forbidden]
related: [refresh-001]
media:
  images: []
  videos: []
---

## Síntoma

Al intentar conectar a una lista o archivo de SharePoint Online desde Power BI,
aparece alguno de estos mensajes:

> Access to the resource is forbidden.

> 401 Unauthorized

> OData: Request failed: The remote server returned an error: (403) Forbidden.

> DataSource.Error: OData: The given URL neither points to an OData service nor
> to a feed.

> Web.Contents failed to get contents from
> 'https://empresa.sharepoint.com/sites/misite/...' (403): Forbidden.

> We couldn't authenticate with the credentials provided. Please try again.

En Power BI Desktop, el popup de autenticación OAuth aparece y se completa, pero
la conexión sigue fallando. En el Service, el refresh programado falla con error
de credenciales o acceso denegado.

## Causa

Power BI no puede autenticarse o no tiene autorización para acceder al recurso de
SharePoint Online. Las causas principales:

- **URL incorrecta**: se usa la URL completa del archivo/lista en lugar de la URL
  raíz del sitio. Power BI requiere la URL del sitio base
  (`https://empresa.sharepoint.com/sites/misite`) y no la URL directa al archivo.
- **Permisos insuficientes en SharePoint**: el usuario no tiene al menos permisos
  de **lectura** sobre el sitio, la lista o la biblioteca de documentos.
- **Token OAuth expirado**: el token de autenticación en el Service expiró (los
  tokens OAuth de Microsoft 365 tienen vigencia limitada y no se renuevan
  automáticamente en todos los escenarios).
- **Conditional Access Policy (Azure AD)**: una política de acceso condicional
  bloquea el acceso desde la IP del Service o del Gateway (ej. política que solo
  permite acceso desde la red corporativa).
- **Modern Authentication deshabilitada**: el tenant tiene deshabilitada la
  autenticación moderna y Power BI no puede usar el flujo OAuth2.
- **Conector incorrecto**: se usa el conector `Web` en lugar de `SharePoint Online
  List` o `SharePoint Folder`, lo que omite el flujo de autenticación adecuado.
- **Tenant distinto**: la cuenta de Power BI pertenece a un tenant y el SharePoint
  a otro (escenarios B2B/guest) sin la configuración de cross-tenant adecuada.
- **App registration sin consentimiento**: en algunos entornos, el admin del tenant
  debe dar consentimiento a la app de Power BI para acceder a SharePoint vía API.

## Solución paso a paso

### Paso 1 — Verificar y corregir la URL

1. La URL para conectar desde Power BI debe ser la **URL raíz del sitio**, no la
   URL del archivo o lista:

   | Correcto | Incorrecto |
   |----------|-----------|
   | `https://empresa.sharepoint.com/sites/misite` | `https://empresa.sharepoint.com/sites/misite/Shared Documents/archivo.xlsx` |
   | `https://empresa.sharepoint.com/sites/misite` | `https://empresa.sharepoint.com/sites/misite/Lists/MiLista/AllItems.aspx` |

2. En Power BI Desktop:
   - `Get Data > SharePoint Online List` → pegar solo la URL del sitio.
   - `Get Data > SharePoint Folder` → pegar la URL del sitio.
3. No usar `Get Data > Web` para SharePoint. Siempre usar los conectores nativos
   de SharePoint.

### Paso 2 — Verificar permisos en SharePoint

1. Navegar al sitio de SharePoint en el browser con la misma cuenta que se usa
   en Power BI.
2. Verificar que se puede acceder al contenido (lista, biblioteca, archivo).
3. Si no tiene acceso, solicitar al propietario del sitio:
   - `Site Settings > Site Permissions > Grant Permissions`
   - Nivel mínimo requerido: **Read** (Leer).
4. Para listas específicas, verificar que no tengan permisos únicos que restrinjan
   el acceso:
   - `List Settings > Permissions for this list`

### Paso 3 — Reautenticar en Power BI Desktop

1. Ir a `File > Options and settings > Data source settings`.
2. Buscar la entrada de SharePoint (`https://empresa.sharepoint.com/...`).
3. Click en `Clear Permissions` para la fuente.
4. Volver a la query → se pedirá autenticarse nuevamente.
5. Seleccionar **"Microsoft Account"** (no "Anonymous" ni "Basic").
6. En la ventana de nivel de acceso, seleccionar la URL más general posible:
   - Preferir `https://empresa.sharepoint.com/` sobre
     `https://empresa.sharepoint.com/sites/misite`
   - Esto evita tener que reautenticar para cada sitio del mismo tenant.
7. Hacer click en `Sign in` → autenticarse con la cuenta que tiene acceso.

### Paso 4 — Reconfigurar credenciales en el Service

1. En powerbi.com → Workspace → Dataset → `Settings`.
2. Expandir `Data source credentials`.
3. Para la fuente de SharePoint, click en `Edit credentials`.
4. Seleccionar:
   - **Authentication method**: OAuth2
   - **Privacy level**: Organizational
5. Click en `Sign in` → autenticarse con una cuenta que tenga acceso al SharePoint.
6. **Importante**: usar una **cuenta de servicio** o una cuenta compartida del
   equipo, no una cuenta personal. Si la persona que autenticó se va de la empresa,
   el refresh se rompe.

### Paso 5 — Verificar políticas de acceso condicional

1. Si la autenticación funciona desde Desktop pero no desde el Service:
   - El Service de Power BI se conecta desde IPs de Microsoft Azure, que pueden
     estar bloqueadas por Conditional Access Policies.
2. Contactar al administrador de Azure AD / Entra ID para:
   - Verificar si hay policies que bloqueen acceso a SharePoint desde IPs externas.
   - Agregar excepciones para los rangos de IP del Power BI Service (service tag
     `PowerBI`).
   - O usar un **Gateway on-premises** como intermediario (el Gateway se conecta
     desde la red corporativa, que sí está permitida).

### Paso 6 — Escenario cross-tenant (B2B)

Si el SharePoint pertenece a un tenant diferente al de Power BI:

1. Verificar que la cuenta tiene acceso como **usuario invitado (guest)** en el
   tenant del SharePoint.
2. Al autenticarse en Power BI, usar la opción de autenticación que permita
   seleccionar el tenant correcto.
3. Si el admin del tenant destino requiere consentimiento para apps externas,
   solicitar al admin que apruebe la app de Power BI en su tenant.

## Cómo prevenirlo

- **Siempre usar la URL raíz del sitio** al configurar la conexión a SharePoint.
- **Usar los conectores nativos de SharePoint** (`SharePoint Online List`,
  `SharePoint Folder`), no el conector genérico `Web`.
- **Autenticar con cuentas de servicio** que no expiren y no estén atadas a un
  empleado individual. Configurar la cuenta como Service Account en Azure AD.
- **Documentar qué cuenta autentica cada dataset** que usa SharePoint. Cuando la
  cuenta rote, actualizar todas las conexiones.
- **Probar el refresh en el Service** inmediatamente después de publicar para
  detectar problemas de credenciales o acceso antes de que el schedule falle.
- **Coordinar con IT** si hay Conditional Access Policies activas, para asegurar
  que el Power BI Service y el Gateway estén habilitados.
- Para archivos Excel en SharePoint, considerar **moverlos a OneDrive for Business**
  o migrar a una base de datos si el volumen es significativo, ya que SharePoint
  no está optimizado como fuente de datos masiva.

## Fuentes

- [Microsoft Docs - Connect to SharePoint Online from Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-sharepoint-online-list)
- [Microsoft Docs - Troubleshoot refresh scenarios - SharePoint](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios)
- [Microsoft Docs - Azure AD Conditional Access for Power BI](https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-power-bi-conditional-access)
- [Microsoft Docs - Power BI data source prerequisites](https://learn.microsoft.com/en-us/power-bi/connect-data/power-bi-data-sources)
