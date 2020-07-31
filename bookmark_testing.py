import AO3
import time
from classes import Fic
import pickle

def get_works_from_bookmarks(mine=True):
    '''
    Returns list of Works, one per bookmark
    '''
    if mine:
        pw = str(input("Please input password: "))
        session = AO3.Session("starrybouquet", pw)
        bookmarks = session.get_bookmarks()

    bookmarked_works = []
    for work in bookmarks:
        if len(bookmarked_works) % 20 == 0 and len(bookmarked_works) != 0:
            print('Pausing for 2 min; we have been through {} bookmarks'.format(len(bookmarked_works)))
            time.sleep(120)
        print(type(work))
        work.reload()
        if work.fandoms[0] == "Stargate SG-1":
            bookmarked_works.append(Fic(work.url, 'starrybouquet', existingAO3Work=work))
    return bookmarked_works

bookmarks = get_works_from_bookmarks()
for work in bookmarks:
    print(work.get_title())
pickle.dump(bookmarks, open('bookmark_data.p', 'wb'))
