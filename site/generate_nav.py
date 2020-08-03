from bs4 import BeautifulSoup

import gspread
from oauth2client.service_account import ServiceAccountCredentials

with open('nav_skeleton.html') as skeleton:
    soup = BeautifulSoup(skeleton, 'html.parser')

def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return [s.strip() for s in string.split(", ")]

def get_filters():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find workbook and open sheets
    legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

    legend_local = legend.get_all_values()

    converted_legend = convert_legend_to_multiple_tags(legend_local)

    return [legend, legend_local, converted_legend]

def convert_legend_to_multiple_tags(filterlegend):
    '''convert_legend_to_multiple_tags(list) --> list
    converts each row in a legend that says, ex. ['f9', 'season 9, season 10, post-series']
    to a list ['f9', [season 9, season 10, post-series], y, season]'''
    newlegend = []
    for row in filterlegend:
        newlegend.append([row[0], row[1], split_by_commas(row[2]), row[3], row[4]])
    return newlegend

def insert_season_subcategories(seasonNum, legend_local):
    '''Inserts html into soup for subcategories of season (aka episodes) given season number.

    Parameters
    ----------
    seasonNum : int
        Description of parameter `seasonNum`.

    Returns
    -------
    str
        String representation of html inserted into season.

    '''

    ep_li = []
    for row in legend_local:
        if row[4] == 'ep' and row[3] == 'y':
            html_data = []
            episode = row[2]
            if '0' in episode[4:6]:
                html_data.append(int(episode[5]))
            else:
                html_data.append(int(episode[5:6]))
            html_data.append(row[0])
            html_data.append(row[1])
        ep_li.append(html_data)

    ep_li = sort(ep_li, key=lambda x: x[0])

    season_div = soup.find(id='#{}'.format(seasonNum))
    season_div.append(soup.new_tag('ul'))
    for li in ep_li:
        wrapper = soup.new_tag('li')
        link = soup.new_tag('a', href='#', data-filter='.{}'.format(li[1]))
        link.string = li[2]
        wrapper.append(link)
        season_div.ul.append(wrapper)

    return season_div
