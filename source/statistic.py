class Data:
    def __init__(self, ui):
        self._coins = 0
        self._health = 5
        self.ui = ui
        # AT FIRST.
        self.ui.update_health(self._health)
        # LEVEL STAGE.
        self.unlocked_level = 6
        self.current_level = 0

    @property
    def health(self):
        return self._health

    @property
    def coins(self):
        return self._coins

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
