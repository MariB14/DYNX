import smbus
import time

bus = smbus.SMBus(1)
addr = 0x68
bus.write_byte_data(addr, 0x6B, 0)

def read(reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg + 1)
    v = (h << 8) + l
    return v - 65536 if v > 32767 else v

while True:
    ax = read(0x3B) / 16384.0
    ay = read(0x3D) / 16384.0
    az = read(0x3F) / 16384.0

    gx = read(0x43) / 131.0
    gy = read(0x45) / 131.0
    gz = read(0x47) / 131.0

    print("acelerómetro:", round(ax, 2), round(ay, 2), round(az, 2))
    print("giroscopio:", round(gx, 2), round(gy, 2), round(gz, 2))
    time.sleep(0.5)
