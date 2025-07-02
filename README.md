## Comando para ejecutar la simulación
´´´
 mpiexec -n 6   --host "192.168.100.2,192.168.100.2,192.168.100.3,192.168.100.3,192.168.100.1,localhost"   --env DISPLAY=$DISPLAY   python3 controlador_nodos.py
´´´