'''System Configuration
'''
import logging
import logging.handlers
import os
import time
from pathlib import Path
from typing import Dict, List

def get_log_path() -> Path:
    """Get log path

    Returns:
        Path: Path to log directory
    """
    log_path = Path('volumes/logs')
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def get_data_path() -> Path:
    """Get data path

    Returns:
        Path: Path to data directory
    """
    data_path = Path('volumes/data')
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path


def get_config_path() -> Path:
    """Get config path

    Returns:
        Path: Path to config directory
    """
    config_path = Path('volumes/config')
    config_path.mkdir(parents=True, exist_ok=True)
    return config_path


def get_cache_path() -> Path:
    """Get cache path

    Returns:
        Path: Path to cache directory
    """
    cache_path = Path('volumes/cache')
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path



def configure_logging():
    """Configures logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # log_dest = get_log_path().joinpath('service.log')
    # print(f'Logging to "{log_dest.as_posix()}"')

    # log_file_handler = logging.handlers.TimedRotatingFileHandler(
    #     filename=log_dest,
    #     when='midnight',
    #     backupCount=5
    # )
    # log_file_handler.setLevel(logging.DEBUG)

    # msg_fmt = '%(asctime)s.%(msecs)03dZ - %(name)s - %(levelname)s - %(message)s'
    # root_formatter = logging.Formatter(msg_fmt, datefmt='%Y-%m-%dT%H:%M:%S')
    # log_file_handler.setFormatter(root_formatter)
    # root_logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # error_formatter = logging.Formatter(msg_fmt, datefmt='%Y-%m-%dT%H:%M:%S')
    # console_handler.setFormatter(error_formatter)
    root_logger.addHandler(console_handler)
    # logging.Formatter.converter = time.gmtime
