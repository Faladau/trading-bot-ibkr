"""
Teste pentru helpers
"""

import pytest
from datetime import datetime, timezone
from src.utils import helpers


class TestHelpers:
    """Teste pentru funcții helper"""
    
    def test_format_price(self):
        """Test formatare preț"""
        assert helpers.format_price(150.50) == "150.50"
        assert helpers.format_price(150.5, decimals=4) == "150.5000"
        assert helpers.format_price(0.1234, decimals=4) == "0.1234"
    
    def test_format_percentage(self):
        """Test formatare procentaj"""
        assert helpers.format_percentage(0.05) == "5.00%"
        assert helpers.format_percentage(0.1234, decimals=1) == "12.3%"
        assert helpers.format_percentage(1.0) == "100.00%"
    
    def test_calculate_percentage_change(self):
        """Test calcul procentaj schimbare"""
        assert helpers.calculate_percentage_change(100, 105) == 0.05
        assert helpers.calculate_percentage_change(100, 95) == -0.05
        assert helpers.calculate_percentage_change(100, 100) == 0.0
        assert helpers.calculate_percentage_change(0, 100) == 0.0
    
    def test_round_to_tick_size(self):
        """Test rotunjire la tick size"""
        assert helpers.round_to_tick_size(150.456, 0.01) == 150.46
        assert abs(helpers.round_to_tick_size(150.456, 0.05) - 150.45) < 0.001
        assert helpers.round_to_tick_size(150.456, 0.1) == 150.5
        assert helpers.round_to_tick_size(150.456, 1.0) == 150.0
    
    def test_safe_divide(self):
        """Test împărțire sigură"""
        assert helpers.safe_divide(10, 2) == 5.0
        assert helpers.safe_divide(10, 0) == 0.0
        assert helpers.safe_divide(10, 0, default=999) == 999
        assert helpers.safe_divide(0, 5) == 0.0
    
    def test_truncate_string(self):
        """Test trunchiere string"""
        assert helpers.truncate_string("short", 10) == "short"
        assert helpers.truncate_string("very long string", 10) == "very lo..."
        assert helpers.truncate_string("test", 4) == "test"
        assert helpers.truncate_string("test", 3) == "..."
    
    def test_is_market_hours_weekday(self):
        """Test verificare market hours în timpul săptămânii"""
        # Luni, 10:00 ET (în timpul orelor de tranzacționare)
        dt = datetime(2024, 1, 15, 15, 0, 0, tzinfo=timezone.utc)  # 15:00 UTC = 10:00 ET
        assert helpers.is_market_hours(dt) is True
        
        # Luni, 8:00 ET (înainte de deschidere)
        dt = datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc)  # 13:00 UTC = 8:00 ET
        assert helpers.is_market_hours(dt) is False
        
        # Luni, 17:00 ET (după închidere)
        dt = datetime(2024, 1, 15, 22, 0, 0, tzinfo=timezone.utc)  # 22:00 UTC = 17:00 ET
        assert helpers.is_market_hours(dt) is False
    
    def test_is_market_hours_weekend(self):
        """Test verificare market hours în weekend"""
        # Sâmbătă
        dt = datetime(2024, 1, 13, 15, 0, 0, tzinfo=timezone.utc)
        assert helpers.is_market_hours(dt) is False
        
        # Duminică
        dt = datetime(2024, 1, 14, 15, 0, 0, tzinfo=timezone.utc)
        assert helpers.is_market_hours(dt) is False
