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
        with open(f"{DEFAULT_DATA_DIR}{filename}", "w") as file:
            file.write(content)
        logging.info(f"File written: {filename}")
    except Exception as e:
        logging.error(f"Error writing file {filename}: {e}")



def setup_logging():
    """Configures logging to stdout or a file."""
    print(f"Setting logging")
    if not LOGDIR:
        logFile = f"/tmp/manage_agenda.log"
    else:
        logFile = f"{LOGDIR}/manage_agenda.log"

    logging.basicConfig(
        filename = logFile,
        # stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
    )



