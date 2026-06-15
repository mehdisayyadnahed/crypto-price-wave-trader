"""
This module contains functions to send buy and sell requests to the exchange API,
check order statuses, cancel active orders if necessary, and process the results.
"""

from get_orderbook_amount_and_price_func import *
from float_truncator_func import *
from variables_func import *
from except_exit_func import *
from get_tradable_crypto_pairs_and_detail_func import *

from time import sleep
import requests as req
import json

# Global variables for trade floating point sizes
crypto_float_size_for_trade = ""
usdt_float_size_for_trade = ""

# Load configurations from variables_func.py
global_vars = variables_func()

# API token used for authorization. Make sure to define YOUR_NOBITEX_API_TOKEN in variables_func.py
token = global_vars["token"]
ex_fee = global_vars["ex_fee"]


def get_order_status_request_func(order_id):
    """
    Sends a GET request to retrieve the status of a specific order from the exchange.
    Returns status details: [order_status, order_amount, order_price, order_amount_on_price].
    """
    url = "https://api.nobitex.ir/market/orders/status?id=" + str(order_id)
    payload = {}
    headers = {'Authorization': 'Token ' + token}

    counter = 0
    while True:
        try:
            resp = req.request("GET", url, headers=headers, data=payload)
            if resp.status_code == 200:
                data = json.loads(resp.text)
                order_status = data["order"]["status"]
                order_amount = data["order"]["amount"]
                order_price = data["order"]["totalPrice"]
                order_amount_on_price = data["order"]["totalOrderPrice"]
                
                return [order_status, order_amount, order_price, order_amount_on_price]
                
        except (KeyError, TypeError, IndexError, ConnectionError, ValueError, 
                UnboundLocalError, req.exceptions.SSLError, req.exceptions.ConnectionError, 
                req.exceptions.ChunkedEncodingError) as e:
            if counter == 2:
                break
            counter += 1
            sleep(0.1)
            pass


def order_status_result_check_func(order_id):
    """
    Checks the status of an order. If the order is 'Active' after some delay, 
    it will attempt to cancel the order and return the executed transaction details.
    """
    order_detail = get_order_status_request_func(order_id)

    if order_detail is None:
        return None
    
    sleep(1)

    order_status = order_detail[0]
    order_amount = order_detail[1]
    order_price = order_detail[2]
    order_amount_on_price = float(order_detail[3])

    # If the order is finalized (Done or Canceled), return the details immediately
    if (order_status == "Done") or (order_status == "Canceled"):
        return [order_status, order_amount, order_price, order_amount_on_price]

    # If the order is still Active, wait and attempt to cancel it
    if order_status == "Active":
        sleep(5)

        url = "https://api.nobitex.ir/market/orders/update-status"
        payload = {
            "order": order_id,
            "status": "canceled"
        }
        files = []
        headers = {'Authorization': 'Token ' + token}

        counter = 0
        while True:
            try:
                resp = req.request("POST", url, headers=headers, data=payload, files=files)
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    order_status = data["updatedStatus"]
                    
                    if order_status == "Done":
                        return ["Done", order_amount, order_price, order_amount_on_price]
                    if order_status == "Canceled":
                        return ["Canceled", order_amount, order_price, order_amount_on_price]
                        
            except (KeyError, TypeError, IndexError, ConnectionError, ValueError, 
                    UnboundLocalError, req.exceptions.SSLError, req.exceptions.ConnectionError, 
                    req.exceptions.ChunkedEncodingError) as e:
                if counter == 2:
                    break
                counter += 1
                sleep(0.1)
                pass


def send_buy_sell_req_func(buy_sell_mode, price_mode, crypto_pair, crypto_float_size_for_trade, 
                           usdt_float_size_for_trade, amount, price=0.0):
    """
    Formats parameters and sends a buy or sell request to the exchange.
    Returns the order ID if the order status becomes 'Active'.
    """
    buy_sell_mode = buy_sell_mode.lower()
    price_mode = price_mode.lower()
    crypto_pair = (crypto_pair[:-4]).lower()

    # Truncate amount and price based on exchange precision requirements
    amount = float_truncator_func(amount, crypto_float_size_for_trade)
    price = float_truncator_func(price, usdt_float_size_for_trade)

    url = "https://api.nobitex.ir/market/orders/add"
    payload = ""

    # Construct payload based on execution mode (market vs limit)
    if price_mode == "market":
        payload = {
            "type": buy_sell_mode,
            "srcCurrency": crypto_pair,
            "dstCurrency": 'usdt',
            "execution": price_mode,
            "amount": amount
        }

    if price_mode == "limit":
        payload = {
            "type": buy_sell_mode,
            "srcCurrency": crypto_pair,
            "dstCurrency": 'usdt',
            "execution": price_mode,
            "price": price,
            "amount": amount
        }

    files = []
    headers = {'Authorization': 'Token ' + token}

    counter = 0
    while True:
        try:
            resp = req.request("POST", url, headers=headers, data=payload, files=files)
            print(resp.text)
            if resp.status_code == 200:
                data = json.loads(resp.text)
                
                if data["status"] == "ok":
                    order_status = data["order"]["status"]
                    order_id = data["order"]["id"]
                    
                    if order_status == "Active":
                        return order_id
                        
        except (KeyError, TypeError, IndexError, ConnectionError, ValueError, 
                UnboundLocalError, req.exceptions.SSLError, req.exceptions.ConnectionError, 
                req.exceptions.ChunkedEncodingError) as e:
            if counter == 2:
                break
            counter += 1
            sleep(0.1)
            pass


