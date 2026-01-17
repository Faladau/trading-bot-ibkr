"""
Trade Models - Trade, Position, Order
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class OrderType(Enum):
    """Tipuri de ordine"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(Enum):
    """Laturile unei ordine"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Status-uri posibile pentru o ordine"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionStatus(Enum):
    """Status-uri posibile pentru o poziție"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"


@dataclass
class Order:
    """Reprezintă un ordin de tranzacționare"""
    
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_fill_price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validare după inițializare"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.filled_quantity < 0:
            raise ValueError("Filled quantity cannot be negative")
        
        if self.filled_quantity > self.quantity:
            raise ValueError("Filled quantity cannot exceed total quantity")
        
        # Validare pentru tipuri de ordine
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("Limit price required for LIMIT order")
        
        if self.order_type == OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop price required for STOP order")
        
        if self.order_type == OrderType.STOP_LIMIT:
            if self.stop_price is None or self.limit_price is None:
                raise ValueError("Both stop price and limit price required for STOP_LIMIT order")
    
    @property
    def is_filled(self) -> bool:
        """Verifică dacă ordinul este complet executat"""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_partially_filled(self) -> bool:
        """Verifică dacă ordinul este parțial executat"""
        return self.status == OrderStatus.PARTIALLY_FILLED
    
    @property
    def remaining_quantity(self) -> int:
        """Calculează cantitatea rămasă"""
        return self.quantity - self.filled_quantity
    
    @property
    def fill_percentage(self) -> float:
        """Calculează procentajul de execuție"""
        if self.quantity == 0:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100


@dataclass
class Position:
    """Reprezintă o poziție deschisă"""
    
    symbol: str
    side: OrderSide
    quantity: int
    entry_price: float
    current_price: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: PositionStatus = PositionStatus.OPEN
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    orders: List[Order] = field(default_factory=list)
    
    def __post_init__(self):
        """Validare după inițializare"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
        
        if self.current_price <= 0:
            raise ValueError("Current price must be positive")
        
        # Validare pentru BUY
        if self.side == OrderSide.BUY:
            if self.take_profit is not None and self.take_profit <= self.entry_price:
                raise ValueError("Take profit must be greater than entry price for BUY position")
            if self.stop_loss is not None and self.stop_loss >= self.entry_price:
                raise ValueError("Stop loss must be less than entry price for BUY position")
        
        # Validare pentru SELL
        if self.side == OrderSide.SELL:
            if self.take_profit is not None and self.take_profit >= self.entry_price:
                raise ValueError("Take profit must be less than entry price for SELL position")
            if self.stop_loss is not None and self.stop_loss <= self.entry_price:
                raise ValueError("Stop loss must be greater than entry price for SELL position")
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculează profit/pierdere nerealizată"""
        if self.side == OrderSide.BUY:
            return (self.current_price - self.entry_price) * self.quantity
        else:  # SELL
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculează profit/pierdere nerealizată procentuală"""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def is_profitable(self) -> bool:
        """Verifică dacă poziția este profitabilă"""
        return self.unrealized_pnl > 0
    
    @property
    def is_at_take_profit(self) -> bool:
        """Verifică dacă poziția a atins take profit"""
        if self.take_profit is None:
            return False
        
        if self.side == OrderSide.BUY:
            return self.current_price >= self.take_profit
        else:  # SELL
            return self.current_price <= self.take_profit
    
    @property
    def is_at_stop_loss(self) -> bool:
        """Verifică dacă poziția a atins stop loss"""
        if self.stop_loss is None:
            return False
        
        if self.side == OrderSide.BUY:
            return self.current_price <= self.stop_loss
        else:  # SELL
            return self.current_price >= self.stop_loss
    
    def update_price(self, new_price: float) -> None:
        """Actualizează prețul curent"""
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self.current_price = new_price


@dataclass
class Trade:
    """Reprezintă un trade completat (poziție închisă)"""
    
    symbol: str
    side: OrderSide
    quantity: int
    entry_price: float
    exit_price: float
    entry_timestamp: datetime
    exit_timestamp: datetime
    commission: float = 0.0
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validare după inițializare"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.entry_price <= 0 or self.exit_price <= 0:
            raise ValueError("Entry and exit prices must be positive")
        
        if self.commission < 0:
            raise ValueError("Commission cannot be negative")
        
        if self.exit_timestamp < self.entry_timestamp:
            raise ValueError("Exit timestamp cannot be before entry timestamp")
    
    @property
    def gross_pnl(self) -> float:
        """Calculează profit/pierdere brută"""
        if self.side == OrderSide.BUY:
            return (self.exit_price - self.entry_price) * self.quantity
        else:  # SELL
            return (self.entry_price - self.exit_price) * self.quantity
    
    @property
    def net_pnl(self) -> float:
        """Calculează profit/pierdere netă (după comisioane)"""
        return self.gross_pnl - self.commission
    
    @property
    def pnl_pct(self) -> float:
        """Calculează profit/pierdere procentuală"""
        if self.entry_price == 0:
            return 0.0
        return ((self.exit_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def is_profitable(self) -> bool:
        """Verifică dacă trade-ul este profitabil"""
        return self.net_pnl > 0
    
    @property
    def duration_seconds(self) -> float:
        """Calculează durata trade-ului în secunde"""
        delta = self.exit_timestamp - self.entry_timestamp
        return delta.total_seconds()
    
    def to_dict(self) -> dict:
        """Convertește la dict pentru serializare"""
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "entry_timestamp": self.entry_timestamp.isoformat(),
            "exit_timestamp": self.exit_timestamp.isoformat(),
            "gross_pnl": self.gross_pnl,
            "net_pnl": self.net_pnl,
            "pnl_pct": self.pnl_pct,
            "commission": self.commission,
            "reason": self.reason
        }
