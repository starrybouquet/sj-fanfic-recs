# Getting Recs from Tumblr
# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.

import pytumblr
import AO3

from bs4 import BeautifulSoup
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time

from classes import Fic, Author

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
        if worksSinceSleep >= 40:
            print('We have been through {} works since last sleep. Pausing for 2 min so that we do not exceed requests.'.format(worksSinceSleep))
            time.sleep(120)

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
                first_blank_legend_line += 1

    update_local_copies()


# work_links = print(get_works('', source='file', filename='samcaarter_reclist.html'))
work_links = ['https://samcaarter.tumblr.com/tagged/sg1%20meme', 'https://samcaarter.tumblr.com/', 'https://samcaarter.tumblr.com/ask', 'https://samcaarter.tumblr.com/made%20by%20me', 'https://samcaarter.tumblr.com/stargategifs', 'https://lutherwest.tumblr.com/', 'https://archiveofourown.org/works/190494', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/1352761', 'https://archiveofourown.org/users/missparker/pseuds/missparker', 'https://archiveofourown.org/series/2545', 'https://archiveofourown.org/users/ziparumpazoo/pseuds/ziparumpazoo', 'https://archiveofourown.org/works/3216521', 'https://archiveofourown.org/users/geneeste/pseuds/geneeste', 'https://archiveofourown.org/works/2721791', 'https://archiveofourown.org/users/iblamethenubbins/pseuds/iblamethenubbins', 'https://archiveofourown.org/works/205063', 'https://archiveofourown.org/users/openended/pseuds/openended', 'https://archiveofourown.org/works/1606748', 'https://archiveofourown.org/users/bluemoonmaverick/pseuds/bluemoonmaverick', 'https://archiveofourown.org/works/71004', 'https://archiveofourown.org/users/draco_somnians/pseuds/draco_somnians', 'https://archiveofourown.org/works/20048035', 'https://archiveofourown.org/users/sharim28/pseuds/sharim28', 'https://archiveofourown.org/works/14122146', 'https://archiveofourown.org/users/NiceHatGeorgia/pseuds/NiceHatGeorgia', 'https://archiveofourown.org/works/16431680', 'https://archiveofourown.org/users/sharim28/pseuds/sharim28', 'https://archiveofourown.org/series/563059', 'https://archiveofourown.org/users/amaradangeli/pseuds/amaradangeli', 'https://archiveofourown.org/works/19245739', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/16021202', 'https://archiveofourown.org/users/Joracwyn/pseuds/Joracwyn', 'https://archiveofourown.org/works/20343862', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/22993711', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/series/294347', 'https://archiveofourown.org/users/fems/pseuds/fems', 'https://archiveofourown.org/works/789410', 'https://archiveofourown.org/users/missparker/pseuds/missparker', 'https://archiveofourown.org/series/7737', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/5186969', 'https://archiveofourown.org/users/3starJeneral/pseuds/3starJeneral', 'https://archiveofourown.org/works/23674651', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/73476', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/202540', 'https://archiveofourown.org/users/nextgreatadventure/pseuds/nextgreatadventure', 'https://archiveofourown.org/works/2036757', 'https://archiveofourown.org/users/KimberleyJackson/pseuds/Kimberley%2520Jackson', 'https://archiveofourown.org/works/3096419', 'https://archiveofourown.org/users/bluemoonmaverick/pseuds/bluemoonmaverick', 'https://archiveofourown.org/works/1167621', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/24787213', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/1144191', 'https://archiveofourown.org/users/bluemoonmaverick/pseuds/bluemoonmaverick', 'https://archiveofourown.org/works/3234047', 'https://archiveofourown.org/users/bluemoonmaverick/pseuds/bluemoonmaverick', 'https://archiveofourown.org/works/1707398', 'https://archiveofourown.org/users/splash_the_cat/pseuds/splash_the_cat', 'https://archiveofourown.org/works/219878', 'https://archiveofourown.org/users/nextgreatadventure/pseuds/nextgreatadventure', 'https://archiveofourown.org/works/17121407', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/4440479', 'https://archiveofourown.org/users/indiefic/pseuds/indiefic', 'https://archiveofourown.org/works/204232', 'https://archiveofourown.org/users/mrv3000/pseuds/mrv3000', 'https://archiveofourown.org/works/16374518', 'https://archiveofourown.org/users/Sarah_M/pseuds/Sarah_M', 'https://archiveofourown.org/works/17652089', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/17688413', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/138238', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/2135820', 'https://archiveofourown.org/users/Salr323/pseuds/Salr323', 'https://archiveofourown.org/works/188755', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/17643473', 'https://archiveofourown.org/users/Sarah_M/pseuds/Sarah_M', 'https://archiveofourown.org/works/386073', 'https://archiveofourown.org/users/NellieOleson/pseuds/NellieOleson', 'https://archiveofourown.org/series/5002', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/189162', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/206266', 'https://archiveofourown.org/users/Rachel500/pseuds/Rachel500', 'https://archiveofourown.org/works/122238', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/223489', 'https://archiveofourown.org/users/Callie/pseuds/Callie', 'https://archiveofourown.org/works/2714642', 'https://archiveofourown.org/users/callista1159/pseuds/callista1159', 'https://archiveofourown.org/works/598565', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/188743', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/8111635', 'https://archiveofourown.org/users/Alicesandra/pseuds/Alicesandra', 'https://archiveofourown.org/works/1142831', 'https://archiveofourown.org/users/Salr323/pseuds/Salr323', 'https://archiveofourown.org/works/148927', 'https://archiveofourown.org/users/nandamai/pseuds/nanda', 'https://archiveofourown.org/works/280910', 'https://archiveofourown.org/users/Rachel500/pseuds/Rachel500', 'https://archiveofourown.org/works/188898', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/108702', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/57533', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/14453', 'https://archiveofourown.org/users/gabolange/pseuds/gabolange', 'https://archiveofourown.org/works/423381', 'https://archiveofourown.org/users/mscorkill/pseuds/Sue%2520Corkill', 'https://archiveofourown.org/works/11827', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/625293', 'https://archiveofourown.org/users/mrspollifax/pseuds/mrspollifax', 'https://archiveofourown.org/works/54982', 'https://archiveofourown.org/users/Ayiana/pseuds/Ayiana', 'https://archiveofourown.org/works/19425232', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/108951', 'https://archiveofourown.org/users/ziparumpazoo/pseuds/ziparumpazoo', 'https://archiveofourown.org/works/4881100', 'https://archiveofourown.org/users/Akamaimom/pseuds/Akamaimom', 'https://archiveofourown.org/works/259294', 'https://archiveofourown.org/users/adventurepants/pseuds/adventurepants', 'https://archiveofourown.org/works/21112469', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/528143', 'https://archiveofourown.org/users/nandamai/pseuds/nanda', 'https://archiveofourown.org/works/18376724', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/series/5939', 'https://archiveofourown.org/users/nandamai/pseuds/nanda', 'https://archiveofourown.org/works/379543', 'https://archiveofourown.org/users/NellieOleson/pseuds/NellieOleson', 'https://archiveofourown.org/works/1138665', 'https://archiveofourown.org/users/AKarswyll/pseuds/AKarswyll', 'https://archiveofourown.org/works/337730', 'https://archiveofourown.org/users/openended/pseuds/openended', 'https://archiveofourown.org/works/19013830', 'https://archiveofourown.org/users/Sarah_M/pseuds/Sarah_M', 'https://archiveofourown.org/works/24218371', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/24689800', 'https://archiveofourown.org/users/samcaarter/pseuds/samcaarter', 'https://archiveofourown.org/works/189170', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/134933', 'https://archiveofourown.org/users/missparker/pseuds/missparker', 'https://archiveofourown.org/works/18773773', 'https://archiveofourown.org/users/CoraClavia/pseuds/CoraClavia', 'https://archiveofourown.org/works/148502', 'https://archiveofourown.org/users/nandamai/pseuds/nanda', 'https://archiveofourown.org/works/855281', 'https://archiveofourown.org/users/NellieOleson/pseuds/NellieOleson', 'https://archiveofourown.org/works/1214026', 'https://archiveofourown.org/users/Salr323/pseuds/Salr323', 'https://archiveofourown.org/works/6496', 'https://archiveofourown.org/users/ziparumpazoo/pseuds/ziparumpazoo', 'https://archiveofourown.org/works/214352', 'https://archiveofourown.org/users/Annerb/pseuds/Annerb', 'https://archiveofourown.org/works/16806', 'https://archiveofourown.org/users/dizzy/pseuds/dizzy', 'https://archiveofourown.org/works/6715675', 'https://archiveofourown.org/users/amaradangeli/pseuds/amaradangeli', 'https://archiveofourown.org/works/16292300', 'https://archiveofourown.org/users/Sarah_M/pseuds/Sarah_M', 'https://archiveofourown.org/works/10739001', 'https://archiveofourown.org/users/amaradangeli/pseuds/amaradangeli', 'https://archiveofourown.org/works/9333437', 'https://archiveofourown.org/users/amaradangeli/pseuds/amaradangeli', 'https://samcaarter.tumblr.com/post/621914267347795968/aus-string-theory-an-au-series-by-annerb-doctor', 'https://www.tumblr.com/reblog/621914267347795968/vasPdCdQ']
works = works_from_links(work_links, 'samcaarter')
print("We found {} works".format(len(works)))
for work in works:
    print(work.get_title())
    add_work(work)
    print('work added')
    print()

# w = get_works_from_bookmarks()
# for title in w:
#     print(w.get_title())


## possible additions:
# - get some filters from tags on work
# - ??
#
