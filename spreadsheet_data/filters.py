import gspread
from oauth2client.service_account import ServiceAccountCredentials


def html_from_url(url):
    '''uses requests to get html in str form (for BeautifulSoup) given a url'''
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return r.text

def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return [s.strip() for s in string.split(", ")]

def get_spreadsheets():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find workbook and open sheets
    recs = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(1)
    legend = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(2)

    recs_local = recs.get_all_values()
    legend_local = legend.get_all_values()

    converted_legend = convert_legend_to_multiple_tags(legend_local)

    return [recs, legend, recs_local, legend_local, converted_legend]


def convert_legend_to_multiple_tags(filterlegend):
    '''convert_legend_to_multiple_tags(list) --> list
    converts each row in a legend that says, ex. ['f9', 'season 9, season 10, post-series']
    to a list ['f9', [season 9, season 10, post-series]]'''
    newlegend = []
    for row in filterlegend:
        newlegend.append([row[0], row[1], split_by_commas(row[2])])
    return newlegend

def add_filters(rownum, recs, recs_local, converted_legend):
    '''add filters to recs sheet (NOT DATA ENTRY) based on categories/eps/seasons entered in doc (manually)'''
    fictags = []
    for col_index in range(5,8):
        fictags.extend(split_by_commas(recs_local[rownum-1][col_index]))

    filters_applicable = [legendrow[0] for legendrow in converted_legend if len(set(fictags) & set(legendrow[2])) > 0]
    filters_string = ' '.join(filters_applicable)
    recs.update('E{}'.format(rownum), filters_string)

    return filters_applicable

def update_filter_legend(sheet_data):
    '''Short summary.

    Parameters
    ----------
    sheet_data : list
        Data from get_spreadsheets in order [recs, legend, recs_local, legend_local, converted_legend]

    Returns
    -------
    type
        Description of returned object.

    '''
    # NEED TO USE SHEET_DATA INSTEAD OF GLOBAL VARS
    recs = sheet_data[0]
    legend = sheet_data[1]
    recs_local = sheet_data[2]
    legend_local = sheet_data[3]
    converted_legend = sheet_data[4]
    print(converted_legend)
    print()
    print()

    first_blank_legend_line = len(legend.col_values(1))+1

    alltags = []
    for row in recs_local:
        rowtags = row[5] + ', ' + row[6] + ', ' + row[7]
        alltags.extend(split_by_commas(rowtags))

    unique_tags = set(alltags)
    print("Got all tags.")
    print()

    for tag in unique_tags:
        tag_exists = False
        for row in converted_legend:
            if tag in row[2]:
                tag_exists = True
                break
        if not tag_exists:
            print("The tag {} does not have a filter associated yet.".format(tag))
            new_filter_name = str(input("Please enter 's' if the filter name should be the same as the tag name, 'e' if the filter name should be the episode without the numbering, the correct filter name, or 'x' to skip: ".format(tag)))
            if new_filter_name == "x":
                continue
            elif new_filter_name == 's':
                filterrow = first_blank_legend_line
                legend.update('A{0}:C{0}'.format(filterrow), [['f{}'.format(filterrow-1), tag, tag]])
                first_blank_legend_line += 1
            elif new_filter_name == 'e':
                filterrow = first_blank_legend_line
                name = tag[tag.find(' ')+1:]
                legend.update('A{0}:C{0}'.format(filterrow), [['f{}'.format(filterrow-1), name, tag]])
                first_blank_legend_line += 1
            else:
                filterrow = first_blank_legend_line
                legend.update('A{0}:C{0}'.format(filterrow), [['f{}'.format(filterrow-1), new_filter_name, tag]])
                first_blank_legend_line += 1


sheetdata = get_spreadsheets()
for r in range(160, 231):
    add_filters(r, sheetdata[0], sheetdata[2], sheetdata[4])
