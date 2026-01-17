"""
Market Data Models - Bar, Quote, Tick
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Bar:
    """Reprezintă o bară OHLCV (Open, High, Low, Close, Volume)"""
    
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Câmpuri opționale pentru Data Collection Agent
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    count: Optional[int] = None          # Număr tranzacții în perioada
    wap: Optional[float] = None          # Weighted Average Price
    hasGaps: Optional[bool] = None       # Dacă bar are gap-uri în date
    source: Optional[str] = None         # Sursă date: IBKR, YAHOO, ALPHA, etc.
    normalized: Optional[bool] = None    # Dacă datele au fost normalizate
    
    def __post_init__(self):
        """Validare după inițializare"""
        if self.high < self.low:
            raise ValueError("High cannot be less than Low")
        if self.open < self.low or self.open > self.high:
            raise ValueError("Open must be between Low and High")
        if self.close < self.low or self.close > self.high:
            raise ValueError("Close must be between Low and High")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
    
    @property
    def price_change(self) -> float:
        """Calculează schimbarea de preț (close - open)"""
        return self.close - self.open
    
    @property
    def price_change_pct(self) -> float:
        """Calculează schimbarea procentuală"""
        if self.open == 0:
            return 0.0
        return (self.close - self.open) / self.open
    
    @property
    def range(self) -> float:
        """Calculează range-ul barei (high - low)"""
        return self.high - self.low
    
    def to_dict(self) -> dict:
        """Convertește la dict pentru serializare"""
        result = {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }
        
        # Adaugă câmpurile opționale dacă există
        if self.symbol is not None:
            result["symbol"] = self.symbol
        if self.timeframe is not None:
            result["timeframe"] = self.timeframe
        if self.count is not None:
            result["count"] = self.count
        if self.wap is not None:
            result["wap"] = self.wap
        if self.hasGaps is not None:
            result["hasGaps"] = self.hasGaps
        if self.source is not None:
            result["source"] = self.source
        if self.normalized is not None:
            result["normalized"] = self.normalized
        
        return result
    
    def to_csv_dict(self) -> dict:
        """Convertește la dict pentru export CSV (toate câmpurile)"""
        return {
            "symbol": self.symbol or "",
            "timeframe": self.timeframe or "",
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "open": round(self.open, 2),
            "high": round(self.high, 2),
            "low": round(self.low, 2),
            "close": round(self.close, 2),
            "volume": self.volume,
            "count": self.count or 0,
            "wap": round(self.wap, 2) if self.wap else 0.0,
            "hasGaps": self.hasGaps if self.hasGaps is not None else False,
            "source": self.source or "",
            "normalized": self.normalized if self.normalized is not None else False
        }


@dataclass
class Quote:
    """Reprezintă un quote (bid/ask)"""
    
    timestamp: datetime
    symbol: str
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    
    def __post_init__(self):
        """Validare după inițializare"""
        if self.bid < 0 or self.ask < 0:
            raise ValueError("Bid and Ask must be positive")
        if self.bid > self.ask:
            raise ValueError("Bid cannot be greater than Ask")
        if self.bid_size < 0 or self.ask_size < 0:
            raise ValueError("Bid size and Ask size cannot be negative")
    
    @property
    def spread(self) -> float:
        """Calculează spread-ul (ask - bid)"""
        return self.ask - self.bid
    
    @property
    def mid_price(self) -> float:
        """Calculează prețul mediu (bid + ask) / 2"""
        return (self.bid + self.ask) / 2


@dataclass
class Tick:
    """Reprezintă un tick (preț instantaneu)"""
    
    timestamp: datetime
    symbol: str
    price: float
    size: int
    
    def __post_init__(self):
        """Validare după inițializare"""
        if self.price < 0:
            raise ValueError("Price must be positive")
        if self.size < 0:
            raise ValueError("Size cannot be negative")
