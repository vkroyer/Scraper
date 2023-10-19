import logging
from logging.handlers import TimedRotatingFileHandler

CustomLogger = logging.getLogger(__name__)

CustomLogger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

# Create a timed rotating file handler
file_handler = TimedRotatingFileHandler(filename='data/app.log', when='W0', backupCount=15)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

CustomLogger.addHandler(file_handler)
CustomLogger.addHandler(stream_handler)