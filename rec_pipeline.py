# Getting Recs from Tumblr
# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.

import pytumblr
from ao3 import AO3
from ao3.works import RestrictedWork
import ffnet
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ao3 = AO3()


class Link(object):
    '''link from html rec list'''

    def __init__(self, raw_link):

        self.link = raw_link
        self.id = '-1'

        if sites['ao3'] in self.link:
            self.site = 'ao3'
        elif sites['ffn'] in self.link:
            self.site = 'ffn'
        else:
            self.site = 'other'

    def __str__(self):
        return self.link

    def get_site(self):
        return self.site

    def get_id(self):
        return self.id

    def get_link(self):
        return self.link

class Work(Link):
    '''works from ao3 or ffn'''

    def __init__(self, raw_link, reccer, ao3=None):
        super().__init__(raw_link)
        self.reccer = reccer
        self.url = raw_link
        if self.site == 'ao3':
            self.id = self.link.partition('/works/')[2]
            try:
                me = ao3.work(id=self.id)
            except RestrictedWork:
                self.title = 'restricted; please enter manually'
                self.desc = 'restricted; please enter manually'
                self.author = 'restricted; please enter manually'
                self.rating = 'restricted; please enter manually'
            self.title = me.title
            self.desc = self.strip_html(me.summary)
            self.author = me.author # may want to connect to author class
            if (me.rating[0]=='Mature') or (me.rating[0]=='Explicit'):
                self.isAdult = True
            else:
                self.isAdult = False

        elif self.site == 'ffn':
            self.id = self.link.partition('/s/')[2].partition('/')[0]
            me = ffnet.Story(id=self.id)
            me.download_data()
            self.title = me.title
            self.desc = me.description
            self.author = me.author_id
            if me.rated == 'M':
                self.isAdult = True
            else:
                self.isAdult = False

    def __str__(self):
        return "Work '{}'' at {}".format(self.title, self.link)

    def get_title(self):
        return self.title

    def get_desc(self):
        return self.desc

    def get_reccer(self):
        return self.reccer

    def get_url(self):
        return self.url

    def strip_html(self, summary):
        soup = BeautifulSoup(summary, 'html.parser')
        return soup.get_text()

class Author(Link):
    '''author from ao3 or ffn'''

    def __init__(self, raw_link):
        super().__init__(raw_link)
        if self.site == 'ao3':
            self.id = self.link.partition('/users/')[2].partition('/')[0]
        elif self.site == 'ffn':
            self.id = self.link.partition('/u/')[2].partition('/')[0]

    def find_name(self):
        '''find name on web'''
        pass

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find workbook and open sheets
recs = client.open("SJ Masterlist Imported").get_worksheet(1)
legend = client.open("SJ Masterlist Imported").get_worksheet(2)
data_out = client.open("SJ Masterlist Imported").get_worksheet(0)

# # Extract and print all of the values
# all_recs = recs.get_all_values()
# print(list_of_values)

# From tumblr API console https://api.tumblr.com/console
# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
  'yIn5BsgXKPGlR4OoHsFV6jT4KC0PeJQ3cGe0mQvSGbT8QGA95k',
  'qbET4dR9xMAntDJTwemIlZucJkpucS2Tm0CZlRdq6yOpvdbozt',
  'JtfABFskd8FpPmptIbNnUJdaaZICuoJHafcGy4YAi8luiBRzRX',
  'vtVGOENMCaforhI1kUniUlDYjWCASI2eiKzOhlBkuIheQPPpOw')

## post url options
# https://starrybouquet.tumblr.com/post/620329944196710401/heya-any-suggestions-for-good-affinity-fix-it
# https://samcaarter.tumblr.com/private/621914267347795968/tumblr_qchqnjlukx1r9gqxq
# https://professortennant.tumblr.com/post/175193322905/samjack-rec-list-pt-1

post_url = "https://starrybouquet.tumblr.com/post/620329944196710401/heya-any-suggestions-for-good-affinity-fix-it"

def split_by_commas(string):
    '''return list of items split by commas and stripped of whitespace'''
    return string.partition(", ")

def get_works(post_url, reccer):
    '''get works from tumblr url with links'''

    if "/post/" in post_url:
        post_url_split = post_url.partition("/post/")
    elif "/private/" in post_url:
        post_url_split = post_url.partition("/private/")

    post_username = post_url_split[0].partition("https://")[2]
    post_id = post_url_split[2].partition("/")[0]

    print("Parsing post from {}".format(post_username)) # check it worked

    post = client.posts(post_username, id=post_id)['posts'][0]
    content = post['trail'][0]['content'].split('<')
    sites = {'ao3': 'archiveofourown.org',
                'ffn': 'fanfiction.net'}

    authors = []
    works = []
    for line in content:
        if "href=" in line:
            link = line.split('"')[1]
            if ('/u/' in link) or ('/users/' in link):
                authors.append(Author(link))
            elif ('/s/' in link) or ('/works/' in link):
                works.append(Work(link, reccer))
            else:
                print('{} is invalid link'.format(link))


    return works

def add_work(work):
    '''from Work class, check the gsheet and add to recs if it's not there.
    If it's already there, add reccer if they're not already there'''
    # use link to figure out if it's already there


def add_filters(rownum):
    '''add filters based on categories/eps/seasons entered in doc (manually)'''
    pass

def add_desc(rownum):
    pass


## possible additions:
# - get some filters from tags on work
# - ??
