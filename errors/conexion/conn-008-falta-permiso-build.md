---
id: conn-008
title: Usuario ve datos de otro tablero al que no tiene acceso (falta permiso Build)
category: conexion
severity: media
tools: [Service]
tags: [permissions, build, shared-dataset, semantic-model, access]
search_hints:
  - "no tenes acceso al modelo subyacente"
  - "you don't have access to the underlying model"
  - "error al captar datos sin permisos"
  - "falta permiso de compilar"
  - "error al capturar datos"
  - "no tiene permisos para ver la informacion de ese modelo"
  - "build permission required"
related: [conn-005]
media:
  images: [conn-008-fig1.png]
  videos: []
---

## Síntoma

Un usuario abre un reporte y ve un mensaje de error al cargar datos, o ve
campos vacíos en visuales que para otros usuarios cargan bien. Mensajes
típicos:

> No tenés acceso al modelo subyacente
>
> O bien: error genérico de "no se pudo cargar los datos" pese a que el
> reporte se abre.

El usuario sí tiene acceso al **reporte**, pero no al **modelo semántico** que
está alimentándolo.

## Causa

El reporte está conectado en vivo (live connection) a un modelo semántico que
vive en otro workspace o que es compartido entre varios reportes. Compartir
el reporte no comparte automáticamente el modelo.

Para que un usuario consuma datos de un modelo compartido desde un reporte
externo, necesita el permiso **Build** (Compilar) sobre el modelo semántico.

Es prácticamente el mismo problema que `conn-005`, pero visto desde el reporte
en vez de desde el mensaje de Analysis Services.

## Solución paso a paso

1. **Identificar el modelo semántico fuente:**
   - Service → abrir el reporte → menú `...` → `View related content` →
     muestra el dataset asociado y su workspace.

2. **Comparar accesos del usuario:**
   - ¿Tiene acceso al **reporte**? Probablemente sí, por eso lo abre.
   - ¿Tiene acceso al **modelo semántico**? Es lo que falta.

3. **Otorgar permiso Build:**
   - Workspace del modelo → modelo semántico → menú `...` →
     `Manage permissions` → agregar al usuario con permiso `Build`.
   - Como alternativa, agregarlo como miembro del workspace con rol
     `Contributor` o superior — incluye `Build` automáticamente.

4. **Si el modelo tiene RLS**, asignar también el usuario al rol
   correspondiente en `Security` → `Add` → seleccionar rol.

5. **Validar:** que el usuario refresque el reporte. Puede tardar unos
   minutos en propagar el permiso.

## Cómo prevenirlo

- Usar **grupos de Azure AD** para distribuir permisos `Build`, no
  asignaciones individuales — el grupo escala con altas/bajas.
- Documentar qué reportes consumen qué modelos, así cuando hay un alta nueva
  se sabe qué permisos pedir de una vez (reporte + dataset + roles RLS).
- Para datos sensibles, preferir **RLS bien configurada** antes que limitar
  el acceso al modelo entero — el modelo se comparte, los datos se filtran.

## Fuentes

- [Build permission for shared semantic models](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-build-permissions)
- [Row-level security (RLS) overview](https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-rls)
