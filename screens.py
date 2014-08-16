import string
import Adafruit_CharLCD as LCD
from ammonia import Ammonia

class Screen(object):
    """A screen."""

    def __init__(self, lcd, interactions):
        self.lcd = lcd
        self.interactions = interactions


    def buttons(self):
        return self.interactions.keys()


    def action(self, button):
        return self.interactions[button]


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
            cursor = chr(Ammonia.RIGHT_ARROW_CHAR) if item == self.current_screen_name() else ' '
            self.lcd.message("%s%s\n" % (cursor, string.capwords(item, '_').replace('_', '')))


    def screen_update(self):
        pass


class Welcome(Selection):
    """Ammonia welcome screen."""

    INTERACTIONS = {
        LCD.UP: {'method': 'select_next_item', 'args': ()},
        LCD.DOWN: {'method': 'select_prev_item', 'args': ()},
        LCD.SELECT: {'method': 'transition_to_item', 'args': ()}
    }

    ITEMS = ('measure', 'calibrate')


    def __init__(self, lcd):
        super(Welcome, self).__init__(lcd, self.INTERACTIONS, self.ITEMS)

