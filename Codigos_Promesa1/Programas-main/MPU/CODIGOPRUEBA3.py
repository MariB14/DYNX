import smbus
import time
import csv
from datetime import datetime

bus = smbus.SMBus(1)
addr = 0x68
bus.write_byte_data(addr, 0x6B, 0)

def read(reg):
    h = bus.read_byte_data(addr, reg)
    l = bus.read_byte_data(addr, reg + 1)
    v = (h << 8) + l
    return v - 65536 if v > 32767 else v

# Primera fase- calibracion del mpu 
print("Calibrando... no muevas el sensor.")
n = 100
acel_offset = {'x': 0, 'y': 0, 'z': 0}
gyro_offset = {'x': 0, 'y': 0, 'z': 0}

for _ in range(n):
    acel_offset['x'] += read(0x3B)
    acel_offset['y'] += read(0x3D)
    acel_offset['z'] += read(0x3F)
    gyro_offset['x'] += read(0x43)
    gyro_offset['y'] += read(0x45)
    gyro_offset['z'] += read(0x47)
    time.sleep(0.01)

acel_offset = {k: v / n for k, v in acel_offset.items()}
gyro_offset = {k: v / n for k, v in gyro_offset.items()}
print("Calibración completada.")

# Segunda fase- Genera la tabla CSV donde se recopilan y guardan los datos
filename = f"mpu6050_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", 
                     "ax(g)", "ay(g)", "az(g)", 
                     "gx(°/s)", "gy(°/s)", "gz(°/s)"])

    print(f"Juntando datos en: {filename} (Ctrl+C para detener)\n")

    try:
        while True:
            ax = (read(0x3B) - acel_offset['x']) / 16384.0
            ay = (read(0x3D) - acel_offset['y']) / 16384.0
            az = (read(0x3F) - acel_offset['z']) / 16384.0
            gx = (read(0x43) - gyro_offset['x']) / 131.0
            gy = (read(0x45) - gyro_offset['y']) / 131.0
            gz = (read(0x47) - gyro_offset['z']) / 131.0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            writer.writerow([timestamp, 
                             round(ax, 2), round(ay, 2), round(az, 2),
                             round(gx, 2), round(gy, 2), round(gz, 2)])
            file.flush()

            print("acelerómetro:", round(ax, 2), round(ay, 2), round(az, 2))
            print("giroscopio:", round(gx, 2), round(gy, 2), round(gz, 2))
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nGrabación detenida.")
