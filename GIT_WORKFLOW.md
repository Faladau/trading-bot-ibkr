# Git Workflow - Strategie de Dezvoltare

## 🌿 Strategie Branch-uri

Folosim **GitHub Flow** simplificat - ușor de urmărit, perfect pentru proiecte mici/medii.

### Branch-uri Principale

1. **`main`** - Cod stabil, funcțional, gata de deployment
   - ✅ Merge doar după testare
   - ✅ Cod review (dacă ești mai mulți)
   - ✅ Tag-uri pentru versiuni (v0.1.0, v0.2.0, etc.)

2. **`develop`** (opțional) - Integrare continuă
   - Pentru proiecte mai mari
   - Poți sări peste pentru început

### Branch-uri de Feature

**Format**: `feature/nume-modul` sau `feature/nume-functie`

Exemple:
- `feature/broker-connector` - Implementare conexiune IBKR
- `feature/strategy-ema` - Implementare strategie EMA
- `feature/risk-manager` - Implementare risk manager
- `feature/config-loader` - Implementare config loader

### Branch-uri de Fix

**Format**: `fix/nume-bug`

Exemple:
- `fix/ibkr-reconnect` - Fix reconectare IBKR
- `fix/position-sizing` - Fix calcul sizing

---

## 🔄 Workflow Recomandat

### 1. Început Lucru Nou (Feature)

```bash
# Actualizează main
git checkout main
git pull origin main

# Creează branch nou
git checkout -b feature/broker-connector

# Lucrează pe branch
# ... faci modificări ...
git add .
git commit -m "feat: implement IBKR connector with auto-reconnect"
```

### 2. Commit-uri Frecvente (Best Practice)

**Fă commit-uri mici și frecvente:**
- ✅ Un commit = o funcționalitate completă (chiar dacă mică)
- ✅ Mesaje clare: `feat:`, `fix:`, `refactor:`, `docs:`
- ✅ Evită commit-uri gigant (1000+ linii)

**Exemple mesaje commit:**
```bash
feat: add IBKR connector with connect/disconnect methods
feat: implement auto-reconnect with exponential backoff
fix: handle IBKR API timeout errors
refactor: extract connection logic to separate class
docs: update architecture.md with broker module details
test: add unit tests for IBKR connector
```

### 3. Push Periodic

```bash
# Push branch-ul tău (chiar dacă nu e gata)
git push origin feature/broker-connector

# Sau cu tracking
git push -u origin feature/broker-connector
```

**De ce?**
- ✅ Backup automat
- ✅ Poți continua de pe alt calculator
- ✅ Poți face PR (Pull Request) pentru review

### 4. Finalizare Feature

```bash
# Asigură-te că totul e commit-at
git status

# Testează local
python -m pytest tests/
# sau
python src/main.py --mode backtest

# Push final
git push origin feature/broker-connector
```

### 5. Merge în Main

**Opțiune A: Direct Merge (rapid)**
```bash
git checkout main
git pull origin main
git merge feature/broker-connector
git push origin main

# Șterge branch-ul local (opțional)
git branch -d feature/broker-connector
```

**Opțiune B: Pull Request (recomandat)**
1. Push branch pe GitHub
2. Creează Pull Request pe GitHub
3. Review cod (dacă ești mai mulți)
4. Merge PR
5. Șterge branch-ul

---

## 🎯 Strategie pentru Trading Bot

### Ordine Implementare (cu Branch-uri)

1. **`feature/utils`** - Utilitare de bază
   - `config_loader.py`
   - `logger.py`
   - `helpers.py`
   - Merge în `main` ✅

2. **`feature/models`** - Entități de date
   - `trade.py`, `signal.py`, `market_data.py`
   - Merge în `main` ✅

3. **`feature/broker-connector`** - Conexiune IBKR
   - `ibkr_connector.py`
   - Merge în `main` ✅

4. **`feature/broker-data`** - Data provider
   - `data_provider.py`
   - Merge în `main` ✅

