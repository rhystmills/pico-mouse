import board
import busio

REGISTERS = (0, 256)

REGISTER_SIZE = 2     # Number of bytes to read from each register.

# Initialize and lock the I2C bus.
i2c = busio.I2C(board.GP3, board.GP2)
while not i2c.try_lock():
    pass

print("started")

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
        i2c.writeto(device, bytes([0x40, 0x00, 0x00, register]))
        i2c.readfrom_into(device, result)
    except OSError as err:
        print("OS error: {0}".format(err))
        continue  # Ignore registers that don't exist!
    print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in result])))

# Unlock the I2C bus when finished.  Ideally put this in a try-finally!
i2c.unlock()