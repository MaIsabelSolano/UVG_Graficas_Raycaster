import pygame
import random
from math import cos, sin, pi, atan2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 0, 200)
TRANSPARENT = (152, 0, 136, 255)

colors = [
    (255, 210, 42),
    (210, 100, 200),
    (238, 239, 168),
    (238, 239, 168),
    (238, 239, 168)
]

walls = {
    "0": pygame.image.load('./materials/wall1.png'),
    "1": pygame.image.load('./materials/wall2.png'),
    "2": pygame.image.load('./materials/wall3.png'),
    "3": pygame.image.load('./materials/wall4.png'),
    "4": pygame.image.load('./materials/wall5.png')
}

sprites = {
    "0": pygame.image.load('./materials/sprite1.png'),
    "1": pygame.image.load('./materials/sprite2.png'),
    "2": pygame.image.load('./materials/sprite3.png'),
    "3": pygame.image.load('./materials/sprite4.png'),
}

enemies = [
    {
        "x": 100,
        "y": 100,
        "sprite": sprites["0"]
    },
    {
        "x": 400,
        "y": 100,
        "sprite": sprites["1"]
    },

]

class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()
        self.blocksize = 50
        self.map = []
        self.zbuffer = [99999 for z in range(0, int(self.width /2))]
        self.player = {
            "x": int(self.blocksize + self.blocksize/2),
            "y": int(self.blocksize + self.blocksize/2),
            "fov": int(pi/3), 
            "a": pi/3
        }

    def clearZ(self):
        self.zbuffer = [99999 for z in range(0, int(self.width / 2))]

    def point(self, x, y, c = WHITE):
        self.screen.set_at((x, y), c)

    def block(self, x, y, texture):
        for i in range(x, x + self.blocksize):
            for j in range(y, y + self.blocksize):
                tx = int((i - x) * 128 / self.blocksize)
                ty = int((j - y) * 128 / self.blocksize)
                c = texture.get_at((tx, ty))
                self.point(i, j, c)

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def cast_ray(self, a):
        d = 0
        ox = self.player["x"]
        oy = self.player["y"]

        while True:
            x = int(ox + d * cos(a))
            y = int(oy + d * sin(a))

            j = int(x/self.blocksize)
            i = int(y/self.blocksize)

            if self.map[i][j] != ' ':
                hitx = x - j * self.blocksize
                hity = y - i * self.blocksize

                if 1 < hitx < self.blocksize - 1:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / self.blocksize)
                return d, self.map[i][j], tx

            self.point(x, y, (255, 100, 100))

            d += 1

    def draw_map(self):
        for x in range(0, 500, self.blocksize):
            for y in range(0, 500, self.blocksize):

                j = int(x/self.blocksize)
                i = int(y/self.blocksize)

                if self.map[i][j] != ' ':
                    c = walls[self.map[i][j]]
                    self.block(x, y, c)

    def draw_strip(self, x, h, c, tx):
        
        start_y = int(self.height/2 - h/2)
        end_y = int(self.height/2 + h/2)
        alto = end_y - start_y

        for y in range(start_y, end_y):
            ty = int((y - start_y) * 128 / alto)
            texture_c = walls[c].get_at((tx, ty))
            self.point(x, y, texture_c)

    def draw_player(self):
        self.point(self.player["x"], self.player["y"])

    def draw_sprite(self, enemy):
        sprite_a = atan2(
            enemy["y"] - self.player["y"],    
            enemy["x"] - self.player["x"],    
        )

        png_size = 128

        # distance calculation
        d = (
            (self.player["x"] - enemy["x"]) **2 +
            (self.player["y"] - enemy["y"]) **2
            ) **0.5

        sprite_size = int((500 / d) * (500 / 20))

        sprite_x = int(
            500 + # offset
            (sprite_a - self.player["a"]) * 500 /self.player["fov"] +
            (500 / 2) -
            sprite_size/2 #center sprite
            )
        sprite_y = int((self.height / 2) - (sprite_size / 2))

        for x in range(sprite_x, sprite_x + sprite_size):
            if 1000 > x > 500: # The enemy is not render over the minimap
                if self.zbuffer[x - 500] >= d:
                    for y in range(sprite_y, sprite_y + sprite_size):
                        tx = int((x - sprite_x) * png_size / sprite_size)
                        ty = int((y - sprite_y) * png_size / sprite_size)
                        
                        c = enemy["sprite"].get_at((tx, ty))

                        self.zbuffer[x - 501] = d

                        # removes purple background
                        if c != TRANSPARENT:
                            self.point(x, y, c)

    def render(self):
        self.draw_map()
        self.draw_player()

        density = 100

        # minimap

        # for i in range(0, density):
        #     a = self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/density
        #     d, c, _ = self.cast_ray(a)


        # 3D Map

        for i in range(0, int(self.width/2)):
            a = self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/(self.width/2)
            d, c, tx = self.cast_ray(a)

            if d <= 0:
                0

            x = int(self.width/2 + i)
            h = self.width/(d * cos(a - self.player["a"])) * self.height/25
            
            if self.zbuffer[i] >= d:
                self.draw_strip(x, h, c, tx)
                self.zbuffer[i] = d

        # Enemies

        # Minimap

        for enemy in enemies:
            self.point(enemy["x"], enemy["y"], (0, 0, 200))

        # 3D
        for enemy in enemies:
            self.draw_sprite(enemy)

        # Division
        
        for i in range(0, 500):
            self.point(499, i)
            self.point(500, i)
            self.point(501, i)
    

pygame.init()
screen = pygame.display.set_mode((1000, 500))
r = Raycaster(screen)
r.load_map('./map.txt')

runnig = True
while runnig:
    screen.fill(BLACK) # floor
    screen.fill(GRAY, (r.width/2, 0, r.width, r.height/2)) # sky

    r.clearZ()

    r.render()

    pygame.display.flip()

    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            runnig = False

        if (event.type == pygame.KEYDOWN):
            if event.key == pygame.K_RIGHT:
                r.player["x"] -= int(5 * sin(r.player["a"]))
                r.player["y"] += int(5 * cos(r.player["a"]))
            if event.key == pygame.K_LEFT:
                r.player["x"] += int(5 * sin(r.player["a"]))
                r.player["y"] -= int(5 * cos(r.player["a"]))
            if event.key == pygame.K_UP:
                r.player["x"] += int(5 * cos(r.player["a"]))
                r.player["y"] += int(5 * sin(r.player["a"]))
            if event.key == pygame.K_DOWN:
                r.player["x"] -= int(5 * cos(r.player["a"]))
                r.player["y"] -= int(5 * sin(r.player["a"]))

            if event.key == pygame.K_a:
                r.player["a"] -= pi/10
            if event.key == pygame.K_d:
                r.player["a"] += pi/10
