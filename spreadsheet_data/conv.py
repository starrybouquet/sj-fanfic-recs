f = open("rec_parse.ipynb.txt", mode='r')
all = f.readlines()
f.close()

raw = open("ipynb_raw.txt", mode='w')
saveNext = False
for line in all:
    if saveNext:
        if "   ]" in line:
            saveNext = False
        else:
            strippedLine = line[4:].strip('\",')
            raw.write(strippedLine)
    else:
        if "\"source\": [" in line:
            saveNext = True

raw.close()
