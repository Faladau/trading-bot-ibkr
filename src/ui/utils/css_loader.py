"""
CSS Loader - Best Practice: Separă logica CSS din Python

Citește fișierele CSS și le injectează în Streamlit.
Portabil: funcționează pe orice server, fără dependență de Streamlit.
"""

import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_css_file(filename: str) -> str:
    """
    Citește un fișier CSS din src/ui/static/css/
    
    Args:
        filename: Numele fișierului (ex: 'layout.css')
    
    Returns:
        Conținutul fișierului CSS sau string gol dacă nu găsește
    """
    css_path = Path(__file__).parent.parent / "static" / "css" / filename
    
    try:
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Eroare citire {filename}: {e}")
    
    return ""


def load_all_css() -> None:
    """
    Încarcă TOATE fișierele CSS și injectează în Streamlit.
    Ordine importantă: layout -> colors -> components
    """
    
    # 1. Layout (TREBUIE PRIMA, cu JS)
    layout_css = load_css_file("layout.css")
    layout_js = """
    <script>
    // LocalStorage pentru persistență la refresh
    const LAYOUT_KEY = 'streamlit_layout_forced';

    function forceLayout90() {
        // Selectori noi (Streamlit 1.40+)
        const main = document.querySelector('section[data-testid="stAppViewContainer"]');
        if (main) {
            main.style.setProperty('max-width', '90%', 'important');
            main.style.setProperty('width', '90%', 'important');
            main.style.setProperty('margin-left', 'auto', 'important');
            main.style.setProperty('margin-right', 'auto', 'important');
        }
        
        // Backup selectori (versiuni mai vechi)
        const blockContainer = document.querySelector('.main .block-container');
        if (blockContainer) {
            blockContainer.style.setProperty('max-width', '90%', 'important');
            blockContainer.style.setProperty('width', '90%', 'important');
            blockContainer.style.setProperty('margin-left', 'auto', 'important');
            blockContainer.style.setProperty('margin-right', 'auto', 'important');
        }
        
        localStorage.setItem(LAYOUT_KEY, 'true');
    }

    function initLayoutPersistence() {
        forceLayout90();
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', forceLayout90);
        }
        
        window.addEventListener('load', forceLayout90);
        
        // MutationObserver - detectează schimbări DOM
        let observer = new MutationObserver(function(mutations) {
            forceLayout90();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class', 'data-testid']
        });
        
        // Interval backup
        setInterval(forceLayout90, 300);
    }

    initLayoutPersistence();
    window.addEventListener('resize', forceLayout90);
    </script>
    """
    
    if layout_css:
        st.markdown(f"<style>{layout_css}</style>{layout_js}", unsafe_allow_html=True)
    
    # 2. Colors
    colors_css = load_css_file("colors.css")
    if colors_css:
        st.markdown(f"<style>{colors_css}</style>", unsafe_allow_html=True)
    
    # 3. Components (optional - dacă ai componente custom)
    components_css = load_css_file("components.css")
    if components_css:
        st.markdown(f"<style>{components_css}</style>", unsafe_allow_html=True)
