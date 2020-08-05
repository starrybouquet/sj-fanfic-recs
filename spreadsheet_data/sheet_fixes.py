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
        pass

def get_ffn_links_from_html(filename, recs, recs_local):
    f = open(filename, 'r')
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    faves = soup.find_all('div', attrs={'class': 'z-list favstories'})

    names = recs.col_values(1)

    f = open('sheet_manual_fix.txt', 'w')

    num_added = 1
    for fav in faves:
        if num_added % 80 == 0:
            print('we have been through {} pausing 2 min'.format(num_added))
            time.sleep(120)
        title = fav['data-title']
        if '\\' in title:
            title = title.replace('\\', '%27', 1)
        if '\'' in title:
            title = title.replace('\'', '%27')
        if ',' in title:
            title = title.replace(',', '%2C')
        try:
            row_index = names.index(title)
            if recs_local[row_index][8] == 'FF.net':
                print('we found {}'.format(title))
                recs.update_cell(row_index+1, 4, fav.a.get('href'))
                print('replaced it with {}'.format(fav.a.get('href')))
                print()
                num_added += 1
        except Exception as e:
            print(e)
            print('error; wrote to file')
            f.write('{}\n'.format(title))
    f.close()

recs, recs_local = get_recs_spreadsheet()
get_ffn_links_from_html('starrybouquet_ffn.html', recs, recs_local)
