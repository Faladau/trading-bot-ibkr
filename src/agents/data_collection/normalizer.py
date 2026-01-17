"""
Data Normalizer - Normalizare și export date (CSV, JSON)
"""

from typing import List
import pandas as pd
import json
from datetime import datetime, timezone
from pathlib import Path

from src.common.models.market_data import Bar
from src.common.logging_utils.logger import get_logger


class DataNormalizer:
    """Normalizare format date."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def bars_to_csv(self, bars: List[Bar], filepath: str) -> bool:
        """Exportă bars → CSV.
        
        Args:
            bars: Lista de Bar-uri
            filepath: Cale fișier CSV
        
        Returns:
            True dacă exportul reușește
        """
        try:
            # Creează directorul dacă nu există
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert la dict pentru CSV
            data = [bar.to_csv_dict() for bar in bars]
            df = pd.DataFrame(data)
            
            # Export CSV
            df.to_csv(filepath, index=False)
            
            self.logger.info(f"Saved {len(bars)} bars to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"CSV export error: {e}")
            return False
    
    def bars_to_json(self, bars: List[Bar], filepath: str, symbol: str, timeframe: str) -> bool:
        """Exportă bars → JSON cu metadata.
        
        Args:
            bars: Lista de Bar-uri
            filepath: Cale fișier JSON
            symbol: Simbol stoc
            timeframe: Timeframe
        
        Returns:
            True dacă exportul reușește
        """
        try:
            # Creează directorul dacă nu există
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            if not bars:
                self.logger.warning(f"No bars to export for {symbol}")
                return False
            
            # Metadata
            metadata = {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": {
                    "start": bars[0].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "end": bars[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "total_bars": len(bars),
                    "date_generated": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                },
                "metadata": {
                    "source": bars[0].source if bars else "UNKNOWN",
                    "normalized": True,
                    "data_quality": {
                        "missing_bars": self._count_missing_bars(bars),
                        "gaps_detected": sum(1 for b in bars if b.hasGaps),
                        "duplicates": self._count_duplicates(bars)
                    }
                },
                "bars": [bar.to_dict() for bar in bars]
            }
            
            # Export JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(bars)} bars to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"JSON export error: {e}")
            return False
    
    def _count_missing_bars(self, bars: List[Bar]) -> int:
        """Detectează baruri lipsă (simplificat - poate fi îmbunătățit)."""
        # TODO: Implementare mai sofisticată bazată pe timeframe
        # Pentru acum, returnăm 0
        return 0
    
    def _count_duplicates(self, bars: List[Bar]) -> int:
        """Detectează duplicate timestamp."""
        if not bars:
            return 0
        timestamps = [b.timestamp for b in bars]
        return len(timestamps) - len(set(timestamps))
