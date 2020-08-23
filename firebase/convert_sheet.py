import time

from my_utils import get_spreadsheets, get_root_firebase, split_by_commas


def get_fic_dict(fic_data_row, filter_legend, rownum):
    '''Gives dict of fic data given row number in spreadsheet

    Parameters
    ----------
    rownum : int
        rownum in SJ Masterlist

    Returns
    -------
    dict
        Description of returned object.

    '''
    fic_data = {'id': 'S{}'.format(rownum),
                'title': fic_data_row[0],
                'author': fic_data_row[1],
                'link': fic_data_row[3],
                'description': fic_data_row[2],
                'site': fic_data_row[8],
                'tag_ids': '',
                'reccer': fic_data_row[9]  # FINISH DECIDING WHAT ELSE GOES HERE
                }

    fictags = []
    for col_index in range(5, 8):
        fictags.extend(split_by_commas(fic_data_row[col_index]))

    filters_applicable = [legendrow[0] for legendrow in filter_legend if len(set(fictags) & set(legendrow[2])) > 0]
    fic_data['tag_ids'] = str(filters_applicable)

    return fic_data


def create_filter_item(filter_data_row):

    if filter_data_row[3] != 'y':
        print()
        print(filter_data_row)
        to_include = str(input('This row is not on the site yet. Press i to include in the database anyway or anything else to skip: '))
        if to_include != 'i':
            return

    filter_dict = {'id': filter_data_row[0],
                   'title': filter_data_row[1],
                   'type': filter_data_row[4],
                   'submenu': filter_data_row[5],
                   'subtag_ids': filter_data_row[2]}

    return filter_dict


def push_to_firebase(root, section_name, data_dict):
    '''Push dict to firebase given section and firebase root

    Parameters
    ----------
    root : firebase db
    section_name : str
        name of section in database. 'fics' or 'filters'
    data_dict : dict
        Dict of data to insert

    Returns
    -------
    firebase entry
        Returns new entry as a firebase object

    '''

    json_dict = {}
    for key, value in data_dict:
        if type(value) != "str":
            json_dict[key] = str(value)
        else:
            json_dict[key] = value

    section = root.equal_to(section_name).get()

    new_entry = section.push(json_dict)

    return new_entry


root = get_root_firebase()
[recs, legend, recs_local, legend_local, converted_legend] = get_spreadsheets()
counter = 0
for row in legend_local:
    filter_dict = create_filter_item(row)
    push_to_firebase(root, 'filters', filter_dict)
    counter += 1
    print('Have added {} filter rows.'.format(counter))
print()
counter = 0
for i in range(len(recs_local)):
    fic_data = get_fic_dict(recs_local[i], legend_local, i+1)
    push_to_firebase(root, 'fics', fic_data)
    counter += 1
    print('Have added {} fics.'.format(counter))
print()
