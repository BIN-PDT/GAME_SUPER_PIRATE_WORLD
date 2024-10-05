from settings import *
from random import choice, randint
from timers import Timer

from sprites import Sprite, Cloud, Icon


class AllSprites(pygame.sprite.Group):
    def __init__(self, level_data):
        super().__init__()
        self.screen = pygame.display.get_surface()
        # MAP SIZE.
        self.MAP_WIDTH = level_data["cols"] * TILE_SIZE
        self.MAP_HEIGHT = level_data["rows"] * TILE_SIZE
        # CAMERA CONSTRAINT.
        self.offset = Vector()
        self.BORDERS = {
            "left": 0,
            "right": -self.MAP_WIDTH + WINDOW_WIDTH,
            "bottom": -self.MAP_HEIGHT + WINDOW_HEIGHT,
            "top": level_data["top_limit"],
        }
        # BACKGROUND.
        self.HAS_SKY = not level_data["bg_tile"]
        if level_data["bg_tile"]:
            start_row = -int(level_data["top_limit"] / TILE_SIZE) - 1
            for row in range(start_row, level_data["rows"]):
                for col in range(level_data["cols"]):
                    pos = col * TILE_SIZE, row * TILE_SIZE
                    Sprite(pos, level_data["bg_tile"], self, -1)
        else:
            self.SKYLINE = level_data["skyline"]
            # LARGE CLOUD.
            self.LC_surf = level_data["clouds"]["large_cloud"]
            self.LC_x, self.LC_SPEED = 0, 50
            self.LC_WIDTH, self.LC_HEIGHT = self.LC_surf.get_size()
            self.LC_TILES = int(self.MAP_WIDTH / self.LC_WIDTH) + 2
            # SMALL CLOUD.
            self.SC_surfs = level_data["clouds"]["small_cloud"]
            self.SC_WIDTH, self.SC_HEIGHT = self.SC_surfs[0].get_size()
            self.SC_timer = Timer(2500, True, self.spawn_small_cloud)
            self.SC_timer.activate()
            for _ in range(15):
                x = randint(0, self.MAP_WIDTH)
                y = randint(-self.BORDERS["top"], self.SKYLINE)
                Cloud((x, y), choice(self.SC_surfs), self)

    def constraint_camera(self):
        if self.offset.x > self.BORDERS["left"]:
            self.offset.x = self.BORDERS["left"]
        elif self.offset.x < self.BORDERS["right"]:
            self.offset.x = self.BORDERS["right"]

        if self.offset.y < self.BORDERS["bottom"]:
            self.offset.y = self.BORDERS["bottom"]
        elif self.offset.y > self.BORDERS["top"]:
            self.offset.y = self.BORDERS["top"]

    def draw_sky(self):
        skyline = self.SKYLINE + self.offset.y
        # SKY BACKGROUND.
        self.screen.fill("#DDC6A1")
        # SEA BACKGROUND.
        rect = pygame.FRect(0, skyline, self.MAP_WIDTH, self.MAP_HEIGHT - skyline)
        pygame.draw.rect(self.screen, "#92A9CE", rect)
        # HORIZONTAL LINE.
        pygame.draw.line(
            self.screen, "#F5F1DE", (0, skyline), (WINDOW_WIDTH, skyline), 4
        )

    def draw_large_clouds(self, dt):
        # MOVE.
        self.LC_x -= self.LC_SPEED * dt
        if self.LC_x <= -self.LC_WIDTH:
            self.LC_x = 0
        # DRAW.
        y = self.SKYLINE - self.LC_HEIGHT + self.offset.y
        for index in range(self.LC_TILES):
            x = self.LC_x + index * self.LC_WIDTH + self.offset.x
            self.screen.blit(self.LC_surf, (x, y))

    def spawn_small_cloud(self):
        x = randint(self.MAP_WIDTH + 500, self.MAP_WIDTH + 600)
        y = randint(-self.BORDERS["top"], self.SKYLINE)
        Cloud((x, y), choice(self.SC_surfs), self)

    def draw(self, player_pos, dt):
        self.offset.x = -(player_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(player_pos[1] - WINDOW_HEIGHT / 2)
        self.constraint_camera()
        # DRAW BACKGROUND.
        if self.HAS_SKY:
            self.SC_timer.update()
            self.draw_sky()
            self.draw_large_clouds(dt)
        # DRAW FOREGROUND.
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.screen.blit(sprite.image, offset_pos)


class WorldSprite(pygame.sprite.Group):
    def __init__(self, data):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = Vector()
        self.data = data

    def draw(self, player_pos):
        self.offset.x = -(player_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(player_pos[1] - WINDOW_HEIGHT / 2)
        # DRAW BACKGROUND.
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.z < Z_LAYERS["main"]:
                offset_pos = sprite.rect.topleft + self.offset
                if sprite.z == Z_LAYERS["path"]:
                    if sprite.level <= self.data.unlocked_level:
                        self.screen.blit(sprite.image, offset_pos)
                else:
                    self.screen.blit(sprite.image, offset_pos)
        # DRAW FOREGROUND.
        for sprite in sorted(self, key=lambda sprite: sprite.rect.centery):
            if sprite.z == Z_LAYERS["main"]:
                offset_pos = sprite.rect.topleft + self.offset
                if isinstance(sprite, Icon):
                    self.screen.blit(sprite.image, offset_pos + Vector(0, -28))
                else:
                    self.screen.blit(sprite.image, offset_pos)
