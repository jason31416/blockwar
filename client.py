"""
client v 1.0.1, blockwar v 1.4.3
"""


version = (1, 4, 3)
support_save_version = [(1, 4, 3)]

import math
import time
import pyge
import os
from functions import *
import socket
import threading

WINSZ = (800, 600)

# Initialize files

if not os.path.exists("saves"):
    os.mkdir("saves")

all_saves = os.listdir("saves")

# new world
wsize = 150
x, y = 0, 0
blksz = 20
vx = x-WINSZ[0]//blksz//2
vy = y-WINSZ[1]//blksz//2
csz = 4
cn = wsize//csz
gamemode = 0 # 0: normal 1: spectator
cty_count = 70
teamn = 4
player_team_boost = 6
only_log_ipt_cty = False

# input wname

svname = input("Server ip:")
if svname == "":
    svname = "0.0.0.0:25465"

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("connecting...")
sk.connect((svname.split(":")[0], int(svname.split(":")[1])))
print("connected!")
sdt = sk.recv(1024).decode("utf-8")
print("server: ", sdt)
if sdt != "hello":
    sk.close()
    print("invalid server!")
    exit(0)
# todo: 0.0.0.0:25465
sk.send(f"blockwar v{version[0]}.{version[1]}.{version[2]}".encode("utf-8"))

wsdts = ""
nws = ""
cnt = 0

while True:
    nws = sk.recv(2048).decode("utf-8")
    print("recved "+nws)
    if nws == "!end":
        break
    wsdts += nws+"\n"
    sk.send(b"ok")
    cnt += 1
    if cnt >= 1000:
        print("too many lines!")
        exit(0)

sk.send(b"ok")

plname = sk.recv(1024).decode("utf-8")
sk.send(b"ok")

wsdt = wsdts.split("\n-\n")

wsize, teamn = int(wsdt[0].split(" ")[0]), int(wsdt[0].split(" ")[1])

# functions

class obj(pyge.Picture):
    def __init__(self, sf, x=-1, y=-1):
        super().__init__(sf, 0, 0)
        self.x, self.y = x, y

    def draw(self, gm: pyge.Game):
        self.pos_in_world()
        if vx <= self.x < vx+WINSZ[0]//blksz and vy <= self.y < vy + WINSZ[1] // blksz:
            gm.sc.blit(to_siz(self.pic, (blksz*(self.pic.get_width()/32), blksz*(self.pic.get_height()/32))), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz))

world = [[0]*wsize for i in range(wsize)]
wattr = [[[-1, 0, 0] for j in range(wsize)] for i in range(wsize)]
winsd = [[-1 for j in range(wsize)] for i in range(wsize)]

# print(wsdt)

for i in range(wsize):
    rw = wsdt[1].split("\n")[i].split(" ")
    for j in range(wsize):
        try:
            world[i][j] = int(rw[j])
        except IndexError:
            print(i, j)
            exit(1)

for i in range(wsize):
    rw = wsdt[2].split("\n")[i].split(" ")
    for j in range(wsize):
        winsd[i][j] = int(rw[j])

for i in range(wsize):
    rw = wsdt[3].split("\n")[i].split(" ")
    for j in range(wsize):
        wattr[i][j] = [int(rw[j].split(",")[0]), int(rw[j].split(",")[1]), int(rw[j].split(",")[2])]

all_ckp = []
ckp_nm = []
for i in wsdt[5].split("\n"):
    if i == "":
        continue
    all_ckp.append((int(i.split(",")[0]), int(i.split(",")[1])))
    ckp_nm.append(i.split(",")[2])

blkattrs = {0: (200, 200, 200), 1: (100, 100, 100), 2: (0, 0, 50), 3: (255, 0, 0), 4: (255, 255, 0), 5: (100, 100, 100)}
# 0: empty, 1: obstacle, 2: road 3: lava 4: city

teams = []

all_plr = []

msg = []

# gun: (cooldown, power, range, damage)

for i in range(teamn):
    teams.append((random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))

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


def get_owner(x, y):
    return wattr[all_ckp[winsd[x][y]][0]][all_ckp[winsd[x][y]][1]][0]

