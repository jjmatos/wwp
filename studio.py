import http.server, socketserver, os, json, urllib.request, urllib.error, urllib.parse, re, uuid, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8080))
MARKER = "<!-- HERMES-PATCH -->"
PAGES = {"home": "index.html", "about": "about/index.html", "services": "services/index.html"}

# === IMAGENES: configuracion ===
UPLOADS_DIR = os.path.join(ROOT, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
UPLOADS_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
UPLOADS_ALLOWED = {"image/jpeg":".jpg", "image/png":".png", "image/webp":".webp", "image/gif":".gif", "image/svg+xml":".svg"}

def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))

def local_generate(prompt, page):
    p = prompt.lower()
    is_table = any(w in p for w in ["tabla","table","cuadro","cuadricula","filas","columnas","datos","comparar","ranking"])
    is_cards = ("plan" in p or "precios" in p or "planes" in p)
    is_testimonials = any(w in p for w in ["testimonial","testimonio","opinion","review","reseña"])
    is_faq = any(w in p for w in ["faq","preguntas"])
    is_hero = any(w in p for w in ["hero","bienvenida","banner"])
    is_team = any(w in p for w in ["equipo","team","miembros","persona"])
    is_stat = any(w in p for w in ["numero","estadistica","kpi","metrica"])
    is_timeline = any(w in p for w in ["timeline","linea temporal","cronologia","historia"])
    is_cta = any(w in p for w in ["cta","llamada","boton"])
    lower_p = prompt.lower().strip()
    is_test_ok = "testea" in lower_p or "probar conexion" in lower_p or lower_p == "test"

    if is_test_ok:
        return "Conexion OK.", '<section class="hms-patch" style="text-align:center"><h2>Test OK</h2></section>\n', "generador-local"

    if is_table:
        nums = re.findall(r"(\d+)", p)
        rows = min(int(nums[0]) if nums else 5, 12)
        is_es = "espanol" in p
        is_pl = "polaco" in p
        pc = ["czerwony","zielony","niebieski","zolty","bialy","czarny","pomaranczowy","rozowy","fioletowy","szary"]
        sc = ["rojo","verde","azul","amarillo","blanco","negro","naranja","rosa","violeta","gris"]
        hc = ["#e74c3c","#2ecc71","#3498db","#f1c40f","#ecf0f1","#2c3e50","#e67e22","#e84393","#9b59b6","#95a5a6"]
        fr = ["manzana","pera","uva","naranja","platano","fresa","limon","sandia","melocoton","cereza"]
        plf = ["jablko","gruszka","winogrono","pomarancz","banan","truskawka","cytryna","arbuz","brzoskwinia","wisnia"]
        rh = ""
        for i in range(rows):
            bg = "rgba(255,255,255,0.03)" if i%2==0 else "rgba(255,255,255,0.06)"
            hcolor = hc[i%10]
            nm = (pc[i%10]+" / "+sc[i%10]).title() if (is_es and is_pl) else (sc[i%10].title() if is_es else (pc[i%10].title() if is_pl else (sc[i%10]+" / "+pc[i%10]).title()))
            rh += '<tr style="background:{bg}"><td><span style="display:inline-block;width:14px;height:14px;border-radius:4px;background:{hcolor};vertical-align:middle;margin-right:8px"></span>{nm}</td><td style="color:{hcolor};font-weight:600">{hcolor}</td><td>{fr}</td><td>{pl}</td></tr>\n'.format(bg=bg, hcolor=hcolor, nm=esc(nm), fr=esc(fr[i%10].title()), pl=esc(plf[i%10].title()))
        t = prompt.strip().title() if len(prompt.strip()) < 50 else "Tabla de colores"
        h = '<section class="hms-patch"><h2>{t}</h2><p style="color:#9aa3c7">{rows} colores.</p><table style="width:100%;border-collapse:collapse"><thead><tr><th>Color</th><th>HEX</th><th>ES</th><th>PL</th></tr></thead><tbody>{rh}</tbody></table></section>\n'.format(t=esc(t), rows=rows, rh=rh)
        return "Tabla generada.", h, "generador-local"

    if is_cards:
        plans = [("Basico","$9/mes",["5 GB","Soporte email","1 usuario"]),("Pro","$29/mes",["50 GB","Soporte 24/7","10 usuarios","API"]),("Enterprise","$99/mes",["Ilimitado","Soporte dedicado","Ilimitados","SLA 99.9%"])]
        ch = ""
        for i, (n, pr, fe) in enumerate(plans):
            hi = i == 1
            bd = "border:1px solid rgba(124,92,255,0.4)" if hi else "border:1px solid rgba(255,255,255,0.12)"
            bg = "background:rgba(124,92,255,0.1)" if hi else "background:rgba(255,255,255,0.03)"
            bd2 = '<span style="background:linear-gradient(135deg,#7c5cff,#21d4fd);color:#fff;padding:4px 10px;border-radius:8px;font-size:11px;font-weight:700;margin-bottom:8px;display:inline-block">Popular</span><br>' if hi else ""
            fl = "".join('<li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06);color:#9aa3c7;font-size:13px">✓ {}</li>'.format(esc(f)) for f in fe)
            ch += '<div style="flex:1;min-width:200px;padding:24px;border-radius:16px;{bd};{bg}">{bd2}<div style="font-size:22px;font-weight:800;color:#eef1ff;margin-bottom:4px">{n}</div><div style="font-size:28px;font-weight:800;background:linear-gradient(90deg,#7c5cff,#21d4fd);-webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:16px">{pr}</div><ul style="list-style:none;padding:0;margin:0">{fl}</ul></div>\n'.format(bd=bd, bg=bg, bd2=bd2, n=esc(n), pr=esc(pr), fl=fl)
        h = '<section class="hms-patch"><h2>Planes y Precios</h2><p style="color:#9aa3c7">Elige el plan ideal.</p><div style="display:flex;gap:16px;margin-top:20px;flex-wrap:wrap">{ch}</div></section>\n'.format(ch=ch)
        return "Planes y precios con 3 tarjetas.", h, "generador-local"

    if is_testimonials:
        ts = [("Maria G.","CEO, TechStart","Transformo nuestra operacion. Soporte excepcional.","⭐⭐⭐⭐⭐"),("Carlos R.","Director, InnovateCo","Mejor inversion del ano. ROI 300%.","⭐⭐⭐⭐⭐"),("Ana L.","Freelancer","Facil, potente y justo. Totalmente recomendado.","⭐⭐⭐⭐")]
        ch = "".join('<div style="flex:1;min-width:240px;padding:20px;border-radius:16px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,255,255,0.03)"><div style="color:#f1c40f;font-size:16px;margin-bottom:8px">{st}</div><p style="color:#eef1ff;font-size:15px;font-style:italic;line-height:1.6;margin:0 0 14px">"{qt}"</p><div style="font-weight:700;color:#eef1ff;font-size:14px">{nm}</div><div style="color:#9aa3c7;font-size:12px">{rl}</div></div>\n'.format(st=st, qt=esc(qt), nm=esc(nm), rl=esc(rl)) for nm, rl, qt, st in ts)
        h = '<section class="hms-patch"><h2>Lo que dicen nuestros clientes</h2><div style="display:flex;gap:16px;margin-top:18px;flex-wrap:wrap">{ch}</div></section>\n'.format(ch=ch)
        return "Testimonios con 3 tarjetas.", h, "generador-local"

    if is_faq:
        faqs = [("Como empiezo?","Registrate gratis en 2 minutos. Sin tarjeta."),("Periodo de prueba?","14 dias gratis con todas las funciones."),("Cancelo cuando quiera?","Sin contratos ni penalizaciones."),("Soporte en espanol?","Si, soporte 24/7 en espanol.")]
        items = "".join('<details style="border:1px solid rgba(255,255,255,0.12);border-radius:12px;padding:14px 18px;margin-bottom:10px;background:rgba(255,255,255,0.03)"><summary style="cursor:pointer;font-weight:700;color:#eef1ff;font-size:15px">{q}</summary><p style="color:#9aa3c7;margin:10px 0 0;line-height:1.6">{a}</p></details>\n'.format(q=q, a=esc(a)) for q, a in faqs)
        h = '<section class="hms-patch"><h2>Preguntas Frecuentes</h2>{items}</section>\n'.format(items=items)
        return "FAQ con 4 preguntas.", h, "generador-local"

    if is_stat:
        st = [("10K+","Clientes activos"),("99.9%","Tiempo de actividad"),("4.9/5","Satisfaccion"),("50M+","Peticiones")]
        items = "".join('<div style="text-align:center;flex:1;min-width:120px;padding:20px"><div style="font-size:36px;font-weight:800;background:linear-gradient(90deg,#7c5cff,#21d4fd);-webkit-background-clip:text;background-clip:text;color:transparent">{n}</div><div style="color:#9aa3c7;font-size:13px;margin-top:4px">{l}</div></div>\n'.format(n=n, l=esc(l)) for n, l in st)
        h = '<section class="hms-patch" style="text-align:center"><h2>Nuestros Numeros</h2><div style="display:flex;gap:12px;margin-top:18px;flex-wrap:wrap">{items}</div></section>\n'.format(items=items)
        return "Estadisticas con 4 numeros.", h, "generador-local"

    if is_team:
        ms = [("Ana Maria","CEO - Fundadora"),("Carlos Perez","CTO"),("Laura Diaz","Head of Design"),("Miguel Santos","Lead Developer")]
        cards = "".join('<div style="text-align:center;flex:1;min-width:140px;padding:20px;border-radius:16px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,255,255,0.03)"><div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#7c5cff,#21d4fd);display:grid;place-items:center;margin:0 auto 10px;font-weight:800;color:#fff;font-size:20px">{init}</div><div style="font-weight:700;color:#eef1ff">{nm}</div><div style="color:#9aa3c7;font-size:13px">{rl}</div></div>\n'.format(init=nm[0], nm=esc(nm), rl=esc(rl)) for nm, rl in ms)
        h = '<section class="hms-patch"><h2>Nuestro Equipo</h2><p style="color:#9aa3c7">Las personas detras del exito.</p><div style="display:flex;gap:16px;margin-top:18px;flex-wrap:wrap">{cards}</div></section>\n'.format(cards=cards)
        return "Equipo con 4 miembros.", h, "generador-local"

    if is_timeline:
        ev = [("2020","Fundacion","Vision de transformar la industria."),("2022","Primer millon","1 millon de usuarios activos."),("2024","Expansion global","Oficinas en Europa y LATAM."),("2026","IA integrada","Plataforma con IA nativa.")]
        items = "".join('<div style="display:flex;gap:16px;margin-bottom:20px"><div style="min-width:60px;text-align:right"><span style="font-weight:800;font-size:14px;background:linear-gradient(90deg,#7c5cff,#21d4fd);-webkit-background-clip:text;background-clip:text;color:transparent">{y}</span></div><div style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#7c5cff,#21d4fd);margin-top:4px;flex-shrink:0"></div><div><div style="font-weight:700;color:#eef1ff">{t}</div><div style="color:#9aa3c7;font-size:13px;margin-top:2px">{d}</div></div></div>\n'.format(y=y, t=esc(t), d=esc(d)) for y, t, d in ev)
        h = '<section class="hms-patch"><h2>Nuestra Historia</h2><div style="margin-top:18px">{items}</div></section>\n'.format(items=items)
        return "Linea temporal con 4 eventos.", h, "generador-local"

    if is_hero:
        h = '<section class="hms-patch" style="text-align:center;padding:48px 24px"><h2 style="font-size:32px;margin-bottom:10px">Bienvenido a Nuestra Plataforma</h2><p style="color:#9aa3c7;font-size:17px;max-width:500px;margin:0 auto">La solucion todo-en-uno para tu negocio.</p><div style="margin-top:24px;display:flex;gap:12px;justify-content:center"><span style="padding:12px 24px;border-radius:12px;background:linear-gradient(135deg,#7c5cff,#21d4fd);color:#fff;font-weight:700">Empezar Gratis</span><span style="padding:12px 24px;border-radius:12px;border:1px solid rgba(255,255,255,0.15);color:#eef1ff;font-weight:600">Ver Demo</span></div></section>\n'
        return "Hero section con CTA.", h, "generador-local"

    if is_cta:
        h = '<section class="hms-patch" style="text-align:center;padding:40px 24px;background:linear-gradient(135deg,rgba(124,92,255,0.15),rgba(33,212,253,0.1))"><h2 style="font-size:28px;margin-bottom:8px">Listo para empezar?</h2><p style="color:#9aa3c7;margin-bottom:20px">Unete a mas de 10,000 empresas.</p><span style="padding:14px 28px;border-radius:14px;background:linear-gradient(135deg,#7c5cff,#21d4fd);color:#fff;font-weight:700;font-size:15px;display:inline-block">Comienza tu prueba gratis</span></section>\n'
        return "CTA con llamada a la accion.", h, "generador-local"

    t = prompt.strip().title() if len(prompt.strip()) < 50 else "Nueva Seccion"
    h = '<section class="hms-patch"><h2>{t}</h2><p style="color:#9aa3c7;line-height:1.7">Generado a partir de: "<em>{p}</em>". Pide algo mas especifico.</p><div style="display:flex;gap:12px;margin-top:18px;flex-wrap:wrap"><div class="c"><b>Idea 1</b><p style="color:#9aa3c7;margin:6px 0 0">Primera idea.</p></div><div class="c"><b>Idea 2</b><p style="color:#9aa3c7;margin:6px 0 0">Segunda idea.</p></div><div class="c"><b>Idea 3</b><p style="color:#9aa3c7;margin:6px 0 0">Tercera idea.</p></div></div></section>\n'.format(t=t, p=prompt[:80])
    return 'Seccion "{}" generada. Pulsa "Aplicar parche".'.format(t[:30]), h, "generador-local"


