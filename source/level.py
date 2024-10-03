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
        self.damage_sprites = pygame.sprite.Group()

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

                if layer == "BG" or layer == "FG":
                    z = Z_LAYERS["bg tiles"]
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
                    frames=assets["player"],
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
            name = obj.name
            pos = obj.x, obj.y
            size = obj.width, obj.height

            if name == "spike":
                center = pos[0] + size[0] / 2, pos[1] + size[1] / 2
                radius, speed = obj.properties["radius"], obj.properties["speed"]
                start_angle = obj.properties["start_angle"]
                end_angle = obj.properties["end_angle"]

                Spike(
                    pos=center,
                    surf=assets["spike"],
                    groups=(self.all_sprites, self.damage_sprites),
                    radius=radius,
                    speed=speed,
                    start_angle=start_angle,
                    end_angle=end_angle,
                )
                # PATH OF SPIKE.
                for radius in range(0, obj.properties["radius"], 20):
                    Spike(
                        pos=center,
                        surf=assets["spike_chain"],
                        groups=self.all_sprites,
                        radius=radius,
                        speed=speed,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        z=Z_LAYERS["bg details"],
                    )
            else:
                frames = assets[name]
                groups = [self.all_sprites]
                if obj.properties["platform"]:
                    groups.append(self.semicollision_sprites)

                if size[0] > size[1]:
                    axis = "X"
                    start_pos = pos[0], pos[1] + size[1] / 2
                    end_pos = pos[0] + size[0], pos[1] + size[1] / 2
                else:
                    axis = "Y"
                    start_pos = pos[0] + size[0] / 2, pos[1]
                    end_pos = pos[0] + size[0] / 2, pos[1] + size[1]
                speed = obj.properties["speed"]
                can_flip = obj.properties["flip"]

                MovingSprite(
                    frames=frames,
                    groups=groups,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    axis=axis,
                    speed=speed,
                    can_flip=can_flip,
                )
                # PATH OF SAW.
                if name == "saw":
                    surf = assets["saw_chain"]
                    if axis == "X":
                        y = start_pos[1] - surf.get_height() / 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite(
                                pos=(x, y),
                                surf=surf,
                                groups=self.all_sprites,
                                z=Z_LAYERS["bg details"],
                            )
                    else:
                        x = start_pos[0] - surf.get_width() / 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite(
                                pos=(x, y),
                                surf=surf,
                                groups=self.all_sprites,
                                z=Z_LAYERS["bg details"],
                            )

    def run(self, dt):
        self.all_sprites.update(dt)
        self.screen.fill("black")
        self.all_sprites.draw(self.player.hitbox.center)
