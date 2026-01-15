# Specificație funcțională — Trading Bot AI cu Interactive Brokers
## v5.1 — Versiunea Finală cu Deployment Cloud (Kamatera + VPS Headless)

---

## 1. Scopul proiectului

Scopul proiectului este dezvoltarea unui **sistem de trading automat**, modular și scalabil, cu capital mic, care să execute strategii simple, robuste și ușor de extins, conectat la **Interactive Brokers (IBKR)** prin API.

Sistemul trebuie să utilizeze agenți AI / componente inteligente pentru analiză și decizie, păstrând un strat de execuție foarte strict și controlat din punct de vedere al riscului. Codul trebuie să fie structurat astfel încât să poată fi ușor modificat și optimizat cu ajutorul unui IDE AI (de ex. Cursor).

---

## 2. Obiective principale

- **Profit mic și repetabil**: Focus pe consistență și ratio câștig/pierdere pe termen lung, nu pe profit maxim per trade. [1]
- **Control strict al riscului**: Limită per trade (max 20% capital), fără leverage, o poziție pe simbol, limite globale de pierdere zilnică. [2]
- **Stabilitate operațională**: Botul trebuie să ruleze ininterrupt, cu mecanisme automate de reconectare la API și recovery din erori. [3]
- **Execuție predictibilă și auditată**: Orice decizie, semnal și ordin este logat complet pentru analiză ulterioară și debugging. [4]
- **Ușor de configurare și deployment**: Config via fișiere (YAML/JSON), cod modularizat pe pachete, containerizabil via Docker în fazele ulterioare. [5]

---

## 3. Stack tehnologic

### 3.1 Limbaj și ecosistem

- **Limbaj**: Python 3.10+ (ecosistem bogat pentru trading, biblioteci AI/ML, integrare API ușoară). [1][2]
- **Virtual Environment**: venv + `requirements.txt` pentru reproducibilitate. [3]

### 3.2 Broker și conectivitate

- **Broker**: Interactive Brokers (IBKR), accesat prin **TWS Workstation** sau **IB Gateway**. [1][4]
- **API Wrapper**: `ib_insync` — wrapper asincron popular, ușor de folosit, utilizat în proiecte IBKR open-source (ReversionSys, mmr, ibkr-ai-trading-bot-gui). [2][5]
- **Biblioteci date**: `pandas`, `numpy` pentru manipulare serii temporale, calcul indicatori, backtesting. [1][3]
- **Persistență**: SQLite (istoric tranzacții, backtesting) și/sau CSV (export date). [4]

### 3.3 Biblioteci specifice

- `ta-lib` sau `pandas_ta`: Calcul indicatori tehnici (EMA, RSI, MACD, volum) rapid și optimizat. [1][2]
- `pyyaml`: Citire configurație din fișiere YAML. [3]
- `logging`: Logging integrat, cu rotating handlers pentru gestiune log-uri. [4]
- `asyncio` + `ib_insync`: Programare asincronă pentru fluxuri non-blocking (date live, ordine, reconexiuni). [5]

---

## 4. Arhitectură sistem — Design modular

Arhitectura este **modulară** și separă clar analiză de execuție. Inspirare din proiecte IBKR existente: mmr (9600dev), ReversionSys (rawsashimi1604), ibkr-ai-trading-bot-gui (jahanzaib-codes). [1][2][3]

### 4.1 Structura de directoare

