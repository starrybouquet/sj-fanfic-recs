# Getting Recs from Tumblr
# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.

import pytumblr
from ao3 import AO3
from ao3.works import RestrictedWork
import ffnet
from bs4 import BeautifulSoup

ao3 = AO3()

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

    def __init__(self, raw_link):
        super().__init__(raw_link)
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
