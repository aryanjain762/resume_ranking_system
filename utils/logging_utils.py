import logging
from config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT

def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )