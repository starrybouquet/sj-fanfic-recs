from ao3 import AO3
from ao3.works import RestrictedWork

ao3 = AO3()

link = 'https://archiveofourown.org/works/16765762'
id = link.partition('/works/')[2]
work = ao3.work(id=id)

print(work.summary)
