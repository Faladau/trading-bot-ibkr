"""
Signal Models - Signal, Indicator
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class SignalAction(Enum):
    """Acțiuni posibile pentru un semnal"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"


@dataclass
class Indicator:
    """Reprezintă un indicator tehnic calculat"""
    
    name: str
    value: float
    timestamp: datetime
    
    def __post_init__(self):
        """Validare după inițializare"""
        if not self.name:
            raise ValueError("Indicator name cannot be empty")
    
    def to_dict(self) -> dict:
        """Convertește la dict pentru serializare"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Signal:
    """Reprezintă un semnal de trading"""
    
    action: SignalAction
    symbol: str
    timestamp: datetime
    entry_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    confidence: float = 0.0
    indicators: Optional[Dict[str, float]] = None
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validare după inițializare"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validare pentru BUY/SELL
        if self.action in [SignalAction.BUY, SignalAction.SELL]:
            if self.entry_price is None or self.entry_price <= 0:
                raise ValueError("Entry price must be positive for BUY/SELL signals")
            
            if self.action == SignalAction.BUY:
                if self.take_profit is not None and self.take_profit <= self.entry_price:
                    raise ValueError("Take profit must be greater than entry price for BUY")
                if self.stop_loss is not None and self.stop_loss >= self.entry_price:
                    raise ValueError("Stop loss must be less than entry price for BUY")
            
            if self.action == SignalAction.SELL:
                if self.take_profit is not None and self.take_profit >= self.entry_price:
                    raise ValueError("Take profit must be less than entry price for SELL")
                if self.stop_loss is not None and self.stop_loss <= self.entry_price:
                    raise ValueError("Stop loss must be greater than entry price for SELL")
    
    @property
    def has_targets(self) -> bool:
        """Verifică dacă semnalul are take profit și stop loss setate"""
        return self.take_profit is not None and self.stop_loss is not None
    
    @property
    def risk_reward_ratio(self) -> Optional[float]:
        """Calculează risk/reward ratio"""
        if not self.has_targets or self.entry_price is None:
            return None
        
        if self.action == SignalAction.BUY:
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.take_profit - self.entry_price)
        else:  # SELL
            risk = abs(self.stop_loss - self.entry_price)
            reward = abs(self.entry_price - self.take_profit)
        
        if risk == 0:
            return None
        
        return reward / risk
    
    def to_dict(self) -> dict:
        """Convertește la dict pentru serializare"""
        return {
            "action": self.action.value,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "entry_price": self.entry_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "confidence": self.confidence,
            "indicators": self.indicators,
            "reason": self.reason
        }
