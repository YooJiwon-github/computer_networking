# -*- coding: utf-8 -*-
import socket


HOST = '127.0.0.1'

PORT = 9999


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))


for i in range(3):

    # 패킷 요청
    packet = str(100 + i)

    # msg = '------------>  packet ' + packet +' send'
    msg = packet
    
    data = msg.encode()

    length = len(data)

    client_socket.sendall(length.to_bytes(4, byteorder="little"))

    client_socket.sendall(data)

    data = client_socket.recv(4)

    length = int.from_bytes(data, "little")

    data = client_socket.recv(length)

    msg = data.decode()

    print(msg)

    # ack 송신
    ack = 'ACK' + packet
    
    data = ack.encode()

    length = len(data)

    client_socket.sendall(length.to_bytes(4, byteorder="little"))

    client_socket.sendall(data)

    print('<---- ', ack, 'send')

client_socket.close()