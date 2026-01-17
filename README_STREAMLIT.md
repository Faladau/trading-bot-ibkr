# Trading Bot Dashboard - Streamlit Cloud Deployment

## 🚀 Deploy pe Streamlit Cloud (GRATUIT)

### Pasul 1: Pregătire Repository

1. **Asigură-te că ai push-at tot pe GitHub:**
   ```bash
   git add .
   git commit -m "feat: add Streamlit dashboard"
   git push
   ```

2. **Verifică că ai următoarele fișiere:**
   - ✅ `app.py` (entry point)
   - ✅ `requirements.txt` (cu streamlit)
   - ✅ `.streamlit/config.toml` (configurație)
   - ✅ `src/ui/dashboard.py` (dashboard)

### Pasul 2: Streamlit Cloud Setup

1. **Creează cont pe [Streamlit Cloud](https://streamlit.io/cloud)**
   - Merge cu cont GitHub
   - GRATUIT pentru proiecte publice

2. **Deploy:**
   - Click "New app"
   - Selectează repository-ul tău: `Faladau/trading-bot-ibkr`
   - Branch: `feature/models` (sau `main`)
   - Main file path: `app.py`
   - Click "Deploy"

3. **Configurare Secrets (opțional):**
   - În Streamlit Cloud → Settings → Secrets
   - Adaugă variabile dacă ai nevoie (IBKR credentials, etc.)

### Pasul 3: Acces Dashboard

- Streamlit Cloud va genera un URL: `https://your-app.streamlit.app`
- Dashboard-ul va fi accesibil de pe telefon (responsive)
- Auto-refresh la fiecare 5 secunde când bot-ul rulează

---

## 📱 Responsive Design

Dashboard-ul este optimizat pentru:
- ✅ Desktop (wide layout)
- ✅ Tablet (adaptive columns)
- ✅ Mobile (stacked layout, full-width buttons)

---

## 🔧 Configurare Locală

### Rulează local:

```bash
# Instalează dependențe
pip install -r requirements.txt

# Rulează dashboard
streamlit run app.py
```

Dashboard-ul va rula pe: `http://localhost:8501`

---

## 📊 Funcționalități Dashboard

1. **Status Agenți** - Status live pentru Agent 1, 2, 3
2. **Live Market Data** - Prețuri curente pentru simboluri
3. **Performance Metrics** - PnL, Win Rate, Sharpe Ratio
4. **Controls** - Start/Stop/Pause/Reset bot
5. **Activity Logs** - Logs recente din agenți

---

## ⚠️ Note Importante

- **Secrets**: Nu commit `.streamlit/secrets.toml` (e în .gitignore)
- **Config**: Dashboard-ul citește din `config/config.yaml`
- **Data**: Asigură-te că `data/` folder există și are date
- **Auto-refresh**: Dashboard-ul se actualizează automat când bot-ul rulează

---

## 🐛 Troubleshooting

### Dashboard nu se încarcă:
- Verifică că `app.py` există în root
- Verifică că `requirements.txt` are `streamlit>=1.28.1`
- Verifică logs în Streamlit Cloud

### Nu apar date:
- Verifică că Agent 1 a generat CSV-uri în `data/processed/`
- Verifică că `config.yaml` are simboluri configurate

### Eroare la import:
- Verifică că toate modulele sunt în `src/`
- Verifică că `__init__.py` există în fiecare folder

---

**Status**: ✅ Ready for Streamlit Cloud Deployment
