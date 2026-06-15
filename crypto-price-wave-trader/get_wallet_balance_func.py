"""
This module retrieves wallet balance details from the target exchange (Nobitex).
It can fetch either the balance of a single specific asset or compile a unified
dictionary of all active tradable currencies currently available in the user's wallet.
"""

import requests as req
import json
from time import sleep

from get_tradable_crypto_pairs_and_detail_func import *
from variables_func import *
from except_exit_func import *

# Disable SSL verification warnings for bypassing validation check
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_wallet_balance_func(mode_or_crypto_name):
    """
    Fetches the wallet balance for a single cryptocurrency or builds a map of balances
    for all active tradable currencies. Bypasses SSL verification and uses token auth.
    """
    try:
        wallet_balance = ''

        while True:
            try:
                variables = variables_func()
                token = variables["token"]
                crypto_list = ""
                crypto_pairs = []
                wallet_balance = {}

                # Mode: Retrieve balances for all active assets
                if mode_or_crypto_name == "all":
                    counter = 0
                    crypto_pairs = get_tradable_crypto_pairs_and_detail_func("list")

                    for crypto in crypto_pairs:
                        # Drop the 'USDT' suffix (e.g., BTCUSDT -> BTC)
                        crypto_clean = crypto[:-4]
                        crypto_pairs[counter] = crypto_clean
                        crypto_list = crypto_clean.lower() + "," + crypto_list
                        counter += 1

                    # Remove the trailing comma
                    crypto_list = crypto_list[:-1]

                # Mode: Retrieve balance for a single specific asset
                if mode_or_crypto_name != "all":
                    crypto_list = mode_or_crypto_name.lower()
                    crypto_pairs.append(mode_or_crypto_name)

                loop_counter = 0  # Initialized to prevent UnboundLocalError during network exceptions
                while True:
                    try:
                        url = "https://api.nobitex.ir/v2/wallets?currencies=" + crypto_list
                        headers = {'Authorization': 'Token ' + token}
                        resp = req.get(url, headers=headers, verify=False)
                        
                        if resp.status_code == 200:
                            data = json.loads(resp.text)
                            break
                    except (KeyError, TypeError, IndexError, ConnectionError, ValueError, UnboundLocalError, 
                            req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
                        if loop_counter == 2:
                            break
                        loop_counter += 1
                        sleep(0.1)
                        pass

                # Parse single asset balance
                if mode_or_crypto_name != "all":
                    try:
                        wallet_balance = data["wallets"][crypto_pairs[0]]["balance"]
                        break
                    except (KeyError, TypeError, IndexError, ConnectionError, ValueError, UnboundLocalError, 
                            req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
                        pass

                # Parse all asset balances into dictionary map
                if mode_or_crypto_name == "all":
                    try:
                        for crypto in crypto_pairs:
                            wallet_balance[crypto] = data["wallets"][crypto]["balance"]
                    except (KeyError, TypeError, IndexError, ConnectionError, ValueError, UnboundLocalError, 
                            req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
                        pass

                    if wallet_balance is not None:
                        break

            except KeyboardInterrupt:
                except_exit_func()
                
        return wallet_balance
        
    except KeyboardInterrupt:
        except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# print(get_wallet_balance_func("all"))
# while True:
#     print(get_wallet_balance_func("RLS"))