"""
Base Data Source - Abstract class pentru orice sursă de date
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.common.models.market_data import Bar


class BaseDataSource(ABC):
    """Abstract class pentru orice sursă de date."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conectează la sursă.
        
        Returns:
            True dacă conexiunea reușește, False altfel
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Deconectează de la sursă.
        
        Returns:
            True dacă deconexiunea reușește, False altfel
        """
        pass
    
    @abstractmethod
    async def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int,
        useRTH: bool = True
    ) -> List[Bar]:
        """Descarcă date istorice pentru un simbol.
        
        Args:
            symbol: Simbol stoc (ex: 'AAPL')
            timeframe: Timeframe (ex: '1H', '1D', '5m')
            lookback_days: Număr de zile înapoi
            useRTH: Folosește ore regulate de trading (IBKR)
        
        Returns:
            Lista de Bar-uri normalizate
        """
        pass
    
    @abstractmethod
    async def subscribe_to_bars(
        self, 
        symbol: str, 
        timeframe: str
    ) -> None:
        """Subscribe la stream live de bars.
        
        Args:
            symbol: Simbol stoc
            timeframe: Timeframe
        """
        pass
    
    @abstractmethod
    def get_latest_bar(self, symbol: str) -> Optional[Bar]:
        """Primește ultimul bar din cache/memorie.
        
        Args:
            symbol: Simbol stoc
        
        Returns:
            Ultimul Bar sau None dacă nu există
        """
        pass
