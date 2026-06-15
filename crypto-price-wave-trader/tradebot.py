"""
Core Trading Bot Engine.
This module processes sequential market scanning loops for selected pairs,
evaluates arbitrage conditions between global and target order books, monitors
active buy positions, and triggers take-profit, stop-loss, or timeout exit orders.
"""

from calculate_crypto_usdt_balance_func import *
from get_wallet_balance_func import *
from get_tradable_crypto_pairs_and_detail_func import *
from except_exit_func import *
from get_crypto_price_func import *
from get_orderbook_amount_and_price_func import *
from variables_func import *
from get_key_by_value_in_dict import *
from date_time_func import *
from float_truncator_func import *
from buy_sell_func import *

from logger_func import *

from time import sleep
from threading import Thread
from os import path, makedirs

# Load configuration parameters
global_vars = variables_func()
ex_fee = global_vars["ex_fee"]                          # Exchange transaction fee
min_sell_time_diff = global_vars["min_sell_time_diff"]  # Minimum hold time (seconds)
max_sell_time_diff = global_vars["max_sell_time_diff"]  # Maximum hold time (seconds)
min_usdt = global_vars["min_usdt"]                      # Minimum trade threshold in USDT
my_usdt_balance = global_vars["my_usdt_balance"]        # Tracked USDT balance
price_diff = global_vars["price_diff"]                  # Profit margin spread requirement
stop_loss_tolerance = global_vars["stop_loss_tolerance"]  # Tolerance coefficient for stop loss
increase_price_counter = global_vars["increase_price_counter"]  # Sequential ticks needed for trend confirmation

# Normalize thresholds based on fees and margins
stop_loss_tolerance = 1 - stop_loss_tolerance
price_diff = price_diff + (ex_fee * 2)

# Global variables for position tracking
trading_crypto_buy_price = ""
trading_crypto_amount = ""
global_crypto_price_when_buy = ""
stop_loss_price_with_profit = ""
stop_loss_price = ""
min_sell_time = 0
max_sell_time = 0

crypto_pairs = get_tradable_crypto_pairs_and_detail_func("list")


