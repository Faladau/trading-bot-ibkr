"""
Trading Bot Dashboard - Streamlit UI
Responsive dashboard pentru monitorizare agenți și trading
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import agenți și modele
from src.common.utils.config_loader import ConfigLoader
from src.common.logging_utils.logger import get_logger

# Configure page
st.set_page_config(
    page_title="Trading Bot v6.2 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pentru responsive design
st.markdown("""
<style>
    /* Responsive design pentru mobile */
    @media (max-width: 768px) {
        .stMetric {
            padding: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            margin: 0.25rem 0;
        }
    }
    
    /* Status indicators */
    .status-active {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        text-align: center;
        font-weight: bold;
    }
    
    .status-idle {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.25rem;
        text-align: center;
        font-weight: bold;
    }
    
    .status-monitoring {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem;
        border-radius: 0.25rem;
        text-align: center;
        font-weight: bold;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.25rem;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class DashboardState:
    """Gestionare stare dashboard."""
    
    def __init__(self):
        if 'bot_running' not in st.session_state:
            st.session_state.bot_running = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {
                'agent1': 'IDLE',
                'agent2': 'IDLE',
                'agent3': 'IDLE'
            }


def load_config() -> dict:
    """Încarcă configurația."""
    try:
        # Încearcă mai multe path-uri pentru compatibilitate Streamlit Cloud
        from pathlib import Path
        
        # Path-uri posibile
        possible_paths = [
            "config/config.yaml",  # Local development
            "config.yaml",  # Root
            Path(__file__).parent.parent.parent / "config" / "config.yaml",  # Absolute
        ]
        
        config_loader = ConfigLoader()
        
        # Încearcă fiecare path
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
        
        # Dacă nu găsește, returnează config default
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
        # Returnează config default în caz de eroare
        return {
            'symbols': ['AAPL', 'MSFT'],
            'app': {'mode': 'paper'},
            'data_collector': {
                'symbols': ['AAPL', 'MSFT'],
                'timeframe': '1D',
                'data_dir': 'data/processed'
            }
        }


def get_latest_market_data(symbols: List[str], data_dir: str = "data/processed") -> pd.DataFrame:
    """Citește ultimele date de piață din CSV."""
    data = []
    data_path = Path(data_dir)
    
    for symbol in symbols:
        # Caută cel mai recent fișier CSV pentru simbol
        csv_files = list(data_path.glob(f"{symbol}_*.csv"))
        if csv_files:
            latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
            try:
                df = pd.read_csv(latest_file)
                if not df.empty:
                    latest_row = df.iloc[-1]
                    data.append({
                        'symbol': symbol,
                        'price': latest_row.get('close', 0),
                        'change_pct': 0.0,  # TODO: calculează din date
                        'volume': latest_row.get('volume', 0),
                        'timestamp': latest_row.get('timestamp', '')
                    })
            except Exception as e:
                st.warning(f"Eroare la citire {symbol}: {e}")
    
    return pd.DataFrame(data)


def get_recent_signals(data_dir: str = "data/signals") -> List[dict]:
    """Citește semnale recente."""
    signals = []
    signals_path = Path(data_dir)
    
    if signals_path.exists():
        json_files = sorted(signals_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for json_file in json_files[:10]:  # Ultimele 10
            try:
                with open(json_file, 'r') as f:
                    signal = json.load(f)
                    signals.append(signal)
            except Exception:
                pass
    
    return signals


def get_recent_trades(data_dir: str = "data/trades") -> List[dict]:
    """Citește trade-uri recente."""
    trades = []
    trades_path = Path(data_dir)
    
    if trades_path.exists():
        json_files = sorted(trades_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for json_file in json_files[:10]:  # Ultimele 10
            try:
                with open(json_file, 'r') as f:
                    trade = json.load(f)
                    trades.append(trade)
            except Exception:
                pass
    
    return trades


def calculate_metrics(trades: List[dict]) -> dict:
    """Calculează metrici de performanță."""
    if not trades:
        return {
            'daily_pnl': 0.0,
            'weekly_pnl': 0.0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0
        }
    
    # TODO: Implementare calcul real
    return {
        'daily_pnl': 2453.21,
        'weekly_pnl': 8127.45,
        'total_pnl': -1234.56,
        'win_rate': 67.3,
        'sharpe_ratio': 1.85
    }


def render_agent_status(status: str, agent_name: str) -> str:
    """Randează status agent cu HTML."""
    status_lower = status.lower()
    if status_lower == 'active':
        return f'<div class="status-active">{agent_name}<br>{status}</div>'
    elif status_lower == 'idle':
        return f'<div class="status-idle">{agent_name}<br>{status}</div>'
    elif status_lower == 'monitoring':
        return f'<div class="status-monitoring">{agent_name}<br>{status}</div>'
    else:
        return f'<div class="status-error">{agent_name}<br>{status}</div>'


def main():
    """Funcție principală dashboard."""
    state = DashboardState()
    config = load_config()
    
    # Header
    st.title("📈 Trading Bot v6.2 Dashboard")
    
    # Agent Status Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        agent1_status = st.session_state.agent_status.get('agent1', 'IDLE')
        st.markdown(render_agent_status(agent1_status, "Agent 1"), unsafe_allow_html=True)
        st.caption("Data Collection")
    
    with col2:
        agent2_status = st.session_state.agent_status.get('agent2', 'IDLE')
        st.markdown(render_agent_status(agent2_status, "Agent 2"), unsafe_allow_html=True)
        st.caption("Decision")
    
    with col3:
        agent3_status = st.session_state.agent_status.get('agent3', 'IDLE')
        st.markdown(render_agent_status(agent3_status, "Agent 3"), unsafe_allow_html=True)
        st.caption("Execution")
    
    st.divider()
    
    # Main Content - 2x2 Grid
    col1, col2 = st.columns(2)
    
    # Top Left: Live Market Data
    with col1:
        st.subheader("📊 Live Market Data")
        symbols = config.get('symbols', ['AAPL', 'MSFT'])
        market_data = get_latest_market_data(symbols)
        
        if not market_data.empty:
            for _, row in market_data.iterrows():
                with st.container():
                    col_price, col_change = st.columns([2, 1])
                    with col_price:
                        st.metric(
                            label=row['symbol'],
                            value=f"${row['price']:.2f}",
                            delta=f"{row['change_pct']:.1f}%"
                        )
                    with col_change:
                        # Mini chart placeholder
                        st.line_chart([row['price']] * 10, height=50)
        else:
            st.info("Nu sunt date disponibile. Rulează Agent 1 pentru a colecta date.")
    
    # Top Right: Performance Metrics
    with col2:
        st.subheader("💰 Performance Metrics")
        trades = get_recent_trades()
        metrics = calculate_metrics(trades)
        
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric("Daily PnL", f"${metrics['daily_pnl']:,.2f}")
            st.metric("Weekly PnL", f"${metrics['weekly_pnl']:,.2f}")
        with col_metric2:
            st.metric("Total PnL", f"${metrics['total_pnl']:,.2f}")
            st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
        
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    
    st.divider()
    
    # Bottom Row
    col3, col4 = st.columns(2)
    
    # Bottom Left: Controls
    with col3:
        st.subheader("🎮 Controls")
        
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("▶️ START", type="primary", use_container_width=True):
                st.session_state.bot_running = True
                st.session_state.agent_status['agent1'] = 'ACTIVE'
                st.success("Bot started!")
                st.rerun()
        
        with col_stop:
            if st.button("⏹️ STOP", type="secondary", use_container_width=True):
                st.session_state.bot_running = False
                st.session_state.agent_status = {
                    'agent1': 'IDLE',
                    'agent2': 'IDLE',
                    'agent3': 'IDLE'
                }
                st.warning("Bot stopped!")
                st.rerun()
        
        col_pause, col_reset = st.columns(2)
        with col_pause:
            st.button("⏸️ PAUSE", use_container_width=True)
        with col_reset:
            st.button("🔄 RESET", use_container_width=True)
        
        st.divider()
        
        # Configuration Display
        st.caption("**Configuration**")
        app_config = config.get('app', {})
        st.text(f"Mode: {app_config.get('mode', 'paper').upper()}")
        st.text(f"Risk Level: Medium")
        st.text(f"Max Position: $50k")
        st.text(f"Stop Loss: 2%")
    
    # Bottom Right: Recent Activity Logs
    with col4:
        st.subheader("📋 Recent Activity Logs")
        
        # Simulare logs (în producție, citește din fișiere)
        logs = [
            {"time": "14:32:15", "agent": "Agent 1", "message": "BUY AAPL x100 @ $175.32"},
            {"time": "14:30:42", "agent": "Agent 3", "message": "Market scan completed"},
            {"time": "14:28:09", "agent": "Agent 2", "message": "Position closed +$234"},
            {"time": "14:25:33", "agent": "Agent 1", "message": "SELL MSFT x50 @ $412.85"},
            {"time": "14:22:18", "agent": "System", "message": "All agents initialized"},
        ]
        
        # Adaugă logs reale dacă există
        signals = get_recent_signals()
        for signal in signals[:5]:
            timestamp = signal.get('timestamp', datetime.now().strftime('%H:%M:%S'))
            logs.append({
                "time": timestamp[-8:-3] if len(timestamp) > 8 else timestamp,
                "agent": "Agent 2",
                "message": f"Signal: {signal.get('action', 'N/A')} {signal.get('symbol', '')}"
            })
        
        # Display logs
        for log in logs[:10]:
            st.text(f"**{log['time']}**: {log['agent']}: {log['message']}")
    
    # Auto-refresh
    if st.session_state.bot_running:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
