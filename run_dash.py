"""
Entry point pentru Dash Dashboard
Rulează: python run_dash.py
"""

from src.ui.dash_app import app, server
from src.common.logging_utils.structured_logger import configure_structlog

# Configure structured logging at startup
configure_structlog(use_json=False)  # Pretty console output for development

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
