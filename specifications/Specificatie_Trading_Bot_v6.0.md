# Specificație funcțională — Trading Bot AI cu Interactive Brokers
## v6.0 — Versiunea Unificată cu Arhitectură Multi-Agent

---

## 1. Scopul proiectului

Scopul proiectului este dezvoltarea unui **sistem de trading automat**, modular și scalabil, cu capital mic, care să execute strategii simple, robuste și ușor de extins, conectat la **Interactive Brokers (IBKR)** prin API.

Sistemul utilizează o **arhitectură multi-agent** cu 3 agenți independenți, fiecare cu responsabilități clare, permițând dezvoltare incrementală, testare independentă și mentenanță ușoară.

---

## 2. Arhitectură Multi-Agent

### 2.1 Concept General

Sistemul este împărțit în **3 agenți independenți**, fiecare cu o singură responsabilitate clară:

1. **Agent 1: Data Collection Agent** — Colectează date brute de piață
2. **Agent 2: Decision Agent** — Analizează date și generează semnale
3. **Agent 3: Execution Agent** — Execută ordine și gestionează riscul

### 2.2 Comunicare între Agenți

Agenții comunică prin:
- **Obiecte Python (models)** — pentru performanță în memorie
- **Fișiere JSON** — pentru persistență și audit
- **Fișiere CSV** — pentru debugging manual și backtesting

**Flux de comunicare:**
```
Agent 1 → Bar (model) + JSON/CSV
         ↓
Agent 2 → Signal (model) + JSON
         ↓
Agent 3 → Order/Position/Trade (models) + JSON
```

### 2.3 Avantaje Arhitectură Multi-Agent

- ✅ **Testabilitate** — Fiecare agent testat independent
- ✅ **Dezvoltare incrementală** — Un agent la rând
- ✅ **Scalabilitate** — Poți adăuga mai mulți agenți
- ✅ **Mentenanță** — Modificări izolate per agent
- ✅ **Backtesting** — Agent 2 rulează pe CSV fără broker

---

## 3. Agent 1 — Data Collection Agent

### 3.1 Scop

Colectează date brute de piață, **fără interpretare sau logică de business**.

### 3.2 Responsabilități

1. **Inițializează conexiunea IBKR**
   - Conectare la TWS/IB Gateway
   - Verificare status sesiune
   - Reconectare automată la erori

2. **Citește lista de simboluri din config**
   - Simboluri din `config.yaml`
   - Validare simboluri

3. **Colectează date OHLCV pentru fiecare simbol**
   - Date istorice (pentru backtesting)
   - Stream live (pentru trading real)
   - Verificare completitudine date

4. **Normalizează formatul**
   - Standardizare timestamp
   - Validare OHLCV (high >= low, etc.)
   - Conversie la model `Bar`

5. **Salvează datele local**
   - CSV pentru verificare manuală
   - JSON pentru agenții următori
   - Structură: `data/historical/{symbol}_{timeframe}.csv`

**⚠️ IMPORTANT:** Agent 1 este **100% market data**. Nu verifică sold, capital sau orice legat de bani. Aceasta creează cuplare inutilă. Doar Agent 3 are voie să întrebe de capital.

### 3.3 Output

**Obiecte Python (models):**
- `Bar` — OHLCV cu timestamp
- `Quote` — Bid/Ask (opțional)
- `Tick` — Preț instantaneu (opțional)

**Fișiere:**
- **CSV:** `data/historical/{symbol}_{timeframe}.csv`
- **JSON:** `data/historical/{symbol}_{timeframe}.json`

**Câmpuri obligatorii în output:**
- `symbol` — Simbolul acțiunii
- `timeframe` — Timeframe (1H, 4H, 1D)
- `timestamp` — Data/ora barei
- `open` — Preț deschidere
- `high` — Preț maxim
- `low` — Preț minim
- `close` — Preț închidere
- `volume` — Volum tranzacționat

### 3.4 Module

- `broker/ibkr_connector.py` — Conexiune și management IBKR
- `broker/data_provider.py` — Colectare date istorice și live
- **Nu conține logică de business!**

### 3.5 Error Handling

- **Pierdere conexiune:** Reconectare automată cu exponential backoff
- **Date incomplete:** Skip bar, log warning
- **Simbol invalid:** Skip simbol, log error
- **Timeout API:** Retry cu limită

---

## 4. Agent 2 — Decision Agent

### 4.1 Scop

Interpretează datele primite de la Agent 1, calculează indicatori tehnici, aplică reguli de strategie și generează semnale clare.

### 4.2 Responsabilități

1. **Citește datele de la Agent 1**
   - Input: `Bar` (model) sau JSON
   - Validare date înainte de procesare

