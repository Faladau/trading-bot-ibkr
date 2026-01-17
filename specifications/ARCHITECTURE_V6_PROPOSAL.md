# Propunere Arhitectură v6.0 - Agenți în Foldere Separate

## 🎯 Concept

Fiecare agent are propriul folder cu tot ce ține de el, inclusiv testele. Modulele comune rămân în foldere comune.

## 📐 Structură Propusă

```
trading_bot/
│
├── config/
│   ├── config.yaml
│   ├── strategy_params.yaml
│   └── risk_params.yaml
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point - orchestrator
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   │
│   │   ├── data_collection/     # 🆕 Data Collection Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # Implementare Data Collection Agent
│   │   │   └── config.py        # Config specific (dacă e nevoie)
│   │   │
│   │   ├── decision/            # 🆕 Decision Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # Implementare Decision Agent
│   │   │   └── config.py
│   │   │
│   │   └── execution/           # 🆕 Execution Agent
│   │       ├── __init__.py
│   │       ├── agent.py         # Implementare Execution Agent
│   │       └── config.py
│   │
│   ├── common/                  # 🆕 Module comune (folosite de mai mulți agenți)
│   │   ├── __init__.py
│   │   │
│   │   ├── broker/              # Folosit de Agent 1 și 3
│   │   │   ├── __init__.py
│   │   │   ├── ibkr_connector.py
│   │   │   ├── data_provider.py
│   │   │   └── execution.py
│   │   │
│   │   ├── strategy/            # Folosit de Agent 2
│   │   │   ├── __init__.py
│   │   │   ├── technical_analysis.py
│   │   │   ├── signal_generator.py
│   │   │   └── filters.py
│   │   │
│   │   ├── risk/                # Folosit de Agent 3
│   │   │   ├── __init__.py
│   │   │   ├── risk_manager.py
│   │   │   └── position_sizing.py
│   │   │
│   │   ├── models/              # Folosit de TOȚI agenții
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py
│   │   │   ├── signal.py
│   │   │   └── trade.py
│   │   │
│   │   ├── logging_utils/       # Folosit de TOȚI
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   │
│   │   └── utils/               # Folosit de TOȚI
│   │       ├── __init__.py
│   │       ├── config_loader.py
│   │       ├── helpers.py
│   │       └── validators.py
│   │
│   ├── services/                # Orchestrează agenții
│   │   ├── __init__.py
│   │   └── trading_service.py
│   │
│   ├── backtest/                # Backtesting
│   │   ├── __init__.py
│   │   ├── backtester.py
│   │   └── metrics.py
│   │
│   └── storage/                 # Persistență (opțional)
│       ├── __init__.py
│       └── repository.py
│
├── tests/
│   ├── __init__.py
│   │
│   ├── data_collection/         # 🆕 Teste Data Collection Agent
│   │   ├── __init__.py
│   │   ├── test_data_collection_agent.py
│   │   └── test_data_provider.py
│   │
│   ├── decision/                # 🆕 Teste Decision Agent
│   │   ├── __init__.py
│   │   ├── test_decision_agent.py
│   │   ├── test_technical_analysis.py
│   │   └── test_signal_generator.py
│   │
│   ├── execution/               # 🆕 Teste Execution Agent
│   │   ├── __init__.py
│   │   ├── test_execution_agent.py
│   │   ├── test_risk_manager.py
│   │   └── test_position_sizing.py
│   │
│   ├── common/                  # 🆕 Teste module comune
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_config_loader.py
│   │   ├── test_helpers.py
│   │   ├── test_validators.py
│   │   └── test_logger.py
│   │
│   └── integration/             # 🆕 Teste integrare
│       ├── __init__.py
│       └── test_agent_communication.py
│
├── data/
│   ├── historical/              # Date istorice (CSV, JSON)
│   ├── signals/                 # Semnale generate (JSON)
│   ├── trades/                  # Trade-uri completate (JSON)
│   ├── backtests/               # Rezultate backtests
│   └── logs/                    # Log-uri
│
├── requirements.txt
├── README.md
└── .env
```

---

## ✅ Avantaje Structură Nouă

1. **Izolare completă** - Fiecare agent e în propriul folder
2. **Teste organizate** - Testele sunt lângă agentul lor
3. **Claritate** - Știi exact unde să cauți ceva
4. **Scalabilitate** - Adaugi agenți noi fără să afectezi alții
5. **Module comune** - Evită duplicarea codului

---

## 🔄 Migrare de la Structura Veche

### Ce mutăm:

1. **Data Collection Agent:**
   - `src/agents/data_collection_agent.py` → `src/agents/data_collection/agent.py`
   - Teste → `tests/data_collection/`

2. **Decision Agent:**
   - `src/agents/decision_agent.py` → `src/agents/decision/agent.py`
   - Teste → `tests/decision/`

3. **Execution Agent:**
   - `src/agents/execution_agent.py` → `src/agents/execution/agent.py`
   - Teste → `tests/execution/`

4. **Module comune:**
   - `src/broker/` → `src/common/broker/`
   - `src/strategy/` → `src/common/strategy/`
   - `src/risk/` → `src/common/risk/`
   - `src/models/` → `src/common/models/`
   - `src/logging_utils/` → `src/common/logging_utils/`
   - `src/utils/` → `src/common/utils/`

5. **Teste comune:**
   - `tests/test_models.py` → `tests/common/test_models.py`
   - `tests/test_config_loader.py` → `tests/common/test_config_loader.py`
   - etc.

---

## 📝 Import-uri Actualizate

### Înainte:
```python
from src.broker.data_provider import DataProvider
from src.models import Bar
```

### După:
```python
from src.common.broker.data_provider import DataProvider
from src.common.models import Bar
```

### Import agenți:
```python
# Data Collection Agent
from src.agents.data_collection.agent import DataCollectionAgent

# Decision Agent
from src.agents.decision.agent import DecisionAgent

# Execution Agent
from src.agents.execution.agent import ExecutionAgent
```

---

## 🎯 Recomandare

**Structura propusă este excelentă pentru:**
- ✅ Organizare clară
- ✅ Testare izolată
- ✅ Mentenanță ușoară
- ✅ Scalabilitate

**Vrei să implementăm această structură?**
