---
id: conn-010
title: El acceso al recurso se prohíbe (Analysis Services)
category: conexion
severity: media
tools: [Desktop, Service]
tags: [analysis-services, forbidden, acceso, dataflow, modelo-semantico, temporal]
search_hints:
  - "El acceso al recurso se prohíbe"
  - "No se puede conectar Se encontró un error al intentar conectarse"
  - "access to the resource is forbidden"
  - "the resource is forbidden analysis services"
  - "no se puede conectar analysis services"
  - "error al conectar con analysis services"
  - "acceso prohibido al modelo semantico"
  - "el acceso al recurso se prohibe"
  - "cannot connect to analysis services forbidden"
related: [conn-005, conn-008]
media:
  images: [conn-010-fig1.png]
  videos: []
---

## Síntoma

Al intentar conectarse a un modelo semántico o dataflow mediante el conector
de Analysis Services en Power BI Desktop, aparece:

> **No se puede conectar**
>
> Se encontró un error al intentar conectarse.
> Detalles: "El acceso al recurso se prohíbe."

En inglés el mensaje equivalente es:

> Access to the resource is forbidden.

El usuario tenía acceso previamente y de repente deja de funcionar.

## Causa

El error indica que el recurso (modelo semántico, dataflow o dataset) al que
se intenta conectar vía Analysis Services **existe pero no está disponible
en ese momento**. Las causas más frecuentes:

- El **modelo o dataflow está siendo modificado** por otro usuario o proceso
  (editando medidas, relaciones, o estructura). Mientras se guarda, el
  servicio bloquea el acceso temporalmente.
- El modelo está en proceso de **refresh** y el servicio rechaza conexiones
  de lectura hasta que finalice.
- El workspace o la capacidad está en un estado transitorio (reinicio de
  capacidad, migración entre nodos).
- **Permisos revocados** — menos frecuente, pero si el admin quitó el
  permiso de Build o lectura del modelo, el error es el mismo.

En la mayoría de los casos observados en YPF este error es **temporal** y se
resuelve solo al cabo de unos minutos.

## Solución paso a paso

1. **Esperar unos minutos y reintentar.** En la ventana del error, hacer
   click en **Reintentar**. Si el modelo estaba en refresh o siendo editado,
   debería volver a estar disponible en 2-10 minutos.

2. **Verificar el estado del modelo upstream:**
   - Ir al workspace en el Service → modelo semántico → `Refresh history`.
   - Si hay un refresh en curso, esperar a que finalice.
   - Si el refresh falló, el modelo puede quedar en estado inconsistente →
     pedir al dueño del modelo que lo republique o refresque manualmente.

3. **Confirmar que el modelo no está siendo editado:**
   - Preguntar al equipo dueño del modelo si alguien está haciendo cambios
     en ese momento (publicando, editando online, etc.).

4. **Verificar permisos (si el error persiste):**
   - Service → modelo semántico → `Manage permissions`.
   - El usuario que conecta necesita al menos permiso de **Build** sobre
     el modelo.
   - Si no lo tiene, solicitar al dueño del workspace que lo otorgue.

5. **Verificar la URL de conexión de Analysis Services:**
   - En Desktop → `Get Data` → `Analysis Services` → confirmar que el
     server es `powerbi://api.powerbi.com/v1.0/myorg/<workspace>` y el
     database es el nombre exacto del modelo.
   - Un typo en el nombre del workspace o modelo puede dar un error similar.

6. **Si nada funciona**, verificar el estado del servicio en
   [status.powerbi.com](https://status.powerbi.com) por si hay una
   incidencia global.

## Cómo prevenirlo

- **No editar ni publicar un modelo mientras otros usuarios lo consumen
  activamente.** Coordinar ventanas de cambios.
- Configurar **notificaciones de refresh** para saber cuándo un modelo
  upstream está refrescando y evitar conectarse en ese momento.
- Para modelos críticos, considerar usar **deployment pipelines** que
  permiten editar en DEV sin afectar al modelo de PROD.

## Fuentes

- [Microsoft - Connect to datasets in the Power BI service from Desktop](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-report-lifecycle-datasets)
- [Microsoft - Manage dataset access permissions](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-manage-access-permissions)
