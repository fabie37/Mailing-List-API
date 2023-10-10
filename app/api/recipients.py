import hashlib
import datetime
from json import loads
from mongoengine import Document, StringField, EmailField, DateTimeField, signals
from mongoengine.errors import MongoEngineException, NotUniqueError
from app.api.exceptions import generate_error_response
from app.env import SALT
from app.api.middleware import middleware

def get_json_from_document(document):
    """
        Get's json string format from document
    """
    recipient_fields_and_values = document.to_json()
    return loads(recipient_fields_and_values)


def generate_hash_from_email_and_salt(email):
    """
        Given an email, return the hash of the email with salt
    """
    recipient_hash = hashlib.sha256()
    recipient_hash.update(bytes(email, 'UTF-8'))
    recipient_hash.update(bytes(SALT, 'UTF-8'))
    return recipient_hash.hexdigest()

@middleware(signals.post_init)
def post_init_recipient_hash_email(_sender, document):
    """
        hash_email : Middleware

        Hashes the email field within the Recipients Doucment.
        This happens post initialisation, as per the middleware handler. 
    """
    if (document.email):
        document.hash = generate_hash_from_email_and_salt(document.email)

@post_init_recipient_hash_email.apply
class Recipients(Document):
    """
        Recipients: Document

        email : email of recipient
        hash  : hash of email for removal purposes
    """
    email = EmailField(required=True, max_length=254, unique=True)
    hash = StringField(allow_none=True, min_length=64, max_length=64)
    joined = DateTimeField(default=datetime.datetime.now())
    meta = {
        'indexes': [
            'hash'
        ]
    }

def construct_response(data, http_code):
    """
        Returns a standard api response upon success
    """
    return {
        "success":True,
        "payload":data
    }, http_code

def get_all_recipients():
    """
        Returns a list of all recipients found in db
    """
    all_recipients = [loads(recipient.to_json()) for recipient in Recipients.objects()]
    return construct_response(all_recipients, 200)

def post_a_recipient(validated_json_data):
    """
        Inserts a new recipient into mail list
    """
    try:
        recipient = Recipients(**validated_json_data)
        recipient.save()
        returnable_json = get_json_from_document(recipient)
        return construct_response(returnable_json, 200)
    except MongoEngineException as exc:
        print(exc.args[0])
        return generate_error_response("Request was denied.", 400)

def delete_a_recipient(hash):
    """
        Provided a delete hash, remove recipient from DB
    """
    try:
        recipient = Recipients.objects.get(hash=hash)
        returnable_json = get_json_from_document(recipient)
        recipient.delete()
        return construct_response(returnable_json, 200)
    except MongoEngineException as exc:
        print(exc)
        return generate_error_response("Unable to remove recipient", 400)

