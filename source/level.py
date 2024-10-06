from settings import *
from random import uniform

from groups import AllSprites
from player import Player
from sprites import *
from enemies import *


class Level:
    def __init__(self, tmx_map, assets, data, switch_command, audios):
        self.screen = pygame.display.get_surface()
        # ASSETS.
        self.switch_command = switch_command
        self.data = data
        self.pearl_surf = assets["pearl"]
        self.particle_surfs = assets["particle"]

        self.item_sound = audios["item"]
        self.item_sound.set_volume(0.2)
        self.damage_sound = audios["damage"]
        self.damage_sound.set_volume(0.2)
        self.pearl_sound = audios["pearl"]
        self.pearl_sound.set_volume(0.5)

        level_data = self.get_level_data(tmx_map, assets)
        self.LEVEL_WIDTH = level_data["cols"] * TILE_SIZE
        self.LEVEL_HEIGHT = level_data["rows"] * TILE_SIZE
        self.LEVEL_UNLOCK = level_data["level_unlock"]
        # GROUP.
        self.all_sprites = AllSprites(level_data)
        self.collision_sprites = pygame.sprite.Group()
        self.semicollision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sriptes = pygame.sprite.Group()
        # SETUP.
        self.load_data(tmx_map, assets, audios, data)

    @staticmethod
    def get_level_data(tmx_map, assets):
        instance = tmx_map.get_layer_by_name("Data")[0]
        properties = instance.properties

        return {
            "rows": tmx_map.height,
            "cols": tmx_map.width,
            "bg_tile": assets["bg_tiles"].get(properties["bg"], None),
            "top_limit": int(properties.get("top_limit", 0)),
            "skyline": int(properties.get("horizontal_pos", WINDOW_HEIGHT / 2)),
            "clouds": {
                "small_cloud": assets["small_cloud"],
                "large_cloud": assets["large_cloud"],
            },
            "level_unlock": properties.get("level_unlock", None),
        }

    def load_data(self, tmx_map, assets, audios, data):
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
        # BACKGROUND DETAILS.
        for obj in tmx_map.get_layer_by_name("BG details"):
            name = obj.name
            pos = obj.x, obj.y
            z = Z_LAYERS["bg details"]

            if name == "static":
                Sprite(pos, obj.image, self.all_sprites, z)
            else:
                frames = assets[name]
                AnimatedSprite(pos, frames, self.all_sprites, z)
                # CANDLE LIGHT EFFECT.
                if name == "candle":
                    pos += Vector(-20, -20)
                    AnimatedSprite(pos, assets["candle_light"], self.all_sprites, z)
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
                    data=data,
                    attack_sound=audios["attack"],
                    jump_sound=audios["jump"],
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
                    if name == "floor_spike" and obj.properties["inverted"]:
                        frames = [
                            pygame.transform.flip(frame, False, True)
                            for frame in frames
                        ]

                    groups = [self.all_sprites]
                    if name in ("palm_small", "palm_large"):
                        groups.append(self.semicollision_sprites)
                    elif name in ("saw", "floor_spike"):
                        groups.append(self.damage_sprites)

                    z = Z_LAYERS["main"] if "bg" not in name else Z_LAYERS["bg details"]

                    animation_speed = (
                        ANIMATION_SPEED
                        if "palm" not in name
                        else ANIMATION_SPEED + uniform(-1, 1)
                    )

                    AnimatedSprite(pos, frames, groups, z, animation_speed)
            # LEVEL FINISH MILESTONE.
            if name == "flag":
                self.finish_milestone = pygame.FRect(pos, (obj.width, obj.height))
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
        # ENEMIES.
        for obj in tmx_map.get_layer_by_name("Enemies"):
            pos = obj.x, obj.y

            if obj.name == "tooth":
                Tooth(
                    pos=pos,
                    frames=assets["tooth"],
                    groups=(self.all_sprites, self.damage_sprites, self.tooth_sprites),
                    collision_sprites=self.collision_sprites,
                )
            else:
                Shell(
                    pos=pos,
                    frames=assets["shell"],
                    groups=(self.all_sprites, self.collision_sprites),
                    reverse=obj.properties["reverse"],
                    player=self.player,
                    create_pearl=self.create_pearl,
                )
        # ITEMS.
        for obj in tmx_map.get_layer_by_name("Items"):
            name = obj.name
            pos = obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2

            Item(
                pos=pos,
                frames=assets["items"][name],
                groups=(self.all_sprites, self.item_sriptes),
                item_type=name,
            )
        # WATER.
        for obj in tmx_map.get_layer_by_name("Water"):
            for row in range(int(obj.height / TILE_SIZE)):
                for col in range(int(obj.width / TILE_SIZE)):
                    pos = obj.x + col * TILE_SIZE, obj.y + row * TILE_SIZE
                    if row == 0:
                        AnimatedSprite(
                            pos=pos,
                            frames=assets["water_top"],
                            groups=self.all_sprites,
                            z=Z_LAYERS["water"],
                        )
                    else:
                        Sprite(
                            pos=pos,
                            surf=assets["water_body"],
                            groups=self.all_sprites,
                            z=Z_LAYERS["water"],
                        )

    def create_pearl(self, pos, direction):
        self.pearl_sound.play()
        Pearl(
            pos=pos,
            surf=self.pearl_surf,
            groups=(self.all_sprites, self.damage_sprites, self.pearl_sprites),
            direction=direction,
        )

    def check_pearl_collision(self):
        for sprite in self.collision_sprites:
            sprites = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            if sprites:
                Particle(sprites[0].rect.center, self.particle_surfs, self.all_sprites)

    def check_hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox):
                self.damage_sound.play()
                self.player.get_damage()
                if isinstance(sprite, Pearl):
                    Particle(sprite.rect.center, self.particle_surfs, self.all_sprites)
                    sprite.kill()

    def check_item_collision(self):
        if self.item_sriptes:
            sprites = pygame.sprite.spritecollide(self.player, self.item_sriptes, True)
            if sprites:
                self.item_sound.play()
                Particle(sprites[0].rect.center, self.particle_surfs, self.all_sprites)
                # REWARDED.
                reward = sprites[0].get_reward()
                if reward[0] == "coin":
                    self.data.coins += reward[1]
                else:
                    self.data.health += reward[1]

    def check_attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
            # FACING TO TARGET.
            is_facing = (
                self.player.rect.centerx < target.rect.centerx
                if self.player.facing_right
                else self.player.rect.centerx > target.rect.centerx
            )

            if (
                is_facing
                and self.player.rect.colliderect(target.rect)
                and self.player.is_attacking
            ):
                target.reverse()

    def check_constraint(self):
        # LEFT CONSTRAINT.
        if self.player.hitbox.left <= 0:
            self.player.hitbox.left = 0
        # RIGHT CONSTRAINT.
        if self.player.hitbox.right >= self.LEVEL_WIDTH:
            self.player.hitbox.right = self.LEVEL_WIDTH
        # FAILURE CONSTRAINT.
        if self.player.hitbox.bottom >= self.LEVEL_HEIGHT:
            self.switch_command("overworld")
        # SUCCESS CONSTRAINT.
        if self.player.hitbox.colliderect(self.finish_milestone):
            self.switch_command("overworld", self.LEVEL_UNLOCK)

    def run(self, dt):
        # UPDATE.
        self.all_sprites.update(dt)
        self.check_pearl_collision()
        self.check_hit_collision()
        self.check_item_collision()
        self.check_attack_collision()
        self.check_constraint()
        # DRAW.
        self.screen.fill("black")
        self.all_sprites.draw(self.player.hitbox.center, dt)
