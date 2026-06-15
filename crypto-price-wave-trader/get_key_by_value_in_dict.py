"""
This module provides a helper utility to look up a dictionary key 
by specifying its corresponding value.
"""


def get_key_by_value_in_dict(my_dict, val):
    """
    Iterates through the provided dictionary and returns the first key 
    whose value matches the specified 'val'. Returns None if no match is found.
    """
    for key, value in my_dict.items():
        if val == value:
            return key