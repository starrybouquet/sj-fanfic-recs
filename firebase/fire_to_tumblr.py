from firebase_admin import db

from my_utils import get_root_firebase, init_tumblr_client, get_spreadsheets
from convert_sheet import get_fic_dict

# # # FIREBASE FUNCTIONS # # #


def find_fic_in_firebase(title, author, orderedByTitleList=None, id=''):
    if orderedByTitleList:
        title_matches = orderedByTitleList.equal_to(title).get()
    else:
        ref = db.reference('test_fics')
        title_matches = ref.order_by_child('Title').equal_to(title).get()
    for key, fic_title in title_matches.items():
        fic = db.reference('test_fics/{}'.format(key)).get()
        if fic['Author'] == author:
            return key, fic
    return


def get_fic_categories(fic_data, source="firebase", legend_firstcol=[], legend_local=[]):
    if source == "firebase":
        # actually needs to be written, clearly
        return ['one tag', 'two tag', 'red tag', 'blue tag']

    elif source == "gsheet":
        tags = []
        for tag_id in fic_data['tag_ids']:
            row_index = legend_firstcol.index(tag_id)
            tags.append(legend_local[row_index][1])
        return tags
# # # TUMBLR FUNCTIONS # # #

def post_fic(fic_data, fic_id, client, state="queued", source="firebase", legend_firstcol=[], legend_local=[]):
    post_body = '<h1><a href="'
    post_body += fic_data['Link']
    post_body += '">'
    post_body += fic_data['Title']
    post_body += "</a></h1><br><p>"
    post_body += fic_data['Description']
    post_body += "</p>"

    slug = ''.join([char for char in fic_data['Title'] if char in 'abcdefghijklmnopqrstuvwxyz-'])
    slug += "_" + fic_id

    if source == "firebase":
        tags = get_fic_categories(fic_data, source)
    elif source == "gsheet":
        tags = get_fic_categories(fic_data, source, legend_firstcol=legend_firstcol, legend_local=legend_local)
    print('Created post. Body html below:')
    print(post_body)

    client.create_text('sjficlist-dev.tumblr.com',
                       state=state, slug=slug, body=post_body, format='html', tags=tags)

    return slug


def row_to_post(rownum, recs_local, legend_firstcol, legend_local, client):
    row_data = recs_local[rownum-1]
    fic_data = get_fic_dict(row_data, legend_local, rownum)
    print()
    print(fic_data)
    post = str(input('queue fic? y to continue: '))
    fic_id = "S{}".format(rownum)
    slug = ""
    if post == "y":
        slug = post_fic(fic_data, fic_id, client, source="gsheet", legend_firstcol=legend_firstcol, legend_local=legend_local)
    return slug


[recs, legend, recs_local, legend_local, converted_legend] = get_spreadsheets()

client = init_tumblr_client(blognum=1)
legend_firstcol = legend.col_values(1)

for row in range(2, 5):
    row_to_post(row, recs_local, legend_firstcol, legend_local, client)

# # i am an idiot who did not understand newlines. this works now.
# root = get_root_firebase()
# key, fic = find_fic_in_firebase('Thoughts', 'starrybouquet')
# print()
# print(fic)
# post = input('queue fic? y to continue: ')
# if post == 'y':
#     post_fic(fic, key, client)
