"""
Dash Components - Componente pentru Dash/Plotly
Versiuni Dash ale componentelor existente
"""

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from datetime import datetime


def render_agent_status_row(agent_statuses: Dict[str, str]) -> html.Div:
    """
    Randează rândul cu status-urile tuturor agenților (Dash version).
    
    Args:
        agent_statuses: Dict cu status-uri {'agent1': 'ACTIVE', 'agent2': 'IDLE', ...}
    
    Returns:
        html.Div cu status-urile agenților
    """
    def get_status_style(status: str) -> dict:
        """Returnează stilul pentru status."""
        status_lower = status.lower()
        if status_lower == 'active':
            return {
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'color': '#ffffff',
                'padding': '1rem',
                'border-radius': '10px',
                'text-align': 'center',
                'font-weight': 'bold',
                'box-shadow': '0 4px 15px rgba(102, 126, 234, 0.4)'
            }
        elif status_lower == 'idle':
            return {
                'background': 'rgba(255, 193, 7, 0.2)',
                'color': '#ffc107',
                'padding': '1rem',
                'border-radius': '10px',
                'text-align': 'center',
                'font-weight': 'bold',
                'border': '1px solid rgba(255, 193, 7, 0.3)'
            }
        elif status_lower == 'monitoring':
            return {
                'background': 'rgba(23, 162, 184, 0.2)',
                'color': '#17a2b8',
                'padding': '1rem',
                'border-radius': '10px',
                'text-align': 'center',
                'font-weight': 'bold',
                'border': '1px solid rgba(23, 162, 184, 0.3)'
            }
        else:  # error
            return {
                'background': 'rgba(220, 53, 69, 0.2)',
                'color': '#dc3545',
                'padding': '1rem',
                'border-radius': '10px',
                'text-align': 'center',
                'font-weight': 'bold',
                'border': '1px solid rgba(220, 53, 69, 0.3)'
            }
    
    return html.Div([
        html.Div([
            html.Div([
                html.Strong("Agent 1"),
                html.Br(),
                html.Strong(agent_statuses.get('agent1', 'IDLE'))
            ], style=get_status_style(agent_statuses.get('agent1', 'IDLE'))),
            html.P("Data Collection", style={'color': 'rgba(255, 255, 255, 0.7)', 'text-align': 'center', 'margin-top': '0.5rem'})
        ], style={'flex': 1}),
        html.Div([
            html.Div([
                html.Strong("Agent 2"),
                html.Br(),
                html.Strong(agent_statuses.get('agent2', 'IDLE'))
            ], style=get_status_style(agent_statuses.get('agent2', 'IDLE'))),
            html.P("Decision", style={'color': 'rgba(255, 255, 255, 0.7)', 'text-align': 'center', 'margin-top': '0.5rem'})
        ], style={'flex': 1}),
        html.Div([
            html.Div([
                html.Strong("Agent 3"),
                html.Br(),
                html.Strong(agent_statuses.get('agent3', 'IDLE'))
            ], style=get_status_style(agent_statuses.get('agent3', 'IDLE'))),
            html.P("Execution", style={'color': 'rgba(255, 255, 255, 0.7)', 'text-align': 'center', 'margin-top': '0.5rem'})
        ], style={'flex': 1}),
    ], style={'display': 'flex', 'gap': '1rem', 'margin-bottom': '1rem'})


