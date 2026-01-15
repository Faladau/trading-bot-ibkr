"""
Teste pentru logger
"""

import pytest
import tempfile
import logging
from pathlib import Path
from src.logging_utils.logger import setup_logger, get_logger


class TestLogger:
    """Teste pentru logger"""
    
    def test_setup_logger_console_only(self):
        """Test setup logger doar pentru console"""
        logger = setup_logger(name="test_console", level="DEBUG", console_output=True, log_file=None)
        
        assert logger.name == "test_console"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logger_with_file(self):
        """Test setup logger cu fișier"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(
                name="test_file",
                level="INFO",
                log_file=log_file,
                console_output=False
            )
            
            assert logger.name == "test_file"
            assert logger.level == logging.INFO
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.handlers.RotatingFileHandler)
            assert log_file.exists()
            
            # Închide handler-ul pentru a permite ștergerea fișierului
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
    
    def test_setup_logger_both_console_and_file(self):
        """Test setup logger cu console și fișier"""
        tmpdir = tempfile.mkdtemp()
        try:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(
                name="test_both",
                level="WARNING",
                log_file=log_file,
                console_output=True
            )
            
            assert len(logger.handlers) == 2
            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
            assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)
            
            # Închide handler-ele pentru a permite ștergerea fișierului
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_get_logger_existing(self):
        """Test obținere logger existent"""
        logger1 = setup_logger(name="test_existing")
        logger2 = get_logger("test_existing")
        
        assert logger1 is logger2
    
    def test_get_logger_new(self):
        """Test obținere logger nou"""
        logger = get_logger("test_new")
        
        assert logger.name == "test_new"
        assert len(logger.handlers) > 0
    
    def test_logger_logs_messages(self):
        """Test că logger-ul loghează mesaje"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(
                name="test_logging",
                level="INFO",
                log_file=log_file,
                console_output=False
            )
            
            logger.info("Test message")
            logger.warning("Test warning")
            
            # Forțează flush pentru a scrie în fișier
            for handler in logger.handlers:
                handler.flush()
            
            # Verifică că fișierul conține mesajele
            content = log_file.read_text()
            assert "Test message" in content
            assert "Test warning" in content
            
            # Închide handler-ul pentru a permite ștergerea fișierului
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