```
trading_bot/
│
├── config/
│   ├── config.yaml              # Configurație generală (simboluri, parametri, API)
│   ├── strategy_params.yaml      # Parametri specifici strategie
│   └── risk_params.yaml          # Parametri risc
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point principal
│   │
│   ├── broker/
│   │   ├── __init__.py
│   │   ├── ibkr_connector.py    # Conexiune și management API IBKR
│   │   ├── data_provider.py     # Descărcare date istorice și stream live
│   │   └── execution.py         # Plasmă ordine, management poziții
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── technical_analysis.py # Calcul EMA, volum, indicatori
│   │   ├── signal_generator.py  # Logică BUY/SELL/HOLD
│   │   └── filters.py           # Filtre suplimentare (trend, oră, etc.)
│   │
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── position_sizing.py   # Calcul dimensiune poziție (20% rule)
│   │   ├── risk_checks.py       # Validare reguli globale (drawdown, nr trade-uri)
│   │   └── limits.py            # Definiții limite și constante
│   │
│   ├── backtest/
│   │   ├── __init__.py
│   │   ├── backtester.py        # Motor backtesting simplu
│   │   ├── metrics.py           # Calcul PnL, drawdown, Sharpe, etc.
│   │   └── portfolio_sim.py     # Simulator portofoliu
│   │
│   ├── logging_utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Configurare logging
│   │   └── formatters.py        # Format log messages
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py           # Funcții utilitare
│       ├── validators.py        # Validare input
│       └── config_loader.py     # Citire config fișiere
│
├── data/
│   ├── historical/              # Fișiere date istorice (CSV)
│   ├── backtests/               # Rezultate backtests (CSV, JSON)
│   └── logs/                    # Log-uri (rotating files)
│
├── tests/
│   ├── test_strategy.py
│   ├── test_risk.py
│   ├── test_execution.py
│   └── test_backtest.py
│
├── requirements.txt             # Dependențe proiect
├── README.md                    # Documentație proiect
└── .env                         # Variabile mediu (IBKR credențiale — **NU COMMIT**)
```

### 4.2 Module și responsabilități

#### A. **broker/ibkr_connector.py**
- Inițializează și gestionează conexiunea la IBKR TWS/IB Gateway. [1][2]
- Implementează logic de reconectare automată la erori de API. [3]
- Expune metode simple: `connect()`, `disconnect()`, `is_connected()`. [4]

#### B. **broker/data_provider.py**
- Descarcă date istorice (open, high, low, close, volume) pentru simboluri și timeframes specificate. [1]
- Subscriu la stream live de date (bare intraday), actualiza în memorie sau bază de date. [2]
- Expune metode: `get_historical_data()`, `subscribe_to_bars()`, `get_latest_bar()`. [3]

#### C. **broker/execution.py**
- Primește semnal trade + dimensiune poziție și plasează ordin IBKR (market sau limit). [1]
- Creează **bracket orders**: ordin de intrare + TP și SL atașate. [2]
- Gestionează partial fills, anulare poziții, asigură mereu existența unui stop-loss. [3]
- Expune: `place_order()`, `cancel_order()`, `modify_order()`, `get_position()`. [4]

#### D. **strategy/technical_analysis.py**
- Calculează indicatori: EMA20, EMA50, volum mediu, RSI (opțional), MACD (opțional). [1][2]
- Primește DataFrame OHLCV și returnează dict cu indicatori calculați. [3]
- Expune: `calculate_ema()`, `calculate_volume_indicators()`, `calculate_momentum_indicators()`. [4]

#### E. **strategy/signal_generator.py**
- Conține logică de **strategie**: analizează indicatori și genereaza BUY/SELL/HOLD. [1]
- **Semnal BUY** inițial:
  - Preț actual închide peste EMA20 (spargere în sus). [1]
  - Volum curent > 1.5 × volum mediu (confirmare spike de volum). [1]
  - Opțional: EMA20 > EMA50 (trend ascendent). [2]
  - Opțional: RSI 40–70 (nu oversoldul, nu overbought la intrare). [2]
- **Semnal SELL**:
  - Atingerea TP (1–3% profit configurabil). [1]
  - Atingerea SL (< 1% pierdere). [1]
  - Evitarea poziții după o oră de la close (fără overnight). [2]
- Returnează: `{'action': 'BUY', 'entry_price': ..., 'tp': ..., 'sl': ..., 'confidence': ...}`. [3]

#### F. **strategy/filters.py**
- Filtre suplimentare: interval orar (ex: 10:00–15:00), tip de piață, CFI-uri. [1][2]
- Funcții: `is_market_open()`, `is_trading_hours()`, `apply_filters()`. [3]

#### G. **risk/position_sizing.py**
- Calculează dimensiune poziție pe baza capitalului disponibil și regulii 20%. [1]
- **Formula**: `position_size = (capital * 0.20) / entry_price` → numărul de acțiuni. [2]
- Validează că nu se depășește limita per simbol. [3]
- Expune: `calculate_position_size()`. [4]

#### H. **risk/risk_checks.py**
- Validează că noul trade nu încalcă reguli globale:
  - O poziție deschisă per simbol. [1]
  - Limita de pierdere zilnică (ex: 3–5% capital total, oprește trading). [2]
  - Limita de trade-uri pe zi (ex: max 10 trade-uri/zi). [3]
  - Capital disponibil minim pentru noul trade. [4]
