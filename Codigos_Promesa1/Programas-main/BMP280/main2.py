from machine import Pin, I2C
from time import sleep, sleep_ms, sleep_us
from BMP180LIB import BMP180


def run():
    busI2C = I2C(1, scl = Pin(22), sda=Pin(21), freq=100000)
    bmp    = BMP180(busI2C)
       
    
    while True:
        print( "temp: "+ str( bmp.get_temperature() ) )
        print( "pressure: "+ str( bmp.get_pressure() ) )
        sleep(1)


if __name__=="__main__":
   run()
