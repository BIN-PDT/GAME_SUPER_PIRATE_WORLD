from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=None):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.image.fill("white")
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()


class MovingSprite(Sprite):
    def __init__(self, groups, start_pos, end_pos, axis, speed):
        surf = pygame.Surface((200, 50))
        super().__init__(start_pos, surf, groups)
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

    def check_boundary(self):
        if self.move_direction == "X":
            if self.rect.left <= self.start_pos[0]:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            elif self.rect.right >= self.end_pos[0]:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
        else:
            if self.rect.top <= self.start_pos[1]:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            elif self.rect.bottom >= self.end_pos[1]:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]

    def update(self, dt):
        self.old_rect = self.rect.copy()

        self.rect.topleft += self.direction * self.SPEED * dt
        self.check_boundary()
