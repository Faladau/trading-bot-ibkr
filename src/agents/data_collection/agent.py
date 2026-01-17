"""
Data Collection Agent
Colectează date brute de piață, fără interpretare sau logică de business.

Responsabilități:
1. Inițializează conexiunea IBKR
2. Citește lista de simboluri din config
3. Colectează date OHLCV pentru fiecare simbol
4. Verifică completitudinea datelor
5. Normalizează formatul
6. Salvează datele local (CSV/JSON)

⚠️ IMPORTANT: Data Collection Agent este 100% market data. Nu verifică sold, capital sau orice legat de bani.
"""

# TODO: Implementare Agent 1 conform v6.0
