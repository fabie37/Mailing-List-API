"""
    auth.py

    Provides the `protected` wrapper for flask API routes.
"""
from functools import wraps
from flask import request
from ..env import API_KEY
from .exceptions import APIAuthError, generate_error_response


def get_api_key_from_request():
    """
        Checks if API exists in JSON request document.
    """
    try:
        given_api_key = request.get_json()['API_KEY']
        return given_api_key
    except Exception as exc:
        raise APIAuthError("API_KEY Entry not found", 400) from exc

def has_provided_correct_api_key(given_api_key:str):
    """
        Checks if API_KEY given is equal to that of the enviroment
    """
    if str(given_api_key) != str(API_KEY):
        raise APIAuthError("API_KEY is Invalid", 401)
    return True

def remove_api_key_from_request():
    """
        Removes api key from request
    """
    del request.json['API_KEY']


def protected(route):
    """Protected decorator to validate requests to ensure they are using the correct API key."""
    @wraps(route)
    def wrapper(*args, **kwargs):
        try:
            unchecked_api_key = get_api_key_from_request()
            has_provided_correct_api_key(unchecked_api_key)
            remove_api_key_from_request()
            return route(*args, **kwargs)
        except APIAuthError as auth_error:
            print(auth_error.message)
            return generate_error_response(auth_error.message, auth_error.http_code)
    return wrapper