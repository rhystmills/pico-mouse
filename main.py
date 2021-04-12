import time
import board
import busio
import usb_hid
from adafruit_hid.mouse import Mouse

mouse = Mouse(usb_hid.devices)

REGISTERS = (0, 6)  # Range of registers to read
REGISTER_SIZE = 1     # Number of bytes to read from each register.

i2c = busio.I2C(board.GP1, board.GP0, frequency=100000, timeout=255)
while not i2c.try_lock():
    pass

# Initialize and lock the I2C bus.

devices = i2c.scan()
while len(devices) < 1:
    devices = i2c.scan()
device = devices[0]
print('Found device with address: {}'.format(hex(device)))

try: 
    i2c.unlock()
finally:
    i2c.unlock()

def read_registers():
    while not i2c.try_lock():
        pass

    # Scan all the registers and read their byte values.
    result = bytearray(REGISTER_SIZE)
    for register in range(*REGISTERS):
        try:
            print("attempting read")
            # Do the handshake
            # i2c.writeto(device, bytes([0x40, 0x00]))
            # i2c.writeto(device, bytes([0x00]))
            # i2c.readfrom_into(device, result)
            i2c.writeto_then_readfrom(device, bytes([0x40, 0x00, 0x00]), register], result)
            # Immediately try to get data from the device
            print("read complete")
            # Pause briefly, because why not
            time.sleep(0.1)
        except OSError as err:
            # If there's an error, log it
            print("OS error: {0}".format(err))
            continue  # Ignore registers that don't exist!
        print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in result])))

    # Unlock the I2C bus when finished.  Ideally put this in a try-finally!
    try: 
        i2c.unlock()
    finally:
        i2c.unlock()

# this function will recall itself every two seconds, triggering the read_registers function
def tick():
    # mouse.click(Mouse.LEFT_BUTTON) 
    read_registers()
    time.sleep(2)
    tick()

tick()