from settings import *
from timers import Timer


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
        self.JUMP_HEIGHT = 900
        self.can_jump = False
        self.on_surface = {"floor": False, "left": False, "right": False}
        # COLLISION.
        self.collision_sprites = collision_sprites
        # TIMER.
        self.timers = {
            "wall jump": Timer(400),
            "wall slide block": Timer(250),
        }

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers["wall jump"].is_active:
            # WALK.
            direction = 0
            if keys[pygame.K_RIGHT]:
                direction += 1
            if keys[pygame.K_LEFT]:
                direction -= 1
            self.direction.x = direction
        # JUMP.
        if keys[pygame.K_SPACE]:
            self.can_jump = True

    def move(self, dt):
        # WALKING.
        self.rect.x += self.direction.x * self.SPEED * dt
        self.collide("X")
        # SLIDING.
        if (
            not self.on_surface["floor"]
            and (self.on_surface["left"] or self.on_surface["right"])
            and not self.timers["wall slide block"].is_active
        ):
            self.direction.y = 0
            self.rect.y += self.GRAVITY / 10 * dt
        # FALLING.
        else:
            self.direction.y += self.GRAVITY / 2 * dt
            self.rect.y += self.direction.y * dt
            self.direction.y += self.GRAVITY / 2 * dt
        self.collide("Y")
        # JUMPING.
        if self.can_jump:
            self.can_jump = False
            # JUMP FROM FLOOR.
            if self.on_surface["floor"]:
                self.timers["wall slide block"].activate()
                self.direction.y = -self.JUMP_HEIGHT
            # JUMP FROM WALL.
            elif (
                self.on_surface["left"] or self.on_surface["right"]
            ) and not self.timers["wall slide block"].is_active:
                self.timers["wall jump"].activate()
                self.direction.y = -self.JUMP_HEIGHT
                self.direction.x = 1 if self.on_surface["left"] else -1

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

    def check_contact(self):
        collision_rects = [sprite.rect for sprite in self.collision_sprites]
        # CHECK PLAYER IS ON THE FLOOR.
        pos = self.rect.bottomleft
        FLOOR_RECT = pygame.Rect(pos, (self.rect.width, 2))
        self.on_surface["floor"] = FLOOR_RECT.collidelist(collision_rects) >= 0
        # CHECK RIGHT WALL SLIDING.
        pos = self.rect.topleft + Vector((-2, self.rect.height / 4))
        LEFT_RECT = pygame.Rect(pos, (2, self.rect.height / 2))
        self.on_surface["left"] = LEFT_RECT.collidelist(collision_rects) >= 0
        # CHECK LEFT WALL SLIDING.
        pos = self.rect.topright + Vector((0, self.rect.height / 4))
        RIGHT_RECT = pygame.Rect(pos, (2, self.rect.height / 2))
        self.on_surface["right"] = RIGHT_RECT.collidelist(collision_rects) >= 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.update_timers()
        self.input()
        self.move(dt)
        self.check_contact()
