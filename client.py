# -*- coding: utf-8 -*-
import socket
import random

HOST = '127.0.0.1'
PORT = 9999

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.bind((HOST, PORT))
sender_socket.listen()

previous_ack = 100 # ������ ������ ack�� ������ ����
expected_packet = 100 # �������� ���ŵǾ�� �� ��Ŷ �ʱ�ȭ

while True:
    client_socket, addr = sender_socket.accept()

    try:
        #��Ŷ ����
        data = client_socket.recv(4)
        length = int.from_bytes(data, "little")
        data = client_socket.recv(length)
        msg = data.decode()
        print('----------> ', msg)

        # ��Ŷ�� ����� ���۵� ���
        if data == (expected_packet).to_bytes(4, byteorder="little"):
            ack_packet = data
            previous_ack = ack_packet

            # �������� ���ŵǾ�� �� ��Ŷ
            expected_packet += 1
        else:
            # ��Ŷ�� �ùٸ��� ���ŵ��� ���� ���, ������ �ùٸ��� ���ŵ� ��Ŷ�� ack�� ������
            ack_packet = previous_ack

        ack_data = str(ack_packet).encode()
        ack_length = len(ack_data)    

        client_socket.sendall(ack_length.to_bytes(4, byteorder="little"))
        client_socket.sendall(ack_data)
        print('<---- ', ack_packet, 'send')
                     
    except Exception as e:
        print("Exception : ", e)
    finally:
        client_socket.close()
