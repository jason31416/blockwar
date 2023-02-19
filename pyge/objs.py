import pyge.game as game
import time

class Button(game.Picture):
    def __init__(self, sf: game.Surface, onclick, x=0, y=0):
        super().__init__(sf, x, y)
        self.onclick = onclick

    def update(self, gm):
        if self.collide():
            if gm.mouse_click[0]:
                self.onclick()

class Switch(game.Picture):
    def __init__(self, x=0, y=0, fgclr = (255,255,255), onclr = (0,255,0), offclr = (255,0,0)):
        sf = game.Surface((40, 20))
        sf.fill(offclr)
        sf2 = game.Surface((18, 18))
        sf2.fill(fgclr)
        sf.blit(sf2, (1, 1))
        self.onclr = onclr
        self.offclr = offclr
        self.fgclr = fgclr
        super().__init__(sf, x, y)
        self.on = False
        self.lstclick = 0

    def update(self, gm: game.Game):
        if self.collide() and gm.mouse_click[0] and time.time() - self.lstclick > 0.4:
            self.on = not self.on
            self.pic.fill(self.onclr if self.on else self.offclr)
            sf2 = game.Surface((18, 18))
            sf2.fill(self.fgclr)
            self.pic.blit(sf2, ((1, 1) if not self.on else (21, 1)))
            self.lstclick = time.time()