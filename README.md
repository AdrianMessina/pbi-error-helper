# PBI Error Helper

App interna tipo wiki para resolver errores comunes de Power BI. La base de
conocimiento crece agregando archivos markdown — no requiere base de datos,
APIs externas ni reentrenar nada.

## Stack

- **UI:** Streamlit
- **Knowledge base:** archivos `.md` con frontmatter YAML
- **Búsqueda:** Whoosh (full-text, pure-python)
- **Multimedia:** imágenes y videos referenciados desde los markdowns
- **Deploy:** Cloudera CDSW / CML (también corre local)

Sin LLMs, sin APIs externas, sin vector DB. Todo file-based y versionable
con git.

## Estructura

```
pbi_error_helper/
├── app.py                  # Streamlit entry point
├── kb.py                   # Loader + search engine
├── requirements.txt
├── README.md
├── setup_proxy.bat         # Helper para el proxy YPF
├── errors/                 # Knowledge base
│   ├── dax/
│   ├── modelo/
│   ├── powerquery/
│   ├── refresh/
│   ├── conexion/
│   ├── copilot/
│   └── version/            # Errores de versión y compatibilidad
└── media/
    ├── images/
    └── videos/
```

## Setup local

1. Configurar proxy (Windows + bash):
   ```bash
   export HTTPS_PROXY=http://proxy-azure
   export HTTP_PROXY=http://proxy-azure
   ```
   O ejecutar `setup_proxy.bat` en CMD.

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Correr la app:
   ```bash
   streamlit run app.py
   ```

4. Abrir `http://localhost:8501`.

## Agregar un nuevo error

1. Elegir categoría: `dax`, `modelo`, `powerquery`, `refresh`, `conexion`, 
   `copilot`, `version`. Si no encaja, crear nueva carpeta bajo `errors/`.

2. Crear archivo con nombre `<categoria>-<NNN>-<slug>.md`. Ejemplo:
   `dax-002-blank-vs-zero.md`.

3. Usar este template:

   ```markdown
   ---
   id: dax-002
   title: BLANK vs 0 en medidas
   category: dax
   severity: media           # baja | media | alta
   tools: [Desktop, Service]
   tags: [measure, BLANK, aggregation]
   related: [dax-001]
   media:
     images: [dax-002-fig1.png]
     videos: []
   ---

   ## Síntoma
   Qué ve el usuario.

   ## Causa
   Por qué pasa.

   ## Solución paso a paso
   1. ...
   2. ...

   ## Cómo prevenirlo
   Buenas prácticas.

   ## Fuentes
   Links a docs oficiales o referencias.
   ```

4. Las imágenes van en `media/images/`. Los videos en `media/videos/`. Solo
   referenciar el nombre del archivo (no el path completo) en el frontmatter.

5. Refrescar la app. El KB se recarga al startup — si está corriendo, hacer
   Rerun desde el menú de Streamlit (`R`).

## Convenciones

- **IDs únicos.** Formato `<categoria>-<NNN>`. No reusar.
- **Severidad:**
  - `alta`: rompe el modelo o impide entregar el reporte.
  - `media`: hay workaround pero degrada la experiencia.
  - `baja`: warning o cosmético.
- **Tools:** `Desktop`, `Service`, `Gateway`, `Mobile`. Mayúscula inicial.
- **Tags:** lowercase, kebab-case. Ej: `circular-dependency`, `power-query`.
- **Related:** lista de IDs (`[dax-001, modelo-002]`).
- **Idioma:** los cuerpos en español, los IDs/tags en inglés.

## Importar errores desde Microsoft Teams

La app no se conecta directo a Teams. El flujo recomendado es exportar o copiar
los mensajes del grupo a un archivo y subirlo desde la sección **Importar
Teams** de la barra lateral.

Formatos soportados:

- JSON: export de Microsoft Graph/eDiscovery o estructura con `value`,
  `messages`, `replies`, `body.content`, `createdDateTime`, etc.
- CSV: columnas como `content`, `body`, `message`, `text`, `createdDateTime`,
  `author`, `threadId`, `replyToId`, `webUrl`.
- TXT/HTML: copiado manual desde Teams. El importador usa bloques separados por
  líneas en blanco.

Desde la app se puede:

- Ver mensajes extraídos.
- Navegar hilos completos.
- Revisar candidatos para artículos de la KB.
- Filtrar por relevancia, solución detectada y texto libre.
- Descargar CSV, JSON o ZIP con Markdown borrador.

### Uso técnico opcional

Preview sin crear archivos:

```bash
python import_teams_issues.py --source teams_exports/pbi-teams.json --verbose
```

Crear artículos en `errors/<categoria>/`:

```bash
python import_teams_issues.py --source teams_exports/pbi-teams.json --write
```

Opciones útiles:

```bash
# Solo hilos donde se detectó una posible solución
python import_teams_issues.py --source teams_exports/pbi-teams.json --solved-only

# Si el export ya está muy filtrado y el preview trae pocos casos
python import_teams_issues.py --source teams_exports/pbi-teams.json --min-score 5

# Procesar una carpeta completa con varios exports
python import_teams_issues.py --source teams_exports --write
```

El importador:

- Filtra hilos con señales de Power BI + error/bug/solución.
- Clasifica en `dax`, `modelo`, `powerquery`, `refresh`, `conexion` o `copilot`.
- Asigna severidad, herramientas y tags.
- Genera IDs consecutivos según la categoría (`dax-006`, `pq-005`, etc.).
- Marca cada entrada como `review_status: draft` y agrega `needs-review`.

Revisar siempre los Markdown generados antes de considerarlos definitivos,
porque la extracción desde conversaciones puede mezclar síntoma, causa y
solución si el hilo tiene mucho ruido.

## Deploy en Cloudera

### CDSW / CML

1. Crear un Project nuevo apuntando a este repo (o subir los archivos).
2. Confirmar que `requirements.txt` está en la raíz del proyecto.
3. Crear una **Application**:
   - Script: `app.py`
   - Run command:
     ```
     streamlit run app.py --server.port=$CDSW_APP_PORT --server.address=127.0.0.1
     ```
   - Engine kernel: Python 3.10+
4. Start Application. La URL queda expuesta dentro del workspace.

### Notas

- Si el cluster tiene su propio proxy/firewall, ajustar variables de entorno
  en el Engine Profile antes del install.
- Para persistir contenido nuevo (errores agregados desde la app misma, si en
  el futuro habilitamos esa función), montar un volumen o conectar a git.

## Roadmap (no implementado)

- [ ] Form en la app para reportar/proponer errores nuevos
- [ ] Estadísticas de búsquedas más frecuentes
- [ ] Export a PDF de un error específico
- [ ] Si IT habilita Azure OpenAI: capa generativa para parafrasear y dar
      respuestas contextuales sin perder las citas a la KB
