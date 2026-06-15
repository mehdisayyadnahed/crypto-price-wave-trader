"""
This module retrieves order book depth from local and global exchanges.
It processes bid/ask prices and volumes, and calculates the exact execution
average price based on the volume of the intended trade (Orderbook Depth Analysis).
"""

import requests as req
import json
from time import sleep

# Disable SSL verification warnings for insecure requests (verify=False)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

from except_exit_func import *
from float_truncator_func import *


def json_data_reader(site, data, mode, counter, price_or_amount):
    """
    Safely retrieves bid/ask prices and amounts from various exchange order books.
    Normalizes keys across exchanges (e.g., Coinbase, Bybit, Kraken).
    """
    if mode == "bid":
        mode = "bids"
    elif mode == "ask":
        mode = "asks"

    try:
        # Standard format exchanges
        if site in ("nobitex", "binance", "gateio"):
            return float(data[mode][counter][price_or_amount])
            
        if site == "kraken":
            pair_key = list(data["result"].keys())[0]
            return float(data["result"][pair_key][mode][counter][price_or_amount])
            
        if site == "huobi":
            return float(data["tick"][mode][counter][price_or_amount])
            
        if site == "coinbase":
            field = "price" if price_or_amount == 0 else "size" if price_or_amount == 1 else price_or_amount
            return float(data["pricebook"][mode][counter][field])
            
        if site == "bybit":
            bybit_mode = 'b' if mode == "bids" else 'a' if mode == "asks" else mode
            return float(data["result"][bybit_mode][counter][price_or_amount])

    except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
        pass


def json_data_checker(site, data, mode):
    """
    Verifies if the order book payload contains valid and non-empty data at the top depth.
    """
    try:
        price = json_data_reader(site, data, mode, 0, 0)
        amount = json_data_reader(site, data, mode, 0, 1)
        
        if price and amount:
            if price is not None and amount is not None and price != "" and amount != "":
                return True
        return False
    except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
        return False


def price_and_amount_calculator(site, data, mode, amount_of_trade):
    """
    Calculates execution price and volume by matching the intended trade size (USDT or crypto)
    against the order book depth levels. Returns detailed list of matched levels and averages.
    """
    try:
        if mode == "bid":
            bid_price_of_amount = 0.0
            counter = 0
            while True:
                if counter == 0:
                    bid_price = json_data_reader(site, data, mode, counter, 0)
                    bid_amount = json_data_reader(site, data, mode, counter, 1)
                    bid_price_of_amount = bid_amount * bid_price
                    counter = 1
                    
                    if bid_price_of_amount >= amount_of_trade:
                        returner = [[], []]
                        returner[0].append(bid_price)
                        returner[0].append(float_truncator_func((amount_of_trade / bid_price), 8))
                        returner[1].append(bid_price)
                        returner[1].append(float_truncator_func((amount_of_trade / bid_price), 8))
                        return returner

                bid_amount_sum = 0.0
                last_bid_price = 0.0
                last_bid_amount = 0.0
                bid_price_of_amount_sum = 0.0
                
                if counter == 1:
                    counter = 0
                    returner = []
                    while True:
                        last_bid_price = json_data_reader(site, data, mode, counter, 0)
                        last_bid_amount = json_data_reader(site, data, mode, counter, 1)
                        bid_amount_sum += last_bid_amount
                        bid_price_of_amount = last_bid_price * last_bid_amount
                        bid_price_of_amount_sum += bid_price_of_amount
                        
                        returner.append([])
                        returner[counter].append(last_bid_price)
                        returner[counter].append(last_bid_amount)
                        
                        if bid_price_of_amount_sum == amount_of_trade:
                            returner.append([])
                            returner[counter + 1].append(float_truncator_func((amount_of_trade / bid_amount_sum), 8))
                            returner[counter + 1].append(float_truncator_func(bid_amount_sum, 8))
                            return returner
                            
                        if bid_price_of_amount_sum > amount_of_trade:
                            diff_price_of_amount = bid_price_of_amount_sum - (last_bid_price * last_bid_amount)
                            diff_price_of_amount = amount_of_trade - diff_price_of_amount
                            need_of_last_bid_amount = float_truncator_func((diff_price_of_amount / last_bid_price), 8)
                            
                            bid_amount_sum -= last_bid_amount
                            bid_amount_sum += need_of_last_bid_amount
                            
                            returner[counter][0] = last_bid_price
                            returner[counter][1] = need_of_last_bid_amount
                            
                            returner.append([])
                            returner[counter + 1].append(float_truncator_func((amount_of_trade / bid_amount_sum), 8))
                            returner[counter + 1].append(float_truncator_func(bid_amount_sum, 8))
                            return returner
                            
                        counter += 1

        if mode == "ask":
            ask_price_of_amount = 0.0
            counter = 0
            while True:
                if counter == 0:
                    ask_price = json_data_reader(site, data, mode, counter, 0)
                    ask_amount = json_data_reader(site, data, mode, counter, 1)
                    counter = 1
                    
                    if ask_amount >= amount_of_trade:
                        returner = [[], []]
                        returner[0].append(ask_price)
                        returner[0].append(amount_of_trade)
                        returner[1].append(ask_price)
                        returner[1].append(amount_of_trade)
                        return returner

                ask_amount_sum = 0.0
                ask_price_sum = 0.0
                last_ask_price = 0.0
                last_ask_amount = 0.0
                ask_price_of_amount_sum = 0.0
                
                if counter == 1:
                    counter = 0
                    returner = []
                    while True:
                        last_ask_price = json_data_reader(site, data, mode, counter, 0)
                        last_ask_amount = json_data_reader(site, data, mode, counter, 1)
                        ask_amount_sum += last_ask_amount
                        ask_price_of_amount = last_ask_price * last_ask_amount
                        ask_price_of_amount_sum += ask_price_of_amount
                        
                        returner.append([])
                        returner[counter].append(last_ask_price)
                        returner[counter].append(last_ask_amount)
                        
                        if ask_amount_sum == amount_of_trade:
                            returner.append([])
                            returner[counter + 1].append(float_truncator_func((ask_price_of_amount_sum / amount_of_trade), 8))
                            returner[counter + 1].append(amount_of_trade)
                            return returner
                            
                        if ask_amount_sum > amount_of_trade:
                            diff_of_amount = ask_amount_sum - last_ask_amount
                            diff_of_amount = amount_of_trade - diff_of_amount
                            
                            ask_price_of_amount_sum = float_truncator_func(ask_price_of_amount_sum - (last_ask_price * last_ask_amount), 8)
                            ask_price_of_amount_sum = float_truncator_func(ask_price_of_amount_sum + (diff_of_amount * last_ask_price), 8)
                            
                            returner.append([])
                            returner[counter][0] = float_truncator_func(last_ask_price, 8)
                            returner[counter][1] = float_truncator_func(diff_of_amount, 8)
                            
                            returner[counter + 1].append(float_truncator_func((ask_price_of_amount_sum / amount_of_trade), 8))
                            returner[counter + 1].append(amount_of_trade)
                            return returner
                            
                        counter += 1

    except KeyboardInterrupt:
        except_exit_func()


