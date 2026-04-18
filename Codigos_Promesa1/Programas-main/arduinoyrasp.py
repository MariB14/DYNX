import serial
import time

# Reemplaza '/dev/ttyACM0' si tu puerto es diferente
puerto = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Espera a que se inicialice el Arduino

try:
    while True:
        if puerto.in_waiting > 0:
            linea = puerto.readline().decode('utf-8').strip()
            print("Valor recibido:", linea)
except KeyboardInterrupt:
    print("Terminando...")
    puerto.close()
