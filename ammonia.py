import sys
import signal
import serial
import threading
import screens
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD


class Ammonia(object):
    """Class to interact with EC, ORP, and TEMP probes and an HD44780 character LCD display."""

    # channel selection pins
    A_PIN = 7
    B_PIN = 12

    # probes channels
    EC_CHANNEL   = 1
    ORP_CHANNEL  = 2
    TEMP_CHANNEL = 3

    # app screens
    SCREENS = {
        'screens.Welcome': {},
        'measure': {
            LCD.LEFT: {'method': 'transition_to', 'args': ('welcome', )}
        },
        'calibrate': {
            LCD.LEFT: {'method': 'transition_to', 'args': ('welcome', )},
            LCD.UP: {'method': 'select_next_probe', 'args': ()},
            LCD.DOWN: {'method': 'select_prev_probe', 'args': ()},
            LCD.SELECT: {'method': 'calibrate_selected_probe', 'args': ()}
        }
    }

    # custom characters
    RIGHT_ARROW_CHAR = 0
    RIGHT_ARROW_CHAR_BITMAP = (
        0b00000000,
        0b00001000,
        0b00001100,
        0b00001110,
        0b00001100,
        0b00001000,
        0b00000000,
        0b00000000
    )
    DOUBLE_ARROW_CHAR = 1
    DOUBLE_ARROW_CHAR_BITMAP = [
        0b00000100,
        0b00001110,
        0b00011111,
        0b00000000,
        0b00011111,
        0b00001110,
        0b00000100,
        0b00000000
    ]


    def __init__(self):
        self._setup_serial()
        self._setup_LCD()
        self._setup_GPIO()
        self.current_screen = 'welcome'
        self.current_screen_daemon = None
        self.daemon_should_run = False


    def _setup_serial(self):
        self.serial = serial.Serial('/dev/ttyAMA0', 38400)


    def _setup_LCD(self):
        self.lcd = LCD.Adafruit_CharLCDPlate()
        self._create_custom_char(self.RIGHT_ARROW_CHAR, self.RIGHT_ARROW_CHAR_BITMAP)
        self._create_custom_char(self.DOUBLE_ARROW_CHAR, self.DOUBLE_ARROW_CHAR_BITMAP)
        self.lcd.clear()


    def _setup_GPIO(self):
        GPIO.setmode(GPIO.BOARD)

        # channel selector pins
        GPIO.setup(self.A_PIN, GPIO.OUT)
        GPIO.setup(self.B_PIN, GPIO.OUT)


    def _create_custom_char(self, location, bitmap):
        self.lcd.write8(LCD.LCD_SETCGRAMADDR | ((location & 7) << 3), False)
        for line in bitmap:
            self.lcd.write8(line, True)
        self.lcd.write8(LCD.LCD_SETDDRAMADDR, False)


    def _read_message(self):
        message = ''

        data = self.serial.read()
        while data != "\r":
            message = message + data
            data = self.serial.read()

        return message


    def _select_channel(self, number):
        b_value = number % 2
        number = number / 2
        a_value = number % 2

        GPIO.output(self.A_PIN, GPIO.LOW if a_value == 0 else GPIO.HIGH)
        GPIO.output(self.B_PIN, GPIO.LOW if b_value == 0 else GPIO.HIGH)


    def _call_method(self, name, args=()):
        getattr(self, '_%s' % name)(*args)


    def _get_class(self, klass):
        parts = klass.split('.')
        module = '.'.join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m


    def _handle_input(self):
        for button in self.current_screen_instance.buttons():
            if self.lcd.is_pressed(button):
                action = self.current_screen_instance.action(button)
                self._call_method(action['method'], action['args'])


    def _transition_to(self, target):
        if self.current_screen_daemon:
            self.daemon_should_run = False
            self.lcd.clear()
            self.lcd.message("Please wait...")
            self.current_screen_daemon.join(10)

        self.current_screen = target
        self.current_screen_instance = self._get_class(target)(self.lcd)
        self.current_screen_instance.screen_init()
        target_method = getattr(self.current_screen_instance, 'screen_update')
        self.daemon_should_run = True
        self.current_screen_daemon = threading.Thread(target=target_method)
        self.current_screen_daemon.daemon = True
        self.current_screen_daemon.start()


    def _transition_to_item(self):
        target = self.current_screen_instance.current_item_name()
        self._transition_to(target)


    def _select_next_item(self):
        self.current_screen_instance.select_next_item()


    def _select_prev_item(self):
        self.current_screen_instance.select_prev_item()


    def _select_next_probe(self):
        # TODO
        pass


    def _select_prev_probe(self):
        # TODO
        pass


    def _calibrate_selected_probe(self):
        # TODO
        pass


    def _measure_screen_init(self):
        self.lcd.clear()
        self.lcd.message("Measuring...")


    def _measure_screen_update(self):
        while self.daemon_should_run:
            self._select_channel(self.TEMP_CHANNEL)
            self.serial.write("R\r")
            temp = self._read_message()

            self._select_channel(self.EC_CHANNEL)
            self.serial.write("%sC\r" % temp)
            ec, _, _ = self._read_message().split(',')

            self._select_channel(self.ORP_CHANNEL)
            self.serial.write("R\r")
            orp = self._read_message()

            ammonia = self._predict_ammonia(float(temp), int(ec), float(orp))

            self.lcd.clear()
            self.lcd.message("NH4+ (mg/l): %s\n" % ammonia)
            self.lcd.message("Temp (C): %s - EC (mS/cm): %s" % (temp, ec))


    def _calibrate_screen_init(self):
        # TODO: implement probe selection for calibration
        pass


    def _calibrate_screen_update(self):
        pass


    def _predict_ammonia(self, temp, ec, orp):
        # TODO: implement ammonia prediction algorithm
        pass


    def start(self):
        self._transition_to('screens.Welcome')
        time_stamp = time.time()

        while True:
            time_now = time.time()
            if (time_now - time_stamp) >= 0.1:
                self._handle_input()
                time_stamp = time_now


def signal_handler(signal, frame):
    print 'Bye'
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    print 'Ammonia RPI'

    # register custom handler
    signal.signal(signal.SIGINT, signal_handler)

    ammonia = Ammonia()
    ammonia.start()
