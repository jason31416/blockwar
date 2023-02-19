"""
v 1.5.2:
    - Fixed city name display
    - Added guns

    - Todo: gun shop!
"""
version = (1, 5, 2)
support_save_version = [(1, 5, 2)]

import math
import time
import pyge
import os
from functions import *

# WINSZ = (800, 600)
WINSZ = (3024//2, 1964//2)

# Initialize files

if not os.path.exists("saves"):
    os.mkdir("saves")

all_saves = os.listdir("saves")

# new world
wsize = 300
x, y = 0, 0
blksz = 40
vx = x-WINSZ[0]//blksz//2
vy = y-WINSZ[1]//blksz//2
csz = 4
cn = wsize//csz
gamemode = 0 # 0: normal 1: spectator
cty_count = 180
teamn = 12
player_team_boost = 0
only_log_ipt_cty = False

defrespctd = 200

clrs = [(0, 0, 255), (255, 50, 50), (0, 255, 0), (255, 0, 255), (255, 255, 0), (0, 255, 255), (255, 125, 0), (0, 150, 0), (50, 50, 50), (255, 170, 170), (128, 64, 0), (135, 206, 235)]

random.shuffle(clrs)

# input wname

wname = input("World name: ")
if wname+".sv" in all_saves:
    print("World already exists, loading that world...")
    wmode = False
else:
    print("Creating new world...")
    wmode = True

# functions

def generate_world():
    global cty_count
    for i in range(20):
        world[random.randint(0, wsize - 1)][random.randint(0, wsize - 1)] = 3

    for j in range(cty_count//2):
        rx, ry = random.randint(0, wsize - 1), random.randint(0, wsize - 1)
        world[rx][ry] = 4
        all_ckp.append((rx, ry))
        winsd[rx][ry] = len(all_ckp) - 1
        ckp_nm.append(getaname())
        if random.randint(0, 3) == 0:
            imp_ckp.append((rx, ry))

    for j in range(cty_count//2):
        rx, ry = random.randint(0, wsize - 1), random.randint(0, wsize - 1)
        world[rx][ry] = 6
        winsd[rx][ry] = 0

    cty_count = cty_count//2

    print("loading world")
    while True:
        ret = generate_area()
        print("\rgenerating area    " + str(int(ret[1] / wsize ** 2 * 100)) + "% (" + str(ret[1]) + "/" + str(
            wsize ** 2 * 100) + " blocks)", end="")
        if not ret[0]:
            break
    print("\nfinished")

teamcnt = [-1] * teamn

def load_world_from_file(fname):
    global wsize, world, wattr, winsd, nearby_terri, entity, nwentity, cty_count, x, y, hp_
    f = open("saves/"+fname+".sv", 'r')
    rd = f.read().split("\n")
    f.close()
    ind = 0
    vsn = tuple(int(i) for i in rd[ind].split("."))
    if vsn == version:
        print("loading world data...")
    elif vsn in support_save_version:
        print("loading world data...")
        print("warning: this save is not saved with the current version of the game, some data may be lost!")
    else:
        print("warning: this save is saved with a not supported version of the game!")
        exit(0)
    ind += 1
    wsz, cty_count, teamn = map(int, rd[ind].split(" "))
    wsize = wsz
    ind += 1
    for i in range(int(wsz)):
        for j in range(int(wsz)):
            world[i][j] = int(rd[ind].split(" ")[j])
        ind += 1
    for i in range(int(wsz)):
        for j in range(int(wsz)):
            wattr[i][j] = [int(k) for k in rd[ind].split(" ")[j].split(",")]
        ind += 1
    for i in range(int(wsz)):
        for j in range(int(wsz)):
            winsd[i][j] = int(rd[ind].split(" ")[j])
        ind += 1
    for i in range(cty_count):
        all_ckp.append((int(rd[ind].split(" ")[i].split(",")[0]), int(rd[ind].split(" ")[i].split(",")[1])))
    ind += 1
    for i in range(teamn):
        teamcnt[i] = int(rd[ind].split(" ")[i])
    ind += 1
    for i in range(cty_count):
        ckp_nm.append(rd[ind].split("::")[i])
    ind += 1
    x, y, hp_ = map(float, rd[ind].split(" "))
    ind += 1
    get_nearby_terri()

def get_nearby_terri():
    for i in range(wsize):
        for j in range(wsize):
            if i+1<wsize and winsd[i+1][j]!=winsd[i][j]:
                nearby_terri[winsd[i][j]].append(winsd[i+1][j])
            if j+1<wsize and winsd[i][j+1]!=winsd[i][j]:
                nearby_terri[winsd[i][j]].append(winsd[i][j+1])
            if i-1>=0 and winsd[i-1][j]!=winsd[i][j]:
                nearby_terri[winsd[i][j]].append(winsd[i-1][j])
            if j-1>=0 and winsd[i][j-1]!=winsd[i][j]:
                nearby_terri[winsd[i][j]].append(winsd[i][j-1])

def save_world(*args):
    f = open("saves/"+wname+".sv", 'w')
    f.write(".".join(map(str, version))+"\n")
    f.write(str(wsize) + " " + str(cty_count) + " " + str(teamn) + "\n")
    for i in range(wsize):
        for j in range(wsize):
            f.write(str(world[i][j]) + " ")
        f.write("\n")
    for i in range(wsize):
        for j in range(wsize):
            f.write(str(wattr[i][j][0]) + "," + str(wattr[i][j][1]) + "," + str(wattr[i][j][2]) + " ")
        f.write("\n")
    for i in range(wsize):
        for j in range(wsize):
            f.write(str(winsd[i][j]) + " ")
        f.write("\n")
    for i in range(cty_count):
        f.write(str(all_ckp[i][0]) + "," + str(all_ckp[i][1]) + " ")
    f.write("\n")
    for i in range(teamn):
        f.write(str(teams[i].alive_player_count) + " ")
    f.write("\n")
    for i in range(cty_count):
        f.write(ckp_nm[i] + "::")
    f.write("\n" + str(x) + " " + str(y) + " " + str(hp_) + "\n")
    f.close()


def get_owner(x, y):
    return wattr[all_ckp[winsd[x][y]][0]][all_ckp[winsd[x][y]][1]][0]

def log(gmtk, msg_, clr=(0, 0, 0)):
    print(str(gmtk)+":", msg_)
    msg.append((gmtk, msg_, clr))

def somewhere_nearby(p1, p2, r):
    rx, ry = p1+random.randint(-r, r), p2+random.randint(-r, r)
    while rx < 0 or rx >= wsize or ry < 0 or ry >= wsize or world[rx][ry] not in (0, 6):
        rx, ry = p1+random.randint(-r, r), p2+random.randint(-r, r)
    return rx, ry

def generate_area():
    global winsd
    bkup = [[winsd[j][i] for i in range(wsize)] for j in range(wsize)]
    bkup2 = [[world[j][i] for i in range(wsize)] for j in range(wsize)]
    bb = False
    cnt = 0
    for i in range(wsize):
        for j in range(wsize):
            if bkup2[i][j]==6:
                cnt += 1
                if i + 1 < wsize:
                    if winsd[i + 1][j] == -1 and random.randint(0, 100) < 60:
                        world[i + 1][j] = 6
                        winsd[i+1][j] = 0
                if i - 1 >= 0:
                    if winsd[i - 1][j] == -1 and random.randint(0, 100) < 60:
                        world[i - 1][j] = 6
                        winsd[i - 1][j] = 0
                if j + 1 < wsize:
                    if winsd[i][j + 1] == -1 and random.randint(0, 100) < 60:
                        world[i][j + 1] = 6
                        winsd[i][j + 1] = 0
                if j - 1 >= 0:
                    if winsd[i][j - 1] == -1 and random.randint(0, 100) < 60:
                        world[i][j - 1] = 6
                        winsd[i][j - 1] = 0
            elif bkup[i][j] != -1:
                cnt += 1
                if i+1 < wsize:
                    if winsd[i+1][j] == -1 and random.randint(0, 100) < 60:
                        winsd[i+1][j] = bkup[i][j]
                    elif winsd[i+1][j] != -1:
                        nearby_terri[bkup[i][j]].append(winsd[i+1][j])
                if i-1 >= 0:
                    if winsd[i-1][j] == -1 and random.randint(0, 100) < 60:
                        winsd[i-1][j] = bkup[i][j]
                    elif winsd[i-1][j] != -1:
                        nearby_terri[bkup[i][j]].append(winsd[i-1][j])
                if j+1 < wsize:
                    if winsd[i][j+1] == -1 and random.randint(0, 100) < 60:
                        winsd[i][j+1] = bkup[i][j]
                    elif winsd[i][j+1] != -1:
                        nearby_terri[bkup[i][j]].append(winsd[i][j+1])
                if j-1 >= 0:
                    if winsd[i][j-1] == -1 and random.randint(0, 100) < 60:
                        winsd[i][j-1] = bkup[i][j]
                    elif winsd[i][j-1] != -1:
                        nearby_terri[bkup[i][j]].append(winsd[i][j-1])
            else:
                bb = True
    return bb, cnt

# config


def_cfgg = {'is_split_line': False, 'allow_sight_away': False, 'ai_no_respawn': False, 'max_ai_targ_at_one_pt': 3, 'cty_as_spawn_point': True, 'lost_all_terri_no_respawn': True, 'let_ai_defence': False, 'wall_hp': 60, "player_in_group": 1, "group_in_team": 20, 'show_split_line': True}

if not is_file('config.txt'):
    write_config('config.txt', def_cfgg)

cfgg = read_config("config.txt")

def get_bool_from_cfg(name, default):
    if name in cfgg:
        if cfgg[name] == 'true':
            return True
        elif cfgg[name] == 'false':
            return False
        else:
            return default
    else:
        print(name, " option not found in config.txt, using default value")
        return default

def get_int_from_cfg(name, default):
    if name in cfgg:
        return int(cfgg[name])
    else:
        print(name, " option not found in config.txt, using default value")
        return default

def get_str_from_cfg(name, default):
    if name in cfgg:
        return cfgg[name]
    else:
        print(name, " option not found in config.txt, using default value")
        return default

is_spilt_line = get_bool_from_cfg('is_split_line', def_cfgg['is_split_line'])
allow_sight_away = get_bool_from_cfg('allow_sight_away', def_cfgg['allow_sight_away'])
ai_no_respawn = get_bool_from_cfg('ai_no_respawn', def_cfgg['ai_no_respawn'])
max_ai_targ_at_one_pt = get_int_from_cfg('max_ai_targ_at_one_pt', def_cfgg['max_ai_targ_at_one_pt'])
cty_as_spawn_point = get_bool_from_cfg('cty_as_spawn_point', def_cfgg['cty_as_spawn_point'])
lost_all_terri_no_respawn = get_bool_from_cfg('lost_all_terri_no_respawn', def_cfgg['lost_all_terri_no_respawn'])
let_ai_defence = get_bool_from_cfg('let_ai_defence', def_cfgg['let_ai_defence'])
wall_hp = get_int_from_cfg('wall_hp', def_cfgg['wall_hp'])
pig = get_int_from_cfg('player_in_group', def_cfgg['player_in_group'])
pit = get_int_from_cfg('group_in_team', def_cfgg['group_in_team'])
spl = get_bool_from_cfg('show_split_line', def_cfgg['show_split_line'])

def dis(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

class obj(pyge.Picture):
    def __init__(self, sf, x=-1, y=-1):
        super().__init__(sf, 0, 0)
        self.x, self.y = x, y

    def draw(self, gm: pyge.Game):
        self.pos_in_world()
        if vx <= self.x < vx+WINSZ[0]//blksz and vy <= self.y < vy + WINSZ[1] // blksz:
            gm.sc.blit(to_siz(self.pic, (blksz*(self.pic.get_width()/32), blksz*(self.pic.get_height()/32))), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz))

    def pos_in_world(self):
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x >= wsize:
            self.x = wsize-1
        if self.y >= wsize:
            self.y = wsize-1

    def touch_block(self):
        self.pos_in_world()
        ax = world[int(self.x)][int(self.y)]
        if self.x+self.pic.get_width()/32 < wsize:
            bx = world[int(self.x+self.pic.get_width()/32)][int(self.y)]
        else:
            bx = 0
        if self.y+self.pic.get_height()/32 < wsize:
            cx = world[int(self.x)][int(self.y+self.pic.get_height()/32)]
        else:
            cx = 0
        if self.x+self.pic.get_width()/32 < wsize and self.y+self.pic.get_height()/32 < wsize:
            dx = world[int(self.x+self.pic.get_width()/32)][int(self.y+self.pic.get_height()/32)]
        else:
            dx = 0
        return ax, bx, cx, dx
    def touch_block_pos(self):
        self.pos_in_world()

        ax = (int(self.x), int(self.y))
        defult = (-1, -1)
        if self.x+self.pic.get_width()/32 < wsize:
            bx = (int(self.x+self.pic.get_width()/32), int(self.y))
        else:
            bx = defult
        if self.y+self.pic.get_height()/32 < wsize:
            cx = (int(self.x), int(self.y+self.pic.get_height()/32))
        else:
            cx = defult
        if self.x+self.pic.get_width()/32 < wsize and self.y+self.pic.get_height()/32 < wsize:
            dx = (int(self.x+self.pic.get_width()/32), int(self.y+self.pic.get_height()/32))
        else:
            dx = defult
        return [ax, bx, cx, dx]

world = [[0]*wsize for i in range(wsize)]
wattr = [[[-1, 0, 0] for j in range(wsize)] for i in range(wsize)]
winsd = [[-1 for j in range(wsize)] for i in range(wsize)]
nearby_terri = [[] for i in range(cty_count)]
# wattr[i][j]: [owner, hp, type] at (i, j)
entity = {}
nwentity = {}
hp_ = 100

class ba:
    def __init__(self, clr, spd, amp):
        self.clr = clr
        self.spd = spd
        self.amp = amp

class ta:
    def __init__(self, clr, nb):
        self.clr = clr
        self.tn = nb
        self.targ = {}
        self.defs = {}
        self.gps = []
        self.csttarg = {}
        self.alive_player_count = 0
    def update(self, gm: pyge.Game):
        if gm.tick%30 == 0:
            for i in all_ckp:
                if i in self.targ:
                    self.targ[i] = 0
                if i in self.defs:
                    self.defs[i] = False
                if wattr[i[0]][i[1]][0] != self.tn and i not in self.targ:
                    self.targ[i] = 0
                if wattr[i[0]][i[1]][0] == self.tn and i in self.targ:
                    self.targ.pop(i)
            for i in self.csttarg:
                self.csttarg[i] = 0
        if gm.tick%30 == 15 and let_ai_defence:
            ni = 0
            for i in all_ckp:
                if wattr[i[0]][i[1]][0] == self.tn and i in imp_ckp:
                    bb = False
                    for j in nearby_terri[ni]:
                        pos = all_ckp[j]
                        if pos in self.targ:
                            bb = True
                            break
                    if bb:
                        if wattr[i[0]][i[1]][0] == self.tn and i not in self.defs:
                            self.defs[i] = False
                    elif i in self.defs:
                        self.defs.pop(i)
                else:
                    if i in self.defs:
                        self.defs.pop(i)
                ni += 1
# todo: group ai

class group:
    def __init__(self, team, name, members):
        self.team = team
        self.name = name
        self.members = members
        self.targ = (-1, -1)
        self.act = True
        self.pos = (-1, -1)

    def update(self, gm: pyge.Game):
        if gm.tick % 15 == 0:
            ntarg = (-1, -1)
            for i in teams[self.team].targ.keys():
                if teams[self.team].targ[i] > max_ai_targ_at_one_pt and self.targ != i:
                    continue
                if ntarg == (-1, -1) or dis(ntarg, self.pos) > dis(i, self.pos):
                    ntarg = i
                    self.act = True
            for i in teams[self.team].csttarg.keys():
                if teams[self.team].csttarg[i] > max_ai_targ_at_one_pt and self.targ != i:
                    continue
                if ntarg == (-1, -1) or dis(ntarg, self.pos) > dis(i, self.pos):
                    ntarg = i
                    self.act = True
            for i in teams[self.team].defs.keys():
                if teams[self.team].defs[i]:
                    continue
                if ntarg == (-1, -1) or 7 >= dis(ntarg, self.pos) > dis(i, self.pos):
                    ntarg = i
                    self.act = False
            if ntarg in teams[self.team].targ:
                teams[self.team].targ[ntarg] += 1
            elif ntarg in teams[self.team].defs:
                teams[self.team].defs[ntarg] = True
            elif ntarg in teams[self.team].csttarg:
                teams[self.team].csttarg[ntarg] += 1
            self.targ = ntarg

blkattrs = {0: ba((200, 200, 200), 1.5, 0), 1: ba((100, 100, 100), 1.5, 100000), 2: ba((0, 0, 50), 2.5, 0), 3: ba((255, 0, 0), 0.2, -1), 4: ba((255, 255, 0), 1.5, 0), 5: ba((100, 100, 100), 1.5, 10), 6: ba((0, 100, 255), 0.5, -1)}
# 0: empty, 1: obstacle, 2: road 3: lava 4: city

teams = []
groups = {"-1": group(0, "-1", [])}

default_gun = [3, 6, 25, 60]

all_guns = [[3, 6, 30, 60], [6, 11, 22, 60], [20, 45, 5, 100]]
# gun: (cooldown, power, ammo, reload)

all_plr = []

all_ckp = []
ckp_nm = []
imp_ckp = []
msg = []


def build_wall(x, y):
    if world[x][y] == 0:
        world[x][y] = 5
        wattr[x][y] = [-1, wall_hp, 0]

def get_et(x, y):
    if (int(x), int(y)) in entity:
        return entity[(int(x), int(y))]
    else:
        return []


for i in range(teamn):
    teams.append(ta(clrs[i], i))

def text(cont, clr=(0, 0, 0)):
    return pyge.pygame.font.Font(None, 20).render(cont, True, clr)

def to_siz(sp, sz):
    return pyge.pygame.transform.scale(sp, sz)

def get_hp_clr(hp, fhp):
    rt = hp/fhp
    if rt == 1:
        return 0, 255, 0
    elif rt > 0.5:
        return 255, 255, 0
    elif rt > 0.25:
        return 255, 170, 0
    else:
        return 255, 0, 0

def get_ammo_clr(hp, fhp):
    rt = hp/fhp
    if rt == 1:
        return 50, 150, 255
    elif rt > 0.5:
        return 0, 255, 0
    elif rt > 0.25:
        return 255, 100, 0
    else:
        return 0, 0, 0

class bullet(obj):
    def __init__(self, x, y, vx, vy, amp, sender, sdt = -1, rg=20, dmg=3, sf=None):
        if sf is None:
            sf = pyge.rect(4, 4)
        super().__init__(sf, x, y)
        self.vx, self.vy = vx, vy
        self.rg = rg
        self.dis = 0
        self.dmg = dmg
        self.amp = amp
        self.sender = sender
        self.senderteam = sdt

    def update(self, gm: pyge.Game):
        if self.x < 0 or self.y < 0 or self.x >= wsize or self.y >= wsize:
            gm.rem_obj(self.name)
            return
        if world[int(self.x)][int(self.y)] == 5:
            wattr[int(self.x)][int(self.y)][1] -= self.dmg
            if wattr[int(self.x)][int(self.y)][1] <= 0:
                world[int(self.x)][int(self.y)] = 0
            gm.rem_obj(self.name)
            return
        if blkattrs[world[int(self.x)][int(self.y)]].amp > self.amp:
            gm.rem_obj(self.name)
            return
        self.x += self.vx
        self.y += self.vy
        self.dis += 1
        if self.dis > self.rg:
            gm.rem_obj(self.name)
        elif self.x < 0 or self.y < 0 or self.x >= wsize or self.y >= wsize:
            gm.rem_obj(self.name)
        elif world[int(self.x)][int(self.y)] == 5:
            wattr[int(self.x)][int(self.y)][1] -= self.dmg
            if wattr[int(self.x)][int(self.y)][1] <= 0:
                world[int(self.x)][int(self.y)] = 0
            gm.rem_obj(self.name)
            return
        elif blkattrs[world[int(self.x)][int(self.y)]].amp > self.amp:
            gm.rem_obj(self.name)
        elif blkattrs[world[int(self.x)][int(self.y)]].amp < self.amp:
            self.amp = blkattrs[world[int(self.x)][int(self.y)]].amp
        for i in all_plr:
            if -0.5 <= self.x-i.x <= 1 and -0.5 <= self.y-i.y <= 1.5 and self.sender != i.name and i.hp > 0:
                i.hp = int(i.hp-self.dmg)
                i.lstdamagefrom = self.senderteam
                gm.rem_obj(self.name)
                if 0 <= (self.x-vx)*blksz <= WINSZ[0] and 0 <= (self.y-vy)*blksz <= WINSZ[1] and (self.sender == "hm_player" or i.name == "hm_player"):
                    gm.draw_text("-"+str(self.dmg), (self.x-vx)*blksz, (self.y-vy)*blksz, 24, color=(255, 0, 0))
                break

# todo: player

class player(obj):
    def __init__(self, team, hp=100, x=0, y=0, typ="ai", isloc=False):
        self.team = team
        self.hp = hp
        self.mxhp = hp
        self.typ = typ
        self.hurt = False
        self.gun = random.choice(all_guns)
        super().__init__(pyge.rect(32, 32, teams[team].clr), x, y)
        self.lstcld = 0
        self.loadam = 0
        self.bllft = self.gun[2]
        self.spawn = x, y
        self.lstcty = x, y
        self.capturing = 0
        self.lstpos = x, y
        self.cpi = 0
        self.respctd = 0
        self.lstdamagefrom = -1
        self.lstheal = 0
        self.islocal = isloc

    def getgrp(self):
        return None

    def respawn(self, gm: pyge.Game):
        global gamemode
        self.lstcty = (int(self.lstcty[0]), int(self.lstcty[1]))
        if wattr[self.lstcty[0]][self.lstcty[1]][0] == self.team:
            self.x, self.y = somewhere_nearby(self.lstcty[0], self.lstcty[1], 5)
            self.gun = random.choice(all_guns)
            self.bllft = self.gun[2]
        else:
            if self.islocal:
                grp: group = groups[self.getgrp()]
                if grp is not None:
                    grp.team = wattr[self.lstcty[0]][self.lstcty[1]][0]
                    if grp in teams[self.team].gps:
                        teams[self.team].gps.remove(self.getgrp())
                    teams[wattr[self.lstcty[0]][self.lstcty[1]][0]].gps.append(self.getgrp())
                teams[wattr[self.lstcty[0]][self.lstcty[1]][0]].alive_player_count += 1
                teams[self.team].alive_player_count -= 1
                self.team = wattr[self.lstcty[0]][self.lstcty[1]][0]
                self.set_surface(pyge.rect(32, 32, teams[self.team].clr))
            else:
                rn = random.randint(0, len(all_ckp)-1)
                cnt = 0
                while wattr[all_ckp[rn][0]][all_ckp[rn][1]][0] != self.team and cnt < 800:
                    rn = random.randint(0, len(all_ckp)-1)
                    cnt += 1
                if cnt < 800:
                    self.x, self.y = somewhere_nearby(all_ckp[rn][0], all_ckp[rn][1], 5)
                elif lost_all_terri_no_respawn:
                    teams[self.team].alive_player_count -= 1
                    if teams[self.team].alive_player_count <= 0:
                        log(gm.tick, "Team " + str(self.team) + " has been eliminated!", (0, 0, 0))
                    if self.typ == "human":
                        gamemode = 1
                    gm.rem_obj(self.name)
                    return
        if ai_no_respawn and self.typ == "ai":
            gm.rem_obj(self.name)
            return

    def draw(self, gm: pyge.Game):
        if self.hp <= 0 or self.respctd > 0:
            return
        if vx <= self.x < vx+WINSZ[0]//blksz and vy <= self.y < vy + WINSZ[1] // blksz:
            gm.sc.blit(to_siz(self.pic, (blksz*(self.pic.get_width()/32), blksz*(self.pic.get_height()/32))), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz))
            gm.sc.blit(pyge.rect((self.hp/self.mxhp)*blksz, 5, get_hp_clr(self.hp, self.mxhp)), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz-10))
            gm.sc.blit(pyge.rect((self.bllft/self.gun[2])*blksz, 3, get_ammo_clr(self.bllft, self.gun[2])), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz-16))
            gm.draw_text(f"{self.gun[1]}", (self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz-25, 18, color=(0, 0, 0))
            # print(self.bllft, self.gun)

    def check(self, gm: pyge.Game):
        if self.respctd > 0:
            self.hp = 0
            self.respctd -= 1
            if self.respctd <= 0:
                self.respawn(gm)
                self.respctd = 0
                self.hp = self.mxhp
            return
        self.hurt = False
        if self.hp <= 0:
            # self.x, self.y = -10, -10
            self.respctd = defrespctd
            return
        if gm.tick%3 == 0:
            bb = False
            for i in get_et(self.x//csz, self.y//csz):
                if i.team != self.team:
                    bb = True
                    break
            if not bb:
                for i, j in self.touch_block_pos():
                    if i == -1:
                        continue
                    if world[i][j] == 4 and wattr[i][j][0] != self.team:
                        self.capturing += 1
                        bb = True
                        if self.capturing > 40:
                            if wattr[i][j][0] == -1:
                                gn = f"{random.randint(0, 10000000000)}"
                                groups[gn] = group(self.team, gn, [])
                                teams[self.team].gps.append(gn)
                                gsx, gsy = somewhere_nearby(i, j, wsize // teamn // 4)
                                for k in range(pig):
                                    px, py = somewhere_nearby(gsx, gsy, 5)
                                    gm.add_player(aiplayer(self.team, gn, x=px, y=py, isloc=True, lstcty=(i, j)))
                                    teams[self.team].alive_player_count += 1
                            if not only_log_ipt_cty or (i, j) in imp_ckp:
                                if wattr[i][j][0] == 0:
                                    log(gm.tick, "Team " + str(self.team) + f" captured your city '{ckp_nm[all_ckp.index((i, j))]}'!", (155, 155, 0))
                                if 0 == self.team:
                                    log(gm.tick, f"your team captured city '{ckp_nm[all_ckp.index((i, j))]}'!", (0, 155, 0))
                            wattr[i][j][0] = self.team
                            self.capturing = 0
                    if world[i][j] == 4 and wattr[i][j][0] == self.team and not self.islocal:
                        self.lstcty = i, j
                if not bb:
                    self.capturing = 0
        for i in self.touch_block():
            if i == 3:
                self.hp -= 0.1
                self.hurt = True
        if get_owner(int(self.x), int(self.y)) == self.team and gm.tick!=self.lstheal:
            self.hp += 0.2
            self.hp = min(self.hp, self.mxhp)
            self.lstheal = gm.tick
        if self.loadam != 0:
            self.loadam -= 1
            if self.loadam == 0:
                self.bllft = self.gun[2]
        strpos = (int(self.x)//csz, int(self.y)//csz)
        if strpos in nwentity:
            nwentity[strpos].append(self)
        else:
            nwentity[strpos] = [self]
        if get_owner(int(self.x), int(self.y)) == self.team:
            bl = False
            for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if 0 <= int(self.x) + i < wsize and 0 <= int(self.y) + j < wsize:
                    if get_owner(int(self.x) + i, int(self.y) + j) != self.team:
                        bl = True
                        break
            if bl:
                if self.typ == "ai":
                    build_wall(int(self.x), int(self.y))
        if gm.keys[pyge.constant.K_b]:
            self.cpi += 1
            if self.cpi >= 20:
                build_wall(int(self.x), int(self.y))
                self.cpi = 0
        if int(self.x) != self.lstpos[0] or int(self.y) != self.lstpos[1]:
            self.lstpos = (int(self.x), int(self.y))
            self.cpi = 0

    def shot(self, gm: pyge.Game, tx, ty):
        if self.loadam != 0:
            return
        if self.lstcld + self.gun[0] >= gm.tick:
            return
        self.lstcld = gm.tick
        tx = tx-self.x
        ty = ty-self.y
        tmp = math.sqrt(tx*tx+ty*ty)
        if tmp == 0:
            return
        dx, dy = tx/tmp, ty/tmp

        amp = 10000000
        for i in self.touch_block():
            amp = min(amp, blkattrs[i].amp)
        sx = self.x+self.pic.get_width()/64
        sy = self.y+self.pic.get_height()/64

        if world[int(self.x)][int(self.y)] == 6:
            blt = bullet(sx, sy, dx, dy, amp, self.name, sdt=self.team, dmg=1)
        else:
            blt = bullet(sx, sy, dx, dy, amp, self.name, sdt=self.team, dmg=self.gun[1])
        gm.add_obj(blt)
        self.bllft -= 1
        if self.bllft <= 0:
            self.loadam = self.gun[3]
    def cmoved(self, dx, dy):
        if abs(dx + dy) == 2:
            dx, dy = dx / 2, dy / 2
        spd = 1000000000000000
        for i in self.touch_block():
            spd = min(spd, blkattrs[i].spd)
        spd /= 5
        if self.x + dx * spd < 0 or self.x + dx * spd >= wsize or self.y + dy * spd < 0 or self.y + dy * spd >= wsize:
            return False
        all_pt = [(0, 0), (self.pic.get_width() / 32, 0), (0, self.pic.get_height() / 32),
                  (self.pic.get_width() / 32, self.pic.get_height() / 32)]
        for j, k in all_pt:
            if self.x + j + dx * spd < wsize and self.y + k + dy * spd < wsize and self.x + j < wsize and self.y + k < wsize and \
                    blkattrs[world[int(self.x + j + dx * spd)][int(self.y + k + dy * spd)]].amp - \
                    blkattrs[world[int(self.x + j)][int(self.y + k)]].amp > 1:
                if not (get_owner(int(self.x + j + dx * spd), int(self.y + k + dy * spd)) == self.team and world[int(self.x + j + dx * spd)][int(self.y + k + dy * spd)] == 5):
                    return False
            if self.x + j + dx * spd < wsize and self.y + k + dy * spd < wsize and self.x + j < wsize and get_owner(int(self.x + j + dx * spd), int(self.y + k + dy * spd)) != self.team and world[int(self.x + j + dx * spd)][int(self.y + k + dy * spd)] == 5:
                return False
        return True
    def moved(self, dx, dy):
        if self.cmoved(dx, dy):
            spd = 1000000000000000
            for i in self.touch_block():
                spd = min(spd, blkattrs[i].spd)
            spd /= 5
            if get_owner(int(x), int(y)) not in [self.team, -1]:
                spd /= 2
            self.x += dx*spd
            self.y += dy*spd
            return True
        else:
            return False

class aiplayer(player):
    def __init__(self, team, group="-1", hp=100, x=0, y=0, isloc=False, lstcty=None):
        super().__init__(team, hp, x, y, isloc=isloc)
        self.group = group
        self.attack = False
        groups[group].members.append(self.name)
        self.lm = (-1, -1)
        self.lm_t = 0
        self.targ = (-1, -1)
        self.lstdef = 0
        if lstcty is not None:
            self.lstcty = lstcty
    def getgrp(self):
        return self.group
    def update(self, gm: pyge.Game):
        self.check(gm)
        if self.hp <= 0:
            return
        # shot nearby opponent
        self.attack = False
        strg = self.gun[2] // csz
        for i in range(max(0, int(self.x) // csz - strg), min(wsize // csz, int(self.x) // csz + strg + 1)):
            for j in range(max(0, int(self.y) // csz - strg), min(wsize // csz, int(self.y) // csz + strg + 1)):
                if len(get_et(i, j)) > 0:
                    for k in get_et(i, j):
                        if k.team != self.team:
                            self.shot(gm, k.x, k.y)
                            self.attack = True
                            if world[i][j] == 4:
                                groups[self.group].act = True
                                groups[self.group].targ = (i, j)
                            break
        # move toward group target
        if groups[self.group].act:
            if self.targ[0] != -1:
                self.targ = (-1, -1)
            tx, ty = groups[self.group].targ
            if tx == -1 or ty == -1:
                pass
            elif tx == int(self.x) and ty == int(self.y):
                if self.targ in teams[self.team].csttarg.keys():
                    teams[self.team].csttarg.pop(self.targ)
            else:
                dx, dy = 0, 0
                if self.x < tx:
                    dx = 1
                elif self.x > tx:
                    dx = -1
                if self.y < ty:
                    dy = 1
                elif self.y > ty:
                    dy = -1
                self.moveai(gm, dx, dy, self.attack)
        elif groups[self.group].targ[0] != -1:
            if self.targ[0] == -1:
                if self.lstdef == 0:
                    self.targ = somewhere_nearby(groups[self.group].targ[0], groups[self.group].targ[1], 20)
                else:
                    self.targ = groups[self.group].targ
            tx, ty = self.targ
            dx, dy = 0, 0
            if self.x < tx:
                dx = 1
            elif self.x > tx:
                dx = -1
            if self.y < ty:
                dy = 1
            elif self.y > ty:
                dy = -1
            self.moveai(gm, dx, dy, self.attack)
            if int(self.x) == tx and int(self.y) == ty:
                if self.targ == groups[self.group].targ:
                    self.lstdef = 0
                else:
                    self.lstdef = 1
                self.targ = (-1, -1)
        groups[self.group].pos = self.x, self.y
    def moveai(self, gm: pyge.Game, dx, dy, no_straight=False):
        # if no_straight:
        #     if self.lm_t >= 40:
        #         if dx == 0:
        #             dx = random.randint(-1, 1)
        #         if dy == 0:
        #             dy = random.randint(-1, 1)
        #         self.lm = (dx, dy)
        #         self.lm_t = 0
        #     else:
        #         if dx == 0:
        #             dx = self.lm[0]
        #         if dy == 0:
        #             dy = self.lm[1]
        #         self.lm_t += 1
        bb = self.cmoved(dx, dy)
        if bb:
            self.moved(dx, dy)
        else:
            spd = 1000000000000000
            for i in self.touch_block():
                spd = min(spd, blkattrs[i].spd)
            spd /= 5
            self.shot(gm, self.x+dx*spd, self.y+dy*spd)
            self.moved(dx, 0)
            self.moved(0, dy)

def rect_alpha(w, h, color=(0, 0, 0, 255)):
    sf = pyge.pygame.Surface((w, h), pyge.pygame.SRCALPHA)
    sf.fill(color)
    return sf

#todo: game

if wmode:
    generate_world()
else:
    try:
        load_world_from_file(wname)
    except Exception as e:
        print("Error: the world file is corrupted or not exist!")
        raise e

class game(pyge.Game):
    totnm = 0
    def add_player(self, pl, nm=None):
        self.add_obj(pl, nm)
        all_plr.append(pl)
        self.totnm+=1
        return pl
    def setup(self):
        self.set_caption("blockwar - " + wname)
        self.add_event_listener(pyge.constant.QUIT, save_world)
        # setup players
        print("initializing entities...")
        if gamemode == 0:
            self.add_player(player(0, typ="human", hp=hp_), "hm_player")
            teams[0].alive_player_count += 1

        for k in range(teamn):
            gx, gy = random.randint(0, wsize-1), random.randint(0, wsize-1)
            cnt = 0
            while ((get_owner(gx, gy) != -1 and get_owner(gx, gy) != k) or world[gx][gy] == 4) and cnt<1000:
                gx, gy = random.randint(0, wsize-1), random.randint(0, wsize-1)
                cnt += 1
            if cnt == 1000:
                continue
            if k == 0:
                gx, gy = 0, 0
            for i in range(pit+(player_team_boost if k == 0 else 0)):
                gn = f"{random.randint(0, 10000000000)}"
                groups[gn] = group(k, gn, [])
                teams[k].gps.append(gn)
                gsx, gsy = somewhere_nearby(gx, gy, wsize//teamn//4)
                for j in range(pig):
                    px, py = somewhere_nearby(gsx, gsy, 5)
                    self.add_player(aiplayer(k, gn, x=px, y=py))
                    teams[k].alive_player_count += 1
        for i, j in all_ckp:
            if wattr[i][j][0] != -1:
                gn = f"{random.randint(0, 10000000000)}"
                groups[gn] = group(wattr[i][j][0], gn, [])
                teams[wattr[i][j][0]].gps.append(gn)
                gsx, gsy = somewhere_nearby(i, j, wsize // teamn // 4)
                for k in range(pig):
                    px, py = somewhere_nearby(gsx, gsy, 5)
                    self.add_player(aiplayer(wattr[i][j][0], gn, x=px, y=py, isloc=True, lstcty=(i, j)))
                    teams[wattr[i][j][0]].alive_player_count += 1
        print("Loaded total players:", self.totnm)
        # setup world

        # for i in range(0, wsize, 10):
        #     for j in range(0, wsize, 10):
        #         if i==0 or j==0:
        #             continue
        #         if world[i][j] == 0:
        #             world[i][j] = 1

        self.tick_rate = 33
        print("finished!")

    def update_back(self):
        global x, y, vx, vy, blksz
        self.sc.fill((30, 0, 30))
        vx = int(x) - WINSZ[0] // blksz // 2
        vy = int(y) - WINSZ[1] // blksz // 2
        if self.now_page == "main":
            if self.keys[pyge.constant.K_c]:
                blksz = 30
            else:
                blksz = 40
            will_draw = []
            for i in range(max(vx, 0), min(vx+WINSZ[0]//blksz+2, wsize)):
                for j in range(max(vy, 0), min(vy+WINSZ[1]//blksz+2, wsize)):
                    self.sc.blit(pyge.rect(blksz-is_spilt_line, blksz-is_spilt_line, blkattrs[world[i][j]].clr), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz))
                    if world[i][j] == 5 and get_owner(i, j) == 0:
                        self.sc.blit(pyge.rect(blksz - is_spilt_line, blksz - is_spilt_line, (150, 150, 150)), ((i - vx - x % 1) * blksz, (j - vy - y % 1) * blksz))
                    if world[i][j] == 5:
                        self.sc.blit(pyge.rect((wattr[i][j][1]/wall_hp)*blksz, 5, get_hp_clr(wattr[i][j][1], wall_hp)), ((i - vx - x % 1) * blksz, (j - vy - y % 1) * blksz))
                    if wattr[all_ckp[winsd[i][j]][0]][all_ckp[winsd[i][j]][1]][0] != -1 and world[i][j] == 0:
                        tc = teams[wattr[all_ckp[winsd[i][j]][0]][all_ckp[winsd[i][j]][1]][0]].clr
                        self.sc.blit(rect_alpha(blksz, blksz, (tc[0], tc[1], tc[2], 100)), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz))
                    if wattr[i][j][0] != -1:
                        self.sc.blit(pyge.rect(blksz//2, blksz//2, teams[wattr[i][j][0]].clr), ((i-vx-x%1)*blksz+blksz//4, (j-vy-y%1)*blksz+blksz//4))
                        if wattr[i][j] == 0:
                            if (i, j) in teams[0].defs.keys():
                                self.sc.blit(pyge.rect(blksz//2, blksz//2, teams[wattr[i][j][0]].clr), ((i-vx-x%1)*blksz+blksz, (j-vy-y%1)*blksz+blksz))
                    if world[i][j] == 4:
                        will_draw.append((ckp_nm[all_ckp.index((i, j))], (i-vx-x%1)*blksz+blksz//2, (j-vy-y%1)*blksz+blksz//2))
                    if spl:
                        if i-1>=0 and winsd[i][j] != winsd[i-1][j] and (get_owner(i-1, j) == 0 or get_owner(i, j) == 0):
                            pyge.pygame.draw.line(self.sc, (150, 150, 150), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz), ((i-vx-x%1)*blksz, (j-vy-y%1+1)*blksz), 2)
                        if j-1>=0 and winsd[i][j] != winsd[i][j-1] and (get_owner(i, j-1) == 0 or get_owner(i, j) == 0):
                            pyge.pygame.draw.line(self.sc, (150, 150, 150), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz), ((i-vx-x%1+1)*blksz, (j-vy-y%1)*blksz), 2)
            for i in will_draw:
                self.draw_text(i[0], i[1], i[2], color=(0, 0, 0))

            if allow_sight_away or gamemode == 1:
                if self.keys[pyge.constant.K_UP]:
                    y -= 1
                if self.keys[pyge.constant.K_DOWN]:
                    y += 1
                if self.keys[pyge.constant.K_LEFT]:
                    x -= 1
                if self.keys[pyge.constant.K_RIGHT]:
                    x += 1
            for i in teams:
                i.update(self)
                for j in i.gps:
                    groups[j].update(self)

    def update_front(self):
        global x, y, nwentity, entity
        if self.now_page == "main":
            entity = nwentity
            nwentity = {}
            if gamemode == 0:
                rp = self.get_obj("hm_player")
                if rp.hp > 0:
                    if not allow_sight_away:
                        rp.x = x
                        rp.y = y
                    if self.keys[pyge.constant.K_c]:
                        spd = 0.5
                    else:
                        spd = 1
                    if self.keys[pyge.constant.K_w]:
                        rp.moved(0, -spd)
                    if self.keys[pyge.constant.K_s]:
                        rp.moved(0, spd)
                    if self.keys[pyge.constant.K_a]:
                        rp.moved(-spd, 0)
                    if self.keys[pyge.constant.K_d]:
                        rp.moved(spd, 0)
                    if self.mouse_click[0] or self.keys[pyge.constant.K_SPACE]:
                        rp.shot(self, self.mouse_pos[0]//blksz+vx, self.mouse_pos[1]//blksz+vy)
                    if rp.x < 0:
                        rp.x = 0
                    if rp.y < 0:
                        rp.y = 0
                    if rp.x >= wsize:
                        rp.x = wsize - 1
                    if rp.y >= wsize:
                        rp.y = wsize - 1
                else:
                    self.sc.fill((0, 0, 0))
                    self.draw_text("You died!", WINSZ[0]//2-100, WINSZ[1]//2, 48, color=(255, 0, 0))
                    self.draw_text(f"You will respawn in {int(rp.respctd//self.tick_rate)} seconds...", WINSZ[0]//2-100, WINSZ[1]//2+50, 24, color=(255, 255, 255))
                rp.check(self)
                if rp.hurt:
                    rp.hurt = False
                    self.sc.blit(pyge.rect(WINSZ[0], 10, (255, 0, 0)), (0, 0))
                    self.sc.blit(pyge.rect(WINSZ[0], 10, (255, 0, 0)), (0, WINSZ[1] - 10))
                    self.sc.blit(pyge.rect(10, WINSZ[1], (255, 0, 0)), (0, 0))
                    self.sc.blit(pyge.rect(10, WINSZ[1], (255, 0, 0)), (WINSZ[0] - 10, 0))
                if not allow_sight_away:
                    x = rp.x
                    y = rp.y
            bx, by = 0, 0
            bsp = WINSZ[0]-wsize//2
            for j in range(0, wsize, 4):
                for i in range(0, wsize, 4):
                    posit = all_ckp[winsd[i][j]]
                    if wattr[posit[0]][posit[1]][0] == 0:
                        if (i, j) in teams[0].csttarg.keys():
                            teams[0].csttarg.pop((i, j))
                    else:
                        if (i, j) in teams[0].csttarg.keys():
                            self.sc.blit(pyge.rect(4, 4, (255, 0, 0)), (bsp + bx-1, by-1))
                            if self.mouse_click[0]:
                                if (self.mouse_pos[0] - bsp) // 2 == i//4 and self.mouse_pos[1] // 2 == j//4:
                                    teams[0].csttarg.pop((i, j))
                                    time.sleep(0.5)
                        else:
                            if self.mouse_click[0]:
                                if (self.mouse_pos[0]-bsp)//2 == i//4 and self.mouse_pos[1]//2 == j//4:
                                    teams[0].csttarg[(i, j)] = 0
                                    time.sleep(0.5)
                    if world[i][j] == 0 and wattr[posit[0]][posit[1]][0] != -1:
                        self.sc.blit(pyge.rect(2, 2, teams[wattr[posit[0]][posit[1]][0]].clr), (bsp+bx, by))
                    else:
                        self.sc.blit(pyge.rect(2, 2, blkattrs[world[i][j]].clr), (bsp + bx, by))
                    if int(x//4*4) == i and int(y//4*4) == j:
                        self.sc.blit(pyge.rect(4, 4, (0, 0, 0)), (bsp + bx-1, by-1))
                    bx += 2
                bx = 0
                by += 2
            if self.keys[pyge.constant.K_p]:
                teams[0].csttarg = {}
            yy = 10
            for i in msg:
                self.draw_text(i[1], 10, yy, color=i[2])
                yy += 30
            if len(msg) > 0:
                if self.tick-msg[0][0] > 90:
                    msg.pop(0)
        self.draw_text("fps: "+str(int(self.fps)), 10, 10, color=(0, 0, 0))
        self.draw_text("your team player counts: "+str(teams[0].alive_player_count), 10, 40, color=(0, 0, 0))

gm = game(sz=WINSZ)
gm.run()