# ═══════ EDITOR DE ELEMENTOS ═══════
# Manipula el HTML de la pagina directamente segun accion + selector CSS aproximado.
# Selector simple basado en tag + clases/ids del outerHTML del elemento clickeado.

def _selector_to_pattern(selector):
    """Convierte un selector tipo 'div.hero > h1' o '.btn.primary' o 'p.lead' en un patron regex
    que matchea la apertura de la primera etiqueta coincidente en el HTML."""
    sel = selector.strip()
    if not sel: return None, None
    # detectar tag
    m = re.match(r'^([a-zA-Z][\w-]*)', sel)
    tag = m.group(1).lower() if m else None
    # extraer clases
    classes = re.findall(r'\.([\w-]+)', sel)
    # extraer id
    idm = re.search(r'#([\w-]+)', sel)
    eid = idm.group(1) if idm else None
    if not tag and not classes and not eid:
        return None, None
    # construir regex: <tag ... atributos ... > (sin > dentro de strings)
    # simplificado: matchear <tag( espacio o fin ) hasta el primer '>'
    parts = ["<"]
    if tag: parts.append(re.escape(tag))
    else:   parts.append("[a-zA-Z][\\w-]*")
    if eid:
        parts.append(r"[^>]*\bid=\"?"+re.escape(eid)+r"\"?")
    if classes:
        # cada clase debe aparecer en class="..."
        for cl in classes:
            parts.append(r"(?=[^>]*\bclass=\"[^\"]*\b"+re.escape(cl)+r"\b)")
    parts.append(r"[^>]*?>")
    pattern = "".join(parts)
    return pattern, (tag, eid, classes)


