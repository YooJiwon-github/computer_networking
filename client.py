# -*- coding: utf-8 -*-
import socket
import random

HOST = '127.0.0.1'
PORT = 9999

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.bind((HOST, PORT))
sender_socket.listen()

previous_ack = None # ������ ������ ack�� ������ ����
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

        if data == (expected_packet).to_bytes(4, byteorder="little"):
            if previous_ack is None:
                   ack_packet = f'ACK {expected_packet}'
                    
            else:
                # ACK �۽�
                ack_packet = msg + ' ACK'
        else:
            # ��Ŷ�� �ùٸ��� ���ŵ��� ���� ���, ������ �ùٸ��� ���ŵ� ��Ŷ�� ack�� ������
            ack_packet = previous_ack

        ack_data = ack_packet.encode()
        ack_length = len(ack_data)    

        client_socket.sendall(ack_length.to_bytes(4, byteorder="little"))
        client_socket.sendall(ack_data)
        print('<---- ', ack_packet, 'send')

        # �������� ���ŵǾ�� �� ��Ŷ
        expected_packet += 1
                     

    except Exception as e:
        print("Exception : ", e)
    finally:
        client_socket.close()
