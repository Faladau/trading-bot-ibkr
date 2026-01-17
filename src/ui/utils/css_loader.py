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
        # Adaugă CSS inline pentru layout 80% care trebuie să fie aplicat ÎNAINTE de Streamlit
        layout_css = """
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
        """
        st.markdown(f"<style>{layout_css}{css_content}</style>", unsafe_allow_html=True)
    else:
        # Fallback CSS dacă fișierul nu există
        st.markdown("""
        <style>
            .stApp {
                background: #1a1a2e !important;
                color: #ffffff !important;
            }
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
        </style>
        """, unsafe_allow_html=True)
