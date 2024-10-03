from settings import *
from supports import *
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
        self.current_stage = Level(self.TMX_MAPS[0], self.level_frames)

    def load_assets(self):
        # MAP.
        self.TMX_MAPS = {
            0: load_pygame(join("data", "levels", "omni.tmx")),
        }
        # LEVEL.
        self.level_frames = {
            "flag": import_folder_list("images", "level", "flag"),
            "saw": import_folder_list("images", "enemies", "saw", "animation"),
            "saw_chain": import_image("images", "enemies", "saw", "saw_chain"),
            "floor_spike": import_folder_list("images", "enemies", "floor_spikes"),
            "palms": import_folder_dict("images", "level", "palms", subordinate=True),
            "candle": import_folder_list("images", "level", "candle"),
            "window": import_folder_list("images", "level", "window"),
            "big_chain": import_folder_list("images", "level", "big_chains"),
            "small_chain": import_folder_list("images", "level", "small_chains"),
            "candle_light": import_folder_list("images", "level", "candle light"),
            "player": import_folder_dict("images", "player", subordinate=True),
            "helicopter": import_folder_list("images", "level", "helicopter"),
            "boat": import_folder_list("images", "objects", "boat"),
            "spike": import_image("images", "enemies", "spike_ball", "spiked_ball"),
            "spike_chain": import_image(
                "images", "enemies", "spike_ball", "spiked_chain"
            ),
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
