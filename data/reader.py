from AO3 import User, Work, Series

from bs4 import BeautifulSoup
import requests
from ao3_requester import requester
import ao3_utils as utils

class Reader(User):
    '''
    Subclass of User that has functionality to get bookmarks. (Bookmark functionality from AO3 Session class)
    '''
    def __init__(self, username, session=None, loadBookmarks=True):
        self.session = None

        super().__init__(username)

        self._bookmarks_url = "https://archiveofourown.org/users/{0}/bookmarks?page={1:d}"

        if loadBookmarks:
            self._bookmarks = None
            self.get_bookmarks()

    def get(self, *args, **kwargs):
        """Request a web page and return a Response object"""

        if self.session is None:
            req = requester.request("get", *args, **kwargs)
        else:
            req = requester.request("get", *args, **kwargs, session=self.session)
        if req.status_code == 429:
            raise utils.HTTPError("We are being rate-limited. Try again in a while or reduce the number of requests")
        return req

    def request(self, url):
        """Request a web page and return a BeautifulSoup object.
        Args:
            url (str): Url to request
        Returns:
            bs4.BeautifulSoup: BeautifulSoup object representing the requested page's html
        """

        req = self.get(url)
        soup = BeautifulSoup(req.content, "lxml")
        return soup

    def _bookmark_pages(self):
        url = self._bookmarks_url.format(self.username, 1)
        soup = self.request(url)
        pages = soup.find("ol", {"title": "pagination"})
        if pages is None:
            return 1
        n = 1
        for li in pages.findAll("li"):
            text = li.getText()
            if text.isdigit():
                n = int(text)
        return n

    def get_bookmarks(self):
        """
        Get bookmarked works. Loads them if they haven't been previously
        Returns:
            list: List of tuples (workid, workname, authors)
        """

        if self._bookmarks is None:
            self._bookmarks = []
            for page in range(self._bookmark_pages()):
                self._load_bookmarks(page=page+1)
        return self._bookmarks

    def _load_bookmarks(self, page=1):
        url = self._bookmarks_url.format(self.username, page)
        soup = self.request(url)
        bookmarks = soup.find("ol", {'class': 'bookmark index group'})
        for bookm in bookmarks.find_all("li", {'class': 'bookmark blurb group'}):
            authors = []
            # for a in bookm.h4.find_all("a"):
            for a in bookm.find_all("a"):
                if 'rel' in a.attrs.keys():
                    if "author" in a['rel']:
                        authors.append(User(a.string, load=False))
                elif a.attrs["href"].startswith("/works"):
                    workname = a.string
                    workid = utils.workid_from_url(a['href'])

                    new = Work(workid, load=False)
                    setattr(new, "title", workname)
                    setattr(new, "authors", authors)
                    if new not in self._bookmarks:
                        self._bookmarks.append(new)
