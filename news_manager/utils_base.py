import click
import logging
import os
import sys

LOGDIR = ""

# --- File I/O ---
def write_file(filename, content):
    """Writes content to a file.

    Args:
        filename (str): The name of the file.
        content (str): The content to write.
    """
    try:
        with open(filename, "w") as file:
            file.write(content)
        logging.info(f"File written: {filename}")
    except Exception as e:
        logging.error(f"Error writing file {filename}: {e}")



def setup_logging(log_dir=None):
    """Configures logging to stdout or a file."""
    if not log_dir:
        logFile = f"/tmp/manage_agenda.log"
    else:
        logFile = f"{log_dir}/manage_agenda.log"

    logger = logging.getLogger('news_manager')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(logFile)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger



