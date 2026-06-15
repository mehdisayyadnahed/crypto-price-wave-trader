"""
This module provides functionality to calculate the USDT equivalent value 
of a specific cryptocurrency currently held in the user's wallet.
"""

from get_wallet_balance_func import *
from get_crypto_price_func import *
from except_exit_func import *


def calculate_crypto_usdt_balance_func(crypto_name):
    """
    Retrieves the wallet balance of a specified cryptocurrency and calculates
    its current value in USDT based on the target exchange's current trade rate.
    """
    try:
        # Fetch the current available amount of the asset in the wallet
        wallet_balance = get_wallet_balance_func(crypto_name)
        
        # Fetch the current price of the asset against USDT from the target exchange
        crypto_price = get_crypto_price_func(crypto_name + "USDT", "target")
        
        # Calculate and return the total value of the asset in USDT equivalent
        return float(wallet_balance) * float(crypto_price)
        
    except KeyboardInterrupt:
        # Clean exit or silence on user interrupt
        pass
        # except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# while True:
#     print(calculate_crypto_usdt_balance_func("BTC"))