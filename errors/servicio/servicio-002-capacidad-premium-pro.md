---
id: servicio-002
title: Modelo en capacidad Pro consumiendo desde Fabric Premium
category: servicio
severity: alta
tools: [Service]
tags: [premium, fabric, pro, capacity, workspace, cross-workspace]
search_hints:
  - "dataset requires a Premium capacity"
  - "el modelo requiere capacidad premium"
  - "capacidad premium o pro"
  - "no está en un nodo de Fabric Premium"
  - "workspace con capacidad Pro"
  - "this dataset is not available because it requires a Premium capacity"
  - "consumiendo desde area pro fabric premium"
related: [servicio-001]
media:
  images: [servicio-002-fig1.png]
  videos: []
---

## Síntoma

Al intentar consumir un modelo semántico de un workspace en otro workspace,
falla la conexión o el reporte aparece con error. Mensajes típicos:

> This dataset is not available because it requires a Premium capacity.
>
> O bien: el reporte no abre en el workspace destino aunque el modelo origen
> esté publicado correctamente.

## Causa

Hay un **mismatch de capacidades** entre los dos workspaces involucrados:

- El workspace que **publica el modelo** está en **Fabric Premium**.
- El workspace que intenta **consumir el modelo** está en capacidad **Pro**.

Las conexiones cross-workspace a modelos compartidos requieren que **ambos
extremos estén en Premium/Fabric**, o que el consumidor tenga licencia PPU.
Un workspace Pro consumiendo desde un workspace Fabric corta la cadena.

Ejemplo real: workspace "DW Tableros Logística" (Pro) consume modelo desde
"VP DOWNSTREAM | TABLEROS" (Fabric).

## Solución paso a paso

1. **Identificar las capacidades de ambos workspaces:**
   - Service → Workspace → `Settings` → `Premium`.
   - Anotar: License mode (Pro / Premium per User / Premium per Capacity /
     Fabric).

2. **Elegir cuál de estas alternativas aplica:**

   **Opción A — Mover el workspace consumidor a Premium/Fabric:**
   - Solicitar al admin del tenant que asigne el workspace a la capacidad
     Fabric existente.
   - Validar costos: una capacidad Fabric tiene un SKU mensual fijo.

   **Opción B — Habilitar PPU para los usuarios del workspace Pro:**
   - Asignar licencia "Premium per User" a cada consumidor.
   - Más caro por usuario, pero evita mover el workspace.

   **Opción C — Replicar el modelo en el workspace consumidor:**
   - Importar el modelo (no live connection) y refrescar localmente.
   - Pierde la *single source of truth* — solo aceptable si los datos no son
     críticos o cambian poco.

   **Opción D — Mover el reporte al workspace que ya está en Fabric:**
   - Publicar el `.pbix` directamente en el workspace de origen.
   - Útil si el reporte es para un público pequeño que ya tiene acceso.

3. **Validar la solución elegida** con un usuario consumidor: abrir el
   reporte y refrescar.

## Cómo prevenirlo

- Mantener un **inventario de capacidades por workspace** para evitar
  publicaciones cross-workspace que crucen Pro ↔ Fabric.
- Definir una política de la organización: dónde viven los modelos centrales,
  con qué capacidad mínima, y quién tiene PPU.
- Antes de publicar un reporte que consume otro modelo, validar las
  capacidades de los workspaces involucrados.

## Fuentes

- [Power BI licensing requirements](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-what-is)
- [Cross-workspace shared datasets](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-across-workspaces)
- [Fabric capacity overview](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
