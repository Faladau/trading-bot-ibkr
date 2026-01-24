"""
Structured Logging Configuration with Python Logging + SQLite
Production-grade logging with database persistence
"""

import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class SQLiteLogHandler(logging.Handler):
    """Custom logging handler that writes logs to SQLite database"""
    
    def __init__(self, db_path: str = "logs/trading_bot.db"):
        """Initialize SQLite log handler"""
        super().__init__()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create logs table if not exists"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    module TEXT,
                    message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing SQLite logs: {e}")
    
    def emit(self, record: logging.LogRecord):
        """Write log record to SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            timestamp = datetime.fromtimestamp(record.created).isoformat()
            level = record.levelname
            module = record.name
            message = self.format(record)
            
            cursor.execute(
                """INSERT INTO logs (timestamp, level, module, message)
                   VALUES (?, ?, ?, ?)""",
                (timestamp, level, module, message)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error writing to SQLite: {e}")


def configure_logging(log_level: str = "INFO"):
    """
    Configure Python logging with SQLite persistence
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console formatter
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # SQLite handler
    sqlite_handler = SQLiteLogHandler()
    sqlite_handler.setLevel(getattr(logging, log_level))
    sqlite_handler.setFormatter(console_formatter)
    logger.addHandler(sqlite_handler)


def get_logs_from_db(limit: int = 100, level_filter: Optional[str] = None) -> list:
    """Query logs from SQLite database"""
    try:
        db_path = Path("logs/trading_bot.db")
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM logs"
        params = []
        
        if level_filter and level_filter.upper() != "ALL":
            query += " WHERE level = ?"
            params.append(level_filter.upper())
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return list(reversed(logs))  # Return in chronological order
    except Exception as e:
        print(f"Error reading logs from DB: {e}")
        return []
