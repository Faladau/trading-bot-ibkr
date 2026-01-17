"""
IBKR Data Source - Implementare pentru Interactive Brokers
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio

from src.agents.data_collection.sources.base_source import BaseDataSource
from src.common.models.market_data import Bar
from src.common.logging_utils.logger import get_logger


class IBKRDataSource(BaseDataSource):
    """Data source pentru Interactive Brokers."""
    
    def __init__(self, host: str, port: int, clientId: int):
        """
        Inițializează IBKR data source.
        
        Args:
            host: Adresa IBKR Gateway/TWS
            port: Port (7497 paper, 7496 live)
            clientId: Client ID unic
        """
        # Lazy import pentru a evita event loop issues în Streamlit
        try:
            from ib_insync import IB, Stock, Contract
            self.IB = IB
            self.Stock = Stock
            self.Contract = Contract
        except ImportError as e:
            raise ImportError(f"ib_insync nu este instalat: {e}")
        
        self.ib = self.IB()
        self.host = host
        self.port = port
        self.clientId = clientId
        self.bars_cache: Dict[str, Bar] = {}
        self.logger = get_logger(__name__)
        self._connected = False
    
    async def connect(self) -> bool:
        """Conectează la IBKR cu retry logic."""
        retries = 3
        for attempt in range(retries):
            try:
                # ib_insync folosește sync API, dar putem rula în executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.ib.connect(self.host, self.port, clientId=self.clientId)
                )
                self._connected = True
                self.logger.info(f"IBKR connected: {self.host}:{self.port}")
                return True
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt+1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # exponential backoff
        self._connected = False
        return False
    
    async def disconnect(self) -> bool:
        """Deconectează IBKR."""
        try:
            if self._connected:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.ib.disconnect)
                self._connected = False
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
            symbol: Simbol stoc (ex: 'AAPL')
            timeframe: Timeframe (ex: '1H', '1D', '5m')
            lookback_days: Zile de descărcat
            useRTH: Ore regulate de trading
        
        Returns:
            Lista de Bar-uri normalizate
        """
        if not self._connected:
            self.logger.error("Not connected to IBKR")
            return []
        
        try:
            # Creează contract (folosește lazy import)
            contract = self.Stock(symbol, 'SMART', 'USD')
            
            # Parametri
            duration_str = f"{lookback_days} D"
            bar_size = self._convert_timeframe(timeframe)
            
            # Request (sync în executor)
            self.logger.info(f"Fetching {symbol} {timeframe} for {lookback_days} days...")
            loop = asyncio.get_event_loop()
            bars_raw = await loop.run_in_executor(
                None,
                lambda: self.ib.reqHistoricalData(
                    contract,
                    endDateTime='',          # Until now
                    durationStr=duration_str,
                    barSizeSetting=bar_size,
                    whatToShow='TRADES',     # Real trades
                    useRTH=useRTH,
                    keepUpToDate=False       # Historic only
                )
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
        if not self._connected:
            self.logger.error("Not connected to IBKR")
            return
        
        try:
            contract = self.Stock(symbol, 'SMART', 'USD')
            bar_size = self._convert_timeframe(timeframe)
            
            # Request cu keepUpToDate=True
            loop = asyncio.get_event_loop()
            bars = await loop.run_in_executor(
                None,
                lambda: self.ib.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',       # Doar astăzi + live
                    barSizeSetting=bar_size,
                    whatToShow='TRADES',
                    useRTH=True,
                    keepUpToDate=True        # LIVE STREAM
                )
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
            timestamp=raw_bar.time,
            open=round(raw_bar.open, 2),
            high=round(raw_bar.high, 2),
            low=round(raw_bar.low, 2),
            close=round(raw_bar.close, 2),
            volume=int(raw_bar.volume),
            symbol=symbol,
            timeframe=timeframe,
            count=int(raw_bar.count) if hasattr(raw_bar, 'count') else None,
            wap=round(raw_bar.average, 2) if hasattr(raw_bar, 'average') else None,
            hasGaps=bool(raw_bar.hasGaps) if hasattr(raw_bar, 'hasGaps') else None,
            source=source,
            normalized=True
        )
