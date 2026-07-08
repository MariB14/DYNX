
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280

#iniciando el fakin bme

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

while True:
    presion = bme280.get_pressure(1023.15)
    altura = 44330.8*(1.0- (presion/1023.15)*0.19026)
    print(f"Altura actual: {altura}")