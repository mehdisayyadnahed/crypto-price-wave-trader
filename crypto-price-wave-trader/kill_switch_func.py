"""
This module provides an emergency "kill switch" functionality to immediately 
liquidate any active cryptocurrency asset in the wallet into USDT and force-exit 
the application.
"""

from get_wallet_balance_func import *
from buy_sell_func import *
from get_tradable_crypto_pairs_and_detail_func import *
from get_crypto_price_func import *
from variables_func import *
from except_exit_func import *

import json


def kill_switch_func():
    """
    Emergency function to scan wallet balances, filter out exceptions, execute a 
    market-sell order on the first identified active asset to liquidate it, and 
    immediately force-terminate the application.
    """
    variables_func_list = variables_func()
    crypto_list_exceptions = variables_func_list["crypto_list_exceptions"]

    try:
        cryptos_wallet_balance = get_wallet_balance_func("all")

        for crypto_in_wallet in cryptos_wallet_balance:
            crypto_name = crypto_in_wallet
            crypto_amount = float(cryptos_wallet_balance[crypto_name])

            # Process only active assets that are not blacklisted/excepted
            if crypto_name.lower() not in crypto_list_exceptions:
                crypto_name_with_usdt = crypto_name + "USDT"

                # Retrieve current trade price from Nobitex
                crypto_price = get_crypto_price_func(crypto_name_with_usdt, "target")
                crypto_value = crypto_amount * crypto_price

                # Fetch decimals and price precision requirements for the trade
                crypto_float_sizes_for_trade = get_tradable_crypto_pairs_and_detail_func(crypto_name_with_usdt)
                crypto_float_size_for_trade = crypto_float_sizes_for_trade[1]
                usdt_float_size_for_trade = crypto_float_sizes_for_trade[2]

                # Dispatch market-sell order to liquidate the asset
                send_buy_sell_req_func(
                    "sell", 
                    "market", 
                    crypto_name_with_usdt, 
                    crypto_float_size_for_trade, 
                    usdt_float_size_for_trade, 
                    crypto_amount, 
                    0
                )
                
                # Terminate execution immediately after initiating liquidation
                except_exit_func()
                
    except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
        except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# print(kill_switch_func())