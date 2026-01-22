import logging
import os

def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        env = os.getenv('ENVIRONMENT', 'development')
        log_level = os.getenv('LOG_LEVEL', 'DEBUG' if env == 'development' else 'INFO')
        logger.setLevel(getattr(logging, log_level))

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger