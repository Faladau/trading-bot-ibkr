# 🚀 Quick Start - Trading Bot Dashboard

## Testare Locală

```bash
# Activează virtual environment
trading_bot_env\Scripts\activate

# Rulează dashboard
streamlit run app.py
```

Dashboard-ul va deschide automat în browser: `http://localhost:8501`

---

## 📱 Deploy pe Streamlit Cloud (GRATUIT)

### Pasul 1: Creează cont
1. Mergi pe [streamlit.io/cloud](https://streamlit.io/cloud)
2. Login cu GitHub
3. Autorizează accesul la repository

### Pasul 2: Deploy
1. Click **"New app"**
2. **Repository**: `Faladau/trading-bot-ibkr`
3. **Branch**: `feature/models` (sau `main`)
4. **Main file**: `app.py`
5. Click **"Deploy"**

### Pasul 3: Acces
- Streamlit Cloud va genera URL: `https://your-app.streamlit.app`
- Dashboard-ul va fi accesibil de pe telefon (responsive)
- Auto-refresh la fiecare 5 secunde

---

## ✅ Ce funcționează acum

- ✅ Status agenți (Agent 1, 2, 3)
- ✅ Live market data (din CSV-uri)
- ✅ Performance metrics (PnL, Win Rate)
- ✅ Controls (Start/Stop/Pause)
- ✅ Activity logs
- ✅ Responsive design (mobile + desktop)

---

## 📝 Note

- Dashboard-ul citește date din `data/processed/` (CSV-uri de la Agent 1)
- Pentru date live, rulează Agent 1 înainte
- Config se citește din `config/config.yaml`

---

**Status**: ✅ Ready for Streamlit Cloud!
