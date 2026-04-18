# bmp180_rpi.py
# Lectura de temperatura y presión del BMP180 desde registros (Raspberry Pi + Python 3)
# Requiere: sudo apt install python3-smbus i2c-tools  (y habilitar I2C en raspi-config)

import time
from smbus2 import SMBus

BMP180_ADDR = 0x77  # a veces 0x77 (típico) o 0x76
REG_CALIB_START = 0xAA
REG_CONTROL     = 0xF4
REG_DATA_MSB    = 0xF6
CMD_TEMP        = 0x2E
CMD_PRESSURE    = 0x34  # agregar (oss<<6)

# oversampling 0..3 (0=rápido, 3=máxima resolución)
OSS = 0

def read_s16(bus, addr, reg):
    hi = bus.read_byte_data(addr, reg)
    lo = bus.read_byte_data(addr, reg+1)
    val = (hi << 8) + lo
    if val & 0x8000:
        val = -((~val & 0xFFFF) + 1)
    return val

def read_u16(bus, addr, reg):
    hi = bus.read_byte_data(addr, reg)
    lo = bus.read_byte_data(addr, reg+1)
    return (hi << 8) + lo

class BMP180:
    def _init_(self, busnum=1, addr=BMP180_ADDR, oss=OSS):
        self.bus = SMBus(busnum)
        self.addr = addr
        self.oss  = oss
        self._read_calibration()

    def _read_calibration(self):
        b = self.bus
        a = self.addr
        self.AC1 = read_s16(b, a, 0xAA)
        self.AC2 = read_s16(b, a, 0xAC)
        self.AC3 = read_s16(b, a, 0xAE)
        self.AC4 = read_u16(b, a, 0xB0)
        self.AC5 = read_u16(b, a, 0xB2)
        self.AC6 = read_u16(b, a, 0xB4)
        self.B1  = read_s16(b, a, 0xB6)
        self.B2  = read_s16(b, a, 0xB8)
        self.MB  = read_s16(b, a, 0xBA)
        self.MC  = read_s16(b, a, 0xBC)
        self.MD  = read_s16(b, a, 0xBE)

    def _read_raw_temp(self):
        self.bus.write_byte_data(self.addr, REG_CONTROL, CMD_TEMP)
        time.sleep(0.005)  # 4.5 ms
        msb = self.bus.read_byte_data(self.addr, REG_DATA_MSB)
        lsb = self.bus.read_byte_data(self.addr, REG_DATA_MSB+1)
        return (msb << 8) + lsb

    def _read_raw_pressure(self):
        self.bus.write_byte_data(self.addr, REG_CONTROL, CMD_PRESSURE + (self.oss << 6))
        wait = [0.005, 0.008, 0.014, 0.026][self.oss]
        time.sleep(wait)
        msb = self.bus.read_byte_data(self.addr, REG_DATA_MSB)
        lsb = self.bus.read_byte_data(self.addr, REG_DATA_MSB+1)
        xlsb= self.bus.read_byte_data(self.addr, REG_DATA_MSB+2)
        up = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.oss)
        return up

    def read(self):
        UT = self._read_raw_temp()

        # Cálculo de temperatura (datasheet)
        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) // (X1 + self.MD)
        B5 = X1 + X2
        T  = (B5 + 8) >> 4  # décimas de °C
        temp_c = T / 10.0

        # Cálculo de presión (datasheet)
        UP = self._read_raw_pressure()
        B6 = B5 - 4000
        X1 = (self.B2 * (B6 * B6 >> 12)) >> 11
        X2 = (self.AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.AC1 * 4 + X3) << self.oss) + 2) >> 2
        X1 = (self.AC3 * B6) >> 13
        X2 = (self.B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self.oss)
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        # p en Pa
        return temp_c, p

if _name_ == "_main_":
    sensor = BMP180(busnum=1, addr=BMP180_ADDR, oss=0)
    while True:
        t, p = sensor.read()
        print(f"Temp: {t:.2f} °C | Presión: {p/100:.2f} hPa")
        time.sleep(1)
