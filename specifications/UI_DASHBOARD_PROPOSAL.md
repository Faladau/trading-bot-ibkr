# Propunere UI Dashboard - Trading Bot v6.2

## 🎯 Scop Principal

**Ce vrem să obținem cu acest dashboard?**

1. **Monitorizare în timp real** - Să vezi ce face botul ACUM
2. **Control rapid** - Să poți opri/porni/modifica fără cod
3. **Înțelegere performanță** - Să vezi dacă strategia funcționează
4. **Debugging ușor** - Să găsești rapid problemele
5. **Confidență** - Să ai încredere că botul lucrează corect

---

## 📊 Structură Propusă (3 Niveluri de Prioritate)

### **NIVEL 1: MUST-HAVE (Implementăm ACUM)**

#### 1. **Header - Status Global** (Top Bar)
```
┌─────────────────────────────────────────────────────────────┐
│ 🟢 Bot ACTIVE | Last Update: 14:32:15 | Mode: PAPER         │
│ Agent 1: 🟢 ACTIVE | Agent 2: 🟡 IDLE | Agent 3: 🟡 IDLE    │
└─────────────────────────────────────────────────────────────┘
```

**Ce afișăm:**
- Status bot (ACTIVE/IDLE/ERROR) - culori clare
- Ultima actualizare (timestamp)
- Mod trading (PAPER/LIVE)
- Status fiecare agent (3 coloane mici)

**De ce e important:**
- Vezi instant dacă botul rulează
- Știi când s-au actualizat datele ultima dată
- Vezi care agent e activ

---

#### 2. **Secțiunea Principală - 3 Coloane**

##### **Coloana 1: Watchlist + Prețuri Live** (Stânga)
```
┌─────────────────────────┐
│ 📊 Watchlist            │
├─────────────────────────┤
│ AAPL  $175.32  +1.2% 🟢 │
│ MSFT  $412.85  -0.5% 🔴 │
│ TSLA  $245.10  +2.1% 🟢 │
└─────────────────────────┘
```

**Ce afișăm:**
- Lista simboluri din config
- Preț curent (din ultimul CSV)
- Change % (față de ultimul preț salvat)
- Indicator vizual (🟢/🔴) pentru direcție

**De ce e important:**
- Vezi rapid ce urmărește botul
- Observi mișcări importante
- Identifici simboluri cu probleme (fără date)

---

##### **Coloana 2: Poziții Active + P&L** (Centru)
```
┌─────────────────────────────┐
│ 💼 Poziții Active           │
├─────────────────────────────┤
│ AAPL: 100 shares @ $175.32   │
│ P&L: +$234.50 (+1.34%) 🟢   │
│ Entry: $173.00 | TP: $178.00│
│ SL: $171.00                  │
├─────────────────────────────┤
│ MSFT: 50 shares @ $412.85   │
│ P&L: -$45.20 (-0.22%) 🔴    │
└─────────────────────────────┘
```

**Ce afișăm:**
- Simbol + cantitate
- Preț intrare
- P&L curent (realizat + nerealizat)
- Take Profit / Stop Loss
- Durată poziție

**De ce e important:**
- Vezi exact ce ai deschis
- Monitorizezi riscul în timp real
- Știi când să intervii manual

---

##### **Coloana 3: Performance Metrics** (Dreapta)
```
┌─────────────────────────────┐
│ 📈 Performance              │
├─────────────────────────────┤
│ Daily P&L:    +$189.30 🟢   │
│ Weekly P&L:   +$1,234.50 🟢 │
│ Total P&L:    +$5,678.90 🟢 │
│ Win Rate:     62.5%          │
│ Max Drawdown: -3.2% 🔴       │
│ Sharpe Ratio: 1.45          │
└─────────────────────────────┘
```

**Ce afișăm:**
- P&L zilnic/săptămânal/total
- Win Rate (% tranzacții profitabile)
- Max Drawdown (cea mai mare scădere)
- Sharpe Ratio (risk-adjusted return)

**De ce e important:**
- Evaluezi performanța strategiei
- Identifici probleme (drawdown mare)
- Decizi dacă să continui sau să oprești

---

#### 3. **Controls + Activity Log** (Bottom)

##### **Controls** (Stânga jos)
```
┌─────────────────────────────┐
│ 🎮 Controls                 │
├─────────────────────────────┤
│ [▶️ START] [⏹️ STOP]        │
│ [⏸️ PAUSE] [🔄 RESET]       │
│                             │
│ ⚙️ Config:                  │
│ Mode: PAPER                 │
│ Risk Level: Medium          │
│ Max Position: $50k          │
│ Stop Loss: 2%               │
└─────────────────────────────┘
```

