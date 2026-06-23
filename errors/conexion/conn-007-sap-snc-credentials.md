---
id: conn-007
title: SAP BW SNCERR_UNKNOWN_MECH (credenciales SNC)
category: conexion
severity: alta
tools: [Desktop, Gateway]
tags: [sap, sap-bw, snc, credentials, wp6, cau, ypf]
search_hints:
  - "SNCERR_UNKNOWN_MECH"
  - "SncPImportPrName() parsing error"
  - "SAP Business Warehouse DataSource.Error"
  - "error dll sap sapcrypto"
  - "error de conexion SAP BW SNC"
  - "error sap power bi"
  - "Secure Network Communication SNC error"
  - "RETURN CODE 20"
related: []
media:
  images: [conn-007-fig1.png, conn-007-fig2.png]
  videos: []
---

## Síntoma

Al conectar Power BI a SAP Business Warehouse usando la cuenta WP6 con SNC,
aparece el error:

> DataSource.Error: SAP Business Warehouse:
> LOCATION    CPIC (TCP/IP) on local host V11AZR... with Unicode
> ERROR       SNCERR_UNKNOWN_MECH
>             SncPImportPrName() parsing error
>             name="p/secude:CN=WP6, O=YPF S.A., C=AR"
> COMPONENT   SNC (Secure Network Communication)
> RETURN CODE: 20
> ErrorCode=5

La conexión nunca se establece. Sin SNC, falla la autenticación contra el
sistema SAP.

## Causa

El cliente SAP local no tiene configurada la **librería criptográfica SNC**
correcta o la cuenta WP6 no tiene alta en el sistema destino.

Causas frecuentes:

- Falta la DLL `sapcrypto.dll` apuntada en la variable SNC del entorno.
- La cuenta WP6 del usuario **no tiene alta** en el servidor SAP destino —
  esto lo gestiona el CAU (no el equipo de BI).
- El string SNC del cliente no incluye la cuenta WP6 — también lo configura
  el CAU.
- La versión del SAP SecureLogin Client está desactualizada.

## Solución paso a paso

1. **Verificar que la DLL existe** en el cliente:
   - Ruta esperada: `C:\Program Files\SAP\FrontEnd\SecureLogin\lib\sapcrypto.dll`
   - Si no está, instalar/reinstalar SAP Secure Login Client desde el portal
     interno.

2. **Configurar la DLL en Power BI Desktop:**
   - `File > Options > Global > Security` → sección **SAP BW**.
   - SNC Library = `Custom` → pegar la ruta:
     `C:\Program Files\SAP\FrontEnd\SecureLogin\lib\sapcrypto.dll`

3. **Pedir al CAU las dos altas que faltan:**
   - **Alta de la cuenta WP6** en el sistema SAP destino (ej. WP601).
   - **Agregar la cuenta WP6 al string SNC** del sistema. Esto solo lo puede
     hacer el CAU, no el equipo de BI.
   - Contactos históricos: GRISMADO, GERMAN o URSINO NICOLAS pueden orientar.

4. **Probar la conexión:**
   - Power BI Desktop → `Get Data > SAP Business Warehouse Application Server`.
   - Server: `slpawsuswp601`, System number `00`, Client `300`.
   - Authentication: `Use SAP Single Sign-On (SSO)` con SNC habilitado.

5. **Si sigue fallando**, validar con el CAU que el string SNC del servidor
   incluya exactamente el partner name `p/secude:CN=WP6, O=YPF S.A., C=AR`.

## Cómo prevenirlo

- Documentar para cada server SAP qué cuentas WP6 están dadas de alta y
  pedirlo proactivamente al onboarding de nuevos integrantes.
- Mantener la DLL `sapcrypto.dll` configurada por GPO en el equipo corporativo
  para no depender de configuración manual por usuario.
- Si vas a cambiar de servidor SAP destino (DEV → PROD), abrir el ticket al
  CAU con anticipación — el alta y la actualización del string SNC tienen
  tiempo de gestión.

## Fuentes

- [Power BI - Connect to SAP BW](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-sap-bw-connector)
- [SAP Note - SNC error troubleshooting](https://help.sap.com/docs/saplogon-for-windows)
