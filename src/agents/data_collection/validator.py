"""
Data Validator - Validare calitate date
"""

from typing import List, Tuple
from src.common.models.market_data import Bar
from src.common.logging_utils.logger import get_logger


class DataValidator:
    """Validare calitate date."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_bar(self, bar: Bar) -> Tuple[bool, str]:
        """Validează un bar individual.
        
        Args:
            bar: Bar de validat
        
        Returns:
            Tuple (is_valid, error_message)
        """
        errors = []
        
        # OHLC logic
        if bar.high < max(bar.open, bar.close):
            errors.append(f"High ({bar.high}) < max(open, close)")
        
        if bar.low > min(bar.open, bar.close):
            errors.append(f"Low ({bar.low}) > min(open, close)")
        
        if bar.high < bar.low:
            errors.append(f"High ({bar.high}) < Low ({bar.low})")
        
        # Price valid
        if bar.open <= 0 or bar.close <= 0:
            errors.append("Price <= 0")
        
        # Volume
        if bar.volume < 0:
            errors.append("Volume < 0")
        
        # WAP logic (dacă există)
        if bar.wap is not None:
            if bar.wap <= 0 and bar.volume > 0:
                errors.append("WAP invalid (WAP <= 0 with volume > 0)")
        
        # Count logic (dacă există)
        if bar.count is not None:
            if bar.count <= 0 and bar.volume > 0:
                errors.append("Count invalid (count <= 0 with volume > 0)")
        
        if errors:
            error_msg = "; ".join(errors)
            self.logger.warning(f"Bar validation errors for {bar.symbol}: {error_msg}")
            return False, error_msg
        
        return True, "OK"
    
    def validate_bars(self, bars: List[Bar]) -> Tuple[int, int]:
        """Validează lista de bars.
        
        Args:
            bars: Lista de Bar-uri
        
        Returns:
            Tuple (valid_count, invalid_count)
        """
        valid, invalid = 0, 0
        for bar in bars:
            is_valid, msg = self.validate_bar(bar)
            if is_valid:
                valid += 1
            else:
                invalid += 1
        
        return valid, invalid
