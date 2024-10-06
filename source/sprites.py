from settings import *
from math import sin, cos, radians
from random import randint


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

    def get_reward(self):
        match self.item_type:
            case "silver":
                return "coin", 1
            case "gold":
                return "coin", 5
            case "diamond":
                return "coin", 10
            case "skull":
                return "coin", 50
            case "potion":
                return "health", 1


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


class Cloud(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, Z_LAYERS["clouds"])
        # SETUP.
        self.rect.midbottom = pos
        # MOVEMENT.
        self.SPEED = randint(50, 120)

    def update(self, dt):
        self.rect.x -= self.SPEED * dt
        # CHECK DESTROY.
        if self.rect.right <= 0:
            self.kill()


class Node(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, level, data, paths):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.z = Z_LAYERS["path"]
        self.level = level
        # PLAYER DATA.
        self.data = data
        # AVAILABLE PATHS.
        self.paths = paths

    def can_move(self, direction):
        return (
            direction in self.paths.keys()
            and int(self.paths[direction][0]) <= self.data.unlocked_level
        )


class Icon(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups):
        super().__init__(groups)
        # ANIMATION.
        self.frames, self.frame_index = frames, 0
        self.state = "idle"
        # SETUP.
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.z = Z_LAYERS["main"]
        # MOVEMENT.
        self.direction = Vector()
        self.SPEED = 400
        self.path = None

    def start_move(self, path):
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def move(self, dt):
        self.rect.center += self.direction * self.SPEED * dt
        self.follow_path()

    def find_path(self):
        if self.path:
            if self.rect.centerx == self.path[0][0]:
                y = 1 if self.rect.centery < self.path[0][1] else -1
                self.direction = Vector(0, y)
            else:
                x = 1 if self.rect.centerx < self.path[0][0] else -1
                self.direction = Vector(x, 0)
        else:
            self.direction = Vector()

    def follow_path(self):
        # VERTICAL.
        if (self.direction.y == 1 and self.rect.centery >= self.path[0][1]) or (
            self.direction.y == -1 and self.rect.centery <= self.path[0][1]
        ):
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()
        # HORIZONTAL.
        elif (self.direction.x == 1 and self.rect.centerx >= self.path[0][0]) or (
            self.direction.x == -1 and self.rect.centerx <= self.path[0][0]
        ):
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def check_state(self):
        if self.direction:
            if self.direction.x == 0:
                self.state = "up" if self.direction.y == -1 else "down"
            else:
                self.state = "left" if self.direction.x == -1 else "right"
        else:
            self.state = "idle"

    def animate(self, dt):
        animation = self.frames[self.state]
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index %= len(animation)

        self.image = animation[int(self.frame_index)]

    def update(self, dt):
        if self.path:
            self.move(dt)
        self.check_state()
        self.animate(dt)


class Path(Sprite):
    def __init__(self, pos, surf, groups, level):
        super().__init__(pos, surf, groups, Z_LAYERS["path"])
        self.level = level
