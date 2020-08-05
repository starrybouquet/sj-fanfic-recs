import ffnet
from classes import Fic
import time
import pickle

def get_faves_from_user(user_url, reccer):
    author = ffnet.User(url=user_url)
    author.download_data()

    favorite_works = []

    for story in author.favorite_stories:
        # story.download_data()
        if len(favorite_works) % 100 == 0 and len(favorite_works) != 0:
            print('Pausing for 2 min; we have been through {} stories'.format(len(favorite_works)))
            time.sleep(120)
        if 'Stargate: SG-1' in story.fandoms:
            print('Found SG-1 story {}'.format(story.title))
            favorite_works.append(Fic('', reccer, existingFFNStory=story))

    return favorite_works

faves = get_faves_from_user('https://www.fanfiction.net/u/12066707/', 'starrybouquet')

for work in faves:
    print(work.get_title())

pickle.dump(faves, open('ffn_faves_data.p', 'wb'))
