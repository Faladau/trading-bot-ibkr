"""
Structured Logging Configuration with Structlog + SQLite
Production-grade logging with JSON output and database persistence
"""

import structlog
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class SQLiteLogHandler:
    """Writes structured logs to SQLite database"""
    
    def __init__(self, db_path: str = "logs/trading_bot.db"):
        """Initialize SQLite log handler"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create logs table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                module TEXT,
                message TEXT,
                context TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def __call__(self, logger, method_name: str, event_dict: Dict[str, Any]) -> str:
        """Log to SQLite - structlog processor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = event_dict.pop('timestamp', datetime.utcnow().isoformat())
            level = event_dict.pop('level', method_name.upper())
            module = event_dict.pop('_name', 'unknown')
            message = event_dict.pop('event', '')
            context = json.dumps({k: str(v) for k, v in event_dict.items() if k not in ['_name', 'timestamp']})
            
            cursor.execute(
                """INSERT INTO logs (timestamp, level, module, message, context)
                   VALUES (?, ?, ?, ?, ?)""",
                (timestamp, level, module, message, context)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error writing to SQLite: {e}")
        
        # Return formatted string for console output
        return f"[{level}] {module}: {message}"


def configure_structlog(log_level: str = "INFO", use_json: bool = False):
    """
    Configure structlog with SQLite persistence
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        use_json: Output JSON format (for production)
    """
    
    if use_json:
        # Production: JSON output
        structlog.configure(
            processors=[
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )
    else:
        # Development: Pretty console output
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )
    
    # Add SQLite handler to all loggers
    structlog.configure(
        processors=[
            SQLiteLogHandler(),
            structlog.processors.JSONRenderer()
        ] if use_json else [
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            SQLiteLogHandler(),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logs_from_db(limit: int = 100, level_filter: str = None) -> list:
    """Query logs from SQLite database"""
    try:
        db_path = Path("logs/trading_bot.db")
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM logs"
        params = []
        
        if level_filter:
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
