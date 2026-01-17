"""
Data Collection Agent - Orchestrator principal pentru colectare date
"""

from typing import List, Optional
import asyncio
from pathlib import Path
from datetime import datetime

from src.common.utils.config_loader import ConfigLoader
from src.common.logging_utils.logger import get_logger
from src.common.models.market_data import Bar

# Lazy imports pentru a evita event loop issues în Streamlit
# IBKRDataSource se importă doar când e necesar
from src.agents.data_collection.sources.yahoo_source import YahooDataSource
from src.agents.data_collection.sources.base_source import BaseDataSource
from src.agents.data_collection.normalizer import DataNormalizer
from src.agents.data_collection.validator import DataValidator


class DataCollectionAgent:
    """Orchestrator principal pentru colectare date."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inițializează Data Collection Agent.
        
        Args:
            config_path: Cale către fișier config (default: config/config.yaml)
        """
        self.config_loader = ConfigLoader()
        if config_path:
            self.config = self.config_loader.load_config(config_path)
        else:
            self.config = self.config_loader.load_config("config.yaml")
        
        self.data_source: Optional[BaseDataSource] = None
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()
        self.logger = get_logger(__name__)
    
    async def initialize(self) -> bool:
        """Inițializare conexiuni și setup.
        
        Returns:
            True dacă inițializarea reușește
        """
        try:
            # Obține config data_collector
            data_collector_config = self.config.get("data_collector", {})
            ibkr_config = self.config.get("ibkr", {})
            data_source_name = data_collector_config.get("data_source", "IBKR")
            
            # Conectează la sursa primară
            if data_source_name.upper() == "IBKR":
                # Lazy import pentru a evita event loop issues în Streamlit
                from src.agents.data_collection.sources.ibkr_source import IBKRDataSource
                self.data_source = IBKRDataSource(
                    host=ibkr_config.get("host", "127.0.0.1"),
                    port=ibkr_config.get("port", 7497),
                    clientId=ibkr_config.get("clientId", 1)
                )
                connected = await self.data_source.connect()
                if not connected:
                    self.logger.warning("Failed to connect to IBKR, will try backup source if configured")
                    # Nu returnăm False aici - încercăm backup
            elif data_source_name.upper() == "YAHOO":
                self.data_source = YahooDataSource()
                connected = await self.data_source.connect()
            else:
                self.logger.error(f"Unknown data source: {data_source_name}")
                return False
            
            # Crează output directories
            data_dir = data_collector_config.get("data_dir", "data/processed")
            Path(data_dir).mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"DataCollectionAgent initialized with {data_source_name}")
            return True
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False
    
    async def collect_all(self) -> bool:
        """Colectează date pentru toate simbolurile.
        
        Returns:
            True dacă colectarea reușește
        """
        try:
            data_collector_config = self.config.get("data_collector", {})
            symbols = data_collector_config.get("symbols", [])
            timeframe = data_collector_config.get("timeframe", "1H")
            lookback_days = data_collector_config.get("lookback_days", 60)
            useRTH = data_collector_config.get("useRTH", True)
            
            if not symbols:
                self.logger.warning("No symbols configured")
                return False
            
            for symbol in symbols:
                self.logger.info(f"Collecting {symbol}...")
                
                # Fetch de la sursa primară
                bars = await self.data_source.fetch_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    lookback_days=lookback_days,
                    useRTH=useRTH
                )
                
                # Dacă nu avem date și avem backup source, încercăm backup
                if not bars:
                    backup_source_name = data_collector_config.get("backup_source")
                    if backup_source_name:
                        self.logger.info(f"No data from primary source, trying backup: {backup_source_name}")
                        backup_source = self._get_backup_source(backup_source_name)
                        if backup_source:
                            await backup_source.connect()
                            bars = await backup_source.fetch_historical_data(
                                symbol=symbol,
                                timeframe=timeframe,
                                lookback_days=lookback_days,
                                useRTH=useRTH
                            )
                            await backup_source.disconnect()
                
                if not bars:
                    self.logger.warning(f"No data for {symbol} from any source")
                    continue
                
                # Validate
                valid_count, invalid_count = self.validator.validate_bars(bars)
                self.logger.info(f"{symbol}: {valid_count} valid, {invalid_count} invalid")
                
                # Save
                await self._save_bars(symbol, bars, data_collector_config)
                
                # Pace limit IBKR (min 10 sec între requests)
                self.logger.info(f"Waiting 10 seconds before next request (IBKR pacing limit)...")
                await asyncio.sleep(10)
            
            self.logger.info("Collection completed")
            return True
        except Exception as e:
            self.logger.error(f"Collection error: {e}")
            return False
    
    async def _save_bars(self, symbol: str, bars: List[Bar], config: dict) -> bool:
        """Salvează bars în format CSV + JSON.
        
        Args:
            symbol: Simbol stoc
            bars: Lista de Bar-uri
            config: Configurație data_collector
        """
        try:
            timeframe = config.get("timeframe", "1H")
            data_dir = config.get("data_dir", "data/processed")
            output_format = config.get("output_format", ["csv", "json"])
            
            # Filename
            from datetime import timezone
            date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
            base_name = f"{data_dir}/{symbol}_{timeframe}_{date_str}"
            
            # CSV
            if "csv" in output_format:
                csv_path = f"{base_name}.csv"
                self.normalizer.bars_to_csv(bars, csv_path)
            
            # JSON
            if "json" in output_format:
                json_path = f"{base_name}.json"
                self.normalizer.bars_to_json(bars, json_path, symbol, timeframe)
            
            return True
        except Exception as e:
            self.logger.error(f"Save error: {e}")
            return False
    
    def _get_backup_source(self, source_name: str) -> Optional[BaseDataSource]:
        """Creează backup source.
        
        Args:
            source_name: Nume sursă ('YAHOO', 'ALPHA', etc.)
        
        Returns:
            BaseDataSource sau None
        """
        source_name_upper = source_name.upper()
        
        if source_name_upper == "IBKR":
            # Lazy import pentru a evita event loop issues în Streamlit
            from src.agents.data_collection.sources.ibkr_source import IBKRDataSource
            ibkr_config = self.config.get("ibkr", {})
            return IBKRDataSource(
                host=ibkr_config.get("host", "127.0.0.1"),
                port=ibkr_config.get("port", 7497),
                clientId=ibkr_config.get("clientId", 1)
            )
        elif source_name_upper == "YAHOO":
            try:
                return YahooDataSource()
            except ImportError as e:
                self.logger.error(f"Cannot create Yahoo source: {e}")
                return None
        else:
            self.logger.warning(f"Unknown backup source: {source_name}")
            return None
    
    async def shutdown(self) -> bool:
        """Dezactivare controlată.
        
        Returns:
            True dacă shutdown-ul reușește
        """
        try:
            if self.data_source:
                await self.data_source.disconnect()
            self.logger.info("DataCollectionAgent shutdown completed")
            return True
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return False


# Entry point
async def main(config_path: Optional[str] = None):
    """Entry point pentru rulare standalone."""
    collector = DataCollectionAgent(config_path)
    if await collector.initialize():
        await collector.collect_all()
        await collector.shutdown()
    else:
        print("Failed to initialize collector")


if __name__ == "__main__":
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    asyncio.run(main(config_file))
