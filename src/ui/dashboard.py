"""
Trading Bot Dashboard - Streamlit UI
Dashboard atractiv pentru monitorizare trading bot
Optimizat pentru verificare 1-2x pe zi

Arhitectură modulară:
- CSS: src/ui/static/css/dashboard.css
- Components: src/ui/components/
- Utils: src/ui/utils/
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import threading

# Import componente și utilități
from src.ui.utils.css_loader import load_all_css
from src.ui.utils.data_loader import load_config, get_latest_market_data, get_recent_trades, calculate_metrics
from src.ui.components.agent_status import render_agent_status_row
from src.ui.components.metrics import render_metrics
from src.ui.components.watchlist import render_watchlist
from src.agents.data_collection import DataCollectionAgent
from src.common.logging_utils import get_logger

logger = get_logger(__name__)

# Configure page
st.set_page_config(
    page_title="Trading Bot v6.2 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS LOADING - BEST PRACTICE ====================
# Încarcă TOATE fișierele CSS din src/ui/static/css/
# CSS-ul e separat, portabil, reusabil - nu depinde de Streamlit
load_all_css()


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


def run_data_collection_agent_thread():
    """Rulează Data Collection Agent în background thread."""
    import asyncio
    
    try:
        agent = DataCollectionAgent()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        is_ready = loop.run_until_complete(agent.initialize())
        if is_ready:
            loop.run_until_complete(agent.collect_all())
            loop.run_until_complete(agent.shutdown())
            st.session_state.agent_status['agent1'] = 'IDLE'
            st.session_state.last_update = datetime.now()
            logger.info("✅ Data Collection Agent completed successfully")
        else:
            st.session_state.agent_status['agent1'] = 'ERROR'
            logger.error("❌ Agent initialization failed")
    except Exception as e:
        logger.error(f"❌ Error in Data Collection Agent: {e}")
        st.session_state.agent_status['agent1'] = 'ERROR'
    finally:
        try:
            loop.close()
        except:
            pass


def render_equity_curve_chart(trades: list) -> None:
    """
    Randează equity curve chart folosind Plotly (modern, nu SVG vechi).
    
    Args:
        trades: Lista de trade-uri
    """
    if not trades:
        st.info("Nu există date pentru equity curve")
        return
    
    # Calculează equity curve
    closed_trades = [t for t in trades if t.get('status') == 'closed']
    if not closed_trades:
        st.info("Nu există trade-uri închise pentru equity curve")
        return
    
    cumulative_pnl = []
    running_sum = 0
    dates = []
    
    for trade in sorted(closed_trades, key=lambda x: x.get('close_time', '2000-01-01')):
        running_sum += trade.get('pnl', 0)
        cumulative_pnl.append(running_sum)
        dates.append(trade.get('close_time', datetime.now().isoformat()))
    
    # Creează chart Plotly modern
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative_pnl,
        mode='lines',
        name='Equity Curve',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.update_layout(
        title="📈 Equity Curve",
        xaxis_title="Data",
        yaxis_title="P&L Cumulativ ($)",
        template="plotly_dark",
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Funcție principală dashboard."""
    state = DashboardState()
    config = load_config()
    
    # Container principal pe 80% din pagină
    with st.container():
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #ffffff; font-size: 3rem; margin-bottom: 0.5rem;">📈 Trading Bot v6.2</h1>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 1.2rem;">Dashboard de Monitorizare</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Agent Status Row (folosind componentă)
    render_agent_status_row(st.session_state.agent_status)
    
    # Last update
    last_update_str = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🕐 Ultima actualizare: {last_update_str} | Mode: {config.get('app', {}).get('mode', 'paper').upper()}")
    
    st.divider()
    
    # Metrici Esențiale (folosind componentă)
    trades = get_recent_trades()
    metrics = calculate_metrics(trades)
    render_metrics(metrics)
    
    st.divider()
    
    # Secțiunea principală - 2 coloane
    col_left, col_right = st.columns(2)
    
    # Left: Watchlist (folosind componentă)
    with col_left:
        symbols = config.get('data_collector', {}).get('symbols', config.get('symbols', ['AAPL', 'MSFT']))
        market_data = get_latest_market_data(symbols)
        render_watchlist(symbols, market_data)
    
    # Right: Poziții Active
    with col_right:
        st.subheader("💼 Poziții Active")
        if metrics.get('active_positions', 0) > 0:
            st.info(f"📌 {metrics.get('active_positions', 0)} poziții active")
            st.caption("Detalii poziții vor fi afișate când Agent 3 este implementat")
        else:
            st.info("ℹ️ Nu există poziții active")
    
    st.divider()
    
    # Equity Curve Chart (Plotly modern)
    render_equity_curve_chart(trades)
    
    st.divider()
    
    # Bottom: Controls + Activity Log (4 coloane pentru butoane)
    st.subheader("🎮 Controls")
    col_start, col_stop, col_refresh, col_empty = st.columns(4)
    
    with col_start:
        if st.button("▶️ START", type="primary", use_container_width=True):
            st.session_state.bot_running = True
            st.session_state.agent_status['agent1'] = 'ACTIVE'
            st.success("Bot started!")
            
            thread = threading.Thread(target=run_data_collection_agent_thread, daemon=True)
            thread.start()
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
    
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Layout: Controls (left) + Activity Log (right)
    col_config, col_activity = st.columns(2)
    
    with col_config:
        st.caption("**⚙️ Configuration**")
        app_config = config.get('app', {})
        st.text(f"Mode: {app_config.get('mode', 'paper').upper()}")
        st.text(f"Risk Level: Medium")
        st.text(f"Max Position: $50k")
        st.text(f"Stop Loss: 2%")
        
        auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=False)
        if auto_refresh:
            import time
            time.sleep(60)
            st.rerun()
    
    with col_activity:
        st.subheader("📋 Recent Activity")
        
        logs = [
            {"time": "14:32:15", "agent": "Agent 1", "message": "Data collection completed"},
            {"time": "14:30:42", "agent": "Agent 3", "message": "Market scan completed"},
            {"time": "14:28:09", "agent": "Agent 2", "message": "Signal generated"},
            {"time": "14:25:33", "agent": "Agent 1", "message": "Data collection started"},
            {"time": "14:22:18", "agent": "System", "message": "All agents initialized"},
        ]
        
        from pathlib import Path
        signals_path = Path("data/signals")
        if signals_path.exists():
            json_files = sorted(signals_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            for json_file in json_files[:5]:
                try:
                    import json
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
        
        for log in logs[:10]:
            st.text(f"**{log['time']}**: {log['agent']}: {log['message']}")


if __name__ == "__main__":
    main()