5. **`feature/strategy-analysis`** - Analiză tehnică
   - `technical_analysis.py`
   - Merge în `main` ✅

6. **`feature/strategy-signals`** - Generare semnale
   - `signal_generator.py`
   - Merge în `main` ✅

7. **`feature/risk-manager`** - Risk management
   - `risk_manager.py`, `position_sizing.py`
   - Merge în `main` ✅

8. **`feature/execution`** - Execuție ordine
   - `execution.py`
   - Merge în `main` ✅

9. **`feature/trading-service`** - Orchestrare
   - `trading_service.py`
   - Merge în `main` ✅

10. **`feature/main-orchestrator`** - Entry point
    - `main.py` complet
    - Merge în `main` ✅

### Regulă: Un Modul = Un Branch

- ✅ Un branch per modul/funcționalitate
- ✅ Merge în `main` când modulul e complet și testat
- ✅ Dacă ai nevoie de rollback, e ușor să revii la commit anterior

---

## 🔙 Rollback (Revenire la Versiune Anterioară)

### Opțiune 1: Revert Commit (Recomandat)

```bash
# Vezi istoricul
git log --oneline

# Revert ultimul commit (creează commit nou care anulează)
git revert HEAD

# Sau revert un commit specific
git revert <commit-hash>
```

**Avantaje:**
- ✅ Păstrează istoricul complet
- ✅ Safe pentru branch-uri partajate
- ✅ Poți revert un revert

### Opțiune 2: Reset (Doar Local, Necomitat)

```bash
# Reset la commit anterior (păstrează modificările)
git reset --soft HEAD~1

# Reset la commit anterior (șterge modificările)
git reset --hard HEAD~1
```

**⚠️ Atenție:** Nu folosi `reset --hard` pe branch-uri deja push-ate!

### Opțiune 3: Checkout Versiune Anterioară

```bash
# Vezi toate commit-urile
git log --oneline

# Checkout la un commit specific (detached HEAD)
git checkout <commit-hash>

# Creează branch nou de la acel commit
git checkout -b fix/rollback-from-commit <commit-hash>
```

---

## 📋 Checklist înainte de Merge

- [ ] Cod funcționează local
- [ ] Teste trec (dacă există)
- [ ] Nu există erori de linting
- [ ] Commit-uri cu mesaje clare
- [ ] Push făcut pe branch
- [ ] Documentație actualizată (dacă e cazul)

---

## 🏷️ Tag-uri pentru Versiuni

```bash
# Creează tag pentru versiune
git tag -a v0.1.0 -m "First working version with broker connection"
git push origin v0.1.0

# Vezi toate tag-urile
git tag

# Checkout la o versiune specifică
git checkout v0.1.0
```

---

## 🚨 Situații Speciale

### Am făcut commit pe main direct (greșeală)

```bash
# Creează branch de la commit-ul curent
git branch feature/salvage-work

# Reset main la commit anterior
git checkout main
git reset --hard HEAD~1

# Continuă pe branch
git checkout feature/salvage-work
```

### Vreau să testez ceva rapid (fără branch)

```bash
# Stash modificările
git stash

# Testează ceva
# ...

# Revino la modificări
git stash pop
```

---

## 📊 Comenzi Utile

```bash
# Vezi branch-urile
git branch -a

# Vezi diferențe între branch-uri
git diff main..feature/broker-connector

# Vezi commit-urile dintr-un branch
git log feature/broker-connector --oneline

# Șterge branch local
git branch -d feature/broker-connector

# Șterge branch remote
git push origin --delete feature/broker-connector
```

---

## ✅ Best Practices

1. **Commit-uri mici și frecvente** - Mai ușor de rollback
2. **Un branch per feature** - Izolare, ușor de testat
3. **Merge doar când e gata** - Main rămâne stabil
4. **Mesaje commit clare** - `feat:`, `fix:`, `refactor:`
5. **Push periodic** - Backup automat
6. **Tag-uri pentru versiuni** - Puncte de referință

---

**Această strategie îți dă control complet și permite rollback ușor! 🚀**
