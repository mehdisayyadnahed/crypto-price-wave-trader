"""
This module provides a utility function to validate strings against 
regular expression patterns using case-insensitive matching.
"""

import re


def use_regex_func(input_string, string_pattern):
    """
    Compiles the specified regex pattern with case-insensitive flag and 
    matches it against the input string. Returns a Match object if matched, otherwise None.
    
    Example:
    use_regex_func("ADAUSDT", "[A-Z]+USDT") -> <re.Match object; span=(0, 7), match='ADAUSDT'>
    """
    # Compile the raw regex pattern safely with case-insensitivity enabled
    pattern = re.compile(string_pattern, re.IGNORECASE)

    # Perform matching from the beginning of the string and return the result
    return pattern.match(input_string)


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# string_pattern = "[A-Z]+USDT" 
# print(use_regex_func("ADAUSDT", string_pattern))