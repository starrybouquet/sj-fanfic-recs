# Getting Recs from Tumblr
# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.

import pytumblr
import AO3
import ffnet

from bs4 import BeautifulSoup
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time
import pickle

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

class Fic(Link):
    '''works from ao3 or ffn'''

    def __init__(self, raw_link, reccer, existingAO3Work=False):
        super().__init__(raw_link)
        self.reccer = reccer
        self.url = raw_link
        if existingAO3Work:
            self.title = existingAO3Work.title
            self.desc = existingAO3Work.summary
            self.author = existingAO3Work.authors[0] # may want to connect to author class
            if (existingAO3Work.rating=='Mature') or (existingAO3Work.rating=='Explicit'):
                self.isAdult = True
            else:
                self.isAdult = False
        else:
            if self.site == 'ao3':
                self.id = AO3.utils.workid_from_url(raw_link)
                # try:
                #     me = AO3.Work(self.id)
                # MUST PUT BACK IN AT SOME POINT
                # except RestrictedWork:
                #     self.title = 'restricted; please enter manually'
                #     self.desc = 'restricted; please enter manually'
                #     self.author = 'restricted; please enter manually'
                #     self.rating = 'restricted; please enter manually'
                me = AO3.Work(self.id)

                self.title = me.title
                self.desc = self.strip_html(me.summary)
                self.author = me.authors[0] # may want to connect to author class
                if (me.rating=='Mature') or (me.rating=='Explicit'):
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

# post_url = "https://starrybouquet.tumblr.com/post/620329944196710401/heya-any-suggestions-for-good-affinity-fix-it"


def strip_redirect_link(url):
    replacements = [['%3A', ':'],
                    ['%2F', '/']]

    start_index = url.find('z=')+2
    end_index = url.find('&t')
    if start_index != -1 and end_index != -1:
        short_url = url[start_index:end_index]
        oldurl = short_url
        realurl = ''
        for charset in replacements:
            realurl = oldurl.replace(charset[0], charset[1])
            oldurl = realurl

        return realurl

    else:
        print("Link could not be stripped. Returning url given.")
        return url

def get_works(post_url, source='tumblr', filename=''):
    '''get works from tumblr url with links
    options for source: tumblr, file, url'''

    if source == 'tumblr':
        if "/post/" in post_url:
            post_url_split = post_url.partition("/post/")
        elif "/private/" in post_url:
            post_url_split = post_url.partition("/private/")

        post_username = post_url_split[0].partition("https://")[2]
        post_id = post_url_split[2].partition("/")[0]

        print("Parsing post from {}".format(post_username)) # check it worked

        post = client.posts(post_username, id=post_id)['posts'][0]
        content = post['trail'][0]['content'].split('<')
        all_links = []
        for line in content:
            if "href=" in line:
                link = line.split('"')[1]
                all_links.append(link)

    elif source == 'url':
        html = html_from_url(post_url)
        soup = BeautifulSoup(html, 'html.parser')
        links_raw = [link.get('href') for link in soup.find_all('a')]
        all_links = []
        requests_session = requests.Session()
        for link in links_raw:
            r = requests_session.get(link)
            print("Link is currently {}".format(r.url))
            # redirectedlink = requests_session.get_redirect_target(r)
            # print("Trying redirect link. Redirected gives {}".format(redirectedlink))
            redirectedlink = strip_redirect_link(link)
            print("Tried to strip redirect link manually. This is what we got {}".format(redirectedlink))
            all_links.append(redirectedlink)

    elif source == 'file':
        f = open(filename, 'r')
        html = f.read()
        f.close()

        soup = BeautifulSoup(html, 'html.parser')
        links_raw = [link.get('href') for link in soup.find_all('a')]
        all_links = []
        requests_session = requests.Session()
        for link in links_raw:
            r = requests_session.get(link)
            print("Link is currently {}".format(r.url))
            # redirectedlink = requests_session.get_redirect_target(r)
            # print("Trying redirect link. Redirected gives {}".format(redirectedlink))
            redirectedlink = strip_redirect_link(link)
            print("Tried to strip redirect link manually. This is what we got {}".format(redirectedlink))
            all_links.append(redirectedlink)

        return all_links

def works_from_links(linkList, reccer):
    authors = []
    works = []
    worksSinceSleep = 0
    for link in linkList:
        if worksSinceSleep >= 30:
            print('We have been through {} works since last sleep. Pausing for 2 min so that we do not exceed requests.'.format(worksSinceSleep))
            time.sleep(120)
            worksSinceSleep = 0

        if ('/u/' in link) or ('/users/' in link):
            print("Author link. Not going to create it because it's a hassle. Uncomment following line to create Authors.")
            # authors.append(Author(link))
        elif ('/s/' in link) or ('/works/' in link):
            works.append(Fic(link, reccer))
            worksSinceSleep += 1
        elif '/series/' in link:
            print('Link is to a series, trying to access series parts now')
            seriesworks = get_works_from_series(link.partition('/series/')[2], reccer)
            works.extend(seriesworks)
            worksSinceSleep += len(seriesworks)
        else:
            print('{} is an invalid link'.format(link))

    return works

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
        print(type(work))
        work.reload()
        if work.fandoms[0] == "Stargate SG-1":
            bookmarked_works.append(Fic(work.url, 'starrybouquet', existingAO3Work=work))
    return bookmarked_works

def get_works_from_series(seriesid, reccer):
    '''get list of works of my Work class given an ao3 series id'''
    series = AO3.Series(seriesid)
    seriesparts = []
    for work in series.work_list:
        work.reload()
        seriesparts.append(Fic(work.url, reccer, existingAO3Work=work))
    return seriesparts

def add_work(work, row_to_add):
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


# work_links = print(get_works('', source='file', filename='samcaarter_reclist.html'))
work_links = pickle.load(open('old_data.p', 'rb'))
works = works_from_links(work_links, 'samcaarter')
pickle.dump(works, open('works_found.p', 'wb'))
print("We found {} works. Dumped them in works_found.p for safekeeping.".format(len(works)))

for work in works:
    print(work.get_title())
    add_work(work, first_blank_line)
    first_blank_line += 1
    print('work added')
    print()

# w = get_works_from_bookmarks()
# for title in w:
#     print(w.get_title())


## possible additions:
# - get some filters from tags on work
# - ??
#
