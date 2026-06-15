"""
This module provides functionality to validate the authenticity and authorization 
status of the Nobitex API token by querying the user profile endpoint.
"""

import requests as req
import json
from time import sleep

# Disable SSL insecure verification warnings caused by verify=False
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

from except_exit_func import *
from variables_func import *


def validation_token_checker_func():
    """
    Sends a GET request to the Nobitex profile endpoint using the configured API token.
    Returns True if the token is authorized and a valid user profile ID is retrieved.
    Returns False if the server returns 401 Unauthorized.
    Retries up to 3 times in case of transport or connection exceptions.
    """
    try:
        variables_func_list = variables_func()
        token = variables_func_list["token"]

        loop_counter = 0
        while True:
            try:
                url = "https://api.nobitex.ir/users/profile"
                headers = {'Authorization': 'Token ' + token}
                resp = req.get(url, headers=headers, verify=False)
                
                if resp.status_code == 401:
                    return False
                    
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    profile_id = data["profile"]["id"]
                    
                    # Ensure the profile ID exists and is not empty
                    if profile_id is not None and profile_id != "":
                        return True
                        
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


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# while True:
#     print(validation_token_checker_func())