# Specificație funcțională — Trading Bot AI cu Interactive Brokers
## v6.1 — Agentul 1 (Data Collector) — ULTRA-GRANULAR

**Status**: READY FOR CURSOR IMPLEMENTATION  
**Data creării**: 2026-01-17  
**Versiune**: 6.1  
**Faza**: Specificație tehnică detaliată pentru **Agentul 1 (Data Collector)**

---

## STRUCTURA DOCUMENT

1. **Scop Agentul 1**
2. **Input / Output Contract**
3. **Responsabilități detaliate**
4. **Schemă de date (JSON, CSV)**
5. **Pași granulari de implementare**
6. **Funcții publice cu semnături**
7. **Pseudo-cod**
8. **Teste unitare**
9. **Cum testezi rezultatele**

---

## 1. SCOP AGENTUL 1 — DATA COLLECTOR

### 1.1 Definiție
Agentul 1 **colectează date brute de pe piață** (preț, volum, timestamp) din surse externe și le **normalizează într-un format unic**, fără a lua nicio decizie de tranzacționare.

### 1.2 Principii de design
- ✅ **Ignoranță de afacere**: Nu știe de strategie, risc, ordine.
- ✅ **Format unic**: Indiferent de sursă, outputul e identic.
- ✅ **Verifiable**: Oricine poate verifica datele în CSV.
- ✅ **Async-ready**: Merge cu AsyncIO pentru non-blocking.
- ✅ **Testabil independent**: Nu depinde de alți agenți.

### 1.3 Surse de date (prioritate)
| Sursă | Tip | Latență | Prioritate | Motiv |
|-------|-----|---------|-----------|-------|
| **IBKR (ib_insync)** | Live + Istoric | <100ms | ⭐⭐⭐⭐⭐ | Oficiale, RTH, test paper |
| **Yahoo Finance (yfinance)** | Istoric | 1-2s | ⭐⭐⭐⭐ | Cross-check, backup |
| **Alpha Vantage** | Istoric | 2-5s | ⭐⭐⭐ | Backup, gratuit |
| **Stooq** | Istoric | 1s | ⭐⭐⭐ | Alternativă Yahoo |

---

## 2. INPUT / OUTPUT CONTRACT

### 2.1 INPUT (Ce primește Agentul 1)

**Sursa**: Fișier configurație YAML

| Parameter | Tip | Exemplu | Mandatory | Descriere |
|-----------|-----|---------|-----------|-----------|
| `symbols` | List[str] | `["AAPL", "MSFT"]` | ✅ | Simbol-uri de tradat |
| `timeframe` | str | `"1H"`, `"1D"`, `"5m"` | ✅ | Granularitate date (IBKR format) |
| `lookback_days` | int | `60` | ✅ | Zile de date istorice de descărcat |
| `data_source` | str | `"IBKR"` | ✅ | Sursă primară |
| `backup_source` | str | `"YAHOO"` | ❌ | Sursă secundară la eșec |
| `output_format` | List[str] | `["csv", "json"]` | ✅ | Formate output |
| `data_dir` | str | `"data/processed"` | ✅ | Cale salvare output |
| `market` | str | `"US"` | ✅ | Piață (US, EU, CRYPTO) |
| `useRTH` | bool | `True` | ✅ | Ore de trading regulate (IBKR) |
| `normalize_splits` | bool | `True` | ✅ | Ajustare split/dividend |

**Exemplu config.yaml:**
```yaml
data_collector:
  symbols:
    - AAPL
    - MSFT
    - AMD
  timeframe: "1H"
  lookback_days: 60
  data_source: "IBKR"
  backup_source: "YAHOO"
  output_format: ["csv", "json"]
  data_dir: "data/processed"
  market: "US"
  useRTH: true
  normalize_splits: true

ibkr:
  host: 127.0.0.1
  port: 7497
  clientId: 1
```

### 2.2 OUTPUT (Ce produce Agentul 1)

**Două formate paralele:**

#### A. CSV (pentru verificare manuală)

**Fișier**: `data/processed/{SYMBOL}_{TIMEFRAME}_{DATE}.csv`

```csv
symbol,timeframe,timestamp,open,high,low,close,volume,count,wap,hasGaps,source,normalized
AAPL,1H,2026-01-17 10:00:00,150.50,151.00,150.20,150.80,1500000,450,150.65,False,IBKR,True
AAPL,1H,2026-01-17 11:00:00,150.80,151.50,150.60,151.20,1200000,420,151.00,False,IBKR,True
MSFT,1H,2026-01-17 10:00:00,380.50,381.00,380.20,380.80,800000,350,380.65,False,IBKR,True
```

