import smbus
import time
import csv
from datetime import datetime

bus = smbus.SMBus(1)
addr = 0x68
bus.write_byte_data(addr, 0x6B, 0)

# Función para leer registros
def read_word(reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg + 1)
    val = (h << 8) + l
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

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

    # Filtro móvil
    buffer_size = 10
    accel_buffer = {'x': [], 'y': [], 'z': []}
    gyro_buffer = {'x': [], 'y': [], 'z': []}

    while True:
        try:
            ax = (read_word(0x3B) - accel_offset['x']) / 16384.0
            ay = (read_word(0x3D) - accel_offset['y']) / 16384.0
            az = (read_word(0x3F) - accel_offset['z']) / 16384.0
            gx = (read_word(0x43) - gyro_offset['x']) / 131.0
            gy = (read_word(0x45) - gyro_offset['y']) / 131.0
            gz = (read_word(0x47) - gyro_offset['z']) / 131.0

            # Filtro móvil
            for axis, val in zip(['x', 'y', 'z'], [ax, ay, az]):
                accel_buffer[axis].append(val)
                if len(accel_buffer[axis]) > buffer_size:
                    accel_buffer[axis].pop(0)
            for axis, val in zip(['x', 'y', 'z'], [gx, gy, gz]):
                gyro_buffer[axis].append(val)
                if len(gyro_buffer[axis]) > buffer_size:
                    gyro_buffer[axis].pop(0)

            ax_avg = sum(accel_buffer['x']) / len(accel_buffer['x'])
            ay_avg = sum(accel_buffer['y']) / len(accel_buffer['y'])
            az_avg = sum(accel_buffer['z']) / len(accel_buffer['z'])
            gx_avg = sum(gyro_buffer['x']) / len(gyro_buffer['x'])
            gy_avg = sum(gyro_buffer['y']) / len(gyro_buffer['y'])
            gz_avg = sum(gyro_buffer['z']) / len(gyro_buffer['z'])

            # Imprimir en consola
            print(f"acelerómetro: {round(ax_avg, 2)} {round(ay_avg, 2)} {round(az_avg, 2)}")
            print(f"giroscopio: {round(gx_avg, 2)} {round(gy_avg, 2)} {round(gz_avg, 2)}\n")

            # Guardar en CSV
            writer.writerow([datetime.now().isoformat(), round(ax_avg, 3), round(ay_avg, 3), round(az_avg, 3),
                             round(gx_avg, 3), round(gy_avg, 3), round(gz_avg, 3)])
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("Lectura terminada.")
            break
