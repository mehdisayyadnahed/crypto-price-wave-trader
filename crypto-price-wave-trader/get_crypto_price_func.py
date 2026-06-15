"""
This module retrieves cryptocurrency prices from various global exchanges 
and the target exchange (Nobitex). It parses different API response formats,
safely checks prices, and calculates a global average price based on availability.
"""

from time import sleep
import requests as req
import json

# Disable SSL insecure verification warnings (verify=False)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

from float_truncator_func import *
from except_exit_func import *


def json_data_reader(site, data):
    """
    Extracts the latest transaction price from the raw JSON payload of a specific exchange.
    Truncates the price output to 8 decimal places.
    """
    try:
        if site == "nobitex":
            return float_truncator_func(float(data["trades"][0]["price"]), 8)
        if site == "bybit":
            return float_truncator_func(float(data["result"]["list"][0]["lastPrice"]), 8)
        if site == "kraken":
            return float_truncator_func(float(data["result"][list(data["result"].keys())[0]]["a"][0]), 8)
        if site == "gateio":
            return float_truncator_func(float(data["last"]), 8)
        if site == "binance":
            return float_truncator_func(float(data["price"]), 8)
        if site == "coinbase":
            return float_truncator_func(float(data["price"]), 8)
        if site == "huobi":
            return float_truncator_func(float(data["tick"]["close"]), 8)

    except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
        pass


def json_data_checker(site, data):
    """
    Validates if the extracted price is valid (not None or empty).
    Returns the parsed price if valid, otherwise returns False.
    """
    try:
        price = json_data_reader(site, data)
        if price:
            if price is not None and price != "":
                return price
        return False
    except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
        return False


def get_crypto_global_func(crypto_pair):
    """
    Fetches latest prices from up to 6 major international exchanges.
    Iterates through candidates trying to fetch at least 3 successful API responses.
    Each endpoint will retry up to 3 times in case of transport errors.
    Returns the truncated average price, or 0 if no sources are available.
    """
    try:
        price_sum = 0.0
        avg_counter = 0
        loop_counter = 0
        site_counter = 0
        site = ""

        # Attempt to gather up to 3 successful exchange prices
        while avg_counter <= 2:
            while site_counter <= 5:
                while loop_counter <= 2:
                    try:
                        if site_counter == 0:
                            resp = req.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=" + crypto_pair, verify=False)
                            site = "bybit"
                        elif site_counter == 1:
                            resp = req.get("https://api.kraken.com/0/public/Ticker?pair=" + crypto_pair, verify=False)
                            site = "kraken"
                        elif site_counter == 2:
                            resp = req.get("https://data.gateapi.io/api/1/ticker/" + (crypto_pair[:-4] + "_" + crypto_pair[-4:]).lower(), verify=False)
                            site = "gateio"
                        elif site_counter == 3:
                            resp = req.get("https://api2.binance.com/api/v3/ticker/price?symbol=" + crypto_pair, verify=False)
                            site = "binance"
                        elif site_counter == 4:
                            resp = req.get("https://api.exchange.coinbase.com/products/" + (crypto_pair[:-4] + "-" + crypto_pair[-4:]).lower() + "/ticker", verify=False)
                            site = "coinbase"
                        elif site_counter == 5:
                            resp = req.get("https://api.huobi.pro/market/detail/merged?symbol=" + crypto_pair.lower(), verify=False)
                            site = "huobi"

                        if resp.status_code == 200:
                            data = json.loads(resp.text)
                            json_data_checker_result = json_data_checker(site, data)
                            if json_data_checker_result is not False:
                                price_sum += json_data_checker_result
                                avg_counter += 1
                                loop_counter = 0
                                break

                        loop_counter += 1

                    except (ConnectionError, req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
                        loop_counter += 1
                        sleep(0.1)
                        pass

                site_counter += 1
                loop_counter = 0
                break

            if site_counter > 5:
                break

        if avg_counter > 0:
            return float_truncator_func((price_sum / avg_counter), 8)
        else:
            return 0.0

    except KeyboardInterrupt:
        except_exit_func()


def get_crypto_target_func(crypto_pair):
    """
    Fetches the current transaction price from the target exchange (Nobitex).
    Retries up to 3 times in case of failure.
    """
    try:
        loop_counter = 0
        while True:
            try:
                resp = req.get("https://api.nobitex.ir/v2/trades/" + crypto_pair, verify=False)
                site = "nobitex"
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    json_data_checker_result = json_data_checker(site, data)
                    if json_data_checker_result is not False:
                        return json_data_checker_result
            except (KeyError, TypeError, IndexError, ConnectionError, ValueError, 
                    UnboundLocalError, req.exceptions.SSLError, req.exceptions.ConnectionError, 
                    req.exceptions.ChunkedEncodingError):
                if loop_counter == 2:
                    break
                loop_counter += 1
                sleep(0.1)
                pass
    except KeyboardInterrupt:
        except_exit_func()


def get_crypto_price_func(crypto_pair, output_mode):
    """
    Orchestrates price requests.
    - 'global' returns the average international price.
    - 'target' returns the target exchange price.
    - 'all' returns both target and global prices in a dictionary.
    """
    try:
        if output_mode == "global":
            return get_crypto_global_func(crypto_pair)
        if output_mode == "target":
            return get_crypto_target_func(crypto_pair)
        if output_mode == "all":
            target = get_crypto_target_func(crypto_pair)
            avg_price = get_crypto_global_func(crypto_pair)
            
            return {
                "target": target,
                "global": avg_price
            }
    except KeyboardInterrupt:
        except_exit_func()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# while True:
#     print(get_crypto_price_func("BTCUSDT", "all"))
#     print(get_crypto_price_func("BTCUSDT", "global"))
#     print(get_crypto_price_func("BTCUSDT", "target"))