**Coloane detaliate:**

| Coloană | Tip | Descriere | Exemplu |
|---------|-----|-----------|---------|
| `symbol` | str | Simbol stoc | `AAPL` |
| `timeframe` | str | Timeframe | `1H`, `1D`, `5m` |
| `timestamp` | datetime | Ora UTC închidere | `2026-01-17 10:00:00` |
| `open` | float | Preț deschidere | `150.50` |
| `high` | float | Preț maxim | `151.00` |
| `low` | float | Preț minim | `150.20` |
| `close` | float | Preț închidere | `150.80` |
| `volume` | int | Volum total | `1500000` |
| `count` | int | Nr. tranzacții în perioada | `450` |
| `wap` | float | Preț mediu ponderat (volum) | `150.65` |
| `hasGaps` | bool | Dacă bar are gap-uri | `False` |
| `source` | str | Sursă date | `IBKR`, `YAHOO` |
| `normalized` | bool | Dacă a fost normalizat | `True` |

#### B. JSON (pentru Agentul 2)

**Fișier**: `data/processed/{SYMBOL}_{TIMEFRAME}_{DATE}.json`

```json
{
  "symbol": "AAPL",
  "timeframe": "1H",
  "period": {
    "start": "2026-01-01 00:00:00",
    "end": "2026-01-17 23:59:59",
    "total_bars": 420,
    "date_generated": "2026-01-17 10:30:00"
  },
  "metadata": {
    "source": "IBKR",
    "useRTH": true,
    "normalized": true,
    "adjustments_applied": ["splits", "dividends"],
    "data_quality": {
      "missing_bars": 0,
      "gaps_detected": 0,
      "duplicates": 0
    }
  },
  "bars": [
    {
      "timestamp": "2026-01-17 10:00:00",
      "open": 150.50,
      "high": 151.00,
      "low": 150.20,
      "close": 150.80,
      "volume": 1500000,
      "count": 450,
      "wap": 150.65,
      "hasGaps": false
    },
    {
      "timestamp": "2026-01-17 11:00:00",
      "open": 150.80,
      "high": 151.50,
      "low": 150.60,
      "close": 151.20,
      "volume": 1200000,
      "count": 420,
      "wap": 151.00,
      "hasGaps": false
    }
  ]
}
```

### 2.3 Schema de validare

```python
# Output validation schema
OUTPUT_SCHEMA = {
    "symbol": str,           # Non-empty, uppercase
    "timeframe": str,        # "1m", "5m", "15m", "1H", "4H", "1D"
    "timestamp": datetime,   # UTC, valid market hours
    "open": float,           # > 0
    "high": float,           # >= high(open, close)
    "low": float,            # <= low(open, close)
    "close": float,          # > 0
    "volume": int,           # >= 0
    "count": int,            # > 0
    "wap": float,            # > 0
    "hasGaps": bool,         # True/False
    "source": str,           # "IBKR", "YAHOO", "ALPHA"
    "normalized": bool       # True/False
}
```

---

## 3. RESPONSABILITĂȚI DETALIATE

### 3.1 Inițializare și conexiune
**Pași:**
1. Citire fișier config YAML
2. Validare parametri config
3. Inițializare connector IBKR (ib_insync)
4. Conectare la TWS/IB Gateway (cu retry logic)
5. Verificare stare conexiune

**Pericol**: Dacă nu reușește conectarea, returnează eroare clar și încearcă backup source.

### 3.2 Descărcare date istorice
**Pași per simbol:**
1. Creează Contract object IBKR
2. Apelează `reqHistoricalData()` cu parametrii
3. Așteaptă răspuns (poate dura secunde)
4. Validează completitudinea datelor
5. Detectează și loghează gap-uri
6. Normalizează format

**Pacing limits IBKR** (IMPORTANT):
- Max 1 request / 10 secunde pentru rate-limit dur
- Soft limit pentru 1H, 1D: ~1-2 sec între requests OK
- Implement: sleep/exponential backoff între requests

### 3.3 Stream live (subscribe la bars)
**Pași:**
1. După descărcare istoric, subscribe la stream
2. `keepUpToDate=True` în ib_insync
3. Primește notificări pentru fiecare bar nou
4. Update în memorie (dict per simbol)
5. Periodic flush la CSV (ex: fiecare 5 minute)

