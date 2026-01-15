"""
Logger - Configurare centralizată pentru logging
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "trading_bot",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configurează logger-ul principal
    
    Args:
        name: Numele logger-ului
        level: Nivelul de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Calea către fișierul de log (None = doar console)
        console_output: Dacă să afișeze și pe console
        max_bytes: Dimensiunea maximă a fișierului înainte de rotire
        backup_count: Numărul de fișiere backup de păstrat
        
    Returns:
        Logger configurat
    """
    logger = logging.getLogger(name)
    
    # Evită adăugarea de handler-e duplicate
    if logger.handlers:
        return logger
    
    # Setează nivelul
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Format pentru mesaje
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pentru console
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler pentru fișier (cu rotire)
    if log_file:
        # Creează directorul dacă nu există
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Obține un logger existent sau creează unul nou
    
    Args:
        name: Numele logger-ului
        
    Returns:
        Logger
    """
    logger = logging.getLogger(name)
    
    # Dacă nu are handler-e, configurează-l cu setări default
    if not logger.handlers:
        setup_logger(name)
    
    return logger
