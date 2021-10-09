def client(ip='192.168.0.181', accion='abrir_tiempo', cantidad=1):
    import socket

    for i in range(cantidad):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, 5050)
        s.connect(server_address)
        try:
            if accion == 'abrir_tiempo':
                message = b'#T'

            elif accion == 'abrir':
                message = b'#A'

            else:
                message = b'#C'

            s.sendall(message)

        finally:
            s.close()