def _find_element_span(html, start, end_open_tag):
    """Dado el HTML y la posicion donde empieza un tag abierto, encuentra el tag de cierre
    correspondiente (respetando anidamiento del mismo tag). Devuelve (start, end_exclusive)
    del bloque completo, INCLUYENDO el tag de apertura y cierre.
    Si no encuentra cierre (HTML malformado), devuelve (start, gt+1) -> solo el tag abierto."""
    # buscar '>' de cierre del tag abierto
    gt = html.find('>', start)
    if gt == -1: return None
    # detectar si es self-closing
    pre = html[max(start, gt-2):gt]
    if pre.endswith('/'):
        return (start, gt+1)
    # tag name
    m = re.match(r'<([a-zA-Z][\w-]*)', html[start:])
    if not m: return None
    tag_name = m.group(1).lower()
    # buscar cierre balanceado
    depth = 1
    i = gt + 1
    open_re  = re.compile(r'<' + re.escape(tag_name) + r'(\s|>|/)', re.IGNORECASE)
    close_re = re.compile(r'</' + re.escape(tag_name) + r'\s*>', re.IGNORECASE)
    while i < len(html):
        o = open_re.search(html, i)
        c = close_re.search(html, i)
        if not c:
            # HTML malformado: no hay cierre. Tratamos como self-closing.
            return (start, gt + 1)
        if o and o.start() < c.start():
            depth += 1
            i = o.end()
        else:
            depth -= 1
            i = c.end()
            if depth == 0:
                return (start, i)
    # tampoco devolvemos None: cerramos en fin de string
    return (start, len(html))


def _apply_element_action(html, action, selector, content, old_text):
    """Aplica la accion al HTML. Devuelve (new_html, msg, ok)."""
    pattern, ctx = _selector_to_pattern(selector)
    if not pattern:
        return html, "Selector invalido: "+selector, False

    m = re.search(pattern, html, re.IGNORECASE)
    if not m:
        return html, "No se encontro el elemento '"+selector+"' en la pagina.", False

    open_start = m.start()
    span = _find_element_span(html, open_start, m.end())
    if not span:
        return html, "No se pudo localizar el bloque completo del elemento.", False
    block_start, block_end = span
    inner_start = html.find('>', open_start) + 1
    inner = html[inner_start:block_end]
    # limpiar cierre
    last_close = inner.rfind('</')
    if last_close != -1:
        inner = inner[:last_close]

    if action == "delete":
        new_html = html[:block_start] + html[block_end:]
        # limpiar líneas vacías residuales
        new_html = re.sub(r'\n\s*\n', '\n', new_html)
        return new_html, "Elemento eliminado.", True

    if action == "edit":
        # Reemplazar el texto del elemento. Conserva la apertura y el cierre.
        # Calculamos la posicion real del cierre: si block_end == gt+1 -> no hay cierre (HTML malformado)
        gt = html.find('>', open_start)
        no_closing = (block_end == gt + 1)

        # Extraer el texto interno actual
        inner_text = re.sub(r'<[^>]+>', '', inner).strip()

        # Sustituir texto respetando old_text si viene
        if old_text and old_text in inner_text:
            new_text = inner_text.replace(old_text, content, 1)
        else:
            new_text = content

        if no_closing:
            # Reconstruir el bloque: apertura + texto + cierre
            tag_m = re.match(r'<([a-zA-Z][\w-]*)[^>]*>', html[open_start:gt+1])
            tag_full = html[open_start:gt+1]
            if tag_m:
                tag_name = tag_m.group(1)
                new_block = tag_full + new_text + "</" + tag_name + ">"
            else:
                new_block = tag_full + new_text
            new_html = html[:open_start] + new_block + html[block_end:]
        else:
            # Mantener el contenido no-texto interior (hijos HTML), pero reemplazar texto plano
            # Si hay old_text en inner, lo cambiamos in-place
            if old_text and old_text in inner:
                new_inner = inner.replace(old_text, content, 1)
                new_html = html[:inner_start] + new_inner + html[block_end:]
            else:
                # Reemplazar primer bloque de texto (entre > y <)
                replaced = re.sub(r'>(\s*[^<]+)<', lambda m: '>' + new_text + '<',
                                  inner, count=1)
                if replaced == inner:
                    # no había texto entre tags: insertar al principio
                    replaced = new_text + inner
                new_html = html[:inner_start] + replaced + html[block_end:]
        return new_html, "Texto actualizado.", True

    if action == "change":
        # reemplazar el BLOQUE entero (tag incluido) con el nuevo HTML
        # 'content' debe ser HTML completo, o si no, lo envolvemos en el tag original
        new_content = content
        if not re.search(r'^<[a-zA-Z]', new_content.strip()):
            # no parece HTML -> envolver en el mismo tag
            tag_m = re.match(r'<([a-zA-Z][\w-]*)', html[open_start:])
            if tag_m:
                new_content = "<" + tag_m.group(1) + ">" + content + "</" + tag_m.group(1) + ">"
        new_html = html[:block_start] + new_content + html[block_end:]
        return new_html, "Elemento reemplazado.", True

    if action == "add":
        # añadir DESPUÉS del bloque objetivo
        # 'content' puede ser HTML completo o texto plano
        new_content = content
        if not re.search(r'^<[a-zA-Z]', new_content.strip()):
            new_content = "<p>" + content + "</p>"
        new_html = html[:block_end] + "\n" + new_content + html[block_end:]
        return new_html, "Contenido insertado despues del elemento.", True

    return html, "Accion no implementada: "+action, False


def ai_generate(prompt, page, api_key, model, endpoint):
    # 1) Resolver endpoint + key: prioridad -> argumentos > env vars
    endpoint = (endpoint or os.environ.get("HERMES_PROXY_URL", "")).strip()
    api_key  = (api_key  or os.environ.get("HERMES_PROXY_KEY", "")).strip()
    model    = (model    or os.environ.get("HERMES_MODEL", "")).strip()

    if not endpoint or not model:
        msg = "Falta endpoint o modelo. Configura el motor IA en el chat (icono engranaje) o define HERMES_PROXY_URL/HERMES_MODEL."
        return msg, '<section class="hms-patch"><h2>Configuracion incompleta</h2><p style="color:#9aa3c7">'+esc(msg)+'</p></section>', "ai-proxy-error"

    # 2) Construir prompt de sistema: pedir SOLO HTML, con estilo dark-glass
    system = (
        "Eres un generador de secciones HTML para un sitio web estatico con estetica dark-glass. "
        "Responde EXCLUSIVAMENTE con un fragmento HTML valido que sera insertado dentro de un <main>. "
        "Usa la clase .hms-patch en el contenedor raiz. "
        "No incluyas <html>, <head>, <body>, <script>, <style> externos ni markdown. "
        "Estilo: colores #7c5cff (acento) y #21d4fd (acento-2), fondo translucido, esquinas 16-22px, "
        "texto claro #eef1ff y mutado #9aa3c7. Incluye un <h2> y parrafos descriptivos."
    )
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": "Pagina: "+page+"\nPeticion: "+prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
    }).encode("utf-8")

    # 3) Hacer request HTTP(S) sin dependencias externas
    req = urllib.request.Request(endpoint, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        # OpenAI-compatible usa "Bearer"; Gemini-compatible tambien
        req.add_header("Authorization", "Bearer " + api_key)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:400]
        msg = "Error HTTP "+str(e.code)+" del proveedor: "+err
        return msg, '<section class="hms-patch"><h2>Error del proveedor</h2><p style="color:#9aa3c7">'+esc(msg)+'</p></section>', "ai-proxy-error"
    except urllib.error.URLError as e:
        msg = "No se pudo conectar con el endpoint: "+str(e.reason)
        return msg, '<section class="hms-patch"><h2>Sin conexion</h2><p style="color:#9aa3c7">'+esc(msg)+'</p></section>', "ai-proxy-error"
    except Exception as e:
        msg = "Fallo inesperado: "+str(e)
        return msg, '<section class="hms-patch"><h2>Error</h2><p style="color:#9aa3c7">'+esc(msg)+'</p></section>', "ai-proxy-error"

    # 4) Parsear respuesta JSON estilo OpenAI
    try:
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        msg = "Respuesta invalida del proveedor: "+str(e)
        return msg, '<section class="hms-patch"><h2>Respuesta invalida</h2><p style="color:#9aa3c7">'+esc(msg)+'</p></section>', "ai-proxy-error"

    # 5) Limpiar posibles envolturas de markdown ```html ... ```
    html = content.strip()
    if html.startswith("```"):
        # quitar primera linea ```html o ``` y la ultima ```
        lines = html.split("\n")
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].lstrip().startswith("```"):
            lines = lines[:-1]
        html = "\n".join(lines).strip()

    # 6) Sanity check: si no parece HTML, envolver
    if "<" not in html or ">" not in html:
        return "El modelo devolvio texto sin HTML.", '<section class="hms-patch"><h2>Sin HTML</h2><p style="color:#9aa3c7">'+esc(html[:300])+'</p></section>', "ai-proxy-error"

    return "Contenido IA generado para '"+page+"'. Pulsa 'Aplicar parche'.", html+"\n", "ai-proxy"

