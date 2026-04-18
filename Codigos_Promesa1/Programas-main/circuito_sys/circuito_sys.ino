int rele= 8;
//es por si quieres añadir otro switch para programar cuando empieza el contador
int entrada = 5;
void setup() {
  // put your setup code here, to run once:
 pinMode(rele, OUTPUT);
 pinMode(entrada,INPUT);
digitalWrite(rele,LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  
int espera;
// cambiar el numero de aqui para cambiar el delay
espera= 10000;
int condicion = digitalRead(entrada);
delay(espera);

digitalWrite(rele,HIGH);

}

