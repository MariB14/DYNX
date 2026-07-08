import time
from smbus2 import SMbus
from bmp280 import BMP280



bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

while True:
    pressure = bmp280.get_pressure()

    presionmar = 1013.25
    altura = 44330.8 * (1.0-(pressure/presionmar) ** 0.19026)
    print(f"{altura}m")
    time.sleep(1)
