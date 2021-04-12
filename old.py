```
import time
import board
import busio
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_bus_device.i2c_device import I2CDevice

mouse = Mouse(usb_hid.devices)

REGISTERS = (0, 256) # Range of registers to read, from the first up to (but
                      # not including!) the second value.

REGISTER_SIZE = 2 # Number of bytes to read from each register.

# Initialize and lock the I2C bus.
i2c = busio.I2C(board.GP9, board.GP8)
while not i2c.try_lock():
    pass

# Find the first I2C device available.
devices = i2c.scan()
while len(devices) < 1:
    devices = i2c.scan()
device = devices[0]
print('Found device with address: {}'.format(hex(device)))


# Scan all the registers and read their byte values.
result = bytearray(REGISTER_SIZE)
for register in range(*REGISTERS):
    try:
        # i2c.writeto(device, bytes([register]))
        # i2c.readfrom_into(device, result)
        i2c.writeto_then_readfrom(device,bytes[0x40, 0x00, 0x00, register], result)
    except OSError:
        continue # Ignore registers that don't exist!
    print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in result])))

# Unlock the I2C bus when finished. Ideally put this in a try-finally!
i2c.unlock()
mouse = Mouse(usb_hid.devices)

def tick():
 mouse.click(Mouse.LEFT_BUTTON) 
 time.sleep(5)
 
tick()
