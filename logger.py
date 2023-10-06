import logging
import os
import pathlib
import time
from logging.handlers import RotatingFileHandler

from config import get_config


def setup_logger():
    log_path = get_config().get('log', 'path')
    log_name = (get_config().get('log', 'name') or time.strftime("%Y-%m-%d")) + ".log"
    log_size = get_config().getByteSize('log', 'max_size')
    log_backups = get_config().getint('log', 'backups')
    log_path = pathlib.Path.joinpath(pathlib.Path(log_path), log_name)

    os.makedirs(log_path.parent, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_path, encoding='utf-8', maxBytes=log_size, backupCount=log_backups)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.name = 'DCSpamRemover'
    logger.setLevel(logging.getLevelName(get_config().getUpper('log', 'level')))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