def get_target_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade):
    """
    Fetches the order book from the target exchange (Nobitex) and calculates
    the volume-weighted price and matched amounts.
    """
    try:
        loop_counter = 0
        while True:
            try:
                resp = req.get("https://api.nobitex.ir/v2/orderbook/" + crypto_pair, verify=False)
                site = "nobitex"
                
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    if json_data_checker(site, data, mode):
                        return price_and_amount_calculator(site, data, mode, amount_of_trade)
                        
            except (ConnectionError, req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
                if loop_counter == 2:
                    break
                loop_counter += 1
                sleep(0.1)
                pass
    except KeyboardInterrupt:
        except_exit_func()


def get_global_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade):
    """
    Fetches order books from up to 6 major international exchanges, calculates
    the average price based on intended volume, and computes global average.
    """
    try:
        price_sum = 0.0
        avg_counter = 0
        loop_counter = 0
        site_counter = 0
        site = ""

        while avg_counter <= 2:
            while site_counter <= 5:
                while loop_counter <= 2:
                    try:
                        if site_counter == 0:
                            resp = req.get("https://api.bybit.com/v5/market/orderbook?category=spot&symbol=" + crypto_pair + "&limit=20", verify=False)
                            site = "bybit"
                        elif site_counter == 1:
                            resp = req.get("https://api.kraken.com/0/public/Depth?pair=" + crypto_pair + "&count=20", verify=False)
                            site = "kraken"
                        elif site_counter == 2:
                            resp = req.get("https://api.gateio.ws/api/v4/spot/order_book?currency_pair=" + (crypto_pair[:-4] + "_" + crypto_pair[-4:]) + "&limit=20", verify=False)
                            site = "gateio"
                        elif site_counter == 3:
                            resp = req.get("https://api2.binance.com/api/v3/depth?symbol=" + crypto_pair + "&limit=20", verify=False)
                            site = "binance"
                        elif site_counter == 4:
                            resp = req.get("https://api.coinbase.com/api/v3/brokerage/market/product_book?product_id=" + (crypto_pair[:-4] + "-" + crypto_pair[-4:]) + "&limit=20", verify=False)
                            site = "coinbase"
                        elif site_counter == 5:
                            resp = req.get("https://api.huobi.pro/market/depth?symbol=" + crypto_pair.lower() + "&type=step0&depth=20", verify=False)
                            site = "huobi"

                        if resp.status_code == 200:
                            data = json.loads(resp.text)
                            if json_data_checker(site, data, mode):
                                price_and_amount = price_and_amount_calculator(site, data, mode, amount_of_trade)
                                price_and_amount = price_and_amount.pop()
                                price_sum += price_and_amount[0]
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


def get_orderbook_amount_and_price_func(crypto_pair, site, mode, amount_of_trade):
    """
    Main orchestrator for volume-weighted order book pricing.
    - 'target' returns local (Nobitex) levels.
    - 'global' returns average global levels.
    - 'all' returns both target and global inside a dictionary.
    """
    if site == "target":
        return get_target_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade)

    if site == "global":
        return get_global_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade)

    if site == "all":
        target_data = get_target_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade)
        target_price = target_data.pop()[0]

        global_price = get_global_orderbook_amount_and_price_func(crypto_pair, mode, amount_of_trade)

        return {
            "target": target_price,
            "global": global_price
        }


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# while True:
#     print(get_orderbook_amount_and_price_func("BTCUSDT", "global", "bid", 3000))
#     print(get_orderbook_amount_and_price_func("BTCUSDT", "all", "ask", 0.1))
#     a = get_orderbook_amount_and_price_func("ETHUSDT", "target", "bid", 20000)
#     a = a[:-1]
#     a = a.pop()
#     print(a)
#     print(float_truncator_func(a[1], 8, "string"))