# Arhitectură Trading Bot - Design Modular

## 🎯 Principii de Design

1. **Separarea responsabilităților** - Fiecare modul are un scop clar și unic
2. **Dependency Injection** - Modulele comunică prin interfețe, nu direct
3. **Single Responsibility** - O clasă = o responsabilitate
4. **DRY (Don't Repeat Yourself)** - Cod comun în `utils/` sau clase de bază
5. **Testabilitate** - Fiecare modul poate fi testat independent

---

## 📐 Structură Proiect (Îmbunătățită)

```
trading_bot/
│
├── config/                          # Configurație (YAML, env)
│   ├── config.yaml
│   ├── strategy_params.yaml
│   └── risk_params.yaml
│
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entry point - orchestrator
│   │
│   ├── models/                      # 🆕 Entități de date (DTOs)
│   │   ├── __init__.py
│   │   ├── trade.py                 # Trade, Position, Order
│   │   ├── signal.py                # Signal, Indicator
│   │   └── market_data.py           # Bar, Quote, Tick
│   │
│   ├── broker/                      # Strat: Infrastructură (I/O)
│   │   ├── __init__.py
│   │   ├── ibkr_connector.py        # Conexiune IBKR
│   │   ├── data_provider.py         # Date istorice + live
│   │   └── execution.py             # Execuție ordine
│   │
│   ├── strategy/                    # Strat: Logică Business
│   │   ├── __init__.py
│   │   ├── base_strategy.py         # 🆕 Clasă abstractă (evită duplicare)
│   │   ├── technical_analysis.py   # Calcul indicatori
│   │   ├── signal_generator.py      # Logică BUY/SELL/HOLD
│   │   └── filters.py               # Filtre (oră, trend, etc.)
│   │
│   ├── risk/                        # Strat: Management Risc
│   │   ├── __init__.py
│   │   ├── position_sizing.py       # Calcul dimensiune poziție
│   │   ├── risk_manager.py          # 🆕 Manager centralizat
│   │   ├── risk_checks.py           # Validări (daily loss, etc.)
│   │   └── limits.py                # Constante și limite
│   │
│   ├── services/                    # 🆕 Servicii (orchestrare logică)
│   │   ├── __init__.py
│   │   ├── trading_service.py        # Orchestrează: strategy + risk + execution
│   │   └── portfolio_service.py     # Gestionare portofoliu
│   │
│   ├── backtest/                    # Strat: Testare
│   │   ├── __init__.py
│   │   ├── backtester.py            # Motor backtesting
│   │   ├── metrics.py               # Calcul metrici
│   │   └── portfolio_sim.py        # Simulator portofoliu
│   │
│   ├── storage/                     # 🆕 Persistență (opțional)
│   │   ├── __init__.py
│   │   ├── repository.py           # Pattern Repository (abstracție DB)
│   │   └── sqlite_store.py         # Implementare SQLite
│   │
│   ├── logging_utils/                # Strat: Observabilitate
│   │   ├── __init__.py
│   │   ├── logger.py               # Configurare logging
│   │   └── formatters.py           # Format log messages
│   │
│   └── utils/                       # Strat: Utilitare
│       ├── __init__.py
│       ├── helpers.py               # Funcții helper
│       ├── validators.py            # Validare input
│       └── config_loader.py        # Citire config
│
├── data/
│   ├── historical/                  # Date istorice (CSV)
│   ├── backtests/                   # Rezultate backtests
│   └── logs/                        # Log-uri
│
└── tests/
    ├── test_strategy.py
    ├── test_risk.py
    ├── test_execution.py
    └── test_backtest.py
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
