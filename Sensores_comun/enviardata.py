import serial
import time

puerto = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
print("Iniciando transmisión de datos reales...")

try:
    while True:
        # 1. Leer el buzón del barómetro
        try:
            with open('/dev/shm/altura.txt', 'r') as f:
                altitud = f.read().strip()
        except FileNotFoundError:
            altitud = "0.0" # Por si el sensor tarda en arrancar

        # 2. Leer el buzón del MPU6050
        try:
            with open('/dev/shm/imu.txt', 'r') as f:
                datos_imu = f.read().strip()
                # datos_imu se verá así: "1.02,0.05,-0.12"
        except FileNotFoundError:
            datos_imu = "0.0,0.0,0.0"

        # 3. Empaquetar todo junto
        mensaje = f"Alt:{altitud}m, Aceleraciones(X,Y,Z):{datos_imu}g\n"
        
        # 4. Enviar por el cable USB
        puerto.write(mensaje.encode('utf-8'))
        
        print(f"Enviado: {mensaje.strip()}")
        
        # Enviamos datos cada 0.2 segundos (5 veces por segundo)
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nTransmisión detenida.")
finally:
    puerto.close()