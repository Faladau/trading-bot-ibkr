# Plan de Migrare: Streamlit → Dash/Plotly

## 🎯 Motiv Migrare

- Deployment pe server propriu (nu Streamlit Cloud)
- Nevoie de tehnologie stabilă și flexibilă
- Control complet asupra deployment-ului
- Production-ready pentru trading bot

---

## 📊 De ce Dash/Plotly

### **Avantaje:**
- ✅ **Matur și stabil** - există din 2017, foarte stabil
- ✅ **Plotly nativ** - cele mai bune grafice pentru trading
- ✅ **Deployment flexibil** - orice server (Docker, VPS, cloud)
- ✅ **Comunitate mare** - multe resurse, tutoriale, exemple
- ✅ **Python pur** - fără JavaScript necesar
- ✅ **Production-ready** - folosit în enterprise
- ✅ **Customizare completă** - control total asupra UI
- ✅ **WebSocket support** - pentru real-time updates (dacă e nevoie)

### **Structură propusă:**
```
src/ui/
├── dash_app.py          # Main Dash app
├── components/          # Componente Dash
│   ├── __init__.py
│   ├── metrics.py
│   ├── charts.py
│   ├── watchlist.py
│   └── agent_status.py
├── callbacks/           # Callbacks pentru interactivitate
│   ├── __init__.py
│   ├── metrics.py
│   └── data.py
└── static/
    ├── css/
    │   └── dashboard.css
    └── assets/
```

---

## 📋 Plan de Migrare (4 Faze)

### **Faza 1: Setup Dash (1-2 ore)**
- [ ] Instalează Dash: `pip install dash plotly gunicorn`
- [ ] Creează `src/ui/dash_app.py` - structură de bază
- [ ] Migrează CSS-ul existent
- [ ] Testează local

### **Faza 2: Migrare Componente (2-3 ore)**
- [ ] Migrează metrici → Dash components
- [ ] Migrează watchlist → Dash DataTable
- [ ] Migrează grafice → Plotly charts (deja compatibile!)
- [ ] Migrează agent status → Dash components

### **Faza 3: Callbacks & Interactivitate (1-2 ore)**
- [ ] Implementează callbacks pentru refresh
- [ ] Implementează callbacks pentru controls (START/STOP)
- [ ] Implementează auto-refresh cu dcc.Interval

### **Faza 4: Deployment (1-2 ore)**
- [ ] Configurează Gunicorn
- [ ] Setup Nginx reverse proxy (opțional)
- [ ] Docker (opțional)
- [ ] Systemd service (opțional)
- [ ] Testează pe server

---

## 🔧 Exemplu Structură Dash

```python
# src/ui/dash_app.py
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from src.ui.utils.data_loader import load_config, get_recent_trades, calculate_metrics
from src.ui.components.metrics import render_metrics_dash
from src.ui.components.watchlist import render_watchlist_dash

app = dash.Dash(__name__, external_stylesheets=['/static/css/dashboard.css'])

app.layout = html.Div([
    html.H1("Trading Bot v6.2 Dashboard"),
    dcc.Interval(id='interval', interval=60000),  # Update la 60s
    html.Div(id='metrics'),
    html.Div(id='watchlist'),
    dcc.Graph(id='equity-curve'),
])

@app.callback(
    [Output('metrics', 'children'),
     Output('watchlist', 'children'),
     Output('equity-curve', 'figure')],
    Input('interval', 'n_intervals')
)
def update_dashboard(n):
    trades = get_recent_trades()
    metrics = calculate_metrics(trades)
    # ... logica
    return metrics_html, watchlist_html, equity_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
```

---

## 🚀 Deployment pe Server

### **Opțiunea 1: Gunicorn (Recomandat)**
```bash
gunicorn src.ui.dash_app:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120
```

### **Opțiunea 2: Docker**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
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

## ✅ Avantaje Migrare

1. **Control complet** - deployment pe orice server
2. **Stabil** - framework matur, fără breaking changes
3. **Flexibil** - poți adăuga orice feature
4. **Production-ready** - folosit în enterprise
5. **Plotly nativ** - grafice excelente
6. **WebSocket** - pentru real-time updates (dacă e nevoie)

---

**Status:** READY TO START - Așteptăm confirmare pentru începerea migrării