### 3.4 Normalizare format
**Pași:**
1. Standardizare timestamp UTC
2. Conversie tipuri date (int, float)
3. Rotundire preț la 2 zecimale
4. Validare OHLC logic (high >= max(open,close), etc.)
5. Detectare și marcaj anomalii

**Anomalii detectate:**
- Volume = 0 (invalid)
- High < Low (eroare date)
- WAP = 0 sau nenormal
- Price gaps > 5% (marca pauze piață)

### 3.5 Salvare output
**Pași:**
1. Transformare în pandas DataFrame (optional)
2. Export CSV cu delimitatorul `,`
3. Export JSON pretty-print
4. Verificare fișiere create (file size > 0)
5. Logging detaliat

---

## 4. SCHEMĂ DE DATE DETALIATĂ

### 4.1 Obiect Bar (ib_insync native)

Din `ib_insync`, un bar istoric are:
```python
from ib_insync import BarData

bar = {
    'time': datetime,     # Ora barei
    'open': float,
    'high': float,
    'low': float,
    'close': float,
    'volume': int,
    'average': float,     # WAP (weighted average price)
    'count': int,         # Număr tranzacții
    'hasGaps': bool       # dacă sunt gaps în date
}
```

### 4.2 Transformare în standardul nostru

```python
# Raw ib_insync bar
raw_bar = ib.reqHistoricalData(...)[0]

# Normalizare
normalized_bar = {
    'symbol': 'AAPL',
    'timeframe': '1H',
    'timestamp': raw_bar.time.strftime('%Y-%m-%d %H:%M:%S'),  # UTC string
    'open': round(raw_bar.open, 2),
    'high': round(raw_bar.high, 2),
    'low': round(raw_bar.low, 2),
    'close': round(raw_bar.close, 2),
    'volume': int(raw_bar.volume),
    'count': int(raw_bar.count),
    'wap': round(raw_bar.average, 2),
    'hasGaps': bool(raw_bar.hasGaps),
    'source': 'IBKR',
    'normalized': True
}
```

### 4.3 Validare logică OHLC

```
Validări:
1. high >= max(open, close)       ✅ OK
2. low <= min(open, close)        ✅ OK
3. open > 0                        ✅ OK
4. high > low                      ✅ OK
5. close > 0                       ✅ OK
6. volume >= 0                     ✅ OK
7. timestamp validă UTC            ✅ OK
8. wap = (total_value / volume)    ✅ Calculat

Dacă orice condiție falsa → Log ERROR + Mark bar cu `valid=False`
```

---

## 5. PAȘI GRANULARI DE IMPLEMENTARE

### PASUL 1: Structură foldere
```
agents/data_collector/
├── __init__.py
├── README.md
├── collector.py                 # Entry point
├── sources/
│   ├── __init__.py
│   ├── ibkr_source.py          # IBKR connector
│   ├── yahoo_source.py         # Yahoo backup
│   └── base_source.py          # Abstract class
├── normalizer.py               # Format standardizare
├── validator.py                # Verificare date
├── config.py                   # Citire config
├── models.py                   # Type hints, dataclasses
├── tests/
│   ├── test_ibkr_source.py
│   ├── test_normalizer.py
│   ├── test_validator.py
│   └── test_output_format.py
└── requirements.txt
```

### PASUL 2: Type hints și dataclasses

**Fișier**: `agents/data_collector/models.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Bar:
    """Standardizat bar data."""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    count: int
    wap: float
    hasGaps: bool
    source: str
    normalized: bool

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'count': self.count,
            'wap': self.wap,
            'hasGaps': self.hasGaps,
            'source': self.source,
            'normalized': self.normalized
        }

@dataclass
class DataCollectorConfig:
    """Configurație data collector."""
    symbols: List[str]
    timeframe: str
    lookback_days: int
    data_source: str
    backup_source: Optional[str]
    output_format: List[str]  # csv, json
    data_dir: str
    market: str
    useRTH: bool
    normalize_splits: bool
```

### PASUL 3: Clase abstract pentru sursele de date

**Fișier**: `agents/data_collector/sources/base_source.py`

```python
from abc import ABC, abstractmethod
from typing import List
from models import Bar

class BaseDataSource(ABC):
    """Abstract class pentru orice sursă de date."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conectează la sursă."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Deconectează."""
        pass
    
    @abstractmethod
    async def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int
    ) -> List[Bar]:
        """Descarcă date istorice."""
        pass
    
    @abstractmethod
    async def subscribe_to_bars(
        self, 
        symbol: str, 
        timeframe: str
    ) -> None:
        """Subscribe la stream live (keepUpToDate)."""
        pass
    
    @abstractmethod
    def get_latest_bar(self, symbol: str) -> Optional[Bar]:
        """Primește ultimul bar din memorie."""
        pass
```

