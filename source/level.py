from settings import *

from groups import AllSprites
from player import Player
from sprites import *


class Level:
    def __init__(self, tmx_map):
        self.screen = pygame.display.get_surface()
        # GROUP.
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semicollision_sprites = pygame.sprite.Group()

        self.load_data(tmx_map)

    def load_data(self, tmx_map):
        # TERRAIN.
        for x, y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
            Sprite(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                surf=surf,
                groups=(self.all_sprites, self.collision_sprites),
            )
        # OBJECT.
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    semicollision_sprites=self.semicollision_sprites,
                )
        # MOVING OBJECT.
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "helicopter":
                width, height = obj.width, obj.height
                pos = obj.x, obj.y
                speed = obj.properties["speed"]
                if width > height:
                    axis = "X"
                    start_pos = pos[0], pos[1] + height / 2
                    end_pos = pos[0] + width, pos[1] + height / 2
                else:
                    axis = "Y"
                    start_pos = pos[0] + width / 2, pos[1]
                    end_pos = pos[0] + width / 2, pos[1] + height

                MovingSprite(
                    groups=(self.all_sprites, self.semicollision_sprites),
                    start_pos=start_pos,
                    end_pos=end_pos,
                    axis=axis,
                    speed=speed,
                )

    def run(self, dt):
        self.all_sprites.update(dt)
        self.screen.fill("black")
        self.all_sprites.draw(self.player.hitbox.center)
