class Data:
    def __init__(self, ui):
        self._coins = 0
        self._health = 5
        self.ui = ui
        # AT FIRST.
        self.ui.update_health(self._health)
        # LEVEL STAGE.
        self._unlocked_level = 0
        self.current_level = 0

    @property
    def health(self):
        return self._health

    @property
    def coins(self):
        return self._coins

    @property
    def unlocked_level(self):
        return self._unlocked_level

    @health.setter
    def health(self, value):
        self._health = value
        self.ui.update_health(value)

    @coins.setter
    def coins(self, value):
        self._coins = value
        if self._coins >= 100:
            self._coins -= 100
            self.health += 1
        self.ui.update_coins(self._coins)

    @unlocked_level.setter
    def unlocked_level(self, value):
        self._unlocked_level = max(0, value)
        self.current_level = min(self.current_level, self._unlocked_level)
