"""
Helpers - Funcții utilitare generale
"""

from datetime import datetime, timezone
from typing import Optional, Union
import pandas as pd


def format_price(price: float, decimals: int = 2) -> str:
    """
    Formatează un preț cu zecimale
    
    Args:
        price: Prețul
        decimals: Numărul de zecimale
        
    Returns:
        String formatat
    """
    return f"{price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formatează un procentaj
    
    Args:
        value: Valoarea (ex: 0.05 pentru 5%)
        decimals: Numărul de zecimale
        
    Returns:
        String formatat (ex: "5.00%")
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculează procentajul de schimbare
    
    Args:
        old_value: Valoarea veche
        new_value: Valoarea nouă
        
    Returns:
        Procentaj de schimbare (ex: 0.05 pentru +5%)
    """
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value


def round_to_tick_size(price: float, tick_size: float = 0.01) -> float:
    """
    Rotunjește un preț la cel mai apropiat tick size
    
    Args:
        price: Prețul
        tick_size: Dimensiunea tick-ului (default: 0.01)
        
    Returns:
        Preț rotunjit
    """
    return round(price / tick_size) * tick_size


def is_market_hours(dt: Optional[datetime] = None, timezone_str: str = "America/New_York") -> bool:
    """
    Verifică dacă este în intervalul de tranzacționare (9:30 - 16:00 ET)
    
    Args:
        dt: Data/ora de verificat (None = acum)
        timezone_str: Timezone-ul pieței (default: America/New_York)
        
    Returns:
        True dacă este în intervalul de tranzacționare
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Convertește la timezone-ul pieței
    market_tz = pd.Timestamp(dt, tz=timezone.utc).tz_convert(timezone_str)
    
    # Verifică dacă este weekday (luni-vineri)
    if market_tz.weekday() >= 5:  # Sâmbătă = 5, Duminică = 6
        return False
    
    # Verifică intervalul orar (9:30 - 16:00)
    hour = market_tz.hour
    minute = market_tz.minute
    
    # Înainte de 9:30
    if hour < 9 or (hour == 9 and minute < 30):
        return False
    
    # După 16:00
    if hour >= 16:
        return False
    
    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Împărțire sigură (evită ZeroDivisionError)
    
    Args:
        numerator: Numărătorul
        denominator: Numitorul
        default: Valoarea default dacă numitorul este 0
        
    Returns:
        Rezultatul împărțirii sau default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunchiază un string la o lungime maximă
    
    Args:
        text: Textul de trunchiat
        max_length: Lungimea maximă
        suffix: Sufixul de adăugat dacă e trunchiat
        
    Returns:
        String trunchiat
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
