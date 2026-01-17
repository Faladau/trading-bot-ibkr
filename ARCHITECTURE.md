# Arhitectură Trading Bot - Design Modular

## 🎯 Principii de Design

1. **Separarea responsabilităților** - Fiecare modul are un scop clar și unic
2. **Dependency Injection** - Modulele comunică prin interfețe, nu direct
3. **Single Responsibility** - O clasă = o responsabilitate
4. **DRY (Don't Repeat Yourself)** - Cod comun în `utils/` sau clase de bază
5. **Testabilitate** - Fiecare modul poate fi testat independent

---

## 📐 Structură Proiect (v6.0 - Multi-Agent)

```
trading_bot/
│
├── config/
│   ├── config.yaml              # Configurație generală
│   ├── strategy_params.yaml      # Parametri strategie
│   └── risk_params.yaml          # Parametri risc
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point - orchestrator
│   │
│   ├── agents/                  # 🆕 Agenții principali (v6.0)
│   │   ├── __init__.py
│   │   ├── data_collection_agent.py    # Agent 1
│   │   ├── decision_agent.py           # Agent 2
│   │   └── execution_agent.py          # Agent 3
│   │
│   ├── broker/                   # Folosit de Agent 1 și 3
│   │   ├── __init__.py
│   │   ├── ibkr_connector.py    # Conexiune IBKR
│   │   ├── data_provider.py     # Colectare date
│   │   └── execution.py         # Execuție ordine
│   │
│   ├── strategy/                 # Folosit de Agent 2
│   │   ├── __init__.py
│   │   ├── technical_analysis.py # Calcul indicatori
│   │   ├── signal_generator.py  # Logică decizie
│   │   └── filters.py           # Filtre
│   │
│   ├── risk/                     # Folosit de Agent 3
│   │   ├── __init__.py
│   │   ├── risk_manager.py      # Validări risc
│   │   └── position_sizing.py   # Calcul sizing
│   │
│   ├── models/                   # Folosit de toți agenții
│   │   ├── __init__.py
│   │   ├── market_data.py       # Bar, Quote, Tick
│   │   ├── signal.py            # Signal, Indicator
│   │   └── trade.py             # Trade, Position, Order
│   │
│   ├── services/                 # Orchestrează agenții
│   │   ├── __init__.py
│   │   └── trading_service.py   # Orchestrator principal
│   │
│   ├── backtest/                 # Backtesting
│   │   ├── __init__.py
│   │   ├── backtester.py
│   │   └── metrics.py
│   │
│   ├── storage/                  # Persistență (opțional)
│   │   ├── __init__.py
│   │   └── repository.py
│   │
│   ├── logging_utils/            # Logging
│   │   ├── __init__.py
│   │   └── logger.py
│   │
│   └── utils/                    # Utilitare
│       ├── __init__.py
│       ├── config_loader.py
│       ├── helpers.py
│       └── validators.py
│
├── data/
│   ├── historical/              # Date istorice (CSV, JSON)
│   ├── signals/                 # 🆕 Semnale generate (JSON)
│   ├── trades/                  # 🆕 Trade-uri completate (JSON)
│   ├── backtests/               # Rezultate backtests
│   └── logs/                    # Log-uri
│
└── tests/
    ├── test_agent1.py           # 🆕 Teste Agent 1
    ├── test_agent2.py           # 🆕 Teste Agent 2
    ├── test_agent3.py           # 🆕 Teste Agent 3
    ├── test_integration.py      # 🆕 Teste integrare
    ├── test_models.py
    ├── test_config_loader.py
    ├── test_helpers.py
    ├── test_validators.py
    └── test_logger.py
```

---

## 🔄 Flux de Date (Pipeline)

```
1. main.py
   ↓
2. broker/data_provider.py → [Market Data]
   ↓
3. strategy/technical_analysis.py → [Indicatori]
   ↓
4. strategy/signal_generator.py → [Signal]
   ↓
5. risk/risk_manager.py → [Validare]
   ↓
6. risk/position_sizing.py → [Dimensiune]
   ↓
7. broker/execution.py → [Order]
   ↓
8. services/trading_service.py → [Monitorizare]
```

---

## 🏗️ Arhitectură pe Straturi

### **Strat 1: Models** (Date)
- Entități pure Python (dataclasses sau Pydantic)
- Fără logică de business
- Exemple: `Trade`, `Position`, `Signal`, `Bar`

### **Strat 2: Broker** (I/O - Infrastructură)
- Conexiune la API extern (IBKR)
- Date input/output
- Execuție ordine
- **Nu conține logică de business**

### **Strat 3: Strategy** (Logică Business)
- Analiză tehnică
- Generare semnale
- Filtre
- **Independent de broker** (poate rula pe date CSV pentru backtest)

### **Strat 4: Risk** (Reguli Business)
- Validări
- Calcul sizing
- Limite
- **Independent de strategy**

### **Strat 5: Services** (Orchestrare)
- Combină strategy + risk + execution
- Logica de workflow
- **Folosește toate straturile de mai jos**

### **Strat 6: Utils** (Suport)
- Funcții helper
- Config loader
- Validatori
- **Folosit de toate straturile**

---

## 🎨 Pattern-uri de Design Folosite

### 1. **Strategy Pattern** (pentru strategii multiple)
```python
# base_strategy.py
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        pass

# ema_breakout_strategy.py
class EMABreakoutStrategy(BaseStrategy):
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        # Implementare specifică
        pass
```

### 2. **Repository Pattern** (pentru persistență)
```python
# repository.py
class TradeRepository(ABC):
    @abstractmethod
    def save_trade(self, trade: Trade) -> None:
        pass

# sqlite_store.py
class SQLiteTradeRepository(TradeRepository):
    def save_trade(self, trade: Trade) -> None:
        # Implementare SQLite
        pass
```

### 3. **Dependency Injection** (pentru testabilitate)
```python
# trading_service.py
class TradingService:
    def __init__(
        self,
        strategy: BaseStrategy,
        risk_manager: RiskManager,
        executor: ExecutionEngine
    ):
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.executor = executor
```

### 4. **Factory Pattern** (pentru creare obiecte)
```python
# strategy_factory.py
class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: str) -> BaseStrategy:
        if strategy_type == "ema_breakout":
            return EMABreakoutStrategy()
        # ...
```

---

## ✅ Avantaje Structură

1. **Modularitate** - Fiecare modul poate fi modificat independent
2. **Testabilitate** - Mock-uim interfețele pentru teste
3. **Extensibilitate** - Adăugăm strategii noi fără să modificăm cod existent
4. **Claritate** - Știi exact unde să cauți ceva
5. **Reutilizare** - Cod comun în `utils/` sau clase de bază
6. **Separation of Concerns** - Fiecare strat are responsabilitate clară

---

## 🚫 Ce Evităm

1. **Cod duplicat** → Folosim clase de bază (`base_strategy.py`)
2. **Dependențe circulare** → Straturi clare, dependențe unidirecționale
3. **God classes** → Clase mici, responsabilitate unică
4. **Hard-coded values** → Totul în config files
5. **Tight coupling** → Comunicare prin interfețe, nu implementări concrete

---

## 📝 Exemplu: Cum Adăugăm o Strategie Nouă

```python
# 1. Creezi strategia (moștenește BaseStrategy)
class MeanReversionStrategy(BaseStrategy):
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        # Logică mean reversion
        pass

# 2. O înregistrezi în factory (opțional)
StrategyFactory.register("mean_reversion", MeanReversionStrategy)

# 3. O folosești în config.yaml
strategy:
  type: "mean_reversion"
  params: {...}

# 4. main.py o încarcă automat
# ✅ Fără să modifici cod existent!
```

---

## 🔍 Unde Caut Ceva?

- **Conexiune IBKR** → `broker/ibkr_connector.py`
- **Calcul indicatori** → `strategy/technical_analysis.py`
- **Logică trading** → `strategy/signal_generator.py`
- **Validare risc** → `risk/risk_manager.py`
- **Execuție ordine** → `broker/execution.py`
- **Orchestrare** → `services/trading_service.py`
- **Config** → `config/*.yaml` + `utils/config_loader.py`

---

**Această structură este scalabilă, testabilă și ușor de urmărit! 🚀**
