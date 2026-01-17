"""
CSS Loader - Încarcă CSS-ul din fișier separat
"""

import streamlit as st
from pathlib import Path


def load_css() -> None:
    """Încarcă CSS-ul din fișierul static."""
    css_path = Path(__file__).parent.parent / "static" / "css" / "dashboard.css"
    
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        # Fallback CSS dacă fișierul nu există
        st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                color: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True)
