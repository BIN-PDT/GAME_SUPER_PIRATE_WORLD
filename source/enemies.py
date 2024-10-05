from settings import *
from random import choice
from timers import Timer


class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        # ANIMATION.
        self.frames, self.frame_index = frames, 0
        # SETUP.
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.z = Z_LAYERS["main"]
        # MOVEMENT.
        self.direction = choice((-1, 1))
        self.SPEED = 200
        self.reverse_timer = Timer(1000)
        # COLLISION.
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

    def reverse(self):
        if not self.reverse_timer.is_active:
            self.direction *= -1
            self.reverse_timer.activate()

    def check_boundary(self):
        pos = self.rect.topleft + Vector(-1, 0)
        WALL_RECT = pygame.FRect(pos, (self.rect.width + 2, 1))
        FLOOR_L = pygame.FRect(self.rect.bottomleft, (-1, 1))
        FLOOR_R = pygame.FRect(self.rect.bottomright, (1, 1))

        if (
            WALL_RECT.collidelist(self.collision_rects) > 0
            or (FLOOR_L.collidelist(self.collision_rects) < 0 and self.direction < 0)
            or (FLOOR_R.collidelist(self.collision_rects) < 0 and self.direction > 0)
        ):
            self.direction *= -1

    def move(self, dt):
        self.rect.x += self.direction * self.SPEED * dt
        self.check_boundary()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index %= len(self.frames)

        self.image = self.frames[int(self.frame_index)]
        # FLIP IMAGE.
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, dt):
        self.reverse_timer.update()
        self.move(dt)
        self.animate(dt)


class Shell(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, reverse, player, create_pearl):
        super().__init__(groups)
        # ANIMATION.
        self.state = "idle"
        self.frame_index = 0
        if reverse:
            self.bullet_direction = -1
            self.frames = {
                key: [pygame.transform.flip(surf, True, False) for surf in surfs]
                for key, surfs in frames.items()
            }
        else:
            self.bullet_direction = 1
            self.frames = frames
        # SETUP.
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS["main"]
        # ATTACK.
        self.player = player
        self.create_pearl = create_pearl
        self.has_fired = False
        self.attack_timer = Timer(3000)

    def check_state(self):
        player_pos = Vector(self.player.hitbox.center)
        shell_pos = Vector(self.rect.center)
        # PLAYER IS NEAR THE SHELL.
        is_nearby = shell_pos.distance_to(player_pos) < 500
        # PLAYER IS IN THE SAME LEVEL OF SHELL.
        is_level = abs(shell_pos.y - player_pos.y) < 30
        # PLAYER IS FRONT OF THE SHELL.
        is_front = (
            shell_pos.x < player_pos.x
            if self.bullet_direction > 0
            else shell_pos.x > player_pos.x
        )
        # PLAYER IS IN ATTACK RANGE OF SHELL.
        if not self.attack_timer.is_active and is_nearby and is_front and is_level:
            self.state = "fire"
            self.frame_index = 0
            self.attack_timer.activate()

    def attack(self):
        start = self.rect.midright if self.bullet_direction > 0 else self.rect.midleft
        offset = Vector(self.bullet_direction * 10, 6)
        self.create_pearl(start + offset, self.bullet_direction)

    def animate(self, delta_time: float):
        animation = self.frames[self.state]
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index < len(animation):
            self.image = animation[int(self.frame_index)]
            # ATTACKING.
            if (
                self.state == "fire"
                and not self.has_fired
                and int(self.frame_index) == 3
            ):
                self.has_fired = True
                self.attack()
        else:
            self.frame_index = 0
            if self.state == "fire":
                self.has_fired = False
                self.state = "idle"

    def update(self, dt):
        self.attack_timer.update()
        self.check_state()
        self.animate(dt)


class Pearl(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, direction):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.z = Z_LAYERS["main"]
        # MOVEMENT.
        self.direction = direction
        self.SPEED = 150
        self.timers = {"life": Timer(5000), "reverse": Timer(1000)}
        self.timers["life"].activate()

    def reverse(self):
        if not self.timers["reverse"].is_active:
            self.direction *= -1
            self.timers["reverse"].activate()

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()
        # MOVE.
        self.rect.x += self.direction * self.SPEED * dt
        # CHECK DEATH.
        if not self.timers["life"].is_active:
            self.kill()