2. **Calculează indicatori tehnici**
   - **EMA 20** — Media exponențială pe 20 perioade
   - **EMA 50** — Media exponențială pe 50 perioade
   - **Volum mediu** — Media volumului pe N perioade
   - **RSI** — Relative Strength Index (opțional)
   - **MACD** — Moving Average Convergence Divergence (opțional)

3. **Aplică regulile de strategie**
   - **Reguli de intrare (BUY):**
     - Preț actual (close) > EMA20
     - Volum curent > 1.5 × volum mediu
     - Opțional: EMA20 > EMA50 (trend ascendent)
     - Opțional: RSI între 40-70
   - **Reguli de ieșire (SELL):**
     - **Agent 2 doar SEMNALEAZĂ condiția de ieșire:**
       - Atingere Take Profit (1-3% profit) → semnalează SELL
       - Atingere Stop Loss (< 1% pierdere) → semnalează SELL
       - Close la final de sesiune (fără overnight) → semnalează SELL
     - **⚠️ IMPORTANT:** Agent 2 NU trimite ordine! Doar generează semnal.
     - **Agent 3 decide când și cum trimite ordinul de ieșire.**
   - **HOLD:** Dacă nu sunt condiții pentru BUY sau SELL

4. **Generează semnal clar**
   - Acțiune: BUY, SELL sau HOLD
   - Preț intrare (dacă BUY/SELL)
   - Take Profit (TP)
   - Stop Loss (SL)
   - **Scor de încredere (0.0 - 1.0)**
     - **Prag minim:** Agent 3 ignoră semnale cu confidence < 0.6 (configurabil)
     - Face sistemul mai robust fără complexitate
     - Filtrează semnale slabe automat

5. **Salvează semnalul**
   - JSON pentru audit
   - Log pentru debugging

### 4.3 Output

**Obiect Python (model):**
- `Signal` — Cu action, entry_price, TP, SL, confidence

**Fișier:**
- **JSON:** `data/signals/{symbol}_{timestamp}.json`

**Câmpuri în output:**
- `action` — BUY, SELL sau HOLD
- `symbol` — Simbolul acțiunii
- `timestamp` — Data/ora semnalului
- `entry_price` — Preț de intrare (dacă BUY/SELL)
- `take_profit` — Preț Take Profit
- `stop_loss` — Preț Stop Loss
- `confidence` — Scor încredere (0.0 - 1.0)
- `indicators` — Dict cu indicatori calculați
- `reason` — Motivul semnalului

### 4.4 Module

- `strategy/technical_analysis.py` — Calcul indicatori
- `strategy/signal_generator.py` — Logică decizie
- `strategy/filters.py` — Filtre (oră, trend, etc.)
- **Independent de broker!** (poate rula pe CSV pentru backtest)

### 4.5 Error Handling

- **Date invalide:** Skip, log warning
- **Indicatori imposibili:** Folosește valori default, log warning
- **Semnal ambiguu:** Generează HOLD, log info

---

## 5. Agent 3 — Execution Agent

### 5.1 Scop

Primește semnale de la Agent 2, validează riscul, calculează dimensiunea poziției, trimite ordine către broker și monitorizează pozițiile.

### 5.2 Responsabilități

1. **Primește semnalul de la Agent 2**
   - Input: `Signal` (model) sau JSON
   - **Validare confidence:** Ignoră semnale cu confidence < prag minim (default: 0.6)
   - Validare semnal înainte de procesare

2. **Rulează verificări de risc**
   - **Daily Loss Limit (HARD STOP):** 
     - Dacă pierderi cumulate >= 3-5% capital, **oprește complet execuția**
     - **Nu mai trimite ordine până a doua zi**
     - Este un hard stop, nu implicit - trebuie scris explicit
   - **Max Trades per Day:** Max 10 trade-uri/zi
   - **Poziție existentă:** O singură poziție per simbol
   - **Capital disponibil:** **Agent 3 este singurul care verifică sold/capital**
   - **Min Capital Check:** Refuză dacă capital < 20% din requirement

3. **Calculează mărimea poziției**
   - Formula: `position_size = (capital * 0.20) / entry_price`
   - Max 20% capital per trade
   - **Limită suplimentară:** Max shares per trade sau max exposure per simbol
     - Protecție la gap-uri mari la small cap
     - Previne poziții prea mari la volatilitate extremă
   - Rotunjire la număr întreg de acțiuni
   - Validare că nu depășește limite

4. **Trimite ordinele către IBKR**
   - **Bracket Order:** Ordin de intrare + TP + SL
   - Tip ordin: MARKET sau LIMIT (configurabil)
   - **⚠️ IMPORTANT:** Agent 3 decide când și cum trimite ordinul
     - Pentru ieșire: Agent 2 semnalează condiția, Agent 3 decide execuția
   - Confirmare execuție
   - Gestionare partial fills