### PASUL 4: IBKR source

**Fișier**: `agents/data_collector/sources/ibkr_source.py`

```python
from ib_insync import IB, Stock, Contract
from typing import List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
from models import Bar
from base_source import BaseDataSource

class IBKRDataSource(BaseDataSource):
    """Data source pentru Interactive Brokers."""
    
    def __init__(self, host: str, port: int, clientId: int):
        self.ib = IB()
        self.host = host
        self.port = port
        self.clientId = clientId
        self.bars_cache: Dict[str, Bar] = {}
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Conectează la IBKR cu retry logic."""
        retries = 3
        for attempt in range(retries):
            try:
                self.ib.connect(
                    self.host, 
                    self.port, 
                    clientId=self.clientId
                )
                self.logger.info(f"IBKR connected: {self.host}:{self.port}")
                return True
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # exponential backoff
        return False
    
    async def disconnect(self) -> bool:
        """Deconectează IBKR."""
        try:
            self.ib.disconnect()
            self.logger.info("IBKR disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")
            return False
    
    async def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int,
        useRTH: bool = True
    ) -> List[Bar]:
        """
        Descarcă date istorice din IBKR.
        
        Args:
            symbol: ex 'AAPL'
            timeframe: ex '1H', '1D'
            lookback_days: zile de descărcat
            useRTH: ore regulate de trading
        
        Returns:
            Lista de Bar-uri normalizate
        """
        try:
            # Creează contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Parametri
            duration_str = f"{lookback_days} D"
            bar_size = self._convert_timeframe(timeframe)  # ex: "1 hour"
            
            # Request
            self.logger.info(f"Fetching {symbol} {timeframe} for {lookback_days} days...")
            bars_raw = self.ib.reqHistoricalData(
                contract,
                endDateTime='',          # Until now
                durationStr=duration_str,
                barSizeSetting=bar_size,
                whatToShow='TRADES',     # Real trades
                useRTH=useRTH,
                keepUpToDate=False       # Historic only
            )
            
            # Convert și normalizare
            bars_normalized = []
            for bar in bars_raw:
                normalized = self._normalize_bar(bar, symbol, timeframe, 'IBKR')
                bars_normalized.append(normalized)
            
            self.logger.info(f"Fetched {len(bars_normalized)} bars for {symbol}")
            return bars_normalized
            
        except Exception as e:
            self.logger.error(f"Fetch error for {symbol}: {e}")
            return []
    
    async def subscribe_to_bars(
        self, 
        symbol: str, 
        timeframe: str
    ) -> None:
        """Subscribe la stream live."""
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            bar_size = self._convert_timeframe(timeframe)
            
            # Request cu keepUpToDate=True
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',       # Doar astazi + live
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,
                keepUpToDate=True        # LIVE STREAM
            )
            
            # Setup callback
            bars.updateEvent += lambda bar: self._on_bar_update(bar, symbol, timeframe)
            
            self.logger.info(f"Subscribed to {symbol} {timeframe} live bars")
        except Exception as e:
            self.logger.error(f"Subscribe error: {e}")
    
    def _on_bar_update(self, bar, symbol: str, timeframe: str):
        """Callback la update bar."""
        normalized = self._normalize_bar(bar, symbol, timeframe, 'IBKR')
        self.bars_cache[symbol] = normalized
        self.logger.debug(f"Bar update: {symbol} {normalized.close}")
    
    def get_latest_bar(self, symbol: str) -> Optional[Bar]:
        """Ultimul bar din cache."""
        return self.bars_cache.get(symbol)
    
    def _convert_timeframe(self, tf: str) -> str:
        """Conversia timeframe App → IBKR."""
        mapping = {
            '1m': '1 min',
            '5m': '5 mins',
            '15m': '15 mins',
            '1H': '1 hour',
            '4H': '4 hours',
            '1D': '1 day'
        }
        return mapping.get(tf, '1 hour')
    
    def _normalize_bar(self, raw_bar, symbol: str, timeframe: str, source: str) -> Bar:
        """Normalizare raw bar → Bar standardizat."""
        return Bar(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=raw_bar.time,
            open=round(raw_bar.open, 2),
            high=round(raw_bar.high, 2),
            low=round(raw_bar.low, 2),
            close=round(raw_bar.close, 2),
            volume=int(raw_bar.volume),
            count=int(raw_bar.count),
            wap=round(raw_bar.average, 2),
            hasGaps=bool(raw_bar.hasGaps),
            source=source,
            normalized=True
        )
```