def tradebot(crypto_pair):
    """
    Main state machine for tracking and trading a specific crypto pair.
    Alternates between scan mode ("Buy") and monitor mode (own asset "Sell").
    """
    log_file_counter = 1
    increase_counter = 0
    increase_mode = False
    last_price = 0.0
    new_price = ""

    try:
        try:
            global my_usdt_balance
            global trading_pair

            trading_pair = "Buy"

            while True:
                # -----------------------------------------------------------------
                # STATE 1: SCANNING / BUY MODE
                # -----------------------------------------------------------------
                if trading_pair == "Buy":

                    if trading_pair == "Buy" and float(my_usdt_balance) > min_usdt:
                        # Fetch price metrics
                        global_crypto_pair_price = get_crypto_price_func(crypto_pair, "global")

                        # Analyze the order book on Nobitex for current bid depth
                        target_bid_price_and_amount = get_orderbook_amount_and_price_func(crypto_pair, "target", "bid", my_usdt_balance)
                        buy_request_list = target_bid_price_and_amount[:-1]
                        target_bid_price_and_amount = target_bid_price_and_amount.pop()
                        target_bid_price = target_bid_price_and_amount[0]
                        target_bid_amount = target_bid_price_and_amount[1]
                        
                        # Calculate minimal profitable sell threshold
                        target_bid_price_with_profit = float_truncator_func((target_bid_price + (target_bid_price * price_diff)), 8)
                        
                        # Log scan status
                        log_text = (
                            f"\n============================================================\n"
                            f"{crypto_pair} Check Time: {date_time_func('all', 'Asia/Tehran')}\n"
                            f"Price in Global & Target: {global_crypto_pair_price}, {target_bid_price}\n"
                            f"USDT Balance: {my_usdt_balance}"
                        )
                        log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                        new_price = global_crypto_pair_price

                        # Track consecutive upward price trends
                        if new_price <= last_price:
                            increase_counter = 0
                            increase_mode = False

                        if new_price > last_price:
                            increase_counter += 1
                            if increase_counter == increase_price_counter:
                                increase_mode = True

                        last_price = new_price

                        # Trigger buy execution if market indicates a trend and profit spreads are valid
                        if increase_mode:
                            if trading_pair == "Buy" and global_crypto_pair_price > target_bid_price_with_profit:
                                trading_pair = crypto_pair

                                # Execute market buy order
                                order_values = buy_sell_func("buy", "market", trading_pair, buy_request_list)
                                
                                done_orders_amount = order_values[0][0]
                                done_orders_value = order_values[0][1]
                                canceled_orders_amount = order_values[1][0]
                                canceled_orders_value = order_values[1][1]
                                
                                if done_orders_amount == 0.0:
                                    trading_pair = "Buy"

                                if done_orders_amount > 0.0:
                                    # Deduct executed order value from tracking balance
                                    my_usdt_balance = float_truncator_func((my_usdt_balance - done_orders_value), 8)
                                    if my_usdt_balance < 0:
                                        my_usdt_balance = 0

                                    # Setup holding timeouts
                                    min_sell_time = date_time_func("epoch") + min_sell_time_diff
                                    max_sell_time = date_time_func("epoch") + max_sell_time_diff

                                    trading_crypto_buy_price = target_bid_price
                                    
                                    # Calculate net purchased asset amount (after subtracting exchange fees)
                                    trading_crypto_amount = done_orders_amount - (done_orders_amount * ex_fee)
                                    trading_crypto_amount_show = float_truncator_func(trading_crypto_amount, 8)
                                    
                                    global_crypto_price_when_buy = global_crypto_pair_price
                                    stop_loss_price_with_profit = target_bid_price_with_profit
                                    
                                    # Calculate stop loss limit
                                    stop_loss_price = float_truncator_func((trading_crypto_buy_price + (trading_crypto_buy_price * (price_diff * stop_loss_tolerance))), 8)
                                    
                                    log_text = (
                                        f"\n============================================================\n"
                                        f"Buy {crypto_pair}\n"
                                        f"Amount: {trading_crypto_amount}"
                                    )
                                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)
                                    
                                    print_text = (
                                        f"\n#################################\n"
                                        f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                        f"Balance of {crypto_pair}\n"
                                        f"After Buy is: {trading_crypto_amount_show}\n"
                                        f"Price in Global is: {global_crypto_pair_price}\n"
                                        f"Price in Target is: {target_bid_price}\n"
                                        f"#################################"
                                    )
                                    print(print_text)

                    # Terminate process if USDT balance falls below minimum threshold
                    if trading_pair == "Buy" and float(my_usdt_balance) <= min_usdt:
                        log_text = (
                            f"\n============================================================\n"
                            f"Sorry, No Enough 'USDT' For Continue :( \n"
                            f"============================================================"
                        )
                        log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                        print_text = (
                            f"\n###########################################################\n"
                            f"Sorry, No Enough 'USDT' For Continue :( \n"
                            f"############################################################"
                        )
                        print(print_text)

                        trading_pair = "Stop"
                        except_exit_func()

                # -----------------------------------------------------------------
                # STATE 2: POSITION MONITORING / SELL MODE
                # -----------------------------------------------------------------
                if trading_pair == crypto_pair:
                    # Query current order book ask levels
                    trading_crypto_target_ask_price_and_amount = get_orderbook_amount_and_price_func(trading_pair, "target", "ask", trading_crypto_amount)
                    sell_request_list = trading_crypto_target_ask_price_and_amount[:-1]
                    trading_crypto_target_ask_price_and_amount = trading_crypto_target_ask_price_and_amount.pop()
                    trading_crypto_target_ask_price = trading_crypto_target_ask_price_and_amount[0]
                    trading_crypto_target_ask_amount = trading_crypto_target_ask_price_and_amount[1]

                    trading_crypto_global_ask_price = get_crypto_price_func(crypto_pair, "global")
                    
                    log_text = (
                        f"\n============================================================\n"
                        f"{trading_pair} Check Time: {date_time_func('all', 'Asia/Tehran')}\n"
                        f"Price in Global & Target: {trading_crypto_global_ask_price}, {trading_crypto_target_ask_price}\n"
                        f"USDT Balance: {my_usdt_balance}"
                    )
                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                    # Check position exits if minimum holding duration has passed and balance holds value
                    if trading_pair == crypto_pair and min_sell_time < date_time_func("epoch") and ((trading_crypto_amount * trading_crypto_target_ask_price) + my_usdt_balance) > min_usdt:
                        if trading_pair == crypto_pair and (trading_crypto_amount * trading_crypto_target_ask_price) > min_usdt:
                        
                            # TRIGGER A: Target Price exceeds or matches Global Price (Take Profit)
                            if trading_pair == crypto_pair and trading_crypto_target_ask_price >= trading_crypto_global_ask_price:
                                order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list)
                                done_orders_amount = order_values[0][0]
                                done_orders_value = order_values[0][1]
                                canceled_orders_amount = order_values[1][0]
                                canceled_orders_value = order_values[1][1]

                                if done_orders_value > 0.0:
                                    executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                    my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                                    log_text = (
                                        f"\n============================================================\n"
                                        f"Sell {trading_pair}\n"
                                        f"Amount: {trading_crypto_amount}\n"
                                        f"For Target Over Price."
                                    )
                                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)
                                    
                                    print_text = (
                                        f"\n#################################\n"
                                        f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                        f"Balance of USDT\n"
                                        f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                        f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                        f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                        f"For Target Over Price.\n"
                                        f"#################################"
                                    )
                                    print(print_text)
                                    trading_pair = "Buy"

                            # TRIGGER B: Global Ask Price drops below calculated Stop Loss limit
                            if trading_pair == crypto_pair and trading_crypto_global_ask_price <= stop_loss_price:
                                order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list) 
                                done_orders_amount = order_values[0][0]
                                done_orders_value = order_values[0][1]
                                canceled_orders_amount = order_values[1][0]
                                canceled_orders_value = order_values[1][1]

                                if done_orders_value > 0.0:
                                    executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                    my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                                    log_text = (
                                        f"\n============================================================\n"
                                        f"Sell {trading_pair}\n"
                                        f"Amount: {trading_crypto_amount}\n"
                                        f"For Global Price Stop Loss."
                                    )
                                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                                    print_text = (
                                        f"\n#################################\n"
                                        f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                        f"Balance of USDT\n"
                                        f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                        f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                        f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                        f"For Global Price Stop Loss.\n"
                                        f"#################################"
                                    )
                                    print(print_text)
                                    trading_pair = "Buy"

                            # TRIGGER C: Target Ask Price drops below calculated Stop Loss limit
                            if trading_pair == crypto_pair and trading_crypto_target_ask_price <= stop_loss_price:
                                order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list) 
                                done_orders_amount = order_values[0][0]
                                done_orders_value = order_values[0][1]
                                canceled_orders_amount = order_values[1][0]
                                canceled_orders_value = order_values[1][1]

                                if done_orders_value > 0.0:
                                    executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                    my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                                    log_text = (
                                        f"\n============================================================\n"
                                        f"Sell {trading_pair}\n"
                                        f"Amount: {trading_crypto_amount}\n"
                                        f"For Target Price Stop Loss."
                                    )
                                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                                    print_text = (
                                        f"\n#################################\n"
                                        f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                        f"Balance of USDT\n"
                                        f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                        f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                        f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                        f"For Target Price Stop Loss.\n"
                                        f"#################################"
                                    )
                                    print(print_text)
                                    trading_pair = "Buy"

                            # TRIGGER D: Holding Duration exceeds Maximum Allowed Hold Time (Time Limit Exit)
                            if max_sell_time < date_time_func("epoch") and trading_pair == crypto_pair:
                                order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list)
                                done_orders_amount = order_values[0][0]
                                done_orders_value = order_values[0][1]
                                canceled_orders_amount = order_values[1][0]
                                canceled_orders_value = order_values[1][1]

                                if done_orders_value > 0.0:
                                    executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                    my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                                    log_text = (
                                        f"\n============================================================\n"
                                        f"Sell {trading_pair}\n"
                                        f"Amount: {trading_crypto_amount}\n"
                                        f"For Max Sell Time."
                                    )
                                    log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)
                                    
                                    print_text = (
                                        f"\n#################################\n"
                                        f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                        f"Balance of USDT\n"
                                        f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                        f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                        f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                        f"For Max Sell Time.\n"
                                        f"#################################"
                                    )
                                    print(print_text)
                                    trading_pair = "Buy"

                        # Handle exception when estimated value of remaining crypto falls below the minimum limit
                        if trading_pair == crypto_pair and (trading_crypto_amount * trading_crypto_target_ask_price) <= min_usdt:
                            order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list)
                            done_orders_amount = order_values[0][0]
                            done_orders_value = order_values[0][1]
                            canceled_orders_amount = order_values[1][0]
                            canceled_orders_value = order_values[1][1]

                            if done_orders_value > 0.0:
                                executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                                my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                                log_text = (
                                    f"\n============================================================\n"
                                    f"Sell {trading_pair}\n"
                                    f"Amount: {trading_crypto_amount}\n"
                                    f"For Minimum 'Crypto'."
                                )
                                log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                                print_text = (
                                    f"\n#################################\n"
                                    f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                    f"Balance of USDT\n"
                                    f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                    f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                    f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                    f"For Minimum 'Crypto'.\n"
                                    f"#################################"
                                )
                                print(print_text)
                                trading_pair = "Buy"
                            
                            else:
                                log_text = (
                                    f"\n============================================================\n"
                                    f"Sorry, No Enough 'Crypto' For Continue :( \n"
                                    f"============================================================"
                                )
                                log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                                print_text = (
                                    f"\n######################################################\n"
                                    f"Sorry, No Enough 'Crypto' For Continue :( \n"
                                    f"######################################################"
                                )
                                print(print_text)

                                trading_pair = "Stop"
                                except_exit_func()

                    # Handle exception when cumulative valuation drops below the safety margin
                    if trading_pair == crypto_pair and ((trading_crypto_amount * trading_crypto_target_ask_price) + my_usdt_balance) <= min_usdt:
                        order_values = buy_sell_func("sell", "market", trading_pair, sell_request_list)
                        done_orders_amount = order_values[0][0]
                        done_orders_value = order_values[0][1]
                        canceled_orders_amount = order_values[1][0]
                        canceled_orders_value = order_values[1][1]

                        if done_orders_value > 0.0:
                            executed_net_value = done_orders_value - (done_orders_value * ex_fee)
                            my_usdt_balance = float_truncator_func((my_usdt_balance + executed_net_value), 8)

                            log_text = (
                                f"\n============================================================\n"
                                f"Sell {trading_pair}\n"
                                f"Amount: {trading_crypto_amount}\n"
                                f"For Minimum 'USDT' and 'Crypto'."
                            )
                            log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                            print_text = (
                                f"\n#################################\n"
                                f"At: {date_time_func('all', 'Asia/Tehran')}\n"
                                f"Balance of USDT\n"
                                f"After Sell {crypto_pair} is: {my_usdt_balance}\n"
                                f"Price in Global is: {trading_crypto_global_ask_price}\n"
                                f"Price in Target is: {trading_crypto_target_ask_price}\n"
                                f"For Minimum 'USDT' and 'Crypto'.\n"
                                f"#################################"
                            )
                            print(print_text)

                        log_text = (
                            f"\n============================================================\n"
                            f"Sorry, No Enough 'Crypto' And 'USDT' For Continue :( \n"
                            f"============================================================"
                        )
                        log_file_counter = logger_func(log_file_counter, crypto_pair, log_text)

                        print_text = (
                            f"\n######################################################\n"
                            f"Sorry, No Enough 'Crypto' And 'USDT' For Continue :( \n"
                            f"######################################################"
                        )
                        print(print_text)

                        trading_pair = "Stop"
                        except_exit_func()
                sleep(5)
        except (KeyError, TypeError, IndexError, ValueError, UnboundLocalError):
            pass
    except KeyboardInterrupt:
        except_exit_func()


def main():
    """
    Main runner when running this file directly. Launches independent threads 
    for each tradable currency pair and maintains daemon execution.
    """
    try:
        for crypto_pair in crypto_pairs:
            trade_bot_thread = Thread(target=tradebot, args=(str(crypto_pair),))
            trade_bot_thread.start()
            
        from parallel_thread_funcs import parallel_thread_funcs
        parallel_thread = Thread(target=parallel_thread_funcs)
        parallel_thread.start()

    except Exception:
        print("\nAn Error Happened!")
        except_exit_func()

    try:
        while True:
            sleep(0.3)
    except KeyboardInterrupt:
        except_exit_func()


if __name__ == '__main__':
    main()