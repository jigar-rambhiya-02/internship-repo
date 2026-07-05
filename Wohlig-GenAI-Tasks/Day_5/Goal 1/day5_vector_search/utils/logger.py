# this is a logger for the project

import logging
import os
import sys

_LOGGER_NAME = "vvs_logger"
_LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output.log")
_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_logger_instance = None



def get_logger() -> logging.Logger:
    global _logger_instance

    if _logger_instane is not None:
        return _logger_instance
    
    logger = logging.getLogger(_LOGGER_NAME)
    
    log_level_en = os.environ.get('LOG_LEVEL', 'INFO').strip().upper()
    log_level = logging.DEBUG if log_level_env == 'DEBUG' else logging.INFO
    logger.setLevel(log_level)
    
    if logger.handlers:
        _logger_instance = logger
        return _logger_instance
    
    formatter = logging.Formatter(fmt = _LOG_FORMAT, datefmt = _DATE_FORMAT)
    
    stream_handler = logging.StreamHandler(stream = sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    file_handler = logging.FileHandler(_LOG_FILE_PATH, mode = 'a', encoding = 'utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.propagate = False
    
    _logger_instance = logger
    return _logger_instance
    
    