- Returnează: `True` (OK) sau `False` (reject cu motiv). [5]
- Expune: `validate_trade()`, `check_daily_loss_limit()`, `check_position_exists()`. [6]

#### I. **backtest/backtester.py**
- Motor backtest care refolosește logica de strategie și risc pe date istorice. [1]
- Simulează book de poziții și calculate PnL simulat pentru fiecare trade. [2]
- Acceptă date din CSV și timeframe configurable. [3]
- Expune: `run_backtest()`, `get_results()`. [4]

#### J. **backtest/metrics.py**
- Calculează metrice de performanță:
  - Profit net absolut și procentual. [1]
  - Drawdown maxim și recovery time. [2]
  - Sharpe Ratio simplificat, sortino ratio (opțional). [3]
  - Win rate, profit factor, liczba trade-uri. [4]
- Expune: `calculate_metrics()`, `print_report()`. [5]

#### K. **logging_utils/logger.py**
- Configurare centralizată a logging cu rotating handlers (daily sau size-based). [1]
- Nivele: DEBUG, INFO, WARNING, ERROR, CRITICAL. [2]
- Output în fișiere + opțional console. [3]

#### L. **main.py**
- Entry point și orchestrator principal. [1]
- Inițializează componentele (IBKR connector, data provider, strategy agent, execution). [2]
- Loop principal: citit date → analiza → signal → risk check → execution → logging. [3]
- Moduri: `--backtest`, `--paper`, `--live`. [4]
- Exemplu:
  ```
  python main.py --mode backtest --config config/config.yaml
  python main.py --mode paper --config config/config.yaml
  python main.py --mode live --config config/config.yaml
  ```

---

## 5. Strategie de tranzacționare detaliată

### 5.1 Strategie inițială: Breakout pe EMA cu volum

#### Caracteristici asset-uri

- **Universul de active**: Acțiuni listate pe NYSE/NASDAQ. [1]
- **Interval de preț**: 2–20 USD. [2]
- **Volum zilnic minim**: > 500.000 acțiuni/zi. [3]

#### Reguli de intrare

1. **Condiția de preț**: Prețul actual (bar de închidere) > EMA20. [1]
2. **Condiția de volum**: Volumul barei curente > 1.5 × volumul mediu (ultime N bare). [1]
3. **Filtru de trend** (opțional): EMA20 > EMA50. [2]
4. **Filtru de oră** (opțional): Bara trebuie să se închidă între 10:00–15:00. [3]
5. **RSI filtru** (opțional, viitor): RSI(2) în range 40–70. [4]

#### Reguli de ieșire

1. **Take Profit**: 1–3% peste prețul de intrare (configurable). [1]
2. **Stop Loss**: < 1% sub prețul de intrare (configurable). [1]
3. **Fără poziții peste noapte**: Orice poziție rămasă deschisă e închisă la close (16:00 ET). [2]

#### Capital și sizing

- **Capital inițial**: ~500 EUR. [1]
- **Risk per trade**: Max 20% din capital disponibil. [1]
- **Numărul de poziții**: 1 simbol pe simbol (nu stacking). [2]

---

## 6. Module risc și management

### 6.1 Limitări per trade

- **Max 20% capital per trade**: Formula `position_size = (capital * 0.20) / entry_price`. [1]
- **Max o poziție per simbol**: Nu se deschid 2+ poziții pe același simbol simultan. [2]
- **Fără leverage**: Se folosește doar cash disponibil. [3]

### 6.2 Limitări globale (zilnice/sesiune)

- **Daily Loss Limit**: Dacă pierderi cumulate >= 3–5% capital total, oprește trading-ul pentru restul zilei. [1][2]
- **Max Trades per Day**: Limita de ex. 10 trade-uri/zi pentru a controla overtrading. [3]
- **Min Capital Check**: Refusă trade dacă capital disponibil < 20% din requerment-ul pozitiei. [4]

### 6.3 Mecanisme de protecție

- **Pozițiile trebuie să aibă mereu SL activ**: Orice poziție deschisă are ordin SL atașat. [1]
- **Verificare volum**: Tranzacția se refusă dacă volum este sub o limită. [2]
- **Reconectare automată**: La deconectare din API, botul încearcă reconectare în 5s, apoi exponential backoff. [3]
- **Shutdown controlat**: La erori critice repetate, botul se oprește și loguje stare pentru debug. [4]

