"""
This module manages background orchestrations on a parallel execution thread.
Tasks include:
- Validating the API token periodically.
- Freezing trading actions during maintenance hours (3:00 to 5:00 AM Tehran time).
- Liquidating small "dust" balances (crypto values between 0 and 1 USDT) back to USDT.
- Refreshing the active tradable assets list and spawning new TradeBot threads for new pairs.
"""

from date_time_func import date_time_func
from get_wallet_balance_func import *
from buy_sell_func import *
from get_tradable_crypto_pairs_and_detail_func import *
from get_crypto_price_func import *
from variables_func import *
from tradebot import tradebot
from except_exit_func import *
from validation_token_checker_func import *

from threading import Thread
from time import sleep
import json

tradable_crypto_data_file = "tradable_crypto_pairs_and_monetary_units.txt"


def parallel_thread_funcs():
    """
    Parallel runtime loop executing maintenance routines.
    Monitors authorization tokens, executes dust liquidation, refreshes 
    cached assets, and dynamically spins up new market trackers.
    """
    try:
        global_vars = variables_func()
        crypto_list_exceptions = global_vars["crypto_list_exceptions"]
        ex_fee = global_vars["ex_fee"]

        global my_usdt_balance
        my_usdt_balance = global_vars["my_usdt_balance"]
        
        global trading_pair
        trading_pair = "Buy"

        try:
            while True:
                # Step 1: Ensure API Token is active and valid
                if not validation_token_checker_func():
                    print("Enter New 'token' In 'variables_func.py' file. ")
                    except_exit_func()

                now_time = int(date_time_func("hour", "Asia/Tehran"))

                # Step 2: Trigger daily maintenance during 3:00 AM or 4:00 AM Tehran Time
                if (now_time == 3 or now_time == 4) and trading_pair == "Buy":
                    
                    trading_pair = "Stop"

                    # Fetch entire wallet balance
                    cryptos_wallet_balance = get_wallet_balance_func("all")

                    # Scan wallet for non-excepted micro-assets (dust) to liquidate
                    for crypto_in_wallet in cryptos_wallet_balance:
                        crypto_name = crypto_in_wallet
                        crypto_amount = float(cryptos_wallet_balance[crypto_name])

                        if crypto_name.lower() not in crypto_list_exceptions:
                            crypto_name_with_usdt = crypto_name + "USDT"
                            crypto_price = get_crypto_price_func(crypto_name_with_usdt, "target")
                            crypto_value = crypto_amount * crypto_price

                            # Identify if asset fits dust criteria: value is > 0 but < 1 USDT
                            if 0.0 < crypto_value < 1.0:
                                crypto_float_sizes_for_trade = get_tradable_crypto_pairs_and_detail_func(crypto_name_with_usdt)
                                crypto_float_size_for_trade = crypto_float_sizes_for_trade[1]
                                usdt_float_size_for_trade = crypto_float_sizes_for_trade[2]

                                # Submit emergency market sell order
                                order_values = send_buy_sell_req_func(
                                    "sell", 
                                    "market", 
                                    crypto_name_with_usdt, 
                                    crypto_float_size_for_trade, 
                                    usdt_float_size_for_trade, 
                                    crypto_amount, 
                                    0
                                )

                                try:
                                    if order_values and order_values != "":
                                        done_orders_value = order_values[0][1]

                                        # Add executed value minus fee back to local USDT balance tracking
                                        if done_orders_value > 0.0:
                                            executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                            my_usdt_balance += float_truncator_func(executed_net_value, 8)
                                except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
                                    pass

                    # Step 3: Refresh active tradable list to discover newly listed pairs
                    old_crypto_list = get_tradable_crypto_pairs_and_detail_func("list")
                    get_tradable_crypto_pairs_and_detail_func("refresh")

                    new_crypto_list = get_tradable_crypto_pairs_and_detail_func("list")
                    loop_index_max = len(new_crypto_list)

                    # Spawn individual tracker threads for newly listed pairs
                    for loop_index in range(loop_index_max):
                        try: 
                            if old_crypto_list[loop_index]:
                                pass
                        except IndexError:
                            # Spawn tracking thread for newly discovered trading pair
                            trade_bot_thread = Thread(target=tradebot, args=(new_crypto_list[loop_index],))
                            trade_bot_thread.start()

                    # Release maintenance freeze and sleep for roughly 2 hours
                    trading_pair = "Buy"
                    sleep(7300)

                # Periodic routine check interval (every 30 seconds)
                sleep(30)
                
        except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
            pass
            
    except KeyboardInterrupt:
        except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# print(parallel_thread_funcs())