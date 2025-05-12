import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(app):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Setup file handler
    log_file = f"logs/stockmaster_{datetime.now().strftime('%Y%m')}.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    
    # Setup formatters
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(file_formatter)
    
    # Set log level
    file_handler.setLevel(logging.INFO)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    
    # Set app logger level
    app.logger.setLevel(logging.INFO)
    
    # Initial log message
    app.logger.info('StockMaster startup')
