unsigned long myTime;
unsigned long Tiempo0;
unsigned long Tiempof;
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>


Adafruit_BMP280 bmp;

// 1. Aquí solo CREAMOS las variables (las inicializamos en 0)
// No intentes leer el sensor aquí porque aún está apagado.
float Pinicial = 0;
float Altinicial = 0;
float AltMax = 0;
float velocidad=0;
float factor=1;
float tiempovuelo; //para registrar tiempo y saber velocidad hasta apogeo
float tinicial;

void setup() {
  Serial.begin(9600);
  long lecturai=0;
  long lecturaa=0;
  // ¡IMPORTANTE! BORRA O COMENTA ESTA LÍNEA:
  // pinMode(1, INPUT); 
  // El pin 1 es TX (transmisión serial). Si lo pones como input, cortas el Serial.println.

  Serial.println(F("BMP280 test"));

  if (!bmp.begin(0x76)) { 
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1);
  }

  // Configuración del sensor
//  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
  //                Adafruit_BMP280::SAMPLING_X2,
    //              Adafruit_BMP280::SAMPLING_X16,
      //            Adafruit_BMP280::FILTER_X16,
        //          Adafruit_BMP280::STANDBY_MS_500);
//
 // Configuración para desactivar el filtro en un BMP280
bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Modo de operación */
                Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                Adafruit_BMP280::SAMPLING_X16,    /* Pres. oversampling */
                Adafruit_BMP280::FILTER_X16,      /* <--- AQUÍ SE DESACTIVA EL FILTRO */
                Adafruit_BMP280::STANDBY_MS_1); /* Tiempo de espera */

  // 2. AHORA SÍ leemos el sensor.
  // Ya pasó el bmp.begin(), así que ahora sí funcionará.
  Pinicial = bmp.readPressure();
  Altinicial = bmp.readAltitude(1013.25);
 
  
Tiempo0=millis();
  Serial.print(F("Presión = "));
  Serial.print(Pinicial);
  Serial.println(" Pa");
  
  Serial.print(F("Altitud Ref = "));
  Serial.print(Altinicial);
  Serial.println(" m");


}
void loop() {
  Serial.print("Time: ");
  myTime = millis();

  Serial.println(myTime); // prints time since program started

Serial.print("Altura inicial: ");
  Serial.println(Altinicial);

  float AltActual = bmp.readAltitude(1013.250000);
  
  // Si Altinicial ya es un número válido, esta resta funcionará bien
  float AltCohete = (AltActual - Altinicial);
  
  Serial.print("Altura del cohete: ");
  Serial.println(AltCohete);

if(AltCohete > 1.1 && AltCohete < 1.2){
tinicial=millis();

}

  if (AltCohete > AltMax  ){
    AltMax = AltCohete;
    if (AltMax>2){
  Tiempof=(myTime - Tiempo0);
velocidad=((AltMax*1000)/(Tiempof-15000));
tiempovuelo= (myTime - tinicial);
    }
  
     }
if(AltMax > 0 ){

      if((AltCohete-factor) <AltMax){

  }
  }

Serial.println("Altura:");
Serial.print(AltCohete);
Serial.println("Presion:");
Serial.print(bmp.readPressure());
delay(1000);
 
}