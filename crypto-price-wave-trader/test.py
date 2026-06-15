"""
This is a testing module (test.py) that mimics the logic of the tradable pairs
detail retriever but suppresses console logging. It bypasses SSL validation warnings 
and handles local caching.
"""

from float_truncator_func import *
from get_crypto_price_func import *
from variables_func import *
from except_exit_func import *
from use_regex_func import *

from time import sleep
import os
import requests as req
import json

# Disable SSL verification warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

file_name = "tradable_crypto_pairs_and_monetary_units.txt"


def float_digit_counter(number):
    """
    Calculates decimal digit counts of numbers by reversing string representation.
    Returns 0 if no decimal point is present.
    """
    float_digits = str(number)[::-1].find('.')
    return 0 if float_digits == -1 else float_digits


def get_request_tradable_cryptos_list_and_detail_func():
    """
    Queries exchange configuration options, parses available pairs, calculates 
    precision requirements, and determines if minimum trade equivalent values
    remain equal to or less than 1 USDT. Unlike the live tracker, console logging 
    is kept commented out in this test instance.
    """
    variables_func_list = variables_func()
    crypto_list_exceptions = variables_func_list["crypto_list_exceptions"]

    active_currencies = ""
    amount_precisions = ""
    price_precisions = ""
    all_currencies = []
    tradable_cryptos = []

    loop_counter = 0
    while True:
        try:
            resp = req.request("GET", "https://api.nobitex.ir/v2/options")
            if resp.status_code == 200:
                data = json.loads(resp.text)
                active_currencies = data["nobitex"]["activeCurrencies"]
                xchange_currencies = data["nobitex"]["xchangeCurrencies"]
                amount_precisions = data["nobitex"]["amountPrecisions"]
                price_precisions = data["nobitex"]["pricePrecisions"]
                break
        except (KeyError, TypeError, IndexError, ConnectionError, ValueError, UnboundLocalError, 
                req.exceptions.SSLError, req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError):
            if loop_counter == 2:
                break
            loop_counter += 1
            sleep(0.1)
            pass

    for amount_precision in amount_precisions:
        if use_regex_func(amount_precision, "[A-Z]+USDT"):
            all_currencies.append((amount_precision[:-4]).lower())

    try:
        for active_currencie in active_currencies:
            if active_currencie not in crypto_list_exceptions:
                if active_currencie not in xchange_currencies:
                    if active_currencie in all_currencies:
                        currencie_with_usdt_uppercase = (active_currencie.upper()) + "USDT"
                        crypto_global_price = get_crypto_price_func(currencie_with_usdt_uppercase, "global")
                        
                        if crypto_global_price != 0:
                            amount_float_digit = float_digit_counter(amount_precisions[currencie_with_usdt_uppercase])

                            minimum_tradabade_amount_float = 1.0
                            for i in range(0, amount_float_digit):
                                minimum_tradabade_amount_float *= 0.1

                            minimum_tradable_price = minimum_tradabade_amount_float * crypto_global_price
                            minimum_tradable_price = float_truncator_func(minimum_tradable_price, amount_float_digit, "float")

                            if minimum_tradable_price <= 1.0:
                                # Console prints are kept commented out as per the test file structure
                                # print(active_currencie)
                                # print("===========")

                                tradable_cryptos.append([
                                    currencie_with_usdt_uppercase,
                                    amount_float_digit,
                                    float_digit_counter(price_precisions[currencie_with_usdt_uppercase])
                                ])
    except KeyboardInterrupt:
        except_exit_func()

    return tradable_cryptos


def get_tradable_crypto_pairs_and_detail_func(mode_or_currency):
    """
    Manages cached read/write operations for tradable lists or resolves specific currency records.
    """
    if mode_or_currency == "list" or mode_or_currency != "refresh":
        tradable_list = []

        if not os.path.isfile(file_name):
            with open(file_name, "w") as file:
                pass

        if os.path.isfile(file_name):
            with open(file_name, "r") as file:
                file_read = file.read()

            file_size = len(file_read)

            if file_size == 0:
                tradable_list = get_request_tradable_cryptos_list_and_detail_func()
                with open(file_name, "w") as file:
                    json.dump(tradable_list, file, indent=2)
                    file.flush()

            if file_size > 0:
                with open(file_name, "r") as file:
                    tradable_list = json.load(file)

        if mode_or_currency == "list":
            returner_list = []
            for tradable_currency in tradable_list:
                index = tradable_list.index(tradable_currency)
                returner_list.append(tradable_list[index][0])
            return returner_list

        if mode_or_currency != "refresh" and mode_or_currency != "list":
            for tradable_currency in tradable_list:
                if mode_or_currency in tradable_currency:
                    index = tradable_list.index(tradable_currency)
                    return tradable_list[index]

    if mode_or_currency == "refresh":
        tradable_list = get_request_tradable_cryptos_list_and_detail_func()
        with open(file_name, "w") as file:
            json.dump(tradable_list, file, indent=2)
            file.flush()


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# print(get_tradable_crypto_pairs_and_detail_func("BTCUSDT"))
# print(get_tradable_crypto_pairs_and_detail_func("list"))
# print(get_tradable_crypto_pairs_and_detail_func("refresh"))