---

## 7. Moduri de execuție și testare

### 7.1 Backtesting
- **Scop**: Validare logică strategie pe date istorice, fără risc real. [1]
- **Intrări**: CSV cu OHLCV, timeframe, perioada de backtest, parametri strategie. [2]
- **Output**: Raport de performanță (PnL, drawdown, Sharpe, nr. de trades). [3]

### 7.2 Paper Trading
- **Scop**: Validare în timp real cu feed-uri live, dar fără ordin-uri reale. [1]
- **Conexiune**: Cont paper IBKR, feed real-time, ordine simulate. [2]
- **Output**: Loguri identice, dar fără debit din cont. [3]

### 7.3 Live Trading
- **Scop**: Execuție cu capital real, respectând toate regulile de risc. [1]
- **Conexiune**: Cont IBKR real, TWS Workstation sau IB Gateway. [2]
- **Necesită**: Autentificare, credențiale din `.env`, validare risc dublu. [3]

---

## 8. Configurație și customizare

### 8.1 Fișier config.yaml

```yaml
app:
  mode: paper  # backtest, paper, live
  debug: true

ibkr:
  host: 127.0.0.1
  port: 7497
  clientId: 1
  paper: true  # false pt. live account

symbols:
  - AAPL
  - MSFT
  - AMD

strategy:
  timeframe: "1H"         # 1H, 4H, 1D
  ema_short: 20
  ema_long: 50
  volume_threshold: 1.5   # 1.5x volum mediu

exits:
  take_profit_pct: 2.0    # 2% TP
  stop_loss_pct: 0.8      # 0.8% SL
  no_overnight: true      # Fără poziții peste noapte

risk:
  capital_initial: 500
  max_risk_per_trade: 0.20  # 20%
  max_positions: 1
  use_leverage: false
  daily_loss_limit: 0.05    # 5% pierdere zilnică = stop
  max_trades_per_day: 10

logging:
  level: INFO
  file: logs/trading.log
```

### 8.2 Fișier .env template (NU COMMIT!)

```
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=1
IBKR_USERNAME=your_username
IBKR_PASSWORD=your_password
PAPER_TRADING=true
INITIAL_CAPITAL=500
```

---

## 9. Logging și monitoring

Fiecare eveniment din sistem este logat cu timestamp, level, și detalii contextuale.

```
2026-01-15 10:23:45 | INFO  | IBKR | Connected to TWS
2026-01-15 10:24:12 | INFO  | DATA | Subscribed to AAPL 1H bars
2026-01-15 10:25:00 | INFO  | STRATEGY | AAPL: EMA20=150.23, EMA50=149.95, Signal=HOLD
2026-01-15 10:26:00 | INFO  | STRATEGY | AAPL: EMA20=150.50, EMA50=149.95, Vol=2.1M, Signal=BUY
2026-01-15 10:26:05 | INFO  | RISK | AAPL: Position size calc => 1 share @ 150.50
2026-01-15 10:26:08 | INFO  | RISK | AAPL: All checks passed, approve trade
2026-01-15 10:26:10 | INFO  | EXECUTION | AAPL: Placed BUY order 1 share @ 150.50, TP=153.51, SL=149.70
2026-01-15 10:26:45 | INFO  | EXECUTION | AAPL: Order filled, position open
2026-01-15 10:28:00 | INFO  | EXECUTION | AAPL: Position at +1.50%, monitoring...
2026-01-15 10:29:00 | INFO  | EXECUTION | AAPL: Hit TP @ 153.52, closed position, PnL=+3.02
```

---

## 10. Metrici de performanță și evaluare

### 10.1 Metrice calculate

- **Profit Net**: Câștig/pierdere absolut în EUR/USD. [1]
- **Return %**: ROI procentual pe capital inițial. [2]
- **Drawdown Maxim**: Cea mai mare cădere de la peak la valley. [3]
- **Win Rate**: % trade-uri profitabile. [5]
- **Sharpe Ratio**: Return / risk (volatilitate), metric de eficiență. [6]
- **Profit Factor**: Profit total / pierdere totală. [7]

### 10.2 Target-uri inițiale (pe backtest)

