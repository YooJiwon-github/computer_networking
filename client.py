# -*- coding: utf-8 -*-
import socket

msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # ���� Ÿ�� ����
server_address = ('127.0.0.1', 9999)
client_socket.sendto(bytesToSend, server_address)

previous_ack = 100  # ������ ������ ack�� ������ ����
expected_packet = 100  # �������� ���ŵǾ�� �� ��Ŷ �ʱ�ȭ

while True:
    try:
        # ��Ŷ ����
        data, _ = client_socket.recvfrom(1024)  # ������ ���������� recvfrom ���
        length = int.from_bytes(data[:4], "little")
        msg = data[4:length + 4].decode()
        print('----------> ', msg)

        # ��Ŷ�� ����� ���۵� ���
        if int(msg) == expected_packet:
            ack_packet = msg
            previous_ack = ack_packet
            # �������� ���ŵǾ�� �� ��Ŷ
            expected_packet += 1
        else:
            # ��Ŷ�� �ùٸ��� ���ŵ��� ���� ���, ������ �ùٸ��� ���ŵ� ��Ŷ�� ack�� ������
            ack_packet = previous_ack

        ack_data = str(ack_packet).encode()
        ack_length = len(ack_data)

        client_socket.sendto(length.to_bytes(4, byteorder="little") + ack_data, server_address)  # sendall ��� sendto ���
        print('<---- ', ack_packet, 'send')

    except Exception as e:
        print("Exception : ", e)
