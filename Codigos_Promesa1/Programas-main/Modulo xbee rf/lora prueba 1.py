
while True:
    packet = rfm9x.receive(timeout=1.0) 

    if packet is not None:
        try:
            packet_text = str(packet, "utf-8").strip()
            print("\n[RX] Mensaje recibido del Nano: {}".format(packet_text))
            
            if packet_text == "hola raspberry":
                
                ack_msg = bytes("ACK", "utf-8")
                rfm9x.send(ack_msg)
                print("--> [TX] ACK enviado al Transmisor.")

                response_msg = bytes("hola arduino", "utf-8")
                rfm9x.send(response_msg)
                print("[TX] Respondiendo con: {}".format(response_msg.decode()))
                
        except Exception as e:
            print(f"Error al procesar el paquete: {e}")
            
    time.sleep(0.1)