- **Win Rate**: Min. 50% (1 din 2 trade-uri profitabil). [1]
- **Profit Factor**: Min. 1.5 (de 1.5x mai mult profit decât pierdere). [2]
- **Return %**: 1–5% per lună în regim stabil. [3]
- **Drawdown Max**: < 10% equity. [4]

---

## 11. Strategie de tranziție Paper → Live (2–4 săptămâni)

### 11.1 De ce paper trading înainte de live?

Paper trading este esențial înainte de a risca bani reali. [1][2]

- **Validare logică pe date live**: Strategia rulează pe feed-uri reale de piață. [1]
- **Teste de stabilitate**: Descoperă bug-uri de reconectare API, partial fills, edge cases. [2]
- **Metrici reale**: PnL, drawdown, slippage pe condiții de piață reale. [3]
- **Fără risc**: Dacă strategia e defectuoasă, nu pierzi bani reali. [4]

### 11.2 Plan tranziție: Paper → Live (4 săptămâni)

**Săptămâna 1: Setup + Backtesting intensiv**
- Implementează modulele core (broker, strategy, risk, execution). [1]
- Descarcă 6–12 luni date istorice pentru 3–5 simboluri. [2]
- Rulează backtesting; target: **winrate >50%, drawdown <10%**. [3]

**Săptămâna 2: Paper Trading — Validare 1 simbol**
- Pornești bot în modul `paper` cu feed-uri live IBKR. [1]
- Selectezi 1 simbol (ex: AMD) și lași botul să ruleze 8–10 ore/zi. [2]
- Monitorizezi în timp real: semnale, ordine, execuții, erori de API. [3]
- Target: Drawdown zilnic < 2%. [4]

**Săptămâna 3: Paper Trading — Scalare 3–5 simboluri**
- Adaugă 2–4 simboluri suplimentare în watchlist. [1]
- Rulează paper pe multi-simbol, monitorizează management al riscului. [2]
- Target: Drawdown max < 3% pe portofoliu. [3]

**Săptămâna 4: Paper Trading + Pregătire Go/No-Go Live**
- Continuă paper trading pe 5 simboluri. [1]
- Generează raport final paper trading: PnL total, metrici, observații. [2]
- **Go/No-Go decision**: Dacă paper show consistent profit + drawdown control. [3]

### 11.3 Criterii Go/No-Go

- [ ] Paper trading: PnL cumulativ pozitiv pe 4 săptămâni. [1]
- [ ] Drawdown max < 5%. [2]
- [ ] Win rate 50%+ și profit factor > 1.2. [3]
- [ ] 0 erori critice non-recuperabile. [4]
- [ ] Logs complet și curat. [5]

### 11.4 Reguli de oprire (Stop Trading)

**INTERZIS să continui trading dacă:**

- Daily loss >= 5% din capital total. [1]
- 3 trade-uri consecutive cu pierderi. [2]
- API errors repetate (> 3 failed orders în 10 min). [3]
- Drawdown cumulativ > 10%. [4]
- Orice ordine nu primește SL/TP (critical bug). [5]

---

## 12. Cerințe hardware/software și deployment cloud

### 12.1 Cerințe laptop local (dezvoltare + testing)

| Componentă | Minim | Recomandat |
|------------|-------|------------|
| **CPU** | Dual-core 2GHz | Intel i5/Ryzen 5+ |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 20GB SSD | 100GB SSD |
| **OS** | Windows 10/11, Ubuntu 22.04+ | Ubuntu 22.04 LTS |
| **Internet** | 10Mbps | 100Mbps+ |

**Software obligatoriu:**
```
1. Python 3.10+          # python.org
2. Git                   # git-scm.com
3. VSCode + Cursor AI    # code.visualstudio.com
4. Interactive Brokers TWS (paper account)
5. Docker (opțional)     # Pentru testare container
```

### 12.2 GitHub repository (gratuit, 2 minute)

1. **github.com** → New repository → `trading-bot-ibkr`
2. **Adaugă `.gitignore`**:
```
.env
__pycache__/
*.pyc
logs/
data/historical/
trading_bot_env/
.DS_Store
```

3. **Push local → GitHub**:
```bash
git init
git add .
git commit -m "Initial commit v5.1"
git branch -M main
git remote add origin https://github.com/USERNAME/trading-bot-ibkr.git
git push -u origin main
```

### 12.3 Deployment opțiuni cloud

