import time
import board
import busio
from digitalio import DigitalInOut
import adafruit_rfm9x

CS = DigitalInOut(board.D8)
RESET = DigitalInOut(board.D22)
RADIO_FREQ_MHZ = 433.0

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
    print("✅ RFM9x inicializado correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar el módulo RFM9x: {e}")
    exit()  # Detener el programa si no se inicializa
