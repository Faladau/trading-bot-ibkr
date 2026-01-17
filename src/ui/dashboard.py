"""
Trading Bot Dashboard - Streamlit UI
Dashboard atractiv pentru monitorizare trading bot
Optimizat pentru verificare 1-2x pe zi
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import asyncio
import threading

# Import agenți și modele
from src.common.utils.config_loader import ConfigLoader
from src.common.logging_utils.logger import get_logger
from src.agents.data_collection import DataCollectionAgent

# Configure page
st.set_page_config(
    page_title="Trading Bot v6.2 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL-uri pentru imagini de background gratuite (Pixabay, Unsplash, etc.)
# Folosim SVG inline ca fallback dacă URL-urile nu funcționează
TRADING_BG_IMAGE_URL = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1920&q=80&auto=format&fit=crop"  # Stock chart
# Alternativ: "https://cdn.pixabay.com/photo/2016/11/19/14/00/code-1839406_1280.jpg"  # Tech background

# SVG inline elaborat pentru grafice financiare subtile (fallback)
TRADING_CHART_SVG = """
<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="position: fixed; top: 0; left: 0; z-index: 0; opacity: 0.12; pointer-events: none;">
    <defs>
        <!-- Grid pattern -->
        <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
            <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(102, 126, 234, 0.25)" stroke-width="0.5"/>
        </pattern>
        <!-- Candlestick pattern -->
        <g id="candlestick-up">
            <line x1="0" y1="15" x2="0" y2="5" stroke="rgba(76, 175, 80, 0.5)" stroke-width="2"/>
            <rect x="-4" y="3" width="8" height="4" fill="rgba(76, 175, 80, 0.4)"/>
        </g>
        <g id="candlestick-down">
            <line x1="0" y1="5" x2="0" y2="15" stroke="rgba(244, 67, 54, 0.5)" stroke-width="2"/>
            <rect x="-4" y="13" width="8" height="4" fill="rgba(244, 67, 54, 0.4)"/>
        </g>
        <!-- Gradient pentru background -->
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#0f0c29;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#302b63;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#24243e;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="100%" height="100%" fill="url(#bgGradient)"/>
    
    <!-- Grid -->
    <rect width="100%" height="100%" fill="url(#grid)"/>
    
    <!-- Multiple candlesticks pattern -->
    <use href="#candlestick-up" x="8%" y="25%" transform="scale(1.5)"/>
    <use href="#candlestick-down" x="15%" y="40%" transform="scale(1.2)"/>
    <use href="#candlestick-up" x="22%" y="18%" transform="scale(1.8)"/>
    <use href="#candlestick-down" x="30%" y="55%" transform="scale(1.0)"/>
    <use href="#candlestick-up" x="38%" y="32%" transform="scale(1.3)"/>
    <use href="#candlestick-down" x="45%" y="48%" transform="scale(1.6)"/>
    <use href="#candlestick-up" x="52%" y="22%" transform="scale(1.1)"/>
    <use href="#candlestick-down" x="60%" y="38%" transform="scale(1.4)"/>
    <use href="#candlestick-up" x="68%" y="28%" transform="scale(1.7)"/>
    <use href="#candlestick-down" x="75%" y="45%" transform="scale(1.2)"/>
    <use href="#candlestick-up" x="82%" y="35%" transform="scale(1.5)"/>
    <use href="#candlestick-down" x="90%" y="50%" transform="scale(1.3)"/>
    
    <!-- Trend lines -->
    <line x1="5%" y1="35%" x2="35%" y2="25%" stroke="rgba(102, 126, 234, 0.35)" stroke-width="1.5" stroke-dasharray="8,4"/>
    <line x1="25%" y1="55%" x2="65%" y2="30%" stroke="rgba(118, 75, 162, 0.35)" stroke-width="1.5" stroke-dasharray="8,4"/>
    <line x1="45%" y1="65%" x2="85%" y2="40%" stroke="rgba(76, 175, 80, 0.35)" stroke-width="1.5" stroke-dasharray="8,4"/>
    
    <!-- Support/Resistance -->
    <line x1="0" y1="35%" x2="100%" y2="35%" stroke="rgba(76, 175, 80, 0.25)" stroke-width="1.5"/>
    <line x1="0" y1="25%" x2="100%" y2="25%" stroke="rgba(244, 67, 54, 0.25)" stroke-width="1.5"/>
    
    <!-- Chart curves -->
    <path d="M 5% 60% Q 25% 50%, 45% 55% T 85% 60%" fill="none" stroke="rgba(102, 126, 234, 0.3)" stroke-width="2.5"/>
    <path d="M 10% 75% Q 30% 65%, 50% 70% T 90% 75%" fill="none" stroke="rgba(118, 75, 162, 0.3)" stroke-width="2.5"/>
    <path d="M 15% 50% Q 35% 40%, 55% 45% T 95% 50%" fill="none" stroke="rgba(76, 175, 80, 0.3)" stroke-width="2.5"/>
