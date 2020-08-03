from bs4 import BeautifulSoup
import requests

import AO3
import ffnet

class Link(object):
    '''link from html rec list'''

    sites = {'ao3': 'archiveofourown.org',
                'ffn': 'fanfiction.net'}

    def __init__(self, raw_link):

        self.link = raw_link
        self.id = '-1'

        if self.sites['ao3'] in self.link:
            self.site = 'ao3'
        elif self.sites['ffn'] in self.link:
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

    def __init__(self, raw_link, reccer, existingAO3Work=False, existingFFNStory=False, ffn_users_loaded=[]):
        super().__init__(raw_link)
        self.reccer = reccer
        self.url = raw_link
        if existingAO3Work:
            self.title = existingAO3Work.title
            self.desc = existingAO3Work.summary[1:]
            self.author = str(existingAO3Work.authors[0].username) # may want to connect to author class
            if (existingAO3Work.rating=='Mature') or (existingAO3Work.rating=='Explicit'):
                self.isAdult = True
            else:
                self.isAdult = False
        elif existingFFNStory:
            existingFFNStory.download_data()
            self.title = existingFFNStory.title
            self.desc = existingFFNStory.description
            author_obj = existingFFNStory.get_user()
            author_obj.download_data()
            self.author = author_obj.username
            if existingFFNStory.rated == 'M':
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
                self.author = str(me.authors[0].username) # may want to connect to author class
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