**Ce afișăm:**
- Butoane START/STOP/PAUSE/RESET
- Configurație curentă (read-only pentru moment)

**De ce e important:**
- Control rapid fără cod
- Verifici setările active

---

##### **Activity Log** (Dreapta jos)
```
┌─────────────────────────────┐
│ 📝 Recent Activity          │
├─────────────────────────────┤
│ 14:32:15 Agent 1: BUY AAPL  │
│ 14:30:42 Agent 3: Order OK  │
│ 14:28:09 Agent 2: SELL MSFT │
│ 14:25:33 Agent 1: Data OK   │
│ 14:22:18 System: Started    │
└─────────────────────────────┘
```

**Ce afișăm:**
- Ultimele 10-15 acțiuni
- Timestamp + Agent + Acțiune
- Color coding (verde=success, roșu=error)

**De ce e important:**
- Vezi ce s-a întâmplat recent
- Debugging rapid
- Transparență totală

---

### **NIVEL 2: NICE-TO-HAVE (După ce Nivel 1 funcționează)**

#### 4. **Charts / Grafice**
- **Equity Curve** - Evoluția contului în timp
- **P&L Daily Chart** - Bar chart zilnic
- **Price Chart** - Candlestick pentru simbol selectat

**De ce:**
- Vizualizare mai bună a trendurilor
- Identifici pattern-uri

---

#### 5. **Trade History Table**
- Tabel complet cu toate tranzacțiile
- Filtrare după: simbol, dată, profit/pierdere
- Export CSV

**De ce:**
- Analiză detaliată
- Raportare

---

#### 6. **Alerts / Notificări**
- Alertă când drawdown > 5%
- Alertă când win rate scade sub 50%
- Alertă când agent eșuează

**De ce:**
- Atenție la probleme critice
- Reacție rapidă

---

### **NIVEL 3: FUTURE (Când totul e stabil)**

#### 7. **Multi-Strategy View**
- Comparație între strategii
- Performance per strategie

#### 8. **Backtesting UI**
- Rulează backtest din UI
- Vizualizează rezultate

#### 9. **Settings Editor**
- Modifică config din UI
- Live preview

---

## 🎨 Design Principles

### **Culori:**
- 🟢 Verde = Profit / Success / Active
- 🔴 Roșu = Pierdere / Error / Stop
- 🟡 Galben = Warning / Idle
- 🔵 Albastru = Info / Monitoring

### **Layout:**
- **Desktop**: 3 coloane principale
- **Mobile**: Stack vertical (prioritizează status + controls)

### **Refresh:**
- Auto-refresh când bot e ACTIVE (10s)
- Manual refresh când bot e IDLE
- Checkbox pentru auto-refresh opțional

---

## 📋 Checklist Implementare

### **Faza 1: Core (ACUM)**
- [x] Status agenți (ACTIVE/IDLE)
- [x] Watchlist cu prețuri
- [x] Performance metrics (P&L, Win Rate)
- [x] Controls (START/STOP)
- [x] Activity log
- [ ] Poziții active (când Agent 3 e implementat)

### **Faza 2: Enhanced (DUPĂ Agent 2 + 3)**
- [ ] Charts (equity curve, P&L daily)
- [ ] Trade history table
- [ ] Alerts system
- [ ] Dark mode toggle

### **Faza 3: Advanced (VIITOR)**
- [ ] Multi-strategy view
- [ ] Backtesting UI
- [ ] Settings editor

---

## ❓ Întrebări pentru Decizie

1. **Ce metrici sunt cele mai importante pentru tine?**
   - P&L zilnic?
   - Win rate?
   - Max drawdown?
   - Altele?

2. **Ce vrei să vezi PRIMUL când deschizi dashboard-ul?**
   - Status bot?
   - Poziții active?
   - Performance?

3. **Cât de des vrei să verifici dashboard-ul?**
   - Continuu (live trading)?
   - O dată pe zi (review)?
   - Când apare o alertă?

4. **Ce acțiuni vrei să poți face din UI?**
   - Doar monitorizare?
   - Control (start/stop)?
   - Modificare strategie?

---

## 🎯 Țel Final

**Dashboard-ul ideal:**
- Se deschide în < 2 secunde
- Afișează tot ce e important la prima vedere
- Permite control rapid (start/stop în 1 click)
- Arată clar dacă ceva nu merge bine
- Funcționează pe telefon (responsive)

---

**Document creat:** 2026-01-17  
**Status:** PROPOSAL - Așteptăm feedback pentru a finaliza structura
