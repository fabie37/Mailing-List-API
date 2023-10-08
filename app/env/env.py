"""
    env.py 

    Localised file to contain all enviroment variables.
"""
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
SALT = os.getenv('SALT')
MONGO_URI = os.getenv('MONGO_URI')
