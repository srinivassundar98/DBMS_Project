from libraries import *
def setup_logging(username):
    # Create a user-specific log directory if it doesn't exist
    log_directory = "user_logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Configure logging for the specific user
    logging.basicConfig(level=logging.INFO,
                        filename=f'{log_directory}/{username}.log',  # User-specific log file
                        filemode='a',  # Append mode
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