| Platformă | Cost | Pentru | Avantaje |
|-----------|------|--------|----------|
| **GitHub Codespaces** | Gratuit 60h/lună | Dev + paper testing | IDE online, Python ready |
| **DigitalOcean Droplet** | $4/lună | Live trading 24/7 | VPS Linux ieftin, SSH acces |
| **Kamatera Free Trial** | **$100 CREDIT GRATUIT** | **Testing scalabil** | **25 luni minim VPS GRATUIT** |
| **ForexVPS.net** | Gratuit (cu broker) | Live cu IBKR | Optimizat trading |

### 12.4 KAMATERA FREE TRIAL — RECOMANDAT ⭐⭐⭐⭐⭐

**Detalii:**
```
✅ 30 zile FREE TRIAL
✅ $100 CREDIT GRATUIT (acoperă 25 luni VPS $4!)
✅ Fără card obligatoriu la signup inițial
✅ Cancel anytime — NU PLĂTEȘTI nimic dacă nu depășești creditul
✅ Full VPS control (CPU, RAM, storage customizabil)
```

**Ghid activare (5 minute):**

1. **kamatera.com/free-trial-vps** → "Start Free Trial"
2. **Sign up**: email + parolă (fără card inițial)
3. **Deploy VPS**:
   ```
   Location: New York/Chicago (US markets - low latency)
   OS: Ubuntu 22.04 LTS
   Specs: 1 vCPU | 1GB RAM | 20GB NVMe
   (~$4/lună după trial — GRATUIT cu $100 credit!)
   ```
4. **SSH acces imediat**: `ssh root@IP_VPS`
5. **Setup bot**:
   ```bash
   apt update && apt install python3-pip git -y
   git clone https://github.com/USERNAME/trading-bot-ibkr.git
   cd trading-bot-ibkr
   pip install -r requirements.txt
   nano .env  # Adaugă IBKR paper keys
   python main.py --mode paper
   ```

**Cost după trial:** $4–24/lună (depinde de specs), dar $100 credit = GRATUIT 25–6 luni!

### 12.5 IB Gateway Headless pe VPS Linux

**Problemă**: TWS necesită GUI, nu rulează headless nativ.  
**Soluție**: Xvfb (virtual display) + IBController (auto-login)

**Script setup automat** (pe Kamatera/DigitalOcean VPS):

```bash
#!/bin/bash
# setup_ib_gateway_headless.sh

# 1. Instalează dependențe
apt update
apt install xvfb wget unzip openjdk-17-jre-headless -y

# 2. Descarcă IB Gateway offline installer
cd /opt
wget https://download2.interactivebrokers.com/installers/ibgateway/latest-standalone/ibgateway-latest-standalone-linux-x64.sh
chmod +x ibgateway-latest-standalone-linux-x64.sh
./ibgateway-latest-standalone-linux-x64.sh --autoaccept --dir /opt/ibgateway

# 3. Descarcă IBController (auto-login headless)
cd /opt
wget https://github.com/ib-controller/ib-controller/releases/latest/download/IBController_3.17.0.zip
unzip IBController_3.17.0.zip

# 4. Configurare IBController
cd IBController
cp config.ini.user.template config.ini
# Edit config.ini și setează:
# TWS_PATH=/opt/ibgateway
# IB_LOGIN_ID=your_paper_account
# IB_PASSWORD=your_password

# 5. Script start automat
cat > /opt/start_ib_gateway.sh << 'EOF'
#!/bin/bash
cd /opt/IBController
xvfb-run -a -s "-screen 0 1024x768x24" java -Xmx512m -jar IBController.jar
EOF
chmod +x /opt/start_ib_gateway.sh

# 6. Systemd service (auto-start la boot)
cat > /etc/systemd/system/ib-gateway.service << 'EOF'
[Unit]
Description=IB Gateway Headless
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/IBController
ExecStart=/opt/start_ib_gateway.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ib-gateway.service
systemctl start ib-gateway.service
```

**Test conexiune**:
```bash
python -c "
from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)  # IB Gateway port
print('Connected OK!')
ib.disconnect()
"
```

### 12.6 Checklist deployment FINAL (0 → live)

