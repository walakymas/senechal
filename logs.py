import logging
import os


def setup_logging():
    """Log to the console; LOG_LEVEL (default INFO) sets the level, DEBUG shows the detail (also command arguments)."""
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper(),
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
