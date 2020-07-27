

# Given a rec list from Tumblr like mine, trying to extract a list of links (fanfic recs).
# Also trying to extract a header image given a blog name.

import pytumblr
from ao3 import AO3
from ao3.works import RestrictedWork
import ffnet
from notion.client import NotionClient

ao3 = AO3()

client = NotionClient(token_v2="token here")

# From tumblr API console https://api.tumblr.com/console
# Authenticate via OAuth
# NEED TO FILL OUT
client = pytumblr.TumblrRestClient()

# post url options
# https://starrybouquet.tumblr.com/post/620329944196710401/heya-any-suggestions-for-good-affinity-fix-it
# https://samcaarter.tumblr.com/private/621914267347795968/tumblr_qchqnjlukx1r9gqxq
# https://professortennant.tumblr.com/post/175193322905/samjack-rec-list-pt-1
