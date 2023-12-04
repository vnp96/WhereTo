"""
Helper functions for the website
"""

def parse_postcode(postcode):
    assert(isinstance(postcode, str))
    parsed_postcode = postcode.replace(" ", "")
    return parsed_postcode
