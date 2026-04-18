import sys
import smbus2
sys.modules['smbus'] = smbus2  
import time
import math
import numpy as np
import matplotlib.pyplot as plt

# --- Configuración Hardware ---
MPU = 0x68
bus = smbus2.SMBus(1)
dt = 0.1  # Tiempo de muestreo

# Variables de estado (Ángulos de Euler)
phi, theta, psi = 0.0, 0.0, 0.0

def init_mpu():
    try:
        bus.write_byte_data(MPU, 0x6B, 0x00)
        print(f"Sensor detectado en {hex(MPU)}")
    except Exception as e:
        print(f"Error de hardware: {e}"); exit()

def read_raw(addr):
    d = bus.read_i2c_block_data(MPU, addr, 6)
    def c(h, l):
        v = (h << 8) | l
        return v - 65536 if v > 32767 else v
    return c(d[0], d[1]), c(d[2], d[3]), c(d[4], d[5])

# --- Funciones de Matrices (Basadas en tu imagen) ---
def get_rotation_matrix(phi, theta, psi):
    # phi, theta, psi en radianes
    cp, sp = math.cos(phi), math.sin(phi)
    ct, st = math.cos(theta), math.sin(theta)
    cs, ss = math.cos(psi), math.sin(psi)
    
    R = np.array([
        [cs*ct, -ss*cp + cs*st*sp,  ss*sp + cs*st*cp],
        [ss*ct,  cs*cp + ss*st*sp, -cs*sp + ss*st*cp],
        [-st,    ct*sp,             ct*cp]
    ])
    return R

def get_euler_matrix(phi, theta):
    cp, sp = math.cos(phi), math.sin(phi)
    ct = math.cos(theta)
    if abs(ct) < 0.001: ct = 0.001 # Protección contra Gimbal Lock
    tt = math.tan(theta)
    
    # Matriz E que relaciona (p, q, r) con derivadas de Euler
    E = np.array([
        [1, sp*tt,  cp*tt],
        [0, cp,    -sp],
        [0, sp/ct,  cp/ct]
    ])
    return E

# --- Configuración de Gráfica ---
plt.ion()
fig, ax = plt.subplots(figsize=(8, 5))
h_phi, h_theta, h_psi = [], [], []
l1, = ax.plot([], [], 'r-', label='Roll (φ)')
l2, = ax.plot([], [], 'b-', label='Pitch (θ)')
l3, = ax.plot([], [], 'g-', label='Yaw (ψ)')
ax.set_ylim(-180, 180)
ax.legend()
ax.set_title("Orientación del UAV - FIME Aviónica")

init_mpu()

try:
    while True:
        start = time.time()
        
        # 1. Leer Acelerómetro y Giroscopio
        ax_r, ay_r, az_r = read_raw(0x3B)
        gx_r, gy_r, gz_r = read_raw(0x43)
        
        # 2. Convertir a unidades físicas (p, q, r en rad/s)
        p = math.radians(gx_r / 131.0)
        q = math.radians(gy_r / 131.0)
        r = math.radians(gz_r / 131.0)
        
        # 3. Calcular ángulos actuales (Uso de acelerómetro para inclinación)
        # Nota: Sin filtro, estas lecturas son sensibles a la vibración del motor
        phi = math.atan2(ay_r, az_r)
        theta = math.atan(-ax_r / math.sqrt(ay_r**2 + az_r**2))
        psi += r * dt # El Yaw se integra porque no hay magnetómetro
        
        # 4. Obtener Matrices R y E
        RotMat = get_rotation_matrix(phi, theta, psi)
        EulMat = get_euler_matrix(phi, theta)
        
        # 5. Mostrar resultados en terminal
        print("\033[H\033[J") # Limpiar terminal
        print(f"Velocidades angulares (p,q,r): {p:.2f}, {q:.2f}, {r:.2f} rad/s")
        print(f"Ángulos (Deg): Roll:{math.degrees(phi):.1f} Pitch:{math.degrees(theta):.1f} Yaw:{math.degrees(psi):.1f}")
        print("\nMATRIZ DE ROTACIÓN (R):")
        print(np.round(RotMat, 4))
        print("\nMATRIZ DE EULER (E):")
        print(np.round(EulMat, 4))
        
        # 6. Actualizar Gráfica
        h_phi.append(math.degrees(phi))
        h_theta.append(math.degrees(theta))
        h_psi.append(math.degrees(psi))
        if len(h_phi) > 50:
            h_phi.pop(0); h_theta.pop(0); h_psi.pop(0)
        
        l1.set_data(range(len(h_phi)), h_phi)
        l2.set_data(range(len(h_theta)), h_theta)
        l3.set_data(range(len(h_psi)), h_psi)
        ax.set_xlim(0, 50)
        plt.pause(0.01)
        
        # Control de frecuencia
        sleep_time = dt - (time.time() - start)
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    plt.close()
    print("\nPrograma finalizado.")