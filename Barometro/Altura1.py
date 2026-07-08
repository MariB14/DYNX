try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
import bme280

# Iniciando el BME280
bus = SMBus(1)
calibration_params = bme280.load_calibration_params(bus, 0x76)

from time import sleep

PRESION_NIVEL_MAR = 1013.25

while True:
    data = bme280.sample(bus, 0x76, calibration_params)
    presion     = data.pressure
    altura      = 44330.0 * (1.0 - (presion / PRESION_NIVEL_MAR) ** 0.1903)

    print(f"Presion:     {presion:.2f} hPa")
    print(f"Altura:      {altura:.2f} m")
    sleep(1)