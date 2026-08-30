# Instalación en VPS — Hermes Chatbot Studio

Este documento explica cómo desplegar **Hermes Chatbot Studio** en un VPS (Ubuntu/Debian/Alpine) usando Python 3.10+.

---

## 1. Requisitos previos

| Requisito | Versión mínima |
|---|---|
| Python | 3.10 |
| pip | 22+ |
| make (opcional) | — |

> **Nota**: El proyecto **no requiere dependencias externas** (solo librería estándar de Python).

---

## 2. Despliegue rápido (script único)

```bash
# 1. Descargar y descomprimir
cd /opt
sudo wget -qO hermes-chatbot-studio.zip "https://TU_URL/hermes-chatbot-studio.zip"
sudo unzip -q hermes-chatbot-studio.zip
cd hermes-chatbot-studio

# 2. (Opcional) Configurar variables de entorno para IA real
export HERMES_PROXY_URL="https://openrouter.ai/api/v1/chat/completions"
export HERMES_PROXY_KEY="sk-or-v1-..."
export HERMES_MODEL="anthropic/claude-3.5-sonnet"
export PORT=8080

# 3. Arrancar
python3 studio.py
```

El servidor escucha en `0.0.0.0:8080`. Abre `http://TU_IP:8080/`.

---

## 3. Despliegue en producción (systemd + nginx)

### 3.1. Usuario y directorio

```bash
sudo useradd -r -s /bin/false hermes
sudo mkdir -p /opt/hermes-chatbot-studio
sudo unzip -q /ruta/a/hermes-chatbot-studio.zip -d /opt/hermes-chatbot-studio
sudo chown -R hermes:hermes /opt/hermes-chatbot-studio
```

### 3.2. Variables de entorno (`.env`)

```bash
sudo -u hermes tee /opt/hermes-chatbot-studio/.env <<'EOF'
# --- Puerto interno (nginx hará proxy a este puerto) ---
PORT=8080

# --- Configuración IA (opcional; si no, usa generador local) ---
HERMES_PROXY_URL=https://openrouter.ai/api/v1/chat/completions
HERMES_PROXY_KEY=sk-or-v1-TU_API_KEY
HERMES_MODEL=anthropic/claude-3.5-sonnet

# Opcional: proveedor Gemini
# HERMES_PROXY_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
# HERMES_PROXY_KEY=AIza...
# HERMES_MODEL=gemini-2.5-pro
EOF
sudo chmod 600 /opt/hermes-chatbot-studio/.env
```

### 3.3. Servicio systemd

```bash
sudo tee /etc/systemd/system/hermes-studio.service <<'EOF'
[Unit]
Description=Hermes Chatbot Studio
After=network.target

[Service]
Type=simple
User=hermes
Group=hermes
WorkingDirectory=/opt/hermes-chatbot-studio
EnvironmentFile=/opt/hermes-chatbot-studio/.env
ExecStart=/usr/bin/python3 studio.py
Restart=on-failure
RestartSec=3
StandardOutput=journal
StandardError=journal
# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hermes-studio
sudo systemctl status hermes-studio
```

### 3.4. Nginx como reverse proxy (HTTPS con Let's Encrypt)

```bash
sudo apt-get update && sudo apt-get install -y nginx certbot python3-certbot-nginx
```

```nginx
# /etc/nginx/sites-available/hermes-studio
server {
    listen 80;
    server_name estudio.tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # WebSocket no se usa, pero por si acaso:
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 90s;
        proxy_send_timeout 90s;
    }

    # Assets estáticos: servir directo con cache
    location /assets/ {
        alias /opt/hermes-chatbot-studio/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/hermes-studio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Certificado HTTPS
sudo certbot --nginx -d estudio.tudominio.com --non-interactive --agree-tos -m tu@email.com
```

---

## 4. Configuración del Bot de Hermes (opcional)

Para que el chatbot use **Hermes real** en lugar del generador local:

1. Instala Hermes en el VPS (o en tu máquina local):
   ```bash
   pip install hermes-ai
   ```
