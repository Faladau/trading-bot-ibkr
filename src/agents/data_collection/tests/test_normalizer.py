"""
Teste pentru DataNormalizer
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from src.agents.data_collection.normalizer import DataNormalizer
from src.common.models.market_data import Bar


class TestDataNormalizer:
    """Teste pentru DataNormalizer."""
    
    def test_bars_to_csv(self):
        """Test export CSV."""
        normalizer = DataNormalizer()
        
        bars = [
            Bar(
                timestamp=datetime(2026, 1, 17, 10, 0, 0),
                open=150.50,
                high=151.00,
                low=150.20,
                close=150.80,
                volume=1500000,
                symbol="AAPL",
                timeframe="1H",
                count=450,
                wap=150.65,
                hasGaps=False,
                source="IBKR",
                normalized=True
            )
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result = normalizer.bars_to_csv(bars, temp_path)
            assert result == True
            assert os.path.exists(temp_path)
            
            # Verifică că fișierul nu e gol
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_bars_to_json(self):
        """Test export JSON."""
        normalizer = DataNormalizer()
        
        bars = [
            Bar(
                timestamp=datetime(2026, 1, 17, 10, 0, 0),
                open=150.50,
                high=151.00,
                low=150.20,
                close=150.80,
                volume=1500000,
                symbol="AAPL",
                timeframe="1H",
                count=450,
                wap=150.65,
                hasGaps=False,
                source="IBKR",
                normalized=True
            )
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            result = normalizer.bars_to_json(bars, temp_path, "AAPL", "1H")
            assert result == True
            assert os.path.exists(temp_path)
            
            # Verifică că fișierul nu e gol
            assert os.path.getsize(temp_path) > 0
            
            # Verifică că e JSON valid
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert data["symbol"] == "AAPL"
                assert data["timeframe"] == "1H"
                assert len(data["bars"]) == 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_bars_to_json_empty_list(self):
        """Test export JSON cu listă goală."""
        normalizer = DataNormalizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            result = normalizer.bars_to_json([], temp_path, "AAPL", "1H")
            assert result == False  # Nu exportă dacă nu sunt bars
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
