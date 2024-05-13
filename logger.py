import logging
from datetime import datetime
import os

log_directory = 'C:/ChatbotLogs'

# Check if the directory exists, and if not, create it
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Setup logger with the full path to the log file
log_path = os.path.join(log_directory, 'chatbot_activity.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def log_message(message_type, message):
    """Logs a message with a timestamp."""
    logging.info(f"{message_type}: {message}")