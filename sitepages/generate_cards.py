from bs4 import BeautifulSoup
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date

episodeList = pd.read_csv('sg1-eps.csv', sep=',', header=None)
print(episodeList.head())


def get_filters():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('../spreadsheet_data/client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find workbook and open sheets
    legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

    legend_local = legend.get_all_values()

    return [legend, legend_local]


def find_in_episode_list(episodeData):
    '''pass'''
    contains = episodeList.loc[episodeList[1].str.contains(episodeData[1])]
    if len(contains) > 1:
        contains = contains.iloc[0]
    return int(contains[0])


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

    ep_tags = []
    for row in legend_local:
        if row[4] == 'ep' and row[3] == 'y' and 's0{}'.format(seasonNum) in row[2]:
            html_data = [row[0], row[1]]
            ep_tags.append(html_data)

    ep_tags.sort(key=find_in_episode_list)

    season_div = soup.find(id='s{}'.format(seasonNum))
    season_div.append(soup.new_tag('ul'))
    for li in ep_li:
        wrapper = soup.new_tag('li')
        link = soup.new_tag('button', href='#/')
        link['onclick'] = "filterSelection('{}')".format(li[0])
        link.string = li[1]
        wrapper.append(link)
        season_div.ul.append(wrapper)

    return season_div



with open('nav_skeleton.html') as skeleton:
    soup = BeautifulSoup(skeleton, 'html.parser')
sheet_legend = get_filters()

for season in range(1,9):
    insert_season_subcategories(season, sheet_legend[1])

insert_categories(sheet_legend[1])
insert_types(sheet_legend[1])

d = date.today()
html_out = str(soup)
output = open('generated_nav_v2_{}.html'.format(d.isoformat()), 'w')
output.write(html_out)
output.close()
