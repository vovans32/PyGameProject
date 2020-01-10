import os
import sys

import pygame


def start_screen():
    fon = pygame.transform.scale(load_image('cover.jpg'), size)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


def load_image(name, way='data', colorkey=None):
    fullname = os.path.join(way, name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
        pass
    return image


def load_level(filename):
    global level_map, objects
    objects = []
    filename = 'data/levels/' + filename + ('.txt' if not filename.endswith('.txt') else '')
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for j, line in enumerate(level_map):
        for i, obj in enumerate(level_map[j]):
            if obj == '#':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      True, 'mole.png'))
            elif obj == 'a':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      False, 'apple.png'))
            elif obj == 'c':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      False, 'carrot.png'))
            elif obj == 'l':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      False, 'lemon.png'))
            elif obj == 'r':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      False, 'radish.png'))
            elif obj == 's':
                objects.append(Object(all_sprites, cell_size * i, cell_size * j,
                                      False, 'strawberry.png'))


def terminate():
    pygame.quit()
    sys.exit()


def new_coords(coords):
    if abs(coords[0][0] - coords[1][0]) >= W // 1.5 or \
            abs(coords[0][1] - coords[1][1]) >= H // 1.5:
        x_0, y_0 = coords[1]
        x_1, y_1 = coords[2]
    else:
        x_0, y_0 = coords[0]
        x_1, y_1 = coords[1]
    x_n, y_n = coords[-1]
    px = x_n + x_1 - x_0
    py = y_n + y_1 - y_0
    if coords[-1][0] > W:
        px = 0
    if coords[-1][0] < 0:
        px = W
    if coords[-1][1] > H:
        py = 0
    if coords[-1][1] < 0:
        py = H

    coords = coords[1:] + [[px, py]]

    return coords


class Object(pygame.sprite.Sprite):
    def __init__(self, group, x, y, isObstacle, image_name, def_image_name=None):
        super().__init__(group)
        print(x, y)
        self.x = x
        self.y = y
        self.isObstacle = isObstacle
        self.defeated = False
        self.image = pygame.transform.scale(load_image('characters/' + image_name),
                                            (cell_size, cell_size))
        self.mask = pygame.mask.from_surface(self.image)
        # if not isObstacle:
        #     self.def_image = load_image('data/characters/' + def_image_name)
        self.rect = pygame.Rect(x - cell_size, y - cell_size, x, y)
        print(self.rect)


class MainObject:
    def __init__(self, *move):
        if type(move) is not list:
            move = [move]
        else:
            move = move[0]
        self.move = [_ for _ in move]
        self.len = len(self.move)

    def go(self):
        try:
            if not self.move[0]:
                return
        except IndexError:
            return
        self.len = len(self.move)
        self.move = new_coords(self.move)

    def erase(self):
        self.move = self.move[1:]

    def append(self, coord):
        self.move.append(coord)

    def clear(self):
        self.move = []

    def __len__(self):
        return len(self.move)

    def __str__(self):
        return str(self.move)


pygame.init()

# size = W, H = pygame.display.Info().current_w, pygame.display.Info().current_h
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

size = W, H = 889, 500
screen = pygame.display.set_mode((W, H))

fon = pygame.transform.scale(load_image('grass.jpg'), (W, H))

clock = pygame.time.Clock()
fps = 60

step = 1
thickness = 16
cell_size = 28

main_object_color = pygame.Color('#490700')


all_sprites = pygame.sprite.Group()

load_level('level1')

start_screen()

running = True
isMainObjectCreation = isGameLost = isGameWon = False
main_object = MainObject()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYUP and event.key == 27:
            screen = pygame.display.set_mode((889, 500))
            size = W, H = 500, 889

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            main_object.clear()
            main_object.append(list(event.pos))
            isMainObjectCreation = True
            for i in objects:
                i.defeated = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if isMainObjectCreation:
                main_object.append(list(event.pos))
            isMainObjectCreation = False
            for i in objects:
                i.defeated = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            main_object.clear()
            main_object.append(None)
            for i in objects:
                i.defeated = False

        if event.type == pygame.MOUSEMOTION:
            if isMainObjectCreation:
                main_object.append(list(event.pos))

    for i in objects:
        try:
            x1, y1 = main_object.move[-1]
            if (i.x - x1) ** 2 + (i.y - y1) ** 2 <= cell_size ** 2:
                i.defeated = True
        except:
            pass
    try:
        for i in range(0, len(main_object) - 1, step):
            from_coord = main_object.move[i]
            to_coord = main_object.move[i + 1]
            if abs(from_coord[0] - to_coord[0]) > W // 2 or abs(from_coord[1] - to_coord[1]) > H:
                continue
            if from_coord[0] and to_coord[0]:
                pygame.draw.line(screen, main_object_color,
                                 from_coord, to_coord, thickness)
            if i == 0:
                pygame.draw.circle(screen, main_object_color, from_coord, 8)
            elif i == len(main_object) - 2:
                pygame.draw.circle(screen, main_object_color, from_coord, 8)
    except IndexError:
        pass

    if any([_.defeated for _ in objects]) and isMainObjectCreation:
        isMainObjectCreation = False
    elif any([_.defeated and _.isObstacle for _ in objects]):
        isGameLost = True
    elif all([_.defeated != _.isObstacle for _ in objects]):
        isGameWon = True

    if isGameLost:
        main_object.erase()
        if not main_object:
            isGameLost = False
            print('-')
    elif isGameWon:
        main_object.erase()
        if not main_object:
            isGameWon = False
            print('+')
    elif not isMainObjectCreation:
        main_object.go()

    clock.tick(fps)

    pygame.display.flip()
    pygame.display.set_caption("fps: " + str(clock.get_fps()))

    screen.blit(fon, (0, 0))
    all_sprites.draw(screen)

pygame.quit()
