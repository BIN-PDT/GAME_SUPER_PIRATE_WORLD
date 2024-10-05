from settings import *
from random import randint
from timers import Timer

from sprites import AnimatedSprite


class UI:
    def __init__(self, font, assets):
        self.screen = pygame.display.get_surface()
        # ASSETS.
        self.heart_surfs = assets["heart"]
        self.coin_surf = assets["coin"]
        self.font = font

        self.HEART_WIDTH = self.heart_surfs[0].get_width()
        self.HEART_PADDING = 10
        # GROUP.
        self.heart_sprites = pygame.sprite.Group()
        # COINS.
        self.coin_quantity = 0
        # TIMER.
        self.coin_timer = Timer(1000)

    def update_health(self, quantity):
        self.heart_sprites.empty()
        for i in range(quantity):
            pos = 10 + i * (self.HEART_WIDTH + self.HEART_PADDING), 10
            Heart(pos, self.heart_surfs, self.heart_sprites)

    def update_coins(self, quanity):
        self.coin_quantity = quanity
        self.coin_timer.activate()

    def show_coins(self):
        if self.coin_timer.is_active:
            # DRAW QUANTITY.
            text_surf = self.font.render(str(self.coin_quantity), False, "#33323D")
            text_rect = text_surf.get_frect(topleft=(10, 30))
            self.screen.blit(text_surf, text_rect)
            # DRAW ICON.
            coin_rect = self.coin_surf.get_rect(center=text_rect.bottomright)
            self.screen.blit(self.coin_surf, coin_rect.move(12, -6))

    def update(self, dt):
        self.coin_timer.update()
        self.heart_sprites.update(dt)
        self.heart_sprites.draw(self.screen)
        self.show_coins()


class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        # SETUP.
        self.is_active = False

    def animate(self, dt):
        self.frame_index += self.ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.is_active = False
            self.frame_index = 0

    def update(self, dt):
        if self.is_active:
            self.animate(dt)
        else:
            if randint(0, 2000) == 1:
                self.is_active = True
