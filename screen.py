class Screen(object):
    """A screen."""

    def __init__(self, lcd, interactions):
        self.lcd = lcd
        self.interactions = interactions


    def buttons(self):
        return self.interactions.keys()


    def action(self, button):
        return self.interactions[button]
