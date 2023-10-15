import logging
import os
import pathlib
import time
from logging.handlers import RotatingFileHandler

from config import get_config


def setup_logger():
    log_path = get_config().get('log', 'path', fallback=".log")
    log_name = get_config().get('log', 'name', fallback='') or time.strftime("%Y-%m-%d")
    log_size = get_config().getByteSize('log', 'max_size', fallback="1MB")
    log_backups = get_config().getint('log', 'backups', fallback=3)
    log_path = pathlib.Path(log_path).joinpath(log_name+".log")

    if not os.path.exists(log_path.parent):
        os.makedirs(log_path.parent, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_path, encoding='utf-8', maxBytes=log_size, backupCount=log_backups)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.name = 'DCSpamRemover'
    logger.setLevel(get_config().getUpper('log', 'level', fallback="INFO"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