```
[ ] 1. Laptop: Python 3.10 + Git + TWS paper instalat (10 min)
[ ] 2. GitHub: Repo creat + push specificație v5.1 (5 min)
[ ] 3. Codespaces: Test backtest + paper trading (1h)
[ ] 4. Kamatera: Free trial VPS creat + SSH (5 min)
[ ] 5. VPS: Git clone + pip install + .env config (10 min)
[ ] 6. VPS IB Gateway: Headless setup + auto-start (20 min)
[ ] 7. VPS paper trading: 24h test continuu (monitorizează logs)
[ ] 8. Metrics OK: Winrate >50%, drawdown <3% (2-4 zile)
[ ] 9. Live switch: config.yaml mode: "live", capital: 50EUR
[ ] 10. Monitorizare: Logs + eventual Telegram alerts
```

**Timp total 0 → paper trading: 1-2 ore**  
**Timp 0 → live trading: 3-5 zile testing**

---

## 13. requirements.txt final

```
ib-insync==0.9.86
pandas==2.1.4
numpy==1.24.3
pandas_ta==0.3.14b0
pyyaml==6.0.1
python-dotenv==1.0.0
asyncio-contextmanager==1.0.0
pytest==7.4.3
streamlit==1.28.1
```

---

## 14. Extensii și roadmap viitor

### 14.1 Scurt termen (1–2 luni)
- [ ] Implementare modul core: broker, strategy, execution, backtest. [1]
- [ ] Backtesting pe 6+ luni date istorice. [2]
- [ ] Paper trading validation pe 2–4 săptămâni. [3]
- [ ] Documentație și tutorial setup local. [4]

### 14.2 Mediu termen (2–4 luni)
- [ ] Suport multi-simbol cu scheduler de scanare. [1]
- [ ] Optimizare parametri via grid search. [2]
- [ ] Integrare AI: model XGBoost pentru scoring. [3]
- [ ] Dashboard Streamlit pentru monitorizare live. [4]

### 14.3 Lung termen (4+ luni)
- [ ] Extindere la cripto (Binance API, similar IBKR). [1]
- [ ] Alte strategii: mean reversion, pairs trading, options. [2]
- [ ] Integrare alerte push (Telegram, Discord). [3]
- [ ] Containerizare Docker, deployment cloud (AWS/GCP). [4]
- [ ] Integrare LLM (OpenAI) pentru analiză conversațională. [5]

---

## 15. Instrucțiuni Cursor AI — Implementare modular

### 15.1 Setup structură inițial

**Prompt Cursor:**
```
"Crează structura de foldere și fișiere goale conform arhitecturii din secțiunea 4.1:
- config/ (config.yaml, strategy_params.yaml, risk_params.yaml)
- src/ (broker/, strategy/, risk/, backtest/, logging_utils/, utils/)
- data/ (historical/, backtests/, logs/)
- tests/
- requirements.txt template

Fă-o modulară și ready pentru implementare progresivă."
```

### 15.2 Implementare module (ordine sugerată)

**Ordine:**
1. `utils/` → helpers, config_loader, logger
2. `broker/` → ibkr_connector, data_provider, execution
3. `strategy/` → technical_analysis, signal_generator, filters
4. `risk/` → position_sizing, risk_checks
5. `backtest/` → backtester, metrics
6. `main.py`

**Exemplu prompt:**
```
"Implementează broker/ibkr_connector.py cu:
- Class IBKRConnector cu metode: connect(), disconnect(), is_connected()
- Reconectare automată la erori (exponential backoff)
- Logging complet
- Type hints și docstrings
Referință: ib_insync library, AsyncIO"
```

---

## 16. Versioning final

| Versiune | Data | Status |
|----------|------|--------|
| v1 | 2026-01-15 | Plan inițial |
| v2 | 2026-01-15 | Detalii GitHub + arhitectură |
| v3 | 2026-01-15 | Modular complet |
| v4 | 2026-01-15 | Paper→live plan 2-4 săptămâni |
| **v5.1** | **2026-01-15** | **FINAL: Hardware, GitHub, Codespaces, Kamatera $100 FREE, VPS Headless, Cursor AI** |

---

**Status v5.1: PRODUCTION READY**  
**Cost total prima lună: $0 (Kamatera $100 free trial)**  
**Next step: Crează GitHub repo și Codespaces!**

**Document: Specificație funcțională — Trading Bot AI cu Interactive Brokers**  
**Versiune: v5.1**  
**Status: READY FOR IMPLEMENTATION**  
**Ultima actualizare: 2026-01-15**
