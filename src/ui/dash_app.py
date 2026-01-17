"""
Trading Bot Dashboard - Dash/Plotly UI
Dashboard modern pentru monitorizare trading bot
Deployment-ready pentru server propriu

Arhitectură modulară:
- CSS: src/ui/static/css/dashboard.css
- Components: src/ui/components/
- Callbacks: src/ui/callbacks/
- Utils: src/ui/utils/
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from datetime import datetime
import asyncio
from pathlib import Path

# Import utilități și componente
from src.ui.utils.data_loader import load_config, get_latest_market_data, get_recent_trades, calculate_metrics
from src.ui.components.dash_components import (
    render_agent_status_row,
    render_metrics_dash,
    render_watchlist_dash,
    render_equity_curve_chart
)
from src.ui.callbacks.dashboard_callbacks import register_callbacks
from src.agents.data_collection import DataCollectionAgent

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[],
    suppress_callback_exceptions=True
)

# Load CSS
css_path = Path(__file__).parent / "static" / "css" / "dashboard.css"
if css_path.exists():
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>Trading Bot v6.2 Dashboard</title>
            <style>{css_content}</style>
            {{%favicon%}}
            {{%css%}}
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    '''

# App layout
app.layout = html.Div([
    # Background simplu dark, fără mov
    html.Div(
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'background': '#1a1a2e',
            'z-index': 0,
            'pointer-events': 'none'
        }
    ),
    
    # Main content
    html.Div([
        # Header
        html.Div([
            html.H1(
                "📈 Trading Bot v6.2",
                style={
                    'color': '#ffffff',
                    'font-size': '3rem',
                    'margin-bottom': '0.5rem',
                    'text-shadow': '0 2px 10px rgba(102, 126, 234, 0.5)',
                    'text-align': 'center'
                }
            ),
            html.P(
                "Dashboard de Monitorizare",
                style={
                    'color': 'rgba(255, 255, 255, 0.7)',
                    'font-size': '1.2rem',
                    'text-align': 'center'
                }
            ),
        ], style={'padding': '2rem 0', 'position': 'relative', 'z-index': 10, 'margin-bottom': '2rem'}),
        
        # Agent Status Row
        html.Div(id='agent-status-row', style={'position': 'relative', 'z-index': 10}),
        
        # Last update
        html.Div(id='last-update', style={'position': 'relative', 'z-index': 10}),
        
        html.Hr(style={'border-color': 'rgba(255, 255, 255, 0.2)'}),
        
        # Metrics
        html.Div(id='metrics-container', style={'position': 'relative', 'z-index': 10}),
        
        html.Hr(style={'border-color': 'rgba(255, 255, 255, 0.2)'}),
        
        # Main content - 2 columns
        html.Div([
            html.Div(id='watchlist-container', style={'position': 'relative', 'z-index': 10}),
            html.Div(id='positions-container', style={'position': 'relative', 'z-index': 10}),
        ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '2rem'}),
        
        html.Hr(style={'border-color': 'rgba(255, 255, 255, 0.2)'}),
        
        # Equity Curve Chart
        html.Div(id='equity-curve-container', style={'position': 'relative', 'z-index': 10}),
        
        html.Hr(style={'border-color': 'rgba(255, 255, 255, 0.2)'}),
        
        # Bottom - Controls + Activity Log
        html.Div([
            html.Div(id='controls-container', style={'position': 'relative', 'z-index': 10}),
            html.Div(id='activity-log-container', style={'position': 'relative', 'z-index': 10}),
        ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '2rem'}),
        
        # Refresh button
        html.Div([
            html.Button(
                "🔄 Refresh Data",
                id='refresh-btn',
                n_clicks=0,
                style={
                    'padding': '0.5rem 1rem',
                    'border-radius': '10px',
                    'border': 'none',
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': '#ffffff',
                    'cursor': 'pointer',
                    'font-weight': 'bold'
                }
            ),
            dcc.Checklist(
                id='auto-refresh',
                options=[{'label': '🔄 Auto-refresh (60s)', 'value': 'enabled'}],
                value=[],
                style={'color': '#ffffff', 'margin-left': '1rem'}
            ),
        ], style={'margin-top': '2rem', 'position': 'relative', 'z-index': 10}),
        
    ], style={'position': 'relative', 'z-index': 10, 'max-width': '80%', 'margin': '0 auto', 'padding': '2rem'}),
    
    # Interval pentru auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=60000,  # 60 seconds
        n_intervals=0,
        disabled=True
    ),
    
    # Store pentru state
    dcc.Store(id='agent-status-store', data={'agent1': 'IDLE', 'agent2': 'IDLE', 'agent3': 'IDLE'}),
    dcc.Store(id='last-update-store', data=datetime.now().isoformat()),
], style={'min-height': '100vh', 'position': 'relative'})

# Register callbacks
register_callbacks(app)

# Server pentru production
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
