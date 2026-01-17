"""
Teste pentru DataValidator
"""

import pytest
from datetime import datetime
from src.agents.data_collection.validator import DataValidator
from src.common.models.market_data import Bar


class TestDataValidator:
    """Teste pentru DataValidator."""
    
    def test_validate_valid_bar(self):
        """Test validare bar OK."""
        validator = DataValidator()
        
        bar = Bar(
            timestamp=datetime.now(),
            open=150.00,
            high=151.00,
            low=149.00,
            close=150.50,
            volume=1000000,
            symbol="AAPL",
            timeframe="1H",
            count=400,
            wap=150.20,
            hasGaps=False,
            source="IBKR",
            normalized=True
        )
        
        is_valid, msg = validator.validate_bar(bar)
        assert is_valid == True
        assert msg == "OK"
    
    def test_validate_invalid_bar_high_low(self):
        """Test validare bar invalid (high < max(open, close))."""
        validator = DataValidator()
        
        # Creează bar valid, apoi modifică manual pentru test
        bar = Bar(
            timestamp=datetime.now(),
            open=150.00,
            high=151.00,
            low=149.00,
            close=150.50,
            volume=1000000,
            symbol="AAPL"
        )
        
        # Modifică high să fie invalid (mai mic decât close)
        bar.high = 150.00  # < close (150.50)
        
        is_valid, msg = validator.validate_bar(bar)
        assert is_valid == False
        assert "High" in msg
    
    def test_validate_invalid_bar_price_zero(self):
        """Test validare bar invalid (price <= 0)."""
        validator = DataValidator()
        
        # Creează bar valid, apoi modifică manual pentru test
        bar = Bar(
            timestamp=datetime.now(),
            open=150.00,
            high=151.00,
            low=149.00,
            close=150.50,
            volume=1000000,
            symbol="AAPL"
        )
        
        # Modifică open să fie 0
        bar.open = 0.0
        
        is_valid, msg = validator.validate_bar(bar)
        assert is_valid == False
        assert "Price" in msg
    
    def test_validate_bars_list(self):
        """Test validare listă de bars."""
        validator = DataValidator()
        
        bars = [
            Bar(
                timestamp=datetime.now(),
                open=150.00,
                high=151.00,
                low=149.00,
                close=150.50,
                volume=1000000,
                symbol="AAPL"
            ),
            Bar(
                timestamp=datetime.now(),
                open=150.00,
                high=151.00,
                low=149.00,
                close=150.50,
                volume=1000000,
                symbol="MSFT"
            )
        ]
        
        # Modifică al doilea bar să fie invalid (high < close)
        bars[1].high = 150.00  # < close (150.50)
        
        valid_count, invalid_count = validator.validate_bars(bars)
        assert valid_count == 1
        assert invalid_count == 1
