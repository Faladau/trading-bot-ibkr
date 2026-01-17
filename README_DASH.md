# Dash Dashboard - Trading Bot v6.2

## 🚀 Rulare Locală

```bash
# Instalează dependențele
pip install -r requirements.txt

# Rulează Dash app
python run_dash.py
```

Dashboard-ul va fi disponibil la: `http://localhost:8050`

---

## 🖥️ Deployment pe Server

### Opțiunea 1: Gunicorn (Recomandat)

```bash
# Instalează gunicorn
pip install gunicorn

# Rulează cu Gunicorn
gunicorn src.ui.dash_app:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120
```

### Opțiunea 2: Systemd Service

Creează `/etc/systemd/system/trading-bot-dash.service`:

```ini
[Unit]
Description=Trading Bot Dashboard
After=network.target

[Service]
User=trader
WorkingDirectory=/opt/trading-bot
Environment="PATH=/opt/trading-bot/venv/bin"
ExecStart=/opt/trading-bot/venv/bin/gunicorn src.ui.dash_app:server --bind 0.0.0.0:8050 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Apoi:
```bash
sudo systemctl enable trading-bot-dash
sudo systemctl start trading-bot-dash
```

### Opțiunea 3: Docker

Creează `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["gunicorn", "src.ui.dash_app:server", "--bind", "0.0.0.0:8050", "--workers", "4"]
```

Build și run:
```bash
docker build -t trading-bot-dash .
docker run -p 8050:8050 trading-bot-dash
```

---

## 🔧 Configurare Nginx (Opțional)

Pentru HTTPS și reverse proxy:

```nginx
server {
    listen 80;
    server_name trading-bot.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Structură Dash

```
src/ui/
├── dash_app.py              # Main Dash app
├── components/
│   └── dash_components.py   # Componente Dash
├── callbacks/
│   └── dashboard_callbacks.py  # Callbacks pentru interactivitate
├── utils/
│   └── data_loader.py       # Funcții pentru date
└── static/
    └── css/
        └── dashboard.css    # CSS (folosit și de Dash)
```

---

## ✅ Avantaje Dash

- ✅ **Matur și stabil** - framework production-ready
- ✅ **Plotly nativ** - grafice excelente
- ✅ **Deployment flexibil** - orice server
- ✅ **Control complet** - customizare totală
- ✅ **Performance** - updates parțiale, nu re-execută tot

---

**Status:** READY FOR DEPLOYMENT
