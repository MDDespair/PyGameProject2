from pygame.image import load
from pygame.sprite import Sprite
from os import path
from sys import exit
from pygame import Rect


def load_image(name, colorkey=None, folder='data'):
    fullPath = path.join(folder, name)
    if not path.isfile(fullPath):
        print(fullPath)
        exit()
    image = load(fullPath)
    return image


class MouseLocationSprite(Sprite):
    def __init__(self, pos):
        super().__init__()
        self.rect = Rect(pos, (1, 1))
