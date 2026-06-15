"""
Configuration File (Active Production Version).
This module exposes a dictionary containing bot configuration variables, 
risk limits, logging restrictions, and authorization tokens. Make sure 
to replace placeholders with your actual credentials.
"""


def variables_func():
    """
    Defines and returns active execution variables, blacklisted assets, fee parameters, 
    risk settings, hold-times, and API access credentials for the bot.
    """
    variables = {
        # Comprehensive list of cryptocurrencies excluded from active trading (e.g., stablecoins, BTC, ETH, and meme coins)
        "crypto_list_exceptions": [
            "rls", "pmn", "shib", "floki", "nft", "btt", "pepe", "babydoge", "dai", "usdc", "usdt", "busd", 
            "gala", "pgala", "egala", "btc", "eth", "ltc", "xrp", "bnb", "eos", "xlm", "etc", "trx", "pmn", 
            "doge", "dai", "dot", "aave", "ada", "ftm", "axs", "mana", "sand", "mkr", "gmt", "usdc", "sol", 
            "atom", "bat", "grt", "near", "ape", "chz", "qnt", "xmr", "busd", "algo", "egala", "hbar", "yfi", 
            "snx", "enj", "crv", "flow", "wbtc", "ldo", "fil", "dydx", "apt", "mask", "flr", "lrc", "comp", 
            "bal", "ens", "sushi", "lpt", "glm", "api3", "one", "dao", "cvc", "nmr", "storj", "snt", "slp", 
            "zrx", "imx", "egld", "blur", "t", "celr", "arb", "1inch", "magic", "gmx", "ton", "band", "cvx", 
            "mdt", "ssv", "wld", "omg", "rdnt", "jst", "render", "bico", "woo", "skl", "fet", "not", "trb", 
            "ethfi", "rsr", "agld", "om", "aevo", "zro", "uma", "meme", "dogs", "g", "ondo", "cati", "hmstr", 
            "eigen", "paxg", "xaut", "ena", "pendle", "xtz", "x", "ankr", "jasmy", "super", "bnx", "cake", 
            "hot", "edu", "major", "safe", "banana", "w", "move", "strk", "zil", "metis", "cookie", "cgpt", 
            "turbo", "s", "zec", "inj", "dexe", "ath", "neiro", "bonk", "morpho"
        ],
        
        # API Authorization Token. SECURITY: REPLACE WITH YOUR ACTUAL KEY
        "token": "YOUR_NOBITEX_API_TOKEN",
        
        # Exchange platform transaction fee percentage (0.0015 represents 0.15%)
        "ex_fee": 0.0015,
        
        # Account USDT balance tracking for simulation/execution
        "my_usdt_balance": 5.5,  # Alternative templates: #11
        
        # Minimum USDT required to initiate any purchase
        "min_usdt": 5.0,  # Alternative templates: #11.1
        
        # Minimum hold duration (seconds) before allowed to initiate a sell
        "min_sell_time_diff": 1200,  # Alternative hold-times: #180, #300
        
        # Maximum hold duration (seconds) before a time exit triggers
        "max_sell_time_diff": 3600,  # Max hold -> 1 hour (3600 seconds)
        
        # Minimal price spread percentage required to execute a buy (0.009 represents 0.9%)
        "price_diff": 0.009,  # Alternative spreads: #0.01
        
        # Tolerance coefficient multiplier for trailing stop loss
        "stop_loss_tolerance": 0.5,  # Alternative coefficients: #0.25
        
        # Consecutive positive price updates required to verify an upward price trend
        "increase_price_counter": 3,  # Alternative limits: #1, #3, #7
        
        # Maximum number of rolling log files to keep per pair
        "max_log_file": 3,
        
        # Maximum size of each individual log file in bytes (3MB)
        "max_log_file_size": 3145728
    }

    return variables