"""
Data Loader - Funcții pentru încărcarea datelor în dashboard
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.common.utils.config_loader import ConfigLoader


def load_config() -> dict:
    """Încarcă configurația."""
    try:
        possible_paths = [
            "config/config.yaml",
            "config.yaml",
            Path(__file__).parent.parent.parent.parent / "config" / "config.yaml",
        ]
        
        config_loader = ConfigLoader()
        
        for config_path in possible_paths:
            try:
                if isinstance(config_path, Path):
                    if config_path.exists():
                        return config_loader.load_config(str(config_path.relative_to(Path.cwd())))
                else:
                    config_file = Path(config_path)
                    if config_file.exists():
                        return config_loader.load_config(config_path)
            except Exception:
                continue
        
        st.warning("Config file not found, using default settings")
        return {
            'symbols': ['AAPL', 'MSFT'],
            'app': {'mode': 'paper'},
            'data_collector': {
                'symbols': ['AAPL', 'MSFT'],
                'timeframe': '1D',
                'data_dir': 'data/processed'
            }
        }
    except Exception as e:
        st.error(f"Eroare la încărcare config: {e}")
        return {
            'symbols': ['AAPL', 'MSFT'],
            'app': {'mode': 'paper'},
            'data_collector': {
                'symbols': ['AAPL', 'MSFT'],
                'timeframe': '1D',
                'data_dir': 'data/processed'
            }
        }


def get_latest_market_data(symbols: List[str], data_dir: str = "data/market_data") -> pd.DataFrame:
    """Citește ultimele date de piață din CSV."""
    data = []
    
    possible_dirs = [
        Path(data_dir),
        Path("data/market_data"),
        Path("data/processed"),
        Path(__file__).parent.parent.parent.parent / "data" / "market_data",
        Path(__file__).parent.parent.parent.parent / "data" / "processed",
    ]
    
    data_path = None
    for path in possible_dirs:
        if path.exists():
            data_path = path
            break
    
    if not data_path:
        return pd.DataFrame(data)
    
    for symbol in symbols:
        try:
            csv_files = list(data_path.glob(f"{symbol}_*.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
                df = pd.read_csv(latest_file)
                if not df.empty:
                    latest_row = df.iloc[-1]
                    # Calculează change % față de penultimul bar
                    if len(df) > 1:
                        prev_close = df.iloc[-2].get('close', latest_row.get('close', 0))
                        current_close = latest_row.get('close', 0)
                        change_pct = ((current_close - prev_close) / prev_close * 100) if prev_close > 0 else 0.0
                    else:
                        change_pct = 0.0
                    
                    data.append({
                        'symbol': symbol,
                        'price': latest_row.get('close', 0),
                        'change_pct': change_pct,
                        'volume': latest_row.get('volume', 0),
                        'timestamp': latest_row.get('timestamp', '')
                    })
        except Exception:
            pass
    
    return pd.DataFrame(data)


def get_recent_trades(data_dir: str = "data/trades") -> List[dict]:
    """Citește trade-uri recente."""
    trades = []
    trades_path = Path(data_dir)
    
    if trades_path.exists():
        json_files = sorted(trades_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for json_file in json_files[:50]:
            try:
                with open(json_file, 'r') as f:
                    trade = json.load(f)
                    trades.append(trade)
            except Exception:
                pass
    
    return trades


def calculate_metrics(trades: List[dict]) -> dict:
    """Calculează metrici de performanță esențiale."""
    if not trades:
        return {
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'active_positions': 0,
            'daily_pnl': 0.0,
            'weekly_pnl': 0.0
        }
    
    # Calculează P&L total
    total_pnl = sum(trade.get('pnl', 0) for trade in trades if trade.get('status') == 'closed')
    
    # Calculează Win Rate
    closed_trades = [t for t in trades if t.get('status') == 'closed']
    if closed_trades:
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        win_rate = (len(winning_trades) / len(closed_trades)) * 100
    else:
        win_rate = 0.0
    
    # Calculează Max Drawdown (simplificat)
    pnl_values = [t.get('pnl', 0) for t in closed_trades]
    if pnl_values:
        cumulative = []
        running_sum = 0
        for pnl in pnl_values:
            running_sum += pnl
            cumulative.append(running_sum)
        
        if cumulative:
            peak = cumulative[0]
            max_dd = 0.0
            for value in cumulative:
                if value > peak:
                    peak = value
                dd = ((peak - value) / peak * 100) if peak > 0 else 0.0
                if dd > max_dd:
                    max_dd = dd
        else:
            max_dd = 0.0
    else:
        max_dd = 0.0
    
    # Poziții active
    active_positions = len([t for t in trades if t.get('status') == 'open'])
    
    # P&L zilnic/săptămânal (simplificat)
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    daily_trades = [t for t in closed_trades if datetime.fromisoformat(t.get('close_time', '2000-01-01')).date() == today]
    weekly_trades = [t for t in closed_trades if datetime.fromisoformat(t.get('close_time', '2000-01-01')).date() >= week_ago]
    
    daily_pnl = sum(t.get('pnl', 0) for t in daily_trades)
    weekly_pnl = sum(t.get('pnl', 0) for t in weekly_trades)
    
    return {
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'max_drawdown': max_dd,
        'active_positions': active_positions,
        'daily_pnl': daily_pnl,
        'weekly_pnl': weekly_pnl
    }
