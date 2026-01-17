## Arhitectură pe agenți – recapitulare și detaliere

Acest document extinde versiunea v5.1 și introduce o arhitectură clară pe agenți, ușor de implementat și testat incremental.

## Model general
Sistemul este împărțit în 3 agenți independenți. Fiecare agent are o singură responsabilitate. Agenții comunică prin fișiere JSON sau obiecte standardizate în memorie.

## Agentul 1 – Colector de date
Scopul tău este să colectezi date brute, fără interpretare.

Pași detaliați:
1. Inițializezi conexiunea IBKR.
2. Citești lista de simboluri din config.
3. Pentru fiecare simbol ceri date OHLCV.
4. Verifici completitudinea datelor.
5. Normalizezi formatul.
6. Salvezi datele local.

Output clar:
- CSV pentru verificare manuală.
- JSON pentru agenții următori.

Câmpuri obligatorii:
- symbol
- timeframe
- timestamp
- open
- high
- low
- close
- volume

## Agentul 2 – Analiză și semnale
Scopul tău este să interpretezi datele.

Pași:
1. Citești datele Agentului 1.
2. Calculezi EMA, volum mediu.
3. Aplici regulile de strategie.
4. Generezi semnal clar.
5. Salvezi semnalul.

Output:
- BUY, SELL sau HOLD.
- Preț intrare.
- TP și SL.
- Scor de încredere.

## Agentul 3 – Execuție
Scopul tău este să execuți ordinele aprobate.

Pași:
1. Primești semnalul.
2. Rulezi verificări de risc.
3. Calculezi mărimea poziției.
4. Trimiți ordinele către IBKR.
5. Monitorizezi poziția.
6. Loghezi rezultatul.

## Flux de lucru recomandat
1. Dezvolți și testezi Agentul 1.
2. Verifici outputul manual.
3. Treci la Agentul 2.
4. Testezi doar pe date istorice.
5. Activezi Agentul 3 doar în paper trading.

## Beneficii pentru tine
- Cod simplu.
- Debug rapid.
- Scalare ușoară.
- Potrivit pentru capital mic.

Document creat pentru implementare pas cu pas în Cursor.

