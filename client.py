# -*- coding: utf-8 -*-
import socket

msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 소켓 타입 변경
server_address = ('127.0.0.1', 9999)
client_socket.sendto(bytesToSend, server_address)

previous_ack = 100  # 이전에 전송한 ack를 저장할 변수
expected_packet = 100  # 다음으로 수신되어야 할 패킷 초기화

while True:
    try:
        # 패킷 수신
        data, _ = client_socket.recvfrom(1024)  # 서버와 마찬가지로 recvfrom 사용
        length = int.from_bytes(data[:4], "little")
        msg = data[4:length + 4].decode()
        print('----------> ', msg)

        # 패킷이 제대로 전송된 경우
        if int(msg) == expected_packet:
            ack_packet = msg
            previous_ack = ack_packet
            # 다음으로 수신되어야 할 패킷
            expected_packet += 1
        else:
            # 패킷이 올바르게 수신되지 않은 경우, 이전에 올바르게 수신된 패킷의 ack를 재전송
            ack_packet = previous_ack

        ack_data = str(ack_packet).encode()
        ack_length = len(ack_data)

        client_socket.sendto(length.to_bytes(4, byteorder="little") + ack_data, server_address)  # sendall 대신 sendto 사용
        print('<---- ', ack_packet, 'send')

    except Exception as e:
        print("Exception : ", e)
