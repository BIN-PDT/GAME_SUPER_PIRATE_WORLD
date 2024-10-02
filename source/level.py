from settings import *

from player import Player
from sprites import *


class Level:
    def __init__(self, tmx_map):
        self.screen = pygame.display.get_surface()
        # GROUP.
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.load_data(tmx_map)

    def load_data(self, tmx_map):
        for x, y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
            Sprite(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                surf=surf,
                groups=(self.all_sprites, self.collision_sprites),
            )

        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)

    def run(self, dt):
        self.all_sprites.update(dt)
        self.screen.fill("black")
        self.all_sprites.draw(self.screen)
