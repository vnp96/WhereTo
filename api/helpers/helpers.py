"""
Helper functions for the website
"""
import psycopg as db



def parse_postcode(postcode):
    assert(isinstance(postcode, str))
    parsed_postcode = postcode.replace(" ", "")
    return parsed_postcode

def querydb_postcodes():

    

