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
import asyncio

# Import componente și utilități
from src.ui.utils.css_loader import load_css
from src.ui.utils.data_loader import load_config, get_latest_market_data, get_recent_trades, calculate_metrics
from src.ui.components.agent_status import render_agent_status_row
from src.ui.components.metrics import render_metrics
from src.ui.components.watchlist import render_watchlist
from src.agents.data_collection import DataCollectionAgent

# Configure page
st.set_page_config(
    page_title="Trading Bot v6.2 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Încarcă CSS-ul din fișier separat (trebuie să fie primul)
load_css()

# CSS suplimentar inline pentru a forța layout-ul după refresh
# Folosim multiple selectori și !important pentru a suprascrie Streamlit
st.markdown("""
<style>
    /* Force layout 80% - aplicat după load_css pentru a suprascrie */
    section[data-testid="stAppViewContainer"] {
        max-width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 2rem !important;
        width: 80% !important;
    }
    .main .block-container {
        max-width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 2rem !important;
        width: 80% !important;
    }
    /* Force pentru Streamlit wide layout - multiple selectori */
    .stApp > div:first-child > div:first-child {
        max-width: 80% !important;
        margin: 0 auto !important;
        width: 80% !important;
    }
    /* Override pentru toate containerele principale */
    .main {
        max-width: 80% !important;
        margin: 0 auto !important;
    }
    /* Force pentru elementele Streamlit care pot suprascrie */
    [data-testid="stAppViewContainer"] > div {
        max-width: 80% !important;
        margin: 0 auto !important;
    }
</style>
<script>
    // Force layout 80% după ce pagina se încarcă complet
    function forceLayout80() {
        const containers = document.querySelectorAll('section[data-testid="stAppViewContainer"], .main .block-container');
        containers.forEach(container => {
            container.style.maxWidth = '80%';
            container.style.marginLeft = 'auto';
            container.style.marginRight = 'auto';
            container.style.padding = '2rem';
        });
    }
    // Rulează imediat și după ce DOM-ul se încarcă
    forceLayout80();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceLayout80);
    } else {
        forceLayout80();
    }
    // Rulează și după un mic delay pentru a acoperi cazurile când Streamlit aplică stilurile mai târziu
    setTimeout(forceLayout80, 100);
    setTimeout(forceLayout80, 500);
    setTimeout(forceLayout80, 1000);
</script>
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
    
    # Background simplu dark, fără mov + text alb forțat + layout 80%
    st.markdown("""
    <style>
    .stApp {
        background: #1a1a2e !important;
        color: #ffffff !important;
    }
    .stApp * {
        color: #ffffff !important;
    }
    /* Force 80% width pentru container principal - IMPORTANT pentru refresh */
    section[data-testid="stAppViewContainer"] {
        max-width: 80% !important;
        margin: 0 auto !important;
        padding: 2rem !important;
    }
    .main .block-container {
        max-width: 80% !important;
        margin: 0 auto !important;
        padding: 2rem !important;
    }
    /* Force white text pentru toate elementele Streamlit */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp p, .stApp div, .stApp span, .stApp label {
        color: #ffffff !important;
    }
    .stApp .stCaption {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
    
    # Bottom: Controls + Activity Log
    col_controls, col_logs = st.columns(2)
    
    # Controls
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
        
        # Simulare logs
        logs = [
            {"time": "14:32:15", "agent": "Agent 1", "message": "Data collection completed"},
            {"time": "14:30:42", "agent": "Agent 3", "message": "Market scan completed"},
            {"time": "14:28:09", "agent": "Agent 2", "message": "Signal generated"},
            {"time": "14:25:33", "agent": "Agent 1", "message": "Data collection started"},
            {"time": "14:22:18", "agent": "System", "message": "All agents initialized"},
        ]
        
        # Adaugă logs reale dacă există
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
            import time
            time.sleep(60)
            st.rerun()


if __name__ == "__main__":
    main()
