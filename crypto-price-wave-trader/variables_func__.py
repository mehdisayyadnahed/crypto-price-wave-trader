"""
Configuration File (Backup / Legacy Version).
This module exposes a dictionary containing bot configuration variables, 
risk limits, and authorization tokens. Make sure to replace placeholders 
with your actual credentials.
"""


def variables_func():
    """
    Defines and returns execution variables, blacklisted assets, fee parameters, 
    risk settings, hold-times, and API access credentials for the bot.
    """
    variables = {
        # List of cryptocurrencies excluded from active trading (e.g., stablecoins or low-liquidity assets)
        "crypto_list_exceptions": ["pmn", "shib", "dai", "usdc", "usdt", "busd", "gala", "pgala", "egala"],
        
        # API Authorization Token. SECURITY: REPLACE WITH YOUR ACTUAL KEY
        "token": "YOUR_NOBITEX_API_TOKEN",
        
        # Exchange platform transaction fee percentage (0.0015 represents 0.15%)
        "ex_fee": 0.0015,
        
        # Account USDT balance tracking for simulation/execution
        "my_usdt_balance": 0.5,  # Alternative templates: #23, #11
        
        # Minimum USDT required to initiate any purchase
        "min_usdt": 0.475,  # Alternative templates: #20, #11.1
        
        # Minimum hold duration (seconds) before allowed to initiate a sell
        "min_sell_time_diff": 1,  # Alternative hold-times: #180, #300
        
        # Maximum hold duration (seconds) before a time exit triggers
        "max_sell_time_diff": 100,
        
        # Minimal price spread percentage required to execute a buy (e.g., 0.009 is 0.9%)
        "price_diff": 0.0000001,  # Alternative spreads: #0.009, #0.01
        
        # Tolerance coefficient multiplier for trailing stop loss
        "stop_loss_tolerance": 0.5,  # Alternative coefficients: #0.25
        
        # Consecutive positive price updates required to verify an upward price trend
        "increase_price_counter": 1  # Alternative limits: #1, #3, #7
    }

    return variables