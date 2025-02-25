import sys
import logging

# basic configuration
def logging_config(debug : bool) -> None:
  """
  Set up the logger if the debug mode is enabled.
  Write the log onto the console and in a file.

  Argument:
    debug: a boolean used to set the logging level
  """

  if debug :
    level = logging.DEBUG
    logging.basicConfig(level = level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.StreamHandler(),  # Log to the console
                            logging.FileHandler("othello.log")  # Log to a file
                        ])

def log_error_message(error : str, context = None : str | None) -> None:
  """
  Log an error message with a given context.

  Arguments:
    error: a string of the error message to be logged
    context: a string describing the context of the error, can be None if no context is given
  """
  logger = logging.getLogger("Othello")
  if context is not None:
    logger.error(f"Context: {context}")
  logging.error(f"Error: {error}", exc_info=True)
