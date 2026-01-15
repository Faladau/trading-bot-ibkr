# Trading Bot AI cu Interactive Brokers

Sistem de trading automat, modular și scalabil, cu capital mic, care execută strategii simple și robuste, conectat la **Interactive Brokers (IBKR)** prin API.

## 📋 Status Setup

### ✅ Python
- **Versiune instalată**: Python 3.12.10
- **Versiune veche păstrată**: Python 3.9.0 (coexistă cu 3.12)
- **Launcher**: Folosește `py` sau `py -3.12` pentru Python 3.12
- **pip**: Funcțional pentru Python 3.12

### ✅ Git
- **Versiune**: Git 2.25.1
- **Configurare**:
  - Nume: Cipri
  - Email: ciprianfaladau@yahoo.com

### ⏳ Următorii pași
- [ ] Creare repository GitHub
- [ ] Push inițial pe GitHub
- [ ] Setup virtual environment (venv)
- [ ] Instalare dependențe (requirements.txt)
- [ ] Verificare acces Interactive Brokers (cont paper)

---

## 🚀 Quick Start (după setup complet)

```bash
# Clone repository
git clone https://github.com/USERNAME/trading-bot-ibkr.git
cd trading-bot-ibkr

# Creează virtual environment
py -3.12 -m venv trading_bot_env

# Activează virtual environment (Windows)
trading_bot_env\Scripts\activate

# Instalează dependențe
pip install -r requirements.txt

# Rulează bot (paper trading)
python src/main.py --mode paper --config config/config.yaml
```

---

## 📁 Structură Proiect

```
trading_bot/
│
├── config/
│   ├── config.yaml              # Configurație generală
│   ├── strategy_params.yaml      # Parametri strategie
│   └── risk_params.yaml          # Parametri risc
│
├── src/
│   ├── main.py                  # Entry point principal
│   ├── broker/                  # Conexiune IBKR
│   ├── strategy/                # Logică trading
│   ├── risk/                    # Management risc
│   ├── backtest/                # Backtesting
│   ├── logging_utils/           # Logging
│   └── utils/                   # Utilitare
│
├── data/
│   ├── historical/              # Date istorice
│   ├── backtests/               # Rezultate backtests
│   └── logs/                    # Log-uri
│
├── tests/                       # Teste
├── requirements.txt             # Dependențe Python
└── README.md                    # Acest fișier
```

---

## 🔧 Tehnologii

- **Python**: 3.12+
- **Broker API**: Interactive Brokers (ib-insync)
- **Date**: pandas, numpy
- **Indicatori**: pandas_ta
- **Config**: pyyaml, python-dotenv

---

## 📖 Specificație

Vezi `specifications/Specificatie_Trading_Bot_v5.1.md` pentru documentația completă.

---

## ⚠️ Important

- **NU commit** fișierul `.env` (conține credențiale IBKR)
- Folosește cont **paper trading** pentru testare
- Testează bine înainte de trading live

---

## 📝 Licență

Proiect personal pentru trading automat.
