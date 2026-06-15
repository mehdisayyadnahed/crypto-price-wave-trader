"""
This module fetches all available cryptocurrency trading pairs ending with 'USDT'
from the target exchange's market-wide order book endpoint.
"""

import requests as req
import json
from time import sleep

# Disable SSL verification warnings caused by bypassing security verification (verify=False)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

from except_exit_func import *
from use_regex_func import *


def get_crypto_pairs_func():
    """
    Requests the complete list of order books from the exchange, filters the keys
    using regex to match 'USDT' trading pairs, and returns a list of them.
    Retries up to 3 times in case of API or connection exceptions.
    """
    try:
        loop_counter = 0
        while True:
            try:
                # Send GET request with SSL verification bypassed to avoid handshake failures
                resp = req.get("https://api.nobitex.ir/v2/orderbook/all", verify=False)
                
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    crypto_pairs = []
                    
                    # Loop through order book keys to identify USDT trading pairs
                    for key in data.keys():
                        if use_regex_func(key, "[A-Z]+USDT"):
                            crypto_pairs.append(key)
                            
                    return crypto_pairs
                    
            except (KeyError, TypeError, IndexError, ConnectionError, ValueError, 
                    UnboundLocalError, req.exceptions.SSLError, req.exceptions.ConnectionError, 
                    req.exceptions.ChunkedEncodingError) as e:
                # Exit the loop and return empty if the retry threshold is reached
                if loop_counter == 2:
                    break
                loop_counter += 1
                sleep(0.1)
                pass
                
    except KeyboardInterrupt:
        except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# while True:
#     print(get_crypto_pairs_func())