import random

def read_config(fname):
    dct = {}
    fl = open(fname, 'r')
    rd = fl.read().split('\n')
    fl.close()
    for i in rd:
        if i != '':
            dct[i.split(':')[0]] = ":".join(i.split(':')[1:])
            if dct[i.split(':')[0]][0] == ' ':
                dct[i.split(':')[0]] = dct[i.split(':')[0]][1:]
    return dct

def write_config(fname, dct):
    fl = open(fname, 'w+')
    for i in dct:
        if type(dct[i]) == bool:
            fl.write(i+': '+("true" if dct[i] else "false")+'\n')
        else:
            fl.write(i+': '+str(dct[i])+'\n')
    fl.close()

def is_file(fname):
    try:
        fl = open(fname, 'r')
        fl.close()
        return True
    except IOError:
        return False


namechoices = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Tianjin", "Hong Kong", "Nanking", "Macau", "Tibet", "Sian", "chu-hai", "ChengTu", "Honolulu", "Anchorage", "Vancouver", "San Francisco", "Seattle", "Los Angeles", "Aklavik", "Edmonton", "Phoenix", "Denver", "Mexico City", "Winnipeg", "Houston", "Minneapolis", "St. Paul", "New Orleans", "Chicago", "Montgomery", "Guatemala", "San Salvador", "Tegucigalpa", "Managua", "Havana", "Indianapolis", "Atlanta", "Detroit"]

def getaname():
    if len(namechoices) <= 0 or random.randint(0, 1) == 0:
        s = ""
        av = ["a", "e", "i", "o", "u", "a", "e", "i", "o", "u", "ai", "ao", "ou"]
        tv = ["b", "p", "m", "f", "c", "d", "g", "h", "j", "k", "l", "n", "p", "qu", "r", "s", "t", "w", "ch"]
        for i in range(random.choice([2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4])):
            s += random.choice(tv)
            s += random.choice(av)
            if random.randint(0, 6) == 0:
                chk = random.choice(av)
                if chk[0] != s[-1] and chk[0] != s[-2] and (len(chk)==1 or (chk[1] != s[-1] and chk[1] != s[-2])):
                    s += chk
        if random.randint(0, 2) == 0:
            s += random.choice(["l", "b", "p", "m", "d", "g", "n", "s", "s"])
            if random.randint(0, 2) == 0:
                s += random.choice("ia")
        if random.randint(0, 3) == 0:
            s = random.choice(av) + s
        if random.randint(0, 4) == 0:
            if random.randint(0, 2) == 0:
                s = random.choice(["san ", "st. "]) + s
            else:
                s += random.choice([" city", " town"])
        return s.capitalize()
    nc = random.choice(namechoices)
    namechoices.remove(nc)
    return nc