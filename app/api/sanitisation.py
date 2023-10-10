"""
    sanitisation.py

    Provides the `sanitise_json` wrapper for flask API Routes
"""

from functools import wraps
from flask import request
from mongoengine import Document, ValidationError
from mongoengine.errors import MongoEngineException
from app.api.exceptions import generate_error_response

def validate_json_using_document(document:Document):
    """
        Validates expected json input by using the MongoEngine ORM (Marshmellow)
    """
    json = request.get_json()
    document_validator = document(**json)
    document_validator.validate()


def remove_field_from_request_json(field):
    """
        Removes a field remove request json
    """
    del request.json[field]

def get_fields_not_in_document_from_request_json(document:Document):
    """
        Fields from the request json not found in document are collected and returned
        as a list
    """
    json = request.get_json()
    fields = []
    for field in json:
        if field not in document._fields:
            fields.append(field)
    return fields

def get_ignored_fields_from_request_json(ignore_fields):
    """
        Fields found in request json also found in ignore_fields list
        are collected and returned as a list
    """
    fields = []
    for field in ignore_fields:
        if field in request.json:
            fields.append(field)
    return fields

def remove_fields_from_request_not_in_document(document:Document, ignore_fields):
    """
        Iterates through the request json and removes fields not found 
        in given document. Optional : if specified, 
    """
    fields_to_remove = []
    fields_not_in_document = get_fields_not_in_document_from_request_json(document)
    fields_to_remove.extend(fields_not_in_document)
    if ignore_fields:
        fields_to_ignore = get_ignored_fields_from_request_json(ignore_fields)
        fields_to_remove.extend(fields_to_ignore)

    for field in fields_to_remove:
        remove_field_from_request_json(field)


def extract_document_fields_from_json(document: Document, ignore_fields=None):
    """
        Allows you to ignore any input that doesn't involve Document fields.
        The ignore_fields param enables you to also disregard additional fields such as DateTimeField()s 
        which are automatically added and shouldn't need to be provided.
    """
    def decorator(route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            remove_fields_from_request_not_in_document(document, ignore_fields)
            print(request.get_json())
            return route(*args, **kwargs)
        return wrapper
    return decorator

def sanitise_json(document:Document):
    """
        Santisise decorator to return only valid json objects
    """
    def decorator(route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            try:
                validate_json_using_document(document)
                return route(*args, **kwargs)
            except ValidationError as val_error:
                return generate_error_response(val_error.message, 403)
            except MongoEngineException as mongo_error:
                return generate_error_response(mongo_error.args, 400)
        return wrapper
    return decorator