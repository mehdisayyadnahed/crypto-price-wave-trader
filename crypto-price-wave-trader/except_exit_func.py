"""
This module handles the safe and forced termination of the running application,
ensuring clean process shutdown with an fallback mechanism.
"""

import sys
import os


def except_exit_func():
    """
    Prints a termination message and shuts down the application process.
    First attempts a standard sys.exit(0). If intercepted or failing, falls
    back to os._exit(0) to force-terminate the application.
    """
    print("\n\nForce Stop.\nExit.\n\n")
    try:
        sys.exit(0)
    except SystemExit:
        # Fallback to absolute low-level OS exit if standard exit is blocked
        os._exit(0)