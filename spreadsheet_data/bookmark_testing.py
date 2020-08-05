import AO3
import time
from classes import Fic
from reader import Reader
import pickle

def get_works_from_bookmarks(username, mine=False):
    '''
    Returns list of Works, one per bookmark
    '''
    if mine:
        pw = str(input("Please input password: "))
        session = AO3.Session("starrybouquet", pw)
        bookmarks = session.get_bookmarks()
    else:
        reader = Reader(username)
        bookmarks = reader.get_bookmarks()

    bookmarked_works = []
    broken_ids = []
    for work in bookmarks:
        if len(bookmarked_works) % 20 == 0 and len(bookmarked_works) != 0:
            print('Pausing for 2 min; we have been through {} bookmarks'.format(len(bookmarked_works)))
            time.sleep(120)
        try:
            work.reload()
            try:
                if work.fandoms[0] == "Stargate SG-1":
                    bookmarked_works.append(Fic(work.url, 'starrybouquet', existingAO3Work=work))
                    print('Added work {}'.format(work.title))
            except:
                broken_ids.append("{0} (id {1})".format(work.title, work.workid))
                print("Work had no fandom, id was {}".format(work.workid))
        except:
            broken_ids.append(work.workid)
            print("Work was restricted, skipping. Work id was {}".format(work.workid))
    return bookmarked_works, broken_ids

bookmarks, please_check_these_works = get_works_from_bookmarks('lilianbones')
for work in bookmarks:
    print(work.get_title())
pickle.dump(bookmarks, open('bookmark_data.p', 'wb'))
errorlog = open('works_with_errors.txt', 'w')
errorlog.write(str(please_check_these_works))
errorlog.close()
