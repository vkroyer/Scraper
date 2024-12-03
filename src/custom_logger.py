import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Make sure there is a log file path
data_path = Path(__file__).parent.parent / "data"
data_path.mkdir(exist_ok=True)
log_file = data_path / "main.log"

CustomLogger = logging.getLogger(__name__)
CustomLogger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s')

# Create a timed rotating file handler
file_handler = TimedRotatingFileHandler(filename=str(log_file), when='midnight', interval=30, backupCount=4)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

CustomLogger.addHandler(file_handler)
CustomLogger.addHandler(stream_handler)