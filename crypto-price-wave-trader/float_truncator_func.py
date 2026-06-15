"""
This module provides functionality to truncate floating-point numbers 
to a specified decimal precision without rounding up.
"""


def float_truncator_func(float_number, truncate_value, mode="float"):
    """
    Truncates a floating-point number to a specified number of decimal places.
    
    Parameters:
    - float_number (float): The number to truncate.
    - truncate_value (int): The number of decimal places to keep.
    - mode (str): 'float' (default) returns float, 'string' returns a formatted string.
    
    Examples:
    - float_truncator_func(35.9875674, 3) -> 35.987 (float)
    - float_truncator_func(132.897642141, 9, "string") -> "132.897642141" (string)
    """
    # Shift decimal point right, convert to integer to drop extra decimals, and shift left back
    factor = 10 ** truncate_value
    truncated = int(float_number * factor) / factor

    if mode == "float":
        return truncated
    if mode == "string":
        # Format the float to string using exact precision padding
        return f"{truncated:.{truncate_value}f}"


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# a = 342 / 12395830453
# print(float_truncator_func(a, 9, "string"))