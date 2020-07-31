import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find workbook and open sheets
recs = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(1)
legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

# def update_local_copies():
#     global recs_local = recs.get_all_values()
#     global legend_local = legend.get_all_values()
#     global first_blank_line = recs.col_values(1).index('')+1
#     global converted_legend = convert_legend_to_multiple_tags(legend_local)
#     global first_blank_legend_line = legend.col_values(1).index('')+1

def html_from_url(url):
    '''uses requests to get html in str form (for BeautifulSoup) given a url'''
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return r.text


def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return string.partition(", ")

def update_local_copies():
    recs_local = recs.get_all_values()
    legend_local = legend.get_all_values()
    first_blank_line = recs.col_values(1).index('')+1
    converted_legend = convert_legend_to_multiple_tags(legend_local)
    first_blank_legend_line = legend.col_values(1).index('')+1


def convert_legend_to_multiple_tags(filterlegend):
    '''convert_legend_to_multiple_tags(list) --> list
    converts each row in a legend that says, ex. ['f9', 'season 9, season 10, post-series']
    to a list ['f9', [season 9, season 10, post-series]]'''
    newlegend = []
    for row in filterlegend:
        newlegend.append([row[0], row[1], split_by_commas(row[2])])
    return newlegend

recs_local = recs.get_all_values()
legend_local = legend.get_all_values()
converted_legend = convert_legend_to_multiple_tags(legend_local)

first_blank_line = len(recs.col_values(1))+1
first_blank_legend_line = len(legend.col_values(1))+1

def add_filters(rownum):
    '''add filters to recs sheet (NOT DATA ENTRY) based on categories/eps/seasons entered in doc (manually)'''
    fictags = []
    for col_index in range(5,8):
        fictags.extend(split_by_commas(recs_local[rownum-1][col_index]))

    filters_applicable = [legendrow[0] for legendrow in converted_legend if len(set(fictags) & set(legendrow[2])) > 0]
    filters_string = ' '.join(filters_applicable)
    recs.update('E{}'.format(rownum), filters_string)

    return filters_applicable

def update_filter_legend():
    alltags = []
    for col in range(6,9):
        alltags.extend(recs.col_values(col))

    unique_tags = set(alltags)

    tag_exists = False
    for tag in unique_tags:
        for row in converted_legend:
            if tag in row[2]:
                tag_exists = True
                break
        if not tag_exists:
            new_filter_name = str(input("The tag {} does not have a filter associated yet. Please enter filter name or 'skip' to skip: "))
            if new_filter_name == "skip":
                continue
            else:
                filterrow = first_blank_legend_line
                legend.update('A{0}:C{0}'.format(filterrow), [filterrow-1, new_filter_name, [tag]])
                first_blank_legend_line += 1

    update_local_copies()