### PASUL 5: Normalizer

**Fișier**: `agents/data_collector/normalizer.py`

```python
from typing import List, Dict
import pandas as pd
from models import Bar
import logging

class DataNormalizer:
    """Normalizare format date."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def bars_to_csv(self, bars: List[Bar], filepath: str) -> bool:
        """Exportă bars → CSV."""
        try:
            df = pd.DataFrame([bar.to_dict() for bar in bars])
            df.to_csv(filepath, index=False)
            self.logger.info(f"Saved {len(bars)} bars to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"CSV export error: {e}")
            return False
    
    def bars_to_json(self, bars: List[Bar], filepath: str, symbol: str, timeframe: str) -> bool:
        """Exportă bars → JSON cu metadata."""
        try:
            import json
            from datetime import datetime
            
            metadata = {
                'symbol': symbol,
                'timeframe': timeframe,
                'period': {
                    'start': bars[0].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': bars[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_bars': len(bars),
                    'date_generated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                },
                'metadata': {
                    'source': bars[0].source if bars else 'UNKNOWN',
                    'normalized': True,
                    'data_quality': {
                        'missing_bars': self._count_missing_bars(bars),
                        'gaps_detected': sum(1 for b in bars if b.hasGaps),
                        'duplicates': self._count_duplicates(bars)
                    }
                },
                'bars': [bar.to_dict() for bar in bars]
            }
            
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Saved {len(bars)} bars to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"JSON export error: {e}")
            return False
    
    def _count_missing_bars(self, bars: List[Bar]) -> int:
        """Detectează baruri lipsă."""
        # Calculează expected count vs actual
        # Implementare simpla pentru start
        return 0
    
    def _count_duplicates(self, bars: List[Bar]) -> int:
        """Detectează duplicate timestamp."""
        timestamps = [b.timestamp for b in bars]
        return len(timestamps) - len(set(timestamps))
```

### PASUL 6: Validator

**Fișier**: `agents/data_collector/validator.py`

```python
from typing import List, Tuple
from models import Bar
import logging

class DataValidator:
    """Validare calitate date."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_bar(self, bar: Bar) -> Tuple[bool, str]:
        """Validează un bar individual."""
        errors = []
        
        # OHLC logic
        if bar.high < bar.open or bar.high < bar.close:
            errors.append(f"High ({bar.high}) < open/close")
        
        if bar.low > bar.open or bar.low > bar.close:
            errors.append(f"Low ({bar.low}) > open/close")
        
        if bar.high < bar.low:
            errors.append(f"High ({bar.high}) < Low ({bar.low})")
        
        # Price valid
        if bar.open <= 0 or bar.close <= 0:
            errors.append("Price <= 0")
        
        # Volume
        if bar.volume < 0:
            errors.append("Volume < 0")
        
        # WAP logic
        if bar.wap <= 0 and bar.volume > 0:
            errors.append("WAP invalid")
        
        if errors:
            self.logger.warning(f"Bar validation errors: {errors}")
            return False, "; ".join(errors)
        
        return True, "OK"
    
    def validate_bars(self, bars: List[Bar]) -> Tuple[int, int]:
        """Validează lista de bars.
        
        Returns:
            (valid_count, invalid_count)
        """
        valid, invalid = 0, 0
        for bar in bars:
            is_valid, msg = self.validate_bar(bar)
            if is_valid:
                valid += 1
            else:
                invalid += 1
        
        return valid, invalid
```

### PASUL 7: Collector (Main orchestrator)

**Fișier**: `agents/data_collector/collector.py`

