"""
Teste pentru validators
"""

import pytest
import tempfile
from pathlib import Path
from src.utils.validators import (
    ValidationError,
    validate_config,
    validate_file_exists,
    validate_positive,
    validate_range,
    validate_percentage,
    validate_symbol,
    validate_port
)


class TestValidators:
    """Teste pentru validatori"""
    
    def test_validate_config_success(self):
        """Test validare config cu toate cheile necesare"""
        config = {
            "app": {"mode": "paper"},
            "ibkr": {"host": "127.0.0.1"},
            "risk": {"capital": 500}
        }
        required = ["app", "ibkr", "risk"]
        
        # Nu ar trebui să arunce excepție
        validate_config(config, required)
    
    def test_validate_config_missing_key(self):
        """Test validare config cu cheie lipsă"""
        config = {"app": {"mode": "paper"}}
        required = ["app", "ibkr"]
        
        with pytest.raises(ValidationError, match="Missing required config keys"):
            validate_config(config, required)
    
    def test_validate_file_exists_success(self):
        """Test validare fișier existent"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            file_path = Path(f.name)
        
        try:
            result = validate_file_exists(file_path)
            assert result == file_path
        finally:
            file_path.unlink()
    
    def test_validate_file_exists_not_found(self):
        """Test validare fișier inexistent"""
        with pytest.raises(ValidationError, match="File not found"):
            validate_file_exists("nonexistent_file.txt")
    
    def test_validate_positive_success(self):
        """Test validare valoare pozitivă"""
        validate_positive(1.0)
        validate_positive(0.1)
        validate_positive(100)
    
    def test_validate_positive_failure(self):
        """Test validare valoare negativă"""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive(0)
        
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive(-1)
    
    def test_validate_range_success(self):
        """Test validare valoare în interval"""
        validate_range(5, 0, 10)
        validate_range(0, 0, 10)
        validate_range(10, 0, 10)
    
    def test_validate_range_failure(self):
        """Test validare valoare în afara intervalului"""
        with pytest.raises(ValidationError, match="must be between"):
            validate_range(-1, 0, 10)
        
        with pytest.raises(ValidationError, match="must be between"):
            validate_range(11, 0, 10)
    
    def test_validate_percentage_success(self):
        """Test validare procentaj valid"""
        validate_percentage(0.0)
        validate_percentage(0.5)
        validate_percentage(1.0)
        validate_percentage(50)  # Format 0-100
        validate_percentage(100)  # Format 0-100
    
    def test_validate_percentage_failure(self):
        """Test validare procentaj invalid"""
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_percentage(-0.1)
        
        with pytest.raises(ValidationError, match="too large"):
            validate_percentage(150)
    
    def test_validate_symbol_success(self):
        """Test validare simbol valid"""
        validate_symbol("AAPL")
        validate_symbol("MSFT")
        validate_symbol("AMD")
        validate_symbol("TSLA")
    
    def test_validate_symbol_failure(self):
        """Test validare simbol invalid"""
        with pytest.raises(ValidationError):
            validate_symbol("")
        
        with pytest.raises(ValidationError):
            validate_symbol("AAPL-MSK")  # Caractere speciale
        
        with pytest.raises(ValidationError):
            validate_symbol("VERYLONGSYMBOL")  # Prea lung
    
    def test_validate_port_success(self):
        """Test validare port valid"""
        validate_port(1)
        validate_port(7497)
        validate_port(65535)
    
    def test_validate_port_failure(self):
        """Test validare port invalid"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_port("7497")
        
        with pytest.raises(ValidationError, match="must be between"):
            validate_port(0)
        
        with pytest.raises(ValidationError, match="must be between"):
            validate_port(65536)