def render_metrics_dash(metrics: Dict[str, float]) -> html.Div:
    """
    Randează metricile esențiale (Dash version).
    
    Args:
        metrics: Dict cu metrici
    
    Returns:
        html.Div cu metricile
    """
    def format_metric(label: str, value: str, delta: str = None, delta_color: str = 'normal') -> html.Div:
        """Creează un metric card."""
        delta_style = {
            'color': '#4caf50' if delta_color == 'normal' else '#f44336',
            'font-size': '0.9rem',
            'margin-top': '0.25rem'
        } if delta else {}
        
        return html.Div([
            html.Div(label, style={'color': 'rgba(255, 255, 255, 0.8)', 'font-size': '0.9rem'}),
            html.Div(value, style={'color': '#ffffff', 'font-size': '2rem', 'font-weight': 'bold'}),
            html.Div(delta, style=delta_style) if delta else None
        ], style={
            'background': 'rgba(255, 255, 255, 0.1)',
            'backdrop-filter': 'blur(10px)',
            'border-radius': '15px',
            'padding': '1.5rem',
            'border': '1px solid rgba(255, 255, 255, 0.2)',
            'box-shadow': '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
        })
    
    total_pnl = metrics.get('total_pnl', 0)
    win_rate = metrics.get('win_rate', 0)
    max_dd = metrics.get('max_drawdown', 0)
    active_pos = metrics.get('active_positions', 0)
    
    pnl_delta = f"{total_pnl:+,.2f}" if total_pnl != 0 else None
    pnl_color = 'normal' if total_pnl >= 0 else 'inverse'
    dd_delta = f"-{max_dd:.2f}%" if max_dd > 0 else None
    dd_color = 'inverse' if max_dd > 5 else 'normal'
    
    return html.Div([
        html.H3("💰 Metrici Esențiale", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
        html.Div([
            format_metric("💵 Total P&L", f"${total_pnl:,.2f}", pnl_delta, pnl_color),
            format_metric("🎯 Win Rate", f"{win_rate:.1f}%", f"{win_rate:.1f}%" if win_rate > 0 else None),
            format_metric("📉 Max Drawdown", f"{max_dd:.2f}%", dd_delta, dd_color),
            format_metric("📊 Poziții Active", f"{active_pos}", f"{active_pos}" if active_pos > 0 else None),
        ], style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'gap': '1rem'})
    ])


def render_watchlist_dash(symbols: List[str], market_data: pd.DataFrame) -> html.Div:
    """
    Randează watchlist-ul (Dash version).
    
    Args:
        symbols: Lista de simboluri
        market_data: DataFrame cu date de piață
    
    Returns:
        html.Div cu watchlist-ul
    """
    if market_data.empty:
        return html.Div([
            html.H3("📊 Watchlist", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
            html.Div(
                "ℹ️ Nu sunt date disponibile. Rulează Agent 1 pentru a colecta date.",
                style={
                    'background': 'rgba(23, 162, 184, 0.2)',
                    'color': '#17a2b8',
                    'padding': '1rem',
                    'border-radius': '10px',
                    'border': '1px solid rgba(23, 162, 184, 0.3)'
                }
            )
        ])
    
    items = []
    for _, row in market_data.iterrows():
        change_pct = row.get('change_pct', 0)
        change_color = '#4caf50' if change_pct >= 0 else '#f44336'
        
        items.append(html.Div([
            html.Strong(row.get('symbol', 'N/A'), style={'color': '#ffffff', 'font-size': '1.2rem'}),
            html.Div(f"${row.get('price', 0):.2f}", style={'color': '#ffffff', 'font-size': '1.5rem', 'font-weight': 'bold'}),
            html.Div(
                f"{change_pct:+.2f}%",
                style={'color': change_color, 'font-size': '1rem', 'margin-top': '0.25rem'}
            )
        ], style={
            'background': 'rgba(255, 255, 255, 0.1)',
            'backdrop-filter': 'blur(10px)',
            'border-radius': '10px',
            'padding': '1rem',
            'border': '1px solid rgba(255, 255, 255, 0.2)',
            'margin-bottom': '0.5rem'
        }))
    
    return html.Div([
        html.H3("📊 Watchlist", style={'color': '#ffffff', 'margin-bottom': '1rem'}),
        html.Div(items)
    ])


def render_equity_curve_chart(trades: List[dict]) -> dcc.Graph:
    """
    Randează equity curve chart (Dash version).
    
    Args:
        trades: Lista de trade-uri
    
    Returns:
        dcc.Graph cu equity curve
    """
    if not trades:
        return dcc.Graph(figure=go.Figure().add_annotation(
            text="Nu există date pentru equity curve",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        ))
    
    closed_trades = [t for t in trades if t.get('status') == 'closed']
    if not closed_trades:
        return dcc.Graph(figure=go.Figure().add_annotation(
            text="Nu există trade-uri închise pentru equity curve",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        ))
    
    cumulative_pnl = []
    running_sum = 0
    dates = []
    
    for trade in sorted(closed_trades, key=lambda x: x.get('close_time', '2000-01-01')):
        running_sum += trade.get('pnl', 0)
        cumulative_pnl.append(running_sum)
        dates.append(trade.get('close_time', datetime.now().isoformat()))
    
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
    
    return dcc.Graph(figure=fig, style={'width': '100%', 'height': '300px'})
