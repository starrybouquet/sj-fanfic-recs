## ON HOLD UNTIL I KNOW HOW TO FIGURE OUT DEPENDENCIES BETTER

from ao3 import AO3
from ao3.works import RestrictedWork
import ffnet

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