class player(obj):
    def __init__(self, team, hp, x, y):
        self.hp = hp
        self.mxhp = 100
        super().__init__(pyge.rect(32, 32, teams[team]), x, y)

    def draw(self, gm: pyge.Game):
        if self.hp <= 0:
            return
        if vx <= self.x < vx+WINSZ[0]//blksz and vy <= self.y < vy + WINSZ[1] // blksz:
            gm.sc.blit(to_siz(self.pic, (blksz*(self.pic.get_width()/32), blksz*(self.pic.get_height()/32))), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz))
            gm.sc.blit(pyge.rect((self.hp/self.mxhp)*blksz, 5, get_hp_clr(self.hp, self.mxhp)), ((self.x-vx-x%1)*blksz, (self.y-vy-y%1)*blksz-10))

def rect_alpha(w, h, color=(0, 0, 0, 255)):
    sf = pyge.pygame.Surface((w, h), pyge.pygame.SRCALPHA)
    sf.fill(color)
    return sf

wall_hp = 60
is_spilt_line = 0
spl = True
gm = None
ept = 0

class game(pyge.Game):
    def add_player(self, pl, nm=None):
        self.add_obj(pl, nm)
        all_plr.append(pl)

    def setup(self):
        global gm
        gm = self
        self.set_caption("blockwar - " + svname)
        for i in wsdt[4].split("\n"):
            self.add_player(player(int(i.split(",")[3]), float(i.split(",")[2]), float(i.split(",")[0]), float(i.split(",")[1])), i.split(",")[4])
        self.tick_rate = 33
        print("finished!")

    def update_back(self):
        global x, y, vx, vy, blksz
        self.sc.fill((30, 0, 30))
        blksz = 30
        try:
            x, y = self.get_obj(plname).x, self.get_obj(plname).y
        except KeyError:
            return
        vx = int(x) - WINSZ[0] // blksz // 2
        vy = int(y) - WINSZ[1] // blksz // 2
        if self.now_page == "main":
            will_draw = []
            for i in range(max(vx, 0), min(vx+WINSZ[0]//blksz+2, wsize)):
                for j in range(max(vy, 0), min(vy+WINSZ[1]//blksz+2, wsize)):
                    self.sc.blit(pyge.rect(blksz, blksz, blkattrs[world[i][j]]), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz))
                    if world[i][j] == 5 and get_owner(i, j) == 0:
                        self.sc.blit(pyge.rect(blksz, blksz, (150, 150, 150)), ((i - vx - x % 1) * blksz, (j - vy - y % 1) * blksz))
                    if world[i][j] == 5:
                        self.sc.blit(pyge.rect((wattr[i][j][1]/wall_hp)*blksz, 5, get_hp_clr(wattr[i][j][1], wall_hp)), ((i - vx - x % 1) * blksz, (j - vy - y % 1) * blksz))
                    if wattr[all_ckp[winsd[i][j]][0]][all_ckp[winsd[i][j]][1]][0] != -1 and world[i][j] == 0:
                        tc = teams[wattr[all_ckp[winsd[i][j]][0]][all_ckp[winsd[i][j]][1]][0]]
                        self.sc.blit(rect_alpha(blksz, blksz, (tc[0], tc[1], tc[2], 100)), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz))
                    if wattr[i][j][0] != -1:
                        self.sc.blit(pyge.rect(blksz//2, blksz//2, teams[wattr[i][j][0]]), ((i-vx-x%1)*blksz+blksz//4, (j-vy-y%1)*blksz+blksz//4))
                        if wattr[i][j] == 0:
                            if (i, j) in teams[0].defs.keys():
                                self.sc.blit(pyge.rect(blksz//2, blksz//2, teams[wattr[i][j][0]]), ((i-vx-x%1)*blksz+blksz, (j-vy-y%1)*blksz+blksz))
                    if world[i][j] == 4:
                        will_draw.append((ckp_nm[all_ckp.index((i, j))], (i-vx-x%1)*blksz+blksz//2, (j-vy-y%1)*blksz+blksz//2))
                    if spl:
                        if i-1>=0 and winsd[i][j] != winsd[i-1][j] and (get_owner(i-1, j) == 0 or get_owner(i, j) == 0):
                            pyge.pygame.draw.line(self.sc, (150, 150, 150), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz), ((i-vx-x%1)*blksz, (j-vy-y%1+1)*blksz), 2)
                        if j-1>=0 and winsd[i][j] != winsd[i][j-1] and (get_owner(i, j-1) == 0 or get_owner(i, j) == 0):
                            pyge.pygame.draw.line(self.sc, (150, 150, 150), ((i-vx-x%1)*blksz, (j-vy-y%1)*blksz), ((i-vx-x%1+1)*blksz, (j-vy-y%1)*blksz), 2)
            for i in will_draw:
                self.draw_text(i[0], i[1], i[2], color=(0, 0, 0))

    def update_front(self):
        global x, y, kev
        bsp = 700
        if self.now_page == "main":
            bx = 0
            by = 0
            for j in range(0, wsize, 4):
                for i in range(0, wsize, 4):
                    posit = all_ckp[winsd[i][j]]
                    if world[i][j] == 0 and wattr[posit[0]][posit[1]][0] != -1:
                        self.sc.blit(pyge.rect(2, 2, teams[wattr[posit[0]][posit[1]][0]]), (bsp+bx, by))
                    else:
                        self.sc.blit(pyge.rect(2, 2, blkattrs[world[i][j]]), (bsp + bx, by))
                    if int(x//4*4) == i and int(y//4*4) == j:
                        self.sc.blit(pyge.rect(4, 4, (0, 0, 0)), (bsp + bx-1, by-1))
                    bx += 2
                bx = 0
                by += 2
            if self.keys[pyge.pygame.K_w]:
                kev += "w "
            if self.keys[pyge.pygame.K_s]:
                kev += "s "
            if self.keys[pyge.pygame.K_a]:
                kev += "a "
            if self.keys[pyge.pygame.K_d]:
                kev += "d "
            if self.mouse_click[0]:
                kev += f"st,{self.mouse_pos[0]//blksz+vx},{self.mouse_pos[1]//blksz+vy} "
            yy = 10
            for i in msg:
                self.draw_text(i[1], 10, yy, color=i[2])
                yy += 30
            if len(msg) > 0:
                if self.tick-msg[0][0] > 90:
                    msg.pop(0)
        self.draw_text("tps: "+str(int(self.fps)), 10, 10, color=(0, 0, 0))
        self.draw_text("ept: "+str(int(ept)), 10, 30, color=(0, 0, 0))

kev = "n"

def update_socket():
    global ept, kev
    while True:
        pkts = ""
        cnt = 0
        while True:
            nws = sk.recv(2048).decode("utf-8")
            # print("recved " + nws)
            if nws == "!end":
                sk.send(b"ok")
                break
            pkts += nws + "\n"
            sk.send(b"ok")
            cnt += 1
            if cnt >= 50000:
                print("too many lines!")
                exit(0)
        ept = cnt
        # print(len(pkts.split("\n")), pkts.split("\n")[0])
        for i in pkts.split("\n"):
            # print("!!!2")
            ev = i.split(" ")[0]
            args = i.split(" ")[1:]
            if ev == "bc":
                world[int(args[0])][int(args[1])] = int(args[2])
                wattr[int(args[0])][int(args[1])] = [int(args[3]), int(args[4]), int(args[5])]
            elif ev == "ec":
                while gm is None:
                    pass
                tpl = gm.get_obj(args[0])
                tpl.x = float(args[1])
                tpl.y = float(args[2])
                tpl.hp = float(args[3])
                # if args[0] == plname:
                #     print("pl:", tpl.x, tpl.y, tpl.hp)
            elif ev == "er":
                while gm is None:
                    pass
                gm.rem_obj(args[0])
            elif ev == "ecr":
                while gm is None:
                    pass
                gm.add_player(player(int(args[1]), float(args[2]), float(args[3]), float(args[4])), args[0])
        sk.send(kev.encode("utf-8"))
        kev = "n"
        # dt = sk.recv(1024).decode("utf-8")
        # print(dt)
        # if dt != "ok":
        #     print("server internal error")
        #     exit(0)
        # sk.send(b"ok")


threading.Thread(target=update_socket).start()

gm = game()
gm.run()