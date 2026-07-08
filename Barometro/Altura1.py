try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280
from time import sleep

# Iniciando el BME280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

PRESION_NIVEL_MAR = 1013.25  # presión estándar a nivel del mar en hPa

while True:
    presion = bme280.get_pressure()
    altura = 44330.0 * (1.0 - (presion / PRESION_NIVEL_MAR) ** 0.1903)

    print(f"Presion:     {presion:.2f} hPa")
    print(f"Altura:      {altura:.2f} m")
    sleep(1)