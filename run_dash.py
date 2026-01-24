"""
Entry point pentru Dash Dashboard
Rulează: python run_dash.py
"""

# Configure logging BEFORE any imports from src
from src.common.logging_utils.structured_logger import configure_logging
configure_logging(log_level="INFO")

# NOW import app and callbacks
from src.ui.dash_app import app, server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
