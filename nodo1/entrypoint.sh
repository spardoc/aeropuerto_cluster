#!/bin/bash

echo "[entrypoint] Verificando claves SSH del host en /etc/ssh/..."
ls -la /etc/ssh/ssh_host_*

if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    echo "[entrypoint] Generando claves SSH del host..."
    ssh-keygen -A
fi

echo "[entrypoint] Iniciando SSH daemon..."
/usr/sbin/sshd -D &
SSHD_PID=$!

# Espera unos segundos para asegurar que sshd arrancó bien
sleep 2

# Cambia 'nodoX.py' por el script que corresponde a cada contenedor
echo "[entrypoint] Iniciando script Python del nodo..."
python /app/nodo1.py &  # ejemplo para nodo1, cambia a nodo2.py o nodo3.py según corresponda

wait $SSHD_PID
