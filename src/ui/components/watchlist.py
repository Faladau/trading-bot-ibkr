"""
Watchlist Component - Componentă pentru afișarea watchlist-ului
"""

import streamlit as st
import pandas as pd
from typing import List


def render_watchlist(symbols: List[str], market_data: pd.DataFrame) -> None:
    """
    Randează watchlist-ul cu date de piață.
    
    Args:
        symbols: Lista de simboluri
        market_data: DataFrame cu date de piață (symbol, price, change_pct, etc.)
    """
    st.subheader("📊 Watchlist")
    
    if not market_data.empty:
        for _, row in market_data.iterrows():
            change_color = "normal" if row.get('change_pct', 0) >= 0 else "inverse"
            st.metric(
                label=row.get('symbol', 'N/A'),
                value=f"${row.get('price', 0):.2f}",
                delta=f"{row.get('change_pct', 0):+.2f}%",
                delta_color=change_color
            )
    else:
        st.info("ℹ️ Nu sunt date disponibile. Rulează Agent 1 pentru a colecta date.")
