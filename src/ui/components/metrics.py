"""
Metrics Component - Componentă pentru afișarea metricilor de performanță
"""

import streamlit as st
from typing import Dict


def render_metrics(metrics: Dict[str, float]) -> None:
    """
    Randează metricile esențiale de performanță.
    
    Args:
        metrics: Dict cu metrici {
            'total_pnl': float,
            'win_rate': float,
            'max_drawdown': float,
            'active_positions': int
        }
    """
    st.subheader("💰 Metrici Esențiale")
    
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        pnl_color = "normal" if metrics.get('total_pnl', 0) >= 0 else "inverse"
        st.metric(
            "💵 Total P&L",
            f"${metrics.get('total_pnl', 0):,.2f}",
            delta=f"{metrics.get('total_pnl', 0):+,.2f}" if metrics.get('total_pnl', 0) != 0 else None,
            delta_color=pnl_color
        )
    
    with col_metric2:
        st.metric(
            "🎯 Win Rate",
            f"{metrics.get('win_rate', 0):.1f}%",
            delta=f"{metrics.get('win_rate', 0):.1f}%" if metrics.get('win_rate', 0) > 0 else None
        )
    
    with col_metric3:
        max_dd = metrics.get('max_drawdown', 0)
        dd_color = "inverse" if max_dd > 5 else "normal"
        st.metric(
            "📉 Max Drawdown",
            f"{max_dd:.2f}%",
            delta=f"-{max_dd:.2f}%" if max_dd > 0 else None,
            delta_color=dd_color
        )
    
    with col_metric4:
        active_pos = metrics.get('active_positions', 0)
        st.metric(
            "📊 Poziții Active",
            f"{active_pos}",
            delta=f"{active_pos}" if active_pos > 0 else None
        )
