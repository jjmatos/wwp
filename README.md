# Hermes Chatbot Studio

Web dinámica con **chatbot flotante** (vidrio oscuro + animaciones) que genera
contenido y lo aplica como **parches** a cada `index.html` del sitio.

## 1) Crear el Bot en Hermes (el "cerebro" IA)
El bot de Hermes es un **perfil**. Dos formas:

**A) Desde la app de escritorio (Bot Mode, activado por defecto):**
- Abre la pestaña **Bots** (barra lateral, junto a Sessions) → **New Agent**.
- Nombre: `site-studio`, Título: `Hermes Site Studio`, y pega el contenido de
  `bot/SOUL.md` en el campo **Custom SOUL.md** (Advanced).
- Opcional: fija modelo/provider y habilita solo las skills de edición de archivos.

**B) Desde la terminal (CLI):**
```bash
hermes profile create site-studio --clone-from default
# edita ~/.hermes/profiles/site-studio/SOUL.md  (pega bot/SOUL.md)
hermes -p site-studio chat   # habla con tu bot
```

Para que el chatbot de la web use Hermes de verdad, levanta el proxy OpenAI-compatible:
```bash
hermes proxy                 # http://localhost:8000/v1/chat/completions
```
y arranca el estudio con:
```bash
HERMES_PROXY_URL=http://localhost:8000/v1/chat/completions HERMES_PROXY_KEY=hermes python3 studio.py
```
(Si no pones el proxy, usa un generador local de respaldo y todo sigue funcionando.)

## 2) Ejecutar el estudio
```bash
cd hermes-chatbot-studio
python3 studio.py
# abre http://localhost:8080
```
Abre el chat flotante (abajo a la derecha), pide p.ej. *"Añade una sección de
testimonios"* y pulsa **Aplicar parche**. Recarga y verás el contenido insertado
en el `index.html` correspondiente, justo tras el marcador `<!-- HERMES-PATCH -->`.

## 3) Cómo funciona el parcheo
- Cada página tiene un marcador `<!-- HERMES-PATCH -->`.
- `POST /api/generate` produce el HTML (via Hermes proxy o generador local).
- `POST /api/patch` inserta ese HTML tras el marcador del `index.html` indicado.
- El Bot de Hermes (SOUL.md) puede hacer lo mismo con sus propias herramientas
  de archivos cuando lo invoques desde la terminal.

## 4) Personalizar el tema
Edita las variables en `assets/widget.css` (`--hms-accent`, `--hms-accent-2`,
`--hms-glass`) y en cada `index.html` (`--a`, `--a2`, `--bg`).

## 5) Modo Desarrollador (multi-elemento)
Click en el icono **layers** del header del chat para abrir el panel lateral derecho.
- Lista **todos los elementos editables** de la pagina actual con un **numero**.
- Muestra **badges numerados** sobre cada elemento en la pagina.
- Marca con checkbox los que quieras modificar y elige una **accion** (Corregir / Cambiar / Añadir / Eliminar).
- Pulsa **"✨ Generar IA"** para pedir sugerencias contextuales, o escribe el contenido manualmente.
- Pulsa **"Aplicar a N elementos"** para ejecutar la accion en lote.
- Atajo de teclado: `Cmd/Ctrl+K` abre/cierra el panel.

Tambien puedes escribir comandos naturales en el chat:
```
cambia el elemento 3
borra los elementos 5, 7 y 9
edita los items 1, 2 y 4
añade el elemento 10
```
El chat detectara el patron y abrira el panel con los elementos preseleccionados.

### Endpoints
- `POST /api/elements`            - lista los elementos editables de una pagina
- `POST /api/elements_apply`      - aplica un lote de acciones en transaccion atomica (backup unico)
- `POST /api/elements_ai`         - genera sugerencias IA para N elementos en una sola llamada

## 6) Buscador e insercion de imagenes
Click en el icono **imagen** (6° boton del header del chat) para abrir el panel de imagenes.
Tambien aparece automaticamente cuando escribes en el chat palabras como "imagen", "foto", "añade una foto de...".

### 3 vias de obtencion
- **Buscar**: Unsplash, Pexels, Pixabay (API keys opcionales; sin ellas se sugiere configurarlas).
- **Generar**: DALL-E 3 (OpenAI), Stable Diffusion (Stability AI) o placeholder SVG automatico si no hay key.
- **Subir**: archivo local (drag & drop o click), max 5 MB, se guarda en `/uploads/`.

### Como funciona
1. Abre el panel (boton imagen o desde el chat).
2. Elige un **tab**: Buscar / Generar / Subir.
3. Escribe un termino o sube un archivo.
4. Selecciona la imagen de la galeria.
5. Pulsa **Insertar** -> la imagen se aniade como `<figure>` al final de la pagina (o reemplaza un `<img>` existente si seleccionaste uno).

### Endpoints de imagenes
- `POST /api/image_search`   - busca en bancos de imagenes (Unsplash/Pexels/Pixabay)
- `POST /api/image_generate` - genera con DALL-E 3, Stable Diffusion o SVG placeholder automatico
- `POST /api/image_upload`   - sube archivo local a `/uploads/`
- `POST /api/image_insert`   - inserta o reemplaza una imagen en la pagina
- `GET  /uploads/<file>`    - sirve archivos subidos
- `GET  /api/image_placeholder` - genera SVG placeholder (siempre funciona, sin API)

## Estructura
```
hermes-chatbot-studio/
├── studio.py            # servidor + API generate/patch
├── index.html           # home (data-page="home")
├── about/index.html     # data-page="about"
├── services/index.html  # data-page="services"
├── assets/widget.css    # tema vidrio oscuro + animaciones
├── assets/widget.js     # chatbot flotante
├── bot/SOUL.md          # persona del Bot de Hermes
└── README.md
```
