"""
    App.py - Main Application File

    This file contains the default associated routes for the API.
"""

import requests
import os
from mongoengine import connect
from flask import Flask, request, render_template, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_parameter_validation import ValidateParameters, Route
from app.env import MONGO_URI, PORT, LOCAL_HOST
from app.api import Recipients, get_all_recipients, post_a_recipient, delete_a_recipient
from app.api.auth import protected
from app.api.sanitisation import sanitise_json, extract_document_fields_from_json
from app.api.exceptions import json_api_parameter_validation_error_handler

app = Flask(__name__)
limiter = Limiter(get_remote_address,
                  app=app,
                  default_limits=["200 per day", "50 per hour"],
                  storage_uri= MONGO_URI
                  )

connect(db="email_db", host=MONGO_URI)

# Hack to get requests to refer to this local machine.
os.environ['NO_PROXY'] = LOCAL_HOST

"""
    Webpage Routes
"""

@app.route("/unsubscribe/<delete_hash>", methods=['GET'])
@limiter.limit("1/second", override_defaults=False)
@ValidateParameters(lambda error : render_template("unsubscribe.html", msg="User Not Found"))
def unsubscribe_get(delete_hash: str = Route(pattern=r'\b[A-Fa-f0-9]{64}\b')):
    """
        URL: /unsubscribe/delete_hash [GET]

        GET: Unsubscribes a user and returns a webpage with a message for user if successful.
        Params:
            delete_hash - Hash of user data needed to identify them in database
    """
    api_url = f'http://{LOCAL_HOST}:{PORT}/api/recipients/'+delete_hash
    req = requests.delete(api_url)
    json = req.json()
    if (not json["success"] or json["success"] is False):
        return render_template("unsubscribe.html", msg="User has already unsubscribed or is not found.")
    return render_template("unsubscribe.html", msg=f'User {json["payload"]["email"]} has unsubscribed.')

"""
    API ROUTES
"""

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
# @protected
@extract_document_fields_from_json(Recipients, ["joined", "hash", "_id"])
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
@ValidateParameters(json_api_parameter_validation_error_handler)
def recipients_delete(delete_hash: str = Route(pattern=r'\b[A-Fa-f0-9]{64}\b')):
    """
        URL: /api/recipients/<delete_hash> [DELETE]

        DELETE: Makes a post request to API to remove user from mail list.
        Params: 
            <deleteHash> : Hash Stored in database locating user's email to remove. 
    """
    return delete_a_recipient(delete_hash)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0')