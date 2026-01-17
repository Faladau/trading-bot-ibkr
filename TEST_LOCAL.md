# Testare Locală - Trading Bot Dashboard

## 🚀 Rulare Locală

### 1. Activează virtual environment
```bash
# Windows PowerShell
.\trading_bot_env\Scripts\Activate.ps1

# Sau Windows CMD
trading_bot_env\Scripts\activate.bat
```

### 2. Rulează Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```

Dashboard-ul va fi disponibil la: `http://localhost:8501`

---

## 🔍 Testare Modificări

### Workflow Recomandat:
1. **Modifică codul** (CSS, Python, etc.)
2. **Salvează fișierul**
3. **Streamlit se reîncarcă automat** (vezi terminalul)
4. **Refresh browser** (F5) pentru a vedea modificările
5. **Testează** - verifică că totul funcționează
6. **Doar când e OK** → `git commit` și `git push`

---

## 🐛 Debugging

### Dacă nu se vede layout-ul pe 80%:
1. Deschide **Developer Tools** în browser (F12)
2. Tab **Console** - verifică erori JavaScript
3. Tab **Elements** - inspectează `section[data-testid="stAppViewContainer"]`
4. Verifică că are `max-width: 80%` aplicat

### Dacă textul nu e alb:
1. Developer Tools → Elements
2. Inspectează elementul cu text invizibil
3. Verifică că CSS-ul nostru este aplicat (cu `!important`)

---

## 📝 Comenzi Utile

```bash
# Verifică sintaxa Python
python -m py_compile src/ui/dashboard.py

# Verifică importuri
python -c "from src.ui.dashboard import main; print('OK')"

# Rulează cu port custom
streamlit run streamlit_app.py --server.port 8502
```

---

## ✅ Checklist înainte de Push

- [ ] Dashboard-ul rulează fără erori
- [ ] Layout-ul este pe 80% după refresh
- [ ] Textul este alb și lizibil
- [ ] Toate componentele se afișează corect
- [ ] Nu sunt erori în Console (F12)

**Doar după ce toate sunt OK → `git commit` și `git push`**
