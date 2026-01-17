"""
Dashboard Callbacks - Callbacks pentru interactivitate Dash
"""

from dash import Input, Output, State, html
from datetime import datetime
import asyncio

from src.ui.utils.data_loader import load_config, get_latest_market_data, get_recent_trades, calculate_metrics
from src.ui.components.dash_components import (
    render_agent_status_row,
    render_metrics_dash,
    render_watchlist_dash,
    render_equity_curve_chart
)


def register_callbacks(app):
    """Înregistrează toate callbacks-urile pentru dashboard."""
    
    @app.callback(
        [
            Output('agent-status-row', 'children'),
            Output('last-update', 'children'),
            Output('metrics-container', 'children'),
            Output('watchlist-container', 'children'),
            Output('positions-container', 'children'),
            Output('equity-curve-container', 'children'),
            Output('activity-log-container', 'children'),
            Output('interval-component', 'disabled'),
            Output('agent-status-store', 'data'),
            Output('last-update-store', 'data')
        ],
        [
            Input('interval-component', 'n_intervals'),
            Input('refresh-btn', 'n_clicks'),
            Input('auto-refresh', 'value')
        ],
        [
            State('agent-status-store', 'data'),
            State('last-update-store', 'data')
        ]
    )
    def update_dashboard(n_intervals, refresh_clicks, auto_refresh, agent_statuses, last_update_str):
        """Callback principal pentru actualizarea dashboard-ului."""
        
        # Load data
        config = load_config()
        trades = get_recent_trades()
        metrics = calculate_metrics(trades)
        symbols = config.get('data_collector', {}).get('symbols', config.get('symbols', ['AAPL', 'MSFT']))
        market_data = get_latest_market_data(symbols)
        
        # Update last update time
        last_update = datetime.now()
        last_update_str = last_update.strftime("%Y-%m-%d %H:%M:%S")
        
        # Render components
        agent_status_row = render_agent_status_row(agent_statuses)
        last_update_div = html.Div(
            f"🕐 Ultima actualizare: {last_update_str} | Mode: {config.get('app', {}).get('mode', 'paper').upper()}",
            style={'color': 'rgba(255, 255, 255, 0.7)', 'text-align': 'center', 'margin-bottom': '1rem'}
        )
        metrics_container = render_metrics_dash(metrics)
        watchlist_container = render_watchlist_dash(symbols, market_data)
        
        # Positions container
        active_pos = metrics.get('active_positions', 0)
        if active_pos > 0:
            positions_container = html.Div([
                html.H3("💼 Poziții Active", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
                html.Div(
                    f"📌 {active_pos} poziții active",
                    style={
                        'background': 'rgba(23, 162, 184, 0.2)',
                        'color': '#17a2b8',
                        'padding': '1rem',
                        'border-radius': '10px',
                        'border': '1px solid rgba(23, 162, 184, 0.3)'
                    }
                ),
                html.P("Detalii poziții vor fi afișate când Agent 3 este implementat", 
                       style={'color': 'rgba(255, 255, 255, 0.7)', 'margin-top': '0.5rem'})
            ])
        else:
            positions_container = html.Div([
                html.H3("💼 Poziții Active", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
                html.Div(
                    "ℹ️ Nu există poziții active",
                    style={
                        'background': 'rgba(23, 162, 184, 0.2)',
                        'color': '#17a2b8',
                        'padding': '1rem',
                        'border-radius': '10px',
                        'border': '1px solid rgba(23, 162, 184, 0.3)'
                    }
                )
            ])
        
        # Equity curve
        equity_curve = render_equity_curve_chart(trades)
        
        # Activity log
        logs = [
            {"time": "14:32:15", "agent": "Agent 1", "message": "Data collection completed"},
            {"time": "14:30:42", "agent": "Agent 3", "message": "Market scan completed"},
            {"time": "14:28:09", "agent": "Agent 2", "message": "Signal generated"},
            {"time": "14:25:33", "agent": "Agent 1", "message": "Data collection started"},
            {"time": "14:22:18", "agent": "System", "message": "All agents initialized"},
        ]
        
        activity_log_items = []
        for log in logs[:10]:
            activity_log_items.append(html.Div(
                f"{log['time']}: {log['agent']}: {log['message']}",
                style={'color': '#ffffff', 'padding': '0.5rem 0', 'border-bottom': '1px solid rgba(255, 255, 255, 0.1)'}
            ))
        
        activity_log = html.Div([
            html.H3("📋 Recent Activity", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
            html.Div(activity_log_items)
        ])
        
        # Auto-refresh enabled/disabled
        interval_disabled = 'enabled' not in (auto_refresh or [])
        
        return (
            agent_status_row,
            last_update_div,
            metrics_container,
            watchlist_container,
            positions_container,
            equity_curve,
            activity_log,
            interval_disabled,
            agent_statuses,
            last_update_str
        )
    
    @app.callback(
        Output('controls-container', 'children'),
        Input('refresh-btn', 'n_clicks')
    )
    def render_controls(n_clicks):
        """Randează controls container."""
        config = load_config()
        app_config = config.get('app', {})
        
        return html.Div([
            html.H3("🎮 Controls", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
            html.Div([
                html.Button(
                    "▶️ START",
                    id='start-btn',
                    n_clicks=0,
                    style={
                        'padding': '0.75rem 1.5rem',
                        'border-radius': '10px',
                        'border': 'none',
                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'color': '#ffffff',
                        'cursor': 'pointer',
                        'font-weight': 'bold',
                        'flex': 1,
                        'margin-right': '0.5rem'
                    }
                ),
                html.Button(
                    "⏹️ STOP",
                    id='stop-btn',
                    n_clicks=0,
                    style={
                        'padding': '0.75rem 1.5rem',
                        'border-radius': '10px',
                        'border': 'none',
                        'background': 'rgba(255, 255, 255, 0.2)',
                        'color': '#ffffff',
                        'cursor': 'pointer',
                        'font-weight': 'bold',
                        'flex': 1
                    }
                ),
            ], style={'display': 'flex', 'gap': '0.5rem', 'margin-bottom': '1rem'}),
            html.Hr(style={'border-color': 'rgba(255, 255, 255, 0.2)'}),
            html.Div([
                html.Strong("⚙️ Configuration", style={'color': '#ffffff'}),
                html.P(f"Mode: {app_config.get('mode', 'paper').upper()}", style={'color': 'rgba(255, 255, 255, 0.7)'}),
                html.P("Risk Level: Medium", style={'color': 'rgba(255, 255, 255, 0.7)'}),
                html.P("Max Position: $50k", style={'color': 'rgba(255, 255, 255, 0.7)'}),
                html.P("Stop Loss: 2%", style={'color': 'rgba(255, 255, 255, 0.7)'}),
            ])
        ])
