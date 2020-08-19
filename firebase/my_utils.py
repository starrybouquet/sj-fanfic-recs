import pytumblr
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


### I/O UTILS ###

def init_tumblr_client():
    # From tumblr API console https://api.tumblr.com/console
    # Authenticate via OAuth
    with open('tumblr_auth.txt', 'r') as f:
        secrets = f.readlines()
    client = pytumblr.TumblrRestClient(secrets[0], secrets[1], secrets[2], secrets[3])
    return client

def get_root_firebase():
    cred = credentials.Certificate("firebase_secret.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://fir-test-project-98169.firebaseio.com/test_fics'
    })

    root = db.reference()
    return root


### PYTHON UTILS ###
def html_from_url(url):
    '''uses requests to get html in str form (for BeautifulSoup) given a url'''
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return r.text


def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return string.partition(", ")
