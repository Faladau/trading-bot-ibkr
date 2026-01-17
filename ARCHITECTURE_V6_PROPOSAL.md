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
│   │   ├── agent1/              # 🆕 Agent 1 - Data Collection
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # Implementare Agent 1
│   │   │   └── config.py        # Config specific (dacă e nevoie)
│   │   │
│   │   ├── agent2/              # 🆕 Agent 2 - Decision
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # Implementare Agent 2
│   │   │   └── config.py
│   │   │
│   │   └── agent3/              # 🆕 Agent 3 - Execution
│   │       ├── __init__.py
│   │       ├── agent.py         # Implementare Agent 3
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
│   ├── agent1/                  # 🆕 Teste Agent 1
│   │   ├── __init__.py
│   │   ├── test_data_collection_agent.py
│   │   └── test_data_provider.py
│   │
│   ├── agent2/                  # 🆕 Teste Agent 2
│   │   ├── __init__.py
│   │   ├── test_decision_agent.py
│   │   ├── test_technical_analysis.py
│   │   └── test_signal_generator.py
│   │
│   ├── agent3/                  # 🆕 Teste Agent 3
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

1. **Agent 1:**
   - `src/agents/data_collection_agent.py` → `src/agents/agent1/agent.py`
   - Teste → `tests/agent1/`

2. **Agent 2:**
   - `src/agents/decision_agent.py` → `src/agents/agent2/agent.py`
   - Teste → `tests/agent2/`

3. **Agent 3:**
   - `src/agents/execution_agent.py` → `src/agents/agent3/agent.py`
   - Teste → `tests/agent3/`

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

---

## 🎯 Recomandare

**Structura propusă este excelentă pentru:**
- ✅ Organizare clară
- ✅ Testare izolată
- ✅ Mentenanță ușoară
- ✅ Scalabilitate

**Vrei să implementăm această structură?**
