import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a timed rotating file handler
handler = TimedRotatingFileHandler(filename='app.log', when='W0', backupCount=15)
logger.addHandler(handler)