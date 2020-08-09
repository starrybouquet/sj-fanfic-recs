from bs4 import BeautifulSoup

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date


def get_filters():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('../spreadsheet_data/client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find workbook and open sheets
    legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

    legend_local = legend.get_all_values()

    return [legend, legend_local]

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
        if row[4] == 'ep' and row[3] == 'y' and 's0{}'.format(seasonNum) in row[2]:
            html_data = []
            episode = row[2]
            if episode[5].isdigit():
                html_data.append(int(episode[4:5]))
            else:
                html_data.append(int(episode[4]))
            html_data.append(row[0])
            html_data.append(row[1])
            ep_li.append(html_data)

    ep_li = sorted(ep_li, key=lambda x: x[0])

    season_div = soup.find(id='s{}'.format(seasonNum))
    season_div.append(soup.new_tag('ul'))
    for li in ep_li:
        wrapper = soup.new_tag('li')
        link = soup.new_tag('button')
        link['class'] = 'base-btn'
        link['onclick'] = "filterSelection('{}')".format(li[1])
        link.string = li[2]
        wrapper.append(link)
        season_div.ul.append(wrapper)

    return season_div

def create_filter_tag(filternum, name, parent):
    wrapper = soup.new_tag('li')
    link = soup.new_tag('button')
    link['class'] = 'base-btn'
    link['onclick'] = "filterSelection('{}')".format(filternum)
    link.string = name
    wrapper.append(link)
    parent.append(wrapper)
    return wrapper

def create_dropdown(parent_atrrs_to_find, div_id):
    button = soup.find(attrs=parent_atrrs_to_find)
    button['class'] = 'right-menu-btn'
    button['href'] = '#{}'.format(div_id)
    div = soup.new_tag('div', id=div_id)
    div['class'] = 'subcategory'
    button.insert_after(div)
    return div

def insert_categories(legend_local):
    categories = []
    aus = []
    ars = []
    holidays = []
    tropes = []
    for row in legend_local:
        if row[4]=='category' and row[3]=='y':
            html_data = [row[0], row[1]]
            if 'ar' in row[5]:
                ars.append(html_data)
            elif 'au' in row[5]:
                aus.append(html_data)
            elif 'holiday' in row[5]:
                holidays.append(html_data)
            elif 'trope' in row[5]:
                tropes.append(html_data)
            else:
                categories.append(html_data)

    categories = sorted(categories, key=lambda x: x[1])
    aus = sorted(aus, key=lambda x: x[1])
    ars = sorted(ars, key=lambda x: x[1])
    holidays = sorted(holidays, key=lambda x: x[1])
    tropes = sorted(tropes, key=lambda x: x[1])

    category_dropdown = soup.find(id='categories')
    category_dropdown.append(soup.new_tag('ul'))

    # tropes
    wrapper = soup.new_tag('li')
    trope_header = soup.new_tag('a', id='trope-btn')
    trope_header.string = 'Cliches'
    wrapper.append(trope_header)
    category_dropdown.ul.append(wrapper)
    trope_div = create_dropdown({'id': 'trope-btn'}, 'tropes')
    trope_div.append(soup.new_tag('ul'))
    for li in tropes:
        create_filter_tag(li[0], li[1], trope_div.ul)

    # general categories
    for li in categories:
        create_filter_tag(li[0], li[1], category_dropdown.ul)

    # add AU dropdown
    au_div = create_dropdown({"onclick": "filterSelection('f41')"}, 'au')
    # all_aus_filter = create_filter_tag('f41', "All Alternate Universes", au_div)
    au_div.append(soup.new_tag('ul'))
    # au_div.ul.append(all_aus_filter)
    # add AUs
    for li in aus:
        create_filter_tag(li[0], li[1], au_div.ul)

    # same for ARs
    ar_div = create_dropdown({"onclick": "filterSelection('f75')"}, 'ar')
    # all_ars_filter = create_filter_tag('f75', "All Alternate Realities", ar_div)
    ar_div.append(soup.new_tag('ul'))
    # ar_div.ul.append(all_ars_filter)
    # add AUs
    for li in ars:
        create_filter_tag(li[0], li[1], ar_div.ul)

    # holidays
    holiday_div = create_dropdown({"onclick": "filterSelection('f86')"}, 'holidays')
    holiday_div.append(soup.new_tag('ul'))
    for li in holidays:
        create_filter_tag(li[0], li[1], holiday_div.ul)

    return category_dropdown



with open('nav_skeleton.html') as skeleton:
    soup = BeautifulSoup(skeleton, 'html.parser')
sheet_legend = get_filters()

for season in range(1,9):
    insert_season_subcategories(season, sheet_legend[1])

insert_categories(sheet_legend[1])

d = date.today()
html_out = str(soup)
output = open('generated_nav_v2_{}.html'.format(d.isoformat()), 'w')
output.write(html_out)
output.close()
