from settings import *
from timers import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, semicollision_sprites):
        super().__init__(groups)
        # ANIMATION.
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        # SETUP.
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox.copy()
        self.z = Z_LAYERS["main"]
        # MOVEMENT.
        self.direction = Vector()
        self.SPEED = 200
        self.GRAVITY = 1300
        self.JUMP_HEIGHT = 900
        self.can_jump = False
        self.on_surface = {"floor": False, "left": False, "right": False}
        # ATTACK.
        self.is_attacking = False
        # COLLISION.
        self.collision_sprites = collision_sprites
        self.semicollision_sprites = semicollision_sprites
        self.platform = None
        # TIMER.
        self.timers = {
            "wall jump": Timer(400),
            "wall slide block": Timer(250),
            "platform skip": Timer(300),
            "attack block": Timer(500),
        }

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers["wall jump"].is_active:
            # WALK.
            direction = 0
            if keys[pygame.K_RIGHT]:
                direction += 1
                self.facing_right = True
            if keys[pygame.K_LEFT]:
                direction -= 1
                self.facing_right = False
            self.direction.x = direction
            # FALL FROM PLATFORM.
            if keys[pygame.K_DOWN]:
                self.timers["platform skip"].activate()
            # ATTACK.
            if keys[pygame.K_x]:
                self.attack()
        # JUMP.
        if keys[pygame.K_SPACE]:
            self.can_jump = True

    def move(self, dt):
        # WALKING.
        self.hitbox.x += self.direction.x * self.SPEED * dt
        self.collide("X")
        # SLIDING.
        if (
            not self.on_surface["floor"]
            and (self.on_surface["left"] or self.on_surface["right"])
            and not self.timers["wall slide block"].is_active
        ):
            self.direction.y = 0
            self.hitbox.y += self.GRAVITY / 10 * dt
        # FALLING.
        else:
            self.direction.y += self.GRAVITY / 2 * dt
            self.hitbox.y += self.direction.y * dt
            self.direction.y += self.GRAVITY / 2 * dt
        self.collide("Y")
        self.semicollide()
        self.rect.center = self.hitbox.center
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
                self.facing_right = self.on_surface["left"]

    def collide(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if axis == "X":
                    if (
                        self.hitbox.left <= sprite.rect.right
                        and self.old_rect.left >= sprite.old_rect.right
                    ):
                        self.hitbox.left = sprite.rect.right
                    elif (
                        self.hitbox.right >= sprite.rect.left
                        and self.old_rect.right <= sprite.old_rect.left
                    ):
                        self.hitbox.right = sprite.rect.left
                else:
                    if (
                        self.hitbox.top <= sprite.rect.bottom
                        and self.old_rect.top >= sprite.old_rect.bottom
                    ):
                        self.hitbox.top = sprite.rect.bottom
                    elif (
                        self.hitbox.bottom >= sprite.rect.top
                        and self.old_rect.bottom <= sprite.old_rect.top
                    ):
                        self.hitbox.bottom = sprite.rect.top
                    # FALL DOWN.
                    self.direction.y = 0

    def semicollide(self):
        if not self.timers["platform skip"].is_active:
            for sprite in self.semicollision_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    if (
                        self.hitbox.bottom >= sprite.rect.top
                        and self.old_rect.bottom <= sprite.old_rect.top
                    ):
                        self.hitbox.bottom = sprite.rect.top
                        # FALL DOWN.
                        self.direction.y = 0

    def check_contact(self):
        collision_rects = [sprite.rect for sprite in self.collision_sprites]
        # CHECK PLAYER IS ON THE FLOOR.
        pos = self.hitbox.bottomleft
        FLOOR_RECT = pygame.Rect(pos, (self.hitbox.width, 2))
        self.on_surface["floor"] = FLOOR_RECT.collidelist(collision_rects) >= 0
        # CHECK RIGHT WALL SLIDING.
        pos = self.hitbox.topleft + Vector((-2, self.hitbox.height / 4))
        LEFT_RECT = pygame.Rect(pos, (2, self.hitbox.height / 2))
        self.on_surface["left"] = LEFT_RECT.collidelist(collision_rects) >= 0
        # CHECK LEFT WALL SLIDING.
        pos = self.hitbox.topright + Vector((0, self.hitbox.height / 4))
        RIGHT_RECT = pygame.Rect(pos, (2, self.hitbox.height / 2))
        self.on_surface["right"] = RIGHT_RECT.collidelist(collision_rects) >= 0
        # CHECK PLAYER IS ON A PLATFORM.
        if self.direction.y >= 0:
            semicollision_rects = [sprite.rect for sprite in self.semicollision_sprites]
            self.on_surface["floor"] |= FLOOR_RECT.collidelist(semicollision_rects) >= 0
        # CHECK PLATFORM THAT PLAYER IS STANDING.
        self.platform = None
        for sprite in (
            self.collision_sprites.sprites() + self.semicollision_sprites.sprites()
        ):
            if hasattr(sprite, "can_move") and sprite.rect.colliderect(FLOOR_RECT):
                self.platform = sprite

    def follow_platfrom(self, dt):
        if self.platform:
            self.hitbox.topleft += self.platform.direction * self.platform.SPEED * dt

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def attack(self):
        if not self.timers["attack block"].is_active:
            self.timers["attack block"].activate()
            self.is_attacking = True
            self.frame_index = 0

    def check_state(self):
        # ON THE GROUND.
        if self.on_surface["floor"]:
            if self.is_attacking:
                self.state = "attack"
            else:
                self.state = "idle" if self.direction.x == 0 else "run"
        # ON THE AIR.
        else:
            if self.is_attacking:
                self.state = "air_attack"
            else:
                if self.on_surface["left"] or self.on_surface["right"]:
                    self.state = "wall"
                else:
                    self.state = "jump" if self.direction.y < 0 else "fall"

    def animate(self, dt):
        animation = self.frames[self.state]
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
            # IDLING AFTER ATTACKING.
            self.is_attacking = False
            if self.state == "attack":
                self.state = "idle"

        self.image = animation[int(self.frame_index)]
        # FLIP IMAGE.
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, dt):
        self.old_rect = self.hitbox.copy()
        self.update_timers()
        self.input()
        self.follow_platfrom(dt)
        self.move(dt)
        self.check_contact()

        self.check_state()
        self.animate(dt)
