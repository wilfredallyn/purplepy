import logging

# Configure logging
logging.basicConfig(
    filename="logfile.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
)

# Example logger
logger = logging.getLogger(__name__)
