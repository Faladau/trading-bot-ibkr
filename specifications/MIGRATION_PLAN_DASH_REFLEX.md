# Plan de Migrare: Streamlit → Dash/Plotly sau Reflex.dev

## 🎯 Context

**Motiv migrare:**
- Deployment pe server propriu (nu Streamlit Cloud)
- Nevoie de tehnologie mai stabilă și flexibilă
- Control complet asupra deployment-ului

---

## 📊 Comparație: Dash/Plotly vs Reflex.dev

### **Dash/Plotly** ⭐⭐⭐⭐⭐ (RECOMANDAT)

**Avantaje:**
- ✅ **Matur și stabil** - există din 2017, foarte stabil
- ✅ **Plotly nativ** - cele mai bune grafice pentru trading
- ✅ **Deployment flexibil** - orice server (Docker, VPS, cloud)
- ✅ **Comunitate mare** - multe resurse, tutoriale, exemple
- ✅ **Python pur** - fără JavaScript necesar
- ✅ **Production-ready** - folosit în enterprise
- ✅ **Customizare completă** - control total asupra UI
- ✅ **WebSocket support** - pentru real-time updates

**Dezavantaje:**
- ❌ **Curba de învățare** - mai complex decât Streamlit
- ❌ **Mai mult cod** - trebuie să scrii mai mult pentru UI

**Deployment:**
```bash
# Simplu cu Gunicorn
gunicorn app:server --bind 0.0.0.0:8050

# Sau cu Docker
docker run -p 8050:8050 trading-bot-dash
```

---

### **Reflex.dev** ⭐⭐⭐⭐

**Avantaje:**
- ✅ **Modern 2026** - tehnologie nouă, design modern
- ✅ **Full-stack Python** - frontend + backend integrat
- ✅ **Plotly nativ** - grafice excelente
- ✅ **State reactiv** - WebSocket built-in
- ✅ **Componente moderne** - UI modern out-of-the-box

**Dezavantaje:**
- ❌ **Framework nou** - API instabil, breaking changes posibile
- ❌ **Comunitate mică** - mai puține resurse
- ❌ **Deployment mai complex** - necesită backend + frontend build

**Deployment:**
```bash
# Build frontend
reflex export

# Run backend
reflex run --backend-only
```

---

## 🎯 Recomandarea Mea: **Dash/Plotly**

### **De ce Dash/Plotly:**

1. **Matur și stabil** - perfect pentru production
2. **Plotly nativ** - grafice excelente pentru trading
3. **Deployment simplu** - Gunicorn + Nginx, sau Docker
4. **Flexibil** - poți adăuga orice feature vrei
5. **Comunitate mare** - multe exemple trading dashboards
6. **Production-ready** - folosit în enterprise

### **Structură propusă:**
```
src/ui/
├── dash_app.py          # Main Dash app
├── components/          # Componente Dash
│   ├── metrics.py
│   ├── charts.py
│   └── watchlist.py
├── static/
│   ├── css/
│   └── assets/
└── callbacks/           # Callbacks pentru interactivitate
    ├── metrics.py
    └── data.py
```

---

## 📋 Plan de Migrare

### **Faza 1: Setup Dash (1-2 ore)**
1. Instalează Dash: `pip install dash plotly`
2. Creează `src/ui/dash_app.py` - structură de bază
3. Migrează componentele existente (metrics, watchlist)
4. Testează local

### **Faza 2: Migrare Componente (2-3 ore)**
1. Migrează metrici → Dash components
2. Migrează watchlist → Dash DataTable
3. Migrează grafice → Plotly charts (deja compatibile!)
4. Migrează CSS → Dash assets

### **Faza 3: Deployment (1-2 ore)**
1. Configurează Gunicorn
2. Setup Nginx reverse proxy
3. Docker (opțional)
4. Testează pe server

### **Faza 4: Features Avansate (opțional)**
1. WebSocket pentru real-time updates
2. Multi-user support
3. Autentificare
4. Export PDF/CSV

---

## 🔧 Exemplu Cod Dash

```python
# src/ui/dash_app.py
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Trading Bot Dashboard"),
    dcc.Graph(id='equity-curve'),
    html.Div(id='metrics'),
    dcc.Interval(id='interval', interval=60000)  # Update la 60s
])

@app.callback(
    Output('equity-curve', 'figure'),
    Input('interval', 'n_intervals')
)
def update_chart(n):
    # Logica pentru equity curve
    fig = go.Figure(...)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
```

---

## 🚀 Deployment pe Server

### **Opțiunea 1: Gunicorn + Nginx**
```bash
# Gunicorn
gunicorn src.ui.dash_app:server --bind 0.0.0.0:8050 --workers 4

# Nginx config
server {
    listen 80;
    server_name trading-bot.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
    }
}
```

### **Opțiunea 2: Docker**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "src.ui.dash_app:server", "--bind", "0.0.0.0:8050"]
```

### **Opțiunea 3: Systemd Service**
```ini
[Unit]
Description=Trading Bot Dashboard
After=network.target

[Service]
User=trader
WorkingDirectory=/opt/trading-bot
ExecStart=/opt/trading-bot/venv/bin/gunicorn src.ui.dash_app:server --bind 0.0.0.0:8050
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## ✅ Avantaje Migrare la Dash

1. **Control complet** - deployment pe orice server
2. **Stabil** - framework matur, fără breaking changes
3. **Flexibil** - poți adăuga orice feature
4. **Production-ready** - folosit în enterprise
5. **Plotly nativ** - grafice excelente
6. **WebSocket** - pentru real-time updates (dacă e nevoie)

---

## 📝 Next Steps

1. **Decizie:** Dash/Plotly sau Reflex.dev?
2. **Dacă Dash:** Încep migrarea componentelor
3. **Dacă Reflex:** Creez proof-of-concept
4. **Deployment:** Setup server după migrare

---

**Document creat:** 2026-01-17  
**Status:** PROPOSAL - Așteptăm decizie pentru migrare
