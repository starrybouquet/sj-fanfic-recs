import time
import pickle
import sys

import AO3
import ffnet

from bs4 import BeautifulSoup
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from classes import Fic, Author

def get_recs_spreadsheet():
    '''Get recs spreadsheets from Google

    Returns
    -------
    recs
        gsheet sheet object
    recs_local
        list of lists version of gsheet sheet

    '''
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    print('credentials authorized.')

    recs = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(1)

    recs_local = recs.get_all_values()

    return recs, recs_local

def add_links_from_works(filename, recs, recs_local):
    works = pickle.load(open(filename, 'rb'))

    for work in works:
        