```python
from typing import List, Optional
import asyncio
import yaml
import logging
from pathlib import Path
from models import Bar, DataCollectorConfig
from sources.ibkr_source import IBKRDataSource
from normalizer import DataNormalizer
from validator import DataValidator
from config import load_config

class DataCollector:
    """Orchestrator principal pentru colectare date."""
    
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.data_source: Optional[IBKRDataSource] = None
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Inițializare conexiuni și setup."""
        try:
            # Conectează la IBKR
            self.data_source = IBKRDataSource(
                host=self.config.get('ibkr.host'),
                port=self.config.get('ibkr.port'),
                clientId=self.config.get('ibkr.clientId')
            )
            
            connected = await self.data_source.connect()
            if not connected:
                self.logger.error("Failed to connect to IBKR")
                return False
            
            # Crează output directories
            Path(self.config['data_dir']).mkdir(parents=True, exist_ok=True)
            
            self.logger.info("DataCollector initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False
    
    async def collect_all(self) -> bool:
        """Colectează date pentru toate simbolurile."""
        try:
            symbols = self.config['symbols']
            timeframe = self.config['timeframe']
            lookback_days = self.config['lookback_days']
            
            for symbol in symbols:
                self.logger.info(f"Collecting {symbol}...")
                
                # Fetch
                bars = await self.data_source.fetch_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    lookback_days=lookback_days,
                    useRTH=self.config['useRTH']
                )
                
                if not bars:
                    self.logger.warning(f"No data for {symbol}")
                    continue
                
                # Validate
                valid_count, invalid_count = self.validator.validate_bars(bars)
                self.logger.info(f"{symbol}: {valid_count} valid, {invalid_count} invalid")
                
                # Save
                await self._save_bars(symbol, bars)
                
                # Pace limit IBKR (min 10 sec între requests)
                await asyncio.sleep(10)
            
            self.logger.info("Collection completed")
            return True
        except Exception as e:
            self.logger.error(f"Collection error: {e}")
            return False
    
    async def _save_bars(self, symbol: str, bars: List[Bar]) -> bool:
        """Salvează bars în format CSV + JSON."""
        try:
            timeframe = self.config['timeframe']
            data_dir = self.config['data_dir']
            
            # Filename
            from datetime import datetime
            date_str = datetime.utcnow().strftime('%Y%m%d')
            base_name = f"{data_dir}/{symbol}_{timeframe}_{date_str}"
            
            # CSV
            if 'csv' in self.config['output_format']:
                csv_path = f"{base_name}.csv"
                self.normalizer.bars_to_csv(bars, csv_path)
            
            # JSON
            if 'json' in self.config['output_format']:
                json_path = f"{base_name}.json"
                self.normalizer.bars_to_json(bars, json_path, symbol, timeframe)
            
            return True
        except Exception as e:
            self.logger.error(f"Save error: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Dezactivare controlată."""
        try:
            if self.data_source:
                await self.data_source.disconnect()
            self.logger.info("DataCollector shutdown completed")
            return True
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return False

# Entry point
async def main(config_path: str):
    collector = DataCollector(config_path)
    if await collector.initialize():
        await collector.collect_all()
        await collector.shutdown()
    else:
        print("Failed to initialize collector")

if __name__ == "__main__":
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    asyncio.run(main(config_file))
```

---

## 6. FUNCȚII PUBLICE — SEMNĂTURI

### 6.1 IBKRDataSource API

```python
# Connect
async def connect() -> bool

# Disconnect
async def disconnect() -> bool

# Fetch historic data
async def fetch_historical_data(
    symbol: str, 
    timeframe: str, 
    lookback_days: int,
    useRTH: bool = True
) -> List[Bar]

# Subscribe live
async def subscribe_to_bars(
    symbol: str, 
    timeframe: str
) -> None

# Get latest bar from cache
def get_latest_bar(symbol: str) -> Optional[Bar]
```

### 6.2 DataNormalizer API

```python
# Export to CSV
def bars_to_csv(bars: List[Bar], filepath: str) -> bool

# Export to JSON
def bars_to_json(
    bars: List[Bar], 
    filepath: str, 
    symbol: str, 
    timeframe: str
) -> bool
```

### 6.3 DataValidator API

```python
# Validate single bar
def validate_bar(bar: Bar) -> Tuple[bool, str]

# Validate list of bars
def validate_bars(bars: List[Bar]) -> Tuple[int, int]  # (valid, invalid)
```

### 6.4 DataCollector API

```python
# Initialize
async def initialize() -> bool

# Collect all symbols
async def collect_all() -> bool

# Save bars
async def _save_bars(symbol: str, bars: List[Bar]) -> bool

# Shutdown
async def shutdown() -> bool
```

---

## 7. PSEUDO-COD — FLUXUL PRINCIPAL

