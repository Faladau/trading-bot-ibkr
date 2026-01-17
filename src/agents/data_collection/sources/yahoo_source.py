"""
Yahoo Finance Data Source - Backup source pentru date istorice
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio

try:
    import yfinance as yf
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False

from src.agents.data_collection.sources.base_source import BaseDataSource
from src.common.models.market_data import Bar
from src.common.logging_utils.logger import get_logger


class YahooDataSource(BaseDataSource):
    """Data source pentru Yahoo Finance (backup)."""
    
    def __init__(self):
        """Inițializează Yahoo Finance data source."""
        if not YAHOO_AVAILABLE:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")
        
        self.bars_cache: Dict[str, Bar] = {}
        self.logger = get_logger(__name__)
        self._connected = True  # Yahoo nu necesită conexiune explicită
    
    async def connect(self) -> bool:
        """Yahoo Finance nu necesită conexiune explicită."""
        self._connected = True
        self.logger.info("Yahoo Finance data source ready (no connection needed)")
        return True
    
    async def disconnect(self) -> bool:
        """Yahoo Finance nu necesită deconexiune."""
        self._connected = False
        self.logger.info("Yahoo Finance data source disconnected")
        return True
    
    async def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int,
        useRTH: bool = True
    ) -> List[Bar]:
        """
        Descarcă date istorice din Yahoo Finance.
        
        Args:
            symbol: Simbol stoc (ex: 'AAPL')
            timeframe: Timeframe (ex: '1H', '1D', '5m')
            lookback_days: Zile de descărcat
            useRTH: Ignorat pentru Yahoo (nu suportă RTH)
        
        Returns:
            Lista de Bar-uri normalizate
        """
        try:
            # Convert timeframe Yahoo format
            interval = self._convert_timeframe(timeframe)
            
            # Calculare perioadă
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            self.logger.info(f"Fetching {symbol} {timeframe} from Yahoo Finance ({lookback_days} days)...")
            
            # Download date (sync în executor)
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(
                None,
                lambda: yf.Ticker(symbol)
            )
            
            # Fetch historical data
            hist = await loop.run_in_executor(
                None,
                lambda: ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    prepost=False  # Nu include pre/post market
                )
            )
            
            if hist.empty:
                self.logger.warning(f"No data from Yahoo Finance for {symbol}")
                return []
            
            # Convert și normalizare
            bars_normalized = []
            for idx, row in hist.iterrows():
                # idx este pandas Timestamp, convert la datetime
                timestamp = idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else datetime.fromtimestamp(idx.timestamp())
                normalized = self._normalize_bar(row, symbol, timeframe, 'YAHOO', timestamp)
                bars_normalized.append(normalized)
            
            self.logger.info(f"Fetched {len(bars_normalized)} bars from Yahoo Finance for {symbol}")
            return bars_normalized
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance fetch error for {symbol}: {e}")
            return []
    
    async def subscribe_to_bars(
        self, 
        symbol: str, 
        timeframe: str
    ) -> None:
        """Yahoo Finance nu suportă live stream - doar istoric."""
        self.logger.warning("Yahoo Finance does not support live streaming. Use IBKR for live data.")
    
    def get_latest_bar(self, symbol: str) -> Optional[Bar]:
        """Ultimul bar din cache (Yahoo nu are live stream)."""
        return self.bars_cache.get(symbol)
    
    def _convert_timeframe(self, tf: str) -> str:
        """Conversia timeframe App → Yahoo Finance format."""
        mapping = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '1H': '1h',
            '4H': '4h',
            '1D': '1d',
            '1W': '1wk',
            '1M': '1mo'
        }
        return mapping.get(tf, '1d')
    
    def _normalize_bar(self, row, symbol: str, timeframe: str, source: str, timestamp: datetime) -> Bar:
        """Normalizare Yahoo Finance row → Bar standardizat."""
        return Bar(
            timestamp=timestamp,
            open=round(float(row['Open']), 2),
            high=round(float(row['High']), 2),
            low=round(float(row['Low']), 2),
            close=round(float(row['Close']), 2),
            volume=int(row['Volume']) if 'Volume' in row else 0,
            symbol=symbol,
            timeframe=timeframe,
            count=None,  # Yahoo nu oferă count
            wap=None,    # Yahoo nu oferă WAP direct
            hasGaps=None,  # Yahoo nu oferă hasGaps
            source=source,
            normalized=True
        )
