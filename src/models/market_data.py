"""
Market Data Models - Bar, Quote, Tick
"""

from dataclasses import dataclass
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
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
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