5. **Monitorizează poziția**
   - Verificare atingere TP/SL
   - Actualizare preț curent
   - Calcul PnL nerealizat
   - Logging periodic

6. **Loghează rezultatul**
   - Fiecare ordin trimis
   - Fiecare poziție deschisă/închisă
   - Fiecare trade completat
   - JSON pentru audit

### 5.3 Output

**Obiecte Python (models):**
- `Order` — Ordin trimis
- `Position` — Poziție deschisă
- `Trade` — Trade completat

**Fișiere:**
- **JSON:** `data/trades/{symbol}_{timestamp}.json`
- **Log:** `data/logs/execution.log`

### 5.4 Module

- `risk/risk_manager.py` — Validări risc
- `risk/position_sizing.py` — Calcul sizing
- `broker/execution.py` — Execuție ordine
- **Nu conține logică de strategie!**

### 5.5 Error Handling

- **Ordin respins:** Log error, skip trade
- **Partial fill:** Gestionează cantitatea rămasă
- **Conexiune pierdută:** Așteaptă reconectare, nu trimite ordine noi
- **Validare risc eșuat:** Refuză trade, log warning

---

## 6. Structură Proiect

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
│   ├── agents/                  # 🆕 Agenții principali (fiecare în folder separat)
│   │   ├── __init__.py
│   │   │
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
│   ├── services/                 # Orchestrează agenții
│   │   ├── __init__.py
│   │   └── trading_service.py
│   │
│   ├── backtest/                 # Backtesting
│   │   ├── __init__.py
│   │   ├── backtester.py
│   │   └── metrics.py
│   │
│   └── storage/                  # Persistență (opțional)
│       ├── __init__.py
│       └── repository.py
│
├── data/
│   ├── historical/              # Date istorice (CSV, JSON)
│   ├── signals/                 # Semnale generate (JSON)
│   ├── trades/                  # Trade-uri completate (JSON)
│   └── logs/                    # Log-uri
│
├── tests/
│   ├── __init__.py
│   │
│   ├── data_collection/         # 🆕 Teste Data Collection Agent
│   │   ├── __init__.py
│   │   └── test_data_collection_agent.py
│   │
│   ├── decision/                # 🆕 Teste Decision Agent
│   │   ├── __init__.py
│   │   └── test_decision_agent.py
│   │
│   ├── execution/               # 🆕 Teste Execution Agent
│   │   ├── __init__.py
│   │   └── test_execution_agent.py
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
├── requirements.txt
├── README.md
└── .env                         # Variabile mediu (NU COMMIT!)
```

---

## 7. Flux de Lucru Recomandat

### Faza 1: Agent 1 (Data Collection)
1. ✅ Models (Bar, Quote, Tick) - **DONE**
2. ⏳ Broker connector (pașii 1-2)
3. ⏳ Data provider (pașii 3-6)
4. ⏳ Output: Bar (model) + JSON/CSV
5. ⏳ Teste cu mock-uri
6. ✅ **Verificare output manual** (CSV)

### Faza 2: Agent 2 (Decision)
1. ✅ Models (Signal) - **DONE**
2. ⏳ Technical analysis (pașii 1-2)
3. ⏳ Signal generator (pașii 3-4)
4. ⏳ Output: Signal (model) + JSON
5. ⏳ **Teste pe date istorice (CSV)** - fără broker

### Faza 3: Agent 3 (Execution)
1. ✅ Models (Order, Position, Trade) - **DONE**
2. ⏳ Risk manager (pașii 1-2)
3. ⏳ Position sizing (pasul 3)
4. ⏳ Order execution (pașii 4-6)
5. ⏳ Teste cu mock broker
6. ⏳ **Paper trading** - doar după validare

### Faza 4: Orchestrare
1. ⏳ Trading service (combină agenții)
2. ⏳ Main orchestrator
3. ⏳ Teste de integrare
4. ⏳ Backtesting complet
5. ⏳ Paper trading complet
6. ⏳ Live trading (doar după validare)

---

## 8. Configurație

### 8.1 config.yaml

```yaml
app:
  mode: paper  # backtest, paper, live
  debug: true

ibkr:
  host: 127.0.0.1
  port: 7497
  clientId: 1
  paper: true

symbols:
  - AAPL
  - MSFT
  - AMD

agent1:
  data_dir: data/historical
  save_csv: true
  save_json: true
  update_interval: 60  # secunde

agent2:
  signals_dir: data/signals
  save_json: true
  indicators:
    ema_short: 20
    ema_long: 50
    volume_threshold: 1.5
    use_rsi: false
    use_macd: false