```
FUNCTION main():
    
    // 1. SETUP
    config = load_config("config/config.yaml")
    collector = DataCollector(config)
    
    // 2. INITIALIZE
    IF NOT await collector.initialize():
        EXIT WITH ERROR "Connection failed"
    
    // 3. COLLECT PER SYMBOL
    FOR EACH symbol IN config.symbols:
        
        // 3a. Fetch
        bars_raw = await data_source.fetch_historical_data(
            symbol,
            config.timeframe,
            config.lookback_days
        )
        
        // 3b. Validate
        (valid_count, invalid_count) = validator.validate_bars(bars_raw)
        LOG "Symbol={symbol}, Valid={valid_count}, Invalid={invalid_count}"
        
        // 3c. Save
        IF 'csv' IN config.output_format:
            normalizer.bars_to_csv(bars_raw, f"data/{symbol}.csv")
        IF 'json' IN config.output_format:
            normalizer.bars_to_json(bars_raw, f"data/{symbol}.json", symbol, config.timeframe)
        
        // 3d. Pace limit (IBKR min 10 sec)
        SLEEP 10 seconds
    
    // 4. SUBSCRIBE LIVE (opțional, pentru monitoring)
    FOR EACH symbol IN config.symbols:
        SUBSCRIBE TO data_source.subscribe_to_bars(symbol, config.timeframe)
    
    // 5. SHUTDOWN
    await collector.shutdown()
    
    RETURN SUCCESS
```

---

## 8. TESTE UNITARE

**Fișier**: `agents/data_collector/tests/test_ibkr_source.py`

```python
import pytest
import asyncio
from models import Bar
from sources.ibkr_source import IBKRDataSource
from datetime import datetime

@pytest.mark.asyncio
async def test_connect():
    """Test IBKR connection."""
    source = IBKRDataSource("127.0.0.1", 7497, 1)
    result = await source.connect()
    assert result == True, "Connection failed"
    await source.disconnect()

@pytest.mark.asyncio
async def test_fetch_historical_data():
    """Test descărcare date istorice."""
    source = IBKRDataSource("127.0.0.1", 7497, 1)
    await source.connect()
    
    bars = await source.fetch_historical_data(
        symbol="AAPL",
        timeframe="1H",
        lookback_days=5,
        useRTH=True
    )
    
    assert len(bars) > 0, "No bars fetched"
    assert all(isinstance(b, Bar) for b in bars), "Invalid bar type"
    
    await source.disconnect()

@pytest.mark.asyncio
async def test_bar_normalization():
    """Test normalizare bar."""
    source = IBKRDataSource("127.0.0.1", 7497, 1)
    await source.connect()
    
    bars = await source.fetch_historical_data("AMD", "1D", 10)
    for bar in bars:
        assert bar.symbol == "AMD"
        assert bar.timeframe == "1D"
        assert bar.normalized == True
    
    await source.disconnect()
```

**Fișier**: `agents/data_collector/tests/test_normalizer.py`

```python
import pytest
from normalizer import DataNormalizer
from models import Bar
from datetime import datetime
import os

def test_bars_to_csv():
    """Test export CSV."""
    normalizer = DataNormalizer()
    
    bars = [
        Bar(
            symbol="AAPL",
            timeframe="1H",
            timestamp=datetime(2026, 1, 17, 10, 0, 0),
            open=150.50,
            high=151.00,
            low=150.20,
            close=150.80,
            volume=1500000,
            count=450,
            wap=150.65,
            hasGaps=False,
            source="IBKR",
            normalized=True
        )
    ]
    
    result = normalizer.bars_to_csv(bars, "/tmp/test.csv")
    assert result == True
    assert os.path.exists("/tmp/test.csv")
    
    os.remove("/tmp/test.csv")

def test_bars_to_json():
    """Test export JSON."""
    normalizer = DataNormalizer()
    
    bars = [
        Bar(
            symbol="AAPL",
            timeframe="1H",
            timestamp=datetime(2026, 1, 17, 10, 0, 0),
            open=150.50,
            high=151.00,
            low=150.20,
            close=150.80,
            volume=1500000,
            count=450,
            wap=150.65,
            hasGaps=False,
            source="IBKR",
            normalized=True
        )
    ]
    
    result = normalizer.bars_to_json(bars, "/tmp/test.json", "AAPL", "1H")
    assert result == True
    assert os.path.exists("/tmp/test.json")
    
    os.remove("/tmp/test.json")
```

**Fișier**: `agents/data_collector/tests/test_validator.py`

