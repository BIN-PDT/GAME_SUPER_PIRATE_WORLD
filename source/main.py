from settings import *
from os.path import join
from pytmx.util_pygame import load_pygame

from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Super Pirate World")
        self.clock = pygame.time.Clock()
        # SETUP.
        self.load_assets()
        self.current_stage = Level(self.TMX_MAPS[0])

    def load_assets(self):
        # MAP.
        self.TMX_MAPS = {
            0: load_pygame(join("data", "levels", "omni.tmx")),
        }

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            # EVENT LOOP.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # GAME LOGIC.
            self.current_stage.run(dt)
            pygame.display.update()


if __name__ == "__main__":
    Game().run()
