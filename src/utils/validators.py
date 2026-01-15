"""
Validators - Validare input și date
"""

from typing import Any, List, Optional, Union
from pathlib import Path


class ValidationError(Exception):
    """Excepție pentru erori de validare"""
    pass


def validate_config(config: dict, required_keys: List[str]) -> None:
    """
    Validează că un dict de config conține toate cheile necesare
    
    Args:
        config: Dict-ul de config
        required_keys: Lista de chei necesare
        
    Raises:
        ValidationError: Dacă lipsește o cheie necesară
    """
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ValidationError(f"Missing required config keys: {', '.join(missing)}")


def validate_file_exists(file_path: Union[str, Path]) -> Path:
    """
    Validează că un fișier există
    
    Args:
        file_path: Calea către fișier
        
    Returns:
        Path object
        
    Raises:
        ValidationError: Dacă fișierul nu există
    """
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {path}")
    return path


def validate_positive(value: float, name: str = "value") -> None:
    """
    Validează că o valoare este pozitivă
    
    Args:
        value: Valoarea de validat
        name: Numele valorii (pentru mesaj de eroare)
        
    Raises:
        ValidationError: Dacă valoarea nu este pozitivă
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")


def validate_range(value: float, min_val: float, max_val: float, name: str = "value") -> None:
    """
    Validează că o valoare este într-un interval
    
    Args:
        value: Valoarea de validat
        min_val: Valoarea minimă
        max_val: Valoarea maximă
        name: Numele valorii (pentru mesaj de eroare)
        
    Raises:
        ValidationError: Dacă valoarea nu este în interval
    """
    if not (min_val <= value <= max_val):
        raise ValidationError(f"{name} must be between {min_val} and {max_val}, got {value}")


def validate_percentage(value: float, name: str = "percentage") -> None:
    """
    Validează că o valoare este un procentaj valid (0-1 sau 0-100)
    
    Args:
        value: Valoarea de validat
        name: Numele valorii
        
    Raises:
        ValidationError: Dacă valoarea nu este un procentaj valid
    """
    if value < 0:
        raise ValidationError(f"{name} cannot be negative, got {value}")
    
    # Acceptă atât 0-1 cât și 0-100
    if value > 1 and value <= 100:
        # Probabil e în format 0-100, e OK
        pass
    elif value > 1:
        raise ValidationError(f"{name} seems too large for a percentage, got {value}")


def validate_symbol(symbol: str) -> None:
    """
    Validează formatul unui simbol de tranzacționare
    
    Args:
        symbol: Simbolul de validat
        
    Raises:
        ValidationError: Dacă simbolul nu este valid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError(f"Symbol must be a non-empty string, got {symbol}")
    
    if len(symbol) > 10:
        raise ValidationError(f"Symbol too long (max 10 characters), got {symbol}")
    
    if not symbol.isalnum():
        raise ValidationError(f"Symbol must contain only alphanumeric characters, got {symbol}")


def validate_port(port: int) -> None:
    """
    Validează un port de rețea
    
    Args:
        port: Port-ul de validat
        
    Raises:
        ValidationError: Dacă port-ul nu este valid
    """
    if not isinstance(port, int):
        raise ValidationError(f"Port must be an integer, got {type(port)}")
    
    if not (1 <= port <= 65535):
        raise ValidationError(f"Port must be between 1 and 65535, got {port}")
