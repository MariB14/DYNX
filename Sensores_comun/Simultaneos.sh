#!/bin/bash
echo "Iniciando sistemas de telemetría..."

# 1. Iniciar los scripts de Python en segundo plano (usando &)
python3 MPU_python.py &
python3 Altura1.py &
python3 enviardata.py &

# Cuando tengas los demás listos, solo quítales el #
# python3 GPS.py &
# python3 Transmisor_RF.py &

echo "Todos los sistemas corriendo simultáneamente."
echo "Presiona Ctrl+C para detener todos los sensores."

# 2. Esta línea mágica atrapa el Ctrl+C y apaga los códigos en segundo plano
trap "echo -e '\n Apagando sensores...'; pkill -P $$; exit" SIGINT

# 3. Mantener el script principal vivo esperando
wait