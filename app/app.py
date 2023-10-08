"""
    App.py - Main Application File

    This file contains the default associated routes for the API.
"""

from mongoengine import connect
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_parameter_validation import ValidateParameters, Route
from .env import MONGO_URI
from .api import Recipients, get_all_recipients, post_a_recipient, delete_a_recipient
from .api.auth import protected
from .api.sanitisation import sanitise_json, extract_document_fields
from .api.exceptions import flask_parameter_validation_error_handler



app = Flask(__name__)
limiter = Limiter(get_remote_address,
                  app=app,
                  default_limits=["200 per day", "50 per hour"],
                  storage_uri= MONGO_URI
                  )

connect(db="email_db", host=MONGO_URI)

@app.route("/api/recipients", methods=['GET'])
@limiter.limit("1/second", override_defaults=False)
@protected
def recipients_get():
    """
        (Protected)
        URL : /api/recipients [GET]

        GET: Gets the list of all recipients.
            JSON Data:
            {
                api_key : Hash Stored as Enviroment Variable on local machine. 
            }
    """
    return get_all_recipients()

@app.route("/api/recipients", methods=['POST'])
@limiter.limit("1/second", override_defaults=False)
@protected
@extract_document_fields(Recipients, ["joined", "hash", "_id"])
@sanitise_json(Recipients)
def recipients_post():
    """
        (Protected)
        URL: /api/recipients [POST]

        POST: Adds a reciepient
            JSON Data:
            {
                api_key : Hash Stored as Enviroment Variable on local machine
                email : Email address to be added to mailing list
            }
    """
    json = request.get_json()
    return post_a_recipient(json)


@app.route("/api/recipients/<delete_hash>", methods=['DELETE'])
@limiter.limit("1/second", override_defaults=False)
@ValidateParameters(flask_parameter_validation_error_handler)
def recipients_delete(delete_hash: str = Route(pattern=r'\b[A-Fa-f0-9]{64}\b')):
    """
        URL: /api/recipients/<delete_hash> [DELETE]

        DELETE: Makes a post request to API to remove user from mail list.
        Params: 
            <deleteHash> : Hash Stored in database locating user's email to remove. 
    """
    return delete_a_recipient(delete_hash)
    

