
#Para importar librerias
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import paho.mqtt.client as mqtt
username = "20f70690-4976-11ea-84bb-8f71124cfdfb"
password = "3d7eaaf9a7c9e28626fcab4ec5a61108cfbb8be0"
clientid = "cccb41b0-4977-11ea-b73d-1be39589c6b2"
mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()
topic_dht11_temp = "v1/" + username + "/things/" + clientid + "/data/1"
topic_dht11_humidity = "v1/" + username + "/things/" + clientid + "/data/2"
BOARD.setup()
class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()         
    def on_rx_done(self):
        print ("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        #print (bytes(payload).decode("utf-8",'ignore'))
        data = bytes(payload).decode("utf-8",'ignore')
        print (data)
        temp = (data[0:4])
        humidity = (data[4:6])
        print ("Temperature:")
        print (temp)
        print ("Humidity:")
        print (humidity)
        mqttc.publish(topic_dht11_temp, payload=temp, retain=True)
        mqttc.publish(topic_dht11_humidity, payload=humidity, retain=True)
        print ("Sent to Cayenne")
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) 
lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
lora.set_pa_config(pa_select=1)
try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print ("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print ("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()

Arduino Code:

#include <SPI.h>
#include <RH_RF95.h>
#include "DHT.h"

#define DHTPIN A0     // what pin we're connected to
#define DHTTYPE DHT11   // DHT type
DHT dht(DHTPIN, DHTTYPE);
int hum;  //Stores humidity value
int temp; //Stores temperature value

RH_RF95 rf95;

void setup() 
{
  Serial.begin(9600);
  dht.begin();
  if (!rf95.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

}

void loop()
{
  temp = dht.readTemperature();
  hum = dht.readHumidity();
  String humidity = String(hum); //int to String
  String temperature = String(temp);
  String data = temperature + humidity;
  Serial.print(data);
  char d[5];
  data.toCharArray(d, 5); //String to char array
  Serial.println("Sending to rf95_server");
  rf95.send(d, sizeof(d));
  rf95.waitPacketSent();
  
  delay(400);
}
 