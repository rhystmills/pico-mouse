import time
import math
from collections import namedtuple
from adafruit_bus_device.i2c_device import I2CDevice
import busio
import board
import usb_hid
from adafruit_hid.mouse import Mouse

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Nunchuk.git"

_I2C_INIT_DELAY = 0.1


class Nunchuk:
    """
    Class which provides interface to Nintendo Nunchuk controller.
    :param i2c: The `busio.I2C` object to use.
    :param address: The I2C address of the device. Default is 0x52.
    :type address: int, optional
    :param i2c_read_delay: The time in seconds to pause between the
        I2C write and read. This needs to be at least 200us. A
        conservative default of 2000us is used since some hosts may
        not be able to achieve such timing.
    :type i2c_read_delay: float, optionalit
    """

    _Values = namedtuple("Values", ("joystick", "buttons", "acceleration"))
    _Joystick = namedtuple("Joystick", ("x", "y"))
    _Buttons = namedtuple("Buttons", ("C", "Z"))
    _Acceleration = namedtuple("Acceleration", ("x", "y", "z"))

    def __init__(self, i2c, address=0x52, i2c_read_delay=0.002):
        self.buffer = bytearray(8)
        self.i2c_device = I2CDevice(i2c, address)
        self._i2c_read_delay = i2c_read_delay
        time.sleep(_I2C_INIT_DELAY)
        with self.i2c_device as i2c_dev:
            # turn off encrypted data
            i2c_dev.write(b"\xF0\x55")
            time.sleep(_I2C_INIT_DELAY)
            i2c_dev.write(b"\xFB\x00")

    @property
    def values(self):
        """The current state of all values."""
        self._read_data()
        return self._Values(
            self._joystick(do_read=False),
            self._buttons(do_read=False),
            self._acceleration(do_read=False),
        )

    @property
    def joystick(self):
        """The current joystick position."""
        return self._joystick()

    @property
    def buttons(self):  # pylint: disable=invalid-name
        """The current pressed state of button Z."""
        return self._buttons()

    @property
    def acceleration(self):
        """The current accelerometer reading."""
        return self._acceleration()

    def _joystick(self, do_read=True):
        if do_read:
            self._read_data()
        return self._Joystick(self.buffer[0], self.buffer[1])  # x, y

    def _buttons(self, do_read=True):
        if do_read:
            self._read_data()
        return self._Buttons(
            not bool(self.buffer[5] & 0x02), not bool(self.buffer[5] & 0x01)  # C  # Z
        )

    def _acceleration(self, do_read=True):
        if do_read:
            self._read_data()
        return self._Acceleration(
            ((self.buffer[5] & 0xC0) >> 6) | (self.buffer[2] << 2),  # ax
            ((self.buffer[5] & 0x30) >> 4) | (self.buffer[3] << 2),  # ay
            ((self.buffer[5] & 0x0C) >> 2) | (self.buffer[4] << 2),  # az
        )

    def _read_data(self):
        return self._read_register(b"\x00")

    def _read_register(self, address):
        with self.i2c_device as i2c:
            i2c.write(address)
            time.sleep(self._i2c_read_delay)  # at least 200us
            i2c.readinto(self.buffer)
        return self.buffer

m = Mouse(usb_hid.devices)
nc = Nunchuk(busio.I2C(board.GP1, board.GP0, frequency=100000, timeout=255))

scaleX = 0.01
scaleY = - 0.01

deadzone_upper = 127
deadzone_lower = 123

cDown = False
zDown = False

# This is to allow double checking (only on left click - and it doesn't really work)
CHECK_COUNT = 0


# This is just to show that we're getting back data - uncomment it and hold down the buttons
# while True:
#    print((0 if nc.button_C else 1, 0 if nc.button_Z else 1))

def attemptLog(n):
    if n > 1:
        return math.log(n)
    if n < -1:
        return -math.log(abs(n))
    return 1

### How should it work:
# If moveX is greater than one, convert to int and move that number of pixels per tick
# If moveX is less than one, divide one by the value. Convert that to an int x. Move the mouseevery x ticks
# Perhaps change this to be based on time in the future, rather than arbitrary ticks?

# base rate values for sub-pixel movement
ySteps = 0
xSteps = 0

minMove = 0.00000001

def move_if_queued(xMove, yMove):
    global xSteps
    global ySteps
    oldXSteps = xSteps
    oldYSteps = ySteps
    newXSteps = int(1/abs(xMove)) if xMove > minMove or xMove < -minMove else 0
    newYSteps = int(1/abs(yMove)) if yMove > minMove or yMove < -minMove else 0
    x_to_move = False
    y_to_move = False
    
    if xSteps == 1:
        x_to_move = True
        xSteps = 0
    if ySteps == 1:
        y_to_move = True
        ySteps = 0

    xVal = 1 if xMove > 0 else -1
    yVal = 1 if yMove > 0 else -1
    m.move(xVal if x_to_move else 0, yVal if y_to_move else 0, 0)

    if xSteps > 0:
        if newXSteps < oldXSteps:
            xSteps = newXSteps
        else:
            xSteps -= 1
    else: xSteps = newXSteps

    if ySteps > 0:
        if newYSteps < oldYSteps:
            ySteps = newYSteps
        else:
            ySteps -= 1
    else: ySteps = newYSteps
        
def diff_from_deadzone(x, y):
    if x <= deadzone_lower or x >= deadzone_upper or y <= deadzone_lower or y >= deadzone_upper:
        relX = min(0, x - deadzone_lower) if x <= deadzone_lower else max(0, x - deadzone_upper)
        relY = min(0, y - deadzone_lower) if y <= deadzone_lower else max(0, y - deadzone_upper)
        return (relX, relY)
    return (0, 0)

while True:
    x, y = nc.joystick
    # Eliminate spurious reads
    if x == 255 or y == 255:
        continue
    print("x: ", x)
    print("y: ", y)
    #if x or y not in deadzone
    (relX, relY) = diff_from_deadzone(x,y)
    xMove = scaleX * abs(relX) * attemptLog(relX)
    yMove = scaleY * abs(relY) * attemptLog(relY)

    if xMove >= 1 or yMove >= 1 or xMove <= -1 or yMove <= -1:
        m.move(int(xMove) if xMove >= 1 or xMove <= -1 else 0, int(yMove) if yMove >= 1 or yMove <= -1 else 0, 0)
    move_if_queued(xMove, yMove)

    buttons = nc.buttons
    c = buttons.C
    z = buttons.Z

    if z and not zDown:
        stillDown = True
        for n in range(CHECK_COUNT):
            if nc.button_Z:
                stillDown = False
                break
        if stillDown:
            m.press(Mouse.RIGHT_BUTTON)
            zDown = True
    elif not z and zDown:
        stillDown = True
        for n in range(CHECK_COUNT):
            if not nc.button_Z:
                stillDown = False
                break
        if stillDown:
            m.release(Mouse.RIGHT_BUTTON)
            zDown = False
    if c and not cDown:
        m.press(Mouse.LEFT_BUTTON)
        cDown = True
    elif not c and cDown:
        m.release(Mouse.LEFT_BUTTON)
        cDown = False