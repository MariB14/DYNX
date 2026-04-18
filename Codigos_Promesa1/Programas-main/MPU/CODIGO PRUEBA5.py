# Importamos las bibliotecas necesarias
import smbus                    # Para la comunicación I2C con el MPU6050
import time                     # Para pausas entre lecturas
import csv                      # Para guardar datos en archivo CSV
from datetime import datetime   # Para nombrar archivos con la fecha actual

# Variables para acumulación y seguimiento
px = 0
py = 0
pz = 0
n = 0

# Inicializamos el bus I2C
bus = smbus.SMBus(1)

# Dirección del MPU6050 (por defecto suele ser 0x68)
addr = 0x68

# Despertamos el MPU6050 (quitamos modo de suspensión)
bus.write_byte_data(addr, 0x6B, 0)

# Función para leer dos bytes y convertirlos en un valor con signo
def read_word(reg):
    h = bus.read_byte_data(addr, reg)       # Byte alto
    l = bus.read_byte_data(addr, reg + 1)   # Byte bajo
    val = (h << 8) + l                      # Combinamos los dos bytes
    if val >= 0x8000:                       # Si el valor representa un número negativo
        return -((65535 - val) + 1)
    else:
        return val

# --- Calibración inicial del sensor ---
print("Calibrando... No muevas el sensor.")

n = 500  # Número de lecturas para promediar

# Diccionarios para guardar las sumas de las lecturas (se convertirán en promedios)
accel_offset = {'x': 0, 'y': 0, 'z': 0}
gyro_offset = {'x': 0, 'y': 0, 'z': 0}

# Acumulamos 500 lecturas para calcular el promedio (desviación inicial)
for _ in range(n):
    accel_offset['x'] += read_word(0x3B)  # Acelerómetro X
    accel_offset['y'] += read_word(0x3D)  # Acelerómetro Y
    accel_offset['z'] += read_word(0x3F)  # Acelerómetro Z
    gyro_offset['x'] += read_word(0x43)   # Giroscopio X
    gyro_offset['y'] += read_word(0x45)   # Giroscopio Y
    gyro_offset['z'] += read_word(0x47)   # Giroscopio Z
    time.sleep(0.002)  # Pausa de 2ms para no saturar el bus

# Promediamos los valores acumulados para obtener la desviación base
accel_offset = {k: v / n for k, v in accel_offset.items()}
gyro_offset = {k: v / n for k, v in gyro_offset.items()}
print("Calibración completada.")

n = 0  # Reiniciamos el contador para uso posterior

# --- Preparar archivo CSV para guardar los datos ---
filename = f"mpu6050_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Abrimos el archivo para escritura
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Tiempo", "Acel_X", "Acel_Y", "Acel_Z", "Gyro_X", "Gyro_Y", "Gyro_Z"])

    # --- Filtro de promedio móvil para suavizar datos ---
    buffer_size = 10  # Tamaño del filtro móvil
    accel_buffer = {'x': [], 'y': [], 'z': []}  # Buffers para acelerómetro
    gyro_buffer = {'x': [], 'y': [], 'z': []}   # Buffers para giroscopio

    # Variables para posición calculada (acumulación de velocidades angulares)
    px = 0
    py = 0
    pz = 0

    # Variables para cálculo de desviación media
    sumx = sumy = sumz = 0
    xav = yav = zav = 0

    # --- Bucle principal de lectura ---
    while True:
        try:
            # Lectura y corrección con offsets, se escala a unidades reales
            ax = (read_word(0x3B) - accel_offset['x']) / 16384.0
            ay = (read_word(0x3D) - accel_offset['y']) / 16384.0
            az = (read_word(0x3F) - accel_offset['z']) / 16384.0
            gx = (read_word(0x43) - gyro_offset['x']) / 131.0
            gy = (read_word(0x45) - gyro_offset['y']) / 131.0
            gz = (read_word(0x47) - gyro_offset['z']) / 131.0

            # --- Aplicamos filtro de promedio móvil ---
            for axis, val in zip(['x', 'y', 'z'], [ax, ay, az]):
                accel_buffer[axis].append(val)
                if len(accel_buffer[axis]) > buffer_size:
                    accel_buffer[axis].pop(0)

            for axis, val in zip(['x', 'y', 'z'], [gx, gy, gz]):
                gyro_buffer[axis].append(val)
                if len(gyro_buffer[axis]) > buffer_size:
                    gyro_buffer[axis].pop(0)

            # Calculamos el promedio del buffer (valores suavizados)
            ax_avg = sum(accel_buffer['x']) / len(accel_buffer['x'])
            ay_avg = sum(accel_buffer['y']) / len(accel_buffer['y'])
            az_avg = sum(accel_buffer['z']) / len(accel_buffer['z'])
            gx_avg = sum(gyro_buffer['x']) / len(gyro_buffer['x'])
            gy_avg = sum(gyro_buffer['y']) / len(gyro_buffer['y'])
            gz_avg = sum(gyro_buffer['z']) / len(gyro_buffer['z'])

            # --- Acumulamos posición angular en cada eje ---
            px += gx_avg
            py += gy_avg
            pz += gz_avg

            # --- Cálculo de desviación media ---
            n += 1
            sumx += gx_avg
            sumy += gy_avg
            sumz += gz_avg
            promx = sumx / n
            promy = sumy / n
            promz = sumz / n

            xav += (gx_avg - promx)
            yav += (gy_avg - promy)
            zav += (gz_avg - promz)

            desvx = xav / n
            desvy = yav / n
            desvz = zav / n

            # --- Imprimimos en consola ---
            print(f"Acelerómetro: {round(ax_avg, 2)} {round(ay_avg, 2)} {round(az_avg, 2)}")
            print(f"Giroscopio: {round(gx_avg, 2)} {round(gy_avg, 2)} {round(gz_avg, 2)}\n")
            print(f"X={round(px,2)}")
            print(f"Y={round(py,2)}")
            print(f"Z={round(pz,2)}")

            # --- Guardamos datos en archivo CSV ---
            writer.writerow([
                datetime.now().isoformat(),
                round(ax_avg, 3), round(ay_avg, 3), round(az_avg, 3),
                round(gx_avg, 3), round(gy_avg, 3), round(gz_avg, 3)
            ])

            time.sleep(1.2)  # Esperamos 1.2 segundos entre lecturas

        except KeyboardInterrupt:
            # Si el usuario presiona Ctrl+C, salimos del bucle
            print("Lectura terminada.")
            break
