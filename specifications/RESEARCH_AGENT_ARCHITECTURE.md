# Research: Arhitectură Multi-Agent pentru Trading Bot

## 📚 Documentație și Exemple Găsite

### Conceptul de 3 Agenți

Arhitectura propusă cu 3 agenți separați este o **best practice** în trading automation:

1. **Agent 1: Data Collection Agent** (Culegere date)
2. **Agent 2: Decision Agent** (Analiză și decizie)
3. **Agent 3: Execution Agent** (Execuție și risk management)

---

## 🏗️ Arhitectură Recomandată

### Agent 1: Data Collection Agent
**Responsabilități:**
- Conectare la broker (IBKR)
- Colectare date de piață (prețuri, volume, istoric)
- Verificare status sesiune
- Verificare sold disponibil
- Stream live de date
- **Output:** Date brute, structurate (Bar, Quote, Tick)

**Module:**
- `broker/ibkr_connector.py` - Conexiune
- `broker/data_provider.py` - Colectare date
- **Nu conține logică de business!**

### Agent 2: Decision Agent
**Responsabilități:**
- Primește date de la Agent 1
- Calculează indicatori tehnici (EMA, RSI, volum)
- Aplică reguli de strategie
- Generează semnale (BUY/SELL/HOLD)
- **Output:** Signal cu entry_price, TP, SL, confidence

**Module:**
- `strategy/technical_analysis.py` - Calcul indicatori
- `strategy/signal_generator.py` - Logică decizie
- `strategy/filters.py` - Filtre (oră, trend, etc.)
- **Independent de broker!** (poate rula pe CSV pentru backtest)

### Agent 3: Execution Agent
**Responsabilități:**
- Primește Signal de la Agent 2
- Validează risc (daily loss, max trades, etc.)
- Calculează position sizing
- Trimite ordine către broker
- Gestionează poziții (monitorizare TP/SL)
- **Output:** Order, Position, Trade

**Module:**
- `risk/risk_manager.py` - Validări risc
- `risk/position_sizing.py` - Calcul sizing
- `broker/execution.py` - Execuție ordine
- **Nu conține logică de strategie!**

---

## 🔄 Flux de Comunicare

```
┌─────────────────┐
│  Agent 1        │
│  Data Collection│
└────────┬─────────┘
         │ Market Data (Bar, Quote)
         ▼
┌─────────────────┐
│  Agent 2        │
│  Decision        │
└────────┬─────────┘
         │ Signal (BUY/SELL/HOLD)
         ▼
┌─────────────────┐
│  Agent 3        │
│  Execution      │
└─────────────────┘
```

### Comunicare prin Interfețe

- **Agent 1 → Agent 2:** Printează `Bar`, `Quote` (models)
- **Agent 2 → Agent 3:** Printează `Signal` (model)
- **Agent 3 → Agent 1:** Cere date (sold, poziții) când e nevoie

---

## ✅ Avantaje Arhitectură Multi-Agent

1. **Testabilitate**
   - Fiecare agent poate fi testat independent
   - Mock-uim datele între agenți
   - Testăm Agent 2 fără conexiune la broker

2. **Dezvoltare Incrementală**
   - Dezvoltăm Agent 1 → testăm
   - Dezvoltăm Agent 2 → testăm (pe date mock)
   - Dezvoltăm Agent 3 → testăm (pe semnale mock)

3. **Scalabilitate**
   - Poți adăuga mai mulți agenți de decizie (strategii diferite)
   - Poți adăuga agenți de monitorizare
   - Poți rula agenți pe servere diferite

4. **Mentenanță**
   - Modificări în Agent 2 nu afectează Agent 3
   - Bug-uri izolate per agent
   - Cod mai clar și mai ușor de înțeles

5. **Backtesting**
   - Agent 2 poate rula pe date istorice (CSV)
   - Agent 3 poate rula în mod simulat
   - Testăm strategia fără risc

---

## 📋 Structură Proiect Actualizată

```
trading_bot/
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_collection_agent.py    # Agent 1
│   │   ├── decision_agent.py           # Agent 2
│   │   └── execution_agent.py          # Agent 3
│   │
│   ├── broker/                         # Folosit de Agent 1 și 3
│   │   ├── ibkr_connector.py
│   │   ├── data_provider.py
│   │   └── execution.py
│   │
│   ├── strategy/                       # Folosit de Agent 2
│   │   ├── technical_analysis.py
│   │   ├── signal_generator.py
│   │   └── filters.py
│   │
│   ├── risk/                           # Folosit de Agent 3
│   │   ├── risk_manager.py
│   │   └── position_sizing.py
│   │
│   ├── models/                         # Folosit de toți agenții
│   │   ├── market_data.py
│   │   ├── signal.py
│   │   └── trade.py
│   │
│   └── services/                       # Orchestrează agenții
│       └── trading_service.py
```

---

## 🎯 Implementare Recomandată

### Faza 1: Agent 1 (Data Collection)
- ✅ Models (Bar, Quote, Tick) - **DONE**
- ⏳ Broker connector
- ⏳ Data provider
- ⏳ Teste cu mock-uri

### Faza 2: Agent 2 (Decision)
- ⏳ Technical analysis
- ⏳ Signal generator
- ⏳ Teste pe date CSV (fără broker)

### Faza 3: Agent 3 (Execution)
- ⏳ Risk manager
- ⏳ Position sizing
- ⏳ Order execution
- ⏳ Teste cu mock broker

### Faza 4: Orchestrare
- ⏳ Trading service (combină toți agenții)
- ⏳ Main orchestrator
- ⏳ Teste de integrare

---

## 🔍 Best Practices Găsite

1. **Separation of Concerns**
   - Fiecare agent are o responsabilitate clară
   - Nu amestecăm colectarea datelor cu logica de decizie

2. **Dependency Injection**
   - Agenții comunică prin interfețe (models)
   - Nu dependențe directe între agenți

3. **Error Handling**
   - Agent 1: Reconectare automată la broker
   - Agent 2: Validare date înainte de analiză
   - Agent 3: Validare risc înainte de execuție

4. **Logging**
   - Fiecare agent loghează acțiunile sale
   - Format consistent pentru debugging

5. **Testing Strategy**
   - Unit tests pentru fiecare agent
   - Integration tests pentru comunicare între agenți
   - Mock-uri pentru dependențe externe

---

## 📝 Note pentru Specificație

Când scrii specificația detaliată, recomand să incluzi:

1. **Interfețe de comunicare**
   - Ce formate de date folosesc agenții
   - Ce evenimente declanșează acțiuni

2. **Error Handling**
   - Ce face Agent 1 dacă pierde conexiunea
   - Ce face Agent 2 dacă primește date invalide
   - Ce face Agent 3 dacă ordinul e respins

3. **State Management**
   - Cum ține Agent 1 starea conexiunii
   - Cum ține Agent 2 indicatorii calculați
   - Cum ține Agent 3 pozițiile deschise

4. **Testing Requirements**
   - Cum testăm fiecare agent independent
   - Cum testăm comunicarea între agenți
   - Cum simulăm scenarii de eroare

---

## 🚀 Concluzie

Arhitectura cu 3 agenți este **excelentă** pentru:
- ✅ Testabilitate
- ✅ Mentenanță
- ✅ Scalabilitate
- ✅ Dezvoltare incrementală

**Recomandare:** Continuăm cu această arhitectură! 🎯
