import requests

import pytumblr
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# # # I/O UTILS # # #

def init_tumblr_client(blognum=1):
    '''Short summary.

    Parameters
    ----------
    blognum : int
        1: sjficlist-dev.tumblr.com
        2: sjficlist-dev-2.tumblr.com
        3. idk? check if you want...

    Returns
    -------
    type
        Description of returned object.

    '''
    # From tumblr API console https://api.tumblr.com/console
    # Authenticate via OAuth
    with open('tumblr_auth_{0}.txt'.format(blognum), 'r') as f:
        secrets = [secret.strip('\n') for secret in f.readlines()]
    client = pytumblr.TumblrRestClient(secrets[0], secrets[1], secrets[2], secrets[3])
    return client


def get_root_firebase():
    cred = credentials.Certificate("firebase_secret.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://fir-test-project-98169.firebaseio.com/test_fics'
    })

    root = db.reference()
    return root


def get_recs_spreadsheet_only():
    '''Get recs spreadsheets from Google

    Returns
    -------
    recs
        gsheet sheet object
    recs_local
        list of lists version of gsheet sheet

    '''
    # use creds to create a client to interact with the Google Drive API
    sheet_url = 'https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ'
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    print('credentials authorized.')

    recs = client.open_by_url(sheet_url).get_worksheet(1)

    recs_local = recs.get_all_values()

    return recs, recs_local


def get_spreadsheets():
    '''Get all spreadsheets

    Returns
    -------
    list
        List of various sheets in various types, as shown below
        [recs, legend, recs_local, legend_local, converted_legend]

    '''
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    print('credentials authorized')

    # Find workbook and open sheets
    recs = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(1)
    legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

    recs_local = recs.get_all_values()
    legend_local = legend.get_all_values()

    converted_legend = []
    for row in legend_local:
        converted_legend.append([row[0], row[1], split_by_commas(row[2])])

    return [recs, legend, recs_local, legend_local, converted_legend]


# # # PYTHON UTILS # # #
def html_from_url(url):
    '''uses requests to get html in str form (for BeautifulSoup) given a url'''
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return r.text


def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return [s.strip() for s in string.split(", ")]
