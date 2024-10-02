from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        # SETUP.
        self.image = pygame.Surface((48, 56))
        self.image.fill("red")
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        # MOVEMENT.
        self.direction = Vector()
        self.SPEED = 200
        self.GRAVITY = 1300
        # COLLISION.
        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        direction = 0
        if keys[pygame.K_RIGHT]:
            direction += 1
        if keys[pygame.K_LEFT]:
            direction -= 1
        self.direction.x = direction

    def move(self, dt):
        # HORIZONTAL.
        self.rect.x += self.direction.x * self.SPEED * dt
        self.collide("X")
        # VERTICAL.
        self.direction.y += self.GRAVITY / 2 * dt
        self.rect.y += self.direction.y * dt
        self.direction.y += self.GRAVITY / 2 * dt
        self.collide("Y")

    def collide(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == "X":
                    if (
                        self.rect.left <= sprite.rect.right
                        and self.old_rect.left >= sprite.old_rect.right
                    ):
                        self.rect.left = sprite.rect.right
                    elif (
                        self.rect.right >= sprite.rect.left
                        and self.old_rect.right <= sprite.old_rect.left
                    ):
                        self.rect.right = sprite.rect.left
                else:
                    if (
                        self.rect.top <= sprite.rect.bottom
                        and self.old_rect.top >= sprite.old_rect.bottom
                    ):
                        self.rect.top = sprite.rect.bottom
                    elif (
                        self.rect.bottom >= sprite.rect.top
                        and self.old_rect.bottom <= sprite.old_rect.top
                    ):
                        self.rect.bottom = sprite.rect.top
                    # FALL DOWN.
                    self.direction.y = 0

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
        self.move(dt)
