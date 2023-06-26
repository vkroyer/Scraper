import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a timed rotating file handler
handler = TimedRotatingFileHandler(filename='app.log', when='midnight', backupCount=7)
logger.addHandler(handler)