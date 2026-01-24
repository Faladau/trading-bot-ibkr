"""
Entry point pentru Dash Dashboard
Rulează: python run_dash.py
"""

import os
import logging
import warnings

# Suppress non-critical warnings BEFORE any imports
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*ui.hideSidebarNav.*')

# Suppress library loggers (Flask, werkzeug, etc.)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)
logging.getLogger('dash').setLevel(logging.WARNING)
logging.getLogger('streamlit').setLevel(logging.ERROR)

# Configure logging BEFORE any imports from src
from src.common.logging_utils.structured_logger import configure_logging
configure_logging(log_level="INFO")

# NOW import app and callbacks
from src.ui.dash_app import app, server

if __name__ == '__main__':
    # Disable Flask's default logger
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
