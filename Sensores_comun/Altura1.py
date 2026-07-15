import time
from smbus2 import SMBus
from bmp280 import BMP280
import RPi.GPIO as GPIO

# Configuración del LED
ledPin = 17 
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, GPIO.LOW)

# Configuración del bus I2C y el sensor
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)
pressure = bmp280.get_pressure()

 # Cálculo de altitud
presionmar = 1013.25
altura = 44330.8 * (1.0 - (pressure / presionmar) ** 0.19026)

try:

    while True:
       
        pressure = bmp280.get_pressure()
        actual = 44330.8 * (1.0 - (pressure / presionmar) ** 0.19026)
        dif = altura-actual
        # Formatear la salida a 2 decimales para que sea más legible
        print(f"Altitud estimada: {dif:.2f} m")
        
        # Lógica del LED
        if dif >= 1:
            GPIO.output(ledPin, GPIO.HIGH)
            print("LED ACTIVADO")
        else:
            GPIO.output(ledPin, GPIO.LOW)
            print("LED APAGADO")
            
        time.sleep(1)

except KeyboardInterrupt:
    # Se ejecuta al presionar Ctrl+C
    print("\nPrograma detenido por el usuario.")

finally:
    # Asegura que los pines se liberen correctamente sin importar cómo termine el script
    GPIO.cleanup()
    print("Pines GPIO limpiados.")
