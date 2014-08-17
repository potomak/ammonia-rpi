import string
import Adafruit_CharLCD as LCD
from ammonia import Ammonia

class Screen(object):
    """A screen."""

    def __init__(self, ammonia, interactions):
        self.ammonia = ammonia
        self.interactions = interactions


    def buttons(self):
        return self.interactions.keys()


    def action(self, button):
        return self.interactions[button]


class Selection(Screen):
    """A selection screen."""

    LCD_LINES = 2


    def __init__(self, ammonia, interactions, items):
        super(Selection, self).__init__(ammonia, interactions)
        self.current_item = 0
        self.window_index = 0
        self.items = items


    def current_item_name(self):
        return self.items[self.current_item]


    def _print_selection(self):
        self.ammonia.lcd.clear()
        for item in self.items[self.window_index:self.window_index + self.LCD_LINES]:
            cursor = chr(Ammonia.RIGHT_ARROW_CHAR) if item == self.current_item_name() else ' '
            self.ammonia.lcd.message("%s%s\n" % (cursor, string.capwords(item, '_').replace('_', '')))


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


    def __init__(self, ammonia):
        super(Welcome, self).__init__(ammonia, self.INTERACTIONS, self.ITEMS)


class Calibrate(Selection):
    """Select probe before calibration."""

    INTERACTIONS = {
        LCD.LEFT: {'method': 'transition_to', 'args': ('welcome', )},
        LCD.UP: {'method': 'select_prev_item', 'args': ()},
        LCD.DOWN: {'method': 'select_next_item', 'args': ()},
        LCD.SELECT: {'method': 'transition_to_item', 'args': ()}
    }

    ITEMS = ('temperature', 'EC', 'ORP')


    def __init__(self, ammonia):
        super(Calibrate, self).__init__(ammonia, self.INTERACTIONS, self.ITEMS)


class Measure(Screen):
    """Measure NH4+ concentration."""

    INTERACTIONS = {
        LCD.LEFT: {'method': 'transition_to', 'args': ('welcome', )}
    }


    def __init__(self, ammonia):
        super(Measure, self).__init__(ammonia, self.INTERACTIONS)


    def screen_init(self):
        self.ammonia.lcd.clear()
        self.ammonia.lcd.message("Measuring...")


    def screen_update(self):
        while self.ammonia.daemon_should_run:
            self.ammonia.select_channel(Ammonia.TEMP_CHANNEL)
            self.ammonia.serial.write("R\r")
            temp = self.ammonia.read_message()

            self.ammonia.select_channel(Ammonia.EC_CHANNEL)
            self.ammonia.serial.write("%sC\r" % temp)
            ec, _, _ = self.ammonia.read_message().split(',')

            self.ammonia.select_channel(Ammonia.ORP_CHANNEL)
            self.ammonia.serial.write("R\r")
            orp = self.ammonia.read_message()

            ammonia = self._predict_ammonia(float(temp), int(ec), float(orp))

            self.ammonia.lcd.clear()
            self.ammonia.lcd.message("NH4+ (mg/l): %s\n" % ammonia)
            self.ammonia.lcd.message("Temp (C): %s - EC (mS/cm): %s" % (temp, ec))


    def _predict_ammonia(self, temp, ec, orp):
        # TODO: implement ammonia prediction algorithm
        pass