class H(http.server.BaseHTTPRequestHandler):
    def _send(self, code, obj=None, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        if obj is not None: self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST,GET,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    def do_GET(self):
        p = self.path.split("?")[0]
        if p.startswith("/assets/"):
            f = p.lstrip("/")
        elif p.startswith("/uploads/"):
            f = p.lstrip("/")
        elif p in ("/",""):
            f = "index.html"
        else:
            f = PAGES.get(p.strip("/"))
        if not f: self._send(404,{"error":"not found"}); return
        path = os.path.join(ROOT, f)
        if not os.path.isfile(path): self._send(404,{"error":"missing "+f}); return
        ctype = "text/html"
        if f.endswith(".css"): ctype="text/css"
        elif f.endswith(".js"): ctype="text/javascript"
        elif f.endswith(".jpg") or f.endswith(".jpeg"): ctype = "image/jpeg"
        elif f.endswith(".png"): ctype = "image/png"
        elif f.endswith(".webp"): ctype = "image/webp"
        elif f.endswith(".gif"): ctype = "image/gif"
        elif f.endswith(".svg"): ctype = "image/svg+xml"
        with open(path,"rb") as fh: self.send_response(200); self.send_header("Content-Type",ctype); self.end_headers(); self.wfile.write(fh.read())
    def do_POST(self):
        length = int(self.headers.get("Content-Length",0)); raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw or b"{}")
        if self.path == "/api/generate":
            prompt = data.get("prompt",""); pg = data.get("page","home")
            api_key = data.get("api_key",""); model = data.get("model","")
            endpoint = data.get("endpoint","")
            if model and endpoint:
                try:
                    r, h, who = ai_generate(prompt, pg, api_key, model, endpoint)
                    self._send(200, {"reply":r,"html":h,"powered_by":who}); return
                except Exception as e:
                    err = "Fallo ai_generate: "+str(e)
                    self._send(500, {"reply":err,"html":'<section class="hms-patch"><h2>Error IA</h2><p style="color:#9aa3c7">'+esc(err)+'</p></section>',"powered_by":"ai-proxy-error"}); return
            # Sin config -> fallback local
            r, h, who = local_generate(prompt, pg); self._send(200, {"reply":r,"html":h,"powered_by":who})
        elif self.path == "/api/patch":
            pg = data.get("page","home"); html = data.get("html",""); f = PAGES.get(pg)
            if not f: self._send(400,{"ok":False,"error":"pagina desconocida"}); return
            path = os.path.join(ROOT, f)
            with open(path,"r",encoding="utf-8") as fh: c = fh.read()
            c = c.replace(MARKER, MARKER+"\n"+html, 1) if MARKER in c else c.replace("</body>", html+"\n</body>", 1)
            with open(path,"w",encoding="utf-8") as fh: fh.write(c)
            self._send(200, {"ok":True,"page":pg,"file":f})
        elif self.path == "/api/element":
            self._handle_element(data)
        elif self.path == "/api/element_ai":
            self._handle_element_ai(data)
        elif self.path == "/api/elements":
            self._handle_elements_list(data)
        elif self.path == "/api/elements_apply":
            self._handle_elements_apply(data)
        elif self.path == "/api/elements_ai":
            self._handle_elements_ai(data)
        elif self.path == "/api/image_search":
            self._handle_image_search(data)
        elif self.path == "/api/image_generate":
            self._handle_image_generate(data)
        elif self.path == "/api/image_insert":
            self._handle_image_insert(data)
        elif self.path == "/api/image_placeholder":
            self._handle_image_placeholder(data)
        elif self.path == "/api/image_upload":
            self._handle_image_upload(length, raw)
        else: self._send(404,{"error":"no route"})

    def _handle_element(self, data):
        """Aplica una accion (add/edit/change/delete) a un selector CSS dentro de la pagina."""
        action   = (data.get("action") or "").strip().lower()
        page     = (data.get("page") or "home").strip()
        selector = (data.get("selector") or "").strip()
        content  = data.get("content") or ""           # HTML o texto nuevo
        old_text = (data.get("old_text") or "").strip()# contexto opcional

        if action not in ("add","edit","change","delete"):
            self._send(400,{"ok":False,"error":"accion invalida (usa add/edit/change/delete)"})
            return
        f = PAGES.get(page)
        if not f:
            self._send(400,{"ok":False,"error":"pagina desconocida"})
            return
        path = os.path.join(ROOT, f)
        try:
            with open(path,"r",encoding="utf-8") as fh: c = fh.read()
        except Exception as e:
            self._send(500,{"ok":False,"error":"no se pudo leer "+f+": "+str(e)})
            return

        new_c, msg, ok = _apply_element_action(c, action, selector, content, old_text)
        if not ok:
            self._send(400,{"ok":False,"error":msg})
            return

        # Backup
        try:
            with open(path+".bak","w",encoding="utf-8") as fh: fh.write(c)
        except Exception: pass
        with open(path,"w",encoding="utf-8") as fh: fh.write(new_c)
        self._send(200,{"ok":True,"page":page,"file":f,"action":action,"msg":msg})

    def _handle_element_ai(self, data):
        """Genera una sugerencia IA para un elemento concreto y la devuelve al frontend."""
        action     = (data.get("action") or "edit").strip().lower()
        page       = (data.get("page") or "home").strip()
        selector   = (data.get("selector") or "").strip()
        tag        = (data.get("tag") or "").strip().lower()
        current    = (data.get("current_text") or "").strip()
        outer_html = (data.get("outer_html") or "").strip()
        user_prompt= (data.get("user_prompt") or "").strip()
        api_key    = (data.get("api_key") or "").strip()
        model      = (data.get("model") or "").strip()
        endpoint   = (data.get("endpoint") or "").strip()
        provider   = (data.get("provider") or "").strip()

        if not user_prompt:
            self._send(400,{"ok":False,"error":"user_prompt vacio"})
            return
        if not model or not endpoint:
            self._send(400,{"ok":False,"error":"Configura el motor IA (engranaje) antes de usar Generar con IA."})
            return

        # Construir prompt de sistema especializado para edicion de elementos
        sys_prompt = _build_element_system_prompt(action, tag, selector)

        # Construir el user prompt con contexto
        ctx_lines = [
            "Accion a aplicar: " + action,
            "Tipo de elemento: " + (tag or "(desconocido)"),
            "Selector CSS: " + (selector or "(ninguno)"),
        ]
        if current:
            ctx_lines.append("Texto actual: \"" + current[:300] + "\"")
        if outer_html:
            ctx_lines.append("HTML del elemento (recortado): " + outer_html[:400])
        ctx_lines.append("")
        ctx_lines.append("Peticion del usuario: " + user_prompt)

        full_prompt = "\n".join(ctx_lines)

        # Llamar a ai_generate
        try:
            reply, html_resp, who = ai_generate(full_prompt, page, api_key, model, endpoint)
        except Exception as e:
            self._send(500,{"ok":False,"error":"Fallo ai_generate: "+str(e)})
            return

        # Limpiar envolturas ```html ... ``` que a veces añade la IA
        clean = html_resp.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            if lines and lines[0].lstrip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].lstrip().startswith("```"):
                lines = lines[:-1]
            clean = "\n".join(lines).strip()

        # Para 'edit' se permite texto plano sin tags; para 'change'/'add' exigimos HTML
        if action == "edit":
            content = clean
        else:
            if "<" not in clean or ">" not in clean:
                self._send(500,{"ok":False,"error":"La IA no devolvio HTML para la accion '"+action+"'","raw":(clean or "")[:300]})
                return
            content = clean

        self._send(200,{
            "ok": True,
            "content": clean,
            "powered_by": who,
            "action": action,
            "tag": tag
        })

    def _handle_elements_list(self, data):
        """Devuelve la lista de elementos editables de la pagina."""
        page = (data.get("page") or "home").strip()
        f = PAGES.get(page)
        if not f:
            self._send(400,{"ok":False,"error":"pagina desconocida"})
            return
        path = os.path.join(ROOT, f)
        try:
            with open(path,"r",encoding="utf-8") as fh: html = fh.read()
        except Exception as e:
            self._send(500,{"ok":False,"error":"no se pudo leer "+f+": "+str(e)})
            return
        elements = list_editable_elements(html)
        self._send(200,{"ok":True,"page":page,"file":f,"count":len(elements),"elements":elements})

    def _handle_elements_apply(self, data):
        """Aplica un lote de acciones en transaccion logica. Backup unico."""
        page    = (data.get("page") or "home").strip()
        actions = data.get("actions") or []
        if not isinstance(actions, list) or not actions:
            self._send(400,{"ok":False,"error":"actions[] requerido (al menos 1)"})
            return
        if len(actions) > 50:
            self._send(400,{"ok":False,"error":"maximo 50 acciones por lote"})
            return
        f = PAGES.get(page)
        if not f:
            self._send(400,{"ok":False,"error":"pagina desconocida"})
            return
        path = os.path.join(ROOT, f)
        try:
            with open(path,"r",encoding="utf-8") as fh: original = fh.read()
        except Exception as e:
            self._send(500,{"ok":False,"error":"no se pudo leer "+f+": "+str(e)})
            return

        current = original
        applied = 0
        failed  = []
        for i, act in enumerate(actions):
            action   = (act.get("action") or "").strip().lower()
            selector = (act.get("selector") or "").strip()
            content  = act.get("content") or ""
            old_text = (act.get("old_text") or "").strip()
            if action not in ("add","edit","change","delete"):
                failed.append({"index":i,"selector":selector,"error":"accion invalida"})
                continue
            new_c, msg, ok = _apply_element_action(current, action, selector, content, old_text)
            if not ok:
                failed.append({"index":i,"selector":selector,"error":msg})
                # ABORT: revertir todo el lote
                self._send(400,{
                    "ok":False,
                    "error":"Accion #"+str(i)+" fallo ('"+selector+"'): "+msg+". Lote ABORTADO, no se aplico ningun cambio.",
                    "applied":applied,
                    "failed":failed
                })
                return
            current = new_c
            applied += 1

        if applied == 0:
            self._send(400,{"ok":False,"error":"Ninguna accion valida","applied":0,"failed":failed})
            return

        # Backup unico del estado previo
        try:
            with open(path+".bak","w",encoding="utf-8") as fh: fh.write(original)
        except Exception: pass
        with open(path,"w",encoding="utf-8") as fh: fh.write(current)
        self._send(200,{"ok":True,"page":page,"file":f,"applied":applied,"failed":failed})

    def _handle_elements_ai(self, data):
        """Genera sugerencias IA para multiples elementos en una sola llamada.
        Devuelve {ok, suggestions: [{selector, content, powered_by}, ...]} en el mismo orden."""
        page      = (data.get("page") or "home").strip()
        selectors = data.get("selectors") or []
        action    = (data.get("action") or "edit").strip().lower()
        tag       = (data.get("tag") or "").strip().lower()
        user_prompt= (data.get("user_prompt") or "").strip()
        api_key   = (data.get("api_key") or "").strip()
        model     = (data.get("model") or "").strip()
        endpoint  = (data.get("endpoint") or "").strip()
        provider  = (data.get("provider") or "").strip()
        elements_ctx = data.get("elements_ctx") or []   # [{selector, tag, text}]

        if not isinstance(selectors, list) or not selectors:
            self._send(400,{"ok":False,"error":"selectors[] requerido"})
            return
        if len(selectors) > 50:
            self._send(400,{"ok":False,"error":"maximo 50 selectores por lote"})
            return
        if not model or not endpoint:
            self._send(400,{"ok":False,"error":"Configura el motor IA antes de usar Generar con IA (multi)."})
            return
        if not user_prompt:
            self._send(400,{"ok":False,"error":"user_prompt vacio"})
            return

        # Construir system prompt: pide a la IA un JSON array
        sys_prompt = (
            "Eres un asistente de edicion web que trabaja sobre VARIOS elementos a la vez. "
            "Recibiras una lista de "+str(len(selectors))+" elementos con su tipo, selector y texto actual. "
            "Tu trabajo es generar el contenido NUEVO para CADA elemento, segun la peticion del usuario. "
            "Responde EXCLUSIVAMENTE con un JSON array valido, sin markdown, sin ```. "
            "El array debe tener EXACTAMENTE "+str(len(selectors))+" objetos en el MISMO ORDEN, con la forma:\n"
            '[{"selector": "...", "content": "..."}, ...]\n'
            "Donde 'content' es el texto/HTML que reemplazara al actual. "
            "Si la accion es 'edit', content puede ser texto plano. "
            "Si es 'change' o 'add', content debe ser HTML valido. "
            "Si es 'delete', content puede ser vacio o null."
        )

        # User prompt con la lista
        lines = [
            "Accion: "+action,
            "Peticion global: "+user_prompt,
            "",
            "Elementos a editar (en orden):"
        ]
        for idx, sel in enumerate(selectors, 1):
            ctx = next((e for e in elements_ctx if e.get("selector") == sel), None)
            tag_e  = (ctx or {}).get("tag", tag or "div")
            text_e = (ctx or {}).get("text", "")
            lines.append(str(idx) + ". selector=\"" + sel + "\" tag=<" + tag_e + ">")
            if text_e:
                lines.append("   texto actual: \"" + text_e[:200] + "\"")

        full_user = "\n".join(lines)

        # Llamada HTTP directa al proveedor (sin pasar por ai_generate) porque
        # ai_generate envuelve el texto en HTML de fallback cuando no detecta tags,
        # y eso rompe el parseo del JSON array.
        try:
            endpoint_eff = (endpoint or os.environ.get("HERMES_PROXY_URL","")).strip()
            api_key_eff  = (api_key  or os.environ.get("HERMES_PROXY_KEY","")).strip()
            if not endpoint_eff or not model:
                self._send(400,{"ok":False,"error":"endpoint o model vacio"})
                return
            req_body = json.dumps({
                "model": model,
                "messages":[
                    {"role":"system","content": sys_prompt},
                    {"role":"user","content": full_user}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }).encode("utf-8")
            http_req = urllib.request.Request(endpoint_eff, data=req_body, method="POST")
            http_req.add_header("Content-Type","application/json")
            if api_key_eff:
                http_req.add_header("Authorization","Bearer "+api_key_eff)
            with urllib.request.urlopen(http_req, timeout=60) as resp:
                raw_text = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            self._send(500,{"ok":False,"error":"Fallo llamada IA: "+str(e)})
            return

        try:
            data_resp = json.loads(raw_text)
            who = "ai-proxy"
            html_resp = data_resp["choices"][0]["message"]["content"]
        except Exception as e:
            self._send(500,{"ok":False,"error":"Respuesta invalida: "+str(e)})
            return

        if not html_resp:
            self._send(500,{"ok":False,"error":"La IA devolvio respuesta vacia","raw":(html_resp or "")[:300]})
            return

        # Limpiar envolturas ```json``` y similares
        clean = html_resp.strip()
        if clean.startswith("```"):
            lines2 = clean.split("\n")
            if lines2 and lines2[0].lstrip().startswith("```"):
                lines2 = lines2[1:]
            if lines2 and lines2[-1].lstrip().startswith("```"):
                lines2 = lines2[:-1]
            clean = "\n".join(lines2).strip()

        # Intentar parsear como JSON array
        suggestions = []
        # Buscar el primer '[' y el último ']'
        a = clean.find("[")
        b = clean.rfind("]")
        if a != -1 and b != -1 and b > a:
            try:
                arr = json.loads(clean[a:b+1])
            except Exception as e:
                self._send(500,{"ok":False,"error":"La IA no devolvio un JSON array valido: "+str(e),"raw":clean[:400]})
                return
            if not isinstance(arr, list):
                self._send(500,{"ok":False,"error":"La IA devolvio algo que no es un array","raw":clean[:400]})
                return
            # Si la IA devolvio menos o mas objetos, los rellenamos/recortamos
            for i, sel in enumerate(selectors):
                if i < len(arr) and isinstance(arr[i], dict):
                    suggestions.append({
                        "selector": sel,
                        "content":  arr[i].get("content",""),
                        "powered_by": who
                    })
                else:
                    suggestions.append({"selector": sel, "content":"", "powered_by": who, "missing": True})
        else:
            # Fallback: tratar todo el contenido como UN solo elemento (probablemente solo 1)
            suggestions = [{"selector": s, "content": clean, "powered_by": who} for s in selectors]

        self._send(200,{
            "ok": True,
            "powered_by": who,
            "action": action,
            "suggestions": suggestions
        })

    # ═══════ IMÁGENES ═══════

    def _handle_image_search(self, data):
        """Busca imagenes en Unsplash/Pexels/Pixabay."""
        query    = (data.get("query") or "").strip()
        source   = (data.get("source") or "all").lower()
        count    = min(int(data.get("count") or 6), 20)
        if not query:
            self._send(400,{"ok":False,"error":"query requerido"}); return
        results = []
        errors  = []
        # Unsplash
        if source in ("all","unsplash"):
            key = (data.get("unsplash_key") or os.environ.get("UNSPLASH_ACCESS_KEY","")).strip()
            if key:
                try:
                    r = self._search_unsplash(query, count, key)
                    results.extend([dict(x, source="unsplash") for x in r])
                except Exception as e:
                    errors.append("unsplash: "+str(e))
        # Pexels
        if source in ("all","pexels"):
            key = (data.get("pexels_key") or os.environ.get("PEXELS_API_KEY","")).strip()
            if key:
                try:
                    r = self._search_pexels(query, count, key)
                    results.extend([dict(x, source="pexels") for x in r])
                except Exception as e:
                    errors.append("pexels: "+str(e))
        # Pixabay
        if source in ("all","pixabay"):
            key = (data.get("pixabay_key") or os.environ.get("PIXABAY_API_KEY","")).strip()
            if key:
                try:
                    r = self._search_pixabay(query, count, key)
                    results.extend([dict(x, source="pixabay") for x in r])
                except Exception as e:
                    errors.append("pixabay: "+str(e))
        if not results:
            msg = "No se encontraron imagenes. "
            if errors:
                msg += "Errores: " + "; ".join(errors)
            else:
                msg += "Configura UNSPLASH_ACCESS_KEY, PEXELS_API_KEY o PIXABAY_API_KEY en .env o en la configuracion del widget."
            self._send(400,{"ok":False,"error":msg,"errors":errors}); return
        # recorta a count
        results = results[:count]
        self._send(200,{"ok":True,"query":query,"count":len(results),"results":results,"errors":errors})

    def _search_unsplash(self, query, count, key):
        url = "https://api.unsplash.com/search/photos?per_page=" + str(count) + "&query=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"Authorization":"Client-ID "+key, "Accept-Version":"v1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = []
        for p in data.get("results", []):
            out.append({
                "id": p.get("id"),
                "url": p.get("urls",{}).get("regular"),
                "thumb": p.get("urls",{}).get("small"),
                "width": p.get("width"),
                "height": p.get("height"),
                "author": p.get("user",{}).get("name",""),
                "alt": p.get("alt_description") or query
            })
        return out

    def _search_pexels(self, query, count, key):
        url = "https://api.pexels.com/v1/search?per_page=" + str(count) + "&query=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"Authorization":key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = []
        for p in data.get("photos", []):
            out.append({
                "id": "pexels-"+str(p.get("id")),
                "url": p.get("src",{}).get("large"),
                "thumb": p.get("src",{}).get("tiny"),
                "width": p.get("width"),
                "height": p.get("height"),
                "author": p.get("photographer",""),
                "alt": p.get("alt") or query
            })
        return out

    def _search_pixabay(self, query, count, key):
        url = "https://pixabay.com/api/?per_page=" + str(count) + "&q=" + urllib.parse.quote(query) + "&key=" + key
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = []
        for p in data.get("hits", []):
            out.append({
                "id": "pixabay-"+str(p.get("id")),
                "url": p.get("largeImageURL"),
                "thumb": p.get("previewURL"),
                "width": p.get("imageWidth"),
                "height": p.get("imageHeight"),
                "author": p.get("user",""),
                "alt": query
            })
        return out

    def _handle_image_generate(self, data):
        """Genera una imagen con DALL-E o Stability. Si no hay provider, devuelve placeholder."""
        prompt  = (data.get("prompt") or "").strip()
        provider= (data.get("provider") or "").lower()
        api_key = (data.get("api_key") or "").strip()
        if not prompt:
            self._send(400,{"ok":False,"error":"prompt requerido"}); return
        if not provider:
            provider = "openai" if (api_key or os.environ.get("OPENAI_API_KEY","")) else "placeholder"
        try:
            if provider == "openai":
                key = api_key or os.environ.get("OPENAI_API_KEY","")
                if not key: raise ValueError("OPENAI_API_KEY no configurada")
                body = json.dumps({"model":"dall-e-3","prompt":prompt,"n":1,"size":"1024x1024"}).encode("utf-8")
                req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body, method="POST",
                    headers={"Authorization":"Bearer "+key, "Content-Type":"application/json"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                item = data["data"][0]
                self._send(200,{"ok":True,"url":item.get("url"),"revised_prompt":item.get("revised_prompt",""),"powered_by":"openai-dalle3"})
                return
            elif provider == "stability":
                key = api_key or os.environ.get("STABILITY_API_KEY","")
                if not key: raise ValueError("STABILITY_API_KEY no configurada")
                body = json.dumps({"text_prompts":[{"text":prompt}],"cfg_scale":7,"height":1024,"width":1024,"samples":1}).encode("utf-8")
                req = urllib.request.Request("https://api.stability.ai/v2beta/stable-image/generate/core",
                    data=body, method="POST",
                    headers={"Authorization":"Bearer "+key, "Content-Type":"application/json", "Accept":"image/*"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    # la respuesta es la imagen binaria directamente
                    raw = resp.read()
                # guardar
                fname = "gen-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8] + ".png"
                with open(os.path.join(UPLOADS_DIR, fname), "wb") as fh: fh.write(raw)
                self._send(200,{"ok":True,"url":"/uploads/"+fname,"revised_prompt":prompt,"powered_by":"stability"})
                return
            else:
                # placeholder
                self._send(200,{"ok":True,"url":"placeholder://"+prompt,"placeholder":True,"revised_prompt":prompt,"powered_by":"placeholder"})
                return
        except Exception as e:
            # si falla, devolvemos placeholder
            self._send(200,{"ok":True,"url":"placeholder://"+prompt,"placeholder":True,"revised_prompt":prompt,"powered_by":"placeholder-fallback","warning":str(e)})

    def _handle_image_placeholder(self, data):
        """Genera un SVG placeholder basado en el prompt (fallback que SIEMPRE funciona)."""
        prompt = (data.get("prompt") or "imagen").strip()
        width  = int(data.get("width")  or 1200)
        height = int(data.get("height") or 600)
        # genera hash del prompt para colores reproducibles
        import hashlib
        h = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        c1 = "#" + h[0:6]
        c2 = "#" + h[6:12]
        # texto seguro
        safe = (prompt[:50] or "imagen").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+str(width)+' '+str(height)+'" width="'+str(width)+'" height="'+str(height)+'">'
            '<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">'
            '<stop offset="0%" stop-color="'+c1+'"/>'
            '<stop offset="100%" stop-color="'+c2+'"/>'
            '</linearGradient></defs>'
            '<rect width="100%" height="100%" fill="url(#g)"/>'
            '<circle cx="20%" cy="30%" r="120" fill="rgba(255,255,255,0.1)"/>'
            '<circle cx="80%" cy="70%" r="180" fill="rgba(255,255,255,0.08)"/>'
            '<text x="50%" y="50%" font-family="Inter,system-ui,sans-serif" font-size="'+str(max(20, min(48, width//25)))+'" '
            'font-weight="800" fill="white" text-anchor="middle" dominant-baseline="middle" opacity="0.95">'
            + safe +
            '</text>'
            '<text x="50%" y="'+str(int(height*0.92))+'" font-family="Inter,system-ui,sans-serif" font-size="14" '
            'fill="white" text-anchor="middle" opacity="0.6">Hermes Studio Placeholder</text>'
            '</svg>'
        )
        # devuelve data URL + svg raw
        import base64
        b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        self._send(200,{"ok":True,"svg":svg,"data_url":"data:image/svg+xml;base64,"+b64,"width":width,"height":height,"prompt":prompt})

    def _handle_image_insert(self, data):
        """Inserta o reemplaza una imagen en una pagina."""
        page     = (data.get("page") or "home").strip()
        selector = (data.get("selector") or "").strip()
        url      = (data.get("url") or "").strip()
        alt      = (data.get("alt") or "").strip()
        position = (data.get("position") or "replace").strip().lower()   # replace | after
        # si la url es placeholder://, conviertela a data url SVG
        if url.startswith("placeholder://"):
            prompt = url[len("placeholder://"):]
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" width="1200" height="600">'
                '<rect width="100%" height="100%" fill="#7c5cff"/>'
                '<text x="50%" y="50%" font-family="Inter,system-ui,sans-serif" font-size="48" font-weight="800" fill="white" text-anchor="middle" dominant-baseline="middle">'
                + (prompt[:30] or "imagen") + '</text></svg>'
            )
            import base64
            url = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
        if not url:
            self._send(400,{"ok":False,"error":"url requerida"}); return
        f = PAGES.get(page)
        if not f: self._send(400,{"ok":False,"error":"pagina desconocida"}); return
        # construir el HTML del <img>
        safe_alt = alt.replace('"', '&quot;')
        img_html = '<img src="'+url.replace('"','%22')+'" alt="'+safe_alt+'" loading="lazy" style="max-width:100%;height:auto;border-radius:14px">'
        path = os.path.join(ROOT, f)
        try:
            with open(path,"r",encoding="utf-8") as fh: original = fh.read()
        except Exception as e:
            self._send(500,{"ok":False,"error":"no se pudo leer: "+str(e)}); return
        # logica: si hay selector, replace/after
        action = "add"  # por defecto: insertar nuevo
        if selector:
            if position == "after":
                action = "add"
            else:
                action = "change"  # reemplazar el elemento por la imagen
                # si el selector apunta a un <img>, mejor cambiar solo el src y alt
                if selector.lower().startswith("img") or "img" in selector.lower()[:6]:
                    # cambio "in-place": reemplazar atributos src/alt del img seleccionado
                    new_c, msg, ok = _apply_img_attrs(original, selector, url, alt)
                    if ok:
                        with open(path+".bak","w",encoding="utf-8") as fh: fh.write(original)
                        with open(path,"w",encoding="utf-8") as fh: fh.write(new_c)
                        self._send(200,{"ok":True,"page":page,"file":f,"action":"img-attrs","msg":msg})
                    else:
                        self._send(400,{"ok":False,"error":msg})
                    return
        # caso general: usar _apply_element_action
        if not selector:
            # crear un bloque <figure> nuevo tras el HERMES-PATCH
            figure = '<figure style="margin:24px auto;max-width:920px;text-align:center">' + img_html + (('<figcaption style="color:#9aa3c7;margin-top:8px;font-size:14px">'+safe_alt+'</figcaption>') if alt else '') + '</figure>'
            c = original
            if MARKER in c:
                c = c.replace(MARKER, MARKER+"\n"+figure, 1)
            else:
                c = c.replace("</body>", figure+"\n</body>", 1)
            with open(path+".bak","w",encoding="utf-8") as fh: fh.write(original)
            with open(path,"w",encoding="utf-8") as fh: fh.write(c)
            self._send(200,{"ok":True,"page":page,"file":f,"action":"create-figure","msg":"Imagen anadida al final de la pagina."})
            return
        new_c, msg, ok = _apply_element_action(original, action, selector, img_html, "")
        if not ok:
            self._send(400,{"ok":False,"error":msg}); return
        with open(path+".bak","w",encoding="utf-8") as fh: fh.write(original)
        with open(path,"w",encoding="utf-8") as fh: fh.write(new_c)
        self._send(200,{"ok":True,"page":page,"file":f,"action":action,"msg":msg})

    def _handle_image_upload(self, length, raw):
        """Recibe un archivo (multipart o base64 JSON) y lo guarda en /uploads/."""
        ctype = (self.headers.get("Content-Type") or "").lower()
        data_b64 = None
        name = "upload"
        # caso 1: JSON con { data: "data:image/...;base64,...", name: "..." }
        if ctype.startswith("application/json"):
            try:
                payload = json.loads(raw.decode("utf-8"))
                url = payload.get("data","")
                name = payload.get("name","upload")
                if url.startswith("data:"):
                    head, b64 = url.split(",",1)
                    mime = head[5:].split(";",1)[0]
                    data_b64 = (mime, b64)
            except Exception as e:
                self._send(400,{"ok":False,"error":"JSON invalido: "+str(e)}); return
        else:
            # caso 2: multipart/form-data - simplificado: leer todo el body
            # (no usamos cgi.FieldStorage para mantener cero dependencias)
            # Se espera: "data:image/png;base64,XXX" en el cuerpo
            try:
                txt = raw.decode("utf-8", errors="replace")
                if txt.startswith("data:"):
                    head, b64 = txt.split(",",1)
                    mime = head[5:].split(";",1)[0]
                    data_b64 = (mime, b64)
            except Exception:
                pass
        if not data_b64:
            self._send(400,{"ok":False,"error":"No se encontro data:image/...;base64,... en el body"}); return
        mime, b64 = data_b64
        if mime not in UPLOADS_ALLOWED:
            self._send(400,{"ok":False,"error":"MIME no permitido: "+mime+". Usa: "+", ".join(UPLOADS_ALLOWED.keys())}); return
        import base64
        try:
            raw_bytes = base64.b64decode(b64)
        except Exception as e:
            self._send(400,{"ok":False,"error":"Base64 invalido: "+str(e)}); return
        if len(raw_bytes) > UPLOADS_MAX_BYTES:
            self._send(400,{"ok":False,"error":"Archivo demasiado grande (max 5 MB)"}); return
        # nombre seguro
        import re as _re
        base = _re.sub(r"[^a-zA-Z0-9._-]", "_", os.path.basename(name or "upload"))
        if not base or base.startswith("."): base = "upload" + UPLOADS_ALLOWED[mime]
        ext = os.path.splitext(base)[1].lower()
        if ext != UPLOADS_ALLOWED[mime]:
            base = os.path.splitext(base)[0] + UPLOADS_ALLOWED[mime]
        # prefijo timestamp-random
        fname = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8] + "-" + base
        full = os.path.join(UPLOADS_DIR, fname)
        with open(full, "wb") as fh: fh.write(raw_bytes)
        self._send(200,{"ok":True,"url":"/uploads/"+fname,"name":base,"size":len(raw_bytes),"mime":mime})


def _apply_img_attrs(html, selector, url, alt):
    """Reemplaza solo los atributos src y alt de un <img> seleccionado. Conserva el resto."""
    pattern, ctx = _selector_to_pattern(selector)
    if not pattern: return html, "Selector invalido: "+selector, False
    m = re.search(pattern, html, re.IGNORECASE)
    if not m: return html, "No se encontro el elemento '"+selector+"'", False
    start, end = m.span()
    tag_text = m.group(0)
    # reemplazar src
    new_tag = re.sub(r'src\s*=\s*"[^"]*"', 'src="'+url.replace('"','%22')+'"', tag_text, count=1)
    if 'src=' not in new_tag:
        new_tag = new_tag[:-1] + ' src="'+url.replace('"','%22')+'">'
    # reemplazar alt
    new_tag = re.sub(r'alt\s*=\s*"[^"]*"', 'alt="'+alt.replace('"','&quot;')+'"', new_tag, count=1)
    if 'alt=' not in new_tag:
        new_tag = new_tag[:-1] + ' alt="'+alt.replace('"','&quot;')+'">'
    return html[:start] + new_tag + html[end:], "Atributos src/alt actualizados.", True


def _build_element_system_prompt(action, tag, selector):
    """Genera el system prompt segun accion + tipo de elemento."""
    base = (
        "Eres un asistente de edicion web. Tu trabajo es generar el contenido NUEVO "
        "para un elemento HTML concreto de una pagina estatica, segun la peticion del usuario. "
        "Responde EXCLUSIVAMENTE con el fragmento que debera ir en el campo de edicion. "
        "Sin explicaciones, sin markdown, sin ```html```.\n\n"
    )
    if action == "edit":
        base += (
            "El usuario quiere REESCRIBIR el texto/contenido de un elemento <"+ (tag or "div") +">. "
            "Devuelve SOLO el texto o HTML interno que reemplazara al actual. "
            "Mantener longitud similar. No envolver en el tag exterior."
        )
    elif action == "change":
        base += (
            "El usuario quiere REEMPLAZAR el elemento <"+ (tag or "div") +"> por otro distinto. "
            "Devuelve el HTML COMPLETO del nuevo elemento, listo para sustituir al original. "
            "Estetica dark-glass coherente: usa #7c5cff (acento), #21d4fd (acento-2), fondo translucido."
        )
    elif action == "add":
        base += (
            "El usuario quiere AÑADIR contenido nuevo justo despues del elemento <"+ (tag or "div") +">. "
            "Devuelve un bloque HTML completo que se insertara a continuacion. "
            "Estetica dark-glass coherente con el sitio."
        )
    elif action == "delete":
        base += (
            "El usuario quiere confirmar la eliminacion. Responde un JSON vacio o el texto 'OK'."
        )
    return base


# ═══════ LISTA DE ELEMENTOS EDITABLES (Modo Desarrollador) ═══════
# Tags que consideramos editables en el contexto del sitio.
EDITABLE_TAGS = {
    "h1","h2","h3","h4","h5","h6",
    "p","span","li","a","button","img",
    "section","article","header","footer","nav","main",
    "div","figure","figcaption","label","small","strong","em"
}

def _build_selector_from_tag(tag, classes, eid):
    s = tag
    if eid: s += "#" + eid
    for cl in classes[:4]:
        s += "." + cl
    return s

def list_editable_elements(html):
    """Recorre el HTML y devuelve una lista de elementos editables con un id incremental.
    Estrategia: encontrar cada tag, filtrar por los de EDITABLE_TAGS, capturar tag/clases/id/texto.
    Excluye elementos dentro de <script>, <style> y los que pertenezcan al widget (clase hms-*)."""
    out = []
    seen = set()      # para no duplicar el mismo nodo si lo matcheamos dos veces
    # Eliminar bloques <script> y <style> del analisis
    clean = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
    clean = re.sub(r'<style\b[^>]*>.*?</style>',  '', clean, flags=re.IGNORECASE|re.DOTALL)

    # Regex para encontrar apertura de cualquier tag (no self-closing)
    tag_re = re.compile(r'<([a-zA-Z][\w-]*)(\s[^>]*?)?>', re.IGNORECASE)
    eid_re  = re.compile(r'\bid\s*=\s*"([^"]+)"', re.IGNORECASE)
    cls_re  = re.compile(r'\bclass\s*=\s*"([^"]+)"', re.IGNORECASE)

    counter = 0
    for m in tag_re.finditer(clean):
        tag = m.group(1).lower()
        if tag not in EDITABLE_TAGS: continue
        attrs = m.group(2) or ""
        # Excluir elementos del widget
        if 'hms-' in attrs: continue
        eid_m  = eid_re.search(attrs)
        eid    = eid_m.group(1) if eid_m else ""
        cls_m  = cls_re.search(attrs)
        classes= cls_m.group(1).split() if cls_m else []
        # si todas las clases son del widget, saltar
        if classes and all(c.startswith('hms-') for c in classes): continue

        # Key unica para no repetir
        key = (tag, eid, tuple(classes))
        if key in seen: continue
        seen.add(key)

        # Extraer el texto interno: tomar hasta el primer '<' que no sea cierre
        start = m.end()
        depth = 1
        i = start
        inner_parts = []
        while i < len(clean) and depth > 0:
            o = clean.find("<", i)
            if o == -1: break
            # texto entre i y o
            inner_parts.append(clean[i:o])
            # que tag es?
            mm = re.match(r'</?([a-zA-Z][\w-]*)', clean[o:])
            if not mm: break
            this_tag = mm.group(1).lower()
            if clean[o+1] == "/":
                if this_tag == tag:
                    depth -= 1
                    if depth == 0: break
                i = clean.find(">", o) + 1
            else:
                if this_tag == tag:
                    depth += 1
                i = clean.find(">", o) + 1

        inner_html = "".join(inner_parts)
        text = re.sub(r'<[^>]+>', ' ', inner_html)
        text = re.sub(r'\s+', ' ', text).strip()
        # recorta el texto y la preview
        text_short = text[:120]
        outer_html = m.group(0) + inner_html[:80] + ("..." if len(inner_html) > 80 else "")
        outer_html = re.sub(r'\s+', ' ', outer_html)[:200]

        counter += 1
        out.append({
            "id": counter,
            "tag": tag,
            "selector": _build_selector_from_tag(tag, classes, eid),
            "classes": classes,
            "id_attr": eid,
            "text": text_short,
            "has_text": bool(text),
            "preview": outer_html
        })
        if counter >= 100: break

    return out

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), H) as s:
        print("Hermes Studio en http://localhost:%d  (Ctrl+C para parar)" % PORT)
        s.serve_forever()
