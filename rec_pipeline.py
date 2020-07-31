# Getting Recs from Tumblr
# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.
import time
import pickle
import sys

import pytumblr
import AO3
import ffnet

from bs4 import BeautifulSoup
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from classes import Fic, Author

sites = {'ao3': 'archiveofourown.org',
            'ffn': 'fanfiction.net'}



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

def single_work_from_link(link, reccer):
    '''Get single work from link given.

    Parameters
    ----------
    link : str

    Returns
    -------
    list [int, Work]
        Work Work (or multiple if the link was a series)
        int equal to number of works retrieved
        List is just [int] if the link was invalid/was an author.
    '''
    if ('/u/' in link) or ('/users/' in link):
        print("Author link. Not going to create it because it's a hassle. Uncomment following line to create Authors.")
        # authors.append(Author(link))
        return [0]
    elif ('/s/' in link) or ('/works/' in link):
        work = Fic(link, reccer)
        numWorksRetrieved = 1
        return [numWorksRetrieved, work]
    elif '/series/' in link:
        print('Link is to a series, trying to access series parts now')
        seriesworks = get_works_from_series(link.partition('/series/')[2], reccer)
        numWorksRetrieved = len(seriesworks)
        return [numWorksRetrieved, seriesworks]
    else:
        print('{} is an invalid link'.format(link))
        return [0]


def multiple_works_from_links(linkList, reccer, sleeptime=90):
    authors = []
    works = []
    worksSinceSleep = 0
    for link in linkList:
        if worksSinceSleep >= 30:
            print('We have been through {0} works since last sleep. Pausing for {1} sec so that we do not exceed requests.'.format(worksSinceSleep, sleeptime))
            time.sleep(sleeptime)
            worksSinceSleep = 0

        linkOutput = single_work_from_link(link, reccer)

        if len(linkOutput) != 1:
            works.extend(linkOutput[1:])
            worksSinceSleep += linkOutput[0]

    return works

def get_works_from_series(seriesid, reccer):
    '''get list of works of my Work class given an ao3 series id'''
    series = AO3.Series(seriesid)
    seriesparts = []
    for work in series.work_list:
        work.reload()
        seriesparts.append(Fic(work.url, reccer, existingAO3Work=work))
    return seriesparts

def get_recs_spreadsheet():
    '''Get recs spreadsheets from Google

    Returns
    -------
    recs
        gsheet sheet object
    recs_local
        list of lists version of gsheet sheet

    '''
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    recs = client.open_by_url('https://docs.google.com/spreadsheets/d/1_9-jjGIO4v1NgppU3ENDEE1itPbnDStyYzbx1J5_OfQ').get_worksheet(1)

    recs_local = recs.get_all_values()

    return recs, recs_local

def add_work(work, row_to_add, linkList, recs_sheet, recs_object):
    '''Add work to fic entry part of spreadsheet. Checks the gsheet and add to recs if it's not there.
    If it's already there, add reccer if they're not already there

    Parameters
    ----------
    work : Work
        Work to add.
    row_to_add : int
        Row number that work should be added to, if it's not yet in sheet.
    linkList : list
        List of all links in sheet, currently. You can get this using sheet.col_values(4).
    recs_sheet : list
        List of lists representing sheet before any works were added.
    recs_object : gsheet sheet
        Sheet object to update.

    Returns
    -------
    int
        1 if work was added, 0 if it was already there.

    '''

    # use link to figure out if it's already there
    if work.get_url() in linkList: #probably need to check that links are consistent
        workrow = linkList.index(work.get_url())
        reccers = recs_sheet[workrow][9]
        if work.get_reccer() not in reccers:
            newvalue = reccers + ", " + work.get_reccer()
            recs_object.update_cell(workrow, 10, newvalue)
        return 0

    else: # need to add fic
        recs_object.update('A{0}:J{0}'.format(row_to_add), [work.get_title(), work.get_author(), work.get_desc(), work.get_url(), '', '', '', '', work.get_site(), work.get_reccer()])
        return 1


# work_links = print(get_works('', source='file', filename='samcaarter_reclist.html'))
recursion_depth = 3000
sys.setrecursionlimit(recursion_depth)
work_links = pickle.load(open('old_data.p', 'rb'))
works = multiple_works_from_links(work_links, 'samcaarter')
print("We found {} works. List below:")
for work in works:
    print(work.get_title())
print()
print("Trying to put them in pickle now.")
try:
    pickle.dump(works, open('works_found.p', 'wb'))
    print()
    print("Successfully dumped, now adding to spreadsheet")
except RecursionError:
    print("Recursion error occurred with depth {}, skipping pickle dump.".format(sys.getrecursionlimit()))
recs, recs_local = get_recs_spreadsheet()
first_blank_line = len(recs.col_values(1))+1
all_links = recs.col_values(4)
for work in works:
    print(work.get_title())
    first_blank_line += add_work(work, first_blank_line, all_links, recs_local, recs)
    print('work added')
    print()

# w = get_works_from_bookmarks()
# for title in w:
#     print(w.get_title())


## possible additions:
# - get some filters from tags on work
# - ??
#
