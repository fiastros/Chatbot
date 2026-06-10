"""
Prevents my 30GB SSD from filling up with massive log files.
"""

import logging
from logging.handlers import RotatingFileHandler
from config import settings
import os

def get_logger(name: str):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Max 5MB per file, keep 3 backups max
    handler = RotatingFileHandler('logs/ingestion.log', maxBytes=5*1024*1024, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger