import sys
import socket

argv = sys.argv
argv.remove(argv[0])

#accion = argv[0]
accion = 'cerrar'
#cantidad = int(argv[1])
cantidad = 1
ip = '192.168.0.17'

for i in range(cantidad):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Conectando a la ip: {ip} en el puerto: 5050')
    server_address = (ip, 8088)
    s.connect(server_address)
    try:
        if accion == 'abrir_tiempo':
            message = b'#T'

        elif accion == 'abrir':
            message = b'#A'

        else:
            message = b'#C'

        print(f'Enviando {str(message)}')
        s.sendall(message)

    finally:
        print('Cerrando conexión')
        s.close()
