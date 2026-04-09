unsigned long myTime;
unsigned long Tiempo0;
unsigned long Tiempof;
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64


Adafruit_BMP280 bmp;

// 1. Aquí solo CREAMOS las variables (las inicializamos en 0)
// No intentes leer el sensor aquí porque aún está apagado.
float Pinicial = 0;
float Altinicial = 0;
float AltMax = 0;
float velocidad=0;
float factor=1;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

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
                Adafruit_BMP280::SAMPLING_X4,    /* Pres. oversampling */
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

    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(10, 10);
  display.println("Altimetro");
  display.display();
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

  if (AltCohete > AltMax  ){
    AltMax = AltCohete;
    if (AltMax>2){
  Tiempof=(myTime - Tiempo0);
velocidad=((AltMax*1000)/(Tiempof-15000));
    }
  
     }
if(AltMax > 0 ){

      if((AltCohete-factor) <AltMax){

  }
  }


  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(10, 5);
  display.println("Maxima altura:");
   display.setTextColor(WHITE);
  display.setCursor(10, 15);
   display.setTextSize(1);
  display.println(AltMax);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(10, 25);
  display.println("velocidad promedio:");
   display.setTextColor(WHITE);
  display.setCursor(10, 35);
   display.setTextSize(1);
  display.println(velocidad);
  display.display();
  Serial.println();
  delay(10);
 
}