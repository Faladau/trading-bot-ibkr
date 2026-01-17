# Structură Proiect - Trading Bot v6.0

## 📐 Organizare pe Agenți

Fiecare agent are propriul folder cu tot ce ține de el, inclusiv testele. Modulele comune rămân în `src/common/`.

---

## 📁 Structură Completă

```
trading_bot/
│
├── config/                       # Configurații YAML
│   ├── config.yaml
│   ├── strategy_params.yaml
│   └── risk_params.yaml
│
├── src/
│   ├── main.py                  # Entry point
│   │
│   ├── agents/                  # 🎯 AGENȚI (fiecare în folder separat)
│   │   ├── data_collection/     # Data Collection Agent
│   │   │   ├── __init__.py
│   │   │   └── agent.py
│   │   │
│   │   ├── decision/            # Decision Agent
│   │   │   ├── __init__.py
│   │   │   └── agent.py
│   │   │
│   │   └── execution/           # Execution Agent
│   │       ├── __init__.py
│   │       └── agent.py
│   │
│   ├── common/                  # 🔧 MODULE COMUNE
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
└── data/                        # Date persistate
    ├── historical/
    ├── signals/
    ├── trades/
    └── logs/
```

---

## 🎯 Import-uri

### În agenți:
```python
# Data Collection Agent
from src.common.models.market_data import Bar
from src.common.broker.data_provider import DataProvider

# Decision Agent
from src.common.models.signal import Signal
from src.common.strategy.technical_analysis import calculate_ema

# Execution Agent
from src.common.models.trade import Order
from src.common.risk.risk_manager import RiskManager
```

### În teste:
```python
# Teste Data Collection Agent
from src.agents.data_collection.agent import DataCollectionAgent
from src.common.models.market_data import Bar

# Teste comune
from src.common.models import Bar, Signal, Trade
from src.common.utils.config_loader import load_config
```

---

## ✅ Avantaje

1. **Izolare completă** - Fiecare agent e în propriul folder
2. **Teste organizate** - Testele sunt lângă agentul lor
3. **Claritate** - Știi exact unde să cauți ceva
4. **Scalabilitate** - Adaugi agenți noi fără să afectezi alții
5. **Module comune** - Evită duplicarea codului

---

## 📝 Note

- **Data Collection Agent** folosește: `common/broker`, `common/models`, `common/utils`, `common/logging_utils`
- **Decision Agent** folosește: `common/strategy`, `common/models`, `common/utils`, `common/logging_utils`
- **Execution Agent** folosește: `common/broker`, `common/risk`, `common/models`, `common/utils`, `common/logging_utils`
