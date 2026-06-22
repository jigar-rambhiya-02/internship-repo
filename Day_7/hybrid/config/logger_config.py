import logging
import os

def setup_logger(name: str = "hybrid_rag") -> logging.Logger:
    """
    Configures a unified logging system that outputs simultaneously to the console 
    and to an append-only 'output.log' file in the project workspace root directory.
    Format: TIMESTAMP | LEVEL | MESSAGE
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if logger is re-initialized across modules
    if not logger.handlers:
        log_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Stream Handler for stdout
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)
        
        # File Handler for local persistence
        log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output.log"))
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
    return logger