agent3:
  trades_dir: data/trades
  save_json: true
  min_confidence: 0.6  # Ignoră semnale sub acest prag
  risk:
    capital_initial: 500
    max_risk_per_trade: 0.20
    max_positions: 1
    daily_loss_limit: 0.05  # HARD STOP - oprește complet până a doua zi
    max_trades_per_day: 10
    max_shares_per_trade: 100  # Limită suplimentară pentru small cap
    max_exposure_per_symbol: 200  # Max exposure per simbol (USD)

strategy:
  timeframe: "1H"
  take_profit_pct: 2.0
  stop_loss_pct: 0.8
  no_overnight: true

logging:
  level: INFO
  file: data/logs/trading.log
```

---

## 9. Reguli de Trading

### 9.1 Reguli de Intrare (BUY)

1. Preț actual (close) > EMA20
2. Volum curent > 1.5 × volum mediu
3. Opțional: EMA20 > EMA50 (trend ascendent)
4. Opțional: RSI între 40-70
5. Nu există poziție deschisă pe simbol
6. Capital disponibil >= 20% din requirement

### 9.2 Reguli de Ieșire (SELL)

1. Atingere Take Profit (1-3% profit)
2. Atingere Stop Loss (< 1% pierdere)
3. Close la final de sesiune (fără overnight)
4. Daily loss limit atins

### 9.3 Reguli de Risc

1. Max 20% capital per trade
2. O singură poziție per simbol
3. Fără leverage
4. Daily loss limit: 3-5% capital total
5. Max 10 trade-uri/zi
6. Nu ține poziții peste noapte

---

## 10. Testing Strategy

### 10.1 Unit Tests

- **Agent 1:** Teste cu mock IBKR API
- **Agent 2:** Teste pe date CSV (fără broker)
- **Agent 3:** Teste cu mock broker și semnale mock

### 10.2 Integration Tests

- Testează comunicarea între agenți
- Testează flux complet cu mock-uri
- Testează error handling

### 10.3 Backtesting

- Agent 2 rulează pe date istorice (CSV)
- Simulare execuție (Agent 3 mock)
- Calcul metrici de performanță

### 10.4 Paper Trading

- Toți agenții rulează cu feed live
- Ordine simulate (nu reale)
- Validare comportament în timp real

### 10.5 Live Trading

- Doar după validare paper trading
- Capital mic inițial (50-100 EUR)
- Monitorizare intensă

---

## 11. Logging și Audit

### 11.1 Logging

- Fiecare agent loghează acțiunile sale
- Format consistent: `timestamp | level | agent | message`
- Rotire fișiere (10MB, 5 backup-uri)

### 11.2 Audit Trail

- **Agent 1:** Toate datele colectate (CSV/JSON)
- **Agent 2:** Toate semnalele generate (JSON)
- **Agent 3:** Toate ordinele și trade-urile (JSON)

### 11.3 Debugging

- Log-uri detaliate în mod debug
- Stack traces pentru erori
- Context pentru fiecare acțiune

---

## 12. Deployment

### 12.1 Local Development

- Python 3.12+
- Virtual environment
- TWS/IB Gateway pentru conexiune

### 12.2 Cloud Deployment (Opțional)

- VPS (Kamatera, DigitalOcean)
- IB Gateway headless
- Systemd service pentru auto-start

**⚠️ RECOMANDARE IMPORTANTĂ:**
- **Nu atinge cloud până nu ai minim 1-2 luni de paper trading stabil**
- Paper trading local este suficient pentru început
- Cloud adaugă complexitate inutilă în faza de dezvoltare
- Focus pe stabilitate și testare înainte de deployment

---

## 13. Versioning

| Versiune | Data | Status | Note |
|----------|------|--------|------|
| v5.1 | 2026-01-15 | ✅ | Versiune inițială modulară |
| v5.2 | 2026-01-XX | ✅ | Arhitectură multi-agent (draft) |
| **v6.0** | **2026-01-XX** | **🔄** | **Versiune unificată finală** |

---

## 14. Concluzie

Această versiune v6.0 combină:
- ✅ **Pașii detaliați** din v5.2
- ✅ **Structura și models** din research
- ✅ **Best practices** pentru arhitectură multi-agent
- ✅ **Comunicare hibridă** (models + JSON/CSV)

**Rezultat:** O arhitectură clară, testabilă, scalabilă și ușor de implementat incremental! 🚀

---

**Document: Specificație funcțională — Trading Bot AI cu Interactive Brokers**  
**Versiune: v6.0**  
**Status: FINAL - READY FOR IMPLEMENTATION**  
**Ultima actualizare: 2026-01-XX**
