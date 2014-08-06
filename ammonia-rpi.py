import sys
import signal
import serial
import threading
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
        'welcome': {
            LCD.UP: { 'method': 'transition_to', 'args': ('measure') },
            LCD.DOWN: { 'method': 'transition_to', 'args': ('calibrate') }
        },
        'measure': {
            LCD.LEFT: { 'method': 'transition_to', 'args': ('welcome') }
        },
        'calibrate': {
            LCD.LEFT: { 'method': 'transition_to', 'args': ('welcome') },
            LCD.UP: { 'method': 'select_next_probe', 'args': () },
            LCD.DOWN: { 'method': 'select_prev_probe', 'args': () },
            LCD.SELECT: { 'method': 'calibrate_selected_probe', 'args': () }
        }
    }


    def __init__(self):
        self.__setup_serial()
        self.__setup_LCD()
        self.__setup_GPIO()
        self.current_screen = 'welcome'
        self.current_screen_daemon = None
        self.daemon_should_run = False


    def __setup_serial(self):
        self.serial = serial.Serial('/dev/ttyAMA0', 38400)


    def __setup_LCD(self):
        self.lcd = LCD.Adafruit_CharLCDPlate()
        self.lcd.clear()


    def __setup_GPIO(self):
        GPIO.setmode(GPIO.BOARD)

        # channel selector pins
        GPIO.setup(A_PIN, GPIO.OUT)
        GPIO.setup(B_PIN, GPIO.OUT)


    def __read_message(self):
        message = ''

        data = self.serial.read()
        while data != "\r":
            message = message + data
            data = self.serial.read()

        return message


    def __select_channel(self, number):
        b_value = number % 2
        number = number / 2
        a_value = number % 2

        GPIO.output(A_PIN, GPIO.LOW if a_value == 0 else GPIO.HIGH)
        GPIO.output(B_PIN, GPIO.LOW if b_value == 0 else GPIO.HIGH)


    def __call_method(self, name, args=()):
        getattr(self, '__%s' % name)(*args)


    def __handle_input(self):
        screen = SCREENS[self.current_screen]

        for button in screen.keys():
            if self.lcd.is_pressed(button):
                state = screen[button]
                self.__call_method(state['method'])(state['args'])


    def __transition_to(self, target):
        if self.current_screen_daemon:
            self.daemon_should_run = False
            self.current_screen_daemon.join(10)

        self.current_screen = target
        self.__call_method('%s_screen_init' % target)
        target_method = getattr(self, '__%s_screen_update' % target)
        self.daemon_should_run = True
        self.current_screen_daemon = threading.Thread(target=target_method)
        self.current_screen_daemon.daemon = True
        self.current_screen_daemon.start()


    def __select_next_probe(self):
        # TODO
        pass


    def __select_prev_probe(self):
        # TODO
        pass


    def __calibrate_selected_probe(self):
        # TODO
        pass


    def __welcome_screen_init(self):
        self.lcd.clear()
        self.lcd.message("Measure\n")
        self.lcd.message("Calibrate\n")


    def __welcome_screen_update(self):
        pass


    def __measure_screen_init(self):
        self.lcd.clear()
        self.lcd.message("Measuring...")


    def __measure_screen_update(self):
        while self.daemon_should_run:
            self.__select_channel(TEMP)
            self.serial.write("R\r")
            temp = self.__read_message()

            self.__select_channel(EC)
            self.serial.write("%sC\r" % temp)
            ec, _, _ = self.__read_message().split(',')

            self.__select_channel(ORP)
            self.serial.write("R\r")
            orp = self.__read_message()

            ammonia = self.__predict_ammonia(float(temp), int(ec), float(orp))

            self.lcd.clear()
            self.lcd.message("NH3: %s\n" % ammonia)
            self.lcd.message("Temp: %s - EC: %s" % (temp, ec))


    def __calibrate_screen_init(self):
        # TODO: implement probe selection for calibration
        pass


    def __calibrate_screen_update(self):
        pass


    def __predict_ammonia(self, temp, ec, orp):
        # TODO: implement ammonia prediction algorithm
        pass


    def start(self):
        self.__transition_to('welcome')

        while True:
            self.__handle_input()


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
