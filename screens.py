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
        self.current_item = 0
        self.window_index = 0
        self.items = items


    def current_item_name(self):
        return self.items[self.current_item]


    def _print_selection(self):
        self.lcd.clear()
        for item in self.items[self.window_index:self.window_index + self.LCD_LINES]:
            cursor = chr(Ammonia.RIGHT_ARROW_CHAR) if item == self.current_item_name() else ' '
            self.lcd.message("%s%s\n" % (cursor, string.capwords(item, '_').replace('_', '')))


    def select_next_item(self):
        if self.current_item + 1 < len(self.items):
            self.current_item = self.current_item + 1
            if not (self.current_item < self.window_index + self.LCD_LINES):
                self.window_index = self.window_index + 1
        self._print_selection()


    def select_prev_item(self):
        if self.current_item - 1 >= 0:
            self.current_item = self.current_item - 1
            if self.current_item < self.window_index:
                self.window_index = self.window_index - 1
        self._print_selection()


    def screen_init(self):
        self._print_selection()


class Welcome(Selection):
    """Ammonia welcome screen."""

    INTERACTIONS = {
        LCD.UP: {'method': 'select_prev_item', 'args': ()},
        LCD.DOWN: {'method': 'select_next_item', 'args': ()},
        LCD.SELECT: {'method': 'transition_to_item', 'args': ()}
    }

    ITEMS = ('measure', 'calibrate')


    def __init__(self, lcd):
        super(Welcome, self).__init__(lcd, self.INTERACTIONS, self.ITEMS)


class Calibrate(Selection):
    """Select probe before calibration."""

    INTERACTIONS = {
        LCD.LEFT: {'method': 'transition_to', 'args': ('screens.Welcome', )},
        LCD.UP: {'method': 'select_prev_item', 'args': ()},
        LCD.DOWN: {'method': 'select_next_item', 'args': ()},
        LCD.SELECT: {'method': 'transition_to_item', 'args': ()}
    }

    ITEMS = ('temperature', 'EC', 'ORP')


    def __init__(self, lcd):
        super(Calibrate, self).__init__(lcd, self.INTERACTIONS, self.ITEMS)
