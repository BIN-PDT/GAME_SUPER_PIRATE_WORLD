from settings import *
from math import sin, cos, radians


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=Z_LAYERS["main"]):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z


class AnimatedSprite(Sprite):
    def __init__(
        self, pos, frames, groups, z=Z_LAYERS["main"], animation_speed=ANIMATION_SPEED
    ):
        # ANIMATION.
        self.frames, self.frame_index = frames, 0
        self.ANIMATION_SPEED = animation_speed
        # SETUP.
        surf = self.frames[self.frame_index]
        super().__init__(pos, surf, groups, z)

    def update(self, dt):
        self.frame_index += self.ANIMATION_SPEED * dt
        self.frame_index %= len(self.frames)

        self.image = self.frames[int(self.frame_index)]


class MovingSprite(AnimatedSprite):
    def __init__(self, frames, groups, start_pos, end_pos, axis, speed, can_flip):
        super().__init__(start_pos, frames, groups)
        # SETUP.
        if axis == "X":
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos
        # MOVEMENT.
        self.can_move = True
        self.move_direction = axis
        self.start_pos, self.end_pos = start_pos, end_pos
        self.direction = Vector(1, 0) if axis == "X" else Vector(0, 1)
        self.SPEED = speed

        self.can_flip = can_flip
        self.reverse = {"flip_x": False, "flip_y": False}

    def check_boundary(self):
        if self.move_direction == "X":
            if self.rect.left <= self.start_pos[0]:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            elif self.rect.right >= self.end_pos[0]:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            # REVERSE.
            self.reverse["flip_x"] = self.direction.x < 0
        else:
            if self.rect.top <= self.start_pos[1]:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            elif self.rect.bottom >= self.end_pos[1]:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            # REVERSE.
            self.reverse["flip_y"] = self.direction.y < 0

    def update(self, dt):
        self.old_rect = self.rect.copy()
        # MOVE.
        self.rect.topleft += self.direction * self.SPEED * dt
        self.check_boundary()
        # ANIMATE.
        super().update(dt)
        # FLIP IMAGE.
        if self.can_flip:
            self.image = pygame.transform.flip(self.image, **self.reverse)


class Spike(Sprite):
    def __init__(
        self,
        pos,
        surf,
        groups,
        radius,
        speed,
        start_angle,
        end_angle,
        z=Z_LAYERS["main"],
    ):
        self.CENTER, self.RADIUS = pos, radius
        self.START_ANGLE = start_angle
        self.END_ANGLE = end_angle
        # MOVEMENT.
        self.IS_FULL_CIRCLE = end_angle == -1
        self.SPEED = speed
        self.angle = start_angle
        self.direction = 1
        # SETUP.
        super().__init__(self.get_pos(), surf, groups, z)

    def get_pos(self):
        x = self.CENTER[0] + cos(radians(self.angle)) * self.RADIUS
        y = self.CENTER[1] + sin(radians(self.angle)) * self.RADIUS
        return x, y

    def update(self, dt):
        self.angle += self.direction * self.SPEED * dt
        self.rect.center = self.get_pos()
        # REVERSE.
        if not self.IS_FULL_CIRCLE:
            if self.angle >= self.END_ANGLE or self.angle <= self.START_ANGLE:
                self.direction *= -1


class Item(AnimatedSprite):
    def __init__(self, pos, frames, groups, item_type):
        super().__init__(pos, frames, groups)
        # SETUP.
        self.rect.center = pos
        self.item_type = item_type


class Particle(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups, Z_LAYERS["fg"])
        # SETUP.
        self.rect.center = pos

    def update(self, dt):
        self.frame_index += self.ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()
