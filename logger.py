import logging
import os
from datetime import datetime

class Logger:
    _instance = None
    _logger = None
    
    def __new__(cls, to_file: bool = True):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger(to_file)
        return cls._instance
    
    def _initialize_logger(self, to_file: bool = True):
        if self._logger is None:
            if to_file:
                os.makedirs("logs", exist_ok=True)
            
            # Clear any existing handlers to avoid duplicates
            logging.getLogger().handlers.clear()
            
            self._logger = logging.getLogger("LawScrapper")
            self._logger.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
            # Create handler
            if to_file:
                handler = logging.FileHandler(
                    f"logs/{datetime.now().strftime('%Y%m%d%H%M%S')}.log", 
                    encoding="utf-8"
                )
            else:
                handler = logging.StreamHandler()
            
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            
            self._logger.info(f"Logger initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def get_logger(self):
        return self._logger