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
│   └── conexion/
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

1. Elegir categoría: `dax`, `modelo`, `powerquery`, `refresh`, `conexion`. Si
   no encaja, crear nueva carpeta bajo `errors/`.

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
