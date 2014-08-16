class Selection(Screen):
    """A selection screen."""

    LCD_LINES = 2


    def __init__(self, lcd, interactions, items):
        super(Selection, self).__init__(lcd, interactions)
        self.current_screen_item = 0
        self.items = items


    def current_screen_name(self):
        return self.items[self.current_screen_item]


    def screen_init(self):
        self.lcd.clear()
        for item in self.items[self.current_screen_item:self.current_screen_item + self.LCD_LINES]:
            self.lcd.message("%s%s\n" % (chr(Ammonia.RIGHT_ARROW_CHAR), item))


    def screen_update(self):
        pass
