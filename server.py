# -*- coding: utf-8 -*-
import socket, threading

def binder(client_socket, addr):

    print('Connected by', addr)

    try:
        
        while True:
           
            data = client_socket.recv(4)
            
            length = int.from_bytes(data, "little")
            
            data = client_socket.recv(length)
            
            msg = data.decode()
            
            # print('Received from', addr)
            print('------------> ', msg)

            # 패킷 송신
            msg = msg + 'packet received'

            data = msg.encode()

            # msg = '------------>  packet received'
            
            # data = msg.encode()
            
            length = len(data)
            
            client_socket.sendall(length.to_bytes(4, byteorder="little"))
            
            client_socket.sendall(data)
    except:
        
        print("except : ", addr)
    finally:
        
        client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('', 9999))

server_socket.listen()

try:

    while True:

        client_socket, addr = server_socket.accept()

        th = threading.Thread(target=binder, args=(client_socket,addr))
        th.start()
except:
    print("server")
finally:

    server_socket.close() 