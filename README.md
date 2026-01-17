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

Arhitectură modulară pe agenți separați. Vezi [STRUCTURE.md](STRUCTURE.md) și [ARCHITECTURE.md](ARCHITECTURE.md) pentru detalii complete.

```
trading_bot/
│
├── config/                       # Configurație (YAML)
│   ├── config.yaml
│   ├── strategy_params.yaml
│   └── risk_params.yaml
│
├── src/
│   ├── main.py                  # Entry point - orchestrator
│   │
│   ├── agents/                  # 🎯 Agenți (fiecare în folder separat)
│   │   ├── data_collection/     # Data Collection Agent
│   │   ├── decision/            # Decision Agent
│   │   └── execution/           # Execution Agent
│   │
│   ├── common/                  # 🔧 Module comune
│   │   ├── broker/              # IBKR connection & data
│   │   ├── strategy/            # Technical analysis
│   │   ├── risk/                # Risk management
│   │   ├── models/              # Data models (Bar, Signal, Trade)
│   │   ├── logging_utils/       # Logging
│   │   └── utils/               # Helpers, validators, config
│   │
│   ├── services/                # Orchestration
│   ├── backtest/                # Backtesting
│   └── storage/                 # Persistence
│
├── tests/
│   ├── data_collection/         # 🧪 Teste Data Collection Agent
│   ├── decision/                # 🧪 Teste Decision Agent
│   ├── execution/               # 🧪 Teste Execution Agent
│   ├── common/                  # 🧪 Teste module comune
│   └── integration/             # 🧪 Teste integrare
│
├── data/
│   ├── historical/              # Date istorice (CSV)
│   ├── signals/                 # Semnale generate (JSON)
│   ├── trades/                  # Trade-uri completate (JSON)
│   └── logs/                    # Log-uri
│
├── requirements.txt             # Dependențe Python
└── README.md                    # Acest fișier
```

### 🎯 Principii de Design
- **Separarea responsabilităților** - Fiecare modul are scop clar
- **Dependency Injection** - Comunicare prin interfețe
- **DRY** - Cod comun în `utils/` sau clase de bază
- **Testabilitate** - Module independente, mock-uibile

---

## 🔧 Tehnologii

- **Python**: 3.12+
- **Broker API**: Interactive Brokers (ib-insync)
- **Date**: pandas, numpy
- **Indicatori**: pandas_ta
- **Config**: pyyaml, python-dotenv

---

## 📖 Specificație

Vezi `specifications/Specificatie_Trading_Bot_v6.0.md` pentru documentația completă (versiunea actuală).

---

## ⚠️ Important

- **NU commit** fișierul `.env` (conține credențiale IBKR)
- Folosește cont **paper trading** pentru testare
- Testează bine înainte de trading live

---

## 📝 Licență

Proiect personal pentru trading automat.
