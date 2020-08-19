import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

print()

cred = credentials.Certificate("firebase_secret.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://fir-test-project-98169.firebaseio.com/test_fics'
})

root = db.reference()
# Add a new fic under /test_fics.
new_fic = root.child('test_fics').push({
    'Title' : 'Dates and Daffodils',
    'Author' : 'starrybouquet',
    'Link' : 'https://archiveofourown.org/works/25945657',
    'Description' : "Even though she'd been thinking about it for the better part of a day, it was still surreal to have Jack O'Neill standing on her doorstep, dressed in jeans, a gray t-shirt, and a flannel that for once wasn't three sizes too big. One hand held a plastic takeout bag with red lettering, and the other was holding...a bunch of daffodils?",
    'Site' : 'AO3'
})

other_new = root.child('test_fics').push({
    'Title' : 'Thoughts',
    'Author' : 'starrybouquet',
    'Link' : 'LINK HERE',
    'Description' : "Five times Sam worries about Jack.",
    'Site' : 'AO3'
})

# Update a child attribute of the new fic.
new_fic.update({'Season' : 'Season 7'})

# Obtain a new reference to the fic, and retrieve child data.
# Result will be made available as a Python dict.
daff = db.reference('test_fics/{0}'.format(new_fic.key)).get()

print(daff)
print()

dark = db.reference('test_fics/-MEyuyKuu16wkYQdGuCP').get()
print(dark)
print()

thoughts = db.reference('test_fics/{0}'.format(other_new.key)).get()
print(thoughts)