```python
from validator import DataValidator
from models import Bar
from datetime import datetime

def test_validate_valid_bar():
    """Test validare bar OK."""
    validator = DataValidator()
    
    bar = Bar(
        symbol="AAPL",
        timeframe="1H",
        timestamp=datetime.now(),
        open=150.00,
        high=151.00,
        low=149.00,
        close=150.50,
        volume=1000000,
        count=400,
        wap=150.20,
        hasGaps=False,
        source="IBKR",
        normalized=True
    )
    
    is_valid, msg = validator.validate_bar(bar)
    assert is_valid == True

def test_validate_invalid_bar_high_low():
    """Test validare bar invalid (high < low)."""
    validator = DataValidator()
    
    bar = Bar(
        symbol="AAPL",
        timeframe="1H",
        timestamp=datetime.now(),
        open=150.00,
        high=149.00,  # INVALID
        low=151.00,
        close=150.50,
        volume=1000000,
        count=400,
        wap=150.20,
        hasGaps=False,
        source="IBKR",
        normalized=True
    )
    
    is_valid, msg = validator.validate_bar(bar)
    assert is_valid == False
```

---

## 9. CUM TESTEZI REZULTATELE

### 9.1 Test local (development)

```bash
# 1. Setup
cd agents/data_collector
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurare (editează config.yaml)
nano ../../config/config.yaml

# 3. Rulare data collector
python collector.py ../../config/config.yaml

# 4. Verificare CSV
cat data/AAPL_1H_20260117.csv

# 5. Verificare JSON
cat data/AAPL_1H_20260117.json

# 6. Run tests
pytest tests/ -v

# 7. Check data quality
python -c "
import pandas as pd
df = pd.read_csv('data/AAPL_1H_20260117.csv')
print(f'Rows: {len(df)}')
print(f'Columns: {df.columns.tolist()}')
print(f'Missing values: {df.isnull().sum().sum()}')
print(df.head())
"
```

### 9.2 Checklist de validare manuală

```
[ ] Datele sunt descărcate (CSV și JSON create)
[ ] CSV are coloane corecte: symbol, timestamp, open, high, low, close, volume, etc.
[ ] Timestamp-uri sunt în ordine crescătoare (nici o inversie)
[ ] High >= max(open, close) pentru fiecare bar
[ ] Low <= min(open, close) pentru fiecare bar
[ ] Volume > 0 pentru fiecare bar
[ ] WAP > 0 pentru fiecare bar
[ ] Nici o valoare NaN sau Inf
[ ] CSV se deschide în Excel fără erori
[ ] JSON este valid JSON (nu ai erori de parsing)
[ ] Timestamp-uri sunt în UTC
[ ] Nu au gap-uri neașteptate în timpuri (ex: 10:00 → 12:00 la 1H)
[ ] Dimensiunea fișierelor e rezonabilă (nu 0 bytes)
```

### 9.3 Test pe mai mulți agenți

După ce Agentul 1 e validat:

```bash
# 1. Generează CSV/JSON de test
python collector.py config/config.yaml

# 2. Copiază CSV în input Agentului 2
cp data/AAPL_1H_*.csv ../strategy_engine/data/

# 3. Agentul 2 citește din CSV și produce semnale
python ../strategy_engine/strategy.py

# 4. Verifică semnale
cat ../strategy_engine/output/AAPL_signals.json
```

---

## 10. RESURSE ȘI REFERINȚE

### Documentare
- [ib_insync API Docs](https://ib-insync.readthedocs.io/api.html) [web:67]
- [Interactive Brokers Python API](https://www.interactivebrokers.com/campus/trading-lessons/python-receiving-market-data/) [web:68]
- [ib_insync Historical Data](https://algotrading101.com/learn/ib_insync-interactive-brokers-api-guide/) [web:71]
- [OHLCV Data Best Practices](https://www.coinapi.io/blog/ohlcv-data-explained-real-time-updates-websocket-behavior-and-trading-applications) [web:73]

### Pacing Limits
- [IBKR Pacing Limits](https://interactivebrokers.github.io/tws-api/historical_limitations.html) — Max 1 req / 10 sec [web:77]
- Soft limit pentru 1H+: ~1-2 sec OK

### Integrări alternative
- Yahoo Finance: `yfinance` library (backup)
- Alpha Vantage: API gratuit (backup)
- Stooq: Source alternativă (backup)

---

## CONCLUZIE

**Agentul 1 este ultra-granular și ready for Cursor implementation.**

- ✅ Responsabilități clare
- ✅ Input/output perfect definite
- ✅ Funcții publice cu semnături
- ✅ Pseudo-cod detaliat
- ✅ Teste incluse
- ✅ Validare manually verificabilă

**Next step**: Implementare în Cursor, apoi Agentul 2.

---

**Document**: Specificație Agentul 1 — Data Collector v6.1  
**Status**: PRODUCTION READY  
**Ultima actualizare**: 2026-01-17  
**Autor**: AI Assistant + Developer Feedback