from firebase_admin import db

from my_utils import get_root_firebase, init_tumblr_client

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


def get_fic_categories(fic_data):
    # actually needs to be written, clearly
    return ['one tag', 'two tag', 'red tag', 'blue tag']

# # # TUMBLR FUNCTIONS # # #


def post_fic(fic_data, id, client, state="published"):
    post_body = '<h1><a href="'
    post_body += fic_data['Link']
    post_body += '">'
    post_body += fic_data['Title']
    post_body += "</a></h1><br><p>"
    post_body += fic_data['Description']
    post_body += "</p>"

    slug = ''.join([char for char in fic_data['Title'] if char in 'abcdefghijklmnopqrstuvwxyz-'])
    slug += "_" + id

    tags = get_fic_categories(fic_data)

    print('Created post. Body html below:')
    print(post_body)

    client.create_text('sjficlist-dev-2.tumblr.com',
                       state=state, slug=slug, body=post_body, format='html', tags=tags)

    return slug


client = init_tumblr_client(blognum=1)
print(client.info())
print(client.posts('starrybouquet.tumblr.com'))
print()
print(client.posts('sjficlist.tumblr.com'))

# so apparently the issue is that it's a sideblog. eeeeee
# root = get_root_firebase()
# key, fic = find_fic_in_firebase('Thoughts', 'starrybouquet')
# print()
# print(fic)
# post = input('post fic? y to continue: ')
# if post == 'y':
#     post_fic(fic, key, client)
