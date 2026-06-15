"""
Main entry point of the cryptocurrency trading bot.
Responsible for initializing and launching independent trading threads for each 
active tradable pair and running the parallel maintenance orchestrator.
"""

from tradebot import *
from parallel_thread_funcs import *
from except_exit_func import *
from get_tradable_crypto_pairs_and_detail_func import *

from time import sleep
from threading import Thread


def main():
    """
    Retrieves the active list of tradable crypto pairs, spawns individual execution
    threads for each tradebot instance, starts the background manager thread,
    and runs the main keep-alive process loop.
    """
    crypto_pairs = get_tradable_crypto_pairs_and_detail_func("list")

    try:
        # Step 1: Launch independent trading threads for each active currency pair
        for crypto_pair in crypto_pairs:
            trade_bot_thread = Thread(target=tradebot, args=(str(crypto_pair),))
            trade_bot_thread.start()

        # Step 2: Spawn the parallel orchestrator for tokens, dust liquidation, and list updates
        parallel_thread = Thread(target=parallel_thread_funcs)
        parallel_thread.start()

    except Exception:
        print("\nAn Error Happened!")
        except_exit_func()

    # Step 3: Keep-alive loop to prevent the parent process from terminating
    try:
        while True:
            sleep(0.3)
    except KeyboardInterrupt:
        except_exit_func()


if __name__ == '__main__':
    main()