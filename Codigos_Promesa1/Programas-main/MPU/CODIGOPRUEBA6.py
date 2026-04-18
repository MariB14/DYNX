import smbus
import time
import csv
from datetime import datetime

# Variables iniciales
bus = smbus.SMBus(1)
addr = 0x68
bus.write_byte_data(addr, 0x6B, 0)  # Salir de modo de reposo

# Leer un registro de 16 bits con signo
def read_word(reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg + 1)
    val = (h << 8) + l
    return -((65535 - val) + 1) if val >= 0x8000 else val

# Calibración
print("Calibrando... No muevas el sensor.")
n = 500
accel_offset = {'x': 0, 'y': 0, 'z': 0}
gyro_offset = {'x': 0, 'y': 0, 'z': 0}
for _ in range(n):
    accel_offset['x'] += read_word(0x3B)
    accel_offset['y'] += read_word(0x3D)
    accel_offset['z'] += read_word(0x3F)
    gyro_offset['x'] += read_word(0x43)
    gyro_offset['y'] += read_word(0x45)
    gyro_offset['z'] += read_word(0x47)
    time.sleep(0.002)

accel_offset = {k: v / n for k, v in accel_offset.items()}
gyro_offset = {k: v / n for k, v in gyro_offset.items()}
print("Calibración completada.")

# Archivo CSV
filename = f"mpu6050_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Tiempo", "Acel_X", "Acel_Y", "Acel_Z", "Gyro_X", "Gyro_Y", "Gyro_Z"])

    # Variables para filtro EMA (Media Ponderada Exponencial)
    alpha = 0.3  # entre 0 (lento) y 1 (muy rápido)
    ax_f = ay_f = az_f = gx_f = gy_f = gz_f = 0

    ciclo = 0  # contador para limitar impresión

    while True:
        try:
            # Leer sensores y aplicar offsets
            ax = (read_word(0x3B) - accel_offset['x']) / 16384.0
            ay = (read_word(0x3D) - accel_offset['y']) / 16384.0
            az = (read_word(0x3F) - accel_offset['z']) / 16384.0
            gx = (read_word(0x43) - gyro_offset['x']) / 131.0
            gy = (read_word(0x45) - gyro_offset['y']) / 131.0
            gz = (read_word(0x47) - gyro_offset['z']) / 131.0

            # Filtro exponencial (EMA)
            ax_f = alpha * ax + (1 - alpha) * ax_f
            ay_f = alpha * ay + (1 - alpha) * ay_f
            az_f = alpha * az + (1 - alpha) * az_f
            gx_f = alpha * gx + (1 - alpha) * gx_f
            gy_f = alpha * gy + (1 - alpha) * gy_f
            gz_f = alpha * gz + (1 - alpha) * gz_f

            # Solo imprimir cada 10 ciclos (reduce saturación)
            if ciclo % 10 == 0:
                print(f"Acel: X={ax_f:.2f}g  Y={ay_f:.2f}g  Z={az_f:.2f}g")
                print(f"Giro: X={gx_f:.2f}°/s  Y={gy_f:.2f}°/s  Z={gz_f:.2f}°/s\n")

            # Guardar en CSV
            writer.writerow([
                datetime.now().isoformat(),
                round(ax_f, 3), round(ay_f, 3), round(az_f, 3),
                round(gx_f, 3), round(gy_f, 3), round(gz_f, 3)
            ])

            ciclo += 1
            time.sleep(0.05)  # Más lecturas por segundo

        except KeyboardInterrupt:
            print("Lectura detenida por el usuario.")
            break
