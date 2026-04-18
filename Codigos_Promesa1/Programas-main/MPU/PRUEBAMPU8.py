import smbus
import time
import csv
from datetime import datetime
from math import atan2, sqrt, degrees

# Inicializar el bus I2C
bus = smbus.SMBus(1)
addr = 0x68
bus.write_byte_data(addr, 0x6B, 0)  # Despertar el MPU6050

# Función para leer una palabra (16 bits) desde un registro
def read_word(reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg + 1)
    val = (h << 8) + l
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

# Calibración inicial
print("Calibrando... No muevas el sensor.")
n_calib = 500
accel_offset = {'x': 0, 'y': 0, 'z': 0}
gyro_offset = {'x': 0, 'y': 0, 'z': 0}

for _ in range(n_calib):
    accel_offset['x'] += read_word(0x3B)
    accel_offset['y'] += read_word(0x3D)
    accel_offset['z'] += read_word(0x3F)
    gyro_offset['x'] += read_word(0x43)
    gyro_offset['y'] += read_word(0x45)
    gyro_offset['z'] += read_word(0x47)
    time.sleep(0.002)

accel_offset = {k: v / n_calib for k, v in accel_offset.items()}
gyro_offset = {k: v / n_calib for k, v in gyro_offset.items()}
print("Calibración completada.\n")

# Crear archivo CSV
filename = f"mpu6050_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
file = open(filename, mode='w', newline='')
writer = csv.writer(file)
writer.writerow(["Tiempo", "Acel_X", "Acel_Y", "Acel_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Ang_X", "Ang_Y", "Ang_Z"])

# Variables para filtro exponencial (EMA)
alpha = 0.5
ax_f = ay_f = az_f = 0.0
gx_f = gy_f = gz_f = 0.0

# Variables para integración (posición angular)
angle_x = angle_y = angle_z = 0.0
last_time = time.time()
alpha_fusion = 0.98  # Peso del giroscopio en filtro complementario

# Ciclo principal
ciclo = 0

try:
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # Leer datos del sensor
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

        # Calcular inclinación desde acelerómetro (roll y pitch)
        roll_acc = degrees(atan2(ay_f, az_f))
        pitch_acc = degrees(atan2(-ax_f, sqrt(ay_f**2 + az_f**2)))

        # Filtro complementario para combinar giroscopio y acelerómetro
        angle_x = alpha_fusion * (angle_x + gx_f * dt) + (1 - alpha_fusion) * pitch_acc
        angle_y = alpha_fusion * (angle_y + gy_f * dt) + (1 - alpha_fusion) * roll_acc
        angle_z += gz_f * dt  # yaw solo con giroscopio

        # Imprimir cada 10 ciclos
        if ciclo % 10 == 0:
            print(f"Aceleración: X={ax_f:.2f}g  Y={ay_f:.2f}g  Z={az_f:.2f}g")
            print(f"Ángulos estimados: Pitch(X)={angle_x:.1f}°  Roll(Y)={angle_y:.1f}°  Yaw(Z)={angle_z:.1f}°\n")

        # Guardar en CSV
        writer.writerow([
            datetime.now().isoformat(),
            round(ax_f, 3), round(ay_f, 3), round(az_f, 3),
            round(gx_f, 3), round(gy_f, 3), round(gz_f, 3),
            round(angle_x, 2), round(angle_y, 2), round(angle_z, 2)
        ])

        ciclo += 1
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Lectura detenida por el usuario.")
    file.close()
