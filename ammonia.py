import sys
import signal
import serial
import threading
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD
from screens import SCREENS


class Ammonia(object):
    """Class to interact with EC, ORP, and TEMP probes and an HD44780 character LCD display."""

    # debounce time
    DEBOUNCE = 0.1

    # channel selection pins
    A_PIN = 16
    B_PIN = 18

    # plate buttons
    BUTTONS = (LCD.LEFT, LCD.RIGHT, LCD.UP, LCD.DOWN, LCD.SELECT)

    # probes channels
    EC_CHANNEL   = 1
    ORP_CHANNEL  = 2
    TEMP_CHANNEL = 3

    # initialization screen
    INIT_SCREEN = 'welcome'

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
        self.current_screen_daemon = None
        self.daemon_should_run = False
        prev_keys = ['%s_prev' % x for x in self.BUTTONS]
        time_keys = ['%s_time' % x for x in self.BUTTONS]
        self.inputs_state = dict(zip(prev_keys + time_keys, [GPIO.HIGH]*5 + [0]*5))


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


    def read_message(self):
        message = ''

        data = self.serial.read()
        while data != "\r":
            message = message + data
            data = self.serial.read()

        return message


    def select_channel(self, number):
        number = number - 1
        b_value = number % 2
        number = number / 2
        a_value = number % 2

        GPIO.output(self.A_PIN, GPIO.LOW if a_value == 0 else GPIO.HIGH)
        GPIO.output(self.B_PIN, GPIO.LOW if b_value == 0 else GPIO.HIGH)


    def _call_method(self, name, args=()):
        return getattr(self, '_%s' % name)(*args)


    def _get_screen_class(self, target):
        return SCREENS[target]


    def _handle_input(self):
        for button in self.current_screen_instance.buttons():
            curr_key = '%s_curr' % button
            prev_key = '%s_prev' % button
            time_key = '%s_time' % button

            self.inputs_state[curr_key] = self.lcd._mcp.input(button)

            # if the switch changed, due to bounce or pressing...
            if self.inputs_state[curr_key] != self.inputs_state[prev_key]:
                # reset the debouncing timer
                self.inputs_state[time_key] = time.time()

            if time.time() - self.inputs_state[time_key] > self.DEBOUNCE:
                # whatever the switch is at, its been there for a long time so
                # lets settle on it!
                if self.lcd.is_pressed(button):
                    action = self.current_screen_instance.action(button)
                    self._call_method(action['method'], action['args'])

            self.inputs_state[prev_key] = self.inputs_state[curr_key]


    def _transition_to(self, target):
        # wait for current thread to join
        if self.current_screen_daemon:
            self.daemon_should_run = False
            self.lcd.clear()
            self.lcd.message("Please wait...")
            self.current_screen_daemon.join(10)

        # create a new instance of target screen class
        self.current_screen = target
        TargetScreenClass = self._get_screen_class(target)
        self.current_screen_instance = TargetScreenClass(self)
        self.current_screen_instance.screen_init()

        # start update thread if screen_update method is defined
        target_method = getattr(self.current_screen_instance, 'screen_update', False)
        if target_method:
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


    def _calibrate_selected_probe(self):
        # TODO
        pass


    def start(self):
        self._transition_to(self.INIT_SCREEN)
        time_stamp = time.time()

        while True:
            self._handle_input()


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
