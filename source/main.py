from settings import *
from supports import *
from os.path import join
from pytmx.util_pygame import load_pygame

from ui import UI
from statistic import Data
from level import Level
from overworld import Overworld


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Super Pirate World")
        self.clock = pygame.time.Clock()
        # SETUP.
        self.load_assets()
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.current_stage = Overworld(
            tmx_map=self.TMX_OVERWORLD,
            assets=self.overworld_frames,
            data=self.data,
            switch_command=self.switch_stage,
        )
        # BACKGROUND MUSIC.
        pygame.mixer.music.load(join("audio", "starlight_city.mp3"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def load_assets(self):
        # MAP.
        self.TMX_OVERWORLD = load_pygame(join("data", "overworld", "overworld.tmx"))
        self.TMX_MAPS = {
            0: load_pygame(join("data", "levels", "0.tmx")),
            1: load_pygame(join("data", "levels", "1.tmx")),
            2: load_pygame(join("data", "levels", "2.tmx")),
            3: load_pygame(join("data", "levels", "3.tmx")),
            4: load_pygame(join("data", "levels", "4.tmx")),
            5: load_pygame(join("data", "levels", "5.tmx")),
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
            "tooth": import_folder_list("images", "enemies", "tooth", "run"),
            "shell": import_folder_dict("images", "enemies", "shell", subordinate=True),
            "pearl": import_image("images", "enemies", "bullets", "pearl"),
            "items": import_folder_dict("images", "items", subordinate=True),
            "particle": import_folder_list("images", "effects", "particle"),
            "water_top": import_folder_list("images", "level", "water", "top"),
            "water_body": import_image("images", "level", "water", "body"),
            "bg_tiles": import_folder_dict("images", "level", "bg", "tiles"),
            "small_cloud": import_folder_list("images", "level", "clouds", "small"),
            "large_cloud": import_image("images", "level", "clouds", "large_cloud"),
        }
        # UI.
        self.font = pygame.font.Font(join("images", "ui", "runescape_uf.ttf"), 32)
        self.ui_frames = {
            "heart": import_folder_list("images", "ui", "heart"),
            "coin": import_image("images", "ui", "coin"),
        }
        # OVERWORLD.
        self.overworld_frames = {
            "palms": import_folder_list("images", "overworld", "palm"),
            "water": import_folder_list("images", "overworld", "water"),
            "path": import_folder_dict("images", "overworld", "path"),
            "icon": import_folder_dict("images", "overworld", "icon", subordinate=True),
        }
        # AUDIO.
        self.audios = {
            "item": pygame.mixer.Sound(join("audio", "coin.wav")),
            "attack": pygame.mixer.Sound(join("audio", "attack.wav")),
            "damage": pygame.mixer.Sound(join("audio", "damage.wav")),
            "hit": pygame.mixer.Sound(join("audio", "hit.wav")),
            "jump": pygame.mixer.Sound(join("audio", "jump.wav")),
            "pearl": pygame.mixer.Sound(join("audio", "pearl.wav")),
        }

    def switch_stage(self, target, unlock=-1):
        if target == "level":
            self.current_stage = Level(
                tmx_map=self.TMX_MAPS[self.data.current_level],
                assets=self.level_frames,
                data=self.data,
                switch_command=self.switch_stage,
                audios=self.audios,
            )
        else:
            self.current_stage = Overworld(
                tmx_map=self.TMX_OVERWORLD,
                assets=self.overworld_frames,
                data=self.data,
                switch_command=self.switch_stage,
            )
            # UPDATE PLAYER DATA.
            if unlock > 0:
                if unlock > self.data.unlocked_level:
                    self.data.unlocked_level = unlock
            else:
                self.data.health -= 1

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
            self.ui.update(dt)
            pygame.display.update()


if __name__ == "__main__":
    Game().run()
