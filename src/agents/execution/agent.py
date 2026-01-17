"""
Execution Agent
Primește semnale, validează riscul, calculează sizing, trimite ordine și monitorizează poziții.

Responsabilități:
1. Primește semnalul de la Decision Agent
2. Rulează verificări de risc (daily loss, max trades, etc.)
3. Calculează mărimea poziției
4. Trimite ordinele către IBKR
5. Monitorizează poziția
6. Loghează rezultatul

⚠️ IMPORTANT: Execution Agent este singurul care verifică sold/capital.
Execution Agent decide când și cum trimite ordinul (inclusiv pentru ieșire).
"""

# TODO: Implementare Agent 3 conform v6.0