2. Crea el perfil:
   ```bash
   hermes profile create site-studio --clone-from default
   # Edita ~/.hermes/profiles/site-studio/SOUL.md con el contenido de bot/SOUL.md
   ```
3. Levanta el proxy OpenAI-compatible:
   ```bash
   hermes proxy  # escucha en 0.0.0.0:8000
   ```
4. En el `.env` del VPS:
   ```bash
   HERMES_PROXY_URL=http://127.0.0.1:8000/v1/chat/completions
   HERMES_PROXY_KEY=hermes
   HERMES_MODEL=site-studio
   ```
5. Reinicia:
   ```bash
   sudo systemctl restart hermes-studio
   ```

## 4.5. Configuracion de imagenes (opcional)

Las imagenes funcionan SIN configurar nada (genera SVG placeholders). Para usar bancos reales o DALL-E, anade al `.env`:

```bash
# --- Buscadores (al menos 1 recomendado) ---
UNSPLASH_ACCESS_KEY=...        # https://unsplash.com/developers
PEXELS_API_KEY=...             # https://www.pexels.com/api/
PIXABAY_API_KEY=...            # https://pixabay.com/api/docs/

# --- Generadores IA (opcional) ---
OPENAI_API_KEY=sk-...          # para DALL-E 3
STABILITY_API_KEY=sk-...       # para Stable Diffusion
```

Y reinicia:
```bash
sudo systemctl restart hermes-studio
```

El icono de imagen del chat (6° boton) abre el panel con 3 tabs:
- **Buscar** (Unsplash/Pexels/Pixabay)
- **Generar con IA** (DALL-E 3 / Stable Diffusion / placeholder SVG)
- **Subir** (archivo local, max 5 MB, queda en `/uploads/`)

---

## 5. Actualizaciones

```bash
cd /opt/hermes-chatbot-studio
sudo -u hermes git pull  # si usas git, o descarga nuevo ZIP
sudo systemctl restart hermes-studio
```

---

## 6. Puertos y firewall

| Puerto | Uso |
|---|---|
| 80/443 | Nginx (HTTPS público) |
| 8080 | Python interno (solo localhost, no exponer) |
| 8000 | Hermes proxy (solo localhost, si se usa) |

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 7. Logs y depuración

```bash
# Logs del servicio
sudo journalctl -u hermes-studio -f

# Logs de nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Test rápido
curl -X POST http://127.0.0.1:8080/api/elements -H "Content-Type: application/json" -d '{"page":"home"}'
```

---

## 8. Estructura de archivos en el VPS

```
/opt/hermes-chatbot-studio/
├── studio.py               # Servidor Python
├── index.html              # Home
├── about/index.html        # Acerca de
├── services/index.html     # Servicios
├── assets/
│   ├── widget.js           # Chatbot + Modo Desarrollador
│   └── widget.css          # Temas dark-glass
├── bot/
│   └── SOUL.md             # Persona del bot
├── README.md
└── .env                    # Variables de entorno (NO commitear)
```

---

## 9. Solución de problemas comunes

| Problema | Solución |
|---|---|
| `Address already in use` | `sudo lsof -ti:8080 | xargs kill -9` y reinicia |
| Chat no conecta | Verifica que nginx pasa `X-Forwarded-Proto` y `Host` |
| IA no responde | Revisa `HERMES_PROXY_URL` y `HERMES_PROXY_KEY` en `.env`; `journalctl -u hermes-studio` |
| Assets 404 | Comprueba `location /assets/` en nginx y que la carpeta existe |
| Permisos | `sudo chown -R hermes:hermes /opt/hermes-chatbot-studio` |

---

## 10. Backup automático (cron)

```bash
sudo -u hermes crontab -e
# Añadir:
0 3 * * * tar -czf /opt/hermes-backups/hermes-$(date +\%F).tar.gz -C /opt/hermes-chatbot-studio . --exclude='*.bak' 2>/dev/null
```

---

**¡Listo!** Tu Hermes Chatbot Studio estará corriendo en `https://estudio.tudominio.com/` con chatbot flotante, modo desarrollador multi-elemento y soporte IA real.