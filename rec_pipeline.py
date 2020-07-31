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

sites = {'ao3': 'archiveofourown.org',
            'ffn': 'fanfiction.net'}

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

    def get_author(self):
        return self.author

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
recs = client.open("SJ Masterlist Data").get_worksheet(1)
legend = client.open("SJ Masterlist Data").get_worksheet(2)

recs_local = recs.get_all_values()
legend_local = legend.get_all_values()
converted_legend = convert_legend_to_multiple_tags(legend_local)

first_blank_line = recs.col_values(1).index('')+1
first_blank_legend_line = legend.col_values(1).index('')+1

def update_local_copies():
    global recs_local = recs.get_all_values()
    global legend_local = legend.get_all_values()
    global first_blank_line = recs.col_values(1).index('')+1
    global converted_legend = convert_legend_to_multiple_tags(legend_local)
    global first_blank_legend_line = legend.col_values(1).index('')+1


def convert_legend_to_dict(filterlegend):
    '''convert_legend_to_multiple_tags(list) --> list
    converts each row in a legend that says, ex. ['f9', 'season 9, season 10, post-series']
    to a list ['f9', [season 9, season 10, post-series]]'''
    newlegend = {}
    for row in filterlegend:
        newlegend.append(row[0], row[1], split_by_commas(row[2]))
    return newlegend

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
    link_matches = recs.findall(work.get_url()) #probably need to check that links are consistent

    if len(link_matches) > 0: # fic is already there
        workrow = link_matches[0].row
        reccers = recs_local[workrow-1][9]
        if work.get_reccer() not in reccers:
            newvalue = reccers + ", " + work.get_reccer()
            recs.update_cell(workrow, 10, newvalue)

    elif len(link_matches) == 0: # need to add fic
        workrow = first_blank_line
        recs.update('A{0}:J{0}'.format(workrow), [work.get_title(), work.get_author(), work.get_desc(), work.get_url(), '', '', '', '', work.get_site(), work.get_reccer()])
        first_blank_line += 1


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

    update_local_copies()





## possible additions:
# - get some filters from tags on work
# - ??
