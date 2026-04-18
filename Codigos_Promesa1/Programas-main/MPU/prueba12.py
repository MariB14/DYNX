import smbus
import time
import csv
from datetime import datetime
from math import atan2, sqrt, degrees

# Nuevas importaciones
import bme280
import smbus2
import board
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

# Configuración OLED (I2C, 128x64)
i2c_oled = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Inicializar I2C para sensores
bus = smbus.SMBus(1)
addr_mpu = 0x68
addr_bme = 0x76  # o 0x77 dependiendo del módulo
bus.write_byte_data(addr_mpu, 0x6B, 0)

# Configurar BME280
bme_calib = bme280.load_calibration_params(bus, addr_bme)

# Función para leer MPU6050
def read_word(reg):
    h = bus.read_byte_data(addr_mpu, reg)
    l = bus.read_byte_data(addr_mpu, reg + 1)
    val = (h << 8) + l
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

# Calibración
print("Calibrando... No muevas el sensor.")
n_calib = 200
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
filename = f"datos_sensores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
file = open(filename, mode='w', newline='')
writer = csv.writer(file)
writer.writerow([
    "Tiempo",
    "Acel_X", "Acel_Y", "Acel_Z",
    "Gyro_X", "Gyro_Y", "Gyro_Z",
    "Pitch", "Roll", "Yaw",
    "Temp_BME", "Presión_BME", "Humedad_BME"
])

# Filtros y variables
alpha = 0.3
ax_f = ay_f = az_f = gx_f = gy_f = gz_f = 0.0
pitch = roll = yaw = 0.0
pitch_smoothed = roll_smoothed = 0.0
alpha_fusion = 0.96
last_time = time.time()
ciclo = 0

# Inicia loop
try:
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # MPU6050
        ax = (read_word(0x3B) - accel_offset['x']) / 16384.0
        ay = (read_word(0x3D) - accel_offset['y']) / 16384.0
        az = (read_word(0x3F) - accel_offset['z']) / 16384.0
        gx = (read_word(0x43) - gyro_offset['x']) / 131.0
        gy = (read_word(0x45) - gyro_offset['y']) / 131.0
        gz = (read_word(0x47) - gyro_offset['z']) / 131.0

        # Filtro exponencial
        ax_f = alpha * ax + (1 - alpha) * ax_f
        ay_f = alpha * ay + (1 - alpha) * ay_f
        az_f = alpha * az + (1 - alpha) * az_f
        gx_f = alpha * gx + (1 - alpha) * gx_f
        gy_f = alpha * gy + (1 - alpha) * gy_f
        gz_f = alpha * gz + (1 - alpha) * gz_f

        # Ángulos
        pitch_acc = degrees(atan2(-ax_f, sqrt(ay_f**2 + az_f**2)))
        roll_acc = degrees(atan2(ay_f, az_f)) if abs(az_f) > 0.01 else roll
        pitch = alpha_fusion * (pitch + gx_f * dt) + (1 - alpha_fusion) * pitch_acc
        roll = alpha_fusion * (roll + gy_f * dt) + (1 - alpha_fusion) * roll_acc
        yaw += gz_f * dt
        pitch_smoothed = 0.9 * pitch_smoothed + 0.1 * pitch
        roll_smoothed = 0.9 * roll_smoothed + 0.1 * roll

        # BME280
        bme_data = bme280.sample(bus, addr_bme, bme_calib)
        temp = bme_data.temperature
        pres = bme_data.pressure
        hum = bme_data.humidity if hasattr(bme_data, 'humidity') else 0

        # Mostrar en OLED cada 10 ciclos
        if ciclo % 10 == 0:
            oled.fill(0)
            oled.text(f"T: {temp:.1f}C", 0, 0, 1)
            oled.text(f"H: {hum:.1f}%", 0, 10, 1)
            oled.text(f"P: {pres:.1f} hPa", 0, 20, 1)
            oled.text(f"Pitch: {pitch_smoothed:.1f}", 0, 40, 1)
            oled.text(f"Roll: {roll_smoothed:.1f}", 0, 50, 1)
            oled.show()

        # Guardar en CSV
        writer.writerow([
            datetime.now().isoformat(),
            round(ax_f, 3), round(ay_f, 3), round(az_f, 3),
            round(gx_f, 3), round(gy_f, 3), round(gz_f, 3),
            round(pitch_smoothed, 2), round(roll_smoothed, 2), round(yaw, 2),
            round(temp, 2), round(pres, 2), round(hum, 2)
        ])

        ciclo += 1
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa detenido.")
    file.close()
