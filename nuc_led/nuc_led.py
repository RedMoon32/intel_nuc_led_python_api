from abc import ABC, abstractmethod

DRIVER_LOCATION = '/proc/acpi/nuc_led'

LED_ID = 'id'
BRIGHTNESS = 'brightness'
STYLE = 'style'
COLOUR = 'colour'


class ColorIsNotValidException(Exception):
    def __init__(self, color):
        super().__init__("Color {0} is not valid color".format(color))


class StyleIsNotValidException(Exception):
    def __init__(self, style):
        super().__init__("Style {0} is not valid style".format(style))


class LED(ABC):
    """
    "Abstract" base class from which to derive RingLED and PowerLED
    """

    _led_id = None
    _colours = None
    _styles = {'Always On': 'none', '1Hz Blink': 'blink_fast',
               '0.5Hz Blink': 'blink_medium', '0.25Hz Blink': 'blink_slow',
               '1Hz Fade': 'fade_fast', '0.5Hz Fade': 'fade_medium',
               '0.25Hz Fade': 'fade_slow'}

    @abstractmethod
    def get_led_id(self):
        pass

    def styles(self):
        return list(LED._styles.values())

    @abstractmethod
    def valid_colours(self):
        pass

    @abstractmethod
    def _read_led_state(self):
        pass

    def get_led_state(self):
        """
        Reads led state from DRIVER_LOCATION
        Returns a dict of led state
        """
        self._led_state.update(self._read_led_state())
        return self._led_state

    def set_led_state(self, data):
        """
        Writes content of data to DRIVER_LOCATION
        """
        current_state = self.get_led_state()
        brightness = data.get(BRIGHTNESS, current_state[BRIGHTNESS])
        style = data.get(STYLE, current_state[STYLE])
        colour = data.get(COLOUR, current_state[COLOUR])
        f = open(DRIVER_LOCATION, 'w')
        payload = ','.join([self.get_led_id(), str(brightness), style, colour])
        print(payload, file=f)
        f.close()

        # update stored state
        self.get_led_state()

    def _get_state_from_text(self, text):
        brightness = (text[0]).split(': ')[1].split('%')[0]
        style = ((text[1]).split(': ')[1].split(' (')[0])
        colour = ((text[2]).split(': ')[1].split(' (')[0]).lower()

        data = {BRIGHTNESS: int(brightness),
                STYLE: LED._styles[style],
                COLOUR: colour}
        return data

    def set_brightness(self, brightness):
        brightness = max(0, min(100, brightness))
        self.set_led_state({BRIGHTNESS: brightness})

    def set_colour(self, colour):
        if colour in self.valid_colours():
            self.set_led_state({COLOUR: colour})
        else:
            raise ColorIsNotValidException(colour)

    def set_style(self, style):
        if style in LED._styles.values():
            self.set_led_state({STYLE: style})
        else:
            raise StyleIsNotValidException(style)

    def turn_off_led(self):
        self.set_led_state({BRIGHTNESS: 0, STYLE: 'none', COLOUR: 'off'})


class RingLED(LED):
    """
    Derived class holding data specific to the ring led
    """

    _led_id = 'ring'
    _colours = ["off", "cyan", "pink", "yellow",
                "blue", "red", "green", "white"]

    def __init__(self):
        self._led_state = {LED_ID: RingLED._led_id}
        self.get_led_state()

    def get_led_id(self):
        return RingLED._led_id

    def valid_colours(self):
        return RingLED._colours

    def _read_led_state(self):
        f = open(DRIVER_LOCATION, 'r')
        state = f.read()
        state = state.split('\n')
        ring_state = state[4:-2]
        f.close()
        return self._get_state_from_text(ring_state)


class PowerLED(LED):
    """
    Derived class holding data specific to the power led
    """

    _led_id = 'power'
    _colours = ["off", "blue", "amber"]

    def __init__(self):
        self._led_state = {LED_ID: PowerLED.led_id}
        self.get_led_state()

    def get_led_id(self):
        return PowerLED._led_id

    def valid_colours(self):
        return PowerLED._colours

    def _read_led_state(self):
        f = open(DRIVER_LOCATION, 'r')
        state = f.read()
        state = state.split('\n')
        power_state = state[:3]
        f.close()
        return self._get_state_from_text(power_state)
