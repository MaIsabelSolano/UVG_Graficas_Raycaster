import pygame
import random
from math import cos, sin, pi

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

colors = [
    (255, 210, 42),
    (210, 100, 200),
    (238, 239, 168)
]

class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()
        self.blocksize = 50
        self.map = []
        self.player = {
            "x": int(self.blocksize + self.blocksize/2),
            "y": int(self.blocksize + self.blocksize/2),
            "fov": int(pi/3), 
            "a": int(pi/3)
        }

    def point(self, x, y, c = WHITE):
        self.screen.set_at((x, y), c)

    def block(self, x, y, c = WHITE):
        for i in range(x, x + self.blocksize + 1):
            for j in range(y, y + self.blocksize + 1):
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
                return d, colors[int(self.map[i][j])]

            self.point(x, y, (255, 100, 100))
            d += 5

    def draw_map(self):
        for x in range(0, 500, self.blocksize):
            for y in range(0, 500, self.blocksize):

                j = int(x/self.blocksize)
                i = int(y/self.blocksize)

                if self.map[i][j] != ' ':
                    c = colors[int(self.map[i][j])]
                    self.block(x, y, c)

    def draw_strip(self, x, h, c):
        
        start_y = int(self.height/2 - h/2)
        end_y = int(self.height/2 + h/2)

        for y in range(start_y, end_y):
            self.point(x, y, c)

    def draw_player(self):
        self.point(self.player["x"], self.player["y"])

    def render(self):
        self.draw_map()
        self.draw_player()

        density = 100

        # minimap

        for i in range(0, density):
            a = self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/density
            d, c = self.cast_ray(a)

        # Division
        
        for i in range(0, 500):
            self.point(499, i)
            self.point(500, i)
            self.point(501, i)

        # 3D Map

        for i in range(0, density):
            a = self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/density
            d, c = self.cast_ray(a)

            x = int(self.width/2 + i)
            h = self.width/(d * cos(a - self.player["a"])) * 100
            
            self.draw_strip(x, h, c)
    

pygame.init()
screen = pygame.display.set_mode((1000, 500))
r = Raycaster(screen)
r.load_map('./map.txt')

runnig = True
while runnig:
    screen.fill(BLACK)

    r.render()

    pygame.display.flip()

    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            runnig = False

        if (event.type == pygame.KEYDOWN):
            if event.key == pygame.K_RIGHT:
                r.player["x"] += 10
            if event.key == pygame.K_LEFT:
                r.player["x"] -= 10
            if event.key == pygame.K_UP:
                r.player["y"] -= 10
            if event.key == pygame.K_DOWN:
                r.player["y"] += 10

            if event.key == pygame.K_a:
                r.player["a"] -= pi/10
            if event.key == pygame.K_d:
                r.player["a"] += pi/10
