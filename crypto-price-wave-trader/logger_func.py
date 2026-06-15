"""
This module provides rotational file logging functionality. 
It maintains a set of rolling log files for each cryptocurrency pair, 
ensuring log directory creation and file size constraints are strictly managed.
"""

from os import path, makedirs
from variables_func import *
from except_exit_func import *


def logger_func(log_file_counter, crypto_pair, log_text):
    """
    Appends log_text to the active log file for the specified crypto_pair.
    If the file exceeds max_log_file_size, it rotates the log counter, 
    clears (truncates) the next file in rotation, and loops back to append the text.
    """
    global_vars = variables_func()
    max_log_file = global_vars["max_log_file"]            # E.g., Max 3 rolling files
    max_log_file_size = global_vars["max_log_file_size"]  # File size threshold in bytes

    exit_loop = False

    while not exit_loop:
        # Step 1: Ensure log directory exists
        if not path.exists('./log_files'):
            try:
                makedirs("./log_files")
            except Exception:
                print("An Error While Trying to Create 'log_files' Directory. ")
                except_exit_func()

        log_file_path = f"./log_files/{crypto_pair.lower()}_{log_file_counter}.txt"

        # Step 2: Ensure the current target log file exists
        if not path.isfile(log_file_path):
            try:
                file = open(log_file_path, "w")
                file.close()
            except Exception:
                print(f"An Error While Trying to Create '{crypto_pair}' log file. ")
                except_exit_func()

        # Step 3: Handle file writing and size verification
        if path.isfile(log_file_path):
            file = open(log_file_path, "a+")
            file_size = path.getsize(log_file_path)

            # If file size is within limits, append the content and exit
            if file_size < max_log_file_size:
                file.write(log_text)
                file.flush()
                file.close()
                return log_file_counter

            # If file size exceeds the limit, close and rotate the counter
            if file_size >= max_log_file_size:
                file.close()

                if log_file_counter <= max_log_file:
                    log_file_counter += 1

                if log_file_counter > max_log_file:
                    log_file_counter = 1

                log_file_path = f"./log_files/{crypto_pair.lower()}_{log_file_counter}.txt"

                # Truncate the next rolling log file to prepare for writing
                try:
                    file = open(log_file_path, "w")
                    file.close()
                except Exception:
                    print(f"An Error While Trying to Create '{crypto_pair}' log file. ")
                    except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# logger_func(1, "btcusdt", "For Target Over Price.")