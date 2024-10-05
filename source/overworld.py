from settings import *

from groups import WorldSprite
from sprites import *


class Overworld:
    def __init__(self, tmx_map, assets, data):
        self.screen = pygame.display.get_surface()
        self.data = data
        # GROUP.
        self.all_sprites = WorldSprite(self.data)
        # SETUP.
        self.load_data(tmx_map, assets)

    def load_data(self, tmx_map, assets):
        # TILES.
        for layer in ("main", "top"):
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                    surf=surface,
                    groups=self.all_sprites,
                    z=Z_LAYERS["bg tiles"],
                )
        # WATER.
        for row in range(tmx_map.height):
            for col in range(tmx_map.width):
                AnimatedSprite(
                    pos=(col * TILE_SIZE, row * TILE_SIZE),
                    frames=assets["water"],
                    groups=self.all_sprites,
                    z=Z_LAYERS["bg"],
                )
        # OBJECTS.
        for obj in tmx_map.get_layer_by_name("Objects"):
            name = obj.name
            pos = obj.x, obj.y

            if name == "palm":
                AnimatedSprite(
                    pos=pos,
                    frames=assets["palms"],
                    groups=self.all_sprites,
                    animation_speed=randint(4, 6),
                )
            else:
                z = Z_LAYERS["bg tiles"] if name == "stone" else Z_LAYERS["bg details"]
                Sprite(pos, obj.image, self.all_sprites, z)
        # NODE & PLAYER.
        for obj in tmx_map.get_layer_by_name("Nodes"):
            name = obj.name
            pos = obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2

            if name == "Node":
                Node(
                    pos=pos,
                    surf=assets["path"]["node"],
                    groups=self.all_sprites,
                    data=self.data,
                    level=obj.properties["stage"],
                )
                # PLAYER.
                if obj.properties["stage"] == self.data.current_level:
                    self.icon = Icon(pos, assets["icon"], self.all_sprites)

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon.rect.center)
