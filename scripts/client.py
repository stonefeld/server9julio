import sys
import socket

argv = sys.argv
argv.remove(argv[0])

accion = argv[0]
cantidad = int(argv[1])
ip = '192.168.100.151'

for i in range(cantidad):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5050)
    s.connect(server_address)
    try:
        if accion == 'abrir_tiempo':
            message = b'#T'

        elif accion == 'abrir':
            message = b'#A'

        else:
            message = b'#C'

        print('Sending ' + str(message))
        s.sendall(message)

        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = s.recv(16)
            amount_received += len(data)
            print('Received: ' + str(data))

        print('Final data count: ' + str(amount_received))

    finally:
        print('Closing socket')
        s.close()

