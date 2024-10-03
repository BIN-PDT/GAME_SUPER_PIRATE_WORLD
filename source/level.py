from settings import *

from groups import AllSprites
from player import Player
from sprites import *


class Level:
    def __init__(self, tmx_map, assets):
        self.screen = pygame.display.get_surface()
        # GROUP.
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semicollision_sprites = pygame.sprite.Group()

        self.load_data(tmx_map, assets)

    def load_data(self, tmx_map, assets):
        # TILES.
        for layer in ("BG", "Terrain", "FG", "Platforms"):
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain":
                    groups.append(self.collision_sprites)
                elif layer == "Platforms":
                    groups.append(self.semicollision_sprites)

                if layer == "BG":
                    z = Z_LAYERS["bg tiles"]
                elif layer == "FG":
                    z = Z_LAYERS["fg"]
                else:
                    z = Z_LAYERS["main"]

                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)
        # OBJECT.
        for obj in tmx_map.get_layer_by_name("Objects"):
            name = obj.name
            pos = (obj.x, obj.y)

            if name == "player":
                self.player = Player(
                    pos=pos,
                    groups=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    semicollision_sprites=self.semicollision_sprites,
                )
            else:
                if name in ("barrel", "crate"):
                    Sprite(
                        pos=pos,
                        surf=obj.image,
                        groups=(self.all_sprites, self.collision_sprites),
                    )
                else:
                    frames = assets["palms"][name] if "palm" in name else assets[name]
                    AnimatedSprite(pos, frames, self.all_sprites)
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