def buy_sell_func(buy_sell_mode, price_mode, crypto_pair, buy_sell_amount_and_price_list):
    """
    Main function to execute a batch of order requests and process their execution outcome.
    Returns a structured nested list containing total Done and Canceled values and amounts.
    """
    orders_id_list = []
    orders_detail_list = []

    # Retrieve trade precision parameters
    crypto_float_sizes_for_trade = get_tradable_crypto_pairs_and_detail_func(crypto_pair)
    crypto_float_size_for_trade = crypto_float_sizes_for_trade[1]
    usdt_float_size_for_trade = crypto_float_sizes_for_trade[2]

    # Step 1: Submit all batch trade requests
    counter = 0
    for buy_sell_request in buy_sell_amount_and_price_list:
        orders_id_list.append(
            send_buy_sell_req_func(
                buy_sell_mode, 
                price_mode, 
                crypto_pair, 
                crypto_float_size_for_trade, 
                usdt_float_size_for_trade, 
                buy_sell_request[1], 
                buy_sell_request[0]
            )
        )
        counter += 1

    # Step 2: Verify the status of submitted orders
    counter = 0
    for order_id in orders_id_list:
        order_status_result_check = order_status_result_check_func(order_id)
        if order_status_result_check is not None:
            orders_detail_list.append(order_status_result_check)
        counter += 1

    total_done_orders_amount = 0.0
    total_done_orders_value = 0.0
    total_canceled_orders_amount = 0.0
    total_canceled_orders_value = 0.0

    orders_result = [[0.0, 0.0], [0.0, 0.0]]

    # Step 3: Aggregate calculations for successful vs canceled parts of the orders
    counter = 0
    for order_detail in orders_detail_list:
        if order_detail[0] == "Done":
            total_done_orders_amount += float(order_detail[1])
            total_done_orders_value += float(order_detail[3])

        if order_detail[0] == "Canceled":
            total_canceled_orders_amount += float(order_detail[1])
            total_canceled_orders_value += float(order_detail[3])
        
        counter += 1

    # Format the aggregated results safely based on asset precision requirements
    orders_result[0][0] = float_truncator_func(total_done_orders_amount, crypto_float_size_for_trade)
    orders_result[0][1] = float_truncator_func(total_done_orders_value, usdt_float_size_for_trade)
    orders_result[1][0] = float_truncator_func(total_canceled_orders_amount, crypto_float_size_for_trade)
    orders_result[1][1] = float_truncator_func(total_canceled_orders_value, usdt_float_size_for_trade)
    
    return orders_result


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# amount = 0.1
# amount = (amount - (amount * 0.015))

# ### buy crypto amount base
# amount = 5
# mode = "ask"
# crypto_pair = "WLDUSDT"
# buy_sell = "buy"
# #########
# target_bid_price_and_amount = get_orderbook_amount_and_price_func(crypto_pair , "target", mode, amount)
# buy_amount_and_price_list = target_bid_price_and_amount[:-1]
# print (buy_amount_and_price_list)
# # total_orders_value = target_bid_price_and_amount.pop()
# done_orders = buy_sell_func(buy_sell, "market", crypto_pair, buy_amount_and_price_list)
# print (done_orders)
# print (float_truncator_func(done_orders[0][0], 9, "string"))


# ### sell usdt amount base
# amount = 5
# mode = "bid"
# crypto_pair = "WLDUSDT"
# buy_sell = "sell"
# #########
# target_bid_price_and_amount = get_orderbook_amount_and_price_func(crypto_pair , "target", mode, amount)
# buy_amount_and_price_list = target_bid_price_and_amount[:-1]
# print (buy_amount_and_price_list)
# # total_orders_value = target_bid_price_and_amount.pop()
# done_orders = buy_sell_func(buy_sell, "market", crypto_pair, buy_amount_and_price_list)
# print (done_orders)
# print (float_truncator_func(done_orders[0][0], 9, "string"))