</svg>
"""

# Custom CSS cu background atractiv și grafice subtile de trading
st.markdown("""
<style>
    /* Background gradient cu pattern-uri de trading */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
        position: relative;
        overflow: hidden;
    }
    
    /* SVG background overlay */
    .trading-bg-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        pointer-events: none;
        opacity: 0.15;
    }
    
    /* Pattern-uri CSS suplimentare */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 20px,
                rgba(102, 126, 234, 0.03) 20px,
                rgba(102, 126, 234, 0.03) 21px
            ),
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 40px,
                rgba(118, 75, 162, 0.03) 40px,
                rgba(118, 75, 162, 0.03) 41px
            );
        pointer-events: none;
        z-index: 0;
    }
    
    /* Carduri glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 1rem;
    }
    
    /* Status indicators cu glow */
    .status-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .status-idle {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .status-monitoring {
        background: rgba(23, 162, 184, 0.2);
        color: #17a2b8;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        border: 1px solid rgba(23, 162, 184, 0.3);
    }
    
    .status-error {
        background: rgba(220, 53, 69, 0.2);
        color: #dc3545;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        border: 1px solid rgba(220, 53, 69, 0.3);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* Butoane moderne */
    .stButton>button {
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .stMetric {
            padding: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            margin: 0.25rem 0;
        }
    }
    
    /* Text color pentru dark background */
    h1, h2, h3, h4, h5, h6, p, .stText {
        color: #ffffff;
    }
    
    /* Container styling */
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Asigură că conținutul este deasupra pattern-urilor */
    .main > div {
        position: relative;
        z-index: 10;
    }
    
    /* Streamlit specific - forțează background */
    section[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
    }
    
    /* Header background */
    header[data-testid="stHeader"] {
        background: rgba(15, 12, 41, 0.8) !important;
    }
    
    /* Candlesticks decorative în colțuri */
    .candlestick-decoration {
        position: fixed;
        width: 3px;
        height: 20px;
        background: linear-gradient(to bottom, 
            rgba(76, 175, 80, 0.3) 0%,
            rgba(76, 175, 80, 0.3) 40%,
            rgba(76, 175, 80, 0.1) 40%,
            rgba(76, 175, 80, 0.1) 60%,
            rgba(76, 175, 80, 0.3) 60%,
            rgba(76, 175, 80, 0.3) 100%
        );
        pointer-events: none;
        z-index: 0;
    }
    
    /* Linii de support/resistance subtile */
    .support-line {
        position: fixed;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%,
            rgba(76, 175, 80, 0.2) 20%,
            rgba(76, 175, 80, 0.2) 80%,
            transparent 100%
        );
        pointer-events: none;
        z-index: 0;
    }
    
    .resistance-line {
        position: fixed;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%,
            rgba(244, 67, 54, 0.2) 20%,
            rgba(244, 67, 54, 0.2) 80%,
            transparent 100%
        );
        pointer-events: none;
        z-index: 0;
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
        from pathlib import Path
        
        possible_paths = [
            "config/config.yaml",
            "config.yaml",
            Path(__file__).parent.parent.parent / "config" / "config.yaml",
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


def get_latest_market_data(symbols: List[str], data_dir: str = "data/processed") -> pd.DataFrame:
    """Citește ultimele date de piață din CSV."""
    data = []
    
    possible_dirs = [
        Path(data_dir),
        Path("data/processed"),
        Path(__file__).parent.parent.parent / "data" / "processed",
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
        for json_file in json_files[:50]:  # Ultimele 50 pentru calcul metrici
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


def render_agent_status(status: str, agent_name: str) -> str:
    """Randează status agent cu HTML."""
    status_lower = status.lower()
    if status_lower == 'active':
        return f'<div class="status-active">{agent_name}<br><strong>{status}</strong></div>'
    elif status_lower == 'idle':
        return f'<div class="status-idle">{agent_name}<br><strong>{status}</strong></div>'
    elif status_lower == 'monitoring':
        return f'<div class="status-monitoring">{agent_name}<br><strong>{status}</strong></div>'
    else:
        return f'<div class="status-error">{agent_name}<br><strong>{status}</strong></div>'


async def run_data_collection_agent():
    """Rulează Data Collection Agent în background."""
    try:
        agent = DataCollectionAgent()
        if await agent.initialize():
            await agent.collect_all()
            await agent.shutdown()
            st.session_state.agent_status['agent1'] = 'IDLE'
            st.session_state.last_update = datetime.now()
    except Exception as e:
        st.error(f"Eroare la rulare Agent 1: {e}")
        st.session_state.agent_status['agent1'] = 'ERROR'


def main():
    """Funcție principală dashboard."""
    state = DashboardState()
    config = load_config()
    
    # Adaugă SVG cu grafice financiare în background (overlay peste background image)
    st.markdown(f"""
    <div class="trading-bg-overlay">
        {TRADING_CHART_SVG}
    </div>
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(15, 12, 41, 0.85) 0%, rgba(48, 43, 99, 0.85) 50%, rgba(36, 36, 62, 0.85) 100%); z-index: 0; pointer-events: none;"></div>
    """, unsafe_allow_html=True)
    
    # Header cu gradient
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; position: relative; z-index: 10;">
        <h1 style="color: #ffffff; font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);">📈 Trading Bot v6.2</h1>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 1.2rem;">Dashboard de Monitorizare</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Last update
    last_update_str = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🕐 Ultima actualizare: {last_update_str} | Mode: {config.get('app', {}).get('mode', 'paper').upper()}")
    
    st.divider()
    
    # Main Content - Metrici Esențiale
    st.subheader("💰 Metrici Esențiale")
    
    trades = get_recent_trades()
    metrics = calculate_metrics(trades)
    
    # Metrici principale în 2 coloane
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        pnl_color = "normal" if metrics['total_pnl'] >= 0 else "inverse"
        st.metric(
            "💵 Total P&L",
            f"${metrics['total_pnl']:,.2f}",
            delta=f"{metrics['total_pnl']:+,.2f}" if metrics['total_pnl'] != 0 else None,
            delta_color=pnl_color
        )
    
    with col_metric2:
        st.metric(
            "🎯 Win Rate",
            f"{metrics['win_rate']:.1f}%",
            delta=f"{metrics['win_rate']:.1f}%" if metrics['win_rate'] > 0 else None
        )
    
    with col_metric3:
        dd_color = "inverse" if metrics['max_drawdown'] > 5 else "normal"
        st.metric(
            "📉 Max Drawdown",
            f"{metrics['max_drawdown']:.2f}%",
            delta=f"-{metrics['max_drawdown']:.2f}%" if metrics['max_drawdown'] > 0 else None,
            delta_color=dd_color
        )
    
    with col_metric4:
        st.metric(
            "📊 Poziții Active",
            f"{metrics['active_positions']}",
            delta=f"{metrics['active_positions']}" if metrics['active_positions'] > 0 else None
        )
    
    st.divider()
    
    # Secțiunea principală - 2 coloane
    col_left, col_right = st.columns(2)
    
    # Left: Watchlist + Market Data
    with col_left:
        st.subheader("📊 Watchlist")
        symbols = config.get('data_collector', {}).get('symbols', config.get('symbols', ['AAPL', 'MSFT']))
        market_data = get_latest_market_data(symbols)
        
        if not market_data.empty:
            for _, row in market_data.iterrows():
                change_color = "normal" if row['change_pct'] >= 0 else "inverse"
                st.metric(
                    label=row['symbol'],
                    value=f"${row['price']:.2f}",
                    delta=f"{row['change_pct']:+.2f}%",
                    delta_color=change_color
                )
        else:
            st.info("ℹ️ Nu sunt date disponibile. Rulează Agent 1 pentru a colecta date.")
    
    # Right: Poziții Active (când Agent 3 e implementat)
    with col_right:
        st.subheader("💼 Poziții Active")
        if metrics['active_positions'] > 0:
            # TODO: Citește poziții reale din data/trades când Agent 3 e implementat
            st.info(f"📌 {metrics['active_positions']} poziții active")
            st.caption("Detalii poziții vor fi afișate când Agent 3 este implementat")
        else:
            st.info("ℹ️ Nu există poziții active")
    
    st.divider()
    
    # Bottom: Controls + Activity Log
    col_controls, col_logs = st.columns(2)
    
    # Controls (secundar - focus pe monitorizare)
    with col_controls:
        st.subheader("🎮 Controls")
        
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("▶️ START", type="primary", use_container_width=True):
                st.session_state.bot_running = True
                st.session_state.agent_status['agent1'] = 'ACTIVE'
                st.success("Bot started!")
                
                # Rulează Agent 1 în background
                asyncio.create_task(run_data_collection_agent())
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
        
        st.divider()
        
        # Configuration Display
        st.caption("**⚙️ Configuration**")
        app_config = config.get('app', {})
        st.text(f"Mode: {app_config.get('mode', 'paper').upper()}")
        st.text(f"Risk Level: Medium")
        st.text(f"Max Position: $50k")
        st.text(f"Stop Loss: 2%")
    
    # Activity Log
    with col_logs:
        st.subheader("📋 Recent Activity")
        
        # Simulare logs (în producție, citește din fișiere)
        logs = [
            {"time": "14:32:15", "agent": "Agent 1", "message": "Data collection completed"},
            {"time": "14:30:42", "agent": "Agent 3", "message": "Market scan completed"},
            {"time": "14:28:09", "agent": "Agent 2", "message": "Signal generated"},
            {"time": "14:25:33", "agent": "Agent 1", "message": "Data collection started"},
            {"time": "14:22:18", "agent": "System", "message": "All agents initialized"},
        ]
        
        # Adaugă logs reale dacă există
        signals_path = Path("data/signals")
        if signals_path.exists():
            json_files = sorted(signals_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            for json_file in json_files[:5]:
                try:
                    with open(json_file, 'r') as f:
                        signal = json.load(f)
                        timestamp = signal.get('timestamp', datetime.now().isoformat())
                        time_str = timestamp[-8:-3] if len(timestamp) > 8 else datetime.now().strftime('%H:%M:%S')
                        logs.append({
                            "time": time_str,
                            "agent": "Agent 2",
                            "message": f"Signal: {signal.get('action', 'N/A')} {signal.get('symbol', '')}"
                        })
                except Exception:
                    pass
        
        # Display logs
        for log in logs[:10]:
            st.text(f"**{log['time']}**: {log['agent']}: {log['message']}")
    
    # Refresh opțional
    st.divider()
    col_refresh, _ = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=False)
        if auto_refresh:
            time.sleep(60)
            st.rerun()
    
    # Închide div-ul pentru z